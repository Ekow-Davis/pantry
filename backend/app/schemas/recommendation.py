from pydantic import BaseModel
from app.schemas.meal import MealOut


class DailyRecommendationOut(BaseModel):
    meal: MealOut
    reason: str
