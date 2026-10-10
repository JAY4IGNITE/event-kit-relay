"""Pydantic request/response schemas for the HTTP API."""
from __future__ import annotations

from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from app.domain.enums import EquipmentType


class CreateReservationIn(BaseModel):
    club_id: str = Field(min_length=1, max_length=100)
    required_types: list[EquipmentType] = Field(min_length=1, max_length=20)
    start: AwareDatetime
    end: AwareDatetime
    idempotency_key: str = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def valid_slot(self) -> "CreateReservationIn":
        if self.end <= self.start:
            raise ValueError("End must be after start")
        return self


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
