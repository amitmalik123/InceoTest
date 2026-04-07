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
        self._mail_config = self._load_mail_config()
        self._queries = self._load_queries()

    def get_vault_connection_string(self, secret_name: str) -> str | None:
        """Fetch a connection string from environment variable.

        Resolution:
        1. Pipeline: AzureKeyVault@2 fetches secrets → env vars.
        2. Local: same env vars set in .env file.

        Args:
            secret_name: Secret name (e.g. 'crm-db-connection-string').
                         Converted to env var: CRM_DB_CONNECTION_STRING.

        Returns:
            The connection string value, or None if unavailable.
        """
        env_var = secret_name.upper().replace("-", "_")
        value = os.getenv(env_var)
        if value:
            self.logger.info(f"Connection string resolved from env var: {env_var}")
        return value

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

    def _load_mail_config(self) -> dict:
        """
        Load mail configuration from mail_config.properties file.
        
        Returns:
            dict: Mail configuration with keys like outlook.email, outlook.password, etc.
        """
        mail_config_path = Path(__file__).parent / "mail_config.properties"
        mail_config = {}
        
        if not mail_config_path.exists():
            self.logger.warning(f"Mail config file not found: {mail_config_path}")
            return mail_config
        
        try:
            with open(mail_config_path, "r") as file:
                for line in file:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                    # Parse key=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        mail_config[key.strip()] = value.strip()
            self.logger.debug(f"Loaded mail config from {mail_config_path}")
        except Exception as e:
            self.logger.error(f"Error loading mail config: {e}")
        
        return mail_config

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
    def screenshot_each_step(self):
        """Check if screenshots should be taken after each BDD step."""
        return self.config.get("test", {}).get("screenshot_each_step", False)

    @property
    def api_auth_token(self):
        """Get API authorization token (env var → YAML fallback)."""
        return os.getenv(f"{self.env.upper()}_API_AUTH_TOKEN") or os.getenv("API_AUTH_TOKEN") or self.config.get("api", {}).get("auth_token", "")

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
        """
        Get Outlook email address.
        
        Priority:
        1. mail_config.properties (outlook.email)
        2. environment variable (OUTLOOK_EMAIL)
        3. YAML config (outlook.email)
        
        Returns:
            Outlook email address (encrypted in properties file, decrypted via crypto_utils)
        """
        # Try mail_config.properties first
        from utils.crypto_utils import decrypt_value
        
        mail_email = self._mail_config.get("outlook.email", "")
        if mail_email:
            try:
                return decrypt_value(mail_email)
            except Exception as e:
                self.logger.warning(f"Error decrypting outlook email from mail_config.properties: {e}")
        
        # Fall back to environment variable
        env_email = os.getenv("OUTLOOK_EMAIL", "")
        if env_email:
            return env_email
        
        # Fall back to YAML (for backward compatibility)
        return self.config.get("outlook", {}).get("email", "")

    @property
    def outlook_password(self):
        """
        Get Outlook password / app-password.
        
        Priority:
        1. mail_config.properties (outlook.password)
        2. environment variable (OUTLOOK_PASSWORD)
        3. Key Vault secret (outlook-password)
        4. YAML config (outlook.password)
        
        Returns:
            Outlook password or App Password (encrypted in properties file, decrypted via crypto_utils)
        """
        # Try mail_config.properties first
        from utils.crypto_utils import decrypt_value
        
        mail_password = self._mail_config.get("outlook.password", "")
        if mail_password:
            try:
                return decrypt_value(mail_password)
            except Exception as e:
                self.logger.warning(f"Error decrypting outlook password from mail_config.properties: {e}")
        
        # Fall back to environment variable
        env_password = os.getenv("OUTLOOK_PASSWORD", "")
        if env_password:
            return env_password
        
        # Fall back to Key Vault + YAML (for backward compatibility)
        yaml_val = self.config.get("outlook", {}).get("password", "")
        vault_password = self._vault_or_yaml("outlook-password", yaml_val)
        if vault_password:
            return vault_password
        
        return ""

    @property
    def outlook_imap_server(self):
        """
        Get Outlook IMAP server.
        
        Priority:
        1. mail_config.properties (outlook.imap_server)
        2. environment variable (OUTLOOK_IMAP_SERVER)
        3. YAML config (outlook.imap_server)
        4. Default: outlook.office365.com
        """
        # Try mail_config.properties first
        mail_server = self._mail_config.get("outlook.imap_server", "")
        if mail_server:
            return mail_server
        
        # Try environment variable
        env_server = os.getenv("OUTLOOK_IMAP_SERVER", "")
        if env_server:
            return env_server
        
        # Fall back to YAML
        yaml_server = self.config.get("outlook", {}).get("imap_server", "")
        if yaml_server:
            return yaml_server
        
        # Default
        return "outlook.office365.com"

    @property
    def outlook_imap_port(self):
        """
        Get Outlook IMAP port.
        
        Priority:
        1. mail_config.properties (outlook.imap_port)
        2. environment variable (OUTLOOK_IMAP_PORT)
        3. YAML config (outlook.imap_port)
        4. Default: 993
        """
        # Try mail_config.properties first
        mail_port = self._mail_config.get("outlook.imap_port", "")
        if mail_port:
            try:
                return int(mail_port)
            except ValueError:
                self.logger.warning(f"Invalid outlook.imap_port in mail_config.properties: {mail_port}")
        
        # Try environment variable
        env_port = os.getenv("OUTLOOK_IMAP_PORT", "")
        if env_port:
            try:
                return int(env_port)
            except ValueError:
                self.logger.warning(f"Invalid OUTLOOK_IMAP_PORT environment variable: {env_port}")
        
        # Fall back to YAML
        yaml_port = self.config.get("outlook", {}).get("imap_port")
        if yaml_port:
            return yaml_port
        
        # Default
        return 993

    @property
    def secret_key(self):
        """Get encryption secret key (YAML → env-var fallback).
        
        Used to decrypt sensitive credentials like Outlook email/password.
        Should be a 16 or 32-byte encryption key.
        """
        yaml_val = self.config.get("secret_key", "")
        return yaml_val or os.getenv("ENCRYPTION_SECRET_KEY", "")


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
