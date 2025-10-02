from collections.abc import Callable
from typing import ClassVar


class TracingDecoratorOptions:
    """Configuration options for tracing decorators.

    Original implementation adapted from opentelemetry-instrumentation-digma.
    Reference: https://github.com/digma-ai/opentelemetry-instrumentation-digma
    """

    class NamingSchemes:
        @staticmethod
        def function_qualified_name(func: Callable) -> str:
            return func.__qualname__

        default_scheme = function_qualified_name

    naming_scheme: Callable[[Callable], str] = NamingSchemes.default_scheme
    default_attributes: ClassVar[dict[str, str]] = {}

    @staticmethod
    def set_naming_scheme(naming_scheme: Callable[[Callable], str]) -> None:
        TracingDecoratorOptions.naming_scheme = naming_scheme

    @staticmethod
    def set_default_attributes(attributes: dict[str, str] | None = None) -> None:
        if attributes:
            for att, value in attributes.items():
                TracingDecoratorOptions.default_attributes[att] = value
