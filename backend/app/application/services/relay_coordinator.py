"""RelayCoordinator — the heart: return -> inspect -> resolve -> notify.

Also owns the two cron actions: ``expire_pending`` (PENDING hold auto-reject)
and ``no_show_sweep`` (CONFIRMED never checked out).
"""
from __future__ import annotations

from datetime import datetime

from app.domain.enums import ReservationId
from app.ports.clock import Clock
from app.ports.repositories import UnitOfWork
from app.ports.services import EventBus, LockManager


class RelayCoordinator:
    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
        clock: Clock,
        locks: LockManager,
    ) -> None:
        self._uow = uow
        self._bus = event_bus
        self._clock = clock
        self._locks = locks

    def run_relay(self, rid: ReservationId, actual_return: datetime) -> None:
        """Return recorded -> open inspection -> PASS/FAIL -> resolve -> notify.

        Snapshots the schedule (Memento) before any risky reroute and restores
        it on failure, then rolls back the UnitOfWork.
        """
        raise NotImplementedError

    def expire_pending(self, rid: ReservationId) -> None:
        """Auto-reject one PENDING hold whose deadline passed (FR-CRON-04).

        Under locks.acquire(kit_id), in one UnitOfWork:
          reload; if status != PENDING: return   # idempotent no-op
          if not is_hold_expired(now): return
          reservation.expire(); kit.release(); deposit.void(); schedule.remove(rid)
          publish(ReservationExpired); commit
        """
        raise NotImplementedError

    def no_show_sweep(self) -> None:
        """Flag CONFIRMED reservations past no_show grace as NO_SHOW."""
        raise NotImplementedError
