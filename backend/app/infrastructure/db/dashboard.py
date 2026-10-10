"""Persistent dashboard operations; commits include both the hold and its deposit.

The local SQLite runner uses one worker. PostgreSQL row locks serialize kit writes
across workers; optimistic versions and unique keys provide a second guard.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas.schemas import CreateReservationIn, KitOut, ReservationOut
from app.config import settings
from app.infrastructure.db.models.orm import (
    ClubModel, DepositModel, EquipmentModel, EventKitModel, ReservationModel,
)

LIVE = ("PENDING", "CONFIRMED", "ACTIVE")


def utc(value: datetime) -> datetime:
    # SQLite's DateTime adapter returns naive values even for timezone=True.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def reservation_out(row: ReservationModel) -> ReservationOut:
    return ReservationOut(reservation_id=row.id, status=row.status,
                          effective_start=utc(row.eff_start), effective_end=utc(row.eff_end))


async def get_reservation(session: AsyncSession, rid: str) -> ReservationModel:
    row = await session.get(ReservationModel, rid)
    if row is None:
        raise HTTPException(404, "Reservation not found")
    return row


async def kits(session: AsyncSession) -> list[EventKitModel]:
    return list(await session.scalars(select(EventKitModel).options(
        selectinload(EventKitModel.slots)).order_by(EventKitModel.id).with_for_update()))


async def usable_types(session: AsyncSession, kit: EventKitModel) -> list[str]:
    if not kit.slots or any(slot.equipment_id is None for slot in kit.slots):
        return []
    ids = [slot.equipment_id for slot in kit.slots]
    if len(set(ids)) != len(ids):
        return []
    items = {item.id: item for item in await session.scalars(
        select(EquipmentModel).where(EquipmentModel.id.in_(ids)))}
    for slot in kit.slots:
        item = items.get(slot.equipment_id)
        if item is None or item.status != "AVAILABLE" or item.type != slot.required_type:
            return []
    return [slot.required_type for slot in kit.slots]


async def list_kits(session: AsyncSession) -> list[KitOut]:
    return [KitOut(kit_id=k.id, status=k.status, complete=bool(await usable_types(session, k)))
            for k in await kits(session)]


async def refresh_kit_status(session: AsyncSession, kit: EventKitModel) -> None:
    if kit.status not in ("AVAILABLE", "RESERVED"):
        return
    active = await session.scalar(select(ReservationModel.id).where(
        ReservationModel.kit_id == kit.id, ReservationModel.status.in_(LIVE)).limit(1))
    kit.status = "RESERVED" if active else "AVAILABLE"


async def sweep(session: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    # Same lock order as create/confirm/cancel prevents scheduler races.
    inventory = await kits(session)
    rows = await session.scalars(select(ReservationModel).where(
        ReservationModel.status.in_(("PENDING", "CONFIRMED"))))
    changed = set()
    for row in rows:
        if row.status == "PENDING" and utc(row.hold_expires_at) <= now:
            row.status = "EXPIRED"
        elif row.status == "CONFIRMED" and utc(row.eff_start) + timedelta(
                minutes=settings.no_show_grace_minutes) <= now:
            row.status = "NO_SHOW"
        else:
            continue
        deposit = await session.get(DepositModel, row.deposit_id) if row.deposit_id else None
        if deposit:
            deposit.status = "VOIDED" if row.status == "EXPIRED" else "FORFEITED"
        changed.add(row.kit_id)
    await session.flush()
    for kit in inventory:
        if kit.id in changed:
            await refresh_kit_status(session, kit)
    await session.commit()


async def create(session: AsyncSession, body: CreateReservationIn) -> ReservationOut:
    inventory = await kits(session)
    existing = await session.scalar(select(ReservationModel).where(
        ReservationModel.idempotency_key == body.idempotency_key))
    requested = sorted(t.value for t in body.required_types)
    if existing:
        if (existing.club_id != body.club_id or utc(existing.booked_start) != body.start
                or utc(existing.booked_end) != body.end
                or sorted(existing.required_types) != requested):
            raise HTTPException(409, "Idempotency key already used for a different request")
        return reservation_out(existing)
    club = await session.get(ClubModel, body.club_id)
    if club is None:
        raise HTTPException(404, "Club not found")
    if club.loyalty_score < 0:
        raise HTTPException(422, "Club is not eligible to reserve a kit")
    now = datetime.now(timezone.utc)
    if body.end <= now:
        raise HTTPException(422, "Reservation must end in the future")
    gap = timedelta(minutes=settings.turnaround_minutes)
    for kit in inventory:
        if kit.status not in ("AVAILABLE", "RESERVED"):
            continue
        available = Counter(await usable_types(session, kit))
        if not available or Counter(requested) - available:
            continue
        conflict = await session.scalar(select(ReservationModel.id).where(
            ReservationModel.kit_id == kit.id,
            ReservationModel.status.in_(LIVE),
            ReservationModel.eff_start < body.end + gap,
            ReservationModel.eff_end > body.start - gap,
        ).limit(1))
        if conflict:
            continue
        rid, did = str(uuid4()), str(uuid4())
        row = ReservationModel(id=rid, club_id=body.club_id, kit_id=kit.id,
                               booked_start=body.start, booked_end=body.end,
                               eff_start=body.start, eff_end=body.end, status="PENDING",
                               created_at=now, hold_expires_at=now + timedelta(
                                   minutes=settings.hold_pending_ttl_minutes),
                               idempotency_key=body.idempotency_key,
                               required_types=requested, deposit_id=did)
        session.add(row)
        await session.flush()
        # Demo ledger only: no external payment is collected by this app.
        session.add(DepositModel(id=did, reservation_id=rid, amount=0,
                                 currency="INR", status="PENDING"))
        kit.status = "RESERVED"
        kit.version += 1
        await session.commit()
        return reservation_out(row)
    raise HTTPException(409, "No usable kit is available for this slot (15-minute inspection gap required)")


async def transition(session: AsyncSession, rid: str, action: str) -> ReservationOut:
    inventory = {kit.id: kit for kit in await kits(session)}
    row = await get_reservation(session, rid)
    target = "CONFIRMED" if action == "confirm" else "CANCELLED"
    if row.status == target:
        return reservation_out(row)
    allowed = ("PENDING",) if action == "confirm" else ("PENDING", "CONFIRMED")
    if row.status not in allowed:
        raise HTTPException(409, f"Cannot {action} a {row.status.lower()} reservation")
    deposit = await session.get(DepositModel, row.deposit_id) if row.deposit_id else None
    if action == "confirm":
        if not deposit or deposit.status != "PENDING":
            raise HTTPException(409, "Reservation has no pending deposit")
        deposit.status = "HELD"
    elif deposit:
        deposit.status = "VOIDED" if deposit.status == "PENDING" else "REFUNDED"
    row.status = target
    await session.flush()
    kit = inventory[row.kit_id]
    await refresh_kit_status(session, kit)
    kit.version += 1
    await session.commit()
    return reservation_out(row)
