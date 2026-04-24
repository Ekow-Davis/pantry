from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, meals, planning, recommendations, admin

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(meals.router)
api_router.include_router(planning.router)
api_router.include_router(recommendations.router)
api_router.include_router(admin.router)
