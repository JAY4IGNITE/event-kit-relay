"""ReservationService — Facade over the reservation subsystem."""
from __future__ import annotations

from app.application.dto.reservation_dto import ReservationRequest, ReservationResult
from app.domain.enums import ReservationId
from app.domain.validators.reservation_validators import ReservationValidator
from app.domain.strategies.delay import DelayPolicy
from app.ports.clock import Clock
from app.ports.repositories import UnitOfWork
from app.ports.services import EventBus, LockManager


class ReservationService:
    """Single entry point: validation, soft hold, deposit, confirm, cancel.

    Hides InventoryService / InspectionService / DepositPolicy / Notifier behind
    one interface (Facade pattern).
    """

    def __init__(
        self,
        uow: UnitOfWork,
        validators: ReservationValidator,
        delay_policy: DelayPolicy,
        event_bus: EventBus,
        clock: Clock,
        locks: LockManager,
    ) -> None:
        self._uow = uow
        self._validators = validators
        self._delay_policy = delay_policy
        self._bus = event_bus
        self._clock = clock
        self._locks = locks

    def create_reservation(self, req: ReservationRequest) -> ReservationResult:
        """Validate, place a soft hold + PENDING deposit, set hold_expires_at.

        Runs under a per-kit lock inside one UnitOfWork; idempotent on
        ``req.idempotency_key``.
        """
        raise NotImplementedError

    def confirm(self, rid: ReservationId) -> None:
        """PENDING + deposit HELD -> CONFIRMED. Guarded against the expiry race."""
        raise NotImplementedError

    def cancel(self, rid: ReservationId, reason: str) -> None:
        raise NotImplementedError

    def get(self, rid: ReservationId) -> ReservationResult:
        raise NotImplementedError
