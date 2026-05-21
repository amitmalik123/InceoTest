"""
Utility functions for test automation - Generic helpers.

Note: Specialized utilities are in dedicated modules:
- JSON operations: json_utils.py (JSONUtils class)
- CSV operations: csv_utils.py (CSVUtils class)
- Locator operations: pages/base_page.py (BasePage.empty_field())
"""

import os
from datetime import datetime
from typing import Any, Dict


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as string.

    Args:
        format: strftime format string (default: YYYYMMDD_HHMMSS)

    Returns:
        Formatted timestamp string

    Example:
        >>> get_timestamp()
        '20260107_143022'
        >>> get_timestamp("%Y-%m-%d")
        '2026-01-07'
    """
    return datetime.now().strftime(format)


def ensure_directory_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist (including parent directories).

    Args:
        directory: Path to directory to create

    Example:
        >>> ensure_directory_exists("reports/allure-results")
        # Creates reports/ and reports/allure-results/ if needed
    """
    os.makedirs(directory, exist_ok=True)


def generate_test_data(template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test data based on template.

    Args:
        template: Template dictionary to copy

    Returns:
        Copy of template with potential modifications

    Note:
        Extend this function with custom test data generation logic
        (e.g., random values, unique IDs, timestamps)
    """
    # Add your custom test data generation logic here
    # Examples:
    # - Add unique IDs: data['unique_id'] = str(uuid.uuid4())
    # - Add timestamps: data['created_at'] = get_timestamp()
    # - Randomize values: data['email'] = f"test_{random.randint(1000,9999)}@test.com"
    return template.copy()
