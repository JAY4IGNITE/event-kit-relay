"""Pydantic request/response schemas for the HTTP API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import EquipmentType


class CreateReservationIn(BaseModel):
    club_id: str
    required_types: list[EquipmentType]
    start: datetime
    end: datetime
    idempotency_key: str


class ReservationOut(BaseModel):
    reservation_id: str
    status: str
    effective_start: datetime
    effective_end: datetime


class CheckoutIn(BaseModel):
    reservation_id: str


class ReturnIn(BaseModel):
    reservation_id: str
    actual_end: datetime
    item_states: dict[str, str]  # equipment_id -> status at return


class CompleteInspectionIn(BaseModel):
    result: str  # PASS | FAIL
    faulty_items: list[str] = []
    notes: str = ""


class KitOut(BaseModel):
    kit_id: str
    status: str
    complete: bool
