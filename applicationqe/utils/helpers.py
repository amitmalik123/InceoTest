"""
Utility functions for test automation - Generic helpers.

Note: Specialized utilities are in dedicated modules:
- JSON operations: json_utils.py (JSONUtils class)
- CSV operations: csv_utils.py (CSVUtils class)
- Locator operations: pages/base_page.py (BasePage.empty_field())
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from playwright.sync_api import Locator


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

def random_number(length: int = 6) -> str:
    """Generate a random numeric string of given length.

    Args:
        length: Number of digits (default: 6)

    Returns:
        Random numeric string

    Example:
        >>> random_number()       # e.g. '482019'
        >>> random_number(10)     # e.g. '7391042856'
    """
    return "".join(random.choices(string.digits, k=length))


def random_alpha(length: int = 5) -> str:
    """Generate a random alphabetic string of given length.

    Args:
        length: Number of characters (default: 5)

    Returns:
        Random lowercase alphabetic string

    Example:
        >>> random_alpha()        # e.g. 'kxmqt'
        >>> random_alpha(8)       # e.g. 'bwjflrpa'
    """
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_alphanumeric(length: int = 8) -> str:
    """Generate a random alphanumeric string of given length.

    Args:
        length: Number of characters (default: 8)

    Returns:
        Random alphanumeric string

    Example:
        >>> random_alphanumeric()     # e.g. 'k3Xm9Qt2'
        >>> random_alphanumeric(12)   # e.g. 'bW4jFl8rPa1z'
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_locator_attribute(locator, attribute_name: str, element_name: str = "element", timeout: int = 10000):
    """
    Get an attribute value from a Playwright locator.

    Args:
        locator: Playwright Locator object
        attribute_name: HTML attribute to retrieve (e.g. 'value', 'class', 'aria-invalid')
        element_name: Human-readable name for logging purposes
        timeout: Maximum time to wait in milliseconds (default: 10000)

    Returns:
        Attribute value as string, or None if not found
    """
    return locator.get_attribute(attribute_name, timeout=timeout)

