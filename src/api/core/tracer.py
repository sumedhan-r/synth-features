import asyncio
import inspect
import os
import socket
import time
import uuid
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any

# Platform-agnostic OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGRPCSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPSpanExporter,
)
from opentelemetry.exporter.zipkin.json import ZipkinExporter

# Auto-instrumentation imports
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.sdk.trace.sampling import (
    Decision,
    Sampler,
    SamplingResult,
    TraceIdRatioBased,
    TraceState,
    get_current_span,
)

# Using direct string attributes instead of deprecated SpanAttributes
from opentelemetry.trace import Context, Link, SpanKind, Tracer
from opentelemetry.util.types import Attributes

from src.api.core.config import get_config
from src.api.schemas.tracer import TracingDecoratorOptions

request_context: ContextVar[dict[str, Any] | None] = ContextVar(
    "request_context", default=None
)


def _create_exporter(tracing_config) -> SpanExporter:
    """Create platform-agnostic trace exporter based on configuration."""
    exporter_type = tracing_config.exporter_type.lower()
    endpoint = tracing_config.exporter_endpoint
    headers = tracing_config.exporter_headers

    match exporter_type:
        case "console":
            return ConsoleSpanExporter()

        case "otlp":
            # Generic OTLP - user provides full endpoint and headers
            if not endpoint:
                raise ValueError("exporter_endpoint required for OTLP exporter")
            # Default to HTTP OTLP, detect gRPC by port or scheme
            if ":4317" in endpoint or endpoint.startswith("grpc://"):
                return OTLPGRPCSpanExporter(
                    endpoint=endpoint, headers=headers if headers else None
                )
            else:
                return OTLPHTTPSpanExporter(
                    endpoint=endpoint, headers=headers if headers else None
                )

        case "zipkin":
            if not endpoint:
                raise ValueError("exporter_endpoint required for Zipkin exporter")
            return ZipkinExporter(endpoint=endpoint)

        case "honeycomb":
            # Honeycomb uses OTLP HTTP
            honeycomb_endpoint = "https://api.honeycomb.io:443/v1/traces"
            honeycomb_headers = {
                "x-honeycomb-team": headers.get("api_key", ""),
                "x-honeycomb-dataset": headers.get(
                    "dataset", tracing_config.service_name
                ),
            }
            return OTLPHTTPSpanExporter(
                endpoint=honeycomb_endpoint, headers=honeycomb_headers
            )

        case "datadog":
            # Datadog Agent OTLP endpoint
            datadog_endpoint = endpoint or "http://localhost:8126/v0.4/traces"
            datadog_headers = {}
            if headers.get("api_key"):
                datadog_headers["DD-API-KEY"] = headers["api_key"]
            return OTLPHTTPSpanExporter(
                endpoint=datadog_endpoint,
                headers=datadog_headers if datadog_headers else None,
            )

        case "azure":
            # Azure Application Insights OTLP endpoint
            if not endpoint:
                raise ValueError(
                    "exporter_endpoint required for Azure (Application Insights OTLP endpoint)"
                )
            azure_headers = {}
            if headers.get("instrumentation_key"):
                azure_headers["Authorization"] = (
                    f"InstrumentationKey {headers['instrumentation_key']}"
                )
            return OTLPHTTPSpanExporter(
                endpoint=endpoint, headers=azure_headers if azure_headers else None
            )

        case "aws":
            # AWS X-Ray via OTLP
            aws_endpoint = endpoint or "https://otlp.amazonaws.com:4317"
            aws_headers = {}
            if headers.get("access_key_id") and headers.get("secret_access_key"):
                # Note: AWS requires proper AWS SDK authentication
                # This is a simplified approach - production should use AWS SDK
                aws_headers["x-aws-access-key-id"] = headers["access_key_id"]
                aws_headers["x-aws-secret-access-key"] = headers["secret_access_key"]
                if headers.get("session_token"):
                    aws_headers["x-aws-session-token"] = headers["session_token"]
            return OTLPGRPCSpanExporter(
                endpoint=aws_endpoint, headers=aws_headers if aws_headers else None
            )

        case "gcp" | "google":
            # Google Cloud Trace via OTLP
            gcp_endpoint = (
                endpoint
                or "https://cloudtrace.googleapis.com/v1/projects/PROJECT_ID/traces:batchWrite"
            )
            gcp_headers = {}
            if headers.get("api_key"):
                gcp_headers["Authorization"] = f"Bearer {headers['api_key']}"
            elif headers.get("service_account_key"):
                # Note: Production should use proper Google Auth SDK
                gcp_headers["Authorization"] = (
                    f"Bearer {headers['service_account_key']}"
                )
            return OTLPHTTPSpanExporter(
                endpoint=gcp_endpoint, headers=gcp_headers if gcp_headers else None
            )

        case _:
            raise ValueError(
                f"Unsupported exporter type: {exporter_type}. Supported: console, otlp, zipkin, honeycomb, datadog, azure, aws, gcp"
            )


