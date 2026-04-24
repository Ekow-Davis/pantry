from fastapi import APIRouter, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.api.deps import DbDep, CurrentUser, CurrentAdmin
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models import Meal, MealStatus, MealCategory, MealCategoryMap, MealRecipe, RecipeIngredient, MealContribution, ContributionStatus
from app.schemas.schemas import MealOut, MealDetailOut, MealCreate, MealUpdate, ContributionOut, MessageResponse
from app.services.nutrition import compute_meal_nutrition
from datetime import date

router = APIRouter(prefix="/meals", tags=["Meals"])


def _meal_options():
    return [
        selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category),
        selectinload(Meal.recipe).selectinload(MealRecipe.ingredients).selectinload(RecipeIngredient.ingredient),
    ]


@router.get("", response_model=list[MealOut])
async def list_meals(
    db: DbDep,
    current_user: CurrentUser,
    category: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = (
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(*_meal_options())
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

    # Increment popularity for views
    for meal in meals:
        meal.popularity_score += 1
    await db.flush()

    return meals


@router.get("/of-the-day", response_model=MealOut)
async def meal_of_the_day(db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(Meal)
        .where(Meal.status == MealStatus.ACTIVE)
        .options(*_meal_options())
        .order_by(Meal.popularity_score.desc())
        .limit(1)
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise NotFoundException("Meal")
    return meal


@router.get("/{meal_id}", response_model=MealDetailOut)
async def get_meal(meal_id: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(Meal)
        .where(Meal.id == meal_id, Meal.status == MealStatus.ACTIVE)
        .options(*_meal_options())
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise NotFoundException("Meal")

    meal.popularity_score += 1
    await db.flush()

    nutrition = await compute_meal_nutrition(meal)
    meal_dict = meal.__dict__.copy()
    meal_dict["nutrition"] = nutrition
    meal_dict["categories"] = [m.category for m in meal.category_mappings]
    return MealDetailOut(**meal_dict)


@router.post("", response_model=MealOut, status_code=201)
async def create_meal(payload: MealCreate, db: DbDep, current_user: CurrentAdmin):
    """Admin only — create a meal directly (bypass contribution queue)."""
    meal = Meal(name=payload.name, description=payload.description)
    db.add(meal)
    await db.flush()

    # Attach categories
    for slug in payload.category_slugs:
        cat_result = await db.execute(select(MealCategory).where(MealCategory.slug == slug))
        cat = cat_result.scalar_one_or_none()
        if cat:
            db.add(MealCategoryMap(meal_id=meal.id, category_id=cat.id))

    await db.flush()
    await db.refresh(meal)
    return meal


@router.patch("/{meal_id}", response_model=MealOut)
async def update_meal(meal_id: str, payload: MealUpdate, db: DbDep, current_user: CurrentAdmin):
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise NotFoundException("Meal")

    if payload.name is not None:
        meal.name = payload.name
    if payload.description is not None:
        meal.description = payload.description
    if payload.status is not None:
        meal.status = payload.status

    db.add(meal)
    await db.flush()
    await db.refresh(meal)
    return meal


@router.post("/contribute", response_model=ContributionOut, status_code=201)
async def contribute_meal(payload: MealCreate, db: DbDep, current_user: CurrentUser):
    # Create the meal in PENDING status
    meal = Meal(
        name=payload.name,
        description=payload.description,
        status=MealStatus.PENDING,
        is_user_contributed=True,
        contributed_by=current_user.id,
    )
    db.add(meal)
    await db.flush()

    # Attach categories
    for slug in payload.category_slugs:
        cat_result = await db.execute(select(MealCategory).where(MealCategory.slug == slug))
        cat = cat_result.scalar_one_or_none()
        if cat:
            db.add(MealCategoryMap(meal_id=meal.id, category_id=cat.id))

    # Create contribution record
    contribution = MealContribution(
        user_id=current_user.id,
        meal_id=meal.id,
        status=ContributionStatus.PENDING,
    )
    db.add(contribution)
    await db.flush()
    await db.refresh(contribution)
    return contribution
