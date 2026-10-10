"""Inspection, Handover, KitCondition, Deposit, Club, Organizer entities."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.domain.enums import (
    ClubId,
    DepositId,
    DepositStatus,
    EquipmentId,
    EquipmentStatus,
    HandoverId,
    HandoverType,
    InspectionId,
    InspectionResult,
    KitId,
    LoyaltyTier,
    OrganizerId,
    ReservationId,
)
from app.domain.value_objects.primitives import Money, TimeSlot


class Inspection:
    id: InspectionId
    kit_id: KitId
    inspector_id: OrganizerId
    window: TimeSlot                 # [actual_return, +15min]
    result: InspectionResult
    faulty_items: list[EquipmentId]
    notes: str

    def complete(self, result: InspectionResult, faulty: list[EquipmentId]) -> None:
        raise NotImplementedError


class KitCondition:
    """Snapshot of every item's status at a handover — the audit record."""

    item_states: dict[EquipmentId, EquipmentStatus]
    acknowledged_by: str
    at: datetime

    def diff(
        self, later: "KitCondition"
    ) -> dict[EquipmentId, tuple[EquipmentStatus, EquipmentStatus]]:
        """diff(checkout, return) = custody-based damage attribution (Rule 10)."""
        raise NotImplementedError


class Handover:
    id: HandoverId
    reservation_id: ReservationId
    type: HandoverType
    at: datetime
    performed_by: str
    condition: KitCondition


class Deposit:
    id: DepositId
    reservation_id: ReservationId
    amount: Money
    status: DepositStatus

    def hold(self) -> None:
        raise NotImplementedError

    def refund(self) -> None:
        raise NotImplementedError

    def forfeit(self, amount: Money) -> None:
        """Full or partial forfeit (supports PARTIALLY_FORFEITED)."""
        raise NotImplementedError

    def void(self) -> None:
        """PENDING -> no charge, used when a soft hold expires before confirm."""
        raise NotImplementedError

    def is_refundable(self) -> bool:
        raise NotImplementedError


class Club:
    """Customer / college club. Aggregate root; loyalty mutated via subscriber."""

    id: ClubId
    name: str
    loyalty_score: int
    loyalty_tier: LoyaltyTier

    def request_reservation(self) -> None:
        raise NotImplementedError

    def can_reserve(self) -> bool:
        raise NotImplementedError

    def get_loyalty_tier(self) -> LoyaltyTier:
        raise NotImplementedError


class Organizer:
    """Admin who inspects kits and handles exceptions."""

    id: OrganizerId
    name: str
