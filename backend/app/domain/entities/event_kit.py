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
        return self.item is not None and self.item.status.is_usable()


class EventKit:
    """The complete shared physical kit — the resource relayed between clubs."""

    id: KitId
    slots: list[EquipmentSlot]
    version: int  # optimistic lock
    _state: "KitState"

    # ---- queries ----
    def is_complete(self) -> bool:
        return all(slot.item is not None for slot in self.slots)

    def all_usable(self) -> bool:
        return all(slot.is_satisfied() for slot in self.slots)

    def is_reservable(self) -> bool:
        """Rule 1: AVAILABLE + complete + all usable."""
        return self.status == KitStatusTag.AVAILABLE and self.is_complete() and self.all_usable()

    @property
    def status(self) -> KitStatusTag:
        return self._state.tag

    # ---- transitions (delegate to current state) ----
    def reserve(self) -> None:
        self._state.reserve(self)

    def checkout(self) -> None:
        self._state.checkout(self)

    def mark_returned(self) -> None:
        self._state.mark_returned(self)

    def pass_inspection(self) -> None:
        self._state.pass_inspection(self)

    def fail_inspection(self) -> None:
        self._state.fail_inspection(self)

    def restore(self) -> None:
        self._state.restore(self)

    def release(self) -> None:
        """Release a soft hold: RESERVED -> AVAILABLE (used by pending-expiry cron)."""
        self._state.release(self)

    def retire(self) -> None:
        raise NotImplementedError

    def swap(self, faulty: Equipment, spare: Equipment) -> None:
        raise NotImplementedError

    def _set_state(self, state: "KitState") -> None:
        self._state = state


class EventKitBuilder:
    """Builder — validated slot-by-slot assembly."""

    def for_template(self, template: KitTemplate) -> "EventKitBuilder":
        raise NotImplementedError

    def with_item(self, item: Equipment) -> "EventKitBuilder":
        raise NotImplementedError

    def build(self) -> EventKit:
        """Raise if any required slot is unfilled."""
        raise NotImplementedError
