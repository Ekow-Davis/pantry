import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, Float, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import utcnow, new_uuid


class MealRecipe(Base):
    __tablename__ = "meal_recipe"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    meal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, unique=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    prep_time_mins: Mapped[Optional[int]] = mapped_column(Integer)
    cook_time_mins: Mapped[Optional[int]] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    meal: Mapped["Meal"] = relationship(back_populates="recipe")  # noqa
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    recipe_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_recipe.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    is_essential: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(String(200))

    recipe: Mapped["MealRecipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_uses")  # noqa
