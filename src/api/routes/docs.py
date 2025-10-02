from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    """Serve Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Synth Features - API Docs",
    )
