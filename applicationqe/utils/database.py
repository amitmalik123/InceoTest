"""
Database utility module for Azure SQL Database and SQL Server connections.
"""

import os
from typing import Optional

import pyodbc

from utils.logger import setup_logger
from utils.settings import Settings

# Global configuration - initialized once at module import
_env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=_env)
logger = setup_logger(__name__)

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
      Server / Data Source           ΓåÆ server
      Database / Initial Catalog     ΓåÆ database
      User ID / UID / User           ΓåÆ username
      Password / PWD                 ΓåÆ password
      Authentication                 ΓåÆ authentication
      Driver                         ΓåÆ driver

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
    env_lower = settings.env.lower()

    if env_lower in RESTRICTED_ENVS:
        error_msg = (
            f"DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    # Log warning for non-test environments (just in case)
    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"ΓÜá Connecting to non-test environment: '{settings.env}'. "
            "Ensure this is intentional."
        )


def get_configured_azure_db():
    """
    Get a configured Azure SQL Database connection using settings.
    This is the recommended way to get database connections in tests.

    Safety: Prevents connections to production/silo databases.
    Only allows connections to test environments (test*, qa, dev, etc.)

    Returns:
        AzureSQLDatabase: Configured database instance ready to connect

    Raises:
        PermissionError: If attempting to connect to production or silo environment

    Example:
        db = get_configured_azure_db()
        db.connect()
        results = db.execute_query("SELECT * FROM Table")
        db.close()

        # Or use context manager
        with get_configured_azure_db() as db:
            db.connect()
            results = db.execute_query("SELECT * FROM Table")
    """
    # Safety check
    _check_environment_safety()
    logger.info(f"Database connection approved for environment: '{settings.env}'")

    return AzureSQLDatabase(
        server=settings.azure_sql_server,
        database=settings.azure_sql_database,
        username=settings.azure_sql_username,
        password=settings.azure_sql_password,
        driver=settings.azure_sql_driver,
        authentication=settings.azure_sql_authentication,
    )


def get_configured_sql_server():
    """
    Get a configured SQL Server connection using settings.
    This is for standard SQL Server connections (non-Azure AD).

    Safety: Prevents connections to production/silo databases.
    Only allows connections to test environments (test*, qa, dev, etc.)

    Returns:
        AzureSQLDatabase: Configured SQL Server instance ready to connect

    Raises:
        PermissionError: If attempting to connect to production or silo environment

    Example:
        db = get_configured_sql_server()
        db.connect()
        results = db.execute_query("SELECT * FROM [CRM].[dbo].[Table]")
        db.close()

        # Or use context manager
        with get_configured_sql_server() as db:
            db.connect()
            results = db.execute_query("SELECT * FROM [CRM].[dbo].[Table]")
    """
    # Safety check
    _check_environment_safety()
    logger.info(f"SQL Server connection approved for environment: '{settings.env}'")

    # Return standard SQL Server connection (no Azure AD authentication)
    return AzureSQLDatabase(
        server=settings.sql_server_host,
        database=settings.sql_server_database,
        username=settings.sql_server_username,
        password=settings.sql_server_password,
        driver=settings.sql_server_driver,
        authentication=None,  # Standard SQL authentication
    )


