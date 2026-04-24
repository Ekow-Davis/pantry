from fastapi import APIRouter, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.api.deps import DbDep, CurrentAdmin
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException
from app.core.security import hash_password
from app.models.user import User
from app.models.meal import Meal, MealCategory, MealCategoryMap
from app.models.ingredient import Ingredient, IngredientNutrition
from app.models.contribution import MealContribution
from app.models.log import MealLogEntry
from app.models.base import MealStatus, ContributionStatus, UserRole
from app.schemas.user import UserOut, AdminUpdateUserRequest
from app.schemas.auth import RegisterRequest
from app.schemas.meal import MealOut
from app.schemas.contribution import ContributionOut, ReviewContributionRequest
from app.schemas.admin import AdminStatsOut
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── User management ───────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: DbDep,
    current_admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    role: str | None = None,
    is_active: bool | None = None,
):
    query = select(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    return (await db.execute(query)).scalars().all()


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: DbDep, current_admin: CurrentAdmin):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    return user


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(payload: RegisterRequest, db: DbDep, current_admin: CurrentAdmin):
    if (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none():
        raise ConflictException("An account with this email already exists.")
    if (await db.execute(select(User).where(User.username == payload.username))).scalar_one_or_none():
        raise ConflictException("This username is already taken.")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        country=payload.country,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: str, payload: AdminUpdateUserRequest, db: DbDep, current_admin: CurrentAdmin):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.cooldown_days is not None:
        user.cooldown_days = payload.cooldown_days
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: str, db: DbDep, current_admin: CurrentAdmin):
    if str(current_admin.id) == user_id:
        raise BadRequestException("You cannot delete your own account.")
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    await db.delete(user)
    return MessageResponse(message="User deleted.")


@router.patch("/users/{user_id}/deactivate", response_model=UserOut)
async def deactivate_user(user_id: str, db: DbDep, current_admin: CurrentAdmin):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    user.is_active = False
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}/reactivate", response_model=UserOut)
async def reactivate_user(user_id: str, db: DbDep, current_admin: CurrentAdmin):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    user.is_active = True
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ── Meal management ───────────────────────────────────────────────────────────

@router.get("/meals", response_model=list[MealOut])
async def list_all_meals(
    db: DbDep,
    current_admin: CurrentAdmin,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    query = (
        select(Meal)
        .options(selectinload(Meal.category_mappings).selectinload(MealCategoryMap.category))
        .order_by(Meal.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if status:
        query = query.where(Meal.status == status)
    return (await db.execute(query)).scalars().unique().all()


# ── Contribution queue ────────────────────────────────────────────────────────

@router.get("/contributions", response_model=list[ContributionOut])
async def list_contributions(
    db: DbDep,
    current_admin: CurrentAdmin,
    status: str = "pending",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    result = await db.execute(
        select(MealContribution)
        .where(MealContribution.status == status)
        .options(selectinload(MealContribution.meal))
        .order_by(MealContribution.submitted_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()


@router.get("/contributions/{contribution_id}", response_model=ContributionOut)
async def get_contribution(contribution_id: str, db: DbDep, current_admin: CurrentAdmin):
    result = await db.execute(
        select(MealContribution)
        .where(MealContribution.id == contribution_id)
        .options(selectinload(MealContribution.meal))
    )
    c = result.scalar_one_or_none()
    if not c:
        raise NotFoundException("Contribution")
    return c


@router.patch("/contributions/{contribution_id}", response_model=ContributionOut)
async def review_contribution(
    contribution_id: str,
    payload: ReviewContributionRequest,
    db: DbDep,
    current_admin: CurrentAdmin,
):
    result = await db.execute(
        select(MealContribution)
        .where(MealContribution.id == contribution_id)
        .options(selectinload(MealContribution.meal))
    )
    c = result.scalar_one_or_none()
    if not c:
        raise NotFoundException("Contribution")
    if c.status != ContributionStatus.PENDING:
        raise BadRequestException("This contribution has already been reviewed.")

    c.status = payload.status
    c.rejection_reason = payload.rejection_reason
    c.reviewed_at = datetime.now(timezone.utc)

    if c.meal:
        c.meal.status = MealStatus.ACTIVE if payload.status == ContributionStatus.APPROVED else MealStatus.REJECTED

    db.add(c)
    await db.flush()
    await db.refresh(c)
    return c


@router.delete("/contributions/{contribution_id}", response_model=MessageResponse)
async def delete_contribution(contribution_id: str, db: DbDep, current_admin: CurrentAdmin):
    c = await db.get(MealContribution, contribution_id)
    if not c:
        raise NotFoundException("Contribution")
    await db.delete(c)
    return MessageResponse(message="Contribution deleted.")


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsOut)
async def get_stats(db: DbDep, current_admin: CurrentAdmin):
    async def count(query):
        return (await db.execute(query)).scalar() or 0

    total_meals = await count(select(func.count(Meal.id)))
    active_meals = await count(select(func.count(Meal.id)).where(Meal.status == MealStatus.ACTIVE))
    pending_meals = await count(select(func.count(Meal.id)).where(Meal.status == MealStatus.PENDING))
    hidden_meals = await count(select(func.count(Meal.id)).where(Meal.status == MealStatus.HIDDEN))

    pending_contrib = await count(select(func.count(MealContribution.id)).where(MealContribution.status == ContributionStatus.PENDING))
    approved_contrib = await count(select(func.count(MealContribution.id)).where(MealContribution.status == ContributionStatus.APPROVED))
    rejected_contrib = await count(select(func.count(MealContribution.id)).where(MealContribution.status == ContributionStatus.REJECTED))

    total_users = await count(select(func.count(User.id)))
    active_users = await count(select(func.count(User.id)).where(User.is_active == True))  # noqa
    admin_users = await count(select(func.count(User.id)).where(User.role == UserRole.ADMIN))

    total_logs = await count(select(func.count(MealLogEntry.id)))
    total_ingredients = await count(select(func.count(Ingredient.id)))
    ingredients_with_nutrition = await count(select(func.count(IngredientNutrition.id)))

    return AdminStatsOut(
        total_meals=total_meals,
        active_meals=active_meals,
        pending_meals=pending_meals,
        hidden_meals=hidden_meals,
        pending_contributions=pending_contrib,
        approved_contributions=approved_contrib,
        rejected_contributions=rejected_contrib,
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        total_log_entries=total_logs,
        total_ingredients=total_ingredients,
        ingredients_missing_nutrition=total_ingredients - ingredients_with_nutrition,
    )
