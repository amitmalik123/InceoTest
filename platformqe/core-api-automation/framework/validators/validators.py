import re
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from framework.loaders.api_definitions_loader import ApiDefinitionsLoader
from framework.common.logger import get_logger

logger = get_logger(__name__)


def validate_db_comparison(api_response, db_result, key_fields, fields_to_compare, context=None):
    """
    Validates row-level and field-level comparison between API response and DB result.
    Resolves variables in {{}} using context if provided.
    Args:
        api_response (list of dict): API response rows
        db_result (list of dict): DB result rows
        key_fields (list of str): Fields to use for row matching
        fields_to_compare (list of dict): [{"source": "api_field", "target": "db_field"}]
        context (dict): Optional context for variable resolution
    Returns:
        errors (list of str): List of mismatch or missing row errors
    """
    logger.debug(f"Fields to compare for DB validation: {fields_to_compare}")
    errors = []

    def resolve_var(val):
        if isinstance(val, str) and val.startswith("{{") and val.endswith("}}") and context:
            var_name = val.strip("{} ")
            return context.get(var_name)
        return val
    
    def resolve_nested_key(data, key):
        """Resolve nested key using dot notation (e.g., 'parties.0.id')"""
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            elif isinstance(value, list):
                try:
                    idx = int(k)
                    value = value[idx]
                except (ValueError, IndexError, TypeError):
                    return None
            else:
                return None
        return value

    normalized_fields = []
    if isinstance(fields_to_compare, list):
        if all(isinstance(f, dict) for f in fields_to_compare):
            # Resolve template variables in source/target field names
            normalized_fields = []
            for f in fields_to_compare:
                # Skip entries with empty source or target
                if not f.get("source") or not f.get("target"):
                    continue
                source_field = resolve_var(f["source"]) if isinstance(f.get("source"), str) else f["source"]
                target_field = resolve_var(f["target"]) if isinstance(f.get("target"), str) else f["target"]
                normalized_fields.append({"source": source_field, "target": target_field})
        elif all(isinstance(f, str) for f in fields_to_compare):
            # Filter out empty strings
            normalized_fields = [
                {"source": f, "target": f} for f in fields_to_compare 
                if f and f.strip()
            ]
    elif isinstance(fields_to_compare, str):
        if fields_to_compare and fields_to_compare.strip():
            normalized_fields = [{"source": fields_to_compare, "target": fields_to_compare}]
        else:
            normalized_fields = []
    else:
        logger.warning(f"Unsupported fields_to_compare format: {fields_to_compare}")
        return [f"Unsupported fields_to_compare format: {fields_to_compare}"]

    # Normalize key_fields format to support both simple list and dict mapping
    # Formats: ["userId"] or [{"source": "userId", "target": "USER_ID"}]
    normalized_key_fields = []
    if key_fields:
        if all(isinstance(k, dict) for k in key_fields):
            # Dict format: [{"source": "userId", "target": "USER_ID"}]
            # Filter out entries with empty source or target
            normalized_key_fields = [
                k for k in key_fields 
                if k.get("source") and k.get("target")
            ]
        elif all(isinstance(k, str) for k in key_fields):
            # Simple format: ["userId"] - same field name in both source and target
            # Filter out empty strings
            normalized_key_fields = [
                {"source": k, "target": k} for k in key_fields 
                if k and k.strip()
            ]
    
    # If no key_fields specified or key_fields empty, compare without row matching
    if not normalized_key_fields:
        # Direct comparison without key matching (assumes single row or direct value comparison)
        if len(api_response) != len(db_result):
            msg = f"Row count mismatch: API has {len(api_response)} rows, DB has {len(db_result)} rows"
            logger.warning(msg)
            errors.append(msg)
            return errors
        
        for idx, api_row in enumerate(api_response):
            db_row = db_result[idx] if idx < len(db_result) else {}
            for mapping in normalized_fields:
                api_field = mapping["source"]
                db_field = mapping["target"]
                api_value = resolve_nested_key(api_row, api_field)
                db_value = db_row.get(db_field)
                
                # Special handling for investment_min field - bidirectional transformation
                # API can return: [{'type': 'System', 'value': 3}] or {'system': 3} or [{'warning': '...'}]
                # DB can return: {'system': 3} or [{'type': 'System', 'value': 3}]
                if db_field == 'investment_min' or api_field == 'investment_min':
                    # Check if API response contains warnings - if so, validation passes
                    if isinstance(api_value, list) and api_value:
                        # Check if any item has a 'warning' field
                        has_warnings = any(isinstance(item, dict) and 'warning' in item for item in api_value)
                        if has_warnings:
                            logger.info(f"Field '{db_field}' contains warnings in API response - validation passes")
                            continue  # Skip validation for fields with warnings
                        
                        # Transform API array format to DB object format for comparison
                        # [{'type': 'System', 'value': 3}] -> {'system': 3}
                        try:
                            transformed_api_value = {}
                            for item in api_value:
                                if isinstance(item, dict) and 'type' in item and 'value' in item:
                                    # Convert type to lowercase to match DB format
                                    key = item['type'].lower()
                                    transformed_api_value[key] = item['value']
                            # Update api_value to the transformed format for comparison
                            if transformed_api_value:
                                api_value = transformed_api_value
                                logger.debug(f"Transformed investment_min API value from array to object format: {api_value}")
                        except Exception as e:
                            logger.warning(f"Failed to transform investment_min API value: {e}")
                    
                    # Handle reverse transformation: API has object, DB has array
                    # API: {'system': 3} vs DB: [{'type': 'System', 'value': 3}]
                    if isinstance(api_value, dict) and isinstance(db_value, list) and db_value:
                        try:
                            # Transform DB array format to object format for comparison
                            transformed_db_value = {}
                            for item in db_value:
                                if isinstance(item, dict) and 'type' in item and 'value' in item:
                                    key = item['type'].lower()
                                    transformed_db_value[key] = item['value']
                            # Update db_value to the transformed format for comparison
                            if transformed_db_value:
                                db_value = transformed_db_value
                                logger.debug(f"Transformed investment_min DB value from array to object format: {db_value}")
                        except Exception as e:
                            logger.warning(f"Failed to transform investment_min DB value: {e}")
                
                logger.debug(f"Comparing field '{api_field}' (API) to '{db_field}' (DB): API={api_value}, DB={db_value}")
                
                # Normalize values for comparison
                def normalize_for_comparison(val1, val2):
                    """Normalize values to handle type mismatches (e.g., int vs string)"""
                    # Case-insensitive string comparison for string values (e.g., GUIDs)
                    if isinstance(val1, str) and isinstance(val2, str):
                        return val1.lower() == val2.lower()
                    
                    # Handle numeric comparisons with type coercion
                    # Convert string numbers to numeric types for comparison
                    def try_numeric(val):
                        if isinstance(val, (int, float)):
                            return val
                        if isinstance(val, str):
                            try:
                                # Try integer conversion first
                                if '.' not in val:
                                    return int(val)
                                else:
                                    return float(val)
                            except (ValueError, TypeError):
                                pass
                        return val
                    
                    norm_val1 = try_numeric(val1)
                    norm_val2 = try_numeric(val2)
                    
                    return norm_val1 == norm_val2
                
                values_match = normalize_for_comparison(api_value, db_value)
            
                if not values_match:
                    msg = f"Mismatch for {db_field}: API={api_value}, DB={db_value}"
                    logger.error(msg)
                    errors.append(msg)
                else:
                    logger.debug(f"Match for {db_field}: {api_value}")
        return errors

    # Key-based row matching with support for different field names in source and target
    for api_row in api_response:
        # Build key tuple from source fields
        api_key = tuple(resolve_var(api_row.get(k["source"].strip('{}'))) for k in normalized_key_fields)
        
        # Find matching DB row using target field names
        db_row = None
        for row in db_result:
            db_key = tuple(row.get(k["target"]) for k in normalized_key_fields)
            if api_key == db_key:
                db_row = row
                break
        
        if not db_row:
            msg = f"No DB row found for key {api_key}"
            logger.warning(msg)
            errors.append(msg)
            continue

        for mapping in normalized_fields:
            api_field = mapping["source"]
            db_field = mapping["target"]
            # Use nested key resolution for API field (supports dot notation like 'parties.0.id')
            api_value = resolve_nested_key(api_row, api_field)
            # Resolve variable if needed
            if api_value is None and api_field.startswith("{{"):
                api_value = resolve_var(api_row.get(api_field.strip("{}")))
            db_value = db_row.get(db_field)
            
            # Special handling for investment_min field - bidirectional transformation
            # API can return: [{'type': 'System', 'value': 3}] or {'system': 3} or [{'warning': '...'}]
            # DB can return: {'system': 3} or [{'type': 'System', 'value': 3}]
            if db_field == 'investment_min' or api_field == 'investment_min':
                # Check if API response contains warnings - if so, validation passes
                if isinstance(api_value, list) and api_value:
                    # Check if any item has a 'warning' field
                    has_warnings = any(isinstance(item, dict) and 'warning' in item for item in api_value)
                    if has_warnings:
                        logger.info(f"Field '{db_field}' contains warnings in API response - validation passes")
                        continue  # Skip validation for fields with warnings
                    
                    # Transform API array format to DB object format for comparison
                    # [{'type': 'System', 'value': 3}] -> {'system': 3}
                    try:
                        transformed_api_value = {}
                        for item in api_value:
                            if isinstance(item, dict) and 'type' in item and 'value' in item:
                                # Convert type to lowercase to match DB format
                                key = item['type'].lower()
                                transformed_api_value[key] = item['value']
                        # Update api_value to the transformed format for comparison
                        if transformed_api_value:
                            api_value = transformed_api_value
                            logger.debug(f"Transformed investment_min API value from array to object format: {api_value}")
                    except Exception as e:
                        logger.warning(f"Failed to transform investment_min API value: {e}")
                
                # Handle reverse transformation: API has object, DB has array
                # API: {'system': 3} vs DB: [{'type': 'System', 'value': 3}]
                if isinstance(api_value, dict) and isinstance(db_value, list) and db_value:
                    try:
                        # Transform DB array format to object format for comparison
                        transformed_db_value = {}
                        for item in db_value:
                            if isinstance(item, dict) and 'type' in item and 'value' in item:
                                key = item['type'].lower()
                                transformed_db_value[key] = item['value']
                        # Update db_value to the transformed format for comparison
                        if transformed_db_value:
                            db_value = transformed_db_value
                            logger.debug(f"Transformed investment_min DB value from array to object format: {db_value}")
                    except Exception as e:
                        logger.warning(f"Failed to transform investment_min DB value: {e}")
            
            # Deep normalize empty values: None, [], {} are considered equivalent
            def normalize_empty(val):
                """Recursively treat None, empty list, and empty dict as equivalent"""
                if val is None or val == [] or val == {}:
                    return None
                # Recursively normalize lists
                if isinstance(val, list):
                    return [normalize_empty(item) for item in val]
                # Recursively normalize dicts
                if isinstance(val, dict):
                    return {k: normalize_empty(v) for k, v in val.items()}
                return val
            
            # Normalize values for comparison
            def normalize_for_comparison(val1, val2):
                """Normalize values to handle type mismatches and empty values"""
                # First normalize empty values
                norm1 = normalize_empty(val1)
                norm2 = normalize_empty(val2)
                
                # Case-insensitive string comparison for string values (e.g., GUIDs)
                if isinstance(norm1, str) and isinstance(norm2, str):
                    return norm1.lower() == norm2.lower()
                
                # Handle numeric comparisons with type coercion
                # Convert string numbers to numeric types for comparison
                def try_numeric(val):
                    if isinstance(val, (int, float)):
                        return val
                    if isinstance(val, str):
                        try:
                            # Try integer conversion first
                            if '.' not in val:
                                return int(val)
                            else:
                                return float(val)
                        except (ValueError, TypeError):
                            pass
                    return val
                
                typed_val1 = try_numeric(norm1)
                typed_val2 = try_numeric(norm2)
                
                return typed_val1 == typed_val2
            
            logger.debug(f"Comparing field '{api_field}' (API) to '{db_field}' (DB): API={api_value}, DB={db_value}")
            if not normalize_for_comparison(api_value, db_value):
                msg = f"Mismatch for {db_field}: API={api_value}, DB={db_value}"
                logger.error(msg)
                errors.append(msg)
            else:
                logger.debug(f"Match for {db_field}: {api_value}")

    return errors


