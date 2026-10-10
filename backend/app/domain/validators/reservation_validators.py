"""Chain of Responsibility — reservation validation pipeline."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.application.dto.reservation_dto import ReservationRequest
    from app.domain.entities.event_kit import EventKit
    from app.domain.entities.misc import Club
    from app.domain.entities.reservation import KitSchedule
    from app.ports.clock import Clock


@dataclass
class ValidationContext:
    kit: "EventKit"
    schedule: "KitSchedule"
    club: "Club"
    clock: "Clock"


class ReservationValidator(ABC):
    _next: Optional["ReservationValidator"] = None

    def set_next(self, nxt: "ReservationValidator") -> "ReservationValidator":
        """Link and return ``nxt`` so chains read fluently."""
        self._next = nxt
        return nxt

    def validate(self, req: "ReservationRequest", ctx: ValidationContext) -> None:
        """Run this link's check, then delegate to the next (if any)."""
        self._check(req, ctx)
        if self._next is not None:
            self._next.validate(req, ctx)

    @abstractmethod
    def _check(self, req: "ReservationRequest", ctx: ValidationContext) -> None:
        """Raise a specific KitRelayError subclass on failure."""
        ...


class KitAvailabilityValidator(ReservationValidator):
    def _check(self, req, ctx) -> None:
        raise NotImplementedError


class EquipmentConditionValidator(ReservationValidator):
    def _check(self, req, ctx) -> None:
        raise NotImplementedError


class SlotOverlapValidator(ReservationValidator):
    def _check(self, req, ctx) -> None:
        raise NotImplementedError


class TurnaroundWindowValidator(ReservationValidator):
    def _check(self, req, ctx) -> None:
        raise NotImplementedError


class ClubEligibilityValidator(ReservationValidator):
    def _check(self, req, ctx) -> None:
        raise NotImplementedError


def build_default_chain() -> ReservationValidator:
    """availability -> condition -> overlap -> turnaround -> eligibility."""
    head = KitAvailabilityValidator()
    (
        head.set_next(EquipmentConditionValidator())
        .set_next(SlotOverlapValidator())
        .set_next(TurnaroundWindowValidator())
        .set_next(ClubEligibilityValidator())
    )
    return head
