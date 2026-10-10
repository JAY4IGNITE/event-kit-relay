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
        raise NotImplementedError

    def overlaps(self, other: "TimeSlot") -> bool:
        raise NotImplementedError

    def gap_to(self, later: "TimeSlot") -> timedelta:
        raise NotImplementedError

    def shifted_to(self, new_start: datetime) -> "TimeSlot":
        """Return a new slot starting at ``new_start`` preserving duration."""
        raise NotImplementedError

    def contains(self, t: datetime) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"

    def __add__(self, other: "Money") -> "Money":
        raise NotImplementedError

    def __sub__(self, other: "Money") -> "Money":
        raise NotImplementedError

    def percentage(self, pct: Decimal) -> "Money":
        raise NotImplementedError


@dataclass(frozen=True)
class TurnaroundWindow:
    """The mandatory inspection gap between two reservations (default 15 min)."""

    duration: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    def window_after(self, actual_return: datetime) -> TimeSlot:
        """Return ``[actual_return, actual_return + duration]``."""
        raise NotImplementedError


@dataclass(frozen=True)
class HoldPolicy:
    """Single source of truth for all time-based reservation deadlines."""

    pending_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=10))
    no_show_grace: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    def pending_deadline(self, created_at: datetime) -> datetime:
        raise NotImplementedError

    def no_show_deadline(self, effective_start: datetime) -> datetime:
        raise NotImplementedError
