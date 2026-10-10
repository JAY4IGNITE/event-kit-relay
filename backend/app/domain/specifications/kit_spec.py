"""Specification pattern — composable kit matching for reroute."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.enums import EquipmentType
from app.domain.value_objects.primitives import TimeSlot

if TYPE_CHECKING:
    from app.domain.entities.event_kit import EventKit


class KitSpecification(ABC):
    @abstractmethod
    def is_satisfied_by(self, kit: "EventKit") -> bool:
        ...

    def __and__(self, other: "KitSpecification") -> "KitSpecification":
        return _AndSpec(self, other)

    def __or__(self, other: "KitSpecification") -> "KitSpecification":
        return _OrSpec(self, other)

    def __invert__(self) -> "KitSpecification":
        return _NotSpec(self)


class _AndSpec(KitSpecification):
    def __init__(self, a: KitSpecification, b: KitSpecification) -> None:
        self.a, self.b = a, b

    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError


class _OrSpec(KitSpecification):
    def __init__(self, a: KitSpecification, b: KitSpecification) -> None:
        self.a, self.b = a, b

    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError


class _NotSpec(KitSpecification):
    def __init__(self, inner: KitSpecification) -> None:
        self.inner = inner

    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError


class IsReservableSpec(KitSpecification):
    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError


class HasRequiredEquipmentSpec(KitSpecification):
    def __init__(self, required: list[EquipmentType]) -> None:
        self.required = required

    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError


class FreeForSlotSpec(KitSpecification):
    def __init__(self, slot: TimeSlot) -> None:
        self.slot = slot

    def is_satisfied_by(self, kit: "EventKit") -> bool:
        raise NotImplementedError
