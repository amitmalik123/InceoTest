"""Database utilities for Billing automation.

This module supports local credentials today and can adopt Azure Key Vault
connection strings later without changing test code.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import pyodbc
import yaml

from utils.logger import setup_logger


logger = setup_logger(__name__)

RESTRICTED_ENVS = {"prod", "production", "silo"}
DEFAULT_DRIVER = "{ODBC Driver 17 for SQL Server}"
DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "billing"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
    / "env.qa.yaml"
)
DEFAULT_LOCAL_CONFIG_PATH = DEFAULT_CONFIG_PATH.with_name("env.qa.local.yaml")
DEFAULT_SQL_QUERIES_PATH = (
    Path(__file__).resolve().parent.parent
    / "queries"
    / "billing"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
    / "sgm_sql_queries.yaml"
)


def _get_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return ""


def _load_config() -> dict[str, Any]:
    explicit_config = os.getenv("TEST_CONFIG_PATH")

    if explicit_config:
        config_path = Path(explicit_config)
        if not config_path.exists():
            return {}
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    merged: dict[str, Any] = {}

    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as file:
            merged = yaml.safe_load(file) or {}

    if DEFAULT_LOCAL_CONFIG_PATH.exists():
        with open(DEFAULT_LOCAL_CONFIG_PATH, "r", encoding="utf-8") as file:
            local_config = yaml.safe_load(file) or {}
        merged = _deep_merge_dicts(merged, local_config)

    return merged


def _deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _get_db_section() -> dict[str, Any]:
    config = _load_config()
    return config.get("database", {}) if isinstance(config, dict) else {}


def get_sql_query(query_name: str, query_file: str | Path | None = None) -> str:
    """Load a named SQL query from the Billing SGM query YAML file."""
    sql_query_path = Path(query_file) if query_file else DEFAULT_SQL_QUERIES_PATH
    queries = _load_yaml_file(sql_query_path)

    if not queries:
        raise FileNotFoundError(f"SQL query file not found or empty: {sql_query_path}")

    query = queries.get(query_name)
    if not isinstance(query, str) or not query.strip():
        available_queries = ", ".join(sorted(queries.keys()))
        raise KeyError(
            f"SQL query '{query_name}' was not found in {sql_query_path}. Available queries: {available_queries}"
        )

    return query.strip()


def _check_environment_safety() -> None:
    env_name = os.getenv("TEST_ENV", "test11").lower()
    if env_name in RESTRICTED_ENVS:
        raise PermissionError(
            f"Database connections are blocked for '{env_name}'. Use a test, qa, or dev environment."
        )


def parse_connection_string(conn_str: str) -> dict[str, str]:
    """Parse an ADO.NET / ODBC-style connection string into key-value pairs."""
    parsed: dict[str, str] = {}
    for part in conn_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        parsed[key.strip().lower()] = value.strip()
    return parsed


def _build_database(
    *,
    server: str,
    database: str,
    username: str = "",
    password: str = "",
    driver: str = DEFAULT_DRIVER,
    authentication: str | None = None,
    encrypt: bool = True,
    trust_server_certificate: bool = True,
) -> "SQLDatabase":
    return SQLDatabase(
        server=server,
        database=database,
        username=username,
        password=password,
        driver=driver,
        authentication=authentication,
        encrypt=encrypt,
        trust_server_certificate=trust_server_certificate,
    )


def get_configured_azure_db() -> "SQLDatabase":
    """Return an Azure SQL database connection using local config or environment variables."""
    _check_environment_safety()
    db_config = _get_db_section().get("azure", {}) if _get_db_section() else {}

    server = _get_env("BILLING_AZURE_DB_SERVER", "BILLING_DB_SERVER") or db_config.get("server", "")
    database = _get_env("BILLING_AZURE_DB_NAME", "BILLING_DB_NAME") or db_config.get("database", "")
    username = _get_env("BILLING_AZURE_DB_USERNAME", "BILLING_DB_USERNAME") or db_config.get("username", "")
    password = _get_env("BILLING_AZURE_DB_PASSWORD", "BILLING_DB_PASSWORD") or db_config.get("password", "")
    driver = _get_env("BILLING_AZURE_DB_DRIVER", "BILLING_DB_DRIVER") or db_config.get(
        "driver", DEFAULT_DRIVER
    )
    authentication = _get_env("BILLING_AZURE_DB_AUTHENTICATION", "BILLING_DB_AUTHENTICATION") or db_config.get(
        "authentication"
    )

    return _build_database(
        server=server,
        database=database,
        username=username,
        password=password,
        driver=driver,
        authentication=authentication,
    )


def get_configured_sql_server() -> "SQLDatabase":
    """Return a SQL Server connection using local config or environment variables."""
    _check_environment_safety()
    db_config = _get_db_section().get("sql_server", {}) if _get_db_section() else {}

    server = _get_env("BILLING_SQL_SERVER", "BILLING_DB_SERVER") or db_config.get("server", "")
    database = _get_env("BILLING_SQL_DATABASE", "BILLING_DB_NAME") or db_config.get("database", "")
    username = _get_env("BILLING_SQL_USERNAME", "BILLING_DB_USERNAME") or db_config.get("username", "")
    password = _get_env("BILLING_SQL_PASSWORD", "BILLING_DB_PASSWORD") or db_config.get("password", "")
    driver = _get_env("BILLING_SQL_DRIVER", "BILLING_DB_DRIVER") or db_config.get(
        "driver", DEFAULT_DRIVER
    )

    return _build_database(
        server=server,
        database=database,
        username=username,
        password=password,
        driver=driver,
    )


def get_db_from_connection_string(conn_str: str, database: str | None = None) -> "SQLDatabase":
    """Create a database connection from a full connection string."""
    parsed = parse_connection_string(conn_str)
    server = parsed.get("server") or parsed.get("data source") or parsed.get("host", "")
    resolved_database = database or parsed.get("database") or parsed.get("initial catalog", "")
    username = parsed.get("user id") or parsed.get("uid") or parsed.get("user", "")
    password = parsed.get("password") or parsed.get("pwd", "")
    driver = parsed.get("driver", DEFAULT_DRIVER)
    authentication = parsed.get("authentication")

    return _build_database(
        server=server,
        database=resolved_database,
        username=username,
        password=password,
        driver=driver,
        authentication=authentication,
    )


def get_db_from_vault(alias: str, database: str | None = None) -> "SQLDatabase":
    """Resolve a database connection string from env vars, with local fallback.

    This keeps the API Key Vault-friendly without requiring Key Vault today.
    """
    _check_environment_safety()
    alias_key = alias.upper().replace("-", "_")
    conn_str = _get_env(
        f"{alias_key}_DB_CONNECTION_STRING",
        f"{alias_key}_CONNECTION_STRING",
        f"{alias_key}_CONN_STRING",
    )

    if conn_str:
        logger.info("Resolved database connection string for alias '%s'", alias)
        return get_db_from_connection_string(conn_str, database=database)

    alias_lower = alias.lower()
    if alias_lower in {"sql", "sql_server", "sqlserver", "crm"}:
        logger.info("Falling back to local SQL Server configuration for alias '%s'", alias)
        return get_configured_sql_server()

    logger.info("Falling back to local Azure SQL configuration for alias '%s'", alias)
    return get_configured_azure_db()


class DatabaseConnection:
    """Base class for database connections."""

    def __init__(self) -> None:
        self.connection = None
        self.cursor = None
        self.logger = setup_logger(__name__)

    def close(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SQLDatabase(DatabaseConnection):
    """SQL Database connection utility for Azure SQL and SQL Server."""

    def __init__(
        self,
        server: str = "",
        database: str = "",
        username: str = "",
        password: str = "",
        driver: str = DEFAULT_DRIVER,
        authentication: str | None = None,
        encrypt: bool = True,
        trust_server_certificate: bool = True,
    ) -> None:
        super().__init__()
        self.server = server or os.getenv("SQL_DB_SERVER", "")
        self.database = database or os.getenv("SQL_DB_DATABASE", "")
        self.username = username or os.getenv("SQL_DB_USERNAME", "")
        self.password = password or os.getenv("SQL_DB_PASSWORD", "")
        self.driver = driver
        self.authentication = authentication
        self.encrypt = encrypt
        self.trust_server_certificate = trust_server_certificate

    def _normalize_driver_name(self, driver: str) -> str:
        return str(driver or "").strip().strip("{}").strip()

    def _pick_fallback_sql_driver(self) -> str | None:
        available_drivers = [str(d).strip() for d in pyodbc.drivers()]
        if not available_drivers:
            return None

        preferred = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "SQL Server",
        ]
        for candidate in preferred:
            if candidate in available_drivers:
                return "{" + candidate + "}"
        return None

    def _build_connection_string(self) -> str:
        if not self.server or not self.database:
            raise ValueError("Database server and database name must be configured before connecting.")

        parts = [
            f"DRIVER={self.driver}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
            f"UID={self.username}",
            f"PWD={self.password}",
        ]

        if self.authentication:
            parts.append(f"Authentication={self.authentication}")

        if self.encrypt:
            parts.append("Encrypt=yes")
        if self.trust_server_certificate:
            parts.append("TrustServerCertificate=yes")

        parts.append("Connection Timeout=30")
        return ";".join(parts) + ";"

    def connect(self):
        """Establish a connection to the database."""
        connection_string = self._build_connection_string()
        masked_string = connection_string.replace(self.password, "****") if self.password else connection_string
        self.logger.info("Connecting to database %s on %s", self.database, self.server)
        self.logger.info("Connection string: %s", masked_string)

        try:
            self.connection = pyodbc.connect(connection_string)
        except pyodbc.InterfaceError as exc:
            # IM002 usually means the configured ODBC driver is not installed.
            if "IM002" not in str(exc):
                raise

            configured_driver = self._normalize_driver_name(self.driver)
            fallback_driver = self._pick_fallback_sql_driver()
            if not fallback_driver:
                raise

            fallback_driver_name = self._normalize_driver_name(fallback_driver)
            if fallback_driver_name == configured_driver:
                raise

            self.logger.warning(
                "Configured SQL driver '%s' not available. Falling back to '%s'.",
                configured_driver,
                fallback_driver_name,
            )

            self.driver = fallback_driver
            retry_connection_string = self._build_connection_string()
            retry_masked = (
                retry_connection_string.replace(self.password, "****")
                if self.password
                else retry_connection_string
            )
            self.logger.info("Retrying DB connection with fallback driver. Connection string: %s", retry_masked)
            self.connection = pyodbc.connect(retry_connection_string)

        self.cursor = self.connection.cursor()
        return self.connection

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[dict[str, Any]]:
        """Execute a SELECT query and return rows as dictionaries."""
        if not self.connection:
            self.connect()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        columns = [column[0] for column in self.cursor.description]
        rows = self.cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        self.logger.info("Query executed successfully. Rows returned: %d", len(results))
        return results

    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        _check_environment_safety()

        if not self.connection:
            self.connect()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        self.connection.commit()
        rows_affected = self.cursor.rowcount
        self.logger.info("Query executed successfully. Rows affected: %d", rows_affected)
        return rows_affected

    def execute_query_and_get_first_value(self, query: str, column_name: str, params=None):
        """Execute a query and return the first value for the requested column."""
        results = self.execute_query(query, params)
        if not results:
            self.logger.warning("No results found for query")
            return None

        first_row = results[0]
        value = first_row.get(column_name)
        return str(value) if value is not None else None

    def execute_select_query_and_get_string_list(
        self,
        query: str,
        column_name: str,
        records_count: int | None = None,
        params=None,
    ) -> list[str]:
        """Execute a query and return a list of string values from the requested column."""
        results = self.execute_query(query, params)
        values: list[str] = []

        for row in results:
            value = row.get(column_name)
            values.append(str(value) if value is not None else "")
            if records_count is not None and len(values) >= records_count:
                break

        self.logger.info("Query completed on %s. Retrieved %d values", column_name, len(values))
        return values


class AzureSQLDatabase(SQLDatabase):
    """Backward-compatible class name for Azure SQL callers."""


class DatabaseConnectionManager:
    """Manage cached database connections by alias."""

    def __init__(self) -> None:
        self._connections: dict[str, SQLDatabase] = {}
        self._logger = setup_logger(__name__)

    def get_vault_db(self, alias: str, database: str | None = None) -> SQLDatabase:
        """Get or create a database connection for the given alias."""
        cache_key = f"{alias}:{database or ''}"
        if cache_key not in self._connections:
            db = get_db_from_vault(alias, database=database)
            db.connect()
            self._connections[cache_key] = db
            self._logger.info("DB connected: %s", alias)

        return self._connections[cache_key]

    def close_all(self) -> None:
        """Close all cached database connections."""
        cached_connections = tuple(self._connections.items())
        for alias, db in cached_connections:
            try:
                db.close()
                self._logger.info("DB connection closed: %s", alias)
            except Exception as exc:  # pragma: no cover - best effort cleanup
                self._logger.warning("Failed to close DB connection '%s': %s", alias, exc)
        self._connections.clear()


class LegacyDBHelper:
    """Compatibility helper for existing step logic during DB migration."""

    def __init__(self, db_connection: SQLDatabase | None = None) -> None:
        self.db = db_connection
        self._logger = setup_logger(__name__)

    def setup_db_connection(self, db_type: str = "sql_server") -> None:
        """Set up a DB connection by type."""
        if self.db is not None:
            return

        if db_type == "azure":
            self.db = get_configured_azure_db()
        else:
            self.db = get_configured_sql_server()

        self.db.connect()
        self._logger.info("Database connection established: %s", db_type)

    def close_db_connection(self) -> None:
        """Close the DB connection if one is open."""
        if self.db:
            self.db.close()
            self._logger.info("Database connection closed")

    def execute_query_and_fetch_columns(
        self, query: str, column_name: str, params: tuple | None = None
    ) -> str | None:
        """Execute a query and return the first value from a target column."""
        if not self.db:
            self.setup_db_connection()

        db = self.db
        assert db is not None

        results = db.execute_query(query, params)
        if not results:
            self._logger.warning("No results found for query")
            return None

        value = results[0].get(column_name)
        if value is None:
            self._logger.warning("Column '%s' not found or null in query results", column_name)
            return None

        return str(value).strip()

    def execute_select_query_and_get_list_as_map(
        self, query: str, params: tuple | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query and return rows as dictionaries."""
        if not self.db:
            self.setup_db_connection()

        db = self.db
        assert db is not None

        results = db.execute_query(query, params)
        if not results:
            self._logger.info("Query returned no results")
            return []

        mapped_results: list[dict[str, Any]] = []
        for row in results:
            mapped_results.append(
                {column: ("" if value is None else str(value)) for column, value in row.items()}
            )

        self._logger.info("Query returned %d rows", len(mapped_results))
        return mapped_results
