from fastapi import APIRouter
from app.api.deps import DbDep, CurrentUser
from app.schemas.schemas import DailyRecommendationOut, PantryMatchResult
from app.services.recommendations import get_daily_recommendation
from app.services.pantry import get_pantry_matches

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/daily", response_model=DailyRecommendationOut)
async def daily_recommendation(current_user: CurrentUser, db: DbDep):
    return await get_daily_recommendation(current_user, db)


@router.get("/pantry", response_model=PantryMatchResult)
async def pantry_recommendations(current_user: CurrentUser, db: DbDep):
    return await get_pantry_matches(current_user, db)
