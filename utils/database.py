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
    from config.settings import get_settings

    return get_settings()


# Safety constants
RESTRICTED_ENVS = ["prod", "production", "silo"]


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
    db_manager=None,
) -> list:
    """
    Execute a database query from the centralized YAML queries file.
    Automatically selects the correct database connection based on db_type in YAML.
    Uses db_manager for connection reuse with USE database switching.

    Args:
        query_category: Category from queries/sql_queries.yaml (e.g., "transfer", "crm")
        query_name: Query name within the category (e.g., "transfer_audit")
        params: Optional query parameters as tuple
        db_manager: DatabaseConnectionManager that provides cached connections
                    with USE database switching

    Returns:
        List of query results

    Raises:
        ValueError: If query not found, db_type/database not specified, or db_manager missing
        PermissionError: If attempting to connect to production/silo environment

    Example:
        results = execute_query_from_yaml(
            "crm", "retirement_billing_client",
            db_manager=db_manager
        )
    """
    if not db_manager:
        raise ValueError(
            "db_manager is required. Pass the db_manager fixture from the step definition."
        )

    # Get query configuration from YAML
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

    # Get database name from query config
    database_name = category_config.get("database")
    if not database_name:
        raise ValueError(
            f"database not specified for query category '{query_category}' in queries/sql_queries.yaml. "
            "Add 'database: <database_name>' to the category."
        )

    # Prefer vault connection-string if vault_alias is configured
    db: SQLDatabase | None = None
    vault_alias = category_config.get("vault_alias")
    if vault_alias:
        db = db_manager.get_vault_db(alias=vault_alias, database=database_name)
        logger.info(
            f"Using vault connection-string (alias='{vault_alias}') "
            f"for: {query_category}.{query_name}"
        )
    else:
        raise ValueError(
            f"No vault_alias configured for query category '{query_category}' "
            f"in queries/sql_queries.yaml. All databases must use connection strings "
            f"from Key Vault. Add 'vault_alias: <alias>' to the category and configure "
            f"the corresponding entry under database.vault_databases in the env YAML."
        )

    # Log connection details
    assert db is not None, f"No database connection resolved for '{query_category}'"
    logger.info(f"Executing query on {db.database} @ {db.server}")
    logger.info(f"Query: {query}")

    # Execute query
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


# Convenience functions
def get_azure_db_connection(**kwargs) -> SQLDatabase:
    """
    Get an Azure SQL Database connection.

    Returns:
        SQLDatabase instance
    """
    return SQLDatabase(**kwargs)

