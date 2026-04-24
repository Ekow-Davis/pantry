import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import MealStatus, CategorySlug, utcnow, new_uuid


class MealCategory(Base):
    __tablename__ = "meal_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[CategorySlug] = mapped_column(SAEnum(CategorySlug), unique=True, nullable=False)

    meal_mappings: Mapped[List["MealCategoryMap"]] = relationship(back_populates="category")  # noqa


class MealCategoryMap(Base):
    __tablename__ = "meal_category_map"
    __table_args__ = (UniqueConstraint("meal_id", "category_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    meal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_categories.id", ondelete="CASCADE"), nullable=False)

    meal: Mapped["Meal"] = relationship(back_populates="category_mappings")  # noqa
    category: Mapped["MealCategory"] = relationship(back_populates="meal_mappings")


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[MealStatus] = mapped_column(SAEnum(MealStatus), default=MealStatus.ACTIVE, nullable=False, index=True)
    popularity_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_user_contributed: Mapped[bool] = mapped_column(Boolean, default=False)
    contributed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    category_mappings: Mapped[List["MealCategoryMap"]] = relationship(back_populates="meal", cascade="all, delete-orphan")  # noqa
    recipe: Mapped[Optional["MealRecipe"]] = relationship(back_populates="meal", uselist=False, cascade="all, delete-orphan")  # noqa
    user_preferences: Mapped[List["UserMealPreference"]] = relationship(back_populates="meal", cascade="all, delete-orphan")  # noqa
    plan_slots: Mapped[List["DailyPlanSlot"]] = relationship(back_populates="meal")  # noqa
    log_entries: Mapped[List["MealLogEntry"]] = relationship(back_populates="meal")  # noqa
    contributions: Mapped[List["MealContribution"]] = relationship(back_populates="meal")  # noqa


class UserMealPreference(Base):
    __tablename__ = "user_meal_preferences"
    __table_args__ = (UniqueConstraint("user_id", "meal_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    allowed_slot_types: Mapped[Optional[List[str]]] = mapped_column(
        # Store as comma-separated string for broad DB compatibility
        String(200), nullable=True
    )
    is_excluded: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="meal_preferences")  # noqa
    meal: Mapped["Meal"] = relationship(back_populates="user_preferences")  # noqa
