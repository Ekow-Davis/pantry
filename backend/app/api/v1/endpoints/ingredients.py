from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import DbDep, CurrentUser, CurrentAdmin
from app.core.exceptions import NotFoundException, ConflictException
from app.models.ingredient import Ingredient, IngredientNutrition
from app.schemas.ingredient import IngredientOut, IngredientCreate, IngredientUpdate, NutritionCreate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("", response_model=list[IngredientOut])
async def list_ingredients(
    db: DbDep,
    current_user: CurrentUser,
    search: str | None = None,
    category: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    query = (
        select(Ingredient)
        .options(selectinload(Ingredient.nutrition))
        .order_by(Ingredient.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if search:
        query = query.where(Ingredient.name.ilike(f"%{search}%"))
    if category:
        query = query.where(Ingredient.category == category)
    return (await db.execute(query)).scalars().all()


@router.get("/{ingredient_id}", response_model=IngredientOut)
async def get_ingredient(ingredient_id: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(Ingredient)
        .where(Ingredient.id == ingredient_id)
        .options(selectinload(Ingredient.nutrition))
    )
    ing = result.scalar_one_or_none()
    if not ing:
        raise NotFoundException("Ingredient")
    return ing


@router.post("", response_model=IngredientOut, status_code=201)
async def create_ingredient(payload: IngredientCreate, db: DbDep, current_admin: CurrentAdmin):
    existing = (await db.execute(select(Ingredient).where(Ingredient.name == payload.name))).scalar_one_or_none()
    if existing:
        raise ConflictException(f"An ingredient named '{payload.name}' already exists.")

    ing = Ingredient(
        name=payload.name,
        unit=payload.unit,
        category=payload.category,
        grams_per_unit=payload.grams_per_unit,
    )
    db.add(ing)
    await db.flush()

    if payload.nutrition:
        n = payload.nutrition
        db.add(IngredientNutrition(
            ingredient_id=ing.id,
            calories_per_100g=n.calories_per_100g,
            protein_g=n.protein_g,
            carbs_g=n.carbs_g,
            fat_g=n.fat_g,
            fiber_g=n.fiber_g,
            data_source=n.data_source,
            is_estimated=n.is_estimated,
        ))
        await db.flush()

    await db.refresh(ing, ["nutrition"])
    return ing


@router.patch("/{ingredient_id}", response_model=IngredientOut)
async def update_ingredient(ingredient_id: str, payload: IngredientUpdate, db: DbDep, current_admin: CurrentAdmin):
    ing = await db.get(Ingredient, ingredient_id)
    if not ing:
        raise NotFoundException("Ingredient")
    if payload.name is not None:
        ing.name = payload.name
    if payload.unit is not None:
        ing.unit = payload.unit
    if payload.category is not None:
        ing.category = payload.category
    if payload.grams_per_unit is not None:
        ing.grams_per_unit = payload.grams_per_unit
    db.add(ing)
    await db.flush()
    await db.refresh(ing, ["nutrition"])
    return ing


@router.delete("/{ingredient_id}", response_model=MessageResponse)
async def delete_ingredient(ingredient_id: str, db: DbDep, current_admin: CurrentAdmin):
    ing = await db.get(Ingredient, ingredient_id)
    if not ing:
        raise NotFoundException("Ingredient")
    await db.delete(ing)
    return MessageResponse(message="Ingredient deleted.")


# ── Nutrition sub-resource ────────────────────────────────────────────────────

@router.put("/{ingredient_id}/nutrition", response_model=IngredientOut)
async def upsert_nutrition(ingredient_id: str, payload: NutritionCreate, db: DbDep, current_admin: CurrentAdmin):
    ing = await db.get(Ingredient, ingredient_id)
    if not ing:
        raise NotFoundException("Ingredient")

    result = await db.execute(
        select(IngredientNutrition).where(IngredientNutrition.ingredient_id == ingredient_id)
    )
    nutrition = result.scalar_one_or_none()

    if nutrition:
        nutrition.calories_per_100g = payload.calories_per_100g
        nutrition.protein_g = payload.protein_g
        nutrition.carbs_g = payload.carbs_g
        nutrition.fat_g = payload.fat_g
        nutrition.fiber_g = payload.fiber_g
        nutrition.data_source = payload.data_source
        nutrition.is_estimated = payload.is_estimated
        db.add(nutrition)
    else:
        db.add(IngredientNutrition(
            ingredient_id=ing.id,
            **payload.model_dump(),
        ))

    await db.flush()
    await db.refresh(ing, ["nutrition"])
    return ing


@router.delete("/{ingredient_id}/nutrition", response_model=MessageResponse)
async def delete_nutrition(ingredient_id: str, db: DbDep, current_admin: CurrentAdmin):
    result = await db.execute(
        select(IngredientNutrition).where(IngredientNutrition.ingredient_id == ingredient_id)
    )
    nutrition = result.scalar_one_or_none()
    if not nutrition:
        raise NotFoundException("Nutrition data")
    await db.delete(nutrition)
    return MessageResponse(message="Nutrition data removed.")