def perform_db_comparison_validation(response, db_result, validation_config, context):
    """
    Orchestrates DB comparison validation based on test case configuration.
    
    Args:
        response: API response object
        db_result: Database query result
        validation_config (dict): data_comparison config from test case
        context (dict): Test execution context with variables
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    if not validation_config or not db_result:
        return True, []
    
    # Parse configuration
    key_fields = validation_config.get('key_field', [])
    fields_to_compare = validation_config.get('fields_to_compare', [])
    source_type = validation_config.get('source', 'api_response')
    source_array_path = validation_config.get('source_array_path', '')
    target_type = validation_config.get('target', 'db_result')
    
    # Handle db_result to expected_values comparison
    if source_type == 'db_result' and target_type == 'expected_values':
        expected_values = validation_config.get('expected_values', {})
        if not expected_values:
            logger.warning("expected_values not found in data_comparison config")
            return True, []
        
        errors = []
        for db_row in db_result:
            for field in fields_to_compare:
                db_value = db_row.get(field)
                expected_value = expected_values.get(field)
                
                logger.debug(f"Comparing DB field '{field}': DB={db_value}, Expected={expected_value}")
                
                if db_value != expected_value:
                    msg = f"Mismatch for field '{field}': DB value='{db_value}', Expected value='{expected_value}'"
                    logger.error(msg)
                    errors.append(msg)
                else:
                    logger.debug(f"Match for field '{field}': {db_value}")
        
        if errors:
            logger.error(f"DB to expected_values comparison failed: {errors}")
            return False, errors
        else:
            logger.info("DB to expected_values comparison passed")
            return True, []
    
    # Determine source data based on source_type
    source_data = None
    if source_type == 'api_response':
        source_data = response.json() if hasattr(response, 'json') else response
    elif source_type == 'api_request':
        source_data = context.get('api_request')
    elif source_type == 'context':
        source_data = context
    else:
        source_data = response.json() if hasattr(response, 'json') else response
    
    if not fields_to_compare or not source_data:
        return True, []
    
    # Apply source_array_path if specified to extract the array from the response
    if source_array_path and isinstance(source_data, dict):
        from framework.common.common_functions import extract_value
        source_data = extract_value(source_data, key=source_array_path)
        if source_data is None:
            logger.error(f"Failed to extract array from source using path '{source_array_path}'")
            return False, [f"Failed to extract array from source using path '{source_array_path}'"]
    
    # Ensure source_data is a list for row-wise comparison
    if isinstance(source_data, dict):
        source_data = [source_data]
    
    # Perform validation
    errors = validate_db_comparison(source_data, db_result, key_fields, fields_to_compare, context)
    
    if errors:
        logger.error(f"DB comparison validation failed: {errors}")
        return False, errors
    else:
        logger.info("DB comparison validation passed")
        return True, []


class ValidationError(Exception):
    """Custom exception for validation failures."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class Validators:
    def _resolve_nested_key(self, data, key):
        """
        Resolve a nested key in a dict or list using dot notation (e.g., 'user.email' or '0.id').
        """
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            elif isinstance(value, list):
                try:
                    idx = int(k)
                    value = value[idx]
                except (ValueError, IndexError, TypeError):
                    return None
            else:
                return None
        return value
    def __init__(self):
        self.definitions = ApiDefinitionsLoader().load()
        self.validations = self.definitions.get('custom_validations', {}).get('fields', {})

    def validate_status_code(self, response, expected: int) -> Optional[str]:
        actual = response.status_code
        if actual != expected:
            msg = f"Expected status code {expected}, got {actual}"
            logger.error(msg)
            return msg
        logger.info(f"Status code {actual} matched expected {expected}")
        return None
    
    def validate_json_schema(self, response, schema: Dict[str, Any]) -> Optional[str]:
        """
        Validate response against JSON schema.
        
        Args:
            response: Response object
            schema: JSON schema dictionary
        
        Returns:
            Error message if validation fails, None if passes
        """
        try:
            import jsonschema
        except ImportError:
            msg = "jsonschema library not installed. Install with: pip install jsonschema"
            logger.error(msg)
            return msg
        
        try:
            actual_json = response.json()
        except Exception as e:
            msg = f"Response is not valid JSON: {e}"
            logger.error(msg)
            return msg
        
        try:
            jsonschema.validate(instance=actual_json, schema=schema)
            logger.info("JSON schema validation PASSED")
            return None
        except jsonschema.ValidationError as ve:
            msg = f"Response JSON does not match schema: {ve}"
            logger.error(msg)
            return msg
    
    def validate_performance(self, response_time_ms: int, max_time_ms: int) -> Optional[str]:
        """
        Validate response time against threshold.
        
        Args:
            response_time_ms: Actual response time in milliseconds
            max_time_ms: Maximum allowed response time in milliseconds
        
        Returns:
            Error message if validation fails, None if passes
        """
        if response_time_ms > max_time_ms:
            msg = f"Response time {response_time_ms}ms exceeds maximum allowed {max_time_ms}ms"
            logger.error(f"Performance validation FAILED: {msg}")
            return msg
        
        logger.info(f"Performance validation PASSED: {response_time_ms}ms <= {max_time_ms}ms")
        return None
    
    def validate_security(self, response: Any, payload: Any, checks: List[str]) -> Optional[str]:
        """
        Validate security checks (SQL injection, XSS patterns).
        
        Args:
            response: Response object
            payload: Request payload
            checks: List of security checks to perform ('sql_injection', 'xss')
        
        Returns:
            Error message if validation fails, None if passes
        """
        if not checks:
            logger.debug("No security checks configured")
            return None
        
        errors = []
        
        # SQL Injection pattern detection
        if 'sql_injection' in checks:
            sql_patterns = [
                r"'\s*OR\s*'1'\s*=\s*'1",
                r"'\s*OR\s*1\s*=\s*1",
                r"--\s*$",
                r";\s*DROP\s+TABLE",
                r"UNION\s+SELECT",
                r"'\s*;\s*--"
            ]
            
            payload_str = str(payload) if payload else ""
            for pattern in sql_patterns:
                if re.search(pattern, payload_str, re.IGNORECASE):
                    try:
                        if response.status_code >= 400:
                            logger.info(f"SQL injection pattern detected and properly rejected with status {response.status_code}")
                        else:
                            errors.append(f"SQL injection pattern detected but request succeeded (status {response.status_code})")
                    except:
                        pass
                    break
        
        # XSS pattern detection
        if 'xss' in checks:
            xss_patterns = [
                r"<script[^>]*>.*?</script>",
                r"javascript:\s*",
                r"onerror\s*=",
                r"onload\s*=",
                r"<iframe[^>]*>"
            ]
            
            payload_str = str(payload) if payload else ""
            for pattern in xss_patterns:
                if re.search(pattern, payload_str, re.IGNORECASE):
                    try:
                        if response.status_code >= 400:
                            logger.info(f"XSS pattern detected and properly rejected with status {response.status_code}")
                        else:
                            errors.append(f"XSS pattern detected but request succeeded (status {response.status_code})")
                    except:
                        pass
                    break
        
        if errors:
            msg = "; ".join(errors)
            logger.error(f"Security validation FAILED: {msg}")
            return msg
        
        logger.info(f"Security validation PASSED for checks: {checks}")
        return None

    def validate_json_keys(self, response, expected_keys: List[str]) -> List[str]:
        errors = []
        try:
            data = response.json()
        except Exception as e:
            msg = f"Failed to parse JSON: {e}"
            logger.error(msg)
            return [msg]

        for key in expected_keys:
            if not self._key_exists(data, key):
                msg = f"Missing key: {key}"
                logger.error(msg)
                errors.append(msg)
            else:
                logger.info(f"Key '{key}' found in response")
        return errors

    def validate_fields(self, data: Dict[str, Any], fields) -> List[str]:
        """
        Validate fields in the response data using custom_validations from api_common_definitions.json.
        Supports both dict ({field: type}) and list of dicts ([{"field":..., "type":...}]).
        """
        logger.debug(f"validate_fields called with data type: {type(data)}, fields_dict: {fields}")
        errors = []
        # Support both dict and list of dicts
        if isinstance(fields, list):
            fields_dict = {item['field']: item['type'] for item in fields if 'field' in item and 'type' in item}
        elif isinstance(fields, dict):
            fields_dict = fields
        else:
            logger.warning(f"Unsupported fields format: {fields}")
            return [f"Unsupported fields format: {fields}"]

        logger.debug(f"Top of validate_fields: data={data}, fields_dict={fields_dict}")
        # If data is a list, validate each item for the given fields
        if isinstance(data, list):
            for idx, item in enumerate(data):
                logger.debug(f"Validating item {idx}: {item}")
                for field, expected_type in fields_dict.items():
                    try:
                        value = self._resolve_nested_key(item, field)
                    except Exception as e:
                        msg = f"Field '{field}' not found in response item {idx}: {e}"
                        logger.error(msg)
                        errors.append(msg)
                        continue
                    validation = self.validations.get(expected_type)
                    regex = validation.get('regex') if validation else None
                    logger.debug(f"Validating item {idx} field '{field}': value='{value}', expected_type='{expected_type}', regex='{regex}'")
                    if not validation:
                        msg = f"No validation rule for type '{expected_type}' in custom_validations."
                        logger.warning(msg)
                        errors.append(msg)
                        continue
                    if regex:
                        logger.debug(f"Validating field '{field}' (type '{expected_type}') with value: '{value}', regex: '{regex}'")
                        match_result = re.match(regex, str(value))
                        logger.debug(f"Match result for field '{field}': {match_result}")
                        if not match_result:
                            msg = f"Field '{field}' value '{value}' in item {idx} does not match type '{expected_type}' (regex: {regex})"
                            logger.error(msg)
                            errors.append(msg)
                        else:
                            logger.info(f"Field '{field}' in item {idx} passed validation for type '{expected_type}' (value: '{value}', regex: '{regex}')")
                    else:
                        msg = f"No regex defined for type '{expected_type}' in custom_validations."
                        logger.warning(msg)
                        errors.append(msg)
        else:
            for field, expected_type in fields_dict.items():
                try:
                    value = self._resolve_nested_key(data, field)
                except Exception as e:
                    msg = f"Field '{field}' not found in response: {e}"
                    logger.error(msg)
                    errors.append(msg)
                    continue
                validation = self.validations.get(expected_type)
                regex = validation.get('regex') if validation else None
                logger.debug(f"Validating field '{field}': value='{value}', expected_type='{expected_type}', regex='{regex}'")
                if not validation:
                    msg = f"No validation rule for type '{expected_type}' in custom_validations."
                    logger.warning(msg)
                    errors.append(msg)
                    continue
                if regex:
                    if not re.match(regex, str(value)):
                        msg = f"Field '{field}' value '{value}' does not match type '{expected_type}' (regex: {regex})"
                        logger.error(msg)
                        errors.append(msg)
                    else:
                        logger.info(f"Field '{field}' passed validation for type '{expected_type}' (value: '{value}', regex: '{regex}')")
                else:
                    msg = f"No regex defined for type '{expected_type}' in custom_validations."
                    logger.warning(msg)
                    errors.append(msg)
        return errors

    def validate_response(
        self, 
        response, 
        expected: Dict[str, Any],
        ignore_fields: Optional[List[str]] = None
    ) -> List[str]:
        from framework.common.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Starting response validation...")
        errors = []

        if 'status_code' in expected:
            err = self.validate_status_code(response, expected['status_code'])
            if err:
                errors.append(err)

        if 'json_keys' in expected:
            errors.extend(self.validate_json_keys(response, expected['json_keys']))

        if 'fields' in expected:
            try:
                data = response.json()
                logger.debug(f"validate_response: data type for fields validation: {type(data)}")
                errors.extend(self.validate_fields(data, expected['fields']))
            except Exception as e:
                msg = f"Failed to validate fields: {e}"
                logger.error(msg)
                errors.append(msg)

        # NEW: Validate full JSON response with ignore_fields support
        if 'json_response' in expected:
            try:
                actual_data = response.json()
                expected_data = expected['json_response']
                
                logger.info("Performing deep JSON comparison...")
                comparison_errors = self._compare_json_responses(
                    actual_data,
                    expected_data,
                    ignore_fields=ignore_fields
                )
                errors.extend(comparison_errors)
            except Exception as e:
                msg = f"Failed to compare JSON responses: {e}"
                logger.error(msg)
                errors.append(msg)

        if errors:
            logger.warning(f"Validation completed with {len(errors)} error(s).")
        else:
            logger.info("Validation passed with no errors.")
        return errors

    def validate_fields(self, data: Dict[str, Any], fields) -> List[str]:
        """
        Validate fields in the response data using custom_validations from api_common_definitions.json.
        Supports both dict ({field: type}) and list of dicts ([{"field":..., "type":...}]).
        """
        logger.debug(f"validate_fields called with data type: {type(data)}, fields_dict: {fields}")
        errors = []
        # Support both dict and list of dicts
        if isinstance(fields, list):
            fields_dict = {item['field']: item['type'] for item in fields if 'field' in item and 'type' in item}
        elif isinstance(fields, dict):
            fields_dict = fields
        else:
            logger.warning(f"Unsupported fields format: {fields}")
            return [f"Unsupported fields format: {fields}"]

        logger.debug(f"Top of validate_fields: data={data}, fields_dict={fields_dict}")
        # If data is a list, validate each item for the given fields
        if isinstance(data, list):
            for idx, item in enumerate(data):
                logger.debug(f"Validating item {idx}: {item}")
                for field, expected_type in fields_dict.items():
                    try:
                        value = self._resolve_nested_key(item, field)
                    except Exception as e:
                        msg = f"Field '{field}' not found in response item {idx}: {e}"
                        logger.error(msg)
                        errors.append(msg)
                        continue
                    validation = self.validations.get(expected_type)
                    regex = validation.get('regex') if validation else None
                    logger.debug(f"Validating item {idx} field '{field}': value='{value}', expected_type='{expected_type}', regex='{regex}'")
                    if not validation:
                        msg = f"No validation rule for type '{expected_type}' in custom_validations."
                        logger.warning(msg)
                        errors.append(msg)
                        continue
                    if regex:
                        logger.debug(f"Validating field '{field}' (type '{expected_type}') with value: '{value}', regex: '{regex}'")
                        match_result = re.match(regex, str(value))
                        logger.debug(f"Match result for field '{field}': {match_result}")
                        if not match_result:
                            msg = f"Field '{field}' value '{value}' in item {idx} does not match type '{expected_type}' (regex: {regex})"
                            logger.error(msg)
                            errors.append(msg)
                        else:
                            logger.info(f"Field '{field}' in item {idx} passed validation for type '{expected_type}' (value: '{value}', regex: '{regex}')")
                    else:
                        msg = f"No regex defined for type '{expected_type}' in custom_validations."
                        logger.warning(msg)
                        errors.append(msg)
        else:
            for field, expected_type in fields_dict.items():
                try:
                    value = self._resolve_nested_key(data, field)
                except Exception as e:
                    msg = f"Field '{field}' not found in response: {e}"
                    logger.error(msg)
                    errors.append(msg)
                    continue
                validation = self.validations.get(expected_type)
                regex = validation.get('regex') if validation else None
                logger.debug(f"Validating field '{field}': value='{value}', expected_type='{expected_type}', regex='{regex}'")
                if not validation:
                    msg = f"No validation rule for type '{expected_type}' in custom_validations."
                    logger.warning(msg)
                    errors.append(msg)
                    continue
                if regex:
                    logger.debug(f"Validating field '{field}' (type '{expected_type}') with value: '{value}', regex: '{regex}'")
                    match_result = re.match(regex, str(value))
                    logger.debug(f"Match result for field '{field}': {match_result}")
                    if not match_result:
                        msg = f"Field '{field}' value '{value}' does not match type '{expected_type}' (regex: {regex})"
                        logger.error(msg)
                        errors.append(msg)
                    else:
                        logger.info(f"Field '{field}' passed validation for type '{expected_type}' (value: '{value}', regex: '{regex}')")
                else:
                    msg = f"No regex defined for type '{expected_type}' in custom_validations."
                    logger.warning(msg)
                    errors.append(msg)
        return errors

    def _remove_ignored_fields(self, data: Any, ignore_fields: List[str], current_path: str = "") -> Any:
        """
        Recursively remove ignored fields from data structure (dict/list).
        Supports both global field names and JSON path notation.
        
        Args:
            data: Data structure to clean (dict, list, or primitive)
            ignore_fields: List of field names or paths to remove
                - Simple names (e.g., 'id') remove all fields with that name globally
                - Paths (e.g., 'parties.0.partyId') remove only specific field at that path
            current_path: Current path in the data structure (internal use)
        
        Returns:
            Cleaned data structure with ignored fields removed
        
        Examples:
            >>> data = {'id': 123, 'name': 'test', 'nested': {'id': 456}}
            >>> self._remove_ignored_fields(data, ['id'])
            {'name': 'test', 'nested': {}}
            
            >>> data = {'parties': [{'partyId': '123', 'name': 'John'}]}
            >>> self._remove_ignored_fields(data, ['parties.0.partyId'])
            {'parties': [{'name': 'John'}]}
        """
        if not ignore_fields:
            return data
        
        # Separate global field names from path-based ignores
        global_ignores = [f for f in ignore_fields if '.' not in f]
        path_ignores = [f for f in ignore_fields if '.' in f]
        
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                # Build the full path for this key
                full_path = f"{current_path}.{k}" if current_path else k
                
                # Check if this field should be ignored globally
                if k in global_ignores:
                    continue
                
                # Check if this exact path should be ignored
                if full_path in path_ignores:
                    continue
                
                # Recursively process the value
                result[k] = self._remove_ignored_fields(v, ignore_fields, full_path)
            
            return result
            
        elif isinstance(data, list):
            result = []
            for index, item in enumerate(data):
                # Build the full path for this array index
                full_path = f"{current_path}.{index}" if current_path else str(index)
                
                # Recursively process each item
                result.append(self._remove_ignored_fields(item, ignore_fields, full_path))
            
            return result
            
        else:
            return data

    def _compare_json_responses(
        self, 
        actual: Dict[str, Any], 
        expected: Dict[str, Any],
        ignore_fields: Optional[List[str]] = None,
        path: str = ""
    ) -> List[str]:
        """
        Deep comparison of two JSON responses with support for ignoring fields.
        
        Args:
            actual: Actual response data
            expected: Expected response data
            ignore_fields: List of field names to ignore during comparison
            path: Current path in nested structure (for error reporting)
        
        Returns:
            List of error messages (empty if responses match)
        """
        errors = []
        ignore_fields = ignore_fields or []
        
        # Remove ignored fields from both structures
        actual_cleaned = self._remove_ignored_fields(actual, ignore_fields)
        expected_cleaned = self._remove_ignored_fields(expected, ignore_fields)
        
        logger.debug(f"Comparing responses at path '{path}' (ignoring: {ignore_fields})")
        
        # Type mismatch
        if type(actual_cleaned) != type(expected_cleaned):
            msg = f"Type mismatch at '{path}': expected {type(expected_cleaned).__name__}, got {type(actual_cleaned).__name__}"
            logger.error(msg)
            errors.append(msg)
            return errors
        
        # Compare dicts
        if isinstance(actual_cleaned, dict):
            # Check for missing keys
            expected_keys = set(expected_cleaned.keys())
            actual_keys = set(actual_cleaned.keys())
            
            missing_keys = expected_keys - actual_keys
            extra_keys = actual_keys - expected_keys
            
            for key in missing_keys:
                msg = f"Missing key '{path}.{key}' in actual response"
                logger.error(msg)
                errors.append(msg)
            
            for key in extra_keys:
                msg = f"Unexpected key '{path}.{key}' in actual response"
                logger.warning(msg)
                # Don't add to errors - extra keys might be acceptable
            
            # Compare common keys
            common_keys = expected_keys & actual_keys
            for key in common_keys:
                new_path = f"{path}.{key}" if path else key
                errors.extend(
                    self._compare_json_responses(
                        actual_cleaned[key],
                        expected_cleaned[key],
                        ignore_fields,
                        new_path
                    )
                )
        
        # Compare lists
        elif isinstance(actual_cleaned, list):
            if len(actual_cleaned) != len(expected_cleaned):
                msg = f"List length mismatch at '{path}': expected {len(expected_cleaned)}, got {len(actual_cleaned)}"
                logger.error(msg)
                errors.append(msg)
                return errors
            
            for idx, (actual_item, expected_item) in enumerate(zip(actual_cleaned, expected_cleaned)):
                new_path = f"{path}[{idx}]"
                errors.extend(
                    self._compare_json_responses(
                        actual_item,
                        expected_item,
                        ignore_fields,
                        new_path
                    )
                )
        
        # Compare primitives
        else:
            if actual_cleaned != expected_cleaned:
                msg = f"Value mismatch at '{path}': expected '{expected_cleaned}', got '{actual_cleaned}'"
                logger.error(msg)
                errors.append(msg)
        
        return errors


