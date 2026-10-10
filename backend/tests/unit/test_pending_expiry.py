"""Unit test stubs for the pending-hold expiry cron and the confirm-vs-expire race.

Uses the FixedClock so time is deterministic.
"""
import pytest

from app.ports.clock import FixedClock
from datetime import datetime, timezone


from unittest.mock import AsyncMock, MagicMock
from app.application.services.relay_coordinator import RelayCoordinator
from app.domain.entities.reservation import Reservation, KitSchedule
from app.domain.entities.event_kit import EventKit
from app.domain.enums import ReservationStatus, KitStatusTag
from app.domain.states.kit_state import ReservedState


@pytest.mark.asyncio
async def test_pending_past_deadline_becomes_expired():
    clock = FixedClock(datetime(2026, 1, 1, 10, 11, tzinfo=timezone.utc))
    
    # Setup mock UoW
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    
    res = Reservation()
    res.id = "r1"
    res.kit_id = "k1"
    res.club_id = "c1"
    res.deposit_id = "d1"
    res.status = ReservationStatus.PENDING
    res.hold_expires_at = datetime(2026, 1, 1, 10, 10, tzinfo=timezone.utc)
    uow.reservations.get.return_value = res
    
    kit = EventKit()
    kit.id = "k1"
    kit._set_state(ReservedState())
    uow.kits.get.return_value = kit
    
    deposit = MagicMock()
    uow.deposits.get.return_value = deposit
    
    schedule = KitSchedule()
    schedule._reservations = [res]
    uow.schedules.get.return_value = schedule
    
    bus = MagicMock()
    locks = MagicMock()
    lock_instance = AsyncMock()
    lock_instance.__aenter__.return_value = None
    lock_instance.__aexit__.return_value = None
    locks.acquire.return_value = lock_instance
    
    coord = RelayCoordinator(uow, bus, clock, locks)
    await coord.expire_pending("r1")
    
    assert res.status == ReservationStatus.EXPIRED
    assert kit.status == KitStatusTag.AVAILABLE
    deposit.void.assert_called_once()
    assert "r1" not in [r.id for r in getattr(schedule, "_reservations", [])]
    bus.publish.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_confirm_after_expiry_raises():
    res = Reservation()
    res.status = ReservationStatus.PENDING
    res.expire()
    
    from app.domain.errors.exceptions import IllegalReservationTransitionError
    with pytest.raises(IllegalReservationTransitionError):
        res.confirm()


@pytest.mark.asyncio
async def test_sweep_on_confirmed_is_noop():
    clock = FixedClock(datetime(2026, 1, 1, 10, 11, tzinfo=timezone.utc))
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    
    res = Reservation()
    res.status = ReservationStatus.CONFIRMED
    uow.reservations.get.return_value = res
    
    coord = RelayCoordinator(uow, MagicMock(), clock, AsyncMock())
    await coord.expire_pending("r1")
    
    # Should return early without acquiring locks or changing status
    assert res.status == ReservationStatus.CONFIRMED
    uow.commit.assert_not_called()
