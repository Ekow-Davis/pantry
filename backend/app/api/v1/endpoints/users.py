from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import DbDep, CurrentUser
from app.core.exceptions import NotFoundException
from app.models import User, UserBlacklist, UserPantry, Ingredient, MealLogEntry
from app.schemas.schemas import (
    UserOut, UpdatePreferencesRequest,
    BlacklistOut, BlacklistAdd, MessageResponse,
    PantryOut, PantrySet, MealLogOut,
)
from datetime import date

router = APIRouter(prefix="/me", tags=["User"])


@router.get("", response_model=UserOut)
async def get_profile(current_user: CurrentUser):
    return current_user


@router.patch("/preferences", response_model=UserOut)
async def update_preferences(payload: UpdatePreferencesRequest, current_user: CurrentUser, db: DbDep):
    if payload.cooldown_days is not None:
        current_user.cooldown_days = payload.cooldown_days
    if payload.assume_cooked is not None:
        current_user.assume_cooked = payload.assume_cooked
    if payload.timezone is not None:
        current_user.timezone = payload.timezone

    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user


# ── Blacklist ─────────────────────────────────────────────────────────────────

@router.get("/blacklist", response_model=list[BlacklistOut])
async def get_blacklist(current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserBlacklist)
        .where(UserBlacklist.user_id == current_user.id)
        .options(selectinload(UserBlacklist.ingredient).selectinload(Ingredient.nutrition))
        .order_by(UserBlacklist.created_at.desc())
    )
    return result.scalars().all()


@router.post("/blacklist", response_model=BlacklistOut, status_code=201)
async def add_to_blacklist(payload: BlacklistAdd, current_user: CurrentUser, db: DbDep):
    # Verify ingredient exists
    ing = await db.get(Ingredient, payload.ingredient_id)
    if not ing:
        raise NotFoundException("Ingredient")

    # Check if already blacklisted
    existing = await db.execute(
        select(UserBlacklist).where(
            UserBlacklist.user_id == current_user.id,
            UserBlacklist.ingredient_id == payload.ingredient_id,
        )
    )
    if existing.scalar_one_or_none():
        from app.core.exceptions import ConflictException
        raise ConflictException("Ingredient is already in your blacklist.")

    entry = UserBlacklist(
        user_id=current_user.id,
        ingredient_id=payload.ingredient_id,
        reason=payload.reason,
        is_allergy=payload.is_allergy,
        is_unavailable=payload.is_unavailable,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry, ["ingredient"])
    return entry


@router.delete("/blacklist/{entry_id}", response_model=MessageResponse)
async def remove_from_blacklist(entry_id: str, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserBlacklist).where(
            UserBlacklist.id == entry_id,
            UserBlacklist.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Blacklist entry")

    await db.delete(entry)
    return MessageResponse(message="Ingredient removed from blacklist.")


# ── Pantry ────────────────────────────────────────────────────────────────────

@router.get("/pantry", response_model=PantryOut)
async def get_pantry(current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserPantry)
        .where(UserPantry.user_id == current_user.id)
        .options(selectinload(UserPantry.ingredient).selectinload(Ingredient.nutrition))
    )
    entries = result.scalars().all()
    return PantryOut(ingredients=[e.ingredient for e in entries])


@router.put("/pantry", response_model=PantryOut)
async def replace_pantry(payload: PantrySet, current_user: CurrentUser, db: DbDep):
    # Delete all current pantry entries
    existing = await db.execute(
        select(UserPantry).where(UserPantry.user_id == current_user.id)
    )
    for entry in existing.scalars().all():
        await db.delete(entry)

    # Add new entries
    for ingredient_id in payload.ingredient_ids:
        ing = await db.get(Ingredient, ingredient_id)
        if ing:
            db.add(UserPantry(user_id=current_user.id, ingredient_id=ingredient_id))

    await db.flush()

    # Return updated pantry
    result = await db.execute(
        select(UserPantry)
        .where(UserPantry.user_id == current_user.id)
        .options(selectinload(UserPantry.ingredient).selectinload(Ingredient.nutrition))
    )
    entries = result.scalars().all()
    return PantryOut(ingredients=[e.ingredient for e in entries])


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history", response_model=list[MealLogOut])
async def get_history(
    current_user: CurrentUser,
    db: DbDep,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 50,
):
    query = (
        select(MealLogEntry)
        .where(MealLogEntry.user_id == current_user.id)
        .options(selectinload(MealLogEntry.meal))
        .order_by(MealLogEntry.eaten_on.desc())
        .limit(limit)
    )
    if from_date:
        query = query.where(MealLogEntry.eaten_on >= from_date)
    if to_date:
        query = query.where(MealLogEntry.eaten_on <= to_date)

    result = await db.execute(query)
    return result.scalars().all()
