"""Equipment hierarchy + Factory, Abstract Factory (templates), and Builder."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from app.domain.enums import EquipmentId, EquipmentStatus, EquipmentType


class Equipment(ABC):
    """An individual physical item inside an EventKit."""

    id: EquipmentId
    name: str
    type: EquipmentType
    status: EquipmentStatus

    def mark_damaged(self) -> None:
        raise NotImplementedError

    def mark_missing(self) -> None:
        raise NotImplementedError

    def mark_available(self) -> None:
        raise NotImplementedError

    def retire(self) -> None:
        raise NotImplementedError

    def is_usable(self) -> bool:
        """Usable iff status is AVAILABLE."""
        raise NotImplementedError

    @abstractmethod
    def spec_summary(self) -> dict:
        ...


class Camera(Equipment):
    resolution: str

    def spec_summary(self) -> dict:
        raise NotImplementedError


class Mic(Equipment):
    wireless: bool

    def spec_summary(self) -> dict:
        raise NotImplementedError


class Tripod(Equipment):
    max_height_cm: int

    def spec_summary(self) -> dict:
        raise NotImplementedError


class Light(Equipment):
    wattage: int

    def spec_summary(self) -> dict:
        raise NotImplementedError


class EquipmentFactory:
    """Factory Method — hides the concrete subclass behind an EquipmentType."""

    @staticmethod
    def create(type: EquipmentType, **specs) -> Equipment:
        raise NotImplementedError


class KitTemplate(Protocol):
    """Abstract Factory — defines which equipment types a kind of kit requires."""

    def required_types(self) -> list[EquipmentType]:
        ...


class StandardAVKit:
    """CAMERA, MIC, TRIPOD, LIGHT."""

    def required_types(self) -> list[EquipmentType]:
        raise NotImplementedError


class PodcastKit:
    """MIC, MIC, LIGHT."""

    def required_types(self) -> list[EquipmentType]:
        raise NotImplementedError