def fetch_agent_name_by_aplid_from_db(
    aplid: str, 
    role: str, 
    query_name: Optional[str] = None,
    id_type: Optional[str] = None,
    second_param: Optional[str] = None
) -> Optional[str]:
    """
    Fetch user name from database by APLID/UserID based on role or custom query.
    
    Supports fetching names for both Agent and Shared Access User (SAU) roles.
    Uses the appropriate query from queries/sql_queries.yaml:
    - Agent (FA): 'agent.agent_name_by_aplid' - requires usl.UserID (APLID)
    - SAU: 'agent.authorized_signer_SAU_name_ManageLogin_by_UserID' - requires sd.UserID and usl.UserID parameters
    
    If query_name is provided, it will be used directly instead of role-based mapping.
    
    Queries the AM database on SQL Server.
    
    Args:
        aplid: User identifier to lookup:
               - For Agent role: APLID (usl.UserID from SSO Link table)
               - For SAU role: UserID (sd.UserID from SSO Details table)
        role: User role (REQUIRED) - accepts:
              Agent: 'FA', 'fa', 'agent', 'Agent' 
              SAU: 'SAU', 'sau', 'shared access user', 'Shared Access User'
        query_name: (OPTIONAL) Custom query name from queries/sql_queries.yaml.
                   If provided, this query will be used instead of role-based mapping.
                   Example: "agentName__by_aplid_from_agentTable"
        id_type: (OPTIONAL) Description of the ID type for logging purposes.
                If not provided, will be derived from role.
                Example: "APLID", "UserID", "AccountNumber"
        second_param: (OPTIONAL) Second parameter for queries that require multiple parameters.
                     For SAU query 'authorized_signer_SAU_name_ManageLogin_by_UserID', this is usl.UserID (Agent ID).
                     Query uses: sd.UserID = ? AND usl.UserID = second_param
        
    Returns:
        User name (Name_ManageLogin) or None if not found
        
    Raises:
        PermissionError: If attempting to connect to production/silo environment
        ValueError: If role is invalid or query not found in sql_queries.yaml
        TypeError: If aplid or role is not provided
        
    Example:
        >>> # Fetch Agent name using APLID with role-based query selection
        >>> agent_name = fetch_agent_name_by_aplid_from_db("123456", role="Agent")
        >>> if agent_name:
        ...     print(f"Agent: {agent_name}")
        
        >>> # Fetch SAU name with two parameters
        >>> sau_name = fetch_agent_name_by_aplid_from_db(
        ...     "789012",  # sd.UserID
        ...     role="SAU",
        ...     query_name="authorized_signer_SAU_name_ManageLogin_by_UserID",
        ...     second_param="123456"  # usl.UserID
        ... )
        >>> if sau_name:
        ...     print(f"Shared Access User: {sau_name}")
        
        >>> # Fetch using custom query name
        >>> name = fetch_agent_name_by_aplid_from_db(
        ...     "456789", 
        ...     role="Agent", 
        ...     query_name="customAgentQuery",
        ...     id_type="CustomID"
        ... )
    """
    try:
        # Step 1: Validate required parameters
        if not aplid:
            raise TypeError("aplid is required and cannot be empty")
        if not role:
            raise TypeError("role is required and cannot be empty")
        
        # Step 2: Normalize and validate role
        role_normalized = _normalize_role(role)
        logger.info(f"Fetching {role_normalized} name for ID: {aplid}")
        
        # Step 3: Get database settings
        settings = _get_db_settings()
        
        # Step 4: Determine which query to use - prefer custom query_name if provided
        if query_name:
            logger.info(f"Using custom query name: {query_name}")
            # If custom query_name provided, use it directly
            if not id_type:
                id_type = "ID"  # Default id_type for custom queries
        else:
            # Fallback to role-based query mapping
            logger.info(f"Using role-based query mapping for role: {role_normalized}")
            if role_normalized == "Agent":
                query_name = "agentName__by_aplid_from_agentTable"
                id_type = "APLID"
            elif role_normalized == "SAU":
                query_name = "sau_name_by_aplid"
                id_type = "UserID"
            else:
                raise ValueError(f"Invalid role: '{role}'. Use 'Agent'/'FA' or 'SAU'/'Shared Access User'.")
        
        # Step 5: Get query from centralized queries file
        query = settings.database_queries.get("agent", {}).get("queries", {}).get(query_name)
        
        if not query:
            raise ValueError(
                f"Query 'agent.{query_name}' not found in queries/sql_queries.yaml. "
                f"Ensure the query is defined under 'agent: -> queries:' section."
            )
        
        logger.info(f"Query found: agent.{query_name}")
        
        # Step 6: Get configured SQL Server connection (agent data is in AM database, accessed via billing vault alias)
        db = get_configured_db("billing", database="AM")
        db.connect()
        logger.info("✓ Connected to AM database")
        
        # Step 7: Execute parameterized query
        logger.info(f"Executing {query_name} query with {id_type}: {aplid}")
        if second_param:
            logger.info(f"  Additional parameter (second_param): {second_param}")
            results = db.execute_query(query, params=(second_param, aplid))
        else:
            results = db.execute_query(query, params=(aplid,))
        
        # Step 8: Close database connection
        db.close()
        logger.info("✓ Database connection closed")
        
        # Step 9: Extract and return name
        if results and len(results) > 0:
            user_name = results[0].get("Name_ManageLogin")
            logger.info(f"✓ {role_normalized} name found: {user_name}")
            return user_name
        else:
            logger.warning(f"⚠ No {role_normalized} found for {id_type}: {aplid}")
            return None
            
    except (PermissionError, ValueError, TypeError) as e:
        logger.error(f"✗ Error: {str(e)}")
        raise
    except Exception as ex:
        logger.error(f"✗ Error fetching {role} name for ID '{aplid}': {str(ex)}")
        raise


def _normalize_role(role: str) -> str:
    """
    Normalize role input to standard format.
    
    Args:
        role: Role input - accepts various formats for Agent or SAU
        
    Returns:
        Normalized role: 'Agent' or 'SAU'
        
    Raises:
        ValueError: If role doesn't match known values
        
    Example:
        >>> _normalize_role("fa")
        'Agent'
        >>> _normalize_role("SAU")
        'SAU'
        >>> _normalize_role("shared access user")
        'SAU'
    """
    # Agent role aliases
    agent_aliases = ["fa", "agent"]
    
    # SAU role aliases
    sau_aliases = ["sau", "shared access user"]
    
    role_lower = role.strip().lower()
    
    if role_lower in agent_aliases:
        return "Agent"
    elif role_lower in sau_aliases:
        return "SAU"
    else:
        raise ValueError(
            f"Invalid role: '{role}'. "
            f"Accepted values for Agent: {agent_aliases + ['Agent', 'FA']}. "
            f"Accepted values for SAU: {sau_aliases + ['SAU', 'Shared Access User']}."
        )

