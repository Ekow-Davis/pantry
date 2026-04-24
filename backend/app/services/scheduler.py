from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
import logging

from app.db.session import AsyncSessionLocal
from app.models.plan import DailyPlan, DailyPlanSlot
from app.models.log import MealLogEntry
from app.models.base import SlotStatus, PlanStatus

logger = logging.getLogger("pantry-api.scheduler")
scheduler = AsyncIOScheduler(timezone="Africa/Accra")


def start_scheduler():
    scheduler.add_job(
        end_of_day_confirmation,
        CronTrigger(hour=23, minute=30),
        id="end_of_day_confirmation",
        replace_existing=True,
    )
    scheduler.add_job(
        nightly_maintenance,
        CronTrigger(hour=0, minute=5),
        id="nightly_maintenance",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")


async def end_of_day_confirmation():
    logger.info("Running end-of-day confirmation.")
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(DailyPlan)
                .where(DailyPlan.plan_date == today, DailyPlan.status == PlanStatus.ACTIVE)
                .options(selectinload(DailyPlan.slots), selectinload(DailyPlan.user))
            )
            plans = result.scalars().all()

            for plan in plans:
                user = plan.user
                for slot in plan.slots:
                    if slot.status != SlotStatus.SUGGESTED or not slot.meal_id:
                        continue
                    if user.assume_cooked:
                        db.add(MealLogEntry(
                            user_id=user.id,
                            slot_id=slot.id,
                            meal_id=slot.meal_id,
                            eaten_on=today,
                            was_planned=True,
                            notes="Auto-confirmed by end-of-day job.",
                        ))
                        slot.status = SlotStatus.CONFIRMED
                        db.add(slot)

                plan.status = PlanStatus.COMPLETED
                db.add(plan)

            await db.commit()
            logger.info(f"End-of-day job done. {len(plans)} plans processed.")
        except Exception as e:
            await db.rollback()
            logger.error(f"End-of-day job failed: {e}")


async def nightly_maintenance():
    logger.info("Running nightly maintenance.")
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(DailyPlan).where(
                    DailyPlan.plan_date < today,
                    DailyPlan.status == PlanStatus.DRAFT,
                )
            )
            for plan in result.scalars().all():
                plan.status = PlanStatus.COMPLETED
                db.add(plan)
            await db.commit()
            logger.info("Nightly maintenance done.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Nightly maintenance failed: {e}")
