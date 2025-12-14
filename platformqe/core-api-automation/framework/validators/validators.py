import re
import json
import os
from typing import List, Dict, Any, Optional
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
            normalized_fields = fields_to_compare
        elif all(isinstance(f, str) for f in fields_to_compare):
            normalized_fields = [{"source": f, "target": f} for f in fields_to_compare]
    elif isinstance(fields_to_compare, str):
        normalized_fields = [{"source": fields_to_compare, "target": fields_to_compare}]
    else:
        logger.warning(f"Unsupported fields_to_compare format: {fields_to_compare}")
        return [f"Unsupported fields_to_compare format: {fields_to_compare}"]

    for api_row in api_response:
        # Build key tuple for matching, resolve variables if needed
        api_key = tuple(resolve_var(api_row.get(k.strip('{}'))) for k in key_fields)
        db_row = next((row for row in db_result if tuple(row.get(k) for k in key_fields) == api_key), None)
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
            logger.debug(
                f"Comparing field '{api_field}' (API) to '{db_field}' (DB): API={api_value}, DB={db_value}"
            )
            # Case-insensitive comparison for string values (e.g., GUIDs)
            if isinstance(api_value, str) and isinstance(db_value, str):
                values_match = api_value.lower() == db_value.lower()
            else:
                values_match = api_value == db_value
           
            if not values_match:
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

    def _remove_ignored_fields(self, data: Any, ignore_fields: List[str]) -> Any:
        """
        Recursively remove ignored fields from data structure (dict/list).
        
        Args:
            data: Data structure to clean (dict, list, or primitive)
            ignore_fields: List of field names to remove
        
        Returns:
            Cleaned data structure with ignored fields removed
        
        Examples:
            >>> data = {'id': 123, 'name': 'test', 'nested': {'id': 456}}
            >>> self._remove_ignored_fields(data, ['id'])
            {'name': 'test', 'nested': {}}
        """
        if not ignore_fields:
            return data
        
        if isinstance(data, dict):
            return {
                k: self._remove_ignored_fields(v, ignore_fields)
                for k, v in data.items()
                if k not in ignore_fields
            }
        elif isinstance(data, list):
            return [self._remove_ignored_fields(item, ignore_fields) for item in data]
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