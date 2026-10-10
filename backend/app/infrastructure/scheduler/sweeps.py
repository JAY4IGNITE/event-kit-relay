"""APScheduler adapter + the two sweep jobs (pending-expiry and no-show)."""
from __future__ import annotations

from datetime import timedelta

from app.application.services.relay_coordinator import RelayCoordinator
from app.ports.clock import Clock
from app.ports.repositories import UnitOfWork
from app.ports.services import Job, Scheduler


class APSchedulerAdapter:
    """Implements the Scheduler port over APScheduler (in-process)."""

    def __init__(self) -> None:
        # from apscheduler.schedulers.asyncio import AsyncIOScheduler
        # self._sched = AsyncIOScheduler()
        raise NotImplementedError

    def schedule_recurring(self, name: str, interval: timedelta, job: Job) -> None:
        raise NotImplementedError

    def schedule_once(self, name: str, at, job: Job) -> None:
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError


class PendingExpirySweep(Job):
    """FR-CRON-02..06: auto-reject PENDING holds past their deadline.

    for r in uow.reservations.find_expired_pending(clock.now()):
        coordinator.expire_pending(r.id)   # each under its own per-kit lock
    """

    def __init__(self, uow: UnitOfWork, coordinator: RelayCoordinator, clock: Clock) -> None:
        self._uow = uow
        self._coordinator = coordinator
        self._clock = clock

    def run(self) -> None:
        raise NotImplementedError


class NoShowSweep(Job):
    """FR-CRON-07: flag CONFIRMED reservations never checked out past grace."""

    def __init__(self, uow: UnitOfWork, coordinator: RelayCoordinator, clock: Clock) -> None:
        self._uow = uow
        self._coordinator = coordinator
        self._clock = clock

    def run(self) -> None:
        raise NotImplementedError
