from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def server_health_check():
    """Server's health check router."""
    return {"success": True}
