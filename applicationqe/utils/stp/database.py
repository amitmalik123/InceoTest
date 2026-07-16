
import os
from typing import Optional

import pyodbc

from utils.logger import setup_logger
from utils.settings import Settings

_env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=_env)
logger = setup_logger(__name__)

RESTRICTED_ENVS = ["prod", "production", "silo"]


def _is_running_in_pipeline() -> bool:
    return bool(os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"))


def _parse_connection_string(conn_str: str) -> dict:
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
    env_lower = settings.env.lower()

    if env_lower in RESTRICTED_ENVS:
        error_msg = (
            f"DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"⚠ Connecting to non-test environment: '{settings.env}'. "
            "Ensure this is intentional."
        )


def get_configured_azure_db():
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
    _check_environment_safety()
    logger.info(f"SQL Server connection approved for environment: '{settings.env}'")

    return AzureSQLDatabase(
        server=settings.sql_server_host,
        database=settings.sql_server_database,
        username=settings.sql_server_username,
        password=settings.sql_server_password,
        driver=settings.sql_server_driver,
        authentication=None,
    )


def get_configured_ewm_db():
    from utils.settings import Settings

    env = os.getenv("TEST_ENV", "test11")
    settings = Settings(env=env)
    logger = setup_logger(__name__)

    env_lower = settings.env.lower()
    restricted_envs = ["prod", "production", "silo"]

    if env_lower in restricted_envs:
        error_msg = (
            f"❌ DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment.\n"
            f"Direct database connections are only allowed for test environments (test*, qa, dev).\n"
            f"Production/Silo database access must be done through approved processes only."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    if not env_lower.startswith("test") and env_lower not in ["qa", "dev", "development"]:
        logger.warning(
            f"⚠ Connecting to EWM database in non-test environment: '{settings.env}'. "
            "Ensure this is intentional."
        )

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


def get_configured_platform_db():
    from utils.settings import Settings

    env = os.getenv("TEST_ENV", "test11")
    settings = Settings(env=env)
    logger = setup_logger(__name__)

    env_lower = settings.env.lower()
    restricted_envs = ["prod", "production", "silo"]

    if env_lower in restricted_envs:
        error_msg = (
            f"DATABASE CONNECTION BLOCKED: Cannot connect to '{settings.env}' environment. "
            f"Direct database connections are only allowed for test environments (test*, qa, dev)."
        )
        logger.error(error_msg)
        raise PermissionError(error_msg)

    if _is_running_in_pipeline():
        conn_str = os.getenv("AM_BILLING_CONNECTION_STRING", "")
        if not conn_str:
            raise EnvironmentError(
                "AM_BILLING_CONNECTION_STRING env var is not set. "
                "Ensure the Azure Key Vault task has run and the secret "
                "'am-billing-connection-string' exists in Key Vault."
            )
        parsed = _parse_connection_string(conn_str)
        logger.info("[Pipeline] Platform DB credentials loaded from AM_BILLING_CONNECTION_STRING (Key Vault)")
        logger.info(f"  Platform Server: {parsed.get('server')}")
        return AzureSQLDatabase(
            server=parsed.get("server"),
            database="Platform",
            username=parsed.get("username"),
            password=parsed.get("password"),
            driver=parsed.get("driver", "{ODBC Driver 17 for SQL Server}"),
            authentication=parsed.get("authentication"),
            encrypt=True,
            trust_server_certificate=True,
        )

    logger.info(f"[Local] Platform database connection for environment: '{settings.env}'")
    logger.info(f"  Server: {settings.ewm_hostname}")
    logger.info(f"  Database: Platform")
    logger.info(f"  Username: {settings.ewm_username}")

    return AzureSQLDatabase(
        server=settings.ewm_hostname,
        database="Platform",
        username=settings.ewm_username,
        password=settings.ewm_password,
        driver="{ODBC Driver 17 for SQL Server}",
        authentication=None,
        encrypt=True,
        trust_server_certificate=True,
    )


def execute_query_from_yaml(
    query_category: str,
    query_name: str,
    params: Optional[tuple] = None,
    azure_db=None,
    sql_server_db=None,
) -> list:
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

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.logger = setup_logger(__name__)

    def close(self):
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
                        f"Attempting Azure SQL connection to {self.database} using SQL authentication"
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
                        f"TrustServerCertificate=no;"
                        "Connection Timeout=30;"
                    )
                    self.logger.info(
                        f"Attempting Azure SQL connection to {self.database} using Azure AD authentication"
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
                self.logger.info(
                    f"Attempting Azure SQL connection to {self.database} using SQL authentication"
                )

            # DEBUG: print connection string (password masked)
            import re as _re
            debug_conn_str = _re.sub(r'(PWD=)[^;]+', r'\1***MASKED***', connection_string)
            self.logger.info(f"[DEBUG] Connection string: {debug_conn_str}")
            print(f"[DEBUG] Connection string: {debug_conn_str}")

            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            self.logger.info(f"Successfully connected to Azure SQL Database: {self.database}")
            return self.connection

        except pyodbc.Error as e:
            self.logger.error(f"Error connecting to Azure SQL Database: {str(e)}")
            raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
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


def get_azure_db_connection(**kwargs) -> AzureSQLDatabase:
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

    if not any(k in kwargs for k in ['server', 'username', 'password']):
        try:
            from utils.settings import settings
            azure_config = settings.config.get('database', {}).get('azure', {})

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
        logger.info(f"✓ {role_normalized} name found for {id_type} {aplid}: {name}")
        return name

    logger.warning(f"No {role_normalized} found for {id_type}: {aplid}")
    return None
