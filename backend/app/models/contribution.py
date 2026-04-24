import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import ContributionStatus, utcnow, new_uuid


class MealContribution(Base):
    __tablename__ = "meal_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[ContributionStatus] = mapped_column(SAEnum(ContributionStatus), default=ContributionStatus.PENDING, nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="contributions")  # noqa
    meal: Mapped[Optional["Meal"]] = relationship(back_populates="contributions")  # noqa
