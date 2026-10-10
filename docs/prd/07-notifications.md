# PRD — Notifications

**Module owner:** Backend
**IDs:** FR-NOT-*
**Pattern:** Observer (event subscriber) over a `Notifier` port.

---

## 1. Purpose

Send notifications to clubs and organizers on every reservation exception.
Notifications are a subscriber reacting to domain events — the relay never calls
the notifier directly.

## 2. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-NOT-01 | On a late return, the next club MUST be notified of the delay and its new effective start. |
| FR-NOT-02 | On damage, the organizer MUST be notified with the faulty items. |
| FR-NOT-03 | On reroute, the affected club MUST be notified of the new kit assignment. |
| FR-NOT-04 | On cancellation, the affected club MUST be notified with the reason. |
| FR-NOT-05 | On pending-hold expiry (EXPIRED), the club MUST be notified that its hold was auto-rejected. |
| FR-NOT-06 | When a kit becomes ready, the next club MUST be notified. |
| FR-NOT-07 | The notifier MUST be a port with at least a console/log adapter in v1 (email adapter optional). |
| FR-NOT-08 | Notification delivery MUST NOT block or fail the relay transaction (fire-and-log). |

## 3. Key operations (signatures)

```python
class Notifier(Protocol):
    def send(self, to: ClubId | OrganizerId, message: str) -> None: ...

class NotificationSubscriber(EventSubscriber):
    def handle(self, event: DomainEvent) -> None: ...   # maps event -> recipient + message
```

## 4. Event → notification map

| Event | Recipient | Message |
|-------|-----------|---------|
| KitReturnedLate | next club | "Your kit is delayed; new start HH:MM." |
| InspectionFailed | organizer | "Kit {id} failed inspection: {items}." |
| ReservationRerouted | club | "Reassigned to kit {id}." |
| ReservationCancelled | club | "Reservation cancelled: {reason}." |
| ReservationExpired | club | "Reservation auto-rejected: hold expired." |
| KitReadyForClub | club | "Your kit is ready for pickup." |

## 5. Acceptance criteria

- Each listed event produces exactly one notification to the correct recipient.
- A failing notifier logs an error but does not roll back the relay.
