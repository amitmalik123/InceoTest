"""
Database utility module for Azure SQL Database and SQL Server connections.
"""

import os
from typing import Optional

import pyodbc

from utils.logger import setup_logger
from utils.retry_utils import RetryContext

logger = setup_logger(__name__)


def _get_db_settings():
    """Get the centralized Settings singleton (lazy import to avoid circular deps)."""
    from config.PortfolioReporting.settings import get_settings

    return get_settings()


# Safety constants
RESTRICTED_ENVS = ["prod", "production", "silo"]


def _is_running_in_pipeline() -> bool:
    """
    Detect whether the code is running inside an Azure DevOps pipeline.
    """
    return bool(os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"))


def _parse_connection_string(conn_str: str) -> dict:
    """
    Parse an ADO.NET / ODBC-style connection string into a normalized dict.
    """
    key_map = {
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
        normalized = key_map.get(raw_key.strip().lower())
        if normalized:
            result[normalized] = value.strip()

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
        logger.warning(
            f"⚠ Connecting to non-test environment: '{s.env}'. " "Ensure this is intentional."
        )


def get_configured_db(alias: str, database: Optional[str] = None):
    """
    Get a configured database connection using a connection string from Key Vault.
    This is the recommended way to get database connections in tests.

    The Azure DevOps pipeline's AzureKeyVault@2 task fetches the secret from
    Key Vault and maps it to an environment variable. Python never calls the
    Key Vault API directly — it just reads os.getenv().

    Safety: Prevents connections to production/silo databases.

    Args:
        alias: Vault database alias (e.g. 'transfer', 'accountdistributions', 'crm', 'billing').
        database: Optional database name override.

    Returns:
        SQLDatabase: Configured database instance ready to connect

    Raises:
        PermissionError: If attempting to connect to production or silo environment
        ValueError: If the alias is not configured or the connection string cannot be resolved.

    Example:
        db = get_configured_db("transfer", database="Transfer")
        db.connect()
        results = db.execute_query("SELECT * FROM Table")
        db.close()

        # Or use context manager
        with get_configured_db("crm") as db:
            db.connect()
            results = db.execute_query("SELECT * FROM [CRM].[dbo].[Table]")
    """
    # Safety check
    _check_environment_safety()
    s = _get_db_settings()
    logger.info(f"Database connection approved for environment: '{s.env}'")

    return get_db_from_vault(alias=alias, database=database)


# ---------------------------------------------------------------------------
# Key Vault connection-string support
# ---------------------------------------------------------------------------


def parse_connection_string(conn_str: str) -> dict[str, str]:
    """
    Parse a SQL Server / Azure SQL connection string into a dictionary.

    Supports both semicolon-separated ``Key=Value`` pairs and
    ADO.NET / JDBC-style strings.

    Common keys produced (normalised to lowercase):
        server, database, user id, password, initial catalog,
        data source, encrypt, authentication, driver, ...

    Args:
        conn_str: Raw connection string, e.g.::

            Server=myserver.database.windows.net;Database=MyDB;
            User Id=myuser;Password=s3cr3t;Encrypt=True;

    Returns:
        dict mapping *lowered* key names to their string values.
    """
    result: dict[str, str] = {}
    # Split on ';' and handle quoted values
    for part in conn_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        result[key.strip().lower()] = value.strip()
    return result


def get_db_from_vault(alias: str, database: Optional[str] = None) -> "SQLDatabase":
    """
    Get a SQLDatabase instance using a **connection string injected as an env var**.

    The Azure DevOps pipeline's ``AzureKeyVault@2`` task fetches the secret from
    Key Vault and maps it to an environment variable. Python never calls the
    Key Vault API directly — it just reads ``os.getenv()``.

    Resolution order:
        1. ``env_var`` from YAML config (e.g. ``CRM_DB_CONNECTION_STRING``)
        2. Derived env var from ``secret_name`` (e.g. ``crm-db-connection-string`` → ``CRM_DB_CONNECTION_STRING``)

    For local development, set the env var in the ``.env`` file.
    For CI/CD, the pipeline injects it automatically via AzureKeyVault@2.

    Safety: Prevents connections to production/silo databases.

    Args:
        alias:    Short name defined in the YAML config under
                  ``database.vault_databases`` (e.g. ``'crm'``, ``'billing'``).
        database: Optional override for the database name extracted from the
                  connection string.

    Returns:
        SQLDatabase: Ready-to-connect database instance.

    Raises:
        ValueError: If the alias is not configured or the connection string
                    cannot be resolved.
        PermissionError: If the current environment is production/silo.

    Example::

        # In pipeline: AzureKeyVault@2 fetches 'crm-db-connection-string'
        #              and maps it to env var CRM_DB_CONNECTION_STRING

        db = get_db_from_vault("crm")
        db.connect()
        rows = db.execute_query("SELECT TOP 5 * FROM Clients")
        db.close()

        # Override the database from the connection string:
        db = get_db_from_vault("crm", database="CRM_Reporting")
    """
    _check_environment_safety()

    s = _get_db_settings()
    cfg = s.get_vault_db_config(alias)  # raises ValueError if missing

    # 1. Try the explicit env_var from YAML config
    env_var = cfg.get("env_var", "")
    conn_str = os.getenv(env_var) if env_var else None

    if conn_str:
        logger.info(f"DB '{alias}': connection string from env var '{env_var}'")
    else:
        # 2. Try deriving env var from secret_name
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
        f"DB '{alias}': connection string resolved → "
        f"server={parsed.get('server') or parsed.get('data source', '?')}"
    )

    # Resolve fields from the parsed connection string
    server = parsed.get("server") or parsed.get("data source") or parsed.get("host")
    db_name = database or (parsed.get("database") or parsed.get("initial catalog"))
    username = parsed.get("user id") or parsed.get("uid") or parsed.get("user")
    password = parsed.get("password") or parsed.get("pwd")

    # Driver: YAML override > connection-string > default
    driver = cfg.get("driver") or parsed.get("driver") or "{ODBC Driver 17 for SQL Server}"

    # Authentication: from connection string or None
    authentication = parsed.get("authentication")

    return SQLDatabase(
        server=server,
        database=db_name,
        username=username,
        password=password,
        driver=driver,
        authentication=authentication,
    )


def get_db_from_connection_string(conn_str: str, driver: Optional[str] = None) -> "SQLDatabase":
    """
    Build a SQLDatabase directly from a raw connection string (no Key Vault lookup).

    Useful when you already have the connection string value.

    Args:
        conn_str: Full connection string.
        driver:   Optional ODBC driver override.

    Returns:
        SQLDatabase ready to connect.
    """
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
    db_manager=None,
) -> list:
    """
    Execute a database query from the centralized YAML queries file.
    Automatically selects the correct database connection based on db_type in YAML.

    Args:
        query_category: Category from queries/sql_queries.yaml (e.g., "transfer", "crm")
        query_name: Query name within the category (e.g., "transfer_audit")
        params: Optional query parameters as tuple
        azure_db: Optional pre-connected Azure DB fixture (legacy/develop flow)
        sql_server_db: Optional pre-connected SQL Server fixture (legacy/develop flow)
        db_manager: Optional DatabaseConnectionManager for cached vault connections

    Returns:
        List of query results

    Raises:
        ValueError: If query/db_type missing or no valid connection path can be resolved
        PermissionError: If attempting to connect to production/silo environment

    Example:
        results = execute_query_from_yaml(
            "crm", "retirement_billing_client",
            db_manager=db_manager
        )
    """
    category_config = _get_db_settings().database_queries.get(query_category, {})

    if not category_config:
        raise ValueError(f"Query category '{query_category}' not found in queries/sql_queries.yaml")

    # Get db_type from YAML
    db_type = category_config.get("db_type")
    if not db_type:
        raise ValueError(
            f"db_type not specified for query category '{query_category}' in queries/sql_queries.yaml. "
            "Add 'db_type: azure' or 'db_type: sql_server' to the category."
        )

    # Get the actual query
    query = category_config.get("queries", {}).get(query_name)
    if not query:
        available_queries = list(category_config.get("queries", {}).keys())
        raise ValueError(
            f"Query '{query_name}' not found in category '{query_category}'. "
            f"Available queries: {available_queries}"
        )

    db = None
    connection_created = False

    database_name = category_config.get("database")
    vault_alias = category_config.get("vault_alias")

    if db_manager and vault_alias and database_name:
        db = db_manager.get_vault_db(alias=vault_alias, database=database_name)
        logger.info(
            f"Using vault connection-string (alias='{vault_alias}') "
            f"for: {query_category}.{query_name}"
        )
    else:
        try:
            if db_type == "azure":
                if azure_db:
                    db = azure_db
                    logger.info(
                        f"Using Azure SQL connection (fixture) for: {query_category}.{query_name}"
                    )
                else:
                    db = get_configured_azure_db()
                    db.connect()
                    connection_created = True
                    logger.info(f"Created Azure SQL connection for: {query_category}.{query_name}")
            elif db_type == "sql_server":
                if sql_server_db:
                    db = sql_server_db
                    logger.info(
                        f"Using SQL Server connection (fixture) for: {query_category}.{query_name}"
                    )
                else:
                    db = get_configured_sql_server()
                    db.connect()
                    connection_created = True
                    logger.info(
                        f"Created SQL Server connection for: {query_category}.{query_name}"
                    )
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

    if db is None:
        raise ValueError(
            f"Could not resolve database connection for category '{query_category}'. "
            "Provide db_manager with vault_alias+database in YAML, or use db_type with fixtures."
        )

    logger.info(f"Executing query on {db.database} @ {db.server}")
    logger.info(f"Query: {query}")
    results = db.execute_query(query, params)
    logger.info(f"Query executed successfully. Rows returned: {len(results)}")
    logger.info(f"Query output data: {results}")
    return results


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
    ):
        """
        Initialize SQL Database connection.

        Args:
            server: SQL server name (e.g., 'server.database.windows.net' or 'server.ncus.assetmark.net')
            database: Database name
            username: Username for authentication
            password: Password for authentication
            driver: ODBC driver to use
            authentication: Authentication method (e.g., 'ActiveDirectoryPassword' for Azure AD, None for SQL auth)
        """
        super().__init__()
        self.server = server or os.getenv("SQL_DB_SERVER")
        self.database = database or os.getenv("SQL_DB_DATABASE")
        self.username = username or os.getenv("SQL_DB_USERNAME")
        self.password = password or os.getenv("SQL_DB_PASSWORD")
        self.driver = driver
        self.authentication = authentication

    def connect(self):
        """Establish connection to SQL Database."""
        try:
            # Detect driver version
            is_driver_18_or_higher = "Driver 18" in str(self.driver) or "Driver 19" in str(
                self.driver
            )

            # Build connection string based on authentication method
            if self.authentication and self.authentication == "ActiveDirectoryPassword":
                if not is_driver_18_or_higher:
                    self.logger.warning(
                        f"ActiveDirectoryPassword requires ODBC Driver 18+. "
                        f"Current: {self.driver}. Using SQL auth instead. "
                        f"Install Driver 18 or use SQL username (not email)."
                    )
                    # Fall back to standard SQL authentication
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
                    # Azure AD Password authentication (Driver 18+)
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
                # Standard SQL authentication
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
                self.logger.info(
                    f"Attempting connection to {self.database} using SQL authentication"
                )
                masked = connection_string.replace(f"PWD={self.password}", "PWD=****")
                self.logger.info(f"connection string {masked} ")

            # Retry transient connection failures (Azure SQL often has transient errors)
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
                        # Non-transient errors (bad credentials, invalid DB) - fail immediately
                        self.logger.error(f"Error connecting to {self.database}: {str(e)}")
                        raise

        except Exception as e:
            self.logger.error(f"Error connecting to {self.database}: {str(e)}")
            raise

    def use_database(self, database_name: str):
        """
        Switch to a different database on the same server connection.
        Uses SQL 'USE [database]' command to avoid creating new connections.

        Args:
            database_name: Name of the database to switch to
        """
        if not self.connection:
            self.connect()

        if self.database != database_name:
            self.cursor.execute(f"USE [{database_name}]")
            self.database = database_name
            self.logger.info(f"Switched to database: {database_name}")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[dict]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Args:
            query: SQL query to execute
            params: Query parameters (optional)

        Returns:
            List of dicts where keys are column names.
            Example: [{"AccountNumber": "A001", "Status": "Active"}, ...]
        """
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
                    # Transient error - reconnect and retry
                    self.logger.warning(f"Transient query error: {str(e)}. Reconnecting...")
                    self.close()
                    self.connect()
                    retry.failed(e)
                except pyodbc.Error as e:
                    # Non-transient error - fail immediately
                    self.logger.error(f"Error executing query: {str(e)}")
                    raise

        return []  # Should not reach here; RetryContext raises on exhaustion

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
        # Safety check: Prevent data modifications in production/silo
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
        Execute a SELECT query and return first value from the specified column.
        """
        results = self.execute_query(query, params)
        if not results:
            self.logger.warning("No results found for query")
            return None

        first_row = results[0]
        if isinstance(first_row, dict):
            value = first_row.get(column_name)
        else:
            columns = [column[0] for column in self.cursor.description]
            if column_name not in columns:
                raise ValueError(
                    f"Column '{column_name}' not found in query results. Available columns: {columns}"
                )
            value = first_row[columns.index(column_name)]

        self.logger.info(f"Query completed on {column_name}: {value}")
        return str(value) if value is not None else None

    def execute_select_query_and_get_string_list(
        self,
        query: str,
        column_name: str,
        records_count=None,
        params=None,
    ) -> list:
        """
        Execute a SELECT query and return a list of string values from specified column.
        """
        results = self.execute_query(query, params)
        if not results:
            self.logger.warning("No results found for query")
            return []

        list_of_values = []
        counter = 0
        for row in results:
            if isinstance(row, dict):
                value = row.get(column_name)
            else:
                columns = [column[0] for column in self.cursor.description]
                if column_name not in columns:
                    raise ValueError(
                        f"Column '{column_name}' not found in query results. Available columns: {columns}"
                    )
                value = row[columns.index(column_name)]
            list_of_values.append(str(value) if value is not None else "")
            counter += 1
            if records_count is not None and counter == records_count:
                break

        self.logger.info(f"Query completed on {column_name}. Retrieved {len(list_of_values)} values")
        return list_of_values


