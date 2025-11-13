from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

from src.api.core.config import get_config
from src.api.core.exception import (
    CustomHTTPException,
    custom_http_exception_handler,
    http_exception_handler,
)
from src.api.core.lifespan import lifespan
from src.api.core.logger import get_logger
from src.api.core.middleware import (
    CacheControlMiddleware,
    SecurityHeadersMiddleware,
    StrictTransportSecurityMiddleware,
    StructuredLoggingMiddleware,
    TracingCorrelationMiddleware,
    XContentTypeOptionsMiddleware,
)
from src.api.core.tracer import setup_tracer
from src.api.routes.api import router as api_router

project_config = get_config()
tracer = setup_tracer()
logger = get_logger(__name__)

app = FastAPI(
    title="Synth Features",
    docs_url=None,
    redoc_url=None,
    version="v1.0",
    lifespan=lifespan,
)


async def startup_event() -> None:
    logger.info("Application is starting...")


async def shutdown_event() -> None:
    logger.info("Application is shutting down...")


app.include_router(api_router)

# Observability middleware - applied first to trace/log entire request lifecycle
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(TracingCorrelationMiddleware)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Correlation-ID",
    update_request_header=True,
)
app.add_middleware(OpenTelemetryMiddleware)  # type: ignore[arg-type]

# Security middleware - enforce security policies and restrictions
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StrictTransportSecurityMiddleware)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(XContentTypeOptionsMiddleware)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=project_config.authorization.trusted_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
