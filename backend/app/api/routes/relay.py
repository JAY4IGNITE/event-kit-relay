"""Reservation + handover + inspection routes (skeleton)."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.schemas import (
    CheckoutIn,
    CompleteInspectionIn,
    CreateReservationIn,
    ReservationOut,
    ReturnIn,
)

router = APIRouter(tags=["relay"])


@router.post("/reservations", response_model=ReservationOut)
async def create_reservation(body: CreateReservationIn) -> ReservationOut:
    raise NotImplementedError


@router.post("/reservations/{rid}/confirm")
async def confirm_reservation(rid: str) -> dict:
    raise NotImplementedError


@router.post("/reservations/{rid}/cancel")
async def cancel_reservation(rid: str, reason: str = "") -> dict:
    raise NotImplementedError


@router.get("/reservations/{rid}", response_model=ReservationOut)
async def get_reservation(rid: str) -> ReservationOut:
    raise NotImplementedError


@router.post("/handovers/checkout")
async def checkout(body: CheckoutIn) -> dict:
    raise NotImplementedError


@router.post("/handovers/return")
async def return_kit(body: ReturnIn) -> dict:
    raise NotImplementedError


@router.post("/inspections/{iid}/complete")
async def complete_inspection(iid: str, body: CompleteInspectionIn) -> dict:
    raise NotImplementedError
