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
def extract_value(response: Any, key: str) -> Any:
    """
    Extracts a value from the response for workflow chaining.
    Supports dot notation and list indexing (e.g., 'users.0.name').
    """
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
