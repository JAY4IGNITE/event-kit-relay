"""Remaining ports: EventBus, LockManager, Scheduler/Job, Notifier."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import ContextManager, Protocol, Union

from app.domain.enums import ClubId, OrganizerId
from app.domain.events.events import DomainEvent


class EventSubscriber(Protocol):
    def handle(self, event: DomainEvent) -> None: ...


class EventBus(Protocol):
    def subscribe(self, event_type: type[DomainEvent], sub: EventSubscriber) -> None: ...
    def publish(self, event: DomainEvent) -> None: ...


class LockManager(Protocol):
    def acquire(self, key: str) -> ContextManager[None]:
        """Serialize mutations per key (e.g. per kit_id)."""
        ...


class Notifier(Protocol):
    def send(self, to: Union[ClubId, OrganizerId], message: str) -> None: ...


class Job(Protocol):
    def run(self) -> None: ...


class Scheduler(Protocol):
    def schedule_recurring(self, name: str, interval: timedelta, job: Job) -> None: ...
    def schedule_once(self, name: str, at: datetime, job: Job) -> None: ...
    def start(self) -> None: ...
    def shutdown(self) -> None: ...
