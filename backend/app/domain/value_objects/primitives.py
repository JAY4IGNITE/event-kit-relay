"""Immutable value objects. Stubs — signatures only, logic to be implemented."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def duration(self) -> timedelta:
        return self.end - self.start

    def overlaps(self, other: "TimeSlot") -> bool:
        return max(self.start, other.start) < min(self.end, other.end)

    def gap_to(self, later: "TimeSlot") -> timedelta:
        return later.start - self.end

    def shifted_to(self, new_start: datetime) -> "TimeSlot":
        """Return a new slot starting at ``new_start`` preserving duration."""
        return TimeSlot(start=new_start, end=new_start + self.duration())

    def contains(self, t: datetime) -> bool:
        return self.start <= t <= self.end


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount, self.currency)

    def percentage(self, pct: Decimal) -> "Money":
        return Money(self.amount * (pct / Decimal(100)), self.currency)


@dataclass(frozen=True)
class TurnaroundWindow:
    """The mandatory inspection gap between two reservations (default 15 min)."""

    duration: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    def window_after(self, actual_return: datetime) -> TimeSlot:
        """Return ``[actual_return, actual_return + duration]``."""
        return TimeSlot(start=actual_return, end=actual_return + self.duration)


@dataclass(frozen=True)
class HoldPolicy:
    """Single source of truth for all time-based reservation deadlines."""

    pending_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=10))
    no_show_grace: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    def pending_deadline(self, created_at: datetime) -> datetime:
        return created_at + self.pending_ttl

    def no_show_deadline(self, effective_start: datetime) -> datetime:
        return effective_start + self.no_show_grace
