"""EventKit aggregate + EquipmentSlot + Builder. Transitions delegate to KitState."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from app.domain.entities.equipment import Equipment, KitTemplate
from app.domain.enums import EquipmentType, KitId, KitStatusTag

if TYPE_CHECKING:
    from app.domain.states.kit_state import KitState


@dataclass
class EquipmentSlot:
    required_type: EquipmentType
    item: Optional[Equipment] = None

    def is_satisfied(self) -> bool:
        """Slot is satisfied iff an item is present AND usable."""
        raise NotImplementedError


class EventKit:
    """The complete shared physical kit — the resource relayed between clubs."""

    id: KitId
    slots: list[EquipmentSlot]
    version: int  # optimistic lock
    _state: "KitState"

    # ---- queries ----
    def is_complete(self) -> bool:
        raise NotImplementedError

    def all_usable(self) -> bool:
        raise NotImplementedError

    def is_reservable(self) -> bool:
        """Rule 1: AVAILABLE + complete + all usable."""
        raise NotImplementedError

    @property
    def status(self) -> KitStatusTag:
        raise NotImplementedError

    # ---- transitions (delegate to current state) ----
    def reserve(self) -> None:
        raise NotImplementedError

    def checkout(self) -> None:
        raise NotImplementedError

    def mark_returned(self) -> None:
        raise NotImplementedError

    def pass_inspection(self) -> None:
        raise NotImplementedError

    def fail_inspection(self) -> None:
        raise NotImplementedError

    def restore(self) -> None:
        raise NotImplementedError

    def release(self) -> None:
        """Release a soft hold: RESERVED -> AVAILABLE (used by pending-expiry cron)."""
        raise NotImplementedError

    def retire(self) -> None:
        raise NotImplementedError

    def swap(self, faulty: Equipment, spare: Equipment) -> None:
        raise NotImplementedError

    def _set_state(self, state: "KitState") -> None:
        raise NotImplementedError


class EventKitBuilder:
    """Builder — validated slot-by-slot assembly."""

    def for_template(self, template: KitTemplate) -> "EventKitBuilder":
        raise NotImplementedError

    def with_item(self, item: Equipment) -> "EventKitBuilder":
        raise NotImplementedError

    def build(self) -> EventKit:
        """Raise if any required slot is unfilled."""
        raise NotImplementedError
