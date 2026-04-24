import uuid
import enum
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class MealStatus(str, enum.Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    PENDING = "pending"
    REJECTED = "rejected"


class SlotType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class SlotStatus(str, enum.Enum):
    SUGGESTED = "suggested"
    CONFIRMED = "confirmed"
    SKIPPED = "skipped"
    REPLACED = "replaced"


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class ContributionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CategorySlug(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"
    ANY = "any"
