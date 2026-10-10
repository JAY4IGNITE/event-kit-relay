"""Exception hierarchy rooted at :class:`KitRelayError`."""
from __future__ import annotations


class KitRelayError(Exception):
    """Root for every domain error — single catch boundary at the API edge."""


class KitUnavailableError(KitRelayError):
    """A kit is damaged, incomplete, or already reserved (Rule 1)."""


class IllegalKitTransitionError(KitRelayError):
    """An attempted kit state transition is not legal from the current state."""


class IllegalReservationTransitionError(KitRelayError):
    """An attempted reservation transition is not legal (e.g. confirm after expire)."""


class ReservationOverlapError(KitRelayError):
    """A proposed slot overlaps an existing reservation or violates turnaround."""


class TurnaroundViolationError(KitRelayError):
    """The mandatory inspection window is not satisfied (Rule 4/5)."""


class ClubNotEligibleError(KitRelayError):
    """The club fails the loyalty eligibility gate."""


class NoAlternativeKitError(KitRelayError):
    """Reroute search exhausted with no suitable kit (Rule 13)."""


class InspectionInProgressError(KitRelayError):
    """An operation was attempted while inspection is still open."""


class DepositOperationError(KitRelayError):
    """An invalid deposit state transition was attempted."""


class ConcurrencyConflictError(KitRelayError):
    """An optimistic-lock version mismatch — the caller should retry."""