def get_configured_ewm_db():
    """
    Get a configured EWM Database connection using settings.
    This connects to the EWM database (AM_Billing) for account-related queries.
    Uses standard SQL Server authentication (not Azure AD).

    Source resolution (automatic):
      - Azure DevOps pipeline ΓåÆ reads AM_BILLING_CONNECTION_STRING env var (injected from Key Vault)
      - Local execution        ΓåÆ reads database.ewm section from config/.secretCred.yaml

    Safety: Prevents connections to production/silo databases.
    Only allows connections to test environments (test*, qa, dev, etc.).

    Returns:
        AzureSQLDatabase: Configured EWM database instance ready to connect

    Raises:
        PermissionError: If attempting to connect to production or silo environment

    Example:
        db = get_configured_ewm_db()
        db.connect()
        results = db.execute_query("SELECT FamilyID FROM [dbo].[Account] WHERE AccountNo = '123'")
        db.close()

        # Or use context manager
        with get_configured_ewm_db() as db:
            db.connect()
            results = db.execute_query("SELECT * FROM [dbo].[Account]")
    """
    from utils.settings import Settings

    # Get environment from environment variable or use default
    env = os.getenv("TEST_ENV", "test11")
    settings = Settings(env=env)
    logger = setup_logger(__name__)

    # Safety check: Prevent connections to production or silo environments
    env_lower = settings.env.lower()
    restricted_envs = ["prod", "production", "silo"]

    if env_lower in restricted_envs:
        error_msg = (
            f"Γ¥î DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    # Log warning for non-test environments
    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"ΓÜá Connecting to EWM database in non-test environment: '{settings.env}'. "
            "Ensure this is intentional."
        )

    # ΓöÇΓöÇ Pipeline execution: use Key Vault secret injected as env var ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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

    # ΓöÇΓöÇ Local execution: use .secretCred.yaml ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    logger.info(f"[Local] EWM database connection approved for environment: '{settings.env}'")
    logger.info(f"  EWM Hostname: {settings.ewm_hostname}")
    logger.info(f"  EWM Database: {settings.ewm_database}")
    logger.info(f"  EWM Username: {settings.ewm_username}")

    # Return EWM database connection (standard SQL authentication)
    return AzureSQLDatabase(
        server=settings.ewm_hostname,
        database=settings.ewm_database,
        username=settings.ewm_username,
        password=settings.ewm_password,
        driver="{ODBC Driver 17 for SQL Server}",
        authentication=None,  # Standard SQL authentication
        encrypt=True,  # Keep encryption enabled
        trust_server_certificate=True,  # Trust certificate for on-premises SQL Server
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
        query_category: Category from queries/sql_queries.yaml (e.g., "transfer", "crm")
        query_name: Query name within the category (e.g., "transfer_audit")
        params: Optional query parameters as tuple
        azure_db: Optional pre-connected Azure DB fixture (reuses connection)
        sql_server_db: Optional pre-connected SQL Server fixture (reuses connection)

    Returns:
        List of query results

    Raises:
        ValueError: If query not found or db_type not specified in YAML
        PermissionError: If attempting to connect to production/silo environment

    Example:
        # Without fixtures (creates new connection)
        results = execute_query_from_yaml("transfer", "transfer_audit")

        # With fixtures (reuses connection)
        results = execute_query_from_yaml(
            "transfer", "transfer_by_id",
            params=(12345,),
            azure_db=azure_db_fixture
        )
    """
    # Get query configuration from YAML
    category_config = settings.database_queries.get(query_category, {})

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

    # Determine which database connection to use
    db = None
    connection_created = False

    try:
        if db_type == "azure":
            if azure_db:
                # Reuse provided fixture connection
                db = azure_db
                logger.info(
                    f"Using Azure SQL connection (fixture) for: {query_category}.{query_name}"
                )
            else:
                # Create new connection
                db = get_configured_azure_db()
                db.connect()
                connection_created = True
                logger.info(f"Created Azure SQL connection for: {query_category}.{query_name}")

        elif db_type == "sql_server":
            if sql_server_db:
                # Reuse provided fixture connection
                db = sql_server_db
                logger.info(
                    f"Using SQL Server connection (fixture) for: {query_category}.{query_name}"
                )
            else:
                # Create new connection
                db = get_configured_sql_server()
                db.connect()
                connection_created = True
                logger.info(f"Created SQL Server connection for: {query_category}.{query_name}")
        else:
            raise ValueError(
                f"Invalid db_type '{db_type}' for category '{query_category}'. "
                "Use 'azure' or 'sql_server'."
            )

        # Log connection details
        logger.info(f"Executing query on {db.database} @ {db.server}")
        logger.info(f"Query: {query}")

        # Execute query
        results = db.execute_query(query, params)
        logger.info(f"Query executed successfully. Rows returned: {len(results)}")

        return results

    finally:
        # Only close if we created the connection (not if using fixture)
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


class AzureSQLDatabase(DatabaseConnection):
    """Azure SQL Database connection utility."""

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
        Initialize Azure SQL Database connection.

        Args:
            server: Azure SQL server name (e.g., 'server.database.windows.net')
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
        """Establish connection to Azure SQL Database."""
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
                        f"Attempting Azure SQL connection to {self.database} using SQL authentication"
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
                        f"TrustServerCertificate=no;"
                        "Connection Timeout=30;"
                    )
                    self.logger.info(
                        f"Attempting Azure SQL connection to {self.database} using Azure AD authentication"
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
                    f"Attempting Azure SQL connection to {self.database} using SQL authentication"
                )

            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            self.logger.info(f"Successfully connected to Azure SQL Database: {self.database}")
            return self.connection

        except pyodbc.Error as e:
            self.logger.error(f"Error connecting to Azure SQL Database: {str(e)}")
            raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters (optional)

        Returns:
            List of rows from query result
        """
        try:
            if not self.connection:
                self.connect()

            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            self.logger.info(f"Query executed successfully. Rows returned: {len(results)}")
            return results

        except pyodbc.Error as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise

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

    def execute_query_and_get_first_value(self, query: str, column_name: str, params: Optional[tuple] = None) -> Optional[str]:
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
                self.logger.warning(f"No results found for query")
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
        records_count: Optional[int] = None,
        params: Optional[tuple] = None
    ) -> list[str]:
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
                self.logger.warning(f"No results found for query")
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


