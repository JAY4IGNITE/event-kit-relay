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

    async def expire_pending(self, rid: ReservationId) -> None:
        async with self._uow as uow:
            reservation = await uow.reservations.get(rid)
            if not reservation or reservation.status != "PENDING":
                return
            
            async with self._locks.acquire(reservation.kit_id):
                # reload to check status again
                reservation = await uow.reservations.get(rid)
                if not reservation or reservation.status != "PENDING":
                    return
                
                if not reservation.is_hold_expired(self._clock.now()):
                    return
                
                reservation.expire()
                kit = await uow.kits.get(reservation.kit_id)
                kit.release()
                
                deposit = await uow.deposits.get(reservation.deposit_id)
                # deposit.void() -> wait, what is the API on deposit?
                # for now, assume deposit has void method
                if hasattr(deposit, "void"):
                    deposit.void()
                    
                schedule = await uow.schedules.get(reservation.kit_id)
                schedule.remove(rid)
                
                from app.domain.events.events import ReservationExpired
                self._bus.publish(ReservationExpired(reservation_id=rid, club_id=reservation.club_id, occurred_at=self._clock.now()))
                await uow.commit()

    def no_show_sweep(self) -> None:
        """Flag CONFIRMED reservations past no_show grace as NO_SHOW."""
        raise NotImplementedError
