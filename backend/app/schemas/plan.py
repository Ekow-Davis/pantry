from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, model_validator
from app.models.base import SlotType, SlotStatus, PlanStatus
from app.schemas.meal import MealOut


class PlanSlotOut(BaseModel):
    id: UUID
    meal: Optional[MealOut]
    slot_type: SlotType
    slot_order: int
    status: SlotStatus

    model_config = {"from_attributes": True}


class DailyPlanOut(BaseModel):
    id: UUID
    plan_date: date
    status: PlanStatus
    slots: List[PlanSlotOut]

    model_config = {"from_attributes": True}


class UpdateSlotRequest(BaseModel):
    status: SlotStatus
    replacement_meal_id: Optional[UUID] = None

    @model_validator(mode="after")
    def replacement_required(self) -> "UpdateSlotRequest":
        if self.status == SlotStatus.REPLACED and not self.replacement_meal_id:
            raise ValueError("replacement_meal_id is required when status is REPLACED.")
        return self


class LogExtraMealRequest(BaseModel):
    meal_id: UUID
    slot_type: SlotType
    eaten_on: Optional[date] = None
    notes: Optional[str] = None
