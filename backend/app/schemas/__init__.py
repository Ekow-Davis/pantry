from app.schemas.common import MessageResponse
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.schemas.user import UserOut, UpdatePreferencesRequest, AdminUpdateUserRequest
from app.schemas.ingredient import IngredientOut, IngredientCreate, IngredientUpdate, NutritionOut, NutritionCreate
from app.schemas.meal import (
    CategoryOut, MealOut, MealDetailOut, MealCreate, MealUpdate,
    MealNutritionOut, MealPreferenceOut, MealPreferenceSet,
    RecipeOut, RecipeCreate, RecipeUpdate, RecipeIngredientOut, RecipeIngredientIn,
)
from app.schemas.plan import DailyPlanOut, PlanSlotOut, UpdateSlotRequest, LogExtraMealRequest
from app.schemas.log import MealLogOut
from app.schemas.pantry import BlacklistOut, BlacklistAdd, PantryOut, PantrySet, PantryMatchResult, PantryMatchItem
from app.schemas.contribution import ContributionOut, ReviewContributionRequest
from app.schemas.admin import AdminStatsOut
from app.schemas.recommendation import DailyRecommendationOut

__all__ = [
    "MessageResponse",
    "RegisterRequest", "LoginRequest", "TokenResponse", "RefreshRequest",
    "UserOut", "UpdatePreferencesRequest", "AdminUpdateUserRequest",
    "IngredientOut", "IngredientCreate", "IngredientUpdate", "NutritionOut", "NutritionCreate",
    "CategoryOut", "MealOut", "MealDetailOut", "MealCreate", "MealUpdate",
    "MealNutritionOut", "MealPreferenceOut", "MealPreferenceSet",
    "RecipeOut", "RecipeCreate", "RecipeUpdate", "RecipeIngredientOut", "RecipeIngredientIn",
    "DailyPlanOut", "PlanSlotOut", "UpdateSlotRequest", "LogExtraMealRequest",
    "MealLogOut",
    "BlacklistOut", "BlacklistAdd", "PantryOut", "PantrySet", "PantryMatchResult", "PantryMatchItem",
    "ContributionOut", "ReviewContributionRequest",
    "AdminStatsOut",
    "DailyRecommendationOut",
]
