"""Database fixtures in base-branch location.

Provides base-compatible database manager fixtures while preserving local
behavior in repositories that do not yet expose vault-connection helpers.
"""

from collections.abc import Generator
from typing import Any

import pytest

from utils.allure_logger import get_allure_logger
from utils.database import AzureSQLDatabase, get_configured_azure_db, get_configured_sql_server

try:
    # Base branch utility (may not exist in local branch yet).
    from utils.database import get_db_from_vault  # type: ignore
except ImportError:  # pragma: no cover - compatibility path
    get_db_from_vault = None


class DatabaseConnectionManager:
    """Manage database connections with lazy initialization and per-alias cache."""

    def __init__(self):
        self._vault_dbs: dict = {}
        self._logger = get_allure_logger(__name__)

    def _get_fallback_db(self, alias: str):
        """Fallback strategy when vault helper is not available locally."""
        normalized = alias.lower()

        if normalized in {"crm", "sql", "sql_server", "sqlserver"}:
            return get_configured_sql_server()

        # Default to azure DB for transfer/azure style aliases.
        return get_configured_azure_db()

    def get_vault_db(self, alias: str, database: str | None = None):
        """Get a DB connection for alias, using vault helper when available."""
        if alias not in self._vault_dbs:
            if get_db_from_vault is not None:
                db = get_db_from_vault(alias, database=database)
            else:
                db = self._get_fallback_db(alias)

            db.connect()
            self._vault_dbs[alias] = db
            self._logger.info(f"DB connected: {alias}")

        return self._vault_dbs[alias]

    def close_all(self):
        """Close all opened connections."""
        for alias, db in self._vault_dbs.items():
            db.close()
            self._logger.info(f"DB connection closed: {alias}")


class LegacyDBHelper:
    """Compatibility helper kept only to support existing step logic during migration."""

    def __init__(self, db_connection: AzureSQLDatabase | None = None):
        self.db = db_connection
        self._auto_close = db_connection is None
        self._logger = get_allure_logger(__name__)

    def setup_db_connection(self, db_type: str = "sql_server") -> None:
        """Set up database connection by type."""
        if self.db is None:
            if db_type == "sql_server":
                self.db = get_configured_sql_server()
            else:
                self.db = get_configured_azure_db()

            self.db.connect()
            self._logger.info(f"Database connection established: {db_type}")

    def close_db_connection(self) -> None:
        """Close database connection if open."""
        if self.db:
            self.db.close()
            self._logger.info("Database connection closed")

    def execute_query_and_fetch_columns(
        self, query: str, column_name: str, params: tuple | None = None
    ) -> str | None:
        """Execute query and return first value from target column."""
        if not self.db:
            self.setup_db_connection()

        results = self.db.execute_query(query, params)
        if not results:
            self._logger.warning("No results found for query")
            return None

        columns = [desc[0] for desc in self.db.cursor.description]
        if column_name not in columns:
            self._logger.error(f"Column '{column_name}' not found in results. Available: {columns}")
            return None

        col_index = columns.index(column_name)
        value = results[0][col_index] if results[0][col_index] is not None else None
        return str(value).strip() if value is not None else None

    def execute_select_query_and_get_list_as_map(
        self, query: str, params: tuple | None = None
    ) -> list[dict[str, Any]]:
        """Execute select query and return rows as a list of dictionaries."""
        if not self.db:
            self.setup_db_connection()

        results = self.db.execute_query(query, params)
        if not results:
            self._logger.info("Query returned no results")
            return []

        columns = [desc[0] for desc in self.db.cursor.description]
        mapped_results: list[dict[str, Any]] = []
        for row in results:
            mapped_results.append(
                {column: (str(row[idx]) if row[idx] is not None else "") for idx, column in enumerate(columns)}
            )

        self._logger.info(f"Query returned {len(mapped_results)} rows")
        return mapped_results


@pytest.fixture(scope="function")
def db_manager() -> Generator[DatabaseConnectionManager, None, None]:
    """Provide lazy DB manager scoped to the test function."""
    manager = DatabaseConnectionManager()
    yield manager
    manager.close_all()


@pytest.fixture(scope="function")
def db_helper() -> Generator[LegacyDBHelper, None, None]:
    """Provide temporary helper-compatible interface during DB migration."""
    helper = LegacyDBHelper()
    yield helper
    helper.close_db_connection()
