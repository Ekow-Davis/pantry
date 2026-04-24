from datetime import date
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.meal import Meal, MealCategoryMap, UserMealPreference
from app.models.ingredient import Ingredient
from app.models.recipe import MealRecipe, RecipeIngredient
from app.models.plan import DailyPlan, DailyPlanSlot
from app.models.log import MealLogEntry
from app.models.pantry import UserBlacklist
from app.models.base import MealStatus, SlotType, SlotStatus, PlanStatus
from app.models.user import User


SLOT_ORDER = [SlotType.BREAKFAST, SlotType.LUNCH, SlotType.DINNER]


async def generate_plan_for_date(user: User, plan_date: date, db: AsyncSession) -> DailyPlan:
    blacklisted_ids = await _get_blacklisted_ids(user.id, db)
    cooldown_map = await _get_cooldown_map(user.id, db)
    user_prefs = await _get_user_prefs(user.id, db)

    result = await db.execute(
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(
            selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
            selectinload(Meal.recipe).selectinload(RecipeIngredient.ingredient),
        )
    )
    all_meals: List[Meal] = result.scalars().unique().all()

    # Apply filters
    available = [m for m in all_meals if _is_available(m.id, plan_date, user.cooldown_days, cooldown_map)]
    available = [m for m in available if not _has_blacklisted(m, blacklisted_ids)]
    excluded_ids = {p.meal_id for p in user_prefs if p.is_excluded}
    available = [m for m in available if m.id not in excluded_ids]

    plan = DailyPlan(user_id=user.id, plan_date=plan_date, status=PlanStatus.ACTIVE)
    db.add(plan)
    await db.flush()

    pref_map = {p.meal_id: p for p in user_prefs}
    used_ids: Set = set()

    for order, slot_type in enumerate(SLOT_ORDER, start=1):
        eligible = _filter_by_slot(available, slot_type, pref_map)
        eligible = [m for m in eligible if m.id not in used_ids]
        scored = _score(eligible, cooldown_map, plan_date)
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
            used_ids.add(chosen.id)

    await db.flush()
    await db.refresh(plan)
    return plan


async def _get_cooldown_map(user_id, db: AsyncSession) -> dict:
    result = await db.execute(
        select(MealLogEntry.meal_id, MealLogEntry.eaten_on)
        .where(MealLogEntry.user_id == user_id)
        .order_by(MealLogEntry.eaten_on.desc())
    )
    seen = {}
    for meal_id, eaten_on in result.all():
        if meal_id not in seen:
            seen[meal_id] = eaten_on
    return seen


def _is_available(meal_id, plan_date: date, cooldown_days: int, cooldown_map: dict) -> bool:
    last = cooldown_map.get(meal_id)
    if not last:
        return True
    return (plan_date - last).days > cooldown_days


async def _get_blacklisted_ids(user_id, db: AsyncSession) -> Set:
    result = await db.execute(
        select(UserBlacklist.ingredient_id).where(UserBlacklist.user_id == user_id)
    )
    return {row[0] for row in result.all()}


def _has_blacklisted(meal: Meal, blacklisted: Set) -> bool:
    if not meal.recipe:
        return False
    return any(ri.ingredient_id in blacklisted for ri in meal.recipe.ingredients)


async def _get_user_prefs(user_id, db: AsyncSession) -> List:
    result = await db.execute(
        select(UserMealPreference).where(UserMealPreference.user_id == user_id)
    )
    return result.scalars().all()


def _filter_by_slot(meals: List[Meal], slot_type: SlotType, pref_map: dict) -> List[Meal]:
    eligible = []
    for meal in meals:
        pref = pref_map.get(meal.id)
        if pref and pref.allowed_slot_types:
            allowed = [s.strip() for s in pref.allowed_slot_types.split(",")]
            if slot_type.value in allowed:
                eligible.append(meal)
            continue
        category_slugs = {m.category.slug.value for m in meal.category_mappings}
        if "any" in category_slugs or slot_type.value in category_slugs:
            eligible.append(meal)
    return eligible


def _score(meals: List[Meal], cooldown_map: dict, plan_date: date) -> List[Meal]:
    def key(m: Meal):
        last = cooldown_map.get(m.id)
        days = 9999 if last is None else (plan_date - last).days
        return (days, m.popularity_score)
    return sorted(meals, key=key, reverse=True)