def _create_sampling_strategy(tracing_config) -> Sampler:
    """Create sampling strategy based on configuration."""
    sampling_type = tracing_config.sampling_type.lower()
    sampling_ratio = tracing_config.sampling_ratio

    match sampling_type:
        case "ratio":
            base_sampler = TraceIdRatioBased(sampling_ratio)
        case "rate_limiting":
            # Future: implement rate limiting sampler
            # For now, fallback to ratio-based
            base_sampler = TraceIdRatioBased(sampling_ratio)
        case "custom":
            # Future: allow custom sampler injection
            # For now, fallback to ratio-based
            base_sampler = TraceIdRatioBased(sampling_ratio)
        case _:
            base_sampler = TraceIdRatioBased(sampling_ratio)

    return ExclusionSampler(base_sampler)


class ExclusionSampler(Sampler):
    """Sampler exclusion particular endpoints."""

    def __init__(self, base_sampler: Sampler) -> None:
        self.base_sampler = base_sampler

    def should_sample(
        self,
        parent_context: Context | None,
        trace_id: int,
        name: str,
        kind: SpanKind | None = None,
        attributes: Attributes = None,
        links: Sequence[Link] | None = None,
        trace_state: TraceState | None = None,
    ) -> SamplingResult:
        if any(substring in name for substring in ("health", "openapi.json", "docs")):
            decision = Decision.DROP
            # Extract the SpanContext from the parent Context
            parent_span_context = get_current_span(parent_context).get_span_context()

            # Use the parent span context's TraceState if available
            if (
                parent_span_context is not None
                and parent_span_context.trace_state is not None
            ):
                trace_state = parent_span_context.trace_state

            return SamplingResult(decision, attributes, trace_state)
        return self.base_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links, trace_state
        )

    def get_description(self) -> str:
        return "Custome sampler that does notsample spans with 'health' in the name"


def _create_service_resource(tracing_config) -> Resource:
    """Create service resource information for better trace identification."""
    # Get environment from ENV variable or config
    environment = os.getenv("ENV", "local").lower().replace("_", "-")

    # Create a unique instance ID using hostname + process ID + random component
    hostname = socket.gethostname()
    process_id = os.getpid()
    unique_suffix = str(uuid.uuid4())[:8]
    instance_id = f"{hostname}-{process_id}-{unique_suffix}"

    # Base resource attributes
    resource_attributes = {
        "service.name": tracing_config.service_name,
        "service.version": tracing_config.service_version,
        "service.instance.id": instance_id,
        "deployment.environment": environment,
        "host.name": hostname,
        "process.pid": process_id,
    }

    # Add custom resource attributes from config
    resource_attributes.update(tracing_config.resource_attributes)

    return Resource(attributes=resource_attributes)


def _instrument_libraries() -> None:
    """Instrument libraries for automatic span creation."""
    # Database instrumentation - all drivers for database-agnostic support
    AsyncPGInstrumentor().instrument()  # PostgreSQL async
    Psycopg2Instrumentor().instrument()  # PostgreSQL sync
    PyMySQLInstrumentor().instrument()  # MySQL
    SQLAlchemyInstrumentor().instrument()  # SQLAlchemy ORM (all databases)

    # Web framework and HTTP instrumentation
    FastAPIInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    URLLibInstrumentor().instrument()
    URLLib3Instrumentor().instrument()

    # Infrastructure instrumentation
    SystemMetricsInstrumentor().instrument()
    ThreadingInstrumentor().instrument()


def setup_tracer() -> Tracer | None:
    """Set up platform-agnostic OpenTelemetry tracing based on configuration."""
    config = get_config()
    tracing_config = config.tracing

    # Check if tracing is enabled
    if not tracing_config.enabled:
        return None

    # Set up resource and exporter
    resource = _create_service_resource(tracing_config)
    exporter = _create_exporter(tracing_config)
    span_processor = BatchSpanProcessor(exporter)

    # Set up sampling strategy
    sampler = _create_sampling_strategy(tracing_config)

    # Create tracer provider
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler,
    )
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Instrument libraries
    _instrument_libraries()

    return trace.get_tracer(__name__, tracer_provider=trace.get_tracer_provider())


