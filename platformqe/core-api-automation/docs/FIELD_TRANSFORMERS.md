# Field Transformers Documentation

## Overview

Field transformers provide a generic, configurable way to transform field values during data comparison without hardcoding API-specific logic in the validation framework. This keeps the framework protocol-agnostic and API-agnostic.

## Architecture

### Components

1. **`framework/common/data_transformers.py`**: Generic transformation logic
2. **Test Case JSON Configuration**: Declarative transformation definitions
3. **`framework/validators/validators.py`**: Integration with validation logic

### Benefits

- **Separation of Concerns**: API-specific transformations are configured in test cases, not hardcoded in framework
- **Reusability**: Same transformations can be applied to different fields
- **Maintainability**: Adding new transformations doesn't require modifying core framework
- **Flexibility**: Each test case can define its own transformations

## Configuration

### Test Case JSON Structure

```json
{
  "validate": {
    "data_comparison": {
      "field_transformers": [
        {
          "field": "field_name",
          "transform": "transformation_type",
          "options": {
            "option1": "value1",
            "option2": "value2"
          }
        }
      ],
      "fields_to_compare": [...]
    }
  }
}
```

## Available Transformations

### 1. array_to_object

Transforms an array of objects into a single object using key-value mapping.

**Use Case**: API returns `[{'type': 'System', 'value': 3}]` but DB stores `{'system': 3}`

**Configuration**:
```json
{
  "field": "investment_min",
  "transform": "array_to_object",
  "options": {
    "key_field": "type",
    "value_field": "value",
    "lowercase_keys": true
  }
}
```

**Example**:
- Input: `[{'type': 'System', 'value': 3}, {'type': 'User', 'value': 5}]`
- Output: `{'system': 3, 'user': 5}`

**Special Handling**: If array contains items with 'warning' field, transformation is skipped:
- Input: `[{'warning': 'some message'}]`
- Output: `[{'warning': 'some message'}]` (unchanged)

### 2. object_to_array

Transforms an object into an array of objects using key-value mapping.

**Use Case**: Reverse transformation when DB has object format but API expects array

**Configuration**:
```json
{
  "field": "price_bands",
  "transform": "object_to_array",
  "options": {
    "key_field": "category",
    "value_field": "price",
    "capitalize_keys": true
  }
}
```

**Example**:
- Input: `{'system': 3, 'user': 5}`
- Output: `[{'category': 'System', 'price': 3}, {'category': 'User', 'price': 5}]`

### 3. normalize_boolean

Converts various boolean representations to Python bool.

**Configuration**:
```json
{
  "field": "is_active",
  "transform": "normalize_boolean",
  "options": {}
}
```

**Example**:
- Input: `"true"`, `"1"`, `1`, `"yes"`, `"Y"` → Output: `True`
- Input: `"false"`, `"0"`, `0`, `"no"`, `"N"` → Output: `False`

### 4. normalize_numeric

Converts string numbers to int or float.

**Configuration**:
```json
{
  "field": "amount",
  "transform": "normalize_numeric",
  "options": {}
}
```

**Example**:
- Input: `"123"` → Output: `123`
- Input: `"123.45"` → Output: `123.45`

### 5. lowercase_string

Converts string to lowercase.

**Configuration**:
```json
{
  "field": "status",
  "transform": "lowercase_string",
  "options": {}
}
```

### 6. uppercase_string

Converts string to uppercase.

### 7. strip_whitespace

Removes leading and trailing whitespace from strings.

## Complete Example

### Test Case JSON

```json
{
  "test_case_id": "GET_MODELS_001",
  "description": "Validate investment minimums from API against DB",
  "endpoint": "/api/v1/models/{modelId}",
  "method": "GET",
  "path_params": {
    "modelId": "{{model_id}}"
  },
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "target": "db_result",
      "key_field": ["modelId"],
      "fields_to_compare": [
        {
          "source": "investment_min",
          "target": "investment_min"
        },
        {
          "source": "modelName",
          "target": "model_name"
        },
        {
          "source": "isActive",
          "target": "is_active"
        }
      ],
      "field_transformers": [
        {
          "field": "investment_min",
          "transform": "array_to_object",
          "options": {
            "key_field": "type",
            "value_field": "value",
            "lowercase_keys": true
          }
        },
        {
          "field": "isActive",
          "transform": "normalize_boolean",
          "options": {}
        }
      ]
    }
  },
  "db_queries": [
    {
      "name": "default",
      "query": "SELECT model_id as modelId, investment_min, model_name, is_active FROM models WHERE model_id = {{model_id}}"
    }
  ]
}
```

