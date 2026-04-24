from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from app.api.deps import DbDep, CurrentUser
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.plan import DailyPlan, DailyPlanSlot
from app.models.log import MealLogEntry
from app.models.meal import Meal
from app.models.base import PlanStatus, SlotStatus
from app.schemas.plan import DailyPlanOut, UpdateSlotRequest, LogExtraMealRequest
from app.schemas.log import MealLogOut
from app.schemas.common import MessageResponse
from app.services.planner import generate_plan_for_date

router = APIRouter(prefix="/plan", tags=["Planning"])


def _plan_eager():
    return [selectinload(DailyPlan.slots).selectinload(DailyPlanSlot.meal)]


@router.get("/today", response_model=DailyPlanOut)
async def get_today_plan(current_user: CurrentUser, db: DbDep):
    return await _get_or_create(current_user, date.today(), db)


@router.get("/{plan_date}", response_model=DailyPlanOut)
async def get_plan_by_date(plan_date: date, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(DailyPlan)
        .where(DailyPlan.user_id == current_user.id, DailyPlan.plan_date == plan_date)
        .options(*_plan_eager())
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan")
    return plan


@router.post("/generate", response_model=DailyPlanOut, status_code=201)
async def generate_plan(current_user: CurrentUser, db: DbDep, plan_date: date | None = None):
    target = plan_date or date.today()
    existing = (await db.execute(
        select(DailyPlan).where(DailyPlan.user_id == current_user.id, DailyPlan.plan_date == target)
    )).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()
    return await generate_plan_for_date(current_user, target, db)


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
        meal = await db.get(Meal, payload.replacement_meal_id)
        if not meal:
            raise NotFoundException("Replacement meal")
        slot.meal_id = payload.replacement_meal_id

    slot.status = payload.status
    if payload.status == SlotStatus.CONFIRMED:
        db.add(MealLogEntry(
            user_id=current_user.id,
            slot_id=slot.id,
            meal_id=slot.meal_id,
            eaten_on=slot.plan.plan_date,
            was_planned=True,
        ))

    db.add(slot)
    await db.flush()

    plan = (await db.execute(
        select(DailyPlan).where(DailyPlan.id == slot.plan_id).options(*_plan_eager())
    )).scalar_one()
    return plan


@router.post("/log", response_model=MealLogOut, status_code=201)
async def log_extra_meal(payload: LogExtraMealRequest, current_user: CurrentUser, db: DbDep):
    if not await db.get(Meal, payload.meal_id):
        raise NotFoundException("Meal")
    log = MealLogEntry(
        user_id=current_user.id,
        meal_id=payload.meal_id,
        eaten_on=payload.eaten_on or date.today(),
        was_planned=False,
        notes=payload.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log, ["meal"])
    return log


@router.delete("/{plan_date}", response_model=MessageResponse)
async def delete_plan(plan_date: date, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(DailyPlan).where(DailyPlan.user_id == current_user.id, DailyPlan.plan_date == plan_date)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan")
    await db.delete(plan)
    return MessageResponse(message="Plan deleted.")


async def _get_or_create(user, plan_date: date, db):
    result = await db.execute(
        select(DailyPlan)
        .where(DailyPlan.user_id == user.id, DailyPlan.plan_date == plan_date)
        .options(*_plan_eager())
    )
    plan = result.scalar_one_or_none()
    if plan:
        return plan
    return await generate_plan_for_date(user, plan_date, db)