def compare_data(source, target, fields, key_field, log_differences=True):
    """
    Compare data between source and target lists based on key fields.
    
    Args:
        source (list): Source data list
        target (list): Target data list to compare against
        fields (list): List of field mappings to compare (str or dict with 'source'/'target')
        key_field (str or list): Field(s) to use as unique identifier
        log_differences (bool): Whether to log differences (default: True)
    
    Raises:
        AssertionError: If differences are found between source and target
    """
    from framework.common.utils import get_composite_key
    
    differences = []
    
    for item in source:
        key = get_composite_key(item, key_field)
        target_item = next((t for t in target if get_composite_key(t, key_field) == key), None)
        if not target_item:
            logger.debug(f"Data comparison: Key '{key}' missing in target.")
            differences.append((key, 'Missing in target'))
            continue
        
        for field_map in fields:
            if isinstance(field_map, dict):
                src_field = field_map.get('source')
                tgt_field = field_map.get('target')
            else:
                src_field = tgt_field = field_map
            
            src_val = item.get(src_field)
            tgt_val = target_item.get(tgt_field)
            
            # Normalize boolean values for comparison
            if src_field and tgt_field and (src_field.lower() == 'visibility' or tgt_field.lower() == 'visibility' or src_field.lower() == 'isvisible' or tgt_field.lower() == 'isvisible'):
                def normalize_bool(val):
                    if isinstance(val, bool):
                        return val
                    if isinstance(val, int):
                        return bool(val)
                    if isinstance(val, str):
                        if val.strip().lower() in ['true', '1', 'yes', 'y']:
                            return True
                        if val.strip().lower() in ['false', '0', 'no', 'n']:
                            return False
                    return val
                
                src_val = normalize_bool(src_val)
                tgt_val = normalize_bool(tgt_val)
            
            if src_val == tgt_val:
                logger.debug(f"Data comparison PASSED: Key='{key}', Field='{src_field}', SourceValue='{src_val}', TargetValue='{tgt_val}'")
            else:
                logger.debug(f"Data comparison FAILED: Key='{key}', Field='{src_field}', SourceValue='{src_val}', TargetValue='{tgt_val}'")
                differences.append((key, f"{src_field} vs {tgt_field}", src_val, tgt_val))
    
    # if log_differences and differences:
    #     print(tabulate(differences, headers=["Key", "Field", "Source", "Target"], tablefmt="grid"))
    assert not differences, f"Data comparison failed: {differences}"


