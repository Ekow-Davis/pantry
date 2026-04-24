import uuid
from datetime import datetime, date, timezone
from typing import List, Optional
from sqlalchemy import (
    String, Boolean, Integer, Float, Text, Date, DateTime,
    ForeignKey, UniqueConstraint, Enum as SAEnum, ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

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


# ── Helpers ───────────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.USER, nullable=False
    )
    country: Mapped[Optional[str]] = mapped_column(String(100))
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Accra")
    cooldown_days: Mapped[int] = mapped_column(Integer, default=4)
    assume_cooked: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # relationships
    meal_preferences: Mapped[List["UserMealPreference"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_plans: Mapped[List["DailyPlan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    blacklist: Mapped[List["UserBlacklist"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    pantry: Mapped[List["UserPantry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    log_entries: Mapped[List["MealLogEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    contributions: Mapped[List["MealContribution"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


# ── Meal Categories ───────────────────────────────────────────────────────────

class MealCategory(Base):
    __tablename__ = "meal_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[CategorySlug] = mapped_column(
        SAEnum(CategorySlug), unique=True, nullable=False
    )

    meal_mappings: Mapped[List["MealCategoryMap"]] = relationship(
        back_populates="category"
    )


# ── Meal Category Map (junction) ──────────────────────────────────────────────

class MealCategoryMap(Base):
    __tablename__ = "meal_category_map"
    __table_args__ = (UniqueConstraint("meal_id", "category_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    meal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meal_categories.id", ondelete="CASCADE"), nullable=False
    )

    meal: Mapped["Meal"] = relationship(back_populates="category_mappings")
    category: Mapped["MealCategory"] = relationship(back_populates="meal_mappings")


# ── Meals ─────────────────────────────────────────────────────────────────────

class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[MealStatus] = mapped_column(
        SAEnum(MealStatus), default=MealStatus.ACTIVE, nullable=False, index=True
    )
    popularity_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_user_contributed: Mapped[bool] = mapped_column(Boolean, default=False)
    contributed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # relationships
    category_mappings: Mapped[List["MealCategoryMap"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan"
    )
    recipe: Mapped[Optional["MealRecipe"]] = relationship(
        back_populates="meal", uselist=False, cascade="all, delete-orphan"
    )
    user_preferences: Mapped[List["UserMealPreference"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan"
    )
    plan_slots: Mapped[List["DailyPlanSlot"]] = relationship(back_populates="meal")
    log_entries: Mapped[List["MealLogEntry"]] = relationship(back_populates="meal")
    contributions: Mapped[List["MealContribution"]] = relationship(back_populates="meal")


# ── User Meal Preferences ─────────────────────────────────────────────────────

class UserMealPreference(Base):
    __tablename__ = "user_meal_preferences"
    __table_args__ = (UniqueConstraint("user_id", "meal_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    meal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    # e.g. ["breakfast", "lunch"] — overrides system category for this user
    allowed_slot_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    is_excluded: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="meal_preferences")
    meal: Mapped["Meal"] = relationship(back_populates="user_preferences")


# ── Ingredients ───────────────────────────────────────────────────────────────

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50))   # default unit (g, ml, piece)
    category: Mapped[Optional[str]] = mapped_column(String(100))  # e.g. protein, vegetable, spice
    # grams per 1 unit — for unit conversion in nutrition calc
    grams_per_unit: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    nutrition: Mapped[Optional["IngredientNutrition"]] = relationship(
        back_populates="ingredient", uselist=False, cascade="all, delete-orphan"
    )
    recipe_uses: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient"
    )
    blacklisted_by: Mapped[List["UserBlacklist"]] = relationship(
        back_populates="ingredient"
    )
    pantry_entries: Mapped[List["UserPantry"]] = relationship(
        back_populates="ingredient"
    )


# ── Ingredient Nutrition ──────────────────────────────────────────────────────

class IngredientNutrition(Base):
    __tablename__ = "ingredient_nutrition"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    calories_per_100g: Mapped[Optional[float]] = mapped_column(Float)
    protein_g: Mapped[Optional[float]] = mapped_column(Float)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float)
    fat_g: Mapped[Optional[float]] = mapped_column(Float)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float)
    data_source: Mapped[Optional[str]] = mapped_column(String(200))
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    ingredient: Mapped["Ingredient"] = relationship(back_populates="nutrition")


# ── Meal Recipe ───────────────────────────────────────────────────────────────

class MealRecipe(Base):
    __tablename__ = "meal_recipe"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    meal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    prep_time_mins: Mapped[Optional[int]] = mapped_column(Integer)
    cook_time_mins: Mapped[Optional[int]] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    meal: Mapped["Meal"] = relationship(back_populates="recipe")
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


# ── Recipe Ingredients ────────────────────────────────────────────────────────

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meal_recipe.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    is_essential: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(String(200))  # e.g. "finely chopped"

    recipe: Mapped["MealRecipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_uses")


# ── Daily Plans ───────────────────────────────────────────────────────────────

class DailyPlan(Base):
    __tablename__ = "daily_plans"
    __table_args__ = (UniqueConstraint("user_id", "plan_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[PlanStatus] = mapped_column(
        SAEnum(PlanStatus), default=PlanStatus.DRAFT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="daily_plans")
    slots: Mapped[List["DailyPlanSlot"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="DailyPlanSlot.slot_order"
    )


# ── Daily Plan Slots ──────────────────────────────────────────────────────────

class DailyPlanSlot(Base):
    __tablename__ = "daily_plan_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_plans.id", ondelete="CASCADE"), nullable=False
    )
    meal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meals.id", ondelete="SET NULL"), nullable=True
    )
    slot_type: Mapped[SlotType] = mapped_column(SAEnum(SlotType), nullable=False)
    slot_order: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[SlotStatus] = mapped_column(
        SAEnum(SlotStatus), default=SlotStatus.SUGGESTED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    plan: Mapped["DailyPlan"] = relationship(back_populates="slots")
    meal: Mapped[Optional["Meal"]] = relationship(back_populates="plan_slots")
    log_entry: Mapped[Optional["MealLogEntry"]] = relationship(
        back_populates="slot", uselist=False
    )


# ── Meal Log Entries ──────────────────────────────────────────────────────────

class MealLogEntry(Base):
    __tablename__ = "meal_log_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_plan_slots.id", ondelete="SET NULL"), nullable=True
    )
    meal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meals.id", ondelete="RESTRICT"), nullable=False
    )
    eaten_on: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    was_planned: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="log_entries")
    slot: Mapped[Optional["DailyPlanSlot"]] = relationship(back_populates="log_entry")
    meal: Mapped["Meal"] = relationship(back_populates="log_entries")


# ── User Blacklist ────────────────────────────────────────────────────────────

class UserBlacklist(Base):
    __tablename__ = "user_blacklists"
    __table_args__ = (UniqueConstraint("user_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(Text)
    is_allergy: Mapped[bool] = mapped_column(Boolean, default=False)
    is_unavailable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="blacklist")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="blacklisted_by")


# ── User Pantry ───────────────────────────────────────────────────────────────

class UserPantry(Base):
    __tablename__ = "user_pantry"
    __table_args__ = (UniqueConstraint("user_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="pantry")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="pantry_entries")


# ── Meal Contributions ────────────────────────────────────────────────────────

class MealContribution(Base):
    __tablename__ = "meal_contributions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    meal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meals.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[ContributionStatus] = mapped_column(
        SAEnum(ContributionStatus), default=ContributionStatus.PENDING, nullable=False
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="contributions")
    meal: Mapped[Optional["Meal"]] = relationship(back_populates="contributions")