class AzureSQLDatabase(SQLDatabase):
    """Backward-compatible class that returns pyodbc rows for execute_query."""

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
        super().__init__(server, database, username, password, driver, authentication)
        self.encrypt = encrypt
        self.trust_server_certificate = trust_server_certificate

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
    Get configured EWM database using pipeline env var or local settings.
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

    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"Connecting to EWM database in non-test environment: '{s.env}'. Ensure this is intentional."
        )

    if _is_running_in_pipeline():
        conn_str = os.getenv("AM_BILLING_CONNECTION_STRING", "")
        if not conn_str:
            raise EnvironmentError(
                "AM_BILLING_CONNECTION_STRING env var is not set. "
                "Ensure Azure Key Vault task mapped the secret."
            )
        parsed = _parse_connection_string(conn_str)
        logger.info("[Pipeline] EWM DB credentials loaded from AM_BILLING_CONNECTION_STRING")
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

    logger.info(f"[Local] EWM database connection approved for environment: '{s.env}'")
    return AzureSQLDatabase(
        server=s.ewm_hostname,
        database=s.ewm_database,
        username=s.ewm_username,
        password=s.ewm_password,
        driver="{ODBC Driver 17 for SQL Server}",
        authentication=None,
        encrypt=True,
        trust_server_certificate=True,
    )


