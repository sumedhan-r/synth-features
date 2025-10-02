from enum import Enum

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
from starlette.status import (
    HTTP_403_FORBIDDEN,
)

tracer = trace.get_tracer(__name__)


class CustomHTTPExceptionInfo:
    def __init__(
        self, status_code: int, error_code: str, detail: str, log_detail: str
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.log_detail = log_detail


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        detail: str,
        headers: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )


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


class CustomHTTPExceptionInfos(Enum):
    """Custom HTTP Exceptions.

    1000 -> Auth related
    2000 -> Development / Maintainance
    """

    SESSION_EXPIRED = CustomHTTPExceptionInfo(
        HTTP_403_FORBIDDEN,
        "RAIERR1001",
        "Session expired",
        "Session has expired. Please log in again.",
    )


class SessionExpiredHTTPException(CustomHTTPException):
    def __init__(self) -> None:
        self.status_code = CustomHTTPExceptionInfos.SESSION_EXPIRED.value.status_code
        self.error_code = CustomHTTPExceptionInfos.SESSION_EXPIRED.value.error_code
        self.detail = CustomHTTPExceptionInfos.SESSION_EXPIRED.value.detail
        super().__init__(
            status_code=self.status_code, error_code=self.error_code, detail=self.detail
        )
