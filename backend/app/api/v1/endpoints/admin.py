from fastapi import APIRouter
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.api.deps import DbDep, CurrentAdmin
from app.core.exceptions import NotFoundException, BadRequestException
from app.models import (
    Meal, MealStatus, MealContribution, ContributionStatus,
    User, MealLogEntry, Ingredient, IngredientNutrition
)
from app.schemas.schemas import (
    ContributionOut, ReviewContributionRequest,
    AdminStatsOut, UserOut, MealOut, MessageResponse
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Contributions ─────────────────────────────────────────────────────────────

@router.get("/contributions", response_model=list[ContributionOut])
async def list_contributions(db: DbDep, current_admin: CurrentAdmin, status: str = "pending"):
    result = await db.execute(
        select(MealContribution)
        .where(MealContribution.status == status)
        .options(
            selectinload(MealContribution.meal),
        )
        .order_by(MealContribution.submitted_at.asc())
    )
    return result.scalars().all()


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
    contribution = result.scalar_one_or_none()
    if not contribution:
        raise NotFoundException("Contribution")

    if contribution.status != ContributionStatus.PENDING:
        raise BadRequestException("This contribution has already been reviewed.")

    contribution.status = payload.status
    contribution.rejection_reason = payload.rejection_reason
    contribution.reviewed_at = datetime.now(timezone.utc)

    # Update the meal's status accordingly
    if contribution.meal:
        if payload.status == ContributionStatus.APPROVED:
            contribution.meal.status = MealStatus.ACTIVE
        else:
            contribution.meal.status = MealStatus.REJECTED

    db.add(contribution)
    await db.flush()
    await db.refresh(contribution)
    return contribution


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(db: DbDep, current_admin: CurrentAdmin, page: int = 1, page_size: int = 50):
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def update_user_role(user_id: str, role: str, db: DbDep, current_admin: CurrentAdmin):
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException("User")
    from app.models import UserRole
    if role not in [r.value for r in UserRole]:
        raise BadRequestException(f"Invalid role: {role}")
    user.role = role
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsOut)
async def get_stats(db: DbDep, current_admin: CurrentAdmin):
    total_meals = (await db.execute(select(func.count(Meal.id)))).scalar()
    active_meals = (await db.execute(select(func.count(Meal.id)).where(Meal.status == MealStatus.ACTIVE))).scalar()
    pending_contributions = (await db.execute(
        select(func.count(MealContribution.id)).where(MealContribution.status == ContributionStatus.PENDING)
    )).scalar()
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_logs = (await db.execute(select(func.count(MealLogEntry.id)))).scalar()

    # Ingredients with no nutrition entry
    ingredients_with_nutrition = (await db.execute(
        select(func.count(IngredientNutrition.id))
    )).scalar()
    total_ingredients = (await db.execute(select(func.count(Ingredient.id)))).scalar()
    missing_nutrition = total_ingredients - ingredients_with_nutrition

    return AdminStatsOut(
        total_meals=total_meals,
        active_meals=active_meals,
        pending_contributions=pending_contributions,
        total_users=total_users,
        total_log_entries=total_logs,
        ingredients_missing_nutrition=missing_nutrition,
    )
