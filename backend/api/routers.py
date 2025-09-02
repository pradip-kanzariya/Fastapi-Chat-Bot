from fastapi import APIRouter
from backend.api.endpoints import health, user, chat

api_routers = APIRouter()

api_routers.include_router(health.router, prefix="/health", tags=["health"])
api_routers.include_router(user.router, prefix="/user", tags=["user"])
api_routers.include_router(chat.router, prefix="/chat", tags=["chat"])