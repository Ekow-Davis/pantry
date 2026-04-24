from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    Meal, MealStatus, MealLogEntry, UserBlacklist,
    UserPantry, RecipeIngredient, MealCategoryMap
)
from app.schemas.schemas import DailyRecommendationOut, PantryMatchResult
from app.core.exceptions import NotFoundException


# ── Daily Recommendation ──────────────────────────────────────────────────────

async def get_daily_recommendation(user, db: AsyncSession) -> DailyRecommendationOut:
    """
    Recommend a meal the user has never eaten, or has eaten least recently.
    Excludes blacklisted ingredients.
    """
    blacklisted = await _get_blacklisted_ids(user.id, db)

    # Get all eaten meal IDs ordered by last eaten date
    eaten_result = await db.execute(
        select(MealLogEntry.meal_id, MealLogEntry.eaten_on)
        .where(MealLogEntry.user_id == user.id)
        .order_by(MealLogEntry.eaten_on.desc())
    )
    eaten_rows = eaten_result.all()
    eaten_map = {}
    for meal_id, eaten_on in eaten_rows:
        if meal_id not in eaten_map:
            eaten_map[meal_id] = eaten_on

    # Get all active meals
    result = await db.execute(
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(
            selectinload(Meal.recipe).selectinload(RecipeIngredient.__mapper__.relationships["recipe"]),
            selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
        )
    )
    all_meals = result.scalars().unique().all()

    # Filter blacklisted
    candidates = [m for m in all_meals if not _has_blacklisted(m, blacklisted)]

    # Separate never-eaten from eaten
    never_eaten = [m for m in candidates if m.id not in eaten_map]
    if never_eaten:
        # Pick the most popular never-eaten meal
        pick = sorted(never_eaten, key=lambda m: m.popularity_score, reverse=True)[0]
        reason = "You haven't tried this one yet."
    else:
        # Pick the one eaten longest ago
        pick = sorted(candidates, key=lambda m: eaten_map.get(m.id, date.min))[0]
        last = eaten_map.get(pick.id)
        days = (date.today() - last).days if last else 0
        reason = f"You last had this {days} day{'s' if days != 1 else ''} ago."

    return DailyRecommendationOut(meal=pick, reason=reason)


# ── Pantry Matcher ────────────────────────────────────────────────────────────

async def get_pantry_matches(user, db: AsyncSession) -> PantryMatchResult:
    """
    Match user's pantry against meal essential ingredients.
    Returns three buckets: can_make, missing_one, missing_few.
    """
    # Get user pantry ingredient IDs
    pantry_result = await db.execute(
        select(UserPantry.ingredient_id).where(UserPantry.user_id == user.id)
    )
    pantry_ids = {row[0] for row in pantry_result.all()}

    # Get all active meals with recipe + essential ingredients
    result = await db.execute(
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(
            selectinload(Meal.recipe).selectinload(RecipeIngredient.__mapper__.relationships["recipe"]),
            selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
        )
    )
    all_meals = result.scalars().unique().all()

    can_make = []
    missing_one = []
    missing_few = []

    for meal in all_meals:
        if not meal.recipe:
            continue
        essential = [ri for ri in meal.recipe.ingredients if ri.is_essential]
        if not essential:
            continue

        missing = [ri for ri in essential if ri.ingredient_id not in pantry_ids]
        count = len(missing)

        if count == 0:
            can_make.append(meal)
        elif count == 1:
            missing_one.append({
                "meal": meal,
                "missing_ingredient": missing[0].ingredient,
            })
        elif count <= 3:
            missing_few.append({
                "meal": meal,
                "missing_ingredients": [ri.ingredient for ri in missing],
            })

    # Sort each bucket by popularity descending
    can_make.sort(key=lambda m: m.popularity_score, reverse=True)
    missing_one.sort(key=lambda x: x["meal"].popularity_score, reverse=True)
    missing_few.sort(key=lambda x: x["meal"].popularity_score, reverse=True)

    return PantryMatchResult(
        can_make=can_make,
        missing_one=missing_one,
        missing_few=missing_few,
    )


# ── Shared helpers ────────────────────────────────────────────────────────────

async def _get_blacklisted_ids(user_id, db: AsyncSession) -> set:
    result = await db.execute(
        select(UserBlacklist.ingredient_id).where(UserBlacklist.user_id == user_id)
    )
    return {row[0] for row in result.all()}


def _has_blacklisted(meal: Meal, blacklisted: set) -> bool:
    if not meal.recipe:
        return False
    return any(ri.ingredient_id in blacklisted for ri in meal.recipe.ingredients)
