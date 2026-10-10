"""State pattern for the EventKit lifecycle.

The base class makes every transition illegal by default; each concrete state
overrides only the transitions that are legal from it. Illegal transitions raise
:class:`IllegalKitTransitionError`, so the lifecycle is enforced structurally
rather than by scattered ``if`` checks.
"""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from app.domain.enums import KitStatusTag
from app.domain.errors.exceptions import IllegalKitTransitionError

if TYPE_CHECKING:
    from app.domain.entities.event_kit import EventKit


class KitState(ABC):
    tag: KitStatusTag

    def reserve(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def checkout(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def mark_returned(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def pass_inspection(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def fail_inspection(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def restore(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError

    def release(self, kit: "EventKit") -> None:
        raise IllegalKitTransitionError


class AvailableState(KitState):
    tag = KitStatusTag.AVAILABLE

    def reserve(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> ReservedState


class ReservedState(KitState):
    tag = KitStatusTag.RESERVED

    def checkout(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> CheckedOutState

    def release(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> AvailableState (soft hold released)


class CheckedOutState(KitState):
    tag = KitStatusTag.CHECKED_OUT

    def mark_returned(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> AwaitingInspectionState


class AwaitingInspectionState(KitState):
    tag = KitStatusTag.AWAITING_INSPECTION

    def pass_inspection(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> AvailableState

    def fail_inspection(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> UnderMaintenanceState


class UnderMaintenanceState(KitState):
    tag = KitStatusTag.UNDER_MAINTENANCE

    def restore(self, kit: "EventKit") -> None:
        raise NotImplementedError  # -> AvailableState


class RetiredState(KitState):
    tag = KitStatusTag.RETIRED
    # terminal — all transitions remain illegal
