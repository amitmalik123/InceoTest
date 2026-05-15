"""
Address Comparison Utilities

Provides helper functions for comparing addresses between arrays and web elements.
Used primarily for Address Change feature validation.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def check_if_array_contains_text(address_array: List[str], text: str) -> bool:
    """
    Check if any element from the address array appears in the given text.
    
    Performs case-insensitive comparison with normalization:
    - Converts both to uppercase
    - Handles hyphens/dashes
    - Trims whitespace
    
    Args:
        address_array: List of address components (street, city, state, zip, etc.)
        text: Text to search within (e.g., full address string from UI)
        
    Returns:
        True if all non-empty address array elements are found in text, False otherwise
        
    Example:
        address_array = ["123 Main St", "Boston", "MA", "02101"]
        text = "123 Main St, Boston, MA 02101"
        result = check_if_array_contains_text(address_array, text)  # Returns True
    """
    if not address_array:
        logger.warning("Empty address array provided")
        return False
    
    if not text:
        logger.warning("Empty text provided")
        return False
    
    # Normalize text for comparison
    normalized_text = text.upper().strip()
    if '-' in normalized_text:
        normalized_text = normalized_text.replace('-', ' ')
    
    matched_count = 0
    total_items = 0
    
    for address_item in address_array:
        # Skip empty items
        if not address_item or address_item.strip() == "":
            continue
        
        total_items += 1
        
        # Normalize address item
        normalized_item = address_item.upper().strip()
        if '-' in normalized_item:
            normalized_item = normalized_item.replace('-', ' ')
        
        # Check if item appears in text
        if normalized_item in normalized_text or normalized_text in normalized_item:
            matched_count += 1
            logger.debug(f"[OK] Found address component: '{address_item}'")
        else:
            logger.debug(f"[FAIL] Address component not found: '{address_item}'")
    
    result = matched_count == total_items and total_items > 0
    
    logger.info(f"Address match result: {matched_count}/{total_items} components matched - {result}")
    
    return result


def check_if_there_is_address_match(address_items: List[str], address_lines: List[str]) -> bool:
    """
    Match address array elements with list of address line strings.
    
    Compares an array of expected address components against actual address lines
    from the UI. Handles normalization for hyphens, case, and whitespace.
    
    Args:
        address_items: List of expected address components (e.g., ["123 Main St", "Boston", "MA", "02101"])
        address_lines: List of actual address line strings from UI
        
    Returns:
        True if all non-empty address items are found in the address lines, False otherwise
        
    Example:
        address_items = ["123 Main St", "Boston", "MA 02101"]
        address_lines = ["123 Main St", "Boston, MA 02101"]
        result = check_if_there_is_address_match(address_items, address_lines)  # Returns True
    """
    if not address_items:
        logger.warning("Empty address_items provided")
        return False
    
    if not address_lines:
        logger.warning("Empty address_lines provided")
        return False
    
    # Filter out empty items
    filtered_items = [item for item in address_items if item and item.strip() != ""]
    
    if not filtered_items:
        logger.warning("All address items were empty after filtering")
        return False
    
    matched = 0
    to_match = len(filtered_items)
    
    for original_addr_item in filtered_items:
        # Normalize the original item
        item_normalized = original_addr_item.strip().upper()
        if '-' in item_normalized:
            item_normalized = item_normalized.replace('-', ' ')
        
        # Check against each address line
        for line_text in address_lines:
            line_normalized = line_text.strip().upper()
            if '-' in line_normalized:
                line_normalized = line_normalized.replace('-', ' ')
            
            # Check for match (item contains line, line contains item, or exact match)
            if (item_normalized in line_normalized or 
                line_normalized in item_normalized or 
                line_normalized == item_normalized):
                matched += 1
                logger.debug(f"[OK] Matched address component: '{original_addr_item}' with line: '{line_text}'")
                break
        else:
            logger.debug(f"[FAIL] No match found for address component: '{original_addr_item}'")
    
    result = matched == to_match
    
    logger.info(f"Address line match result: {matched}/{to_match} components matched - {result}")
    
    return result


def compare_address_arrays(array1: List[str], array2: List[str]) -> bool:
    """
    Compare two address arrays for equality.
    
    Performs normalized comparison to check if two address arrays are the same.
    
    Args:
        array1: First address array
        array2: Second address array
        
    Returns:
        True if arrays are different (for before/after comparison), False if same
    """
    if not array1 or not array2:
        return True  # Consider different if either is empty
    
    # Filter and normalize both arrays
    filtered1 = [item.strip().upper().replace('-', ' ') for item in array1 if item and item.strip()]
    filtered2 = [item.strip().upper().replace('-', ' ') for item in array2 if item and item.strip()]
    
    if len(filtered1) != len(filtered2):
        return True  # Different lengths = different addresses
    
    # Sort both arrays for comparison
    sorted1 = sorted(filtered1)
    sorted2 = sorted(filtered2)
    
    are_same = sorted1 == sorted2
    
    logger.info(f"Address arrays comparison - Are same: {are_same}")
    
    return not are_same  # Return True if different (for before/after validation)


def get_current_date(format_string: str = "MM/dd/yyyy") -> str:
    """
    Get current date formatted according to the specified format.
    
    Args:
        format_string: Date format string (default: "MM/dd/yyyy")
        
    Returns:
        Formatted current date string
    """
    from datetime import datetime
    
    # Convert Java-style format to Python strftime format
    python_format = format_string.replace("MM", "%m").replace("dd", "%d").replace("yyyy", "%Y")
    
    return datetime.now().strftime(python_format)


def if_two_arrays_same(array1: List[str], array2: List[str]) -> bool:
   
    if array1 is None and array2 is None:
        return True
    
    if array1 is None or array2 is None:
        return False
    
    if len(array1) != len(array2):
        return False
    
    for i in range(len(array1)):
        if array1[i] != array2[i]:
            return False
    
    return True
