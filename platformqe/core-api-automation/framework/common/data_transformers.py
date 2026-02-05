"""
Data Transformers Module

This module provides generic, reusable data transformation functions for API testing.
Transformers can be configured per field in test case JSON files via the field_transformers configuration.

Example usage in test case JSON:
{
  "validate": {
    "data_comparison": {
      "field_transformers": [
        {
          "field": "investment_min",
          "transform": "array_to_object",
          "options": {
            "key_field": "type",
            "value_field": "value",
            "lowercase_keys": true
          }
        }
      ],
      "fields_to_compare": [...]
    }
  }
}
"""

from typing import Any, Dict, List, Optional
from framework.common.logger import get_logger

logger = get_logger(__name__)


class DataTransformer:
    """
    Generic data transformer that applies configured transformations to field values.
    """
    
    def __init__(self, transformers_config: Optional[List[Dict]] = None):
        """
        Initialize transformer with configuration.
        
        Args:
            transformers_config: List of transformer configurations
                [
                    {
                        "field": "field_name",
                        "transform": "transformation_type",
                        "options": {...}
                    }
                ]
        """
        self.transformers_config = transformers_config or []
        self.transformers = {
            'array_to_object': self._array_to_object,
            'object_to_array': self._object_to_array,
            'normalize_boolean': self._normalize_boolean,
            'normalize_numeric': self._normalize_numeric,
            'lowercase_string': self._lowercase_string,
            'uppercase_string': self._uppercase_string,
            'strip_whitespace': self._strip_whitespace,
            'substring': self._substring,
        }
    
    def apply_transformations(self, field_name: str, value: Any, parent_path: str = '') -> Any:
        """
        Apply configured transformations to a field value.
        Recursively processes nested structures (lists and dicts).
        
        Args:
            field_name: Name of the field to transform
            value: Original value
            parent_path: Path to the parent field (for nested structures)
        
        Returns:
            Transformed value or original value if no transformations configured
        """
        # Build the full path for matching wildcard patterns
        full_path = f"{parent_path}.{field_name}" if parent_path else field_name
        
        # Find transformer config for this field (exact match)
        transformer_config = next(
            (t for t in self.transformers_config if t.get('field') == field_name),
            None
        )
        
        # If no exact match, try wildcard pattern matching (e.g., versions.*.publishedDate)
        if not transformer_config:
            for t in self.transformers_config:
                pattern = t.get('field', '')
                # Check if pattern contains wildcard
                if '*' in pattern:
                    # Convert pattern to regex (e.g., versions.*.publishedDate -> publishedDate$)
                    # Extract the final part after the last wildcard
                    parts = pattern.split('*')
                    if parts and field_name.endswith(parts[-1].lstrip('.')):
                        transformer_config = t
                        break
        
        # If we have a transformer config, apply it to the value
        if transformer_config:
            transform_type = transformer_config.get('transform')
            options = transformer_config.get('options', {})
            
            if transform_type in self.transformers:
                try:
                    transformer_func = self.transformers[transform_type]
                    transformed_value = transformer_func(value, options)
                    logger.debug(f"Transformed field '{full_path}' using '{transform_type}': {value} -> {transformed_value}")
                    return transformed_value
                except Exception as e:
                    logger.warning(f"Failed to transform field '{full_path}' using '{transform_type}': {e}")
            else:
                logger.warning(f"Unknown transformation type '{transform_type}' for field '{full_path}'")
        
        # If value is a list, recursively apply transformations to each item
        if isinstance(value, list):
            return [self.apply_transformations(field_name, item, parent_path) if not isinstance(item, dict) 
                    else self._transform_dict(item, full_path) 
                    for item in value]
        
        # If value is a dict, recursively apply transformations to all fields
        if isinstance(value, dict):
            return self._transform_dict(value, full_path)
        
        return value
    
    def _transform_dict(self, data: dict, parent_path: str = '') -> dict:
        """
        Recursively transform all fields in a dictionary.
        
        Args:
            data: Dictionary to transform
            parent_path: Path to the parent field
        
        Returns:
            Transformed dictionary
        """
        result = {}
        for key, val in data.items():
            result[key] = self.apply_transformations(key, val, parent_path)
        return result
    
    def _array_to_object(self, value: Any, options: Dict) -> Any:
        """
        Transform array of objects to a single object using key-value mapping.
        
        Example:
            Input: [{'type': 'System', 'value': 3}, {'type': 'User', 'value': 5}]
            Options: {"key_field": "type", "value_field": "value", "lowercase_keys": true}
            Output: {'system': 3, 'user': 5}
        
        Special handling for warnings:
            If array contains items with 'warning' field, returns value unchanged
            Example: [{'warning': 'some message'}] -> [{'warning': 'some message'}]
        
        Args:
            value: Array of objects to transform
            options: Transformation options
                - key_field: Field name to use as key
                - value_field: Field name to use as value
                - lowercase_keys: Whether to lowercase keys (default: False)
        
        Returns:
            Transformed object or original value if not applicable
        """
        if not isinstance(value, list) or not value:
            return value
        
        # Check for warnings - if present, skip transformation
        has_warnings = any(
            isinstance(item, dict) and 'warning' in item 
            for item in value
        )
        if has_warnings:
            logger.debug("Array contains warnings, skipping transformation")
            return value
        
        key_field = options.get('key_field', 'type')
        value_field = options.get('value_field', 'value')
        lowercase_keys = options.get('lowercase_keys', False)
        
        result = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            
            if key_field not in item or value_field not in item:
                logger.debug(f"Item missing required fields '{key_field}' or '{value_field}', skipping")
                continue
            
            key = item[key_field]
            if lowercase_keys and isinstance(key, str):
                key = key.lower()
            
            result[key] = item[value_field]
        
        return result if result else value
    
    def _object_to_array(self, value: Any, options: Dict) -> Any:
        """
        Transform object to array of objects using key-value mapping.
        
        Example:
            Input: {'system': 3, 'user': 5}
            Options: {"key_field": "type", "value_field": "value", "capitalize_keys": true}
            Output: [{'type': 'System', 'value': 3}, {'type': 'User', 'value': 5}]
        
        Args:
            value: Object to transform
            options: Transformation options
                - key_field: Field name for keys (default: 'type')
                - value_field: Field name for values (default: 'value')
                - capitalize_keys: Whether to capitalize keys (default: False)
                - uppercase_keys: Whether to uppercase keys (default: False)
        
        Returns:
            Transformed array or original value if not applicable
        """
        if not isinstance(value, dict) or not value:
            return value
        
        key_field = options.get('key_field', 'type')
        value_field = options.get('value_field', 'value')
        capitalize_keys = options.get('capitalize_keys', False)
        uppercase_keys = options.get('uppercase_keys', False)
        
        result = []
        for k, v in value.items():
            key = k
            if capitalize_keys and isinstance(key, str):
                key = key.capitalize()
            elif uppercase_keys and isinstance(key, str):
                key = key.upper()
            
            result.append({key_field: key, value_field: v})
        
        return result
    
    def _normalize_boolean(self, value: Any, options: Dict) -> Any:
        """
        Normalize various boolean representations to Python bool.
        
        Example:
            Input: "true", "1", 1, "yes", "Y"
            Output: True
        
        Args:
            value: Value to normalize
            options: Not used for this transformation
        
        Returns:
            Normalized boolean or original value if not applicable
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, int):
            return bool(value)
        
        if isinstance(value, str):
            lower_val = value.strip().lower()
            if lower_val in ['true', '1', 'yes', 'y']:
                return True
            if lower_val in ['false', '0', 'no', 'n']:
                return False
        
        return value
    
    def _normalize_numeric(self, value: Any, options: Dict) -> Any:
        """
        Normalize numeric values (convert strings to int/float).
        
        Example:
            Input: "123" -> 123
            Input: "123.45" -> 123.45
        
        Args:
            value: Value to normalize
            options: Not used for this transformation
        
        Returns:
            Normalized numeric value or original value if not applicable
        """
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            try:
                # Try integer conversion first
                if '.' not in value:
                    return int(value)
                else:
                    return float(value)
            except (ValueError, TypeError):
                pass
        
        return value
    
    def _lowercase_string(self, value: Any, options: Dict) -> Any:
        """
        Convert string to lowercase.
        
        Args:
            value: Value to transform
            options: Not used for this transformation
        
        Returns:
            Lowercase string or original value if not applicable
        """
        if isinstance(value, str):
            return value.lower()
        return value
    
    def _uppercase_string(self, value: Any, options: Dict) -> Any:
        """
        Convert string to uppercase.
        
        Args:
            value: Value to transform
            options: Not used for this transformation
        
        Returns:
            Uppercase string or original value if not applicable
        """
        if isinstance(value, str):
            return value.upper()
        return value
    
    def _strip_whitespace(self, value: Any, options: Dict) -> Any:
        """
        Strip whitespace from string values.
        
        Args:
            value: Value to transform
            options: Not used for this transformation
        
        Returns:
            Trimmed string or original value if not applicable
        """
        if isinstance(value, str):
            return value.strip()
        return value
    
    def _substring(self, value: Any, options: Dict) -> Any:
        """
        Extract a substring from string values.
        
        Example:
            Input: "2026-01-14T13:35:21.450602Z"
            Options: {"start": 0, "end": 19}
            Output: "2026-01-14T13:35:21"
        
        Args:
            value: Value to transform
            options: Transformation options
                - start: Starting index (default: 0)
                - end: Ending index (optional)
        
        Returns:
            Substring or original value if not applicable
        """
        if not isinstance(value, str):
            return value
        
        start = options.get('start', 0)
        end = options.get('end')
        
        if end is not None:
            return value[start:end]
        else:
            return value[start:]


def apply_field_transformers(
    data: Any,
    field_name: str,
    transformers_config: Optional[List[Dict]] = None
) -> Any:
    """
    Convenience function to apply transformations to a field value.
    
    Args:
        data: Data structure containing the field
        field_name: Name of the field to transform
        transformers_config: Transformer configuration
    
    Returns:
        Transformed value
    """
    transformer = DataTransformer(transformers_config)
    return transformer.apply_transformations(field_name, data)


def get_bidirectional_transformer(
    source_format: str,
    target_format: str,
    options: Dict
) -> Optional[str]:
    """
    Get the appropriate transformation type based on source and target formats.
    
    Args:
        source_format: Source data format ('array', 'object', etc.)
        target_format: Target data format ('array', 'object', etc.)
        options: Transformation options
    
    Returns:
        Transformation type name or None if not supported
    """
    if source_format == 'array' and target_format == 'object':
        return 'array_to_object'
    elif source_format == 'object' and target_format == 'array':
        return 'object_to_array'
    
    return None
