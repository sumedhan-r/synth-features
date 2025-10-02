from fastapi import APIRouter

from src.api.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", description="Check if the application is accessible")
async def health() -> dict:
    return {"status": "ok"}
