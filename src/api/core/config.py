"""Module to manage the configuration of this project."""

# mypy: disable_error_code="call-arg"
import os
from functools import cache

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from src.api.core.logger import get_logger

logger = get_logger(__name__)

ENV = os.getenv("ENV", "LOCAL")
logger.info(f"Setting up for {ENV} environment")
CONFIG_DIR = "configs"
CONFIG_YAML_DIR = f"{CONFIG_DIR}/{ENV.lower()}.config.yaml"
global_azure_vault_url: str | None = None  # To suppress mypy


# def get_secret(secret_reference: str, azure_vault_url: str | None = None) -> str | None:
#     """Retrieves a secret from the secret manager.

#         The pattern of the secret_reference is <secret_source>:<secret_name>.
#         For Azure Keyvault the <secret_source> is azure_kv. If there is no
#         <secret_source> passed, the function will return an error.

#         To add new secret source, update the match condition of this function
#         to match the new source name.

#     Args:
#         secret_reference (str): The value following the pattern
#             <secret_source>:<secret_name> (e.g. azure_kv:<secret_name>).
#         azure_vault_url (Optional[str]): Azure Keyvault URL. If provided,
#             this will be used instead of the global_azure_vault_url.

#     Returns:
#         str: The secret value retrieved from the secrets source.

#     Global Variables:
#         global_azure_vault_url (str): Azure Keyvault URL. Set when we initialize the
#             Settings class.
#     """
#     match secret_reference.split(":"):
#         case ["azure_kv", secret_name]:
#             effective_vault_url = azure_vault_url or global_azure_vault_url
#             if effective_vault_url is None:
#                 error_message = (
#                     "Azure vault_url is None. Please ensure the vault_url "
#                     "is set to retrieve secrets from Azure."
#                 )
#                 logger.error(error_message)
#                 raise ValueError(error_message)
#             secrets_manager = AzureSecretsManager(vault_url=effective_vault_url)
#             return secrets_manager.get_secret(secret_name=secret_name)
#         case _:
#             error_message = (
#                 "Please use a secret source (e.g. azure_kv) to refer to a secret value."
#             )
#             logger.error(error_message)
#             raise ValueError(error_message)


class GuitarConfig(BaseModel):
    """Config for guitar string frequencies."""

    low_e: float
    a: float
    d: float
    g: float
    b: float
    high_e: float


class Config(BaseSettings):
    """Master config that combines all the settings to one object."""

    guitar: GuitarConfig
    model_config = SettingsConfigDict(yaml_file=CONFIG_YAML_DIR, extra="ignore")

    # @model_validator(mode="before")
    # @classmethod
    # def set_vault_url(cls: type["Config"], values: dict) -> dict:
    #     """Sets the vault_url to a global variable so it can be used in get_secret."""
    #     global global_azure_vault_url  # noqa: PLW0603
    #     global_azure_vault_url = values.get("azure_keyvault_url")
    #     return values

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
    """
    return Config()
