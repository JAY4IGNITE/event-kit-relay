"""Clock port — all 'now' reads go through this so tests can pin/advance time."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class SystemClock:
    """Production clock."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock:
    """Test clock — pins 'now' and allows advancing it."""

    def __init__(self, at: datetime) -> None:
        self._at = at

    def now(self) -> datetime:
        return self._at

    def advance(self, **kwargs) -> None:
        from datetime import timedelta

        self._at = self._at + timedelta(**kwargs)
