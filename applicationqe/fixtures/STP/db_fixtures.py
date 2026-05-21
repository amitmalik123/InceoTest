"""
Database Fixtures

Provides fixtures for database connection management with lazy initialization.
"""

import pytest

from utils.allure_logger import get_allure_logger
from utils.database import get_configured_azure_db, get_configured_sql_server


class DatabaseConnectionManager:
    """
    Manages database connections with lazy initialization.
    Only creates connections when actually requested.
    Automatically closes all created connections after test.
    """

    def __init__(self):
        self._azure_db = None
        self._sql_server_db = None
        self._logger = get_allure_logger(__name__)

    @property
    def azure_db(self):
        """Get Azure DB connection - created on first access (lazy)"""
        if self._azure_db is None:
            self._azure_db = get_configured_azure_db()
            self._azure_db.connect()
            self._logger.info(f"Azure DB connected: {self._azure_db.database}")
        return self._azure_db

    @property
    def sql_server_db(self):
        """Get SQL Server connection - created on first access (lazy)"""
        if self._sql_server_db is None:
            self._sql_server_db = get_configured_sql_server()
            self._sql_server_db.connect()
            self._logger.info(f"SQL Server connected: {self._sql_server_db.database}")
        return self._sql_server_db

    def close_all(self):
        """Close all created connections"""
        if self._azure_db:
            self._azure_db.close()
            self._logger.info("Azure DB connection closed")
        if self._sql_server_db:
            self._sql_server_db.close()
            self._logger.info("SQL Server connection closed")


@pytest.fixture(scope="function")
def db_manager():
    """
    Database connection manager with lazy initialization.
    Only connects to databases that are actually used.

    Usage:
        def step(db_manager):
            results = execute_query_from_yaml(
                "transfer", "transfer_audit",
                azure_db=db_manager.azure_db  # Connects only if accessed
            )
    """
    manager = DatabaseConnectionManager()
    yield manager
    manager.close_all()
