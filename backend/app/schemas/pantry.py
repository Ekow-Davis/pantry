from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.schemas.ingredient import IngredientOut
from app.schemas.meal import MealOut


class BlacklistOut(BaseModel):
    id: UUID
    ingredient: IngredientOut
    reason: Optional[str]
    is_allergy: bool
    is_unavailable: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BlacklistAdd(BaseModel):
    ingredient_id: UUID
    reason: Optional[str] = None
    is_allergy: bool = False
    is_unavailable: bool = False


class PantryOut(BaseModel):
    ingredients: List[IngredientOut]


class PantrySet(BaseModel):
    ingredient_ids: List[UUID]


class PantryMatchItem(BaseModel):
    meal: MealOut
    missing_ingredient: Optional[IngredientOut] = None
    missing_ingredients: Optional[List[IngredientOut]] = None


class PantryMatchResult(BaseModel):
    can_make: List[MealOut]
    missing_one: List[PantryMatchItem]
    missing_few: List[PantryMatchItem]
