from enum import Enum

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

tracer = trace.get_tracer(__name__)


class CustomHTTPExceptionInfo:
    def __init__(
        self, status_code: int, error_code: str, detail: str, log_detail: str
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.log_detail = log_detail


class CustomHTTPExceptionInfos(Enum):
    """
    Custom HTTP Exceptions.

    Error Code Ranges:
    - 1000-1999: Authentication & Authorization
    - 2000-2999: Database/Storage (all tables/entities)
    - 3000-3999: String Instruments (business logic)
    - 4000-4999: Wind Instruments (business logic)
    - 5000-5999: Percussion Instruments (business logic)
    - 6000-6999: Keyboard Instruments (business logic)
    - 7000-7999: Electronic/Synthesizers (business logic)
    - 8000-8999: Vocal (business logic)
    - 9000-9999: Audio Processing (format conversion, effects, filters)
    - 10000-10999: Schema/Validation errors

    Note: Feature-specific exceptions are defined in api/core/exceptions/<feature>.py
    """

    pass


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        detail: str,
        log_detail: str,
        headers: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.log_detail = log_detail
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )


# ==================== Exception Handlers ====================


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    with tracer.start_as_current_span("HTTPException") as span:
        span.set_status(Status(StatusCode.ERROR, str(exc.detail)))
        span.record_exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def custom_http_exception_handler(
    _request: Request, exc: CustomHTTPException
) -> JSONResponse:
    with tracer.start_as_current_span("CustomHTTPException") as span:
        span.set_status(Status(StatusCode.ERROR, str(exc.detail)))
        span.set_attribute("error_code", exc.error_code)
        span.record_exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )
