"""Dashboard API regression tests using an isolated, real SQLite database."""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.infrastructure.db.base import Base, get_session
from app.infrastructure.db.models.orm import (
    ClubModel,
    EquipmentModel,
    EventKitModel,
    KitSlotModel,
    ReservationModel,
)
from app.main import app


@pytest.fixture
async def dashboard():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with sessions() as session:
        session.add(ClubModel(id="club-demo", name="Demo Club"))
        session.add(EventKitModel(id="kit-demo", status="AVAILABLE"))
        for kind in ("CAMERA", "MIC", "TRIPOD", "LIGHT"):
            session.add(EquipmentModel(
                id=f"equipment-{kind}", name=kind, type=kind, status="AVAILABLE"
            ))
            session.add(KitSlotModel(
                id=f"slot-{kind}", kit_id="kit-demo", required_type=kind,
                equipment_id=f"equipment-{kind}",
            ))
        await session.commit()

    async def isolated_session():
        async with sessions() as session:
            yield session

    previous_override = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = isolated_session
    try:
        # ASGITransport deliberately does not run the production scheduler lifespan.
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_session, None)
        else:
            app.dependency_overrides[get_session] = previous_override
        await engine.dispose()


@pytest.fixture
def booking():
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    return {
        "club_id": "club-demo",
        "required_types": ["CAMERA", "MIC", "TRIPOD", "LIGHT"],
        "start": start.isoformat(),
        "end": (start + timedelta(hours=1)).isoformat(),
        "idempotency_key": "dashboard-booking",
    }


async def create_booking(client, booking):
    response = await client.post("/reservations", json=booking)
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.mark.asyncio
async def test_inventory_lists_complete_and_empty_kits(dashboard):
    client, sessions = dashboard
    async with sessions() as session:
        session.add(EventKitModel(id="empty-kit", status="AVAILABLE"))
        await session.commit()
    response = await client.get("/kits")
    assert response.status_code == 200, response.text
    kits = {kit["kit_id"]: kit for kit in response.json()}
    assert kits["kit-demo"]["complete"] is True
    assert kits["empty-kit"]["complete"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize("field,value", [("status", "DAMAGED"), ("type", "MIC")])
async def test_unusable_equipment_makes_kit_unselectable(dashboard, booking, field, value):
    client, sessions = dashboard
    async with sessions() as session:
        camera = await session.get(EquipmentModel, "equipment-CAMERA")
        setattr(camera, field, value)
        await session.commit()
    inventory = await client.get("/kits")
    assert inventory.status_code == 200, inventory.text
    assert inventory.json()[0]["complete"] is False
    response = await client.post("/reservations", json=booking)
    assert response.status_code == 409, response.text


@pytest.mark.asyncio
async def test_club_details_and_missing_club(dashboard):
    client, _ = dashboard
    response = await client.get("/clubs/club-demo")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Demo Club"
    assert (await client.get("/clubs/missing")).status_code == 404


@pytest.mark.asyncio
async def test_create_confirm_and_get_return_complete_reservation(dashboard, booking):
    client, _ = dashboard
    created = await create_booking(client, booking)
    assert created["status"] == "PENDING"
    assert datetime.fromisoformat(created["effective_start"]) == datetime.fromisoformat(booking["start"])
    assert datetime.fromisoformat(created["effective_end"]) == datetime.fromisoformat(booking["end"])
    rid = created["reservation_id"]
    confirmed = await client.post(f"/reservations/{rid}/confirm")
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json() == {**created, "status": "CONFIRMED"}
    fetched = await client.get(f"/reservations/{rid}")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json() == confirmed.json()


@pytest.mark.asyncio
async def test_idempotency_reuses_reservation_and_rejects_different_payload(dashboard, booking):
    client, _ = dashboard
    first = await create_booking(client, booking)
    repeated = await create_booking(client, booking)
    assert repeated == first
    changed = {**booking, "end": (
        datetime.fromisoformat(booking["end"]) + timedelta(minutes=30)
    ).isoformat()}
    conflict = await client.post("/reservations", json=changed)
    assert conflict.status_code == 409, conflict.text


@pytest.mark.asyncio
@pytest.mark.parametrize("confirm", [False, True])
async def test_cancellation_releases_reserved_window(dashboard, booking, confirm):
    client, _ = dashboard
    created = await create_booking(client, booking)
    rid = created["reservation_id"]
    if confirm:
        response = await client.post(f"/reservations/{rid}/confirm")
        assert response.status_code == 200, response.text
    cancelled = await client.post(f"/reservations/{rid}/cancel", params={"reason": "Event cancelled"})
    assert cancelled.status_code == 200, cancelled.text
    fetched = await client.get(f"/reservations/{rid}")
    assert fetched.json()["status"] == "CANCELLED"
    replacement = await create_booking(client, {**booking, "idempotency_key": "replacement"})
    assert replacement["reservation_id"] != rid


@pytest.mark.asyncio
@pytest.mark.parametrize("gap_minutes,expected_status", [(-30, 409), (0, 409), (14, 409), (15, 200)])
async def test_overlaps_and_turnaround_boundary(dashboard, booking, gap_minutes, expected_status):
    client, _ = dashboard
    await create_booking(client, booking)
    next_start = datetime.fromisoformat(booking["end"]) + timedelta(minutes=gap_minutes)
    response = await client.post("/reservations", json={
        **booking, "idempotency_key": "second-booking", "start": next_start.isoformat(),
        "end": (next_start + timedelta(hours=1)).isoformat(),
    })
    if expected_status == 200:
        assert response.status_code in (200, 201), response.text
    else:
        assert response.status_code == expected_status, response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_case", ["inverted", "timezoneless", "empty_types"])
async def test_invalid_reservation_input_is_rejected(dashboard, booking, invalid_case):
    client, _ = dashboard
    if invalid_case == "inverted":
        booking["start"], booking["end"] = booking["end"], booking["start"]
    elif invalid_case == "timezoneless":
        booking["start"] = datetime.fromisoformat(booking["start"]).replace(tzinfo=None).isoformat()
    else:
        booking["required_types"] = []
    response = await client.post("/reservations", json=booking)
    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_reservation_for_unknown_club_is_not_found(dashboard, booking):
    client, _ = dashboard
    response = await client.post("/reservations", json={**booking, "club_id": "missing"})
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_expired_hold_is_persisted_and_cannot_be_confirmed(dashboard, booking):
    client, sessions = dashboard
    created = await create_booking(client, booking)
    rid = created["reservation_id"]
    async with sessions() as session:
        reservation = await session.get(ReservationModel, rid)
        reservation.hold_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()
    response = await client.post(f"/reservations/{rid}/confirm")
    assert response.status_code in (409, 422), response.text
    async with sessions() as session:
        assert (await session.get(ReservationModel, rid)).status == "EXPIRED"
        assert (await session.get(EventKitModel, "kit-demo")).status == "AVAILABLE"
    replacement = await create_booking(client, {**booking, "idempotency_key": "after-expiry"})
    assert replacement["reservation_id"] != rid


@pytest.mark.asyncio
async def test_kit_schedule_is_available_and_missing_kit_is_not_found(dashboard, booking):
    client, _ = dashboard
    created = await create_booking(client, booking)
    response = await client.get("/kits/kit-demo/schedule")
    assert response.status_code == 200, response.text
    assert created["reservation_id"] in response.text
    assert (await client.get("/kits/missing/schedule")).status_code == 404