def perform_generic_data_comparison(
    source_data: Any,
    target_data: Any,
    comparison_config: Dict,
    context: Dict
) -> Tuple[bool, List[str]]:
    """
    Generic data comparison that supports all combinations:
    - api_response vs api_request
    - api_response vs db_result
    - api_response vs api_response (e.g., from different queries)
    - api_request vs api_request (e.g., from different steps)
    - api_request vs db_result
    - db_result vs db_result (e.g., from different queries)
    
    Also supports record count comparison with compare_record_count flag.
    
    Args:
        source_data: Source data for comparison (already resolved)
        target_data: Target data for comparison (already resolved)
        comparison_config (dict): Configuration with key_field, fields_to_compare, etc.
        context (dict): Test execution context for variable resolution
    
    Returns:
        tuple: (is_valid: bool, errors: list of str)
    """
    logger.debug(f"Performing generic data comparison with config: {comparison_config}")
    
    # Parse configuration
    comparison_name = comparison_config.get('comparison_name', 'Data comparison')
    log_differences = comparison_config.get('log_differences', True)
    compare_record_count = comparison_config.get('compare_record_count', False)
    
    # Handle record count comparison mode
    if compare_record_count:
        return _perform_record_count_comparison(
            source_data, 
            target_data, 
            comparison_config,
            comparison_name,
            log_differences
        )
    
    # Regular field-level comparison
    key_fields = comparison_config.get('key_field', [])
    fields_to_compare = comparison_config.get('fields_to_compare', [])
    
    # Handle direct value comparison (no fields_to_compare specified)
    # This is used for simple value-to-literal comparisons
    if not fields_to_compare:
        logger.debug(f"{comparison_name}: No fields_to_compare specified, performing direct value comparison")
        
        # Compare source_data and target_data directly
        if source_data == target_data:
            logger.info(f"{comparison_name} PASSED: Values match ('{source_data}' == '{target_data}')")
            return True, []
        else:
            error_msg = f"Value mismatch: expected '{target_data}', got '{source_data}'"
            logger.error(f"{comparison_name} FAILED: {error_msg}")
            return False, [error_msg]
    
    if source_data is None or target_data is None:
        error_msg = f"{comparison_name}: Source or target data is None"
        logger.warning(error_msg)
        return False, [error_msg]
    
    # Ensure source and target data are lists for row-wise comparison
    if isinstance(source_data, dict):
        source_data = [source_data]
    if isinstance(target_data, dict):
        target_data = [target_data]
    
    if not isinstance(source_data, list) or not isinstance(target_data, list):
        error_msg = f"{comparison_name}: Source or target data is not list/dict format"
        logger.error(error_msg)
        return False, [error_msg]
    
    # Perform comparison using the existing validate_db_comparison logic
    try:
        errors = validate_db_comparison(
            source_data, 
            target_data, 
            key_fields, 
            fields_to_compare, 
            context
        )
        
        if errors:
            logger.error(f"{comparison_name} FAILED: {errors}")
            return False, errors
        else:
            logger.info(f"{comparison_name} PASSED")
            return True, []
            
    except Exception as e:
        error_msg = f"{comparison_name}: Exception occurred - {str(e)}"
        logger.error(error_msg)
        return False, [error_msg]


