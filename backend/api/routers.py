from fastapi import APIRouter
from backend.api.endpoints import chat_route, health_route, user_route

api_routers = APIRouter()

api_routers.include_router(health_route.router, prefix="/health", tags=["health"])
api_routers.include_router(user_route.router, prefix="/user", tags=["user"])
api_routers.include_router(chat_route.router, prefix="/chat", tags=["chat"])