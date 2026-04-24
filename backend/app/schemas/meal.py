from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.base import CategorySlug
from app.schemas.ingredient import IngredientOut


class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: CategorySlug

    model_config = {"from_attributes": True}


class RecipeIngredientOut(BaseModel):
    id: UUID
    ingredient: IngredientOut
    quantity: Optional[float]
    unit: Optional[str]
    is_essential: bool
    notes: Optional[str]

    model_config = {"from_attributes": True}


class RecipeIngredientIn(BaseModel):
    ingredient_id: UUID
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_essential: bool = False
    notes: Optional[str] = None


class RecipeOut(BaseModel):
    id: UUID
    instructions: Optional[str]
    prep_time_mins: Optional[int]
    cook_time_mins: Optional[int]
    servings: int
    ingredients: List[RecipeIngredientOut]

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    instructions: Optional[str] = None
    prep_time_mins: Optional[int] = None
    cook_time_mins: Optional[int] = None
    servings: int = 1
    ingredients: List[RecipeIngredientIn] = []


class RecipeUpdate(BaseModel):
    instructions: Optional[str] = None
    prep_time_mins: Optional[int] = None
    cook_time_mins: Optional[int] = None
    servings: Optional[int] = None


class MealNutritionOut(BaseModel):
    calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    nutrition_complete: bool


class MealOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    image_url: Optional[str]
    status: str
    popularity_score: int
    is_user_contributed: bool
    categories: List[CategoryOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class MealDetailOut(MealOut):
    recipe: Optional[RecipeOut]
    nutrition: Optional[MealNutritionOut]


class MealCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_slugs: List[CategorySlug]
    recipe: Optional[RecipeCreate] = None


class MealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category_slugs: Optional[List[CategorySlug]] = None


class MealPreferenceOut(BaseModel):
    id: UUID
    meal_id: UUID
    meal_name: str
    allowed_slot_types: Optional[str]
    is_excluded: bool

    model_config = {"from_attributes": True}


class MealPreferenceSet(BaseModel):
    meal_id: UUID
    allowed_slot_types: Optional[List[str]] = None
    is_excluded: bool = False
