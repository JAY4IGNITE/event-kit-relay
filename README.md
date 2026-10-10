# College Event Kit Relay

A reservation and custody-tracking system for shared audio-visual **EventKits**
(camera, mic, tripod, light). One physical kit is relayed between college clubs
across sequential time slots, with a mandatory **15-minute inspection window**
between consecutive reservations. Late returns shift the next club's *effective*
start time (originals preserved) and delays cascade forward.

> This repository is a **scaffold**: full project structure, configs, typed
> interfaces, and design-pattern stubs. Business logic methods raise
> `NotImplementedError` and are meant to be filled in per the PRDs in `docs/prd`.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| Database | PostgreSQL 16 (local, via Docker) |
| Scheduler | APScheduler behind a `Scheduler` port (pending-expiry + no-show sweeps) |
| Frontend | TypeScript, React 18, Vite, TanStack Query |
| API types | Generated from the FastAPI OpenAPI schema (`npm run gen:api`) |

## Quick start

```bash
cp .env.example .env
docker compose up --build
# backend  -> http://localhost:8000  (interactive docs at /docs)
# frontend -> http://localhost:5173
# apply the DB schema once the stack is up:
docker compose exec backend alembic upgrade head
```

Or use the Makefile targets: `make up`, `make migrate`, `make backend-test`.

## Layout

```
docs/prd/              Product requirements (start at 00-master-prd.md)
backend/app/
  domain/              pure business logic (entities, value objects, states,
                       strategies, policies, specifications, validators, events)
  application/         orchestration (services, commands, dto)
  ports/               Protocols: repositories, UnitOfWork, Clock, EventBus,
                       LockManager, Scheduler, Notifier
  infrastructure/      adapters (SQLAlchemy, APScheduler, event bus, notifier)
  api/                 FastAPI routes + schemas
  main.py              app entrypoint + scheduler lifecycle
frontend/src/          React + Vite SPA (features/, api/, components/)
docker-compose.yml     db + backend + frontend
```

## Architecture

Hexagonal (ports & adapters). The `domain` layer imports nothing outward and is
unit-testable with a `FixedClock` and in-memory repositories. See
`docs/prd/01-architecture.md` for the full rationale and the design-pattern map
(State, Strategy, Observer, Chain of Responsibility, Specification, Factory,
Builder, Repository, Unit of Work, Command, Memento, Facade, Adapter).

## The two time-based sweeps ("crons")

| Job | Watches | Fires when | Result |
|-----|---------|-----------|--------|
| **PendingExpirySweep** | `PENDING` reservations | hold deadline passes | → `EXPIRED` (auto-reject), kit released, deposit voided |
| **NoShowSweep** | `CONFIRMED`, never checked out | grace passes | → `NO_SHOW`, deposit forfeited |

Both run on a recurring interval via the `Scheduler` port, read "now" from the
`Clock` port (so tests can advance time), and are self-healing after downtime.
Details and the confirm-vs-expire race analysis: `docs/prd/08-scheduling-crons.md`.

## Security note

This scaffold ships **no authentication** on the API. Before any networked or
shared deployment, add authn/authz (e.g. OAuth2/JWT on the FastAPI side) and
restrict CORS — the endpoints are currently open.

## Testing

```bash
cd backend && pip install -e ".[dev]" && pytest   # unit stubs are skipped until implemented
```

Unit tests target the state machine, the delay cascade, and the pending-expiry
race using a deterministic `FixedClock`.
