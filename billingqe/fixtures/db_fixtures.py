"""Database fixtures for Billing automation."""

from collections.abc import Generator

import pytest

from utils.database import DatabaseConnectionManager, LegacyDBHelper


@pytest.fixture(scope="function")
def db_manager() -> Generator[DatabaseConnectionManager, None, None]:
    """Provide a lazy DB manager scoped to the test function."""
    manager = DatabaseConnectionManager()
    yield manager
    manager.close_all()


@pytest.fixture(scope="function")
def db_helper() -> Generator[LegacyDBHelper, None, None]:
    """Provide a compatibility DB helper for older step logic."""
    helper = LegacyDBHelper()
    yield helper
    helper.close_db_connection()
"""Database fixture module placeholder.

DB fixtures are not implemented yet for Billing automation.
Add connection/session fixtures here when DB validation is introduced.
"""
