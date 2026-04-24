import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import UserRole, utcnow, new_uuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Accra")
    cooldown_days: Mapped[int] = mapped_column(Integer, default=4)
    assume_cooked: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # relationships
    meal_preferences: Mapped[List["UserMealPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
    daily_plans: Mapped[List["DailyPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
    blacklist: Mapped[List["UserBlacklist"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
    pantry: Mapped[List["UserPantry"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
    log_entries: Mapped[List["MealLogEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
    contributions: Mapped[List["MealContribution"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa
