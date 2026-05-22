"""
Test Data Fixtures

Provides fixtures for loading and managing test data with scalable query capabilities.
"""

import csv
from typing import Dict, List, Optional

import pytest

from utils.settings import settings


class TestDataManager:
    """
    Scalable test data manager with flexible query capabilities.

    Query by ANY field, filter multiple rows, and easily access test data.
    """

    def __init__(self, data_rows: List[Dict[str, str]]):
        """Initialize with all CSV rows"""
        self._data = data_rows

    def get_by(self, **criteria) -> Optional[Dict[str, str]]:
        """
        Get FIRST row matching ALL criteria.

        Args:
            **criteria: Field-value pairs to match

        Returns:
            dict: First matching row, or None

        Examples:
            data.get_by(test_scenario="add_ach")
            data.get_by(user_type="advisor", test_scenario="add_ach")
            data.get_by(username="T11_User2_Test")
        """
        for row in self._data:
            if all(row.get(key) == value for key, value in criteria.items()):
                return row
        return None

    def filter_by(self, **criteria) -> List[Dict[str, str]]:
        """
        Get ALL rows matching ALL criteria.

        Args:
            **criteria: Field-value pairs to match

        Returns:
            list[dict]: All matching rows

        Examples:
            data.filter_by(user_type="advisor")  # All advisor users
            data.filter_by(test_scenario="roth_conversion")
        """
        matches = []
        for row in self._data:
            if all(row.get(key) == value for key, value in criteria.items()):
                matches.append(row)
        return matches

    def get_all(self) -> List[Dict[str, str]]:
        """Get all test data rows"""
        return self._data

    def get_scenarios(self) -> List[str]:
        """Get list of unique test scenarios"""
        return list(
            set(row.get("test_scenario", "") for row in self._data if row.get("test_scenario"))
        )

    def get_user_types(self) -> List[str]:
        """Get list of unique user types"""
        return list(set(row.get("user_type", "") for row in self._data if row.get("user_type")))

    def __len__(self):
        """Return number of data rows"""
        return len(self._data)

    def __getitem__(self, index):
        """Allow indexing: data[0], data[1], etc."""
        return self._data[index]


# NOTE: test_context fixture moved to tests/bdd/steps/conftest.py
# to properly include test_data. Do not redefine here.


@pytest.fixture(scope="session")
def test_data_manager():
    """
    Scalable test data manager (session scope - loaded once).

    Returns:
        TestDataManager: Manager with query capabilities

    Examples:
        # Get by any field
        data.get_by(test_scenario="add_ach")
        data.get_by(user_type="advisor")
        data.get_by(username="T11_User2_Test")

        # Filter multiple rows
        advisors = data.filter_by(user_type="advisor")

        # Get all scenarios
        scenarios = data.get_scenarios()
    """
    from utils.logger import setup_logger

    logger = setup_logger(__name__)
    csv_path = settings.test_data_csv
    logger.info(f"[SESSION SCOPE] Loading test data from: {csv_path}")

    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        data_rows = list(reader)

    logger.info(f"[SESSION SCOPE] Loaded {len(data_rows)} test data row(s)")

    # Show available scenarios and user types
    manager = TestDataManager(data_rows)
    logger.info(f"[SESSION SCOPE] Available scenarios: {manager.get_scenarios()}")
    logger.info(f"[SESSION SCOPE] Available user types: {manager.get_user_types()}")

    return manager


@pytest.fixture(scope="session")
def test_data(test_data_manager):
    """
    Get first row of test data (backward compatibility).

    Returns:
        dict: First row of test data

    Example:
        def test_example(test_data):
            username = test_data.get('username')
    """
    return test_data_manager[0] if len(test_data_manager) > 0 else {}