# PostgreSQL Database - Currently not used in the framework
# Uncomment if PostgreSQL support is needed in the future
# Note: Requires psycopg2 package (pip install psycopg2)

# class PostgreSQLDatabase(DatabaseConnection):
#     """PostgreSQL Database connection utility."""
#
#     def __init__(
#         self,
#         host: Optional[str] = None,
#         port: Optional[int] = None,
#         database: Optional[str] = None,
#         username: Optional[str] = None,
#         password: Optional[str] = None,
#         use_pool: bool = False,
#         min_connections: int = 1,
#         max_connections: int = 10,
#     ):
#         """
#         Initialize PostgreSQL Database connection.
#
#         Args:
#             host: Database host
#             port: Database port
#             database: Database name
#             username: Username for authentication
#             password: Password for authentication
#             use_pool: Whether to use connection pooling
#             min_connections: Minimum connections in pool
#             max_connections: Maximum connections in pool
#         """
#         super().__init__()
#         self.host = host or os.getenv("POSTGRES_HOST", "localhost")
#         self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
#         self.database = database or os.getenv("POSTGRES_DATABASE")
#         self.username = username or os.getenv("POSTGRES_USERNAME")
#         self.password = password or os.getenv("POSTGRES_PASSWORD")
#         self.use_pool = use_pool
#         self.min_connections = min_connections
#         self.max_connections = max_connections
#         self.connection_pool = None
#
#     def connect(self):
#         """Establish connection to PostgreSQL Database."""
#         try:
#             if self.use_pool:
#                 self.connection_pool = psycopg2.pool.SimpleConnectionPool(
#                     self.min_connections,
#                     self.max_connections,
#                     host=self.host,
#                     port=self.port,
#                     database=self.database,
#                     user=self.username,
#                     password=self.password,
#                 )
#                 self.connection = self.connection_pool.getconn()
#                 self.logger.info(
#                     f"Successfully created PostgreSQL connection pool for: {self.database}"
#                 )
#             else:
#                 self.connection = psycopg2.connect(
#                     host=self.host,
#                     port=self.port,
#                     database=self.database,
#                     user=self.username,
#                     password=self.password,
#                 )
#                 self.logger.info(f"Successfully connected to PostgreSQL Database: {self.database}")
#
#             self.cursor = self.connection.cursor()
#             return self.connection
#
#         except psycopg2.Error as e:
#             self.logger.error(f"Error connecting to PostgreSQL Database: {str(e)}")
#             raise
#
#     def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
#         """
#         Execute a SELECT query and return results.
#
#         Args:
#             query: SQL query to execute
#             params: Query parameters (optional)
#
#         Returns:
#             List of rows from query result
#         """
#         try:
#             if not self.connection:
#                 self.connect()
#
#             if params:
#                 self.cursor.execute(query, params)
#             else:
#                 self.cursor.execute(query)
#
#             results = self.cursor.fetchall()
#             self.logger.info(f"Query executed successfully. Rows returned: {len(results)}")
#             return results
#
#         except psycopg2.Error as e:
#             self.logger.error(f"Error executing query: {str(e)}")
#             raise
#
#     def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
#         """
#         Execute an INSERT, UPDATE, or DELETE query.
#
#         Args:
#             query: SQL query to execute
#             params: Query parameters (optional)
#
#         Returns:
#             Number of rows affected
#         """
#         try:
#             if not self.connection:
#                 self.connect()
#
#             if params:
#                 self.cursor.execute(query, params)
#             else:
#                 self.cursor.execute(query)
#
#             self.connection.commit()
#             rows_affected = self.cursor.rowcount
#             self.logger.info(f"Query executed successfully. Rows affected: {rows_affected}")
#             return rows_affected
#
#         except psycopg2.Error as e:
#             self.connection.rollback()
#             self.logger.error(f"Error executing non-query: {str(e)}")
#             raise
#
#     def close(self):
#         """Close database connection and return to pool if using pooling."""
#         if self.cursor:
#             self.cursor.close()
#         if self.connection:
#             if self.use_pool and self.connection_pool:
#                 self.connection_pool.putconn(self.connection)
#                 self.logger.info("Connection returned to pool")
#             else:
#                 self.connection.close()
#                 self.logger.info("Database connection closed")
#
#         if self.connection_pool:
#             self.connection_pool.closeall()
#             self.logger.info("Connection pool closed")
#
#     def execute_many(self, query: str, data: list) -> int:
#         """
#         Execute a query with multiple parameter sets (bulk insert/update).
#
#         Args:
#             query: SQL query to execute
#             data: List of tuples containing parameter sets
#
#         Returns:
#             Number of rows affected
#         """
#         try:
#             if not self.connection:
#                 self.connect()
#
#             self.cursor.executemany(query, data)
#             self.connection.commit()
#             rows_affected = self.cursor.rowcount
#             self.logger.info(f"Batch query executed successfully. Rows affected: {rows_affected}")
#             return rows_affected
#
#         except psycopg2.Error as e:
#             self.connection.rollback()
#             self.logger.error(f"Error executing batch query: {str(e)}")
#             raise


