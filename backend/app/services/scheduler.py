from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timezone
import logging

from app.db.session import AsyncSessionLocal
from app.models import DailyPlan, DailyPlanSlot, MealLogEntry, SlotStatus, PlanStatus, User

logger = logging.getLogger("pantry-api.scheduler")

scheduler = AsyncIOScheduler(timezone="Africa/Accra")


def start_scheduler():
    # End-of-day cooldown confirmation — runs at 23:30 every night
    scheduler.add_job(
        end_of_day_confirmation,
        CronTrigger(hour=23, minute=30),
        id="end_of_day_confirmation",
        replace_existing=True,
    )

    # Nightly plan cleanup / stats update — runs at 00:05
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


# ── Jobs ──────────────────────────────────────────────────────────────────────

async def end_of_day_confirmation():
    """
    For each user with active plans from today that still have SUGGESTED slots:
      - If assume_cooked is True → create log entries for unconfirmed slots
      - If assume_cooked is False → leave them as-is (no cooldown consumed)
    """
    logger.info("Running end-of-day confirmation job.")
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            # Load all active plans for today with unconfirmed slots
            result = await db.execute(
                select(DailyPlan)
                .where(DailyPlan.plan_date == today, DailyPlan.status == PlanStatus.ACTIVE)
                .options(
                    selectinload(DailyPlan.slots),
                    selectinload(DailyPlan.user),
                )
            )
            plans = result.scalars().all()

            for plan in plans:
                user = plan.user
                for slot in plan.slots:
                    if slot.status != SlotStatus.SUGGESTED:
                        continue  # already handled by user
                    if not slot.meal_id:
                        continue  # empty slot

                    if user.assume_cooked:
                        # Create log entry — meal is treated as cooked
                        log = MealLogEntry(
                            user_id=user.id,
                            slot_id=slot.id,
                            meal_id=slot.meal_id,
                            eaten_on=today,
                            was_planned=True,
                            notes="Auto-confirmed by end-of-day job.",
                        )
                        db.add(log)
                        slot.status = SlotStatus.CONFIRMED
                        db.add(slot)
                    # else: assume_cooked is False — slot stays SUGGESTED, no log, no cooldown

                plan.status = PlanStatus.COMPLETED
                db.add(plan)

            await db.commit()
            logger.info(f"End-of-day job completed. Processed {len(plans)} plans.")

        except Exception as e:
            await db.rollback()
            logger.error(f"End-of-day job failed: {e}")


async def nightly_maintenance():
    """
    Lightweight nightly job:
    - Mark any leftover DRAFT plans older than today as COMPLETED
    """
    logger.info("Running nightly maintenance job.")
    today = date.today()

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(DailyPlan).where(
                    DailyPlan.plan_date < today,
                    DailyPlan.status == PlanStatus.DRAFT,
                )
            )
            old_plans = result.scalars().all()
            for plan in old_plans:
                plan.status = PlanStatus.COMPLETED
                db.add(plan)

            await db.commit()
            logger.info(f"Nightly maintenance: marked {len(old_plans)} stale plans as completed.")

        except Exception as e:
            await db.rollback()
            logger.error(f"Nightly maintenance failed: {e}")
