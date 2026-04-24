from __future__ import annotations
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.models.models import UserRole, SlotType, SlotStatus, PlanStatus, ContributionStatus, CategorySlug


# ── Shared ────────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    country: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    country: Optional[str]
    timezone: str
    cooldown_days: int
    assume_cooked: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdatePreferencesRequest(BaseModel):
    cooldown_days: Optional[int] = None
    assume_cooked: Optional[bool] = None
    timezone: Optional[str] = None

    @field_validator("cooldown_days")
    @classmethod
    def validate_cooldown(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 30):
            raise ValueError("cooldown_days must be between 1 and 30.")
        return v


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: CategorySlug

    model_config = {"from_attributes": True}


# ── Ingredients ───────────────────────────────────────────────────────────────

class NutritionOut(BaseModel):
    calories_per_100g: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    data_source: Optional[str]
    is_estimated: bool

    model_config = {"from_attributes": True}


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


class NutritionCreate(BaseModel):
    calories_per_100g: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    data_source: Optional[str] = None
    is_estimated: bool = False


# ── Recipes ───────────────────────────────────────────────────────────────────

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


# ── Meals ─────────────────────────────────────────────────────────────────────

class MealNutritionOut(BaseModel):
    """Computed nutrition for a meal per serving."""
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


# ── Meal Preferences ──────────────────────────────────────────────────────────

class MealPreferenceOut(BaseModel):
    id: UUID
    meal_id: UUID
    meal_name: str
    allowed_slot_types: Optional[List[str]]
    is_excluded: bool

    model_config = {"from_attributes": True}


class MealPreferenceSet(BaseModel):
    meal_id: UUID
    allowed_slot_types: Optional[List[SlotType]] = None
    is_excluded: bool = False


# ── Plans ─────────────────────────────────────────────────────────────────────

class PlanSlotOut(BaseModel):
    id: UUID
    meal: Optional[MealOut]
    slot_type: SlotType
    slot_order: int
    status: SlotStatus

    model_config = {"from_attributes": True}


class DailyPlanOut(BaseModel):
    id: UUID
    plan_date: date
    status: PlanStatus
    slots: List[PlanSlotOut]

    model_config = {"from_attributes": True}


class UpdateSlotRequest(BaseModel):
    status: SlotStatus
    replacement_meal_id: Optional[UUID] = None  # required if status = REPLACED


class LogExtraMealRequest(BaseModel):
    meal_id: UUID
    slot_type: SlotType
    eaten_on: Optional[date] = None   # defaults to today
    notes: Optional[str] = None


# ── Meal Log ──────────────────────────────────────────────────────────────────

class MealLogOut(BaseModel):
    id: UUID
    meal: MealOut
    eaten_on: date
    slot_type: Optional[str] = None
    was_planned: bool
    notes: Optional[str]
    logged_at: datetime

    model_config = {"from_attributes": True}


# ── Blacklist ─────────────────────────────────────────────────────────────────

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


# ── Pantry ────────────────────────────────────────────────────────────────────

class PantryOut(BaseModel):
    ingredients: List[IngredientOut]


class PantrySet(BaseModel):
    ingredient_ids: List[UUID]


class PantryMatchResult(BaseModel):
    can_make: List[MealOut]
    missing_one: List[dict]   # {meal, missing_ingredient}
    missing_few: List[dict]   # {meal, missing_ingredients: []}


# ── Recommendations ───────────────────────────────────────────────────────────

class DailyRecommendationOut(BaseModel):
    meal: MealOut
    reason: str   # e.g. "You haven't tried this before" or "Last cooked 12 days ago"


# ── Contributions ─────────────────────────────────────────────────────────────

class ContributionOut(BaseModel):
    id: UUID
    user_id: UUID
    meal: Optional[MealOut]
    status: ContributionStatus
    rejection_reason: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ReviewContributionRequest(BaseModel):
    status: ContributionStatus  # APPROVED or REJECTED
    rejection_reason: Optional[str] = None

    @model_validator(mode="after")
    def reason_required_for_rejection(self) -> "ReviewContributionRequest":
        if self.status == ContributionStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting.")
        return self


# ── Admin Stats ───────────────────────────────────────────────────────────────

class AdminStatsOut(BaseModel):
    total_meals: int
    active_meals: int
    pending_contributions: int
    total_users: int
    total_log_entries: int
    ingredients_missing_nutrition: int
