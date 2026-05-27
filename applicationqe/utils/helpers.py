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

def find_element_position_in_parent(
    parent_locator: Locator,
    search_attribute: str,
    search_value: str,
) -> Optional[int]:
    """
    Find position of element in parent by attribute value.

    Args:
        parent_locator: Parent locator containing child elements
        search_attribute: Attribute name to search ('value', 'id', 'class', etc)
        search_value: Attribute value to match

    Returns:
        Position index (0-based) or None if not found

    Example:
        # Find position of input with value='radiobtnNo'
        pos = find_element_position_in_parent(
            second_td.locator("input"),
            "value",
            "radiobtnNo"
        )
    """
    all_elements = parent_locator.all()
    for i, elem in enumerate(all_elements):
        attr_value = elem.get_attribute(search_attribute)
        if attr_value == search_value:
            return i
    return None


def get_locator_attribute(
    locator: Locator,
    attribute_name: str,
    element_name: str = "element",
    timeout: int = 5000,
    handle_none_as_empty: bool = True,
) -> Optional[str]:
    """
    Get attribute value from a Playwright locator with logging and error handling.
    
    Waits for the element to be attached to DOM, then retrieves the attribute value.
    Useful for consistently fetching attributes across page objects with unified logging.
    
    Args:
        locator: Playwright Locator to fetch attribute from
        attribute_name: Name of the attribute to get (e.g., 'aria-invalid', 'class', 'data-qa')
        element_name: Human-readable element name for logging (default: 'element')
        timeout: Wait timeout in milliseconds (default: 5000)
        handle_none_as_empty: Convert None attribute values to empty string (default: True)
        
    Returns:
        Attribute value as string, or empty string if None and handle_none_as_empty=True,
        or None if handle_none_as_empty=False
        
    Raises:
        PlaywrightTimeoutError: If element not found within timeout
        
    Example:
        # Get aria-invalid attribute from signature button
        aria_invalid = get_locator_attribute(
            locator=sig_button,
            attribute_name='aria-invalid',
            element_name='signature button'
        )
        # Returns: "false" or "" if not set
        
        # Get class from parent div
        parent_class = get_locator_attribute(
            locator=parent_div,
            attribute_name='class',
            element_name='parent div'
        )
    """
    logger.debug(f"Waiting for {element_name} to be attached to DOM...")
    
    try:
        # Wait for element to be attached to DOM
        locator.wait_for(state='attached', timeout=timeout)
        logger.debug(f"✓ {element_name} found in DOM")
        
        # Get the attribute value
        logger.debug(f"Fetching '{attribute_name}' attribute from {element_name}...")
        attr_value = locator.get_attribute(attribute_name)
        
        # Handle None value
        if attr_value is None:
            if handle_none_as_empty:
                logger.debug(f"Attribute '{attribute_name}' not found on {element_name}, returning empty string")
                return ""
            else:
                logger.warning(f"Attribute '{attribute_name}' is None on {element_name}")
                return None
        
        # Log and return the value
        logger.debug(f"✓ Attribute '{attribute_name}' retrieved: '{attr_value}'")
        return attr_value
        
    except Exception as e:
        logger.error(f"✗ Failed to get attribute '{attribute_name}' from {element_name}: {e}")
        raise
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

