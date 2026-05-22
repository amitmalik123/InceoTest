"""
Base Validator Interface

Defines the standard interface that custom validator scripts should implement
for integration with the test framework's script execution system.

Custom validators can either:
1. Inherit from BaseValidator class and override validate() method
2. Implement a standalone 'validate' function with the same signature
3. Return results in the standard ScriptResult format

Example usage:

    from framework.validators.base_validator import BaseValidator, ScriptResult, ScriptContext
    
    class MyCustomValidator(BaseValidator):
        def validate(self, context: ScriptContext) -> ScriptResult:
            # Custom validation logic
            errors = []
            extracted = {}
            
            # Access test context
            response = context.response.body
            payload = context.test_case.get('payload')
            db_results = context.db_results
            
            # Perform validation
            if response.get('status') != 'success':
                errors.append('Expected success status')
            
            # Extract values for use in assertions
            extracted['transaction_id'] = response.get('id')
            
            return ScriptResult(
                success=len(errors) == 0,
                errors=errors,
                extracted_values=extracted
            )
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Re-export from script_executor for convenience
from framework.validators.script_executor import (
    ScriptContext,
    ScriptResult,
    RequestContext,
    ResponseContext
)


class BaseValidator(ABC):
    """
    Abstract base class for custom validators.
    
    Inherit from this class to create type-safe validators with full IDE support.
    The validate() method receives full test context and should return ScriptResult.
    """
    
    @abstractmethod
    def validate(self, context: ScriptContext) -> ScriptResult:
        """
        Execute validation logic with provided test context.
        
        Args:
            context: ScriptContext containing test case, request, response, 
                    db_results, extracted_vars, and config
        
        Returns:
            ScriptResult with validation outcome and any extracted values
        """
        pass
    
    def extract_value(self, data: Any, path: str, default: Any = None) -> Any:
        """
        Helper to extract nested value using dot notation.
        
        Args:
            data: Source data (dict or list)
            path: Dot-separated path (e.g., 'results.0.value')
            default: Default value if path not found
        
        Returns:
            Extracted value or default
        """
        if not data or not path:
            return default
        
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else None
                except (ValueError, TypeError):
                    return default
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def compare_values(
        self, 
        actual: Any, 
        expected: Any, 
        field_name: str = "",
        tolerance: float = 0.0001
    ) -> tuple:
        """
        Compare two values with optional tolerance for floating point numbers.
        
        Args:
            actual: Actual value from response
            expected: Expected/computed value
            field_name: Name for error messages
            tolerance: Relative tolerance for float comparison
        
        Returns:
            Tuple of (is_match: bool, error_message: Optional[str])
        """
        if actual is None and expected is None:
            return True, None
        
        if actual is None:
            return False, f"{field_name} missing (expected: {expected})"
        
        if expected is None:
            return False, f"{field_name} has no expected value"
        
        # Numeric comparison with tolerance
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            if expected == 0:
                is_match = abs(actual) <= tolerance
            else:
                relative_diff = abs((actual - expected) / expected)
                is_match = relative_diff <= tolerance
            
            if not is_match:
                return False, f"{field_name}: actual={actual}, expected={expected}, diff={abs(actual - expected)}"
            return True, None
        
        # String comparison (case-insensitive for IDs)
        if isinstance(actual, str) and isinstance(expected, str):
            if actual.lower() == expected.lower():
                return True, None
            return False, f"{field_name}: actual='{actual}', expected='{expected}'"
        
        # Direct comparison for other types
        if actual != expected:
            return False, f"{field_name}: actual={actual}, expected={expected}"
        
        return True, None


# Type aliases for cleaner code
ValidatorResult = ScriptResult
ValidationContext = ScriptContext


def create_success_result(
    extracted_values: Dict[str, Any] = None,
    computed_values: Dict[str, Any] = None,
    message: str = None
) -> ScriptResult:
    """
    Helper to create a successful validation result.
    
    Args:
        extracted_values: Values to make available in extract_values
        computed_values: Computed/expected values for comparison
        message: Optional success message
    
    Returns:
        ScriptResult indicating success
    """
    return ScriptResult(
        success=True,
        errors=[],
        extracted_values=extracted_values or {},
        computed_values=computed_values or {},
        metadata={"message": message} if message else {}
    )


def create_failure_result(
    errors: List[str],
    extracted_values: Dict[str, Any] = None,
    computed_values: Dict[str, Any] = None
) -> ScriptResult:
    """
    Helper to create a failed validation result.
    
    Args:
        errors: List of error messages
        extracted_values: Values to make available even on failure
        computed_values: Computed values for debugging
    
    Returns:
        ScriptResult indicating failure
    """
    return ScriptResult(
        success=False,
        errors=errors,
        extracted_values=extracted_values or {},
        computed_values=computed_values or {}
    )
