import time
from collections.abc import Awaitable, Callable
from typing import Any

from asgi_correlation_id import correlation_id
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.types import ASGIApp

from src.api.core.logger import bind_context, clear_context, get_logger
from src.api.core.tracer import add_trace_attributes, set_request_context


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response


class StrictTransportSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response


class XContentTypeOptionsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add structured logging context to requests."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Extract correlation ID from headers (set by TracingCorrelationMiddleware)
        corr_id = correlation_id.get()

        # Clear any existing context
        clear_context()

        # Bind request context
        bind_context(
            correlation_id=corr_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.time()

        # Log request start
        self.logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            correlation_id=corr_id,
        )

        try:
            # Process request
            response = await call_next(request)

        except Exception as e:
            # Log request error
            process_time = time.time() - start_time

            # Extract custom error code if it's a CustomHTTPException
            error_context = {
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time_ms": round(process_time * 1000, 2),
                "correlation_id": corr_id,
            }

            # Add error_code if it's a CustomHTTPException
            if hasattr(e, "error_code"):
                error_context["error_code"] = e.error_code

            self.logger.exception("Request failed", **error_context)
            raise
        else:
            # Calculate processing time
            process_time = time.time() - start_time

            # Log request completion
            self.logger.info(
                "Request completed",
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                correlation_id=corr_id,
            )

            return response

        finally:
            # Clear context after request
            clear_context()


class TracingCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation context to traces."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Generate or extract correlation ID
        corr_id = correlation_id.get()

        # Set correlation context
        correlation_context: dict[str, Any] = {"correlation_id": corr_id}

        # Set request context for the duration of this request
        set_request_context(**correlation_context)

        # Add correlation headers to response
        start_time = time.time()

        try:
            response = await call_next(request)

            # Add timing and status to trace
            processing_time = time.time() - start_time
            add_trace_attributes(
                **{
                    "http.status_code": response.status_code,
                    "http.response_time_ms": round(processing_time * 1000, 2),
                    "request.success": response.status_code < HTTP_400_BAD_REQUEST,
                }  # type: ignore[arg-type]
            )

        except Exception as e:
            processing_time = time.time() - start_time
            add_trace_attributes(
                **{
                    "error": True,
                    "exception.type": type(e).__name__,
                    "exception.message": str(e),
                    "http.response_time_ms": round(processing_time * 1000, 2),
                    "request.success": False,
                }  # type: ignore[arg-type]
            )
            raise
        else:
            return response
