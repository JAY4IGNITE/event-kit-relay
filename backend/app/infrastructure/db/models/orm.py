"""SQLAlchemy ORM models (schema skeleton). Mapped to the tables in 01-architecture.md.

Note the ``version_id_col`` on mutable aggregates — SQLAlchemy raises
StaleDataError on a concurrent write, which the repository maps to
ConcurrencyConflictError.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class ClubModel(Base):
    __tablename__ = "clubs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    loyalty_score: Mapped[int] = mapped_column(Integer, default=0)
    loyalty_tier: Mapped[str] = mapped_column(String, default="BRONZE")


class OrganizerModel(Base):
    __tablename__ = "organizers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class EquipmentModel(Base):
    __tablename__ = "equipment"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="AVAILABLE")
    specs: Mapped[dict] = mapped_column(JSON, default=dict)


class EventKitModel(Base):
    __tablename__ = "event_kits"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, default="AVAILABLE")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}
    slots: Mapped[list["KitSlotModel"]] = relationship(back_populates="kit")


class KitSlotModel(Base):
    __tablename__ = "kit_slots"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kit_id: Mapped[str] = mapped_column(ForeignKey("event_kits.id"))
    required_type: Mapped[str] = mapped_column(String)
    equipment_id: Mapped[str | None] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    kit: Mapped[EventKitModel] = relationship(back_populates="slots")


class KitScheduleModel(Base):
    __tablename__ = "kit_schedules"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kit_id: Mapped[str] = mapped_column(ForeignKey("event_kits.id"))
    turnaround_minutes: Mapped[int] = mapped_column(Integer, default=15)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}


class ReservationModel(Base):
    __tablename__ = "reservations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    club_id: Mapped[str] = mapped_column(ForeignKey("clubs.id"))
    kit_id: Mapped[str] = mapped_column(ForeignKey("event_kits.id"))
    booked_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    booked_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    eff_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    eff_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    hold_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String, unique=True)
    required_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    deposit_id: Mapped[str | None] = mapped_column(String, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}


class InspectionModel(Base):
    __tablename__ = "inspections"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kit_id: Mapped[str] = mapped_column(ForeignKey("event_kits.id"))
    inspector_id: Mapped[str] = mapped_column(ForeignKey("organizers.id"))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    result: Mapped[str] = mapped_column(String, default="PENDING")
    faulty_items: Mapped[dict] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(String, default="")


class HandoverModel(Base):
    __tablename__ = "handovers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    reservation_id: Mapped[str] = mapped_column(ForeignKey("reservations.id"))
    type: Mapped[str] = mapped_column(String)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    performed_by: Mapped[str] = mapped_column(String)


class KitConditionModel(Base):
    __tablename__ = "kit_conditions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    handover_id: Mapped[str] = mapped_column(ForeignKey("handovers.id"))
    item_states: Mapped[dict] = mapped_column(JSON, default=dict)
    acknowledged_by: Mapped[str] = mapped_column(String)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DepositModel(Base):
    __tablename__ = "deposits"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    reservation_id: Mapped[str] = mapped_column(ForeignKey("reservations.id"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String, default="INR")
    status: Mapped[str] = mapped_column(String, default="PENDING")


class DomainEventModel(Base):
    __tablename__ = "domain_events"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed: Mapped[bool] = mapped_column(default=False)