### API Response
```json
{
  "modelId": "MOD123",
  "modelName": "Growth Portfolio",
  "isActive": "true",
  "investment_min": [
    {"type": "System", "value": 5000},
    {"type": "User", "value": 10000}
  ]
}
```

### DB Result
```json
[{
  "modelId": "MOD123",
  "model_name": "Growth Portfolio",
  "is_active": 1,
  "investment_min": {
    "system": 5000,
    "user": 10000
  }
}]
```

### Transformation Flow

1. **investment_min Field**:
   - API: `[{"type": "System", "value": 5000}, {"type": "User", "value": 10000}]`
   - After transformation: `{"system": 5000, "user": 10000}`
   - DB: `{"system": 5000, "user": 10000}`
   - **Result**: ✅ Match

2. **isActive Field**:
   - API: `"true"`
   - After transformation: `True`
   - DB: `1` (normalized to `True` by existing logic)
   - **Result**: ✅ Match

## Adding New Transformations

To add a new transformation type:

1. Add transformation method to `DataTransformer` class in `data_transformers.py`:

```python
def _my_custom_transform(self, value: Any, options: Dict) -> Any:
    """
    Description of transformation.
    
    Args:
        value: Value to transform
        options: Transformation options
    
    Returns:
        Transformed value
    """
    # Implementation here
    return transformed_value
```

2. Register in `__init__` method:

```python
self.transformers = {
    'array_to_object': self._array_to_object,
    'my_custom_transform': self._my_custom_transform,  # Add here
    # ... other transformers
}
```

3. Use in test case JSON:

```json
{
  "field": "my_field",
  "transform": "my_custom_transform",
  "options": {
    "custom_option": "value"
  }
}
```

## Migration Guide

### Before (Hardcoded Logic)

❌ **validators.py** contained hardcoded investment_min transformation:

```python
if db_field == 'investment_min' or api_field == 'investment_min':
    # 50+ lines of hardcoded transformation logic
    ...
```

### After (Configurable Approach)

✅ **Test case JSON** contains declarative configuration:

```json
{
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
  ]
}
```

### Migration Steps

1. Identify fields with hardcoded transformations
2. Add corresponding `field_transformers` configuration to test case JSON
3. Remove hardcoded logic from validators.py
4. Test to ensure validation still passes

## Best Practices

1. **Keep transformations simple**: Each transformer should do one thing well
2. **Document options**: Clearly document available options for each transformation
3. **Handle edge cases**: Transformers should gracefully handle None, empty values, etc.
4. **Log transformations**: Use logger.debug() to log transformation steps for debugging
5. **Test bidirectionally**: If data can be in multiple formats, test both directions

## Troubleshooting

### Transformation not applied

**Symptom**: Values don't match even though transformation is configured

**Solution**:
1. Check field name in `field_transformers` matches exactly
2. Verify transformation type is correct
3. Check logs for transformation errors
4. Ensure options are properly formatted

### Wrong transformation result

**Symptom**: Transformation produces unexpected output

**Solution**:
1. Review transformation options (e.g., `lowercase_keys`, `key_field`)
2. Check input data format
3. Add debug logging to see intermediate values
4. Test transformation in isolation

## Performance Considerations

- Transformations are applied only when configured
- Transformer instance is created once per validation
- Minimal overhead for fields without transformations
- Cache transformation results if needed for large datasets

## Future Enhancements

Potential future improvements:

1. **Chained transformations**: Apply multiple transformations in sequence
2. **Conditional transformations**: Apply based on data conditions
3. **Custom transformer plugins**: Load transformers from external modules
4. **Transformation validation**: Validate transformation configuration at load time
5. **Performance optimizations**: Batch transformations for large datasets
