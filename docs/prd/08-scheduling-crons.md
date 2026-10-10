# PRD — Scheduling & Crons

**Module owner:** Backend / Platform
**IDs:** FR-CRON-*
**Pattern:** Scheduler port + Job; recurring sweeps using the `Clock` port.

---

## 1. Purpose

Define the time-based background jobs ("crons") that move reservations out of
transient states automatically. Two independent sweeps exist; they watch
different states and MUST NOT be conflated.

## 2. The two sweeps

| Job | Watches | Fires when | Transition | Side effects |
|-----|---------|-----------|-----------|--------------|
| **PendingExpirySweep** | reservations in **PENDING** | `now >= hold_expires_at` | PENDING → **EXPIRED** (auto-reject) | release kit hold (RESERVED→AVAILABLE), void PENDING deposit, remove from schedule, emit `ReservationExpired`, notify club |
| **NoShowSweep** | reservations in **CONFIRMED** | `now >= effective_start + no_show_grace`, never checked out | CONFIRMED → **NO_SHOW** | forfeit deposit, free/relay kit, loyalty penalty, emit `ReservationNoShow`, notify |

`EXPIRED` is the terminal "auto-rejected" status for a hold that was never
confirmed in time. It is distinct from manual `CANCELLED` and from `NO_SHOW`.

## 3. Hold policy (single source of truth)

```python
@dataclass(frozen=True)
class HoldPolicy:
    pending_ttl: timedelta = timedelta(minutes=10)      # confirm within 10 min or auto-reject
    no_show_grace: timedelta = timedelta(minutes=15)
    def pending_deadline(self, created_at: datetime) -> datetime: ...
    def no_show_deadline(self, effective_start: datetime) -> datetime: ...
```

`pending_ttl` is configurable via environment (`HOLD_PENDING_TTL_MINUTES`).

## 4. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-CRON-01 | On creation, a reservation MUST store `hold_expires_at = created_at + HoldPolicy.pending_ttl`. |
| FR-CRON-02 | `PendingExpirySweep` MUST run on a recurring interval (default every 60 s) via the `Scheduler` port. |
| FR-CRON-03 | The sweep MUST query `find_expired_pending(now)` using the injected `Clock`, not `datetime.now()` directly. |
| FR-CRON-04 | For each expired pending, the system MUST, under a per-kit lock and in one UnitOfWork: re-check status is still PENDING, call `reservation.expire()`, `kit.release()`, `deposit.void()`, `schedule.remove(rid)`, emit `ReservationExpired`, commit. |
| FR-CRON-05 | The expiry action MUST be idempotent: if the reservation is no longer PENDING (already confirmed/cancelled), it MUST be skipped as a no-op. |
| FR-CRON-06 | `confirm()` and `expire()` MUST be mutually exclusive guards on PENDING; the per-kit lock + optimistic `version` MUST make the confirm-vs-expire race safe. |
| FR-CRON-07 | `NoShowSweep` MUST run on a recurring interval and flag CONFIRMED reservations past `no_show_deadline` as NO_SHOW. |
| FR-CRON-08 | Both sweeps MUST be self-healing after downtime: on the next tick they process everything currently overdue (no missed-tick backlog needed). |
| FR-CRON-09 | A sweep MUST process each candidate independently; one failure MUST NOT abort the whole batch. |
| FR-CRON-10 | Sweep behavior MUST be deterministically testable with a `FixedClock` by advancing time and asserting the resulting status. |

## 5. The confirm-vs-expire race (why it is safe)

```
             t0: reservation PENDING, hold_expires_at = t0+10m
   ┌──────────────────────────┬──────────────────────────┐
   │ Club calls confirm()     │ PendingExpirySweep fires  │
   │ acquire lock(kit_id) ────┼──> blocks                 │
   │ reload; status==PENDING  │                           │
   │ deposit.hold(); CONFIRMED│                           │
   │ commit; release lock ────┼──> acquire lock(kit_id)   │
   │                          │ reload; status==CONFIRMED │
   │                          │ guard fails -> no-op       │
   └──────────────────────────┴──────────────────────────┘
```

Both paths take `locks.acquire(kit_id)` and re-read status after loading, so they
serialize. Whichever commits first wins; the loser sees a non-PENDING status —
`confirm()` on an EXPIRED reservation raises `IllegalReservationTransitionError`,
and the sweep on a CONFIRMED reservation returns as a no-op. Optimistic `version`
is the backstop if the lock is ever bypassed.

## 6. Scheduler port + jobs (signatures)

```python
class Job(Protocol):
    def run(self) -> None: ...

class Scheduler(Protocol):
    def schedule_recurring(self, name: str, interval: timedelta, job: Job) -> None: ...
    def schedule_once(self, name: str, at: datetime, job: Job) -> None: ...   # delay-queue variant

class PendingExpirySweep(Job):
    def __init__(self, uow: UnitOfWork, coordinator: RelayCoordinator, clock: Clock): ...
    def run(self) -> None: ...   # for r in uow.reservations.find_expired_pending(clock.now()): coordinator.expire_pending(r.id)

class NoShowSweep(Job):
    def run(self) -> None: ...

class RelayCoordinator:
    def expire_pending(self, rid: ReservationId) -> None: ...
    def no_show_sweep(self) -> None: ...
```

Repository support:

```python
class ReservationRepository(Protocol):
    def find_expired_pending(self, now: datetime) -> list[Reservation]: ...  # PENDING AND hold_expires_at <= now
    def find_no_shows(self, now: datetime) -> list[Reservation]: ...
```

## 7. Wiring (composition root)

```python
scheduler.schedule_recurring("pending-expiry", timedelta(minutes=1),
                             PendingExpirySweep(uow, coordinator, clock))
scheduler.schedule_recurring("no-show",        timedelta(minutes=1),
                             NoShowSweep(uow, coordinator, clock))
```

## 8. Design alternative — delay queue (noted, not default)

Instead of polling, at creation call
`scheduler.schedule_once(hold_expires_at, ExpireReservationJob(rid))` for
to-the-second precision. Trade-off: needs a durable timer and misses are harder
to recover. The recurring sweep is primary because it is self-healing; the
one-shot can be layered in later if precise expiry timing is required.

## 9. Acceptance criteria

- A PENDING reservation whose `hold_expires_at` has passed is EXPIRED within one sweep interval, and its kit returns to AVAILABLE with the deposit voided.
- Confirming at the exact deadline either fully confirms (kit stays RESERVED→CONFIRMED) or cleanly fails as expired — never a half state.
- A CONFIRMED reservation never checked out past grace becomes NO_SHOW with the deposit forfeited.
- Advancing a `FixedClock` past the deadline in a test flips the status deterministically.
- Killing and restarting the scheduler still expires everything overdue on the next tick.
