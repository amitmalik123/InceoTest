"""
Database Fixtures

Provides fixtures for database connection management with lazy initialization.
All connections use connection strings from environment variables
(injected by pipeline's AzureKeyVault@2 task or set in .env for local dev).
"""

from collections.abc import Generator

import pytest

from utils.allure_logger import get_allure_logger
from utils.database import get_db_from_vault


class DatabaseConnectionManager:
    """
    Manages database connections with lazy initialization.

    All connections use connection strings from environment variables
    (injected by pipeline or set in .env for local dev).

    Connections are cached per vault alias and automatically closed after test.
    """

    def __init__(self):
        self._vault_dbs: dict = {}  # Cache per vault alias
        self._logger = get_allure_logger(__name__)

    def get_vault_db(self, alias: str, database: str | None = None):
        """Get a connection via vault connection-string, cached per alias."""
        if alias not in self._vault_dbs:
            db = get_db_from_vault(alias, database=database)
            db.connect()
            self._vault_dbs[alias] = db
            self._logger.info(f"Vault DB connected: {alias}")
        return self._vault_dbs[alias]

    def close_all(self):
        """Close all created connections"""
        for alias, db in self._vault_dbs.items():
            db.close()
            self._logger.info(f"Vault DB connection closed: {alias}")


@pytest.fixture(scope="function")
def db_manager() -> Generator[DatabaseConnectionManager, None, None]:
    """
    Database connection manager with lazy initialization and USE switching.
    One connection per server type, switches databases via USE command.
    Connection is reused across multiple queries within the same test.

    Usage:
        def step(db_manager):
            results = execute_query_from_yaml(
                "crm", "retirement_billing_client",
                db_manager=db_manager  # Reuses connection, switches DB via USE
            )
    """
    manager = DatabaseConnectionManager()
    yield manager
    manager.close_all()
