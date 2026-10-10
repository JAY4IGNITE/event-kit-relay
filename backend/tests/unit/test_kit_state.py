"""Unit test stubs for the kit State machine.

These are intentionally skipped — they document the intended behavior and will
be enabled once the domain logic is implemented.
"""
import pytest


@pytest.mark.skip(reason="scaffold: implement EventKit state transitions")
def test_available_kit_can_be_reserved():
    ...


@pytest.mark.skip(reason="scaffold: implement EventKit state transitions")
def test_illegal_transition_raises():
    # e.g. checkout() on an AVAILABLE (not RESERVED) kit must raise
    # IllegalKitTransitionError
    ...


@pytest.mark.skip(reason="scaffold: implement soft-hold release")
def test_reserved_kit_release_returns_to_available():
    ...
