"""Kit + club read routes and health check (skeleton)."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.schemas import KitOut

router = APIRouter(tags=["inventory"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/kits", response_model=list[KitOut])
async def list_kits() -> list[KitOut]:
    raise NotImplementedError


@router.get("/kits/{kit_id}/schedule")
async def kit_schedule(kit_id: str) -> dict:
    raise NotImplementedError


@router.get("/clubs/{club_id}")
async def get_club(club_id: str) -> dict:
    raise NotImplementedError