def get_azure_db_connection(**kwargs) -> SQLDatabase:
    """
    Get an Azure SQL Database connection for MaintenanceWorkflow database.

    Returns:
        AzureSQLDatabase instance
    """
    if _is_running_in_pipeline() and not any(
        k in kwargs for k in ["server", "username", "password"]
    ):
        conn_str = os.getenv("MAINTENANCEWORKFLOW_DB_CONNECTION_STRING", "")
        if conn_str:
            parsed = _parse_connection_string(conn_str)
            logger.info(
                "[Pipeline] Azure DB credentials loaded from MAINTENANCEWORKFLOW_DB_CONNECTION_STRING"
            )
            username = parsed.get("username", "")
            driver = parsed.get(
                "driver",
                "{ODBC Driver 18 for SQL Server}" if "@" in username else "{ODBC Driver 17 for SQL Server}",
            )
            authentication = parsed.get(
                "authentication", "ActiveDirectoryPassword" if "@" in username else None
            )
            return AzureSQLDatabase(
                server=parsed.get("server"),
                database=parsed.get("database"),
                username=username,
                password=parsed.get("password"),
                driver=driver,
                authentication=authentication,
            )
        raise EnvironmentError(
            "MAINTENANCEWORKFLOW_DB_CONNECTION_STRING env var is not set. "
            "Ensure Azure Key Vault task mapped the secret."
        )

    if not any(k in kwargs for k in ["server", "username", "password"]):
        try:
            s = _get_db_settings()
            azure_config = s.config.get("database", {}).get("azure", {})
            if azure_config:
                kwargs.setdefault("server", azure_config.get("hostname"))
                kwargs.setdefault("username", azure_config.get("username"))
                kwargs.setdefault("password", azure_config.get("password"))
                kwargs.setdefault("database", azure_config.get("database", "EWMProcessCenter"))
                username = kwargs.get("username")
                if username and "@" in username:
                    kwargs.setdefault("driver", "{ODBC Driver 18 for SQL Server}")
                    kwargs.setdefault("authentication", "ActiveDirectoryPassword")
            logger.info("[Local] Azure DB credentials loaded from settings (database.azure)")
        except Exception:
            pass

    return AzureSQLDatabase(**kwargs)


