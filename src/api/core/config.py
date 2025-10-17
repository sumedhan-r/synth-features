"""Module to manage the configuration of this project."""

# mypy: disable_error_code="call-arg"
import asyncio
import os
from functools import cache
from typing import Any

from pydantic import BaseModel, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from src.api.core.logger import get_logger
from src.api.core.secrets import get_secret, initialize_secret_manager

logger = get_logger(__name__)

ENV = os.getenv("ENV", "LOCAL")
logger.info(f"Setting up for {ENV} environment")
CONFIG_DIR = "configs"
CONFIG_YAML_DIR = f"{CONFIG_DIR}/{ENV.lower()}.config.yaml"


def get_secret_from_platform(value: Any) -> Any:
    """Resolve secret references using the platform-configured secret manager."""
    if not isinstance(value, str) or not value.startswith("secret:"):
        return value

    secret_ref = value.replace("secret:", "", 1)
    try:
        secret_value = asyncio.run(get_secret(secret_ref))
        return secret_value or value
    except Exception as e:
        logger.warning(f"Failed to resolve secret '{secret_ref}': {e}")
        return value


class StringInstrumentPreset(BaseModel):
    """Configuration for a string instrument preset."""

    tuning: list[str]
    vibration_seconds: float
    damping: float


class StringInstrumentsConfig(BaseModel):
    """Configuration for all string instrument presets."""

    ukulele: StringInstrumentPreset
    guitar: StringInstrumentPreset


class PlatformConfig(BaseModel):
    """Config for deployment platform services."""

    deployment_platform: str | None
    azure_vault_url: str | None
    azure_resource_group: str | None
    aws_region: str | None
    aws_account_id: str | None
    gcp_project_id: str | None
    gcp_region: str | None


class TracingConfig(BaseModel):
    """Config for distributed tracing - platform agnostic."""

    enabled: bool
    service_name: str
    service_version: str
    sampling_ratio: float
    sampling_type: str
    exporter_type: str
    exporter_endpoint: str | None
    exporter_headers: dict[str, str]
    resource_attributes: dict[str, str]

    # Resolve secrets in exporter_headers
    @field_validator("exporter_headers", mode="before")
    @classmethod
    def resolve_header_secrets(cls, v: dict[str, str]) -> dict[str, str]:
        """Resolve secret references in exporter headers."""
        if not isinstance(v, dict):
            return v
        return {key: get_secret_from_platform(value) for key, value in v.items()}


class Config(BaseSettings):
    """Master config that combines all the settings to one object."""

    string_instruments: StringInstrumentsConfig
    platform: PlatformConfig
    tracing: TracingConfig
    model_config = SettingsConfigDict(yaml_file=CONFIG_YAML_DIR, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def initialize_platform_services(cls, values: dict) -> dict:
        """Initialize platform-specific services before field validation."""
        if isinstance(values, dict) and "platform" in values:
            platform_config = values["platform"]
            if isinstance(platform_config, dict):
                initialize_secret_manager(
                    platform=platform_config.get("deployment_platform"),
                    azure_vault_url=platform_config.get("azure_vault_url"),
                    aws_region=platform_config.get("aws_region"),
                    gcp_project_id=platform_config.get("gcp_project_id"),
                )
        return values

    @classmethod
    def settings_customise_sources(
        cls: type["Config"],
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Pydantic customized settings to change the source to yaml.

        Allows user to override the yaml file by passing _yaml_file when
        initializing Config (e.g. config = Config(_yaml_file="some_config.yaml"))
        """
        model_yaml_path = settings_cls.model_config.get("yaml_file")
        init_kwargs = init_settings.init_kwargs  # type: ignore[attr-defined]
        init_yaml_path = init_kwargs.get("_yaml_file")
        settings_cls.model_config["yaml_file"] = (
            init_yaml_path if init_yaml_path else model_yaml_path
        )
        return (YamlConfigSettingsSource(settings_cls),)


@cache
def get_config() -> Config:
    """Initializes the config.

    This is done so that the config is not initialized every time the module is
    imported. By doing this, it is easier to mock the config in tests.
    Platform services are automatically initialized via model validator.
    """
    return Config()