def _perform_record_count_comparison(
    source_data: Any,
    target_data: Any,
    comparison_config: Dict,
    comparison_name: str,
    log_differences: bool
) -> Tuple[bool, List[str]]:
    """
    Compare record counts between source and target data.
    
    Args:
        source_data: Source data (response, request, or db_result)
        target_data: Target data (response, request, or db_result)
        comparison_config: Configuration with array paths
        comparison_name: Name of the comparison for logging
        log_differences: Whether to log differences
    
    Returns:
        tuple: (is_valid: bool, errors: list of str)
    """
    from framework.common.common_functions import extract_value
    
    try:
        # Debug logging
        logger.debug(f"Record count comparison - source_data type: {type(source_data)}, target_data type: {type(target_data)}")
        logger.debug(f"source_data value: {source_data if not isinstance(source_data, list) or len(str(source_data)) < 200 else f'[list with {len(source_data)} items]'}")
        logger.debug(f"target_data value: {target_data if not isinstance(target_data, list) or len(str(target_data)) < 200 else f'[list with {len(target_data)} items]'}")
        
        # Extract record counts
        # Note: source_data and target_data have already been extracted by _resolve_data_source
        # so we don't need to apply array_path again
        source_count = extract_value(source_data, key="", record_count=True, array_path="")
        target_count = extract_value(target_data, key="", record_count=True, array_path="")
        
        # Compare counts
        if source_count == target_count:
            logger.info(f"{comparison_name} PASSED: Source count ({source_count}) == Target count ({target_count})")
            return True, []
        else:
            error_msg = f"Record count mismatch: Source has {source_count} records, Target has {target_count} records"
            if log_differences:
                logger.error(f"{comparison_name} FAILED: {error_msg}")
            return False, [error_msg]
            
    except Exception as e:
        error_msg = f"Record count comparison failed: {str(e)}"
        logger.error(f"{comparison_name}: {error_msg}")
        return False, [error_msg]


