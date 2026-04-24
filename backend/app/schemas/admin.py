from pydantic import BaseModel


class AdminStatsOut(BaseModel):
    total_meals: int
    active_meals: int
    pending_meals: int
    hidden_meals: int
    pending_contributions: int
    approved_contributions: int
    rejected_contributions: int
    total_users: int
    active_users: int
    admin_users: int
    total_log_entries: int
    total_ingredients: int
    ingredients_missing_nutrition: int