def add_trace_attributes(**attributes: str | float | bool) -> None:
    """Add attributes to the current active span."""
    current_span = trace.get_current_span()
    if current_span.is_recording():
        for key, value in attributes.items():
            current_span.set_attribute(key, value)


def set_request_context(**context: str | float | bool) -> None:
    """Set request context for correlation across spans."""
    current_context = request_context.get() or {}
    current_context.update(context)
    request_context.set(current_context)

    # Also add to current span
    add_trace_attributes(**context)


def get_request_context() -> dict[str, Any]:
    """Get the current request context."""
    return request_context.get() or {}


@contextmanager
def create_inner_span(
    span_name: str,
    attributes: dict[str, Any] | None = None,
    *,
    record_exception: bool = True,
    func: Callable | None = None,
) -> Generator[Any, None, None]:
    """Create an inner span with simplified attribute handling.

    Args:
        span_name: Name of the span
        attributes: Optional dictionary of attributes to set on the span
        record_exception: Whether to record exceptions automatically
        func: Optional function to use for tracer module detection

    Usage:
        # Basic usage (uses caller's module)
        with create_inner_span("operation.name", {"key": "value"}):
            # Your code here
            pass

        # With specific function for tracer
        with create_inner_span("operation.name", {"key": "value"}, func=some_function):
            # Uses some_function.__module__ for tracer
            pass
    """
    # Determine tracer based on function or caller module
    if func is not None:
        # Use the provided function's module for tracer
        tracer = trace.get_tracer(func.__module__)
    else:
        # Get the calling module dynamically
        current_frame = inspect.currentframe()
        if current_frame is None or current_frame.f_back is None:
            # Fallback to tracer module name
            tracer = trace.get_tracer(__name__)
        else:
            caller_frame = current_frame.f_back
            caller_module = caller_frame.f_globals["__name__"]
            tracer = trace.get_tracer(caller_module)

    start_time = time.time()

    with tracer.start_as_current_span(
        span_name, record_exception=record_exception
    ) as span:
        # Set custom attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        # Add request context
        context = get_request_context()
        for key, value in context.items():
            if not key.startswith("http."):  # Avoid duplicating HTTP attributes
                span.set_attribute(f"request.{key}", str(value))

        try:
            yield span
        except Exception as e:
            span.set_attribute("operation.success", False)  # noqa: FBT003
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise
        else:
            # Calculate duration and set success attributes
            duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("duration_ms", round(duration_ms, 2))
            span.set_attribute("operation.success", True)  # noqa: FBT003


def _decorate_class(
    cls: type,
    record_exception: bool,  # noqa: FBT001
    attributes: dict[str, str] | None,
    existing_tracer: Tracer | None,
) -> type:
    """Decorate all non-private methods of a class."""
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        # Ignore private functions
        if not name.startswith("_"):
            if isinstance(inspect.getattr_static(cls, name), staticmethod):
                setattr(
                    cls,
                    name,
                    staticmethod(
                        instrument(
                            record_exception=record_exception,
                            attributes=attributes,
                            existing_tracer=existing_tracer,
                        )(method)
                    ),
                )
            else:
                setattr(
                    cls,
                    name,
                    instrument(
                        record_exception=record_exception,
                        attributes=attributes,
                        existing_tracer=existing_tracer,
                    )(method),
                )
    return cls


def _create_span_wrapper(
    func_or_class: Callable,
    span_name: str,
    record_exception: bool,  # noqa: FBT001
    attributes: dict[str, str] | None,
    existing_tracer: Tracer | None,
) -> Callable:
    """Create the appropriate span wrapper for sync or async functions."""
    # Check if already decorated
    undecorated_func = getattr(func_or_class, "__tracing_unwrapped__", None)
    if undecorated_func:
        return func_or_class

    func_or_class.__tracing_unwrapped__ = func_or_class  # type: ignore[attr-defined]
    tracer = existing_tracer or trace.get_tracer(func_or_class.__module__)

    if asyncio.iscoroutinefunction(func_or_class):
        wrapper = _create_async_wrapper(
            func_or_class, span_name, record_exception, attributes, tracer
        )
    else:
        wrapper = _create_sync_wrapper(
            func_or_class, span_name, record_exception, attributes, tracer
        )

    wrapper.__signature__ = inspect.signature(func_or_class)  # type: ignore[attr-defined]
    return wrapper


