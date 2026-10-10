"""Unit test stubs for the pending-hold expiry cron and the confirm-vs-expire race.

Uses the FixedClock so time is deterministic.
"""
import pytest

from app.ports.clock import FixedClock
from datetime import datetime, timezone


@pytest.mark.skip(reason="scaffold: implement RelayCoordinator.expire_pending")
def test_pending_past_deadline_becomes_expired():
    # Given a PENDING reservation created at T with pending_ttl=10m
    # When the clock advances to T+11m and PendingExpirySweep runs
    # Then status == EXPIRED, kit back to AVAILABLE, deposit voided
    clock = FixedClock(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    assert clock.now().hour == 10


@pytest.mark.skip(reason="scaffold: implement confirm-vs-expire guard")
def test_confirm_after_expiry_raises():
    # Confirming an EXPIRED reservation must raise IllegalReservationTransitionError
    ...


@pytest.mark.skip(reason="scaffold: implement idempotent sweep")
def test_sweep_on_confirmed_is_noop():
    # expire_pending on an already-CONFIRMED reservation returns without change
    ...
