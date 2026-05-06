# Custom Script Validators

This document explains how to create and use custom validator scripts in the API testing framework.

## Overview

Custom validator scripts allow you to run complex validation logic that goes beyond simple field comparison. You can implement domain-specific calculations, database validations, and custom business logic, with results captured for use in assertions and data comparisons.

## Key Features

- **Named Database Queries**: Support for multiple named queries (`db_queries` dict format)
- **Dynamic Configuration**: Load validation parameters (e.g., risk bands) from database
- **Script Result Extraction**: Capture computed values for assertions
- **Structured Logging**: ASCII-safe console output with `[PASS]`/`[FAIL]` markers
- **Flexible Query Patterns**: Auto-detect query types from naming conventions

## Quick Start

### 1. Add Script Reference to Test Case

In your test case JSON, add a `scripts` field with the path to your validator:

```json
{
    "test_id": "TC001",
    "service_name": "analyticsApiServices",
    "endpoint": "/v1/analytics",
    "method": "POST",
    "payload": { ... },
    "expected_status": "200",
    
    "scripts": ["analyticsApiServices\\validators\\ewma_validator.py"],
    
    "db_queries": {
        "monthlyPerformance_query": "SELECT ... FROM AM.dbo.MonthlyPerformance ...",
        "riskBands_query": "SELECT ProfileValue, AnnualStdDeviation FROM Platform.dbo.RiskProfile ORDER BY ProfileValue"
    },
    "db_type": "mssql",
    "db_connection_name": "am_db",
    "db_query_timing": "before_api",
    
    "extract_values": [
        {
            "from": "script_result",
            "key": "computed_annualized_volatility",
            "assign_to": "expected_volatility"
        },
        {
            "from": "script_result", 
            "key": "api_annualized_volatility",
            "assign_to": "actual_volatility"
        }
    ],
    
    "validate": {
        "assertions": [
            {
                "actual": "{{actual_volatility}}",
                "expected": "{{expected_volatility}}",
                "operator": "==",
                "message": "Volatility should match computed value"
            }
        ]
    }
}
```

### 2. Named Database Queries

Use `db_queries` (dict format) for multiple named queries:

```json
{
    "db_queries": {
        "monthlyPerformance_query": "SELECT TOP 180 a.MonthId, a.performance AS Model1_Performance, b.performance AS Model2_Performance FROM AM.dbo.MonthlyPerformance a INNER JOIN AM.dbo.MonthlyPerformance b ON a.MonthId = b.MonthId WHERE a.ItemId = 'CLSTU6' AND b.ItemId = 'GPSDN2' ORDER BY a.MonthId DESC",
        "riskBands_query": "SELECT ProfileValue, AnnualStdDeviation FROM Platform.dbo.RiskProfile ORDER BY ProfileValue"
    },
    "db_type": "mssql",
    "db_connection_name": "am_db",
    "db_query_timing": "before_api"
}
```

**Query Naming Conventions:**
- `*_query` suffix for clarity (e.g., `monthlyPerformance_query`)
- Lowercase with underscores or camelCase supported
- Use descriptive names matching the data purpose

**Supported Query Name Patterns:**
| Pattern | Examples | Use Case |
|---------|----------|----------|
| Performance | `monthlyPerformance_query`, `performance`, `monthly_performance` | Time series data |
| Risk Bands | `riskBands_query`, `risk_bands`, `riskBands` | Configuration data |
| Default | `default` | Backward compatibility |

### 3. Create Your Validator Script

Create a Python script in `testdata/<service_name>/validators/`:

```python
# testdata/analyticsApiServices/validators/my_validator.py

from framework.common.logger import get_logger

logger = get_logger(__name__)


def validate(context):
    """
    Main validation function called by the script executor.
    
    Args:
        context: ScriptContext or dict containing:
            - test_case: Full test case configuration
            - request: Request details (endpoint, method, payload)
            - response: API response data
            - db_results: Database query results
            - extracted_vars: Previously extracted variables
            - config: Framework configuration
    
    Returns:
        dict with:
            - success: bool - whether validation passed
            - errors: List[str] - error messages if failed
            - extracted_values: Dict[str, Any] - values for extract_values
            - computed_values: Dict[str, Any] - computed expected values
    """
    # Handle both ScriptContext object and dict formats
    if hasattr(context, 'to_dict'):
        ctx = context.to_dict()
    else:
        ctx = context
    
    errors = []
    extracted_values = {}
    
    # Get data from context
    test_case = ctx.get('test_case', {})
    response = ctx.get('response', {})
    api_response = response.get('body') if isinstance(response, dict) else None
    
    # Perform your custom validation
    if api_response:
        # Example: validate a computed field
        actual_value = api_response.get('someField')
        expected_value = compute_expected_value(test_case.get('payload'))
        
        if actual_value != expected_value:
            errors.append(f"someField mismatch: actual={actual_value}, expected={expected_value}")
        
        # Store values for extract_values
        extracted_values['computed_value'] = expected_value
        extracted_values['actual_value'] = actual_value
    
    return {
        "success": len(errors) == 0,
        "errors": errors,
        "extracted_values": extracted_values,
        "computed_values": {
            "expected": expected_value
        }
    }


def compute_expected_value(payload):
    # Your custom computation logic
    return payload.get('input', 0) * 2
```

