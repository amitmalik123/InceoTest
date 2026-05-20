"""
Azure Key Vault Client

Provides secure secret retrieval from Azure Key Vault with:
- Lazy initialization (connects only when a secret is requested)
- In-memory caching (each secret fetched once per session)
- Graceful fallback when Key Vault is unavailable (local dev)

Secret naming convention:
    {environment}-{service}-{secret-type}
    e.g. test11-azure-sql-password, test11-api-auth-token

Required environment variables (set in .env or CI/CD):
    AZURE_KEY_VAULT_URL  – e.g. https://my-vault.vault.azure.net/

For CI/CD (service principal), also set:
    AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AzureKeyVaultClient:
    """
    Thread-safe, lazy-initialized Key Vault client with caching.

    Usage:
        vault = AzureKeyVaultClient()
        password = vault.get_secret("test11-azure-sql-password")

        # Batch fetch
        secrets = vault.get_secrets([
            "test11-azure-sql-username",
            "test11-azure-sql-password",
        ])
    """

    def __init__(self, vault_url: Optional[str] = None):
        """
        Args:
            vault_url: Key Vault URL. Falls back to AZURE_KEY_VAULT_URL env var.
        """
        self._vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL", "")
        self._client = None  # lazy
        self._cache: Dict[str, str] = {}
        self._available: Optional[bool] = None  # None = not checked yet

    # ------------------------------------------------------------------
    # Lazy initialisation
    # ------------------------------------------------------------------
    def _init_client(self):
        """Create the SecretClient on first use."""
        if self._client is not None:
            return

        if not self._vault_url:
            self._available = False
            logger.info("AZURE_KEY_VAULT_URL not set – Key Vault disabled (using YAML fallback)")
            return

        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            credential = DefaultAzureCredential()
            self._client = SecretClient(vault_url=self._vault_url, credential=credential)
            self._available = True
            logger.info(f"Key Vault client initialised: {self._vault_url}")
        except ImportError:
            self._available = False
            logger.warning(
                "azure-identity / azure-keyvault-secrets not installed. "
                "Install with: pip install azure-identity azure-keyvault-secrets"
            )
        except Exception as exc:
            self._available = False
            logger.warning(f"Key Vault initialisation failed: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def is_available(self) -> bool:
        """Check whether Key Vault is reachable (initialises on first call)."""
        if self._available is None:
            self._init_client()
        return bool(self._available)

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a single secret by name.

        Args:
            secret_name: Secret name in Key Vault (e.g. 'test11-azure-sql-password').
            default: Value returned when Key Vault is unavailable or the secret
                     does not exist.

        Returns:
            The secret value, or *default* if Key Vault is not available /
            the secret is missing.
        """
        # Return from cache if already fetched
        if secret_name in self._cache:
            return self._cache[secret_name]

        if not self.is_available:
            return default

        try:
            assert self._client is not None
            retrieved = self._client.get_secret(secret_name)
            value = retrieved.value
            self._cache[secret_name] = value
            logger.debug(f"Secret retrieved from Key Vault: {secret_name}")
            return value
        except Exception as exc:
            logger.warning(f"Failed to retrieve secret '{secret_name}': {exc}")
            return default

    def get_secrets(self, secret_names: List[str]) -> Dict[str, Optional[str]]:
        """
        Retrieve multiple secrets at once.

        Args:
            secret_names: List of secret names.

        Returns:
            Dict mapping each name to its value (or None if missing).
        """
        return {name: self.get_secret(name) for name in secret_names}

    def clear_cache(self) -> None:
        """Clear the in-memory secret cache."""
        self._cache.clear()
        logger.debug("Key Vault cache cleared")


# ---------------------------------------------------------------------------
# Module-level singleton & convenience function
# ---------------------------------------------------------------------------
_default_client: Optional[AzureKeyVaultClient] = None


def _get_default_client() -> AzureKeyVaultClient:
    global _default_client
    if _default_client is None:
        _default_client = AzureKeyVaultClient()
    return _default_client


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function – fetches a secret using the module-level client.

    Usage:
        from utils.azure_key_vault import get_secret
        password = get_secret("test11-azure-sql-password")
    """
    return _get_default_client().get_secret(secret_name, default)