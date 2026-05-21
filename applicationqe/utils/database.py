"""
Database utility module for Azure SQL Database and SQL Server connections.
"""

import os
from typing import Optional

import pyodbc

from utils.logger import setup_logger
from utils.settings import Settings
from utils.retry_utils import RetryContext

# Global configuration - initialized once at module import
_env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=_env)
logger = setup_logger(__name__)


def _get_db_settings():
    """Get the centralized Settings singleton (lazy import to avoid circular deps)."""
    from config.settings import get_settings

    return get_settings()
# Safety constants
RESTRICTED_ENVS = ["prod", "production", "silo"]


def _is_running_in_pipeline() -> bool:
    """
    Detect whether the code is running inside an Azure DevOps pipeline.
    Azure DevOps always sets SYSTEM_TEAMFOUNDATIONCOLLECTIONURI for every job.
    Returns True if running in pipeline, False if running locally.
    """
    return bool(os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"))


def _parse_connection_string(conn_str: str) -> dict:
    """
    Parse an ADO.NET / ODBC-style connection string into a dict.

    Handles common key aliases:
      Server / Data Source           -> server
      Database / Initial Catalog     -> database
      User ID / UID / User           -> username
      Password / PWD                 -> password
      Authentication                 -> authentication
      Driver                         -> driver

    Args:
        conn_str: Connection string, e.g.
            "Server=host;Database=db;User ID=user;Password=pwd;Authentication=Active Directory Password;"

    Returns:
        dict with normalised keys: server, database, username, password, authentication, driver
    """
    KEY_MAP = {
        "server": "server",
        "data source": "server",
        "database": "database",
        "initial catalog": "database",
        "user id": "username",
        "uid": "username",
        "user": "username",
        "password": "password",
        "pwd": "password",
        "authentication": "authentication",
        "driver": "driver",
    }

    result: dict = {}
    for part in conn_str.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        raw_key, _, value = part.partition("=")
        normalised = KEY_MAP.get(raw_key.strip().lower())
        if normalised:
            result[normalised] = value.strip()

    return result


def _check_environment_safety():
    """
    Check if database connection is allowed for current environment.

    Raises:
        PermissionError: If attempting to connect to production or silo environment
    """
    s = _get_db_settings()
    env_lower = s.env.lower()

    if env_lower in RESTRICTED_ENVS:
        error_msg = (
            f"DATABASE CONNECTION BLOCKED: Cannot connect to '{s.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    # Log warning for non-test environments (just in case)
    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(f"Connecting to non-test environment: '{s.env}'. Ensure this is intentional.")


def get_configured_db(alias: str, database = None):
    """
    Get a configured database connection using a connection string from Key Vault.

    Safety: Prevents connections to production/silo databases.

    Args:
        alias: Vault database alias (e.g. 'transfer', 'accountdistributions', 'crm', 'billing').
        database: Optional database name override.

    Returns:
        SQLDatabase: Configured database instance ready to connect
    """
    _check_environment_safety()
    s = _get_db_settings()
    logger.info(f"Database connection approved for environment: '{s.env}'")

    return get_db_from_vault(alias=alias, database=database)


def get_configured_azure_db():
    """Local-compatible Azure SQL resolver from standard settings fields."""
    _check_environment_safety()
    s = _get_db_settings()

    logger.info(f"Database connection approved for environment: '{s.env}'")
    return AzureSQLDatabase(
        server=s.azure_sql_server,
        database=s.azure_sql_database,
        username=s.azure_sql_username,
        password=s.azure_sql_password,
        driver=s.azure_sql_driver,
        authentication=s.azure_sql_authentication,
    )


def get_configured_sql_server():
    """Local-compatible SQL Server resolver from standard settings fields."""
    _check_environment_safety()
    s = _get_db_settings()

    logger.info(f"SQL Server connection approved for environment: '{s.env}'")
    return AzureSQLDatabase(
        server=s.sql_server_host,
        database=s.sql_server_database,
        username=s.sql_server_username,
        password=s.sql_server_password,
        driver=s.sql_server_driver,
        authentication=None,
    )


def get_configured_ewm_db():
    """
    Get a configured EWM Database connection using settings.
    This connects to the EWM database (AM_Billing) for account-related queries.
    Uses standard SQL Server authentication (not Azure AD).

    Source resolution (automatic):
      - Azure DevOps pipeline -> reads AM_BILLING_CONNECTION_STRING env var (injected from Key Vault)
      - Local execution        -> reads database.ewm section from config/.secretCred.yaml

    Safety: Prevents connections to production/silo databases.
    Only allows connections to test environments (test*, qa, dev, etc.).

    Returns:
        AzureSQLDatabase: Configured EWM database instance ready to connect

    Raises:
        PermissionError: If attempting to connect to production or silo environment

    Example:
        with get_configured_ewm_db() as db:
            db.connect()
            results = db.execute_query("SELECT * FROM [dbo].[Account]")
    """
    from utils.settings import Settings

    env = os.getenv("TEST_ENV", "test11")
    settings = Settings(env=env)
    logger = setup_logger(__name__)

    env_lower = settings.env.lower()
    restricted_envs = ["prod", "production", "silo"]

    if env_lower in restricted_envs:
        error_msg = (
            f"DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"Connecting to EWM database in non-test environment: '{settings.env}'. "
            "Ensure this is intentional."
        )

    # Pipeline execution: use Key Vault secret injected as env var
    if _is_running_in_pipeline():
        conn_str = os.getenv("AM_BILLING_CONNECTION_STRING", "")
        if not conn_str:
            raise EnvironmentError(
                "AM_BILLING_CONNECTION_STRING env var is not set. "
                "Ensure the Azure Key Vault task has run and the secret "
                "'am-billing-connection-string' exists in Key Vault."
            )
        parsed = _parse_connection_string(conn_str)
        logger.info("[Pipeline] EWM DB credentials loaded from AM_BILLING_CONNECTION_STRING (Key Vault)")
        logger.info(f"  EWM Server: {parsed.get('server')}")
        logger.info(f"  EWM Database: {parsed.get('database')}")
        return AzureSQLDatabase(
            server=parsed.get("server"),
            database=parsed.get("database"),
            username=parsed.get("username"),
            password=parsed.get("password"),
            driver=parsed.get("driver", "{ODBC Driver 17 for SQL Server}"),
            authentication=parsed.get("authentication"),
            encrypt=True,
            trust_server_certificate=True,
        )

    # Local execution: use .secretCred.yaml
    logger.info(f"[Local] EWM database connection approved for environment: '{settings.env}'")
    logger.info(f"  EWM Hostname: {settings.ewm_hostname}")
    logger.info(f"  EWM Database: {settings.ewm_database}")
    logger.info(f"  EWM Username: {settings.ewm_username}")

    return AzureSQLDatabase(
        server=settings.ewm_hostname,
        database=settings.ewm_database,
        username=settings.ewm_username,
        password=settings.ewm_password,
        driver="{ODBC Driver 17 for SQL Server}",
        authentication=None,
        encrypt=True,
        trust_server_certificate=True,
    )


# ---------------------------------------------------------------------------
# Key Vault connection-string support
# ---------------------------------------------------------------------------


def parse_connection_string(conn_str: str) -> dict:
    """
    Parse a SQL Server / Azure SQL connection string into a dictionary.

    Supports semicolon-separated Key=Value pairs.

    Args:
        conn_str: Raw connection string.

    Returns:
        dict mapping lowered key names to values.
    """
    result = {}
    for part in conn_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        result[key.strip().lower()] = value.strip()
    return result


def get_db_from_vault(alias: str, database=None):
    """
    Get a SQLDatabase instance using a connection string injected as an env var.

    Resolution order:
        1. env_var from YAML config
        2. Derived env var from secret_name
    """
    _check_environment_safety()

    s = _get_db_settings()
    cfg = s.get_vault_db_config(alias)

    env_var = cfg.get("env_var", "")
    conn_str = os.getenv(env_var) if env_var else None

    if conn_str:
        logger.info(f"DB '{alias}': connection string from env var '{env_var}'")
    else:
        secret_name = cfg.get("secret_name", "")
        if secret_name:
            derived_env_var = secret_name.upper().replace("-", "_")
            conn_str = os.getenv(derived_env_var)
            if conn_str:
                logger.info(
                    f"DB '{alias}': connection string from derived env var '{derived_env_var}'"
                )

    if not conn_str:
        raise ValueError(
            f"Could not resolve connection string for database alias '{alias}'.\n"
            f"Tried:\n"
            f"  1. Env var: {cfg.get('env_var', '(not set)')}\n"
            f"  2. Derived env var from secret_name: {cfg.get('secret_name', '').upper().replace('-', '_')}\n"
            f"\n"
            f"For local dev: set {cfg.get('env_var', 'the env var')} in your .env file.\n"
            f"For CI/CD: ensure AzureKeyVault@2 task maps the secret to the env var."
        )

    parsed = parse_connection_string(conn_str)
    logger.info(
        f"DB '{alias}': connection string resolved -> "
        f"server={parsed.get('server') or parsed.get('data source', '?')}"
    )

    server = parsed.get("server") or parsed.get("data source") or parsed.get("host")
    db_name = database or (parsed.get("database") or parsed.get("initial catalog"))
    username = parsed.get("user id") or parsed.get("uid") or parsed.get("user")
    password = parsed.get("password") or parsed.get("pwd")
    driver = cfg.get("driver") or parsed.get("driver") or "{ODBC Driver 17 for SQL Server}"
    authentication = parsed.get("authentication")

    return SQLDatabase(
        server=server,
        database=db_name,
        username=username,
        password=password,
        driver=driver,
        authentication=authentication,
    )


def get_db_from_connection_string(conn_str: str, driver=None):
    """Build a SQLDatabase directly from a raw connection string."""
    parsed = parse_connection_string(conn_str)

    server = parsed.get("server") or parsed.get("data source") or parsed.get("host")
    db_name = parsed.get("database") or parsed.get("initial catalog")
    username = parsed.get("user id") or parsed.get("uid") or parsed.get("user")
    password = parsed.get("password") or parsed.get("pwd")
    drv = driver or parsed.get("driver") or "{ODBC Driver 17 for SQL Server}"
    authentication = parsed.get("authentication")

    return SQLDatabase(
        server=server,
        database=db_name,
        username=username,
        password=password,
        driver=drv,
        authentication=authentication,
    )

def execute_query_from_yaml(
    query_category: str,
    query_name: str,
    params: Optional[tuple] = None,
    azure_db=None,
    sql_server_db=None,
) -> list:
    """
    Execute a database query from the centralized YAML queries file.
    Automatically selects the correct database connection based on db_type in YAML.

    Args:
        query_category: Category from queries/sql_queries.yaml
        query_name: Query name within the category
        params: Optional query parameters as tuple
        azure_db: Optional pre-connected Azure DB fixture (reuses connection)
        sql_server_db: Optional pre-connected SQL Server fixture (reuses connection)
    """
    category_config = settings.database_queries.get(query_category, {})
    if not category_config:
        raise ValueError(f"Query category '{query_category}' not found in queries/sql_queries.yaml")
    db_type = category_config.get("db_type")
    if not db_type:
        raise ValueError(
            f"db_type not specified for query category '{query_category}' in queries/sql_queries.yaml. "
            "Add 'db_type: azure' or 'db_type: sql_server' to the category."
        )

    query = category_config.get("queries", {}).get(query_name)
    if not query:
        available_queries = list(category_config.get("queries", {}).keys())
        raise ValueError(
            f"Query '{query_name}' not found in category '{query_category}'. "
            f"Available queries: {available_queries}"
        )

    db = None
    connection_created = False

    try:
        if db_type == "azure":
            if azure_db:
                db = azure_db
                logger.info(f"Using Azure SQL connection (fixture) for: {query_category}.{query_name}")
            else:
                db = get_configured_azure_db()
                db.connect()
                connection_created = True
                logger.info(f"Created Azure SQL connection for: {query_category}.{query_name}")

        elif db_type == "sql_server":
            if sql_server_db:
                db = sql_server_db
                logger.info(f"Using SQL Server connection (fixture) for: {query_category}.{query_name}")
            else:
                db = get_configured_sql_server()
                db.connect()
                connection_created = True
                logger.info(f"Created SQL Server connection for: {query_category}.{query_name}")
        else:
            raise ValueError(
                f"Invalid db_type '{db_type}' for category '{query_category}'. "
                "Use 'azure' or 'sql_server'."
            )

        logger.info(f"Executing query on {db.database} @ {db.server}")
        logger.info(f"Query: {query}")

        results = db.execute_query(query, params)
        logger.info(f"Query executed successfully. Rows returned: {len(results)}")

        return results

    finally:
        if connection_created and db:
            db.close()
            logger.info("Database connection closed")



class DatabaseConnection:
    """Base class for database connections."""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.logger = setup_logger(__name__)

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SQLDatabase(DatabaseConnection):
    """SQL Database connection utility for both Azure SQL and standard SQL Server."""


    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "{ODBC Driver 17 for SQL Server}",
        authentication: Optional[str] = None,
        encrypt: bool = True,
        trust_server_certificate: bool = False,
    ):
        """
        Initialize SQL Database connection.

        Args:
            server: SQL server name (e.g., 'server.database.windows.net')
            database: Database name
            username: Username for authentication
            password: Password for authentication
            driver: ODBC driver to use
            authentication: Authentication method (e.g., 'ActiveDirectoryPassword')
            encrypt: Whether to use encrypted connection (default: True)
            trust_server_certificate: Whether to trust server certificate (default: False)
        """
        super().__init__()
        self.server = server or os.getenv("AZURE_SQL_SERVER")
        self.database = database or os.getenv("AZURE_SQL_DATABASE")
        self.username = username or os.getenv("AZURE_SQL_USERNAME")
        self.password = password or os.getenv("AZURE_SQL_PASSWORD")
        self.driver = driver
        self.authentication = authentication
        self.encrypt = encrypt
        self.trust_server_certificate = trust_server_certificate

    def connect(self):
        """Establish a connection to the Azure SQL database with retry logic."""
        try:
            is_driver_18_or_higher = "Driver 18" in str(self.driver) or "Driver 19" in str(
                self.driver
            )

            if self.authentication and self.authentication == "ActiveDirectoryPassword":
                if not is_driver_18_or_higher:
                    self.logger.warning(
                        f"ActiveDirectoryPassword requires ODBC Driver 18+. "
                        f"Current: {self.driver}. Using SQL auth instead. "
                        f"Install Driver 18 or use SQL username (not email)."
                    )
                    connection_string = (
                        f"DRIVER={self.driver};"
                        f"SERVER={self.server};"
                        f"DATABASE={self.database};"
                        f"UID={self.username};"
                        f"PWD={self.password};"
                        "Encrypt=yes;"
                        "TrustServerCertificate=yes;"
                        "Connection Timeout=30;"
                    )
                    self.logger.info(
                        f"Attempting connection to {self.database} using SQL authentication (Azure AD fallback)"
                    )
                else:
                    connection_string = (
                        f"DRIVER={self.driver};"
                        f"SERVER={self.server};"
                        f"DATABASE={self.database};"
                        f"UID={self.username};"
                        f"PWD={self.password};"
                        f"Authentication={self.authentication};"
                        "Encrypt=yes;"
                        "TrustServerCertificate=yes;"
                        "Connection Timeout=30;"
                    )
                    self.logger.info(
                        f"Attempting connection to {self.database} using Azure AD authentication"
                    )
            else:
                if self.username and "@" in self.username:
                    self.logger.warning(
                        f"Email username '{self.username}' may fail with SQL auth. "
                        f"Use SQL username OR install Driver 18 for Azure AD."
                    )
                connection_string = (
                    f"DRIVER={self.driver};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                    "Connection Timeout=30;"
                )
                self.logger.info(f"Attempting connection to {self.database} using SQL authentication")
                masked = connection_string.replace(f"PWD={self.password}", "PWD=****")
                self.logger.info(f"connection string {masked} ")

            with RetryContext(max_retries=3, initial_delay=2.0, exponential_base=2.0) as retry:
                while retry.should_retry():
                    try:
                        self.connection = pyodbc.connect(connection_string)
                        self.cursor = self.connection.cursor()
                        self.logger.info(
                            f"Successfully connected to {self.database} on {self.server}"
                        )
                        retry.success()
                        return self.connection
                    except pyodbc.OperationalError as e:
                        self.logger.warning(
                            f"Transient connection error to {self.database}: {str(e)}"
                        )
                        retry.failed(e)
                    except pyodbc.Error as e:
                        self.logger.error(f"Error connecting to {self.database}: {str(e)}")
                        raise

        except Exception as e:
            self.logger.error(f"Error connecting to {self.database}: {str(e)}")
            raise

    def use_database(self, database_name: str):
        """
        Switch to a different database on the same server connection.
        Uses SQL 'USE [database]' command to avoid creating new connections.
        """
        if not self.connection:
            self.connect()

        if self.database != database_name:
            self.cursor.execute(f"USE [{database_name}]")
            self.database = database_name
            self.logger.info(f"Switched to database: {database_name}")

    def execute_query(self, query: str, params=None) -> list:
        """Execute a SELECT query and return results as list of dictionaries."""
        if not self.connection:
            self.connect()

        with RetryContext(max_retries=2, initial_delay=1.0, exponential_base=2.0) as retry:
            while retry.should_retry():
                try:
                    if params:
                        self.cursor.execute(query, params)
                    else:
                        self.cursor.execute(query)

                    columns = [col[0] for col in self.cursor.description]
                    rows = self.cursor.fetchall()
                    results = [dict(zip(columns, row)) for row in rows]
                    self.logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                    self.logger.info(f"Columns: {columns}")
                    retry.success()
                    return results

                except pyodbc.OperationalError as e:
                    self.logger.warning(f"Transient query error: {str(e)}. Reconnecting...")
                    self.close()
                    self.connect()
                    retry.failed(e)
                except pyodbc.Error as e:
                    self.logger.error(f"Error executing query: {str(e)}")
                    raise

        return []


    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Safety: Prevents data modification in production/silo environments.
        Only allows INSERT/UPDATE/DELETE in test environments (test*, qa, dev).

        Args:
            query: SQL query to execute
            params: Query parameters (optional)

        Returns:
            Number of rows affected

        Raises:
            PermissionError: If attempting to modify data in production or silo environment
        """
        _check_environment_safety()

        try:
            if not self.connection:
                self.connect()

            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            self.connection.commit()
            rows_affected = self.cursor.rowcount
            self.logger.info(f"Query executed successfully. Rows affected: {rows_affected}")
            return rows_affected

        except pyodbc.Error as e:
            self.connection.rollback()
            self.logger.error(f"Error executing non-query: {str(e)}")
            raise

    def execute_query_and_get_first_value(self, query: str, column_name: str, params=None):
        """
        Execute a SELECT query and return the first value from specified column.

        Args:
            query: SQL query to execute
            column_name: Name of the column to extract value from
            params: Query parameters (optional)

        Returns:
            String value from the specified column, or None if no results
        """
        try:
            results = self.execute_query(query, params)

            if not results:
                self.logger.warning("No results found for query")
                return None

            columns = [column[0] for column in self.cursor.description]
            if column_name not in columns:
                raise ValueError(f"Column '{column_name}' not found in query results. Available columns: {columns}")

            column_index = columns.index(column_name)
            value = results[0][column_index]

            self.logger.info(f"Query completed on {column_name}: {value}")
            return str(value) if value is not None else None

        except pyodbc.Error as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise

    def execute_select_query_and_get_string_list(
        self,
        query: str,
        column_name: str,
        records_count=None,
        params=None,
    ) -> list:
        """
        Execute a SELECT query and return a list of string values from specified column.

        Args:
            query: SQL query to execute
            column_name: Name of the column to extract values from
            records_count: Maximum number of records to return (optional)
            params: Query parameters (optional)

        Returns:
            List of string values from the specified column
        """
        try:
            results = self.execute_query(query, params)

            if not results:
                self.logger.warning("No results found for query")
                return []

            columns = [column[0] for column in self.cursor.description]
            if column_name not in columns:
                raise ValueError(f"Column '{column_name}' not found in query results. Available columns: {columns}")

            column_index = columns.index(column_name)
            list_of_values = []
            counter = 0

            for row in results:
                value = row[column_index]
                list_of_values.append(str(value) if value is not None else "")
                counter += 1
                if records_count is not None and counter == records_count:
                    break

            self.logger.info(f"Query completed on {column_name}. Retrieved {len(list_of_values)} values")
            return list_of_values

        except pyodbc.Error as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise


class AzureSQLDatabase(SQLDatabase):
    """Backward-compatible class that returns pyodbc rows for execute_query."""

    def execute_query(self, query: str, params=None) -> list:
        """Execute SELECT query and return pyodbc row objects for legacy callers."""
        if not self.connection:
            self.connect()

        with RetryContext(max_retries=2, initial_delay=1.0, exponential_base=2.0) as retry:
            while retry.should_retry():
                try:
                    if params:
                        self.cursor.execute(query, params)
                    else:
                        self.cursor.execute(query)

                    results = self.cursor.fetchall()
                    self.logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                    retry.success()
                    return results

                except pyodbc.OperationalError as e:
                    self.logger.warning(f"Transient query error: {str(e)}. Reconnecting...")
                    self.close()
                    self.connect()
                    retry.failed(e)
                except pyodbc.Error as e:
                    self.logger.error(f"Error executing query: {str(e)}")
                    raise

        return []


# Convenience functions
def get_azure_db_connection(**kwargs):
    """
    Get an Azure SQL Database connection for the MaintenanceWorkflow database.

    Source resolution (automatic):
      - Azure DevOps pipeline -> reads MAINTENANCEWORKFLOW_DB_CONNECTION_STRING env var
      - Local execution        -> reads database.azure section from config/.secretCred.yaml

    Returns:
        AzureSQLDatabase instance
    """
    # Pipeline execution: use Key Vault secret injected as env var
    if _is_running_in_pipeline() and not any(k in kwargs for k in ['server', 'username', 'password']):
        conn_str = os.getenv("MAINTENANCEWORKFLOW_DB_CONNECTION_STRING", "")
        if conn_str:
            parsed = _parse_connection_string(conn_str)
            logger.info("[Pipeline] Azure DB credentials loaded from MAINTENANCEWORKFLOW_DB_CONNECTION_STRING (Key Vault)")
            username = parsed.get("username", "")
            driver = parsed.get("driver", "{ODBC Driver 18 for SQL Server}" if "@" in username else "{ODBC Driver 17 for SQL Server}")
            authentication = parsed.get("authentication", "ActiveDirectoryPassword" if "@" in username else None)
            return AzureSQLDatabase(
                server=parsed.get("server"),
                database=parsed.get("database"),
                username=username,
                password=parsed.get("password"),
                driver=driver,
                authentication=authentication,
            )
        else:
            raise EnvironmentError(
                "MAINTENANCEWORKFLOW_DB_CONNECTION_STRING env var is not set. "
                "Ensure the Azure Key Vault task has run and the secret "
                "'maintenanceworkflow-db-connection-string' exists in Key Vault."
            )

    # Local execution: use .secretCred.yaml
    if not any(k in kwargs for k in ['server', 'username', 'password']):
        try:
            from utils.settings import settings as _settings
            azure_config = _settings.config.get('database', {}).get('azure', {})
            if azure_config:
                kwargs.setdefault('server', azure_config.get('hostname'))
                kwargs.setdefault('username', azure_config.get('username'))
                kwargs.setdefault('password', azure_config.get('password'))
                kwargs.setdefault('database', azure_config.get('database', 'EWMProcessCenter'))
                username = kwargs.get('username')
                if username and '@' in username:
                    kwargs.setdefault('driver', '{ODBC Driver 18 for SQL Server}')
                    kwargs.setdefault('authentication', 'ActiveDirectoryPassword')
            logger.info("[Local] Azure DB credentials loaded from .secretCred.yaml (database.azure)")
        except Exception:
            pass

    return AzureSQLDatabase(**kwargs)


def _normalize_role(role: str) -> str:
    """Normalize role input to 'Agent' or 'SAU'."""
    role_lower = role.strip().lower()
    if role_lower in ("fa", "agent"):
        return "Agent"
    elif role_lower in ("sau", "shared access user"):
        return "SAU"
    else:
        raise ValueError(
            f"Invalid role: '{role}'. Use 'Agent'/'FA' or 'SAU'/'Shared Access User'."
        )


def fetch_agent_name_by_aplid_from_db(
    aplid: str,
    role: str,
    query_name=None,
    id_type=None,
    second_param=None,
):
    """
    Fetch user name from the AM database by APLID/UserID based on role.

    Args:
        aplid: User identifier (APLID for Agent, UserID for SAU).
        role: User role - 'FA'/'Agent' or 'SAU'/'Shared Access User'.
        query_name: Optional override query name from sql_queries.yaml.
        id_type: Optional label used in log messages.
        second_param: Optional second query parameter.

    Returns:
        Name_ManageLogin value or None if not found.
    """
    if not aplid:
        raise TypeError("aplid is required and cannot be empty")
    if not role:
        raise TypeError("role is required and cannot be empty")

    role_normalized = _normalize_role(role)

    if query_name:
        id_type = id_type or "ID"
    else:
        if role_normalized == "Agent":
            query_name = "agentName__by_aplid_from_agentTable"
            id_type = "APLID"
        else:
            query_name = "sau_name_by_aplid"
            id_type = "UserID"

    query = settings.database_queries.get("agent", {}).get("queries", {}).get(query_name)
    if not query:
        raise ValueError(
            f"Query 'agent.{query_name}' not found in queries/sql_queries.yaml. "
            "Ensure it is defined under 'agent: -> queries:'."
        )

    db = get_configured_ewm_db()
    db.connect()
    try:
        params = (second_param, aplid) if second_param else (aplid,)
        results = db.execute_query(query, params=params)
    finally:
        db.close()

    if results:
        row = results[0]
        try:
            name = row.Name_ManageLogin
        except AttributeError:
            columns = [col[0] for col in db.cursor.description] if db.cursor else []
            idx = columns.index("Name_ManageLogin") if "Name_ManageLogin" in columns else 0
            name = row[idx]
        logger.info(f"{role_normalized} name found for {id_type} {aplid}: {name}")
        return name

    logger.warning(f"No {role_normalized} found for {id_type}: {aplid}")
    return None
