from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from app.api.deps import DbDep, CurrentUser
from app.core.exceptions import NotFoundException, ConflictException
from app.models.user import User
from app.models.pantry import UserBlacklist, UserPantry
from app.models.ingredient import Ingredient
from app.models.log import MealLogEntry
from app.schemas.user import UserOut, UpdatePreferencesRequest
from app.schemas.pantry import BlacklistOut, BlacklistAdd, PantryOut, PantrySet
from app.schemas.log import MealLogOut
from app.schemas.common import MessageResponse

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
    if not await db.get(Ingredient, payload.ingredient_id):
        raise NotFoundException("Ingredient")
    existing = (await db.execute(
        select(UserBlacklist).where(
            UserBlacklist.user_id == current_user.id,
            UserBlacklist.ingredient_id == payload.ingredient_id,
        )
    )).scalar_one_or_none()
    if existing:
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


@router.patch("/blacklist/{entry_id}", response_model=BlacklistOut)
async def update_blacklist_entry(entry_id: str, payload: BlacklistAdd, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserBlacklist).where(UserBlacklist.id == entry_id, UserBlacklist.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Blacklist entry")
    entry.reason = payload.reason
    entry.is_allergy = payload.is_allergy
    entry.is_unavailable = payload.is_unavailable
    db.add(entry)
    await db.flush()
    await db.refresh(entry, ["ingredient"])
    return entry


@router.delete("/blacklist/{entry_id}", response_model=MessageResponse)
async def remove_from_blacklist(entry_id: str, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserBlacklist).where(UserBlacklist.id == entry_id, UserBlacklist.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Blacklist entry")
    await db.delete(entry)
    return MessageResponse(message="Ingredient removed from blacklist.")


@router.delete("/blacklist", response_model=MessageResponse)
async def clear_blacklist(current_user: CurrentUser, db: DbDep):
    result = await db.execute(select(UserBlacklist).where(UserBlacklist.user_id == current_user.id))
    for entry in result.scalars().all():
        await db.delete(entry)
    return MessageResponse(message="Blacklist cleared.")


# ── Pantry ────────────────────────────────────────────────────────────────────

@router.get("/pantry", response_model=PantryOut)
async def get_pantry(current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(UserPantry)
        .where(UserPantry.user_id == current_user.id)
        .options(selectinload(UserPantry.ingredient).selectinload(Ingredient.nutrition))
    )
    return PantryOut(ingredients=[e.ingredient for e in result.scalars().all()])


@router.put("/pantry", response_model=PantryOut)
async def replace_pantry(payload: PantrySet, current_user: CurrentUser, db: DbDep):
    existing = (await db.execute(select(UserPantry).where(UserPantry.user_id == current_user.id))).scalars().all()
    for e in existing:
        await db.delete(e)
    for ingredient_id in payload.ingredient_ids:
        if await db.get(Ingredient, ingredient_id):
            db.add(UserPantry(user_id=current_user.id, ingredient_id=ingredient_id))
    await db.flush()
    result = await db.execute(
        select(UserPantry)
        .where(UserPantry.user_id == current_user.id)
        .options(selectinload(UserPantry.ingredient).selectinload(Ingredient.nutrition))
    )
    return PantryOut(ingredients=[e.ingredient for e in result.scalars().all()])


@router.delete("/pantry", response_model=MessageResponse)
async def clear_pantry(current_user: CurrentUser, db: DbDep):
    existing = (await db.execute(select(UserPantry).where(UserPantry.user_id == current_user.id))).scalars().all()
    for e in existing:
        await db.delete(e)
    return MessageResponse(message="Pantry cleared.")


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
    return (await db.execute(query)).scalars().all()


@router.delete("/history/{entry_id}", response_model=MessageResponse)
async def delete_log_entry(entry_id: str, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(MealLogEntry).where(MealLogEntry.id == entry_id, MealLogEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Log entry")
    await db.delete(entry)
    return MessageResponse(message="Log entry removed.")
