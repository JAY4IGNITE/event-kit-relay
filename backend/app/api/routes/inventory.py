"""Kit + club read routes and health check."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.schemas import KitOut
from app.api.dependencies import dashboard_session
from app.infrastructure.db import dashboard
from app.infrastructure.db.models.orm import ClubModel, EventKitModel, ReservationModel

router = APIRouter(tags=["inventory"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/kits", response_model=list[KitOut])
async def list_kits(session: AsyncSession = Depends(dashboard_session)) -> list[KitOut]:
    return await dashboard.list_kits(session)


@router.get("/kits/{kit_id}/schedule")
async def kit_schedule(kit_id: str, session: AsyncSession = Depends(dashboard_session)) -> dict:
    if await session.get(EventKitModel, kit_id) is None:
        raise HTTPException(404, "Kit not found")
    rows = await session.scalars(select(ReservationModel).where(
        ReservationModel.kit_id == kit_id).order_by(ReservationModel.eff_start))
    return {"kit_id": kit_id, "reservations": [dashboard.reservation_out(r) for r in rows]}


@router.get("/clubs/{club_id}")
async def get_club(club_id: str, session: AsyncSession = Depends(dashboard_session)) -> dict:
    club = await session.get(ClubModel, club_id)
    if club is None:
        raise HTTPException(404, "Club not found")
    return {"club_id": club.id, "name": club.name,
            "loyalty_score": club.loyalty_score, "loyalty_tier": club.loyalty_tier}