def _normalize_role(role: str) -> str:
    """Normalize role input to 'Agent' or 'SAU'."""
    role_lower = role.strip().lower()
    if role_lower in ("fa", "agent"):
        return "Agent"
    if role_lower in ("sau", "shared access user"):
        return "SAU"
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
    Fetch user name from EWM database by APLID/UserID based on role.
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

    query = _get_db_settings().database_queries.get("agent", {}).get("queries", {}).get(query_name)
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
            if isinstance(row, dict):
                name = row.get("Name_ManageLogin")
            else:
                idx = columns.index("Name_ManageLogin") if "Name_ManageLogin" in columns else 0
                name = row[idx]
        logger.info(f"{role_normalized} name found for {id_type} {aplid}: {name}")
        return name

    logger.warning(f"No {role_normalized} found for {id_type}: {aplid}")
    return None

def fetch_authorized_signer(
    aplid: str, 
    role: str, 
    test_data: dict,
    second_param: Optional[str] = None
) -> str:
    """
    Fetch authorized signer name with environment-aware data source selection.
    
    For production, silo, and test10 environments: Returns value from test sheet (test_data)
    For other environments (test11, test12): Queries the database
    
    This function implements the strategy to avoid direct database access for protected
    environments while using test data for those environments.
    
    Args:
        aplid: User identifier (APLID for Agent role, UserID for SAU role)
        role: User role - 'Agent'/'FA' or 'SAU'/'Shared Access User'
        test_data: Dictionary containing test data row with 'Authorized_Signer_Role_Name' column
        second_param: (OPTIONAL) Second parameter required for SAU queries (Agent UserID)
        
    Returns:
        Authorized signer name from either test sheet or database
        
    Raises:
        ValueError: If authorized signer not found in test data for protected environments
        PermissionError: If attempting database access to restricted environments (handled by fetch_agent_name_by_aplid_from_db)
        
    Example:
        >>> test_data = {"Authorized_Signer_Role_Name": "John Smith", "APLID": "123456"}
        >>> name = fetch_authorized_signer("123456", "Agent", test_data)
        >>> print(name)  # "John Smith"
        
        >>> # For SAU with two parameters
        >>> name = fetch_authorized_signer("789012", "SAU", test_data, second_param="123456")
        >>> print(name)  # "Jane Doe"
    """
    try:
        settings = _get_db_settings()
        env = settings.env.lower()
        
        # Target environments where test sheet is used instead of database
        sheet_based_envs = ["prod", "production", "silo", "test10"]
        
        if env in sheet_based_envs:
            # Use test sheet value for protected environments
            signer_name = test_data.get("Authorized_Signer_Role_Name", "").strip()
            
            if not signer_name:
                raise ValueError(
                    f"Authorized_Signer_Role_Name not found in test data for {env} environment. "
                    f"Ensure 'Authorized_Signer_Role_Name' column is populated in test_data.{env}.csv"
                )
            
            logger.info(f"Using Authorized_Signer from test sheet for {env}: {signer_name}")
            return signer_name
        else:
            # Use database for other environments
            logger.info(f"Using Authorized_Signer from database for {env}")
            
            # For SAU role, need to pass second_param for the query
            if second_param:
                signer_name = fetch_agent_name_by_aplid_from_db(
                    aplid, 
                    role,
                    query_name="authorized_signer_SAU_name_ManageLogin_by_UserID",
                    second_param=second_param
                )
            else:
                signer_name = fetch_agent_name_by_aplid_from_db(aplid, role)
            
            # Strip whitespace from database result
            if signer_name:
                signer_name = signer_name.strip()
            
            if not signer_name:
                raise ValueError(
                    f"Authorized_Signer not found in database for {aplid} with role {role}"
                )
            
            return signer_name
            
    except ValueError as e:
        logger.error(f"Error fetching Authorized_Signer: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching Authorized_Signer: {str(e)}")
        raise