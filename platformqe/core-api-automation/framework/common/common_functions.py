import json
import os
import re
from typing import Any, Dict, List, Optional, Callable
from .logger import get_logger

logger = get_logger(__name__)

# Function registry for dynamic invocation
_FUNCTION_MAP: Dict[str, Callable] = {}

def register_function(name: str):
    """Decorator to register a function for dynamic invocation."""
    def decorator(func: Callable):
        _FUNCTION_MAP[name] = func
        return func
    return decorator

@register_function('merge_headers')
def merge_headers(headers: Dict[str, str], headers_additional: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Merges common and additional headers for a request."""
    merged = headers.copy() if headers else {}
    if headers_additional:
        merged.update(headers_additional)
    logger.debug(f"Merged headers: {merged}")
    return merged

@register_function('extract_value')
def extract_value(response: Any, key: str, record_count: bool = False, array_path: str = None) -> Any:
    """
    Extracts a value from the response for workflow chaining.
    Supports dot notation and list indexing (e.g., 'users.0.name').
    Supports record counting for arrays in both JSON (REST) and XML (SOAP) responses.
    
    Args:
        response: Response data (dict, list, or XML string/object)
        key: Key path to extract (supports dot notation)
        record_count: If True, returns the count of items in the array at array_path
        array_path: Path to the array whose count should be returned (supports dot notation and Jinja-like paths)
    
    Returns:
        Extracted value, record count, or None if extraction fails
    """
    # Handle record_count mode
    if record_count:
        if array_path:
            return _extract_record_count(response, array_path)
        else:
            # Empty array_path means count the root level array
            if isinstance(response, list):
                count = len(response)
                logger.debug(f"Root level array has {count} items")
                return count
            else:
                logger.warning(f"record_count requested with empty array_path, but response is not a list: {type(response)}")
                return 0
    
    # Regular value extraction
    value = response
    for k in key.split('.'):
        if isinstance(value, dict):
            value = value.get(k)
        elif isinstance(value, list) and k.isdigit():
            index = int(k)
            value = value[index] if index < len(value) else None
        else:
            logger.warning(f"Failed to extract '{key}' from response.")
            return None
    logger.debug(f"Extracted value for '{key}': {value}")
    return value


def _extract_record_count(response: Any, array_path: str) -> int:
    """
    Extracts record count from an array in the response.
    Works for both JSON (REST) and XML (SOAP) responses.
    
    Args:
        response: Response data (dict, list, XML string, or XML object)
        array_path: Path to the array (supports dot notation, e.g., 'users', 'data.items', 'Body.Response.Users')
    
    Returns:
        Count of items in the array, or 0 if array not found
    """
    try:
        # Check if response is SOAP/XML (string or XML object)
        if isinstance(response, str) and response.strip().startswith('<'):
            return _count_xml_elements(response, array_path)
        elif hasattr(response, 'tag'):  # lxml Element
            return _count_xml_elements_from_element(response, array_path)
        
        # Check if response is a dict with xml_response (SOAP client format)
        if isinstance(response, dict) and 'xml_response' in response:
            return _count_xml_elements(response['xml_response'], array_path)
        
        # Handle JSON/dict response (REST)
        return _count_json_array(response, array_path)
        
    except Exception as e:
        logger.warning(f"Failed to extract record count from '{array_path}': {e}")
        return 0


def _count_json_array(response: Any, array_path: str) -> int:
    """
    Count items in a JSON array using dot notation path.
    
    Args:
        response: JSON response (dict or list)
        array_path: Path to array (e.g., 'users', 'data.items', 'response.data.users')
    
    Returns:
        Count of items in array
    """
    value = response
    path_parts = array_path.split('.')
    
    for part in path_parts:
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            index = int(part)
            value = value[index] if index < len(value) else None
        else:
            logger.warning(f"Failed to navigate to '{array_path}' in JSON response")
            return 0
        
        if value is None:
            logger.warning(f"Path '{array_path}' not found in JSON response")
            return 0
    
    # Count the array
    if isinstance(value, list):
        count = len(value)
        logger.debug(f"JSON array at '{array_path}' has {count} items")
        return count
    else:
        logger.warning(f"Path '{array_path}' does not point to an array in JSON response")
        return 0


def _count_xml_elements(xml_content: str, array_path: str) -> int:
    """
    Count XML elements in SOAP/XML response using path.
    
    Args:
        xml_content: XML content as string
        array_path: Path to array elements (e.g., 'Body.Response.Users.User', '//User')
    
    Returns:
        Count of matching XML elements
    """
    try:
        from lxml import etree
        
        # Parse XML
        root = etree.fromstring(xml_content.encode('utf-8') if isinstance(xml_content, str) else xml_content)
        return _count_xml_elements_from_element(root, array_path)
        
    except Exception as e:
        logger.error(f"Failed to parse XML for record count: {e}")
        return 0


def _count_xml_elements_from_element(root, array_path: str) -> int:
    """
    Count XML elements from an lxml Element using path.
    
    Args:
        root: lxml Element root
        array_path: Path to array elements (supports XPath or dot notation)
    
    Returns:
        Count of matching XML elements
    """
    try:
        # If array_path starts with '//', treat as XPath
        if array_path.startswith('//') or array_path.startswith('/'):
            elements = root.xpath(array_path)
            count = len(elements)
            logger.debug(f"XML XPath '{array_path}' matched {count} elements")
            return count
        
        # Otherwise, use dot notation (navigate through elements)
        path_parts = array_path.split('.')
        current = root
        
        for part in path_parts:
            # Find child elements with this tag name (ignoring namespaces)
            children = current.findall(f".//*[local-name()='{part}']")
            
            if not children:
                # Try direct child
                children = [child for child in current if child.tag.endswith(part) or child.tag.split('}')[-1] == part]
            
            if not children:
                logger.warning(f"XML path part '{part}' not found in path '{array_path}'")
                return 0
            
            # If this is the last part, count all matching elements
            if part == path_parts[-1]:
                count = len(children)
                logger.debug(f"XML array at '{array_path}' has {count} items")
                return count
            else:
                # Move to first matching child for next iteration
                current = children[0]
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to count XML elements at '{array_path}': {e}")
        return 0


@register_function('validate_user_role')
def validate_user_role(role: str, allowed_roles: Optional[List[str]] = None) -> bool:
    """Checks if role is one of allowed values."""
    if allowed_roles is None:
        allowed_roles = ['admin', 'user', 'guest']
    result = role in allowed_roles
    logger.debug(f"Role '{role}' validation result: {result}")
    return result

def invoke_common_function(function_name: str, *args, **kwargs) -> Any:
    """
    Dynamically invoke a registered common function by name.
    """
    func = _FUNCTION_MAP.get(function_name)
    if not func:
        raise ValueError(f"Function '{function_name}' not implemented.")
    logger.info(f"Invoking function '{function_name}' with args={args}, kwargs={kwargs}")
    return func(*args, **kwargs)

def list_common_functions() -> List[str]:
    """Returns a list of registered common function names."""
    return list(_FUNCTION_MAP.keys())

# Optional: Add a test harness for demonstration
if __name__ == "__main__":
    from framework.common.logger import get_logger
    logger = get_logger(__name__)
    logger.info("--- Demo: merge_headers ---")
    h1 = {"Authorization": "Bearer token"}
    h2 = {"Content-Type": "application/json"}
    logger.info(invoke_common_function("merge_headers", h1, h2))

    logger.info("--- Demo: extract_value ---")
    resp = {"user": {"id": 123, "name": "Alice"}, "users": [{"name": "Bob"}, {"name": "Carol"}]}
    logger.info(invoke_common_function("extract_value", resp, "user.id"))
    logger.info(invoke_common_function("extract_value", resp, "users.1.name"))

    logger.info("--- Demo: validate_user_role ---")
    logger.info(invoke_common_function("validate_user_role", "admin"))
    logger.info(invoke_common_function("validate_user_role", "guest"))
    logger.info(invoke_common_function("validate_user_role", "invalid"))

    logger.info("--- Registered Functions ---")
    logger.info(list_common_functions())
