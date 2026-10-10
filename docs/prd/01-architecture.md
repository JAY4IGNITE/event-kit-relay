# Architecture & Tech Stack

**Status:** Draft v1.0
**Last updated:** 2026-10-10

---

## 1. Stack decision

| Concern | Choice | Why |
|---------|--------|-----|
| Backend framework | FastAPI (Python 3.11) | Async, Pydantic v2 validation, auto OpenAPI → feeds the TS client. Fits the service-oriented relay design. |
| ORM | SQLAlchemy 2.0 async | Mature, supports `version_id_col` for optimistic locking and `SELECT ... FOR UPDATE` row locks. |
| Migrations | Alembic | Standard with SQLAlchemy. |
| Database | PostgreSQL 16 (Docker) | Real transactions + row-level locking needed by the concurrency design; production parity. |
| Scheduler | APScheduler behind a `Scheduler` port | In-process recurring sweeps for pending-expiry and no-show; port keeps the domain clean and swappable for Celery/cloud later. |
| Frontend | React 18 + Vite + TypeScript | Fast SPA for organizer + club dashboards. |
| Data fetching | TanStack Query | Caching + polling for schedule/relay state. |
| API types | openapi-typescript | Generate TS types/client from the FastAPI OpenAPI schema — one source of truth. |
| Backend tests | pytest + FixedClock | Deterministic time-based tests for crons and delay cascades. |
| Frontend tests | Vitest | Vite-native. |
| Orchestration | Docker Compose | `db`, `backend`, `frontend` with one `docker compose up`. |

## 2. Hexagonal / ports-and-adapters layering

```
app/
  domain/            pure business logic, no I/O, no framework imports
    entities/        EventKit, Reservation, KitSchedule, Equipment, Inspection,
                     Handover, KitCondition, Deposit, Club, Organizer
    value_objects/   TimeSlot, Money, TurnaroundWindow, HoldPolicy, ids
    states/          KitState + concrete states (State pattern)
    strategies/      DelayResolutionStrategy + variants
    policies/        DepositPolicy, LoyaltyPolicy, TurnaroundPolicy
    specifications/  KitSpecification + composable specs
    validators/      ReservationValidator chain
    events/          DomainEvent + concrete events
    errors/          KitRelayError hierarchy
  application/        orchestration (depends only on ports)
    services/        ReservationService (Facade), HandoverService,
                     InspectionService, InventoryService, RelayCoordinator
    commands/        Command pattern handover ops
    dto/             request/result dataclasses
  ports/             Protocols: repositories, UnitOfWork, Clock, EventBus,
                     LockManager, Scheduler, Notifier
  infrastructure/     adapters implementing ports
    db/              SQLAlchemy models + repositories + UnitOfWork
    scheduler/       APScheduler adapter + sweep jobs
    notifications/   console/email notifier
    eventbus/        in-process event bus
  api/                FastAPI routes + Pydantic schemas (HTTP adapter)
```

**Dependency rule:** `domain` imports nothing from `application`, `infrastructure`,
or `api`. `application` imports `domain` + `ports` only. `infrastructure` and `api`
implement/consume `ports`. This is what makes the relay unit-testable with an
in-memory UnitOfWork and a `FixedClock`.

## 3. Design patterns applied

| Pattern | Location | Purpose |
|---------|----------|---------|
| State | `domain/states` + EventKit | Enforce legal kit lifecycle; illegal transitions raise. |
| Strategy | `domain/strategies`, policies | Swap late-return / deposit / loyalty behavior. |
| Observer | `ports.EventBus` + subscribers | Decouple notification, loyalty, audit from relay. |
| Chain of Responsibility | `domain/validators` | Open/closed reservation validation pipeline. |
| Specification | `domain/specifications` | Composable kit matching for reroute. |
| Factory / Abstract Factory | `EquipmentFactory`, `KitTemplate` | Hide concrete equipment/kit construction. |
| Builder | `EventKitBuilder` | Validated slot assembly. |
| Repository + Unit of Work | `ports` + `infrastructure/db` | Isolate storage; atomic multi-aggregate relay. |
| Command | `application/commands` | Auditable, undoable handover operations. |
| Memento | `KitSchedule.snapshot/restore` | Roll back timeline on failed reroute. |
| Facade | `ReservationService` | One entry point over the subsystem. |
| Adapter | `infrastructure/*` | Swap DB / clock / notifier without domain change. |

## 4. Concurrency & consistency

- **Optimistic locking:** `version` column on `EventKit`, `Reservation`, `KitSchedule`; stale writes raise `ConcurrencyConflictError`.
- **Pessimistic row locks:** `SELECT ... FOR UPDATE` on the kit row inside `create_reservation` and `run_relay` via `LockManager`.
- **Transactional relay:** `UnitOfWork` wraps reservation + deposit + schedule mutations; failed reroute → `schedule.restore(memento)` + rollback.
- **Idempotency:** `ReservationRequest.idempotency_key` dedupes retried submits.
- **Time via port:** all "now" reads go through `Clock`; sweeps use it so tests can advance time.

## 5. Data model (tables)

| Table | Key columns |
|-------|-------------|
| clubs | id, name, loyalty_score, loyalty_tier |
| organizers | id, name |
| equipment | id, name, type, status, specs(jsonb) |
| event_kits | id, status, version |
| kit_slots | id, kit_id, required_type, equipment_id(nullable) |
| reservations | id, club_id, kit_id, booked_start, booked_end, eff_start, eff_end, actual_end, status, created_at, hold_expires_at, deposit_id, version |
| kit_schedules | id, kit_id, turnaround_minutes, version |
| inspections | id, kit_id, inspector_id, window_start, window_end, result, faulty_items(jsonb), notes |
| handovers | id, reservation_id, type, at, performed_by |
| kit_conditions | id, handover_id, item_states(jsonb), acknowledged_by, at |
| deposits | id, reservation_id, amount, currency, status |
| domain_events | id, type, payload(jsonb), occurred_at, processed |

## 6. API surface (v1)

| Method | Path | Purpose |
|--------|------|---------|
| POST | /reservations | Create (soft hold) |
| POST | /reservations/{id}/confirm | Confirm within hold window |
| POST | /reservations/{id}/cancel | Manual cancel |
| GET | /reservations/{id} | Fetch |
| POST | /handovers/checkout | Check out a confirmed reservation |
| POST | /handovers/return | Return a kit (opens inspection) |
| POST | /inspections/{id}/complete | Record PASS/FAIL + faulty items |
| GET | /kits | List kits + status |
| GET | /kits/{id}/schedule | Relay timeline |
| GET | /clubs/{id} | Club + loyalty |
| GET | /health | Liveness |

## 7. Local run

```bash
cp .env.example .env
docker compose up --build        # db + backend + frontend
# backend  -> http://localhost:8000  (docs at /docs)
# frontend -> http://localhost:5173
docker compose exec backend alembic upgrade head
```

## 8. Testing strategy

- **Unit:** domain state machine, `propagate_delay` cascade (FixedClock), validators, strategies.
- **Integration:** repository + UnitOfWork against a disposable Postgres; confirm-vs-expire race.
- **Contract:** generate TS types from OpenAPI in CI; fail if drift.
