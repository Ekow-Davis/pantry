import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import SlotType, SlotStatus, PlanStatus, utcnow, new_uuid


class DailyPlan(Base):
    __tablename__ = "daily_plans"
    __table_args__ = (UniqueConstraint("user_id", "plan_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[PlanStatus] = mapped_column(SAEnum(PlanStatus), default=PlanStatus.DRAFT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="daily_plans")  # noqa
    slots: Mapped[List["DailyPlanSlot"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="DailyPlanSlot.slot_order",
    )


class DailyPlanSlot(Base):
    __tablename__ = "daily_plan_slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("daily_plans.id", ondelete="CASCADE"), nullable=False)
    meal_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="SET NULL"), nullable=True)
    slot_type: Mapped[SlotType] = mapped_column(SAEnum(SlotType), nullable=False)
    slot_order: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[SlotStatus] = mapped_column(SAEnum(SlotStatus), default=SlotStatus.SUGGESTED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plan: Mapped["DailyPlan"] = relationship(back_populates="slots")
    meal: Mapped[Optional["Meal"]] = relationship(back_populates="plan_slots")  # noqa
    log_entry: Mapped[Optional["MealLogEntry"]] = relationship(back_populates="slot", uselist=False)  # noqa