def perform_data_comparison_array(
    response: Any,
    context: Dict,
    data_comparison_configs: List[Dict]
) -> Tuple[bool, List[str]]:
    """
    Execute multiple data comparisons as specified in data_comparison array.
    Supports any combination of data sources: api_response, api_request, db_result.
    
    Args:
        response: API response object
        context: Test execution context containing:
            - api_request: The request payload/data
            - db_result: Default DB query result
            - db_results: Dict of named DB query results
            - Any other extracted variables
        data_comparison_configs: List of data_comparison configuration dicts
    
    Returns:
        tuple: (is_valid: bool, all_errors: list of str)
    """
    if not data_comparison_configs:
        return True, []
    
    # Support both array and single dict format for backward compatibility
    if isinstance(data_comparison_configs, dict):
        data_comparison_configs = [data_comparison_configs]
    
    all_errors = []
    all_valid = True
    
    for idx, comparison_config in enumerate(data_comparison_configs):
        comparison_name = comparison_config.get('comparison_name', f'Comparison #{idx+1}')
        logger.info(f"Executing {comparison_name}")
        
        # Resolve source data
        source_type = comparison_config.get('source', 'api_response')
        source_data = _resolve_data_source(source_type, comparison_config, response, context)
        
        # Resolve target data
        target_type = comparison_config.get('target', 'db_result')
        target_data = _resolve_data_source(target_type, comparison_config, response, context)
        
        # Perform comparison
        is_valid, errors = perform_generic_data_comparison(
            source_data,
            target_data,
            comparison_config,
            context
        )
        
        if not is_valid:
            all_valid = False
            all_errors.extend([f"{comparison_name}: {err}" for err in errors])
    
    return all_valid, all_errors


