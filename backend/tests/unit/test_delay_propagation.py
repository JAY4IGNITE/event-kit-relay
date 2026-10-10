"""Unit test stubs for cascading delay propagation (uses FixedClock)."""
import pytest


@pytest.mark.skip(reason="scaffold: implement KitSchedule.propagate_delay")
def test_late_return_shifts_next_effective_start():
    # A sched 10:00-12:00, returns 12:10; B booked 12:15
    # expect B.effective_start == 12:25  (MAX(12:15, 12:10+15m))
    ...


@pytest.mark.skip(reason="scaffold: implement cascade")
def test_delay_cascades_to_third_reservation():
    # A->B->C; A late pushes B which pushes C until slack absorbs it
    ...


@pytest.mark.skip(reason="scaffold: booked_slot immutability")
def test_booked_slot_never_mutated():
    # after any propagation, booked_slot is unchanged (Rule 8)
    ...
