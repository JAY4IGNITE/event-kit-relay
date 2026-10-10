"""Request/result DTOs for the application layer."""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import EquipmentType, ReservationId, ReservationStatus
from app.domain.value_objects.primitives import TimeSlot


@dataclass(frozen=True)
class ReservationRequest:
    club_id: str
    required_types: list[EquipmentType]
    desired_slot: TimeSlot
    idempotency_key: str


@dataclass(frozen=True)
class ReservationResult:
    reservation_id: ReservationId
    status: ReservationStatus
    effective_slot: TimeSlot
