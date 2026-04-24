import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.models.base import utcnow, new_uuid


class UserBlacklist(Base):
    __tablename__ = "user_blacklists"
    __table_args__ = (UniqueConstraint("user_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    is_allergy: Mapped[bool] = mapped_column(Boolean, default=False)
    is_unavailable: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="blacklist")  # noqa
    ingredient: Mapped["Ingredient"] = relationship(back_populates="blacklisted_by")  # noqa


class UserPantry(Base):
    __tablename__ = "user_pantry"
    __table_args__ = (UniqueConstraint("user_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="pantry")  # noqa
    ingredient: Mapped["Ingredient"] = relationship(back_populates="pantry_entries")  # noqa
