"""Domain events (Observer). Published by the relay, consumed by subscribers."""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DomainEvent(ABC):
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), kw_only=True
    )


@dataclass
class ReservationConfirmed(DomainEvent):
    reservation_id: str = ""


@dataclass
class ReservationExpired(DomainEvent):
    """Emitted when a PENDING hold is auto-rejected by the expiry cron."""

    reservation_id: str = ""
    club_id: str = ""


@dataclass
class ReservationNoShow(DomainEvent):
    reservation_id: str = ""
    club_id: str = ""


@dataclass
class KitReturnedLate(DomainEvent):
    reservation_id: str = ""
    minutes_late: int = 0


@dataclass
class InspectionFailed(DomainEvent):
    kit_id: str = ""
    faulty_items: list[str] = field(default_factory=list)


@dataclass
class EquipmentReplaced(DomainEvent):
    kit_id: str = ""
    replaced: list[str] = field(default_factory=list)


@dataclass
class ReservationRerouted(DomainEvent):
    reservation_id: str = ""
    new_kit_id: str = ""


@dataclass
class ReservationCancelled(DomainEvent):
    reservation_id: str = ""
    reason: str = ""


@dataclass
class DelayPropagated(DomainEvent):
    kit_id: str = ""
    shifts: list = field(default_factory=list)  # list[ScheduleShift]


@dataclass
class KitReadyForClub(DomainEvent):
    kit_id: str = ""
    club_id: str = ""


@dataclass
class DepositRefunded(DomainEvent):
    deposit_id: str = ""


@dataclass
class DepositForfeited(DomainEvent):
    deposit_id: str = ""