def _resolve_data_source(
    data_source_type: str,
    comparison_config: Dict,
    response: Any,
    context: Dict
) -> Any:
    """
    Resolve data source based on type and optional query name.
    
    Supported data source types:
    - 'api_response': API response data
    - 'api_request': API request payload
    - 'db_result': Database query result (with optional query name)
    - 'variable': Direct variable from context (variable name specified in source_variable/target_variable)
    - 'literal': Direct literal value (string, integer, float, boolean, null) from source_literal/target_literal
    - 'context.var_name': Context variable with explicit prefix
    - Any other string: Treated as variable name from context
    
    Args:
        data_source_type: Type of data source (api_response, api_request, db_result, variable, literal, etc.)
        comparison_config: Comparison configuration dict
        response: API response object
        context: Test execution context
    
    Returns:
        Resolved data or None if not found
    """
    from framework.common.common_functions import extract_value
    
    # Determine if this is source or target to get the correct keys
    is_source = 'source' in comparison_config and comparison_config['source'] == data_source_type

    # Handle literal values first as they don't need extraction
    if data_source_type == 'literal':
        literal_key = 'source_literal' if is_source else 'target_literal'
        if literal_key in comparison_config:
            literal_value = comparison_config[literal_key]
            logger.debug(f"Using literal value for {'source' if is_source else 'target'}: {literal_value}")
            return literal_value
        else:
            logger.warning(f"'literal' type specified but no '{literal_key}' provided")
            return None

    data = None
    query_key = comparison_config.get('source_query', 'default') if is_source else comparison_config.get('target_query', 'default')

    if data_source_type == 'api_response':
        # Handle empty responses gracefully to avoid JSON parsing errors
        if not getattr(response, 'text', True) or getattr(response, 'status_code', 200) == 204:
            logger.debug("API response is empty (e.g., 204 No Content), returning empty dict.")
            data = {}
        else:
            try:
                data = response.json() if hasattr(response, 'json') else response
            except Exception as ex:
                logger.warning(f"Failed to parse response as JSON, using raw text instead: {ex}")
                data = response.text
    
    elif data_source_type == 'api_request':
        data = context.get('api_request')
    
    elif data_source_type == 'db_result':
        db_results = context.get('db_results', {})
        if query_key and query_key in db_results:
            data = db_results.get(query_key)
        elif query_key == 'default' and context.get('db_result') is not None:
            logger.warning("Using legacy 'db_result' fallback. Consider using db_queries with 'default' key.")
            data = context.get('db_result')
        else:
            available_queries = list(db_results.keys()) if db_results else []
            raise ValueError(
                f"Query '{query_key}' not found in db_results. "
                f"Available queries: {available_queries}. "
                f"Please specify one of these using 'source_query' or 'target_query'."
            )
            
    elif data_source_type == 'variable':
        var_key = 'source_variable' if is_source else 'target_variable'
        var_name = comparison_config.get(var_key)
        if var_name:
            data = context.get(var_name)
            if data is None:
                logger.warning(f"Variable '{var_name}' not found in context")
        else:
            logger.warning(f"'variable' type specified but no '{var_key}' provided")
    
    elif data_source_type.startswith('context.'):
        var_name = data_source_type.replace('context.', '')
        data = context.get(var_name)
        if data is None:
            logger.debug(f"Data source '{data_source_type}' not found in context, treating as None")

    else:
        # Fallback: Treat as a direct variable name from context
        data = context.get(data_source_type)
        if data is None:
            logger.debug(f"Data source '{data_source_type}' not found in context, treating as None")

    # --- Unified Extraction Logic ---
    # Apply array_path extraction to the resolved data, regardless of its source
    array_path_key = 'source_array_path' if is_source else 'target_array_path'
    array_path = comparison_config.get(array_path_key, '')
    
    if array_path and data is not None:
        logger.debug(f"Extracting value from {data_source_type} using path: {array_path}")
        extracted_data = extract_value(data, key=array_path)
        if extracted_data is None:
            logger.error(f"Failed to extract value from {data_source_type} using path '{array_path}'")
        data = extracted_data
        
    return data