def _create_sync_wrapper(
    func: Callable,
    span_name: str,
    record_exception: bool,  # noqa: FBT001
    attributes: dict[str, str] | None,
    tracer: Tracer,
) -> Callable:
    """Create synchronous span wrapper."""

    @wraps(func)
    def wrap_with_span_sync(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        name = span_name or TracingDecoratorOptions.naming_scheme(func)
        with tracer.start_as_current_span(
            name, record_exception=record_exception
        ) as span:
            _set_span_attributes(span, func, attributes)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                _set_error_attributes(span, e)
                raise
            else:
                span.set_attribute("operation.success", True)  # noqa: FBT003
                return result

    return wrap_with_span_sync


def _create_async_wrapper(
    func: Callable,
    span_name: str,
    record_exception: bool,  # noqa: FBT001
    attributes: dict[str, str] | None,
    tracer: Tracer,
) -> Callable:
    """Create asynchronous span wrapper."""

    @wraps(func)
    async def wrap_with_span_async(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        name = span_name or TracingDecoratorOptions.naming_scheme(func)
        with tracer.start_as_current_span(
            name, record_exception=record_exception
        ) as span:
            _set_span_attributes(span, func, attributes)
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                _set_error_attributes(span, e)
                raise
            else:
                span.set_attribute("operation.success", True)  # noqa: FBT003
                return result

    return wrap_with_span_async


def _set_span_attributes(
    span: Any,  # noqa: ANN401
    func: Callable,
    attributes: dict[str, str] | None,
) -> None:
    """Set all span attributes including semantic, default, and custom."""
    # Semantic attributes using modern conventions
    span.set_attribute("code.namespace", func.__module__)
    span.set_attribute("code.function", func.__qualname__)
    span.set_attribute("code.filepath", func.__code__.co_filename)
    span.set_attribute("code.lineno", func.__code__.co_firstlineno)

    # Default and custom attributes
    _set_attributes_dict(span, TracingDecoratorOptions.default_attributes)
    _set_attributes_dict(span, attributes)

    # Request context
    context = get_request_context()
    for key, value in context.items():
        if not key.startswith("http."):  # Avoid duplicating HTTP attributes
            span.set_attribute(f"request.{key}", value)


def _set_attributes_dict(span: Any, attributes_dict: dict[str, str] | None) -> None:  # noqa: ANN401
    """Set attributes from a dictionary."""
    if attributes_dict:
        for key, value in attributes_dict.items():
            span.set_attribute(key, value)


def _set_error_attributes(span: Any, exception: Exception) -> None:  # noqa: ANN401
    """Set error-related attributes on span."""
    span.set_attribute("operation.success", False)  # noqa: FBT003
    span.set_attribute("error.type", type(exception).__name__)
    span.set_attribute("error.message", str(exception))


def instrument(
    _func_or_class: Callable | None = None,
    *,
    span_name: str = "",
    record_exception: bool = True,
    attributes: dict[str, str] | None = None,
    existing_tracer: Tracer | None = None,
    ignore: bool = False,
) -> Callable:
    """A decorator to instrument a class or function with an OTEL tracing span.

    Original implementation adapted from opentelemetry-instrumentation-digma.
    Reference: https://github.com/digma-ai/opentelemetry-instrumentation-digma

    Args:
        _func_or_class: The function or class to instrument, automatically assigned
        span_name: Specify the span name explicitly, rather than use the naming convention
        record_exception: Sets whether exceptions and stacktrace are recorded automatically
        attributes: A dictionary of span attributes to add to the span
        existing_tracer: Use a specific tracer instead of creating one
        ignore: Do not instrument this function

    Returns:
        The decorator function
    """
    # Check if this is a class decorator
    if inspect.isclass(_func_or_class):
        return _decorate_class(
            _func_or_class, record_exception, attributes, existing_tracer
        )

    def span_decorator(func_or_class: Callable) -> Callable:
        if inspect.isclass(func_or_class):
            return _decorate_class(
                func_or_class, record_exception, attributes, existing_tracer
            )

        if ignore:
            return func_or_class

        return _create_span_wrapper(
            func_or_class, span_name, record_exception, attributes, existing_tracer
        )

    if _func_or_class is None:
        return span_decorator
    return span_decorator(_func_or_class)
