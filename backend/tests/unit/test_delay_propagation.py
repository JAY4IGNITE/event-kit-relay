"""Unit test stubs for cascading delay propagation (uses FixedClock)."""
import pytest


from datetime import datetime, timezone, timedelta
from app.domain.entities.reservation import Reservation, KitSchedule
from app.domain.value_objects.primitives import TimeSlot, TurnaroundWindow
from app.domain.enums import ReservationStatus
from app.ports.clock import FixedClock


def _make_res(start, end, res_id="r1"):
    r = Reservation()
    r.id = res_id
    r.booked_slot = TimeSlot(start, end)
    r.effective_slot = TimeSlot(start, end)
    r.actual_end = None
    r.status = ReservationStatus.PENDING
    return r


def test_late_return_shifts_next_effective_start():
    clock = FixedClock(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    rA = _make_res(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc), datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc), "rA")
    rB = _make_res(datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc), datetime(2026, 1, 1, 14, 0, tzinfo=timezone.utc), "rB")
    
    schedule = KitSchedule()
    schedule.kit_id = "k1"
    schedule.turnaround = TurnaroundWindow(timedelta(minutes=15))
    schedule.add(rA)
    schedule.add(rB)
    
    # A returns late at 12:10
    rA.actual_end = datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc)
    
    schedule.propagate_delay(rA, clock)
    
    assert rB.effective_slot.start == datetime(2026, 1, 1, 12, 25, tzinfo=timezone.utc)


def test_delay_cascades_to_third_reservation():
    clock = FixedClock(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    rA = _make_res(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc), datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc), "rA")
    rB = _make_res(datetime(2026, 1, 1, 11, 15, tzinfo=timezone.utc), datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc), "rB")
    rC = _make_res(datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc), datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc), "rC")
    
    schedule = KitSchedule()
    schedule.kit_id = "k1"
    schedule.turnaround = TurnaroundWindow(timedelta(minutes=15))
    schedule.add(rA)
    schedule.add(rB)
    schedule.add(rC)
    
    # A returns late at 11:10
    rA.actual_end = datetime(2026, 1, 1, 11, 10, tzinfo=timezone.utc)
    
    schedule.propagate_delay(rA, clock)
    
    # B needs 15min turnaround, so starts at 11:25 and ends at 12:10.
    # C needs 15min turnaround after B's end, but B's effective end is 12:10, 
    # so C needs to start at 12:25
    assert rB.effective_slot.start == datetime(2026, 1, 1, 11, 25, tzinfo=timezone.utc)
    assert rB.effective_slot.end == datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc)
    assert rC.effective_slot.start == datetime(2026, 1, 1, 12, 25, tzinfo=timezone.utc)


def test_booked_slot_never_mutated():
    clock = FixedClock(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    rA = _make_res(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc), datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc), "rA")
    rB = _make_res(datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc), datetime(2026, 1, 1, 14, 0, tzinfo=timezone.utc), "rB")
    original_booked = rB.booked_slot
    
    schedule = KitSchedule()
    schedule.kit_id = "k1"
    schedule.turnaround = TurnaroundWindow(timedelta(minutes=15))
    schedule.add(rA)
    schedule.add(rB)
    
    rA.actual_end = datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc)
    schedule.propagate_delay(rA, clock)
    
    assert rB.booked_slot == original_booked
    assert rB.effective_slot != original_booked
