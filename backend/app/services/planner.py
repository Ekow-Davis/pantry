from datetime import date, timedelta
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    Meal, MealStatus, MealCategoryMap, MealCategory,
    DailyPlan, DailyPlanSlot, MealLogEntry, PlanStatus,
    UserBlacklist, UserMealPreference, RecipeIngredient, SlotType, SlotStatus
)
from app.models.models import User


SLOT_ORDER = [SlotType.BREAKFAST, SlotType.LUNCH, SlotType.DINNER]


async def generate_plan_for_date(user: User, plan_date: date, db: AsyncSession) -> DailyPlan:
    """
    Full planning pipeline:
      1. Get all active meals
      2. Filter by cooldown
      3. For each slot type, filter by eligible categories / user overrides
      4. Filter out blacklisted ingredients
      5. Score by recency (furthest from last eaten = highest score)
      6. Pick top meal per slot
    """
    # ── Load supporting data ─────────────────────────────────────────────────
    blacklisted_ingredient_ids = await _get_blacklisted_ingredient_ids(user.id, db)
    cooldown_map = await _get_cooldown_map(user.id, db)
    user_prefs = await _get_user_preferences(user.id, db)

    # ── Load all active meals with their categories and recipe ingredients ───
    result = await db.execute(
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(
            selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
            selectinload(Meal.recipe).selectinload(RecipeIngredient.__mapper__.relationships["recipe"]),
        )
    )
    all_meals: List[Meal] = result.scalars().unique().all()

    # ── Apply cooldown filter ────────────────────────────────────────────────
    available_meals = [
        m for m in all_meals
        if _is_available(m.id, plan_date, user.cooldown_days, cooldown_map)
    ]

    # ── Apply blacklist filter ───────────────────────────────────────────────
    available_meals = [
        m for m in available_meals
        if not _has_blacklisted_ingredient(m, blacklisted_ingredient_ids)
    ]

    # ── Apply user exclusions ────────────────────────────────────────────────
    excluded_ids = {p.meal_id for p in user_prefs if p.is_excluded}
    available_meals = [m for m in available_meals if m.id not in excluded_ids]

    # ── Create the plan ──────────────────────────────────────────────────────
    plan = DailyPlan(user_id=user.id, plan_date=plan_date, status=PlanStatus.ACTIVE)
    db.add(plan)
    await db.flush()

    used_meal_ids: Set = set()
    pref_map = {p.meal_id: p for p in user_prefs}

    for order, slot_type in enumerate(SLOT_ORDER, start=1):
        eligible = _filter_by_slot(available_meals, slot_type, pref_map)
        eligible = [m for m in eligible if m.id not in used_meal_ids]
        scored = _score_meals(eligible, cooldown_map, plan_date)

        chosen = scored[0] if scored else None
        slot = DailyPlanSlot(
            plan_id=plan.id,
            meal_id=chosen.id if chosen else None,
            slot_type=slot_type,
            slot_order=order,
            status=SlotStatus.SUGGESTED,
        )
        db.add(slot)
        if chosen:
            used_meal_ids.add(chosen.id)

    await db.flush()
    await db.refresh(plan)
    return plan


# ── Cooldown helpers ──────────────────────────────────────────────────────────

async def _get_cooldown_map(user_id, db: AsyncSession) -> dict:
    """Returns {meal_id: last_eaten_date} for all meals the user has eaten."""
    result = await db.execute(
        select(MealLogEntry.meal_id, MealLogEntry.eaten_on)
        .where(MealLogEntry.user_id == user_id)
        .order_by(MealLogEntry.eaten_on.desc())
    )
    rows = result.all()
    seen = {}
    for meal_id, eaten_on in rows:
        if meal_id not in seen:
            seen[meal_id] = eaten_on
    return seen


def _is_available(meal_id, plan_date: date, cooldown_days: int, cooldown_map: dict) -> bool:
    last_eaten = cooldown_map.get(meal_id)
    if not last_eaten:
        return True
    return (plan_date - last_eaten).days > cooldown_days


# ── Blacklist helpers ─────────────────────────────────────────────────────────

async def _get_blacklisted_ingredient_ids(user_id, db: AsyncSession) -> Set:
    result = await db.execute(
        select(UserBlacklist.ingredient_id).where(UserBlacklist.user_id == user_id)
    )
    return {row[0] for row in result.all()}


def _has_blacklisted_ingredient(meal: Meal, blacklisted: Set) -> bool:
    if not meal.recipe:
        return False
    for ri in meal.recipe.ingredients:
        if ri.ingredient_id in blacklisted:
            return True
    return False


# ── Preference helpers ────────────────────────────────────────────────────────

async def _get_user_preferences(user_id, db: AsyncSession) -> List:
    result = await db.execute(
        select(UserMealPreference).where(UserMealPreference.user_id == user_id)
    )
    return result.scalars().all()


def _filter_by_slot(meals: List[Meal], slot_type: SlotType, pref_map: dict) -> List[Meal]:
    eligible = []
    for meal in meals:
        pref = pref_map.get(meal.id)

        # User has a personal override for this meal
        if pref and pref.allowed_slot_types:
            if slot_type.value in pref.allowed_slot_types:
                eligible.append(meal)
            continue

        # Fall back to system categories
        category_slugs = {m.category.slug.value for m in meal.category_mappings}
        if "any" in category_slugs or slot_type.value in category_slugs:
            eligible.append(meal)

    return eligible


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score_meals(meals: List[Meal], cooldown_map: dict, plan_date: date) -> List[Meal]:
    """
    Sort meals by score descending.
    Score = days since last eaten (never eaten = very high score).
    Tie-break: popularity_score.
    """
    def score(meal: Meal) -> tuple:
        last_eaten = cooldown_map.get(meal.id)
        if last_eaten is None:
            days_since = 9999  # never eaten — highest priority
        else:
            days_since = (plan_date - last_eaten).days
        return (days_since, meal.popularity_score)

    return sorted(meals, key=score, reverse=True)
