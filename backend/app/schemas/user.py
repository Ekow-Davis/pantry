from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator
from app.models.base import UserRole


class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    country: Optional[str]
    timezone: str
    cooldown_days: int
    assume_cooked: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdatePreferencesRequest(BaseModel):
    cooldown_days: Optional[int] = None
    assume_cooked: Optional[bool] = None
    timezone: Optional[str] = None

    @field_validator("cooldown_days")
    @classmethod
    def validate_cooldown(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 30):
            raise ValueError("cooldown_days must be between 1 and 30.")
        return v


class AdminUpdateUserRequest(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    cooldown_days: Optional[int] = None
