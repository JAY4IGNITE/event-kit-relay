"""Reservation entity + KitSchedule (relay timeline) + Memento."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.domain.enums import ClubId, DepositId, KitId, ReservationId, ReservationStatus
from app.domain.value_objects.primitives import TimeSlot, TurnaroundWindow

if TYPE_CHECKING:
    from app.ports.clock import Clock


class Reservation:
    """One club's booking of one kit for a time slot."""

    id: ReservationId
    club_id: ClubId
    kit_id: KitId
    booked_slot: TimeSlot          # original intent — never mutated (Rule 8)
    effective_slot: TimeSlot       # operational — shifts with delay (Rule 9)
    actual_end: Optional[datetime]
    status: ReservationStatus
    deposit_id: DepositId
    created_at: datetime
    hold_expires_at: datetime      # created_at + HoldPolicy.pending_ttl
    version: int

    def confirm(self) -> None:
        """PENDING (+ deposit HELD) -> CONFIRMED. Raise if not PENDING."""
        raise NotImplementedError

    def activate(self) -> None:
        raise NotImplementedError

    def complete(self, actual_end: datetime) -> None:
        raise NotImplementedError

    def cancel(self, reason: str) -> None:
        raise NotImplementedError

    def expire(self) -> None:
        """PENDING -> EXPIRED (auto-reject by the hold cron). Raise if not PENDING."""
        raise NotImplementedError

    def mark_no_show(self) -> None:
        raise NotImplementedError

    def is_late(self) -> bool:
        """actual_end > booked_slot.end."""
        raise NotImplementedError

    def is_hold_expired(self, now: datetime) -> bool:
        """status == PENDING and now >= hold_expires_at."""
        raise NotImplementedError

    def shift_effective_start(self, new_start: datetime) -> None:
        """Move effective_slot to new_start, preserving duration."""
        raise NotImplementedError

    def overlaps(self, other: "Reservation") -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class ScheduleShift:
    reservation_id: ReservationId
    old: TimeSlot
    new: TimeSlot


@dataclass(frozen=True)
class ScheduleMemento:
    kit_id: KitId
    slots: tuple[tuple[ReservationId, TimeSlot], ...]


class KitSchedule:
    """Ordered relay timeline of reservations for one kit."""

    kit_id: KitId
    turnaround: TurnaroundWindow
    _reservations: list[Reservation]  # kept time-ordered

    def add(self, r: Reservation) -> None:
        raise NotImplementedError

    def remove(self, rid: ReservationId) -> None:
        raise NotImplementedError

    def next_after(self, r: Reservation) -> Optional[Reservation]:
        raise NotImplementedError

    def has_capacity(self, slot: TimeSlot) -> bool:
        """No overlap AND turnaround gap preserved on both sides."""
        raise NotImplementedError

    def propagate_delay(self, frm: Reservation, clock: "Clock") -> list[ScheduleShift]:
        """Cascade: effective_start = MAX(booked_start, prev.actual_end + turnaround)."""
        raise NotImplementedError

    def snapshot(self) -> ScheduleMemento:
        raise NotImplementedError

    def restore(self, m: ScheduleMemento) -> None:
        raise NotImplementedError
