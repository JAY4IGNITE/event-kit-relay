"""Repository and UnitOfWork ports (Protocols)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol

from app.domain.entities.event_kit import EventKit
from app.domain.entities.misc import Club, Deposit
from app.domain.entities.reservation import KitSchedule, Reservation
from app.domain.enums import ClubId, DepositId, KitId, ReservationId
from app.domain.value_objects.primitives import TimeSlot


class ReservationRepository(Protocol):
    def get(self, rid: ReservationId) -> Reservation: ...
    def save(self, r: Reservation) -> None:
        """Persist; raise ConcurrencyConflictError on version mismatch."""
        ...

    def overlapping(self, kit_id: KitId, slot: TimeSlot) -> list[Reservation]: ...
    def find_expired_pending(self, now: datetime) -> list[Reservation]:
        """PENDING AND hold_expires_at <= now (drives the expiry cron)."""
        ...

    def find_no_shows(self, now: datetime) -> list[Reservation]: ...


class EventKitRepository(Protocol):
    def get(self, kit_id: KitId) -> EventKit: ...
    def save(self, kit: EventKit) -> None: ...
    def list_all(self) -> list[EventKit]: ...


class KitScheduleRepository(Protocol):
    def for_kit(self, kit_id: KitId) -> KitSchedule: ...
    def save(self, schedule: KitSchedule) -> None: ...


class ClubRepository(Protocol):
    def get(self, club_id: ClubId) -> Club: ...
    def save(self, club: Club) -> None: ...


class DepositRepository(Protocol):
    def get(self, deposit_id: DepositId) -> Deposit: ...
    def save(self, deposit: Deposit) -> None: ...


class UnitOfWork(Protocol):
    """Transactional boundary over all repositories."""

    reservations: ReservationRepository
    kits: EventKitRepository
    schedules: KitScheduleRepository
    clubs: ClubRepository
    deposits: DepositRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *exc) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
