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
        if self.status != ReservationStatus.PENDING:
            from app.domain.errors.exceptions import IllegalReservationTransitionError
            raise IllegalReservationTransitionError(f"Cannot confirm reservation in status {self.status}")
        self.status = ReservationStatus.CONFIRMED

    def activate(self) -> None:
        if self.status != ReservationStatus.CONFIRMED:
            from app.domain.errors.exceptions import IllegalReservationTransitionError
            raise IllegalReservationTransitionError(f"Cannot activate reservation in status {self.status}")
        self.status = ReservationStatus.ACTIVE

    def complete(self, actual_end: datetime) -> None:
        self.status = ReservationStatus.COMPLETED
        self.actual_end = actual_end

    def cancel(self, reason: str) -> None:
        self.status = ReservationStatus.CANCELLED

    def expire(self) -> None:
        """PENDING -> EXPIRED (auto-reject by the hold cron). Raise if not PENDING."""
        if self.status != ReservationStatus.PENDING:
            from app.domain.errors.exceptions import IllegalReservationTransitionError
            raise IllegalReservationTransitionError(f"Cannot expire reservation in status {self.status}")
        self.status = ReservationStatus.EXPIRED

    def mark_no_show(self) -> None:
        self.status = ReservationStatus.NO_SHOW

    def is_late(self) -> bool:
        """actual_end > booked_slot.end."""
        if not self.actual_end: return False
        return self.actual_end > self.booked_slot.end

    def is_hold_expired(self, now: datetime) -> bool:
        """status == PENDING and now >= hold_expires_at."""
        return self.status == ReservationStatus.PENDING and now >= self.hold_expires_at

    def shift_effective_start(self, new_start: datetime) -> None:
        """Move effective_slot to new_start, preserving duration."""
        self.effective_slot = self.effective_slot.shifted_to(new_start)

    def overlaps(self, other: "Reservation") -> bool:
        return self.effective_slot.overlaps(other.effective_slot)


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
        if not hasattr(self, "_reservations"):
            self._reservations = []
        self._reservations.append(r)
        self._reservations.sort(key=lambda x: x.effective_slot.start)

    def remove(self, rid: ReservationId) -> None:
        if not hasattr(self, "_reservations"):
            self._reservations = []
        self._reservations = [r for r in self._reservations if r.id != rid]

    def next_after(self, r: Reservation) -> Optional[Reservation]:
        if not hasattr(self, "_reservations"):
            self._reservations = []
        for res in self._reservations:
            if res.effective_slot.start >= r.effective_slot.end and res.id != r.id:
                return res
        return None

    def has_capacity(self, slot: TimeSlot) -> bool:
        """No overlap AND turnaround gap preserved on both sides."""
        if not hasattr(self, "_reservations"):
            self._reservations = []
        for r in self._reservations:
            if r.effective_slot.overlaps(slot):
                return False
            # Check gap
            if r.effective_slot.start < slot.start:
                if r.effective_slot.gap_to(slot) < self.turnaround.duration:
                    return False
            else:
                if slot.gap_to(r.effective_slot) < self.turnaround.duration:
                    return False
        return True

    def propagate_delay(self, frm: Reservation, clock: "Clock") -> list[ScheduleShift]:
        """Cascade: effective_start = MAX(booked_start, prev.actual_end + turnaround)."""
        shifts = []
        current = frm
        while current:
            nxt = self.next_after(current)
            if not nxt:
                break
            
            # calculate required start
            if current.actual_end:
                required_start = current.actual_end + self.turnaround.duration
            else:
                required_start = current.effective_slot.end + self.turnaround.duration
                
            new_start = max(nxt.booked_slot.start, required_start)
            
            if new_start > nxt.effective_slot.start:
                old_slot = nxt.effective_slot
                nxt.shift_effective_start(new_start)
                shifts.append(ScheduleShift(nxt.id, old_slot, nxt.effective_slot))
                current = nxt
            else:
                break # slack absorbed the delay
        return shifts

    def snapshot(self) -> ScheduleMemento:
        if not hasattr(self, "_reservations"):
            self._reservations = []
        return ScheduleMemento(
            kit_id=self.kit_id,
            slots=tuple((r.id, r.effective_slot) for r in self._reservations)
        )

    def restore(self, m: ScheduleMemento) -> None:
        if not hasattr(self, "_reservations"):
            self._reservations = []
        slot_map = dict(m.slots)
        for r in self._reservations:
            if r.id in slot_map:
                r.effective_slot = slot_map[r.id]
        self._reservations.sort(key=lambda x: x.effective_slot.start)
