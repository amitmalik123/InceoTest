"""
Test Validation Manager

Orchestrates all validation operations including status code, response fields,
response matching, and JSON schema validation.
Note: SOAP validation is handled automatically by SoapClient (framework/clients/soap_client.py).
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from framework.common.logger import get_logger
from framework.common.template_utils import render_hybrid, render_template
from framework.common.utils import normalize_path
from framework.validators.validators import Validators

logger = get_logger(__name__)


class TestValidationManager:
    """
    Manages all validation types for test execution.
    Coordinates status code, field, response, and schema validation.
    Note: SOAP validation is not handled here - it's automatic in SoapClient.
    """
    
    def __init__(self):
        """Initialize validation manager"""
        self.validators = Validators()
        logger.debug("TestValidationManager initialized")
    
    def validate_status_code(
        self, 
        response: Any, 
        expected_status: int,
        protocol: str = "REST"
    ):
        """
        Validate HTTP status code (skip for DB_ONLY).
        Delegates to Validators.validate_status_code().
        
        Args:
            response: Response object
            expected_status: Expected status code
            protocol: Protocol type
        
        Raises:
            AssertionError: If status code doesn't match
        """
        if protocol == 'DB_ONLY':
            logger.debug("Skipping status code validation for DB_ONLY protocol")
            return
        
        # Delegate to validators
        error = self.validators.validate_status_code(response, expected_status)
        if error:
            raise AssertionError(error)
        
        logger.info(f"Status code validation PASSED: {response.status_code}")
    
    def validate_performance(
        self,
        response_time_ms: int,
        case: Dict
    ):
        """
        Validate response time against max_response_time_ms threshold.
        Delegates to Validators.validate_performance().
        
        Args:
            response_time_ms: Actual response time in milliseconds
            case: Test case configuration
        
        Raises:
            AssertionError: If response time exceeds threshold
        """
        validate_cfg = case.get('validate', {})
        performance_cfg = validate_cfg.get('performance', {})
        max_time = performance_cfg.get('max_response_time_ms')
        
        if max_time is None:
            logger.debug("No max_response_time_ms configured, skipping performance validation")
            return
        
        error = self.validators.validate_performance(response_time_ms, int(max_time))
        if error:
            raise AssertionError(error)
    
    def validate_security(
        self,
        response: Any,
        payload: Any,
        case: Dict
    ):
        """
        Validate security checks (SQL injection, XSS patterns).
        Delegates to Validators.validate_security().
        
        Args:
            response: Response object
            payload: Request payload
            case: Test case configuration
        
        Raises:
            AssertionError: If security checks fail
        """
        validate_cfg = case.get('validate', {})
        security_cfg = validate_cfg.get('security', {})
        checks = security_cfg.get('checks', [])
        
        if not checks:
            logger.debug("No security checks configured, skipping security validation")
            return
        
        error = self.validators.validate_security(response, payload, checks)
        if error:
            raise AssertionError(error)
    
    def validate_assertions(
        self,
        case: Dict,
        context: Dict
    ) -> Dict:
        """
        Execute custom assertions defined in case['validate']['assertions'].
        Each assertion supports:
          - actual: value or {{var}}
          - expected: value or {{var}}
          - operator: ==, !=, >, <, >=, <=, contains, not_contains, starts_with, ends_with, in, not_in
          - message: failure message
        
        Args:
            case: Test case configuration
            context: Context dictionary for variable resolution
        
        Returns:
            Dict with stats: {"total": int, "passed": int, "failed": int}
        
        Raises:
            AssertionError: If any assertion fails
        """
        validate_cfg = case.get("validate", {}) or {}
        assertions = validate_cfg.get("assertions", []) or []
        
        if not assertions:
            logger.debug("No custom assertions configured, skipping assertions validation")
            return {"total": 0, "passed": 0, "failed": 0}
        
        def resolve_template(value):
            """Resolve simple {{var}} templates using context."""
            if isinstance(value, (int, float, bool)) or value is None:
                return value
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2]
                return context.get(var_name)
            return value
        
        def to_number_if_possible(v):
            """Try to coerce value to number if it looks numeric."""
            if isinstance(v, (int, float)):
                return v
            if isinstance(v, str):
                try:
                    if "." in v:
                        return float(v)
                    return int(v)
                except Exception:
                    return v
            return v
        
        for idx, assertion in enumerate(assertions, 1):
            actual_raw = assertion.get("actual")
            expected_raw = assertion.get("expected")
            operator = assertion.get("operator", "==")
            message = assertion.get("message", "Custom assertion failed")
            
            actual = resolve_template(actual_raw)
            expected = resolve_template(expected_raw)
            
            # For numeric operators, try to convert to numbers
            if operator in [">", "<", ">=", "<="]:
                actual_val = to_number_if_possible(actual)
                expected_val = to_number_if_possible(expected)
            else:
                actual_val = actual
                expected_val = expected
            
            try:
                # Comparison operators
                if operator == "==":
                    assert actual_val == expected_val, f"{message}: actual={actual_val}, expected={expected_val}"
                elif operator == "!=":
                    assert actual_val != expected_val, f"{message}: actual={actual_val}, expected (different)={expected_val}"
                elif operator == ">":
                    assert float(actual_val) > float(expected_val), f"{message}: actual={actual_val} <= expected={expected_val}"
                elif operator == "<":
                    assert float(actual_val) < float(expected_val), f"{message}: actual={actual_val} >= expected={expected_val}"
                elif operator == ">=":
                    assert float(actual_val) >= float(expected_val), f"{message}: actual={actual_val} < expected={expected_val}"
                elif operator == "<=":
                    assert float(actual_val) <= float(expected_val), f"{message}: actual={actual_val} > expected={expected_val}"
                
                # String operators
                elif operator == "contains":
                    assert str(expected_val) in str(actual_val), f"{message}: '{expected_val}' not in '{actual_val}'"
                elif operator == "not_contains":
                    assert str(expected_val) not in str(actual_val), f"{message}: '{expected_val}' found in '{actual_val}'"
                elif operator == "starts_with":
                    assert str(actual_val).startswith(str(expected_val)), f"{message}: '{actual_val}' does not start with '{expected_val}'"
                elif operator == "ends_with":
                    assert str(actual_val).endswith(str(expected_val)), f"{message}: '{actual_val}' does not end with '{expected_val}'"
                
                # List/Collection operators
                elif operator == "in":
                    # actual_val should be in expected_val (expected_val is a list/collection)
                    assert actual_val in expected_val, f"{message}: '{actual_val}' not in {expected_val}"
                elif operator == "not_in":
                    # actual_val should not be in expected_val (expected_val is a list/collection)
                    assert actual_val not in expected_val, f"{message}: '{actual_val}' found in {expected_val}"
                
                else:
                    raise AssertionError(f"Unsupported operator '{operator}' in custom assertion. Supported: ==, !=, >, <, >=, <=, contains, not_contains, starts_with, ends_with, in, not_in")
                
                # Log detailed success message
                logger.info(f"✓ Assertion {idx} PASSED: {actual_val} {operator} {expected_val}")
            
            except AssertionError as e:
                logger.error(f"✗ Assertion {idx} FAILED: {str(e)}")
                raise
        
        logger.info(f"Custom assertions validation PASSED: {len(assertions)} assertion(s)")
        
        # Build details array for UI display
        details = []
        for assertion in assertions:
            message = assertion.get("message", "Custom assertion")
            details.append({"message": message, "status": "PASS"})
        
        return {
            "total": len(assertions), 
            "passed": len(assertions), 
            "failed": 0,
            "details": details
        }
    
    def prepare_expected(self, case: Dict, context: Dict) -> Dict:
        """
        Prepare expected validation config from case.
        
        Args:
            case: Test case configuration
            context: Context dictionary for rendering
        
        Returns:
            Expected validation configuration dictionary
        """
        if 'expected' in case and case['expected']:
            expected = render_hybrid(case['expected'], context)
        else:
            # Handle empty expected_status for DB_ONLY tests
            expected_status_str = case.get('expected_status', '200')
            protocol = case.get('protocol', case.get('method', '')).upper()
            
            if expected_status_str == '' or expected_status_str is None:
                expected_status = 200 if protocol != 'DB_ONLY' else None
            else:
                expected_status = int(expected_status_str)
            
            expected = {'status_code': expected_status} if expected_status else {}
        
        # Always include 'fields' from the test case if present
        if 'validate' in case and case['validate'] and 'fields' in case['validate']:
            fields_block = case['validate']['fields']
            
            if isinstance(fields_block, list):
                # Convert list format to dict format
                fields_dict = {
                    item['field']: item['type'] 
                    for item in fields_block 
                    if 'field' in item and 'type' in item
                }
                logger.debug(f"Fields dict for validation: {fields_dict}")
                expected['fields'] = fields_dict
            elif isinstance(fields_block, dict):
                logger.debug(f"Fields dict for validation: {fields_block}")
                expected['fields'] = fields_block
        
        return expected
    
    def validate_response_fields(
        self, 
        response: Any, 
        expected: Dict,
        case: Dict
    ) -> List[str]:
        """
        Validate response fields using Validators.
        
        Args:
            response: Response object
            expected: Expected validation configuration
            case: Test case configuration
        
        Returns:
            List of validation errors (empty if validation passed)
        """
        if not expected:
            logger.debug("No expected validation config, skipping field validation")
            return []
        
        try:
            # Log the actual response JSON before validation
            try:
                logger.debug(f"Actual response JSON for validation: {response.json()}")
            except Exception as e:
                logger.warning(f"Could not parse response JSON: {e}")
            
            logger.debug(f"Expected config for validation: {expected}")
            
            validation_errors = self.validators.validate_response(response, expected)
            
            if validation_errors:
                logger.error(f"Field validation FAILED: {validation_errors}")
            else:
                logger.info("Field validation PASSED")
            
            return validation_errors
            
        except Exception as e:
            error_msg = f"Field validation error: {e}"
            logger.error(error_msg)
            return [error_msg]
    
    def validate_response_match(
        self, 
        response: Any,
        expected_response: Any,
        ignore_fields: Optional[List[str]] = None,
        case: Dict = None
    ):
        """
        Compare actual vs expected response with ignore_fields support.
        
        Args:
            response: Response object
            expected_response: Expected response (dict, list, or string)
            ignore_fields: List of field names to ignore in comparison
            case: Test case configuration
        
        Raises:
            AssertionError: If response doesn't match expected
        """
        # Parse actual response
        actual_response = self._parse_response(response)
        
        # Render expected_response if it's a file path
        expected_response = self._load_expected_response(expected_response)
        
        # Get ignore_fields from case if not provided
        if ignore_fields is None and case:
            ignore_fields = case.get('ignore_fields', case.get('ignore_keys', []))
        
        # Default dynamic fields to ignore in response comparison
        if not ignore_fields:
            ignore_fields = [
                "traceId", "id", "addressid", "contactid", "identifierid", 
                "timestamp", "createdDate", "modifiedDate", "entitycreateddate",
                "individualdateofbirth", "version"
            ]
        
        logger.info(f"Comparing responses with ignore_fields: {ignore_fields}")
        
        # Perform comparison
        if isinstance(expected_response, str):
            self._compare_string_response(actual_response, expected_response, response)
        else:
            self._compare_dict_response(actual_response, expected_response, ignore_fields)
        
        logger.info("Response match validation PASSED")
    
    def _parse_response(self, response: Any) -> Any:
        """Parse response as JSON or fallback to text"""
        try:
            actual_response = response.json()
            logger.debug(f"Response parsed as JSON")
            return actual_response
        except:
            actual_response = response.text.strip()
            logger.debug(f"Response is not JSON, using text: '{actual_response}'")
            return actual_response
    
    def _load_expected_response(self, expected_response: Any) -> Any:
        """Load expected response from file if path provided"""
        if isinstance(expected_response, str):
            rendered = render_template(expected_response, {})
            
            # If rendered looks like a JSON file path, try to load it
            if rendered.endswith('.json'):
                # Normalize path separators for cross-platform compatibility
                rendered = normalize_path(rendered)
                rel_path = os.path.join('testdata', rendered)
                if os.path.exists(rel_path):
                    with open(rel_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                elif os.path.exists(rendered):
                    with open(rendered, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            return rendered
        
        return expected_response
    
    def _compare_string_response(self, actual: Any, expected: str, response: Any):
        """Compare string-based response"""
        is_json = isinstance(actual, (dict, list))
        
        if is_json:
            actual_text = json.dumps(actual) if actual else ""
        else:
            actual_text = actual
        
        # Handle empty response case
        if not actual_text and not expected:
            logger.info("Both expected and actual responses are empty - match")
            return
        
        if expected and not actual_text:
            # Expected something but got empty response
            logger.warning(f"Expected response '{expected}' but got empty response. "
                         f"Status: {response.status_code}")
            
            # Don't fail for empty responses on error status codes (4xx, 5xx)
            if response.status_code < 400:
                raise AssertionError(
                    f"Expected response text but got empty response.\n"
                    f"Expected: '{expected}'\nActual: (empty)"
                )
            else:
                logger.info(f"Empty response is acceptable for error status {response.status_code}")
                return
        
        # Check if expected is substring or exact match
        if expected not in actual_text and actual_text != expected:
            raise AssertionError(
                f"Response text does not match expected.\n"
                f"Expected: '{expected}'\nActual: '{actual_text}'"
            )
        
        logger.info(f"Response text matched expected: '{expected}'")
    
    def _compare_dict_response(self, actual: Any, expected: Any, ignore_fields: List[str]):
        """Compare dict/list-based response"""
        def dicts_equal_ignoring_keys(d1, d2, ignore_keys):
            """Recursively compare dicts/lists ignoring specified keys"""
            if isinstance(d1, dict) and isinstance(d2, dict):
                for k in d1:
                    if k in ignore_keys:
                        continue
                    if k not in d2 or not dicts_equal_ignoring_keys(d1[k], d2[k], ignore_keys):
                        return False
                for k in d2:
                    if k in ignore_keys:
                        continue
                    if k not in d1:
                        return False
                return True
            elif isinstance(d1, list) and isinstance(d2, list):
                return all(dicts_equal_ignoring_keys(x, y, ignore_keys) for x, y in zip(d1, d2))
            else:
                return d1 == d2
        
        if not dicts_equal_ignoring_keys(actual, expected, ignore_fields):
            raise AssertionError(
                f"Actual response does not match expected_response (ignoring: {ignore_fields}).\n"
                f"Expected: {expected}\nActual: {actual}"
            )
        
        logger.info(f"Response matched expected (with ignored fields: {ignore_fields})")
    
    def validate_schema(self, response: Any, schema_file: str):
        """
        Validate response against JSON schema.
        Loads schema file and delegates to Validators.validate_json_schema().
        
        Args:
            response: Response object
            schema_file: Path to JSON schema file (relative to testdata/)
        
        Raises:
            AssertionError: If validation fails
        """
        # Normalize path separators for cross-platform compatibility
        schema_file = normalize_path(schema_file)
        schema_path = os.path.join('testdata', schema_file)
        
        if not os.path.exists(schema_path):
            error_msg = f"Schema file not found: {schema_path}"
            logger.error(f"[CONTRACT CHECK FAIL] {error_msg}")
            raise AssertionError(error_msg)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Delegate to validators
        error = self.validators.validate_json_schema(response, schema)
        if error:
            error_msg = f"Schema validation failed for {schema_file}: {error}"
            logger.error(f"[CONTRACT CHECK FAIL] {error_msg}")
            raise AssertionError(error_msg)
        
        logger.info(f"Schema validation PASSED for {schema_file}")


# Singleton accessor function
_validation_manager_instance = None

def get_validation_manager() -> TestValidationManager:
    """
    Get the singleton TestValidationManager instance.
    
    Returns:
        TestValidationManager singleton instance
    
    Example:
        >>> validation_mgr = get_validation_manager()
        >>> validation_mgr.validate_status_code(response, 200, protocol)
        >>> errors = validation_mgr.validate_response_fields(response, expected, case)
        >>> validation_mgr.validate_response_match(response, expected_response, ignore_fields)
        >>> validation_mgr.validate_schema(response, 'schemas/user.json')
    """
    global _validation_manager_instance
    if _validation_manager_instance is None:
        _validation_manager_instance = TestValidationManager()
    return _validation_manager_instance
