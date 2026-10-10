"""Core enumerations and typed identifiers for the domain.

Typed IDs use ``NewType`` to avoid primitive obsession: a ``KitId`` cannot be
passed where a ``ClubId`` is expected without a type-checker complaint.
"""
from __future__ import annotations

from enum import Enum
from typing import NewType

# ---- Typed identifiers ----
ClubId = NewType("ClubId", str)
OrganizerId = NewType("OrganizerId", str)
KitId = NewType("KitId", str)
EquipmentId = NewType("EquipmentId", str)
ReservationId = NewType("ReservationId", str)
InspectionId = NewType("InspectionId", str)
DepositId = NewType("DepositId", str)
HandoverId = NewType("HandoverId", str)


class EquipmentType(str, Enum):
    CAMERA = "CAMERA"
    MIC = "MIC"
    TRIPOD = "TRIPOD"
    LIGHT = "LIGHT"


class EquipmentStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DAMAGED = "DAMAGED"
    MISSING = "MISSING"
    RETIRED = "RETIRED"


class KitStatusTag(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CHECKED_OUT = "CHECKED_OUT"
    AWAITING_INSPECTION = "AWAITING_INSPECTION"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    RETIRED = "RETIRED"


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    REROUTED = "REROUTED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    EXPIRED = "EXPIRED"  # pending hold lapsed -> auto-rejected


class DepositStatus(str, Enum):
    PENDING = "PENDING"
    HELD = "HELD"
    REFUNDED = "REFUNDED"
    FORFEITED = "FORFEITED"
    PARTIALLY_FORFEITED = "PARTIALLY_FORFEITED"


class HandoverType(str, Enum):
    CHECKOUT = "CHECKOUT"
    RETURN = "RETURN"


class InspectionResult(str, Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"


class LoyaltyTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
