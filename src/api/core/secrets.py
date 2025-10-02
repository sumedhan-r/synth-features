"""Platform-agnostic secrets management system."""

import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, cast

from src.api.core.logger import get_logger

if TYPE_CHECKING:
    from azure.keyvault.secrets.aio import SecretClient
    from google.cloud.secretmanager import SecretManagerServiceClient

logger = get_logger(__name__)


class SecretManager(ABC):
    """Abstract base class for secret managers."""

    @abstractmethod
    async def get_secret(self, secret_name: str) -> str | None:
        """Retrieve a secret by name."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this secret manager is available in the current environment."""
        pass


class LocalSecretManager(SecretManager):
    """Local environment variable-based secret manager for development."""

    async def get_secret(self, secret_name: str) -> str | None:
        """Get secret from environment variables."""
        value = os.getenv(secret_name)
        if value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment variables")
        return value

    def is_available(self) -> bool:
        """Local secrets are always available."""
        return True


class AzureKeyVaultManager(SecretManager):
    """Azure Key Vault secret manager."""

    def __init__(self, vault_url: str | None = None):
        self.vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        self._client: SecretClient | None = None

    async def get_secret(self, secret_name: str) -> str | None:
        """Get secret from Azure Key Vault."""
        if not self.is_available():
            return None

        try:
            from azure.keyvault.secrets.aio import SecretClient
            from azure.identity.aio import DefaultAzureCredential

            if not self._client and self.vault_url:
                credential = DefaultAzureCredential()
                self._client = SecretClient(
                    vault_url=self.vault_url, credential=credential
                )

            if self._client:
                secret = await self._client.get_secret(secret_name)
                logger.debug(f"Retrieved secret '{secret_name}' from Azure Key Vault")
                return secret.value
            return None

        except ImportError:
            logger.warning("Azure Key Vault dependencies not installed")
            return None
        except Exception as e:
            logger.error(
                f"Failed to retrieve secret '{secret_name}' from Azure Key Vault: {e}"
            )
            return None

    def is_available(self) -> bool:
        """Check if Azure Key Vault is configured and available."""
        return bool(self.vault_url)


class AWSSecretsManager(SecretManager):
    """AWS Secrets Manager secret manager."""

    def __init__(self, region_name: str | None = None):
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._client: Any = None

    async def get_secret(self, secret_name: str) -> str | None:
        """Get secret from AWS Secrets Manager."""
        if not self.is_available():
            return None

        try:
            import boto3  # type: ignore[import-untyped]
            from botocore.exceptions import ClientError  # type: ignore[import-untyped]

            if not self._client:
                self._client = boto3.client(
                    "secretsmanager", region_name=self.region_name
                )

            if self._client:
                response = self._client.get_secret_value(SecretId=secret_name)
                logger.debug(
                    f"Retrieved secret '{secret_name}' from AWS Secrets Manager"
                )
                return response.get("SecretString")
            return None

        except ImportError:
            logger.warning("AWS SDK (boto3) not installed")
            return None
        except ClientError as e:
            logger.error(
                f"Failed to retrieve secret '{secret_name}' from AWS Secrets Manager: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving secret '{secret_name}' from AWS: {e}"
            )
            return None

    def is_available(self) -> bool:
        """Check if AWS region is configured."""
        return bool(self.region_name)


class GCPSecretManager(SecretManager):
    """Google Cloud Secret Manager secret manager."""

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self._client: SecretManagerServiceClient | None = None

    async def get_secret(self, secret_name: str) -> str | None:
        """Get secret from Google Cloud Secret Manager."""
        if not self.is_available():
            return None

        try:
            from google.cloud import secretmanager

            if not self._client:
                self._client = secretmanager.SecretManagerServiceClient()

            if self._client:
                name = (
                    f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                )
                response = self._client.access_secret_version(request={"name": name})
                logger.debug(
                    f"Retrieved secret '{secret_name}' from GCP Secret Manager"
                )
                return response.payload.data.decode("UTF-8")
            return None

        except ImportError:
            logger.warning("Google Cloud SDK not installed")
            return None
        except Exception as e:
            logger.error(
                f"Failed to retrieve secret '{secret_name}' from GCP Secret Manager: {e}"
            )
            return None

    def is_available(self) -> bool:
        """Check if GCP project is configured."""
        return bool(self.project_id)


