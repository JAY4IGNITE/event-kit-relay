# PRD — Relay, Inspection & Damage Handling

**Module owner:** Backend
**IDs:** FR-REL-*
**Related:** `04-inventory.md`, `07-notifications.md`

---

## 1. Purpose

Own the physical relay: checkout, return, the mandatory 15-minute inspection
window, PASS/PASS outcomes, and damage resolution (replace → reroute → cancel).
Coordinated by `RelayCoordinator`, which is the heart of the system.

## 2. Kit lifecycle (State pattern)

```
AVAILABLE --reserve--> RESERVED --checkout--> CHECKED_OUT --mark_returned--> AWAITING_INSPECTION
                           |                                                    |
                           |--release--> AVAILABLE                PASS --> AVAILABLE
                                                                  FAIL --> UNDER_MAINTENANCE --restore--> AVAILABLE
```

Illegal transitions raise `IllegalKitTransitionError`. Legality lives in the state classes, not scattered `if`s.

## 3. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-REL-01 | Checkout MUST require a CONFIRMED reservation and transition the kit CHECKED_OUT, recording a CHECKOUT handover with a KitCondition snapshot. |
| FR-REL-02 | Return MUST transition the kit AWAITING_INSPECTION and record a RETURN handover with a KitCondition snapshot and `actual_end`. |
| FR-REL-03 | Every return MUST open an inspection window `[actual_end, actual_end + 15min]` before the kit can be reused (Rule 3, 4). |
| FR-REL-04 | Inspection completion with result PASS MUST transition the kit AVAILABLE and trigger delay propagation to the successor. |
| FR-REL-05 | Inspection completion with result FAIL MUST transition the kit UNDER_MAINTENANCE and start damage handling. |
| FR-REL-06 | Damage handling MUST attempt, in order: (1) replace faulty items from spares, (2) reroute the successor to another suitable kit, (3) cancel the successor. |
| FR-REL-07 | If replacement succeeds, the kit MUST be restored to AVAILABLE and the successor keeps its reservation. |
| FR-REL-08 | Reroute MUST use the Specification `IsReservableSpec & HasRequiredEquipmentSpec(types) & FreeForSlotSpec(slot)` to find a candidate. |
| FR-REL-09 | Damage MUST be attributed via `KitCondition.diff(checkout, return)` to the club that held the kit — never the next club (Rule 10). |
| FR-REL-10 | The relay MUST snapshot the schedule before a risky reroute and restore it on failure (Memento), then roll back the UnitOfWork. |
| FR-REL-11 | Each relay outcome MUST publish domain events (KitReturnedLate, InspectionFailed, EquipmentReplaced, ReservationRerouted, ReservationCancelled, DelayPropagated, KitReadyForClub) for subscribers. |

## 4. Key operations (signatures)

```python
class HandoverService:
    def checkout(self, rid: ReservationId) -> Handover: ...
    def return_kit(self, rid: ReservationId, condition: KitCondition) -> Handover: ...

class InspectionService:
    def open_window(self, kit_id: KitId, inspector: OrganizerId, actual_return: datetime) -> Inspection: ...
    def complete(self, iid: InspectionId, result: InspectionResult, faulty: list[EquipmentId]) -> None: ...

class RelayCoordinator:
    def run_relay(self, rid: ReservationId, actual_return: datetime) -> None: ...
```

## 5. Damage decision tree

```
Inspection FAIL
  ├─ spare available for each faulty type? ── yes ─> replace -> kit AVAILABLE -> keep successor
  └─ no
       ├─ alternative kit matches spec? ── yes ─> reroute successor -> notify
       └─ no ─> cancel successor -> refund per deposit policy -> notify
```

## 6. Acceptance criteria

- A FAIL with an available spare restores the kit and preserves the successor's reservation.
- A FAIL with no spare but an alternative kit reroutes the successor and emits ReservationRerouted.
- A FAIL with no spare and no alternative cancels the successor and emits ReservationCancelled.
- Damage on the camera between checkout(AVAILABLE) and return(DAMAGED) is attributed to the returning club only.
- A reroute that fails mid-way leaves the schedule identical to its pre-relay snapshot.