# Convenience functions
def get_azure_db_connection(**kwargs) -> AzureSQLDatabase:
    """
    Get an Azure SQL Database connection for the MaintenanceWorkflow database.

    Source resolution (automatic):
      - Azure DevOps pipeline ΓåÆ reads MAINTENANCEWORKFLOW_DB_CONNECTION_STRING env var
                                (injected from Key Vault secret 'maintenanceworkflow-db-connection-string')
      - Local execution        ΓåÆ reads database.azure section from config/.secretCred.yaml

    Returns:
        AzureSQLDatabase instance
    """
    # ΓöÇΓöÇ Pipeline execution: use Key Vault secret injected as env var ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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

    # ΓöÇΓöÇ Local execution: use .secretCred.yaml ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    # If no credentials provided, try to load from settings
    if not any(k in kwargs for k in ['server', 'username', 'password']):
        try:
            from utils.settings import settings
            azure_config = settings.config.get('database', {}).get('azure', {})

            if azure_config:
                kwargs.setdefault('server', azure_config.get('hostname'))
                kwargs.setdefault('username', azure_config.get('username'))
                kwargs.setdefault('password', azure_config.get('password'))
                # Default database name if not specified
                kwargs.setdefault('database', azure_config.get('database', 'EWMProcessCenter'))

                # If username is an email, use Azure AD authentication with Driver 18
                username = kwargs.get('username')
                if username and '@' in username:
                    kwargs.setdefault('driver', '{ODBC Driver 18 for SQL Server}')
                    kwargs.setdefault('authentication', 'ActiveDirectoryPassword')
            logger.info("[Local] Azure DB credentials loaded from .secretCred.yaml (database.azure)")
        except Exception:
            # If settings can't be loaded, fall back to environment variables
            pass

    return AzureSQLDatabase(**kwargs)


# PostgreSQL connection factory - commented out as PostgreSQL is not used
# def get_postgres_connection(**kwargs) -> PostgreSQLDatabase:
#     return PostgreSQLDatabase(**kwargs)


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
    query_name: Optional[str] = None,
    id_type: Optional[str] = None,
    second_param: Optional[str] = None,
) -> Optional[str]:
    """
    Fetch user name from the AM database by APLID/UserID based on role.

    Args:
        aplid: User identifier (APLID for Agent, UserID for SAU).
        role: User role ΓÇö 'FA'/'Agent' or 'SAU'/'Shared Access User'.
        query_name: Optional override query name from sql_queries.yaml under 'agent.queries'.
        id_type: Optional label used in log messages (derived from role if omitted).
        second_param: Optional second query parameter (used by some SAU queries).

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
        # pyodbc rows support index and attribute access; try both
        try:
            name = row.Name_ManageLogin
        except AttributeError:
            columns = [col[0] for col in db.cursor.description] if db.cursor else []
            idx = columns.index("Name_ManageLogin") if "Name_ManageLogin" in columns else 0
            name = row[idx]
        logger.info(f"Γ£ô {role_normalized} name found for {id_type} {aplid}: {name}")
        return name

    logger.warning(f"No {role_normalized} found for {id_type}: {aplid}")
    return None