## ScriptContext Details

The script receives a `ScriptContext` object (or dict) with the following structure:

```python
{
    "test_case": {
        "test_id": "TC001",
        "endpoint": "/v1/analytics",
        "method": "POST",
        "payload": { ... },
        "expected_status": "200",
        "db_queries": {                      # Named queries (dict format)
            "monthlyPerformance_query": "SELECT ...",
            "riskBands_query": "SELECT ..."
        },
        # ... all other test case fields
    },
    "request": {
        "endpoint": "/v1/analytics",
        "method": "POST",
        "url": "https://api.example.com",
        "headers": {"Content-Type": "application/json"},
        "payload": { ... },
        "query_params": {}
    },
    "response": {
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": { ... },  # Parsed JSON response
        "text": "...",     # Raw response text
        "response_time_ms": 150
    },
    "db_results": {                          # Named query results (dict)
        "monthlyPerformance_query": [
            {"MonthId": "2024-01", "CLSTU6_Performance": 0.05, ...},
            ...
        ],
        "riskBands_query": [
            {"ProfileValue": 0, "AnnualStdDeviation": 0.00525},
            {"ProfileValue": 1, "AnnualStdDeviation": 0.06671},
            ...
        ],
        "default": [...]                     # Backward compatibility (first query)
    },
    "extracted_vars": {
        # Variables from previous test cases
        "user_id": "12345",
        "token": "abc..."
    },
    "config": {
        # Framework configuration
        "base_url": "https://api.example.com",
        # ...
    }
}
```

## ScriptResult Format

Your validator should return a dictionary with:

```python
{
    "success": True,          # Required: bool
    "errors": [],              # Required: List[str] - error messages
    "extracted_values": {      # Optional: values for extract_values
        "computed_volatility": 0.123,
        "risk_score": 3.5
    },
    "computed_values": {       # Optional: expected values (for reporting)
        "expectedVolatility": 0.123,
        "expectedRiskScore": 3.5
    },
    "comparison_data": {       # Optional: data for data_comparison
        "expected": { ... },
        "actual": { ... }
    },
    "metadata": {              # Optional: additional info
        "validator": "MyValidator",
        "execution_time_ms": 50
    }
}
```

## Using Class-Based Validators

For more complex validators, use the `BaseValidator` class:

```python
from framework.validators.base_validator import BaseValidator, ScriptResult, ScriptContext


class MyComplexValidator(BaseValidator):
    """
    Custom validator for complex business logic.
    """
    
    def validate(self, context: ScriptContext) -> ScriptResult:
        errors = []
        extracted_values = {}
        
        # Access context data
        api_response = context.response.body
        request_payload = context.test_case.get('payload')
        db_results = context.db_results
        
        # Use helper methods
        actual_value = self.extract_value(api_response, 'results.0.value')
        expected_value = self._compute_expected(request_payload)
        
        # Compare with tolerance
        is_match, error = self.compare_values(
            actual=actual_value,
            expected=expected_value,
            field_name="results.value",
            tolerance=0.001
        )
        
        if error:
            errors.append(error)
        
        extracted_values['computed_result'] = expected_value
        
        return ScriptResult(
            success=len(errors) == 0,
            errors=errors,
            extracted_values=extracted_values
        )
    
    def _compute_expected(self, payload):
        # Your business logic
        return sum(item['weight'] for item in payload.get('items', []))
```

## Extracting Values from Script Results

Use `"from": "script_result"` in `extract_values` to capture script outputs:

```json
{
    "extract_values": [
        {
            "from": "script_result",
            "key": "computed_volatility",
            "assign_to": "expected_volatility"
        },
        {
            "from": "script_result",
            "key": "actual_value",
            "assign_to": "api_volatility"
        }
    ]
}
```

