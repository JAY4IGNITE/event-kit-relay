"""In-process EventBus + console Notifier + event subscribers."""
from __future__ import annotations

from collections import defaultdict
from typing import Union

from app.domain.enums import ClubId, OrganizerId
from app.domain.events.events import DomainEvent
from app.ports.services import EventSubscriber


class InProcessEventBus:
    """Synchronous in-memory bus. Swap for an outbox/queue in production."""

    def __init__(self) -> None:
        self._subs: dict[type, list[EventSubscriber]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], sub: EventSubscriber) -> None:
        self._subs[event_type].append(sub)

    def publish(self, event: DomainEvent) -> None:
        for sub in self._subs.get(type(event), []):
            sub.handle(event)


class ConsoleNotifier:
    """Notifier port adapter that logs to stdout (v1)."""

    def send(self, to: Union[ClubId, OrganizerId], message: str) -> None:
        print(f"[NOTIFY -> {to}] {message}")


class NotificationSubscriber(EventSubscriber):
    """Maps domain events to notifications (Observer)."""

    def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError


class LoyaltySubscriber(EventSubscriber):
    """Applies LoyaltyPolicy.delta_for and recomputes tier."""

    def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError


class AuditSubscriber(EventSubscriber):
    """Persists custody/condition diffs to the audit ledger."""

    def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError
