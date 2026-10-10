"""Policy objects (Strategy) for deposits, loyalty, and turnaround."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.enums import LoyaltyTier
from app.domain.value_objects.primitives import TurnaroundWindow

if TYPE_CHECKING:
    from app.domain.entities.misc import Inspection
    from app.domain.entities.reservation import Reservation
    from app.domain.events.events import DomainEvent


class DepositPolicy(ABC):
    @abstractmethod
    def settle(self, reservation: "Reservation", inspection: "Inspection") -> list["DomainEvent"]:
        ...


class StandardDepositPolicy(DepositPolicy):
    """Clean + on-time -> refund; damage/late/no-show -> forfeit (Rule 15)."""

    def settle(self, reservation: "Reservation", inspection: "Inspection") -> list["DomainEvent"]:
        raise NotImplementedError


class LoyaltyPolicy(ABC):
    @abstractmethod
    def delta_for(self, event: "DomainEvent") -> int:
        ...

    @abstractmethod
    def tier_for(self, score: int) -> LoyaltyTier:
        ...

    @abstractmethod
    def can_reserve(self, score: int) -> bool:
        ...


class StandardLoyaltyPolicy(LoyaltyPolicy):
    def delta_for(self, event: "DomainEvent") -> int:
        raise NotImplementedError

    def tier_for(self, score: int) -> LoyaltyTier:
        raise NotImplementedError

    def can_reserve(self, score: int) -> bool:
        raise NotImplementedError


class TurnaroundPolicy:
    """Single source of truth for the mandatory inspection window length."""

    window: TurnaroundWindow
