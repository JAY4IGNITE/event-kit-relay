# PRD — Reservations & Scheduling

**Module owner:** Backend
**IDs:** FR-RES-*
**Related:** `08-scheduling-crons.md` (hold expiry), `05-deposits.md`, `06-loyalty.md`

---

## 1. Purpose

Own the reservation lifecycle and the per-kit relay timeline (`KitSchedule`):
creation with validation, the soft-hold + confirm handshake, overlap and
turnaround enforcement, late-return resolution, and cascading delay propagation.

## 2. Reservation lifecycle

```
PENDING --confirm()[deposit HELD]--> CONFIRMED --activate()--> ACTIVE --complete()--> COMPLETED
   |                                     |                         |
   |--expire() [hold cron] --> EXPIRED   |--no_show cron--> NO_SHOW |--reroute--> REROUTED
   |--cancel() [manual] -----> CANCELLED |--reroute--> REROUTED
```

- **PENDING** holds the kit as a *soft hold* (kit = RESERVED, deposit = PENDING).
- **EXPIRED** / **CANCELLED** / **NO_SHOW** / **COMPLETED** / **REROUTED** are terminal.

## 3. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-RES-01 | The system MUST create a reservation in PENDING status with `booked_slot = effective_slot` and a `hold_expires_at = created_at + HoldPolicy.pending_ttl`. |
| FR-RES-02 | Creation MUST run the validator chain (availability → equipment condition → overlap → turnaround → club eligibility) and reject with a specific error on first failure. |
| FR-RES-03 | Creation MUST place a soft hold on the kit (RESERVED) and a PENDING deposit atomically in one UnitOfWork. |
| FR-RES-04 | Creation MUST be idempotent per `idempotency_key` — a retried submit returns the same reservation. |
| FR-RES-05 | `confirm()` MUST require status PENDING and a HELD deposit, then transition to CONFIRMED. Confirming an EXPIRED/CANCELLED reservation MUST raise `IllegalReservationTransitionError`. |
| FR-RES-06 | `cancel(reason)` MUST be allowed from PENDING or CONFIRMED, release the kit hold, and trigger deposit settlement. |
| FR-RES-07 | The system MUST preserve `booked_slot` unchanged for the life of the reservation (Rule 8). |
| FR-RES-08 | `effective_slot` MUST reflect operational delays and always preserve the original duration. |
| FR-RES-09 | Two reservations for the same kit MUST NOT overlap, and MUST be separated by at least `TurnaroundWindow.duration` (default 15 min). |
| FR-RES-10 | On a late return, `effective_start = MAX(booked_start, previous.actual_end + turnaround)`. |
| FR-RES-11 | A delay MUST cascade forward: each successor recomputes against its predecessor's effective end until one absorbs the slack. |
| FR-RES-12 | All kit mutations during create/relay MUST hold a per-kit lock and use optimistic `version` as a backstop. |

## 4. Key operations (signatures)

```python
class ReservationService:  # Facade
    def create_reservation(self, req: ReservationRequest) -> ReservationResult: ...
    def confirm(self, rid: ReservationId) -> None: ...
    def cancel(self, rid: ReservationId, reason: str) -> None: ...
    def get(self, rid: ReservationId) -> ReservationResult: ...

class KitSchedule:
    def has_capacity(self, slot: TimeSlot) -> bool: ...          # overlap + turnaround
    def propagate_delay(self, frm: Reservation, clock: Clock) -> list[ScheduleShift]: ...
    def snapshot(self) -> ScheduleMemento: ...
    def restore(self, m: ScheduleMemento) -> None: ...
```

## 5. Edge cases

- Confirm arrives in the same instant the hold-expiry cron fires → per-kit lock serializes; first commit wins, loser raises/no-ops (see `08-scheduling-crons.md`).
- Overlap check must consider the turnaround gap on both sides of the proposed slot.
- Cascading delay must stop at the first successor whose slack ≥ incoming delay (AbsorbDelayStrategy).

## 6. Acceptance criteria

- Creating two reservations for the same kit/slot concurrently yields exactly one success.
- A late return of A at 12:10 (sched end 12:00) with B booked 12:15 sets B.effective_start = 12:25 and shifts C accordingly.
- A PENDING reservation past `hold_expires_at` becomes EXPIRED and frees the kit (covered by cron PRD).
- `booked_slot` is byte-for-byte unchanged after any number of delay propagations.
