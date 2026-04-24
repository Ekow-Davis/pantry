from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import DbDep, CurrentUser, CurrentAdmin
from app.core.exceptions import NotFoundException, ConflictException
from app.models.meal import Meal, MealCategory, MealCategoryMap, UserMealPreference
from app.models.recipe import MealRecipe, RecipeIngredient
from app.models.contribution import MealContribution
from app.models.ingredient import Ingredient
from app.models.base import MealStatus, ContributionStatus
from app.schemas.meal import (
    MealOut, MealDetailOut, MealCreate, MealUpdate,
    MealPreferenceOut, MealPreferenceSet,
    RecipeOut, RecipeCreate, RecipeUpdate,
)
from app.schemas.contribution import ContributionOut
from app.schemas.common import MessageResponse
from app.services.nutrition import compute_meal_nutrition

router = APIRouter(prefix="/meals", tags=["Meals"])


def _meal_eager():
    return [
        selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
        selectinload(Meal.recipe).selectinload(MealRecipe.ingredients).selectinload(RecipeIngredient.ingredient).selectinload(Ingredient.nutrition),
    ]


# ── Meals CRUD ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[MealOut])
async def list_meals(
    db: DbDep,
    current_user: CurrentUser,
    category: str | None = None,
    search: str | None = None,
    status: str = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = (
        select(Meal)
        .where(Meal.status == status)
        .options(*_meal_eager())
        .order_by(Meal.popularity_score.desc(), Meal.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if search:
        query = query.where(Meal.name.ilike(f"%{search}%"))
    if category:
        query = (
            query
            .join(MealCategoryMap, Meal.id == MealCategoryMap.meal_id)
            .join(MealCategory, MealCategoryMap.category_id == MealCategory.id)
            .where(MealCategory.slug == category)
        )
    result = await db.execute(query)
    meals = result.scalars().unique().all()
    for meal in meals:
        meal.popularity_score += 1
    await db.flush()
    return meals


@router.get("/of-the-day", response_model=MealOut)
async def meal_of_the_day(db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(Meal).where(Meal.status == MealStatus.ACTIVE).options(*_meal_eager()).order_by(Meal.popularity_score.desc()).limit(1)
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise NotFoundException("Meal")
    return meal


@router.get("/{meal_id}", response_model=MealDetailOut)
async def get_meal(meal_id: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id).options(*_meal_eager())
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise NotFoundException("Meal")
    meal.popularity_score += 1
    await db.flush()
    nutrition = await compute_meal_nutrition(meal)
    return MealDetailOut(
        **{c.key: getattr(meal, c.key) for c in meal.__table__.columns},
        categories=[m.category for m in meal.category_mappings],
        recipe=meal.recipe,
        nutrition=nutrition,
    )


@router.post("", response_model=MealOut, status_code=201)
async def create_meal(payload: MealCreate, db: DbDep, current_admin: CurrentAdmin):
    existing = (await db.execute(select(Meal).where(Meal.name == payload.name))).scalar_one_or_none()
    if existing:
        raise ConflictException(f"A meal named '{payload.name}' already exists.")

    meal = Meal(name=payload.name, description=payload.description, status=MealStatus.ACTIVE)
    db.add(meal)
    await db.flush()

    await _attach_categories(meal.id, payload.category_slugs, db)

    if payload.recipe:
        await _create_recipe(meal.id, payload.recipe, db)

    await db.flush()
    result = await db.execute(select(Meal).where(Meal.id == meal.id).options(*_meal_eager()))
    return result.scalar_one()


@router.patch("/{meal_id}", response_model=MealOut)
async def update_meal(meal_id: str, payload: MealUpdate, db: DbDep, current_admin: CurrentAdmin):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise NotFoundException("Meal")
    if payload.name is not None:
        meal.name = payload.name
    if payload.description is not None:
        meal.description = payload.description
    if payload.status is not None:
        meal.status = payload.status
    if payload.category_slugs is not None:
        existing_maps = (await db.execute(select(MealCategoryMap).where(MealCategoryMap.meal_id == meal_id))).scalars().all()
        for m in existing_maps:
            await db.delete(m)
        await db.flush()
        await _attach_categories(meal_id, payload.category_slugs, db)
    db.add(meal)
    await db.flush()
    result = await db.execute(select(Meal).where(Meal.id == meal_id).options(*_meal_eager()))
    return result.scalar_one()


@router.delete("/{meal_id}", response_model=MessageResponse)
async def delete_meal(meal_id: str, db: DbDep, current_admin: CurrentAdmin):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise NotFoundException("Meal")
    await db.delete(meal)
    return MessageResponse(message="Meal deleted.")


@router.patch("/{meal_id}/hide", response_model=MealOut)
async def hide_meal(meal_id: str, db: DbDep, current_admin: CurrentAdmin):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise NotFoundException("Meal")
    meal.status = MealStatus.HIDDEN
    db.add(meal)
    await db.flush()
    result = await db.execute(select(Meal).where(Meal.id == meal_id).options(*_meal_eager()))
    return result.scalar_one()


@router.patch("/{meal_id}/unhide", response_model=MealOut)
async def unhide_meal(meal_id: str, db: DbDep, current_admin: CurrentAdmin):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise NotFoundException("Meal")
    meal.status = MealStatus.ACTIVE
    db.add(meal)
    await db.flush()
    result = await db.execute(select(Meal).where(Meal.id == meal_id).options(*_meal_eager()))
    return result.scalar_one()


# ── Recipe sub-resource ───────────────────────────────────────────────────────

@router.get("/{meal_id}/recipe", response_model=RecipeOut)
async def get_recipe(meal_id: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(MealRecipe)
        .where(MealRecipe.meal_id == meal_id)
        .options(selectinload(MealRecipe.ingredients).selectinload(RecipeIngredient.ingredient).selectinload(Ingredient.nutrition))
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise NotFoundException("Recipe")
    return recipe


@router.put("/{meal_id}/recipe", response_model=RecipeOut)
async def upsert_recipe(meal_id: str, payload: RecipeCreate, db: DbDep, current_admin: CurrentAdmin):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise NotFoundException("Meal")

    result = await db.execute(select(MealRecipe).where(MealRecipe.meal_id == meal_id))
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    await _create_recipe(meal_id, payload, db)
    await db.flush()

    result = await db.execute(
        select(MealRecipe)
        .where(MealRecipe.meal_id == meal_id)
        .options(selectinload(MealRecipe.ingredients).selectinload(RecipeIngredient.ingredient).selectinload(Ingredient.nutrition))
    )
    return result.scalar_one()


@router.patch("/{meal_id}/recipe", response_model=RecipeOut)
async def update_recipe_meta(meal_id: str, payload: RecipeUpdate, db: DbDep, current_admin: CurrentAdmin):
    result = await db.execute(select(MealRecipe).where(MealRecipe.meal_id == meal_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise NotFoundException("Recipe")
    if payload.instructions is not None:
        recipe.instructions = payload.instructions
    if payload.prep_time_mins is not None:
        recipe.prep_time_mins = payload.prep_time_mins
    if payload.cook_time_mins is not None:
        recipe.cook_time_mins = payload.cook_time_mins
    if payload.servings is not None:
        recipe.servings = payload.servings
    db.add(recipe)
    await db.flush()
    result = await db.execute(
        select(MealRecipe)
        .where(MealRecipe.meal_id == meal_id)
        .options(selectinload(MealRecipe.ingredients).selectinload(RecipeIngredient.ingredient).selectinload(Ingredient.nutrition))
    )
    return result.scalar_one()


# ── User meal preferences ─────────────────────────────────────────────────────

@router.get("/preferences/mine", response_model=list[MealPreferenceOut])
async def get_my_preferences(current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserMealPreference)
        .where(UserMealPreference.user_id == current_user.id)
        .options(selectinload(UserMealPreference.meal))
    )
    prefs = result.scalars().all()
    return [
        MealPreferenceOut(
            id=p.id,
            meal_id=p.meal_id,
            meal_name=p.meal.name,
            allowed_slot_types=p.allowed_slot_types,
            is_excluded=p.is_excluded,
        )
        for p in prefs
    ]


@router.put("/preferences/mine", response_model=MealPreferenceOut)
async def set_meal_preference(payload: MealPreferenceSet, current_user: CurrentUser, db: DbDep):
    meal = await db.get(Meal, payload.meal_id)
    if not meal:
        raise NotFoundException("Meal")

    result = await db.execute(
        select(UserMealPreference).where(
            UserMealPreference.user_id == current_user.id,
            UserMealPreference.meal_id == payload.meal_id,
        )
    )
    pref = result.scalar_one_or_none()
    slot_str = ",".join(payload.allowed_slot_types) if payload.allowed_slot_types else None

    if pref:
        pref.allowed_slot_types = slot_str
        pref.is_excluded = payload.is_excluded
    else:
        pref = UserMealPreference(
            user_id=current_user.id,
            meal_id=payload.meal_id,
            allowed_slot_types=slot_str,
            is_excluded=payload.is_excluded,
        )
    db.add(pref)
    await db.flush()
    return MealPreferenceOut(
        id=pref.id,
        meal_id=pref.meal_id,
        meal_name=meal.name,
        allowed_slot_types=pref.allowed_slot_types,
        is_excluded=pref.is_excluded,
    )


@router.delete("/preferences/{pref_id}", response_model=MessageResponse)
async def delete_meal_preference(pref_id: str, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserMealPreference).where(UserMealPreference.id == pref_id, UserMealPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        raise NotFoundException("Preference")
    await db.delete(pref)
    return MessageResponse(message="Preference removed.")


# ── Contributions ─────────────────────────────────────────────────────────────

@router.post("/contribute", response_model=ContributionOut, status_code=201)
async def contribute_meal(payload: MealCreate, db: DbDep, current_user: CurrentUser):
    meal = Meal(
        name=payload.name,
        description=payload.description,
        status=MealStatus.PENDING,
        is_user_contributed=True,
        contributed_by=current_user.id,
    )
    db.add(meal)
    await db.flush()
    await _attach_categories(meal.id, payload.category_slugs, db)
    if payload.recipe:
        await _create_recipe(meal.id, payload.recipe, db)

    contribution = MealContribution(
        user_id=current_user.id,
        meal_id=meal.id,
        status=ContributionStatus.PENDING,
    )
    db.add(contribution)
    await db.flush()
    await db.refresh(contribution, ["meal"])
    return contribution


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _attach_categories(meal_id, slugs, db):
    for slug in slugs:
        cat = (await db.execute(select(MealCategory).where(MealCategory.slug == slug))).scalar_one_or_none()
        if cat:
            db.add(MealCategoryMap(meal_id=meal_id, category_id=cat.id))
    await db.flush()


async def _create_recipe(meal_id, payload: RecipeCreate, db):
    recipe = MealRecipe(
        meal_id=meal_id,
        instructions=payload.instructions,
        prep_time_mins=payload.prep_time_mins,
        cook_time_mins=payload.cook_time_mins,
        servings=payload.servings,
    )
    db.add(recipe)
    await db.flush()
    for ri in payload.ingredients:
        ing = await db.get(Ingredient, ri.ingredient_id)
        if ing:
            db.add(RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ri.ingredient_id,
                quantity=ri.quantity,
                unit=ri.unit,
                is_essential=ri.is_essential,
                notes=ri.notes,
            ))
    await db.flush()
