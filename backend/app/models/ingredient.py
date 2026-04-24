import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import utcnow, new_uuid


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    grams_per_unit: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    nutrition: Mapped[Optional["IngredientNutrition"]] = relationship(back_populates="ingredient", uselist=False, cascade="all, delete-orphan")  # noqa
    recipe_uses: Mapped[List["RecipeIngredient"]] = relationship(back_populates="ingredient")  # noqa
    blacklisted_by: Mapped[List["UserBlacklist"]] = relationship(back_populates="ingredient")  # noqa
    pantry_entries: Mapped[List["UserPantry"]] = relationship(back_populates="ingredient")  # noqa


class IngredientNutrition(Base):
    __tablename__ = "ingredient_nutrition"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, unique=True)
    calories_per_100g: Mapped[Optional[float]] = mapped_column(Float)
    protein_g: Mapped[Optional[float]] = mapped_column(Float)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float)
    fat_g: Mapped[Optional[float]] = mapped_column(Float)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float)
    data_source: Mapped[Optional[str]] = mapped_column(String(200))
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="nutrition")
