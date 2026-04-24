from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.schemas.meal import MealOut


class MealLogOut(BaseModel):
    id: UUID
    meal: MealOut
    eaten_on: date
    was_planned: bool
    notes: Optional[str]
    logged_at: datetime

    model_config = {"from_attributes": True}
