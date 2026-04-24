import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import utcnow, new_uuid


class MealLogEntry(Base):
    __tablename__ = "meal_log_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("daily_plan_slots.id", ondelete="SET NULL"), nullable=True)
    meal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="RESTRICT"), nullable=False)
    eaten_on: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    was_planned: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="log_entries")  # noqa
    slot: Mapped[Optional["DailyPlanSlot"]] = relationship(back_populates="log_entry")  # noqa
    meal: Mapped["Meal"] = relationship(back_populates="log_entries")  # noqa
