"""Unit test stubs for the kit State machine.

These are intentionally skipped — they document the intended behavior and will
be enabled once the domain logic is implemented.
"""
import pytest


from app.domain.entities.event_kit import EventKit, EquipmentSlot
from app.domain.states.kit_state import AvailableState, ReservedState
from app.domain.enums import KitId
from app.domain.errors.exceptions import IllegalKitTransitionError


def test_available_kit_can_be_reserved():
    kit = EventKit()
    kit.id = KitId("k1")
    kit.slots = []
    kit.version = 1
    kit._set_state(AvailableState())
    kit.reserve()
    assert kit.status.value == "RESERVED"


def test_illegal_transition_raises():
    kit = EventKit()
    kit.id = KitId("k1")
    kit.slots = []
    kit.version = 1
    kit._set_state(AvailableState())
    with pytest.raises(IllegalKitTransitionError):
        kit.checkout()


def test_reserved_kit_release_returns_to_available():
    kit = EventKit()
    kit.id = KitId("k1")
    kit.slots = []
    kit.version = 1
    kit._set_state(ReservedState())
    kit.release()
    assert kit.status.value == "AVAILABLE"
