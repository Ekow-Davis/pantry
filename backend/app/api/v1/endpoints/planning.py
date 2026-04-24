from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timezone
from app.api.deps import DbDep, CurrentUser
from app.core.exceptions import NotFoundException, BadRequestException
from app.models import (
    DailyPlan, DailyPlanSlot, MealLogEntry, Meal,
    PlanStatus, SlotStatus, SlotType, MealStatus
)
from app.schemas.schemas import (
    DailyPlanOut, UpdateSlotRequest, LogExtraMealRequest, MessageResponse, MealLogOut
)
from app.services.planner import generate_plan_for_date

router = APIRouter(prefix="/plan", tags=["Planning"])


def _plan_options():
    return [
        selectinload(DailyPlan.slots).selectinload(DailyPlanSlot.meal)
    ]


@router.get("/today", response_model=DailyPlanOut)
async def get_today_plan(current_user: CurrentUser, db: DbDep):
    today = date.today()
    return await _get_or_create_plan(current_user.id, today, db, current_user)


@router.get("/{plan_date}", response_model=DailyPlanOut)
async def get_plan_by_date(plan_date: date, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(DailyPlan)
        .where(DailyPlan.user_id == current_user.id, DailyPlan.plan_date == plan_date)
        .options(*_plan_options())
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan")
    return plan


@router.post("/generate", response_model=DailyPlanOut, status_code=201)
async def generate_plan(current_user: CurrentUser, db: DbDep, plan_date: date | None = None):
    target_date = plan_date or date.today()

    # Delete existing plan for the date if any
    existing = await db.execute(
        select(DailyPlan).where(
            DailyPlan.user_id == current_user.id,
            DailyPlan.plan_date == target_date,
        )
    )
    old_plan = existing.scalar_one_or_none()
    if old_plan:
        await db.delete(old_plan)
        await db.flush()

    plan = await generate_plan_for_date(current_user, target_date, db)
    return plan


@router.patch("/slots/{slot_id}", response_model=DailyPlanOut)
async def update_slot(slot_id: str, payload: UpdateSlotRequest, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(DailyPlanSlot)
        .where(DailyPlanSlot.id == slot_id)
        .options(selectinload(DailyPlanSlot.plan))
    )
    slot = result.scalar_one_or_none()
    if not slot or slot.plan.user_id != current_user.id:
        raise NotFoundException("Slot")

    if payload.status == SlotStatus.REPLACED:
        if not payload.replacement_meal_id:
            raise BadRequestException("replacement_meal_id is required when replacing a slot.")
        meal = await db.get(Meal, payload.replacement_meal_id)
        if not meal:
            raise NotFoundException("Replacement meal")
        slot.meal_id = payload.replacement_meal_id

    slot.status = payload.status

    # If confirmed — create a log entry
    if payload.status == SlotStatus.CONFIRMED:
        log = MealLogEntry(
            user_id=current_user.id,
            slot_id=slot.id,
            meal_id=slot.meal_id,
            eaten_on=slot.plan.plan_date,
            was_planned=True,
        )
        db.add(log)

    # If skipped — no log entry (cooldown not consumed)

    db.add(slot)
    await db.flush()

    # Return the full plan
    plan_result = await db.execute(
        select(DailyPlan)
        .where(DailyPlan.id == slot.plan_id)
        .options(*_plan_options())
    )
    return plan_result.scalar_one()


@router.post("/log", response_model=MealLogOut, status_code=201)
async def log_extra_meal(payload: LogExtraMealRequest, current_user: CurrentUser, db: DbDep):
    meal = await db.get(Meal, payload.meal_id)
    if not meal:
        raise NotFoundException("Meal")

    eaten = payload.eaten_on or date.today()

    log = MealLogEntry(
        user_id=current_user.id,
        meal_id=payload.meal_id,
        eaten_on=eaten,
        was_planned=False,
        notes=payload.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log, ["meal"])
    return log


# ── Internal helper ───────────────────────────────────────────────────────────

async def _get_or_create_plan(user_id, plan_date, db, user):
    result = await db.execute(
        select(DailyPlan)
        .where(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date)
        .options(*_plan_options())
    )
    plan = result.scalar_one_or_none()
    if plan:
        return plan
    return await generate_plan_for_date(user, plan_date, db)
