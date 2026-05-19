"""
Settings module to load and provide access to configuration from YAML files.

Usage:
    from config.settings import get_settings
    settings = get_settings()          # lazily created, cached singleton

    # or (backward-compatible, triggers __getattr__ on first access):
    from config.settings import settings
"""

import os
from pathlib import Path

import yaml  # type: ignore
from dotenv import load_dotenv

from utils.azure_key_vault import AzureKeyVaultClient
from utils.logger import setup_logger

# Load .env file from project root (if present).
# Real env-vars (e.g. from CI/CD) take precedence; .env is never committed.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    """Load and provide access to configuration settings."""

    def __init__(self, env: str):
        """
        Initialize settings by loading configuration from YAML file.

        Args:
            env: Environment name (test11, test12, silo, prod, qa, etc.).
                 Always use ``get_settings()`` instead of calling this directly.
        """
        self.env = env
        self.logger = setup_logger(__name__)
        self.config_path = Path(__file__).parent / f"env.{env}.yaml"
        self.config = self._load_config()
        self._queries = self._load_queries()
        self._vault = AzureKeyVaultClient()

    def _vault_or_yaml(self, vault_key: str, yaml_value):
        """Try Key Vault first, fall back to YAML value."""
        secret = self._vault.get_secret(f"{self.env}-{vault_key}")
        if secret is not None:
            return secret
        return yaml_value

    def get_vault_connection_string(self, secret_name: str) -> str | None:
        """Fetch a connection string from environment variable or Key Vault.

        The framework's preferred approach is **env-var first**:
        1. The Azure DevOps pipeline ``AzureKeyVault@2`` task fetches secrets
           and maps them to env vars (e.g. ``CRM_DB_CONNECTION_STRING``).
        2. For local dev, the same env vars are set in the ``.env`` file.
        3. As a last resort, falls back to the Python Key Vault client.

        Args:
            secret_name: Key Vault secret name (e.g. 'crm-db-connection-string').
                         Also used to derive an env-var name by uppercasing and
                         replacing hyphens with underscores.

        Returns:
            The connection string value, or None if unavailable.
        """
        # 1. Try env var derived from secret name: crm-db-connection-string → CRM_DB_CONNECTION_STRING
        env_var = secret_name.upper().replace("-", "_")
        value = os.getenv(env_var)
        if value:
            self.logger.info(f"Connection string resolved from env var: {env_var}")
            return value

        # 2. Fallback: try Key Vault directly (for backward compatibility)
        return self._vault.get_secret(secret_name)

    def get_connection_string_from_env(self, env_var: str) -> str | None:
        """Read a connection string directly from an environment variable.

        This is the cleanest approach when the pipeline or ``.env`` file
        sets a specific env-var name.

        Args:
            env_var: Environment variable name, e.g. 'CRM_DB_CONNECTION_STRING'.

        Returns:
            The connection string value, or None.
        """
        value = os.getenv(env_var)
        if value:
            self.logger.info(f"Connection string resolved from env var: {env_var}")
        return value

    def get_vault_db_config(self, alias: str) -> dict:
        """Get a database configuration by its alias from YAML.

        Reads the ``database.vault_databases.<alias>`` section from the
        environment YAML file::

            vault_databases:
              crm:
                env_var: CRM_DB_CONNECTION_STRING
                secret_name: crm-db-connection-string
              billing:
                env_var: AM_BILLING_CONNECTION_STRING
                secret_name: am-billing-connection-string

        The pipeline's ``AzureKeyVault@2`` task fetches the Key Vault secret
        and injects it as the specified ``env_var``. Python never calls Key
        Vault directly — it just reads ``os.getenv(env_var)``.

        Args:
            alias: Short alias for the database (e.g. 'crm', 'billing').

        Returns:
            dict with ``env_var``, ``secret_name``, and optionally ``driver``.

        Raises:
            ValueError: If the alias is not defined in the YAML.
        """
        vault_dbs = self.config.get("database", {}).get("vault_databases", {})
        if alias not in vault_dbs:
            available = list(vault_dbs.keys())
            raise ValueError(
                f"Vault database alias '{alias}' not found in config. " f"Available: {available}"
            )
        return vault_dbs[alias]

    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)

    @property
    def base_url(self):
        """Get base URL for the application."""
        return self.config["application"]["base_url"]

    @property
    def login_url(self):
        """Get login URL for the application."""
        return self.config["application"].get("login_url", self.base_url)

    @property
    def timeout(self):
        """Get default timeout in milliseconds."""
        return self.config["application"]["timeout"]

    @property
    def browser_type(self):
        """Get browser type (chromium, firefox, webkit)."""
        return self.config["browser"]["browser_type"]

    @property
    def headless(self):
        """Check if browser should run in headless mode."""
        return self.config["browser"]["headless"]

    @property
    def viewport(self):
        """Get viewport dimensions."""
        return self.config["browser"]["viewport"]

    @property
    def browser_args(self):
        """Get browser launch arguments."""
        return self.config["browser"].get("args", [])

    @property
    def test_data_csv(self):
        """Get path to test data CSV file."""
        base_path = Path(__file__).parent.parent
        return base_path / self.config["data"]["test_data_csv"]

    @property
    def test_data_excel(self):
        """Get path to test data Excel file."""
        excel_path = self.config.get("data", {}).get("test_data_excel")
        if not excel_path:
            return None
        base_path = Path(__file__).parent.parent
        return base_path / excel_path

    @property
    def allure_results_dir(self):
        """Get Allure results directory."""
        base_path = Path(__file__).parent.parent
        return base_path / self.config["reporting"]["allure_results"]

    @property
    def screenshot_each_step(self):
        """Check if screenshots should be taken after each BDD step."""
        return self.config.get("test", {}).get("screenshot_each_step", False)

    @property
    def screenshot_on_failure(self):
        """Check if screenshots should be taken on test failure."""
        return self.config.get("test", {}).get("screenshot_on_failure", True)

    @property
    def api_auth_token(self):
        """Get API authorization token (Key Vault → YAML fallback)."""
        yaml_val = self.config.get("api", {}).get("auth_token", "")
        return self._vault_or_yaml("api-auth-token", yaml_val)

    @property
    def database_config(self):
        """Get database configuration."""
        return self.config.get("database", {})

    @property
    def vault_databases(self) -> dict:
        """Get all configured vault database aliases."""
        return self.config.get("database", {}).get("vault_databases", {})

    def get_app_config(self, app_name: str) -> dict:
        """
        Get configuration for a specific application.

        Args:
            app_name: Application name (ewm, crm, etc.)

        Returns:
            dict: Application configuration of the specified app.

        Raises:
            ValueError: If application not found in config
        """
        apps = self.config.get("applications", {})
        if app_name not in apps:
            available = list(apps.keys())
            raise ValueError(
                f"Application '{app_name}' not found in config. Available: {available}"
            )
        return apps[app_name]

    def get_available_apps(self) -> list:
        """Get list of all configured applications."""
        return list(self.config.get("applications", {}).keys())

    def _load_queries(self):
        """Load SQL queries from queries/sql_queries.yaml once at init time."""
        queries_path = Path(__file__).parent.parent / "queries" / "sql_queries.yaml"
        if not queries_path.exists():
            self.logger.warning(f"Queries file not found: {queries_path}")
            return {}

        with open(queries_path, "r") as file:
            return yaml.safe_load(file) or {}

    @property
    def database_queries(self):
        """Get predefined database queries (loaded once from queries/sql_queries.yaml)."""
        return self._queries

    # --- Outlook Email (IMAP) ---

    @property
    def outlook_email(self):
        """Get Outlook email address (YAML → env-var fallback)."""
        return self.config.get("outlook", {}).get("email", "") or os.getenv("OUTLOOK_EMAIL", "")

    @property
    def outlook_password(self):
        """Get Outlook password / app-password (Key Vault → YAML → env-var fallback)."""
        yaml_val = self.config.get("outlook", {}).get("password", "")
        return self._vault_or_yaml("outlook-password", yaml_val) or os.getenv(
            "OUTLOOK_PASSWORD", ""
        )

    @property
    def outlook_imap_server(self):
        """Get Outlook IMAP server. Defaults to outlook.office365.com."""
        return self.config.get("outlook", {}).get("imap_server", "outlook.office365.com")

    @property
    def outlook_imap_port(self):
        """Get Outlook IMAP port. Defaults to 993."""
        return self.config.get("outlook", {}).get("imap_port", 993)


# ---------------------------------------------------------------------------
# Lazy singleton – environment resolved ONCE from TEST_ENV env-var
# ---------------------------------------------------------------------------
_settings_instance = None


def get_settings() -> Settings:
    """Return the lazily-initialised, environment-aware Settings singleton.

    The environment is read from the ``TEST_ENV`` env-var which should be
    set in the project-root ``.env`` file (or exported by CI/CD).
    The instance is created on first call and cached for the process lifetime.

    Raises:
        RuntimeError: If ``TEST_ENV`` is not set anywhere.
    """
    global _settings_instance
    if _settings_instance is None:
        env = os.getenv("TEST_ENV")
        if not env:
            raise RuntimeError(
                "TEST_ENV is not set. "
                "Add TEST_ENV=<env-name> to the .env file in the project root, "
                "or export it as an environment variable."
            )
        _settings_instance = Settings(env=env)
    return _settings_instance


def __getattr__(name: str):
    """PEP 562 – allow ``from config.settings import settings``."""
    if name == "settings":
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
