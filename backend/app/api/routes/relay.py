"""Reservation + handover + inspection routes (skeleton)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import dashboard_session
from app.infrastructure.db import dashboard

from app.api.schemas.schemas import (
    CheckoutIn,
    CompleteInspectionIn,
    CreateReservationIn,
    ReservationOut,
    ReturnIn,
)

router = APIRouter(tags=["relay"])


@router.post("/reservations", response_model=ReservationOut)
async def create_reservation(
    body: CreateReservationIn, session: AsyncSession = Depends(dashboard_session),
) -> ReservationOut:
    return await dashboard.create(session, body)


@router.post("/reservations/{rid}/confirm", response_model=ReservationOut)
async def confirm_reservation(
    rid: str, session: AsyncSession = Depends(dashboard_session),
) -> ReservationOut:
    return await dashboard.transition(session, rid, "confirm")


@router.post("/reservations/{rid}/cancel", response_model=ReservationOut)
async def cancel_reservation(
    rid: str, reason: str = "", session: AsyncSession = Depends(dashboard_session),
) -> ReservationOut:
    return await dashboard.transition(session, rid, "cancel")


@router.get("/reservations/{rid}", response_model=ReservationOut)
async def get_reservation(
    rid: str, session: AsyncSession = Depends(dashboard_session),
) -> ReservationOut:
    return dashboard.reservation_out(await dashboard.get_reservation(session, rid))


@router.post("/handovers/checkout")
async def checkout(body: CheckoutIn) -> dict:
    raise HTTPException(501, "Checkout is not implemented in this dashboard demo")


@router.post("/handovers/return")
async def return_kit(body: ReturnIn) -> dict:
    raise HTTPException(501, "Returns are not implemented in this dashboard demo")


@router.post("/inspections/{iid}/complete")
async def complete_inspection(iid: str, body: CompleteInspectionIn) -> dict:
    raise HTTPException(501, "Inspections are not implemented in this dashboard demo")
