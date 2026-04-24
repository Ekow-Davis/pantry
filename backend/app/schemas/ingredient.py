from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class NutritionOut(BaseModel):
    calories_per_100g: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    data_source: Optional[str]
    is_estimated: bool

    model_config = {"from_attributes": True}


class NutritionCreate(BaseModel):
    calories_per_100g: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    data_source: Optional[str] = None
    is_estimated: bool = False


class IngredientOut(BaseModel):
    id: UUID
    name: str
    unit: Optional[str]
    category: Optional[str]
    grams_per_unit: Optional[float]
    nutrition: Optional[NutritionOut]

    model_config = {"from_attributes": True}


class IngredientCreate(BaseModel):
    name: str
    unit: Optional[str] = None
    category: Optional[str] = None
    grams_per_unit: Optional[float] = None
    nutrition: Optional[NutritionCreate] = None


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    grams_per_unit: Optional[float] = None
