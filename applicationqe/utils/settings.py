
import os
from pathlib import Path
import yaml  # type: ignore
from utils.logger import setup_logger

class Settings:
    """Load and provide access to configuration settings."""

    def __init__(self, env="test11"):
        
        self.env = env
        self.logger = setup_logger(__name__)
        self.config_path = Path(__file__).parent.parent / "config" / "stp" / "stp_moneyin_moneyout" / f"env.{env}.yaml"
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from env YAML and merge with .secretCred.yaml."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        # Load base environment config
        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file) or {}
        
        # Load and merge .secretCred.yaml
        secret_file = self.config_path.parent / ".secretCred.yaml"
        if secret_file.exists():
            with open(secret_file, "r") as file:
                secrets = yaml.safe_load(file)
                if secrets:
                    self.logger.info(f"Loaded secrets with keys: {list(secrets.keys())}")
                    if 'database' in secrets and 'azure' in secrets.get('database', {}):
                        self.logger.info(f"Azure DB config is set")
                    # Merge secrets into config (secrets take precedence)
                    for key, value in secrets.items():
                        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                            config[key].update(value)
                        else:
                            config[key] = value
        
        return config

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
        
        env_token = os.environ.get("API_AUTH_TOKEN", "")
        # Skip if it's an unexpanded ADO variable expression like $(secret-name)
        if env_token and not (env_token.startswith("$(") and env_token.endswith(")")):
            return env_token
        return self.config.get("api", {}).get("auth_token", "")

    @property
    def database_config(self):
        """Get database configuration."""
        return self.config.get("database", {})

    @property
    def azure_sql_server(self):
        """Get Azure SQL server name."""
        return self.config.get("database", {}).get("azure_sql", {}).get("server")

    @property
    def azure_sql_database(self):
        """Get Azure SQL database name."""
        return self.config.get("database", {}).get("azure_sql", {}).get("database")

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

    @property
    def azure_sql_username(self):
        """Get Azure SQL username."""
        return self.config.get("database", {}).get("azure_sql", {}).get("username")

    @property
    def azure_sql_password(self):
        """Get Azure SQL password."""
        return self.config.get("database", {}).get("azure_sql", {}).get("password")

    @property
    def azure_sql_driver(self):
        """Get Azure SQL ODBC driver."""
        return (
            self.config.get("database", {})
            .get("azure_sql", {})
            .get("driver", "{ODBC Driver 17 for SQL Server}")
        )

    @property
    def azure_sql_authentication(self):
        """Get Azure SQL authentication method."""
        return self.config.get("database", {}).get("azure_sql", {}).get("authentication")

    @property
    def ewm_hostname(self):
        """Get EWM database hostname based on environment."""
        ewm_config = self.config.get("database", {}).get("ewm", {})
        env_lower = self.env.lower()
        
        if "test12" in env_lower or "t12" in env_lower:
            return ewm_config.get("hostname", "t12ewmdba")
        elif "test10" in env_lower or "t10" in env_lower:
            return ewm_config.get("hostname_t10", "t10ewmdba")
        else:
            return ewm_config.get("hostname_t11", "ewmdba.test11.ncus.assetmark.net")
    
    @property
    def ewm_username(self):
        """Get EWM database username."""
        return self.config.get("database", {}).get("ewm", {}).get("username", "DevUser")
    
    @property
    def ewm_password(self):
        """Get EWM database password."""
        return self.config.get("database", {}).get("ewm", {}).get("password", "9SfzgS7Q4k")
    
    @property
    def ewm_database(self):
        """Get EWM database name (AM_Billing for Account table)."""
        return "AM_Billing"

    @property
    def sql_server_config(self):
        """Get SQL Server configuration."""
        return self.config.get("database", {}).get("sql_server", {})

    @property
    def sql_server_host(self):
        """Get SQL Server host name."""
        return self.config.get("database", {}).get("sql_server", {}).get("server")

    @property
    def sql_server_database(self):
        """Get SQL Server database name."""
        return self.config.get("database", {}).get("sql_server", {}).get("database")

    @property
    def sql_server_username(self):
        """Get SQL Server username."""
        return self.config.get("database", {}).get("sql_server", {}).get("username")

    @property
    def sql_server_password(self):
        """Get SQL Server password."""
        return self.config.get("database", {}).get("sql_server", {}).get("password")

    @property
    def sql_server_driver(self):
        """Get SQL Server ODBC driver."""
        return (
            self.config.get("database", {})
            .get("sql_server", {})
            .get("driver", "{ODBC Driver 17 for SQL Server}")
        )

    @property
    def database_queries(self):
        """
        Get predefined database queries from queries/sql_queries.yaml.
        This is a centralized location for all SQL queries shared across environments.
        """
        queries_path = Path(__file__).parent.parent / "queries" / "stp" / "stp_moneyin_moneyout" / "sql_queries.yaml"
        if not queries_path.exists():
            self.logger.warning(f"Queries file not found: {queries_path}")
            return {}

        with open(queries_path, "r") as file:
            return yaml.safe_load(file)

    def get_role_url(self, role: str) -> str:
        """
        Get URL for a specific role from role_urls configuration.
        
        Args:
            role: Role name (e.g., 'manage_bene_test')
        
        Returns:
            str: URL for the role
        
        Raises:
            ValueError: If role not found in configuration
        """
        role_urls = self.config.get("role_urls", {})
        if role not in role_urls:
            available = list(role_urls.keys())
            raise ValueError(
                f"Role '{role}' not found in role_urls config. Available: {available}"
            )
        return role_urls[role].get("base_url")


# Singleton instance ΓÇö TEST_ENV must be explicitly set (no default)
_env = os.environ.get("TEST_ENV")
if not _env:
    raise RuntimeError(
        "TEST_ENV environment variable is not set. "
        "Run: set TEST_ENV=<env>  (test11 / test12 / silo / qa / prod)"
    )
settings = Settings(env=_env)
