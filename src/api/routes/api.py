from fastapi import APIRouter

from src.api.routes.docs import router as docs_router
from src.api.routes.health import router as health_router

router = APIRouter()

router.include_router(
    docs_router,
    prefix="/docs",
    tags=["documentation"],
)

router.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
)
