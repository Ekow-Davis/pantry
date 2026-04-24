from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, model_validator
from app.models.base import ContributionStatus
from app.schemas.meal import MealOut


class ContributionOut(BaseModel):
    id: UUID
    user_id: UUID
    meal: Optional[MealOut]
    status: ContributionStatus
    rejection_reason: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ReviewContributionRequest(BaseModel):
    status: ContributionStatus
    rejection_reason: Optional[str] = None

    @model_validator(mode="after")
    def reason_required(self) -> "ReviewContributionRequest":
        if self.status == ContributionStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason is required when rejecting.")
        return self
