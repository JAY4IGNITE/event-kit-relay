"""pytest fixtures shared across tests."""
from datetime import datetime, timezone

import pytest

from app.ports.clock import FixedClock


@pytest.fixture
def fixed_clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
