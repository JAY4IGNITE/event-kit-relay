# Diagrams

## Kit lifecycle (State pattern)

```mermaid
stateDiagram-v2
    [*] --> AVAILABLE
    AVAILABLE --> RESERVED: reserve()
    RESERVED --> CHECKED_OUT: checkout()
    RESERVED --> AVAILABLE: release()  (soft hold / expiry)
    CHECKED_OUT --> AWAITING_INSPECTION: mark_returned()
    AWAITING_INSPECTION --> AVAILABLE: pass_inspection()
    AWAITING_INSPECTION --> UNDER_MAINTENANCE: fail_inspection()
    UNDER_MAINTENANCE --> AVAILABLE: restore()
    AVAILABLE --> RETIRED: retire()
    RETIRED --> [*]
```

## Reservation lifecycle (with crons)

```mermaid
stateDiagram-v2
    [*] --> PENDING: create_reservation()
    PENDING --> CONFIRMED: confirm() [deposit HELD]
    PENDING --> EXPIRED: expire() ⏰ pending-expiry cron
    PENDING --> CANCELLED: cancel() [manual]
    CONFIRMED --> ACTIVE: activate()
    CONFIRMED --> NO_SHOW: no-show cron ⏰
    CONFIRMED --> REROUTED: reroute()
    ACTIVE --> COMPLETED: complete()
    ACTIVE --> REROUTED: reroute()
    EXPIRED --> [*]
    CANCELLED --> [*]
    NO_SHOW --> [*]
    COMPLETED --> [*]
    REROUTED --> [*]
```

## Confirm vs pending-expiry race

```mermaid
sequenceDiagram
    participant Club
    participant Svc as ReservationService
    participant Cron as PendingExpirySweep
    participant Lock as LockManager
    Note over Club,Cron: reservation is PENDING, hold_expires_at reached
    par Club confirms
        Club->>Svc: confirm(rid)
        Svc->>Lock: acquire(kit_id)
        Svc->>Svc: reload; status==PENDING -> CONFIRMED; commit
        Svc->>Lock: release
    and Cron fires
        Cron->>Lock: acquire(kit_id)  (blocks until released)
        Cron->>Cron: reload; status==CONFIRMED -> no-op
    end
```

## Domain class diagram

```mermaid
classDiagram
    class Equipment
    Equipment <|-- Camera
    Equipment <|-- Mic
    Equipment <|-- Tripod
    Equipment <|-- Light

    class EventKit {
      +KitId id
      +int version
      +status() KitStatusTag
      +reserve()
      +checkout()
      +mark_returned()
      +release()
    }
    class EquipmentSlot
    class KitState
    EventKit "1" o-- "*" EquipmentSlot
    EquipmentSlot "1" --> "0..1" Equipment
    EventKit "1" --> "1" KitState
    KitState <|-- AvailableState
    KitState <|-- ReservedState
    KitState <|-- CheckedOutState
    KitState <|-- AwaitingInspectionState
    KitState <|-- UnderMaintenanceState

    class Reservation
    class KitSchedule
    class Deposit
    class Club
    KitSchedule "1" o-- "*" Reservation
    Reservation "1" --> "1" Club
    Reservation "1" --> "1" EventKit
    Reservation "1" --> "1" Deposit

    class RelayCoordinator
    class DelayResolutionStrategy
    class ReservationValidator
    class EventBus
    RelayCoordinator ..> DelayResolutionStrategy : selects
    RelayCoordinator ..> EventBus : publishes
```
