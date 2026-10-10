"""Strategy pattern — late-return / delay resolution."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.domain.enums import KitId

if TYPE_CHECKING:
    from app.domain.entities.reservation import Reservation
    from app.domain.events.events import DomainEvent


@dataclass
class DelayContext:
    delayed: "Reservation"
    successor: Optional["Reservation"]
    inspection_end: datetime
    alternative_kit: Optional[KitId]


class DelayResolutionStrategy(ABC):
    @abstractmethod
    def resolve(self, ctx: DelayContext) -> list["DomainEvent"]:
        ...


class AbsorbDelayStrategy(DelayResolutionStrategy):
    """Successor has enough slack; no shift needed."""

    def resolve(self, ctx: DelayContext) -> list["DomainEvent"]:
        raise NotImplementedError


class DelayNextCustomerStrategy(DelayResolutionStrategy):
    """Shift the successor's effective slot forward."""

    def resolve(self, ctx: DelayContext) -> list["DomainEvent"]:
        raise NotImplementedError


class RerouteStrategy(DelayResolutionStrategy):
    """Move the successor to another suitable kit."""

    def resolve(self, ctx: DelayContext) -> list["DomainEvent"]:
        raise NotImplementedError


class CancelStrategy(DelayResolutionStrategy):
    """No option remains; cancel the successor and refund."""

    def resolve(self, ctx: DelayContext) -> list["DomainEvent"]:
        raise NotImplementedError


class DelayPolicy:
    """Selects the appropriate strategy based on delay magnitude and availability."""

    def select(self, ctx: DelayContext) -> DelayResolutionStrategy:
        raise NotImplementedError