class SecretManagerFactory:
    """Factory for creating appropriate secret managers based on configuration."""

    @staticmethod
    def create_managers(
        platform: str | None = None,
        azure_vault_url: str | None = None,
        aws_region: str | None = None,
        gcp_project_id: str | None = None,
    ) -> list[SecretManager]:
        """Create secret managers based on platform configuration."""
        managers: list[SecretManager] = []

        # If platform is specified, create only that manager
        if platform:
            platform_lower = platform.lower()
            if platform_lower == "azure" and azure_vault_url:
                managers.append(AzureKeyVaultManager(vault_url=azure_vault_url))
            elif platform_lower == "aws" and aws_region:
                managers.append(AWSSecretsManager(region_name=aws_region))
            elif platform_lower == "gcp" and gcp_project_id:
                managers.append(GCPSecretManager(project_id=gcp_project_id))
            elif platform_lower == "local":
                managers.append(LocalSecretManager())
            else:
                logger.warning(f"Unknown or misconfigured platform: {platform}")
        else:
            # Auto-detect based on available configuration
            if azure_vault_url:
                managers.append(AzureKeyVaultManager(vault_url=azure_vault_url))
            if aws_region:
                managers.append(AWSSecretsManager(region_name=aws_region))
            if gcp_project_id:
                managers.append(GCPSecretManager(project_id=gcp_project_id))

        # Always add local manager as fallback
        managers.append(LocalSecretManager())

        return managers


class UnifiedSecretManager:
    """Unified secret manager that tries multiple backends."""

    def __init__(
        self,
        managers: list[SecretManager] | None = None,
        platform: str | None = None,
        azure_vault_url: str | None = None,
        aws_region: str | None = None,
        gcp_project_id: str | None = None,
    ):
        if managers:
            self.managers = managers
        else:
            self.managers = SecretManagerFactory.create_managers(
                platform=platform,
                azure_vault_url=azure_vault_url,
                aws_region=aws_region,
                gcp_project_id=gcp_project_id,
            )

        manager_types = [type(m).__name__ for m in self.managers]
        logger.info(f"Initialized secret manager with backends: {manager_types}")

    async def get_secret(self, secret_reference: str) -> str | None:
        """
        Get secret from the first available manager.

        Secret reference format: <manager_type>:<secret_name> or just <secret_name>
        Examples:
        - "azure_kv:api-key" - specifically from Azure Key Vault
        - "aws:database-password" - specifically from AWS Secrets Manager
        - "gcp:service-account-key" - specifically from GCP Secret Manager
        - "api-key" - try all managers in order
        """
        if ":" in secret_reference:
            manager_type, secret_name = secret_reference.split(":", 1)
            return await self._get_secret_from_specific_manager(
                manager_type, secret_name
            )
        else:
            return await self._get_secret_from_any_manager(secret_reference)

    async def _get_secret_from_specific_manager(
        self, manager_type: str, secret_name: str
    ) -> str | None:
        """Get secret from a specific manager type."""
        manager_map = {
            "azure_kv": AzureKeyVaultManager,
            "aws": AWSSecretsManager,
            "gcp": GCPSecretManager,
            "local": LocalSecretManager,
        }

        manager_class = manager_map.get(manager_type)
        if not manager_class:
            logger.error(f"Unknown secret manager type: {manager_type}")
            return None

        for manager in self.managers:
            if isinstance(manager, manager_class):
                return await manager.get_secret(secret_name)

        logger.warning(f"Secret manager '{manager_type}' not available")
        return None

    async def _get_secret_from_any_manager(self, secret_name: str) -> str | None:
        """Try to get secret from any available manager."""
        for manager in self.managers:
            try:
                value = await manager.get_secret(secret_name)
                if value:
                    return value
            except Exception as e:
                logger.warning(
                    f"Failed to get secret from {type(manager).__name__}: {e}"
                )
                continue

        logger.warning(f"Could not retrieve secret '{secret_name}' from any manager")
        return None


_global_secret_manager: UnifiedSecretManager | None = None


def initialize_secret_manager(
    platform: str | None = None,
    azure_vault_url: str | None = None,
    aws_region: str | None = None,
    gcp_project_id: str | None = None,
) -> None:
    """Initialize the global secret manager with platform configuration."""
    global _global_secret_manager
    _global_secret_manager = UnifiedSecretManager(
        platform=platform,
        azure_vault_url=azure_vault_url,
        aws_region=aws_region,
        gcp_project_id=gcp_project_id,
    )


def get_secret_manager() -> UnifiedSecretManager:
    """Get the global secret manager instance."""
    global _global_secret_manager
    if _global_secret_manager is None:
        # Fallback to environment variables if not initialized through config
        platform = os.getenv("DEPLOYMENT_PLATFORM")
        azure_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        aws_region = os.getenv("AWS_DEFAULT_REGION")
        gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        initialize_secret_manager(
            platform=platform,
            azure_vault_url=azure_vault_url,
            aws_region=aws_region,
            gcp_project_id=gcp_project_id,
        )

    # initialize_secret_manager always sets _global_secret_manager
    return cast(UnifiedSecretManager, _global_secret_manager)


async def get_secret(secret_reference: str) -> str | None:
    """Convenience function to get a secret."""
    manager = get_secret_manager()
    return await manager.get_secret(secret_reference)