These extracted values can then be used in:
- **Assertions**: `{"actual": "{{api_volatility}}", "expected": "{{expected_volatility}}"}`
- **Data comparison**: Reference in `data_comparison.fields_to_compare`
- **Subsequent test cases**: Values are stored globally

## Multiple Scripts

You can run multiple validators by providing an array:

```json
{
    "scripts": [
        "analyticsApiServices\\validators\\ewma_validator.py",
        "analyticsApiServices\\validators\\secondary_validator.py"
    ]
}
```

Results from all scripts are aggregated - if any fails, the overall result fails.

## Example: EWMA Blended Risk Validator

See [ewma_validator.py](../testdata/analyticsApiServices/validators/ewma_validator.py) for a complete example that:

1. Parses model weights from request payload
2. Fetches/parses model returns from database results (named query: `monthlyPerformance_query`)
3. Loads dynamic risk profile bands from database (named query: `riskBands_query`)
4. Computes expected EWMA volatility independently
5. Compares with API response values using tolerance-based matching
6. Returns computed values for assertions

### Named Query Access Pattern

```python
def validate(api_response, request_payload, db_results=None, config=None):
    """
    Validate using named database queries.
    
    Args:
        db_results: Dict with named query results
            - 'monthlyPerformance_query': Performance data rows
            - 'riskBands_query': Risk profile bands
            - 'default': First query result (backward compatibility)
    """
    # Access named queries with fallback patterns
    performance_data = (
        db_results.get('monthlyPerformance_query') or
        db_results.get('monthly_performance') or
        db_results.get('performance') or
        db_results.get('default')
    )
    
    risk_bands_data = (
        db_results.get('riskBands_query') or
        db_results.get('risk_bands_query') or
        db_results.get('risk_bands') or
        db_results.get('riskBands')
    )
    
    # Parse risk bands into format: {profile_id: volatility_threshold}
    if risk_bands_data:
        risk_profile_bands = _parse_risk_profile_bands(risk_bands_data)
        logger.info(f"Loaded {len(risk_profile_bands)} risk profile bands from database")
    else:
        risk_profile_bands = DEFAULT_RISK_PROFILE_BANDS
        logger.info("Using default risk profile bands")
```

### Logging Best Practices

Use ASCII-safe markers for Windows compatibility:

```python
# Good - ASCII safe
logger.info("[PASS] Validation successful")
logger.error("[FAIL] Validation failed")

# Avoid - Unicode may cause issues on Windows cp1252
# logger.info("✓ Validation successful")  
# logger.error("✗ Validation failed")

# Structured validation output
logger.info("=" * 80)
logger.info("VALIDATION SUMMARY:")
logger.info("=" * 80)
logger.info(f"Annualized Volatility:")
logger.info(f"  API Value:         {actual_vol}")
logger.info(f"  Computed Value:    {computed_vol}")
logger.info(f"  Difference:        {abs(actual_vol - computed_vol)}")
logger.info(f"  Status:            [PASS] Within tolerance")
logger.info("-" * 80)
```

## Best Practices

1. **Keep validators focused**: Each validator should test one specific aspect
2. **Use meaningful error messages**: Include actual and expected values
3. **Extract computed values**: Make them available for extract_values
4. **Handle missing data gracefully**: Return clear errors when required data is missing
5. **Use logging**: Import and use `get_logger(__name__)` for debugging
6. **Document your validator**: Add docstrings explaining the validation logic
7. **Test independently**: Validators can be tested outside the framework
8. **Use named queries**: Leverage `db_queries` dict for multiple data sources
9. **ASCII-safe logging**: Use `[PASS]`/`[FAIL]` instead of Unicode symbols
10. **Fallback patterns**: Support multiple query name formats for flexibility

## Reporting Integration

Validator results integrate with the reporting system:

### Report Locations

| Report Type | Format | Purpose |
|------------|--------|---------|
| HTML Report | `reports/<timestamp>/html_report_*.html` | Visual dashboard |
| JSON Report | `reports/<timestamp>/json_report_*.json` | Machine-readable |
| JUnit XML | `reports/<timestamp>/junit_report_*.xml` | CI/CD integration |
| Allure Results | `reports/<timestamp>/allure-results/` | Interactive reports |

### Validation Statistics

Script results contribute to validation statistics in reports:

```python
# Result structure captured for reporting
{
    "validation_stats": {
        "assertions": {"total": 3, "passed": 3, "failed": 0},
        "contract_checks": {"total": 1, "passed": 1, "failed": 0},
        "security_checks": {"total": 2, "passed": 2, "failed": 0},
        "data_comparisons": {"total": 1, "passed": 1, "failed": 0}
    }
}
```
