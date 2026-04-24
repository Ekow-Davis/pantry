# Import all models here so SQLAlchemy's mapper and Alembic's autogenerate
# can discover every table. Order matters — referenced tables before referencing ones.

from app.models.base import (  # noqa
    UserRole, MealStatus, SlotType, SlotStatus,
    PlanStatus, ContributionStatus, CategorySlug,
)
from app.models.user import User  # noqa
from app.models.ingredient import Ingredient, IngredientNutrition  # noqa
from app.models.meal import Meal, MealCategory, MealCategoryMap, UserMealPreference  # noqa
from app.models.recipe import MealRecipe, RecipeIngredient  # noqa
from app.models.plan import DailyPlan, DailyPlanSlot  # noqa
from app.models.log import MealLogEntry  # noqa
from app.models.pantry import UserBlacklist, UserPantry  # noqa
from app.models.contribution import MealContribution  # noqa

__all__ = [
    "UserRole", "MealStatus", "SlotType", "SlotStatus",
    "PlanStatus", "ContributionStatus", "CategorySlug",
    "User",
    "Ingredient", "IngredientNutrition",
    "Meal", "MealCategory", "MealCategoryMap", "UserMealPreference",
    "MealRecipe", "RecipeIngredient",
    "DailyPlan", "DailyPlanSlot",
    "MealLogEntry",
    "UserBlacklist", "UserPantry",
    "MealContribution",
]
