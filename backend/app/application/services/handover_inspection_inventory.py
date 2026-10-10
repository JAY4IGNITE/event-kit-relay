"""Handover, Inspection, and Inventory application services."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.domain.entities.event_kit import EventKit
from app.domain.entities.misc import Handover, Inspection, KitCondition
from app.domain.enums import EquipmentId, InspectionId, InspectionResult, KitId, OrganizerId, ReservationId
from app.domain.specifications.kit_spec import KitSpecification


class HandoverService:
    def checkout(self, rid: ReservationId) -> Handover:
        """Require CONFIRMED reservation; kit -> CHECKED_OUT; record CHECKOUT."""
        raise NotImplementedError

    def return_kit(self, rid: ReservationId, condition: KitCondition) -> Handover:
        """Kit -> AWAITING_INSPECTION; record RETURN + actual_end."""
        raise NotImplementedError


class InspectionService:
    def open_window(
        self, kit_id: KitId, inspector: OrganizerId, actual_return: datetime
    ) -> Inspection:
        """Open [actual_return, actual_return + turnaround]."""
        raise NotImplementedError

    def complete(
        self, iid: InspectionId, result: InspectionResult, faulty: list[EquipmentId]
    ) -> None:
        raise NotImplementedError


class InventoryService:
    def find_reroute_candidate(self, spec: KitSpecification) -> Optional[EventKit]:
        raise NotImplementedError

    def replace_faulty(self, kit: EventKit, faulty: list[EquipmentId]) -> bool:
        raise NotImplementedError
