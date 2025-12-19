# TestCase Template

This file describes the structure and required fields for a test case JSON file.

## Overview
Test cases are defined in JSON format and support multiple protocols (REST, GraphQL, SOAP, gRPC), database validation, and data-driven testing with CSV files. The framework uses a modular approach with test_helpers for executing tests.

## Key Fields

### Core Test Identification
- `test_id`: Unique identifier for the test case (e.g., "TC001")
- `test_name`: Descriptive name of the test case
- `test_type`: Array of test types (e.g., ["functional", "regression", "performance"])
- `test_summary`: Short summary of the test case
- `protocol`: Protocol type (e.g., "REST", "GraphQL", "SOAP", "gRPC") - defaults to "REST"

### API Configuration
- `service_name`: **Unique identifier for the API service** being tested. Maps to `api_endpoints` in config
  - **Auto-generated** by `generate_testcases.py` from OpenAPI/Swagger spec title or filename
  - **Examples**: 
    - "Parties Service API 1.0" → "parties"
    - "Work Item Notification API" → "work_item_notification"
    - Swagger file "parties-api.json" → "parties"
  - **Must match** service name in `config/config.yaml` under `api_endpoints`
  - Enables multiple API endpoints with different auth tokens, timeouts, and base URLs
- `endpoint`: API endpoint to test (e.g., "/Party/{id}"). Supports Jinja2 templates: "{{variable}}"
- `method`: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
- `headers_additional`: Additional HTTP headers (merged with service defaults)
- `payload`: Request payload (supports Jinja2 templating)

### Database Validation
- `db_type`: Database type - "mssql", "postgresql", "mongodb", "cosmosdb", "sqlite"
- `db_connection_name`: Named connection from `db_connections` in config (e.g., "parties", "tracking_center")
- `db_query`: SQL/NoSQL query for validation. Supports Jinja2 templates: "{{variable}}"

### Data-Driven Testing
- `test_data_file`: Path to CSV file with test data (relative to testdata directory)
- Each CSV row generates a separate test execution with variable substitution

### Response Validation
- `expected_status`: Expected HTTP status code (e.g., "200", "404")
- `expected_response`: Expected response body (JSON object, string, or null)
- `expected_response_schema`: Path to JSON schema file for validation
- `extract_values`: Values to extract from response for use in subsequent tests
  - **Regular value extraction**: `{"from": "response", "key": "user.id", "assign_to": "userId"}`
  - **Record count extraction (REST/SOAP)**: `{"from": "response", "record_count": true, "array_path": "users", "assign_to": "userCount"}`
    - `record_count`: Boolean flag to enable array counting mode
    - `array_path`: Path to the array (supports dot notation for JSON and XPath for SOAP/XML)
      - **REST/JSON examples**: `"users"`, `"data.items"`, `"response.data.users"`
      - **SOAP/XML examples**: `"Body.Response.Users.User"`, `"//User"`, `"items"`
    - Works for both REST (JSON) and SOAP (XML) responses automatically
  - **Database extraction**: `{"from": "db_result", "query": "default", "assign": [{"key": "id", "assign_to": "dbId"}]}`
- `validate`: Validation configuration object
  - `status_code`: Expected status code validation
  - `schema_validation`: JSON schema validation
  - `data_comparison`: **Can be an array** for multiple comparisons or single object for backward compatibility
    - **Array format (NEW)**: Supports multiple comparisons with any combination of data sources
    - **Single object format (OLD)**: Single comparison for backward compatibility
    - **Supported data sources**: `api_response`, `api_request`, `db_result`, or context variables
    - **Configuration per comparison**:
      - **Field-level comparison (default)**:
        - `source`: Source data type (e.g., "api_response", "api_request", "db_result")
        - `target`: Target data type (e.g., "db_result", "api_response", "api_request")
        - `source_query`: Named query for source (when using db_result, default: "default")
        - `target_query`: Named query for target (when using db_result, default: "default")
        - `key_field`: Fields used to match records between source and target
        - `fields_to_compare`: Fields to compare (supports multiple formats)
        - `log_differences`: Boolean to log differences (default: true)
        - `comparison_name`: Descriptive name for the comparison
      - **Record count comparison (NEW)**:
        - `compare_record_count`: Boolean - set to `true` to enable record count comparison
        - `source_array_path`: Path to array in source data (empty `""` for top-level)
        - `target_array_path`: Path to array in target data (empty `""` for top-level)
        - `log_differences`: Boolean to log differences (default: true)
        - `comparison_name`: Descriptive name for the comparison
  - `performance`: Performance thresholds
  - `security`: Security checks

Copy this file and modify as needed for new test cases.

## Test Execution Flow

The framework uses modular test_helpers for executing tests:

1. **test_case_loader.py**: Loads and filters test cases from JSON files or directories
2. **test_client_manager.py**: Creates and manages API clients for different services
3. **test_context_manager.py**: Maintains test context and extracted variables
4. **test_db_manager.py**: Handles database connections and query execution
5. **test_payload_manager.py**: Renders payload templates with Jinja2
6. **test_validation_manager.py**: Validates responses against schemas and expectations
7. **test_result_collector.py**: Collects and organizes test results

## Service Name Generation

When using `generate_testcases.py` to auto-generate test cases from OpenAPI/Swagger specs, the `service_name` field is automatically populated:

```bash
# Generate from OpenAPI spec
python -m framework.generate_testcases openapi apiSpecs/parties-api.json testcases_autogenerated/parties/

# Generate from Postman collection
python -m framework.generate_testcases postman apiSpecs/UserCollection.postman_collection.json testcases_autogenerated/UserCollection/
```

**Service Name Derivation**:
1. **Input filename** (preferred): Extracts base name, removes common patterns
2. **API title** (fallback): Cleans up spec title field

**Transformation Rules**:
- Removes: "API", "Service", version numbers (v1, v2, 1.0, etc.)
- Converts: CamelCase → snake_case
- Sanitizes: Special characters removed, underscores normalized
- Max length: 30 characters
- Examples: 
  - "Parties Service API v1.0" → "parties"
  - "UserManagementAPI" → "user_management"

# TestCase_Template Protocol Field Guide

This guide explains which fields in the unified test case template are required or ignored for each supported protocol. Use this as a reference when creating or editing test cases in `TestCase_Template.json`.

## Protocol Field Requirements

- **protocol: "REST"**
  - **Required:** `method`, `endpoint`, `headers_additional`, `payload`, `expected_status`, `expected_response`, etc.
  - **Ignore:** `rpc_method`, `graphql_query`, `graphql_variables`, `soap_action`, `soap_envelope`

- **protocol: "gRPC"**
  - **Required:** `rpc_method`, `payload`, `expected_status`, `expected_response`, etc.
  - **Ignore:** `endpoint`, `graphql_query`, `graphql_variables`, `soap_action`, `soap_envelope`

- **protocol: "GraphQL"**
  - **Required:** `graphql_query`, `graphql_variables`, `expected_status`, `expected_response`, etc.
  - **Ignore:** `endpoint`, `rpc_method`, `soap_action`, `soap_envelope`

- **protocol: "SOAP"**
  - **Required:** `soap_action`, `soap_envelope`, `expected_status`, `expected_response`, etc.
  - **Ignore:** `endpoint`, `rpc_method`, `graphql_query`, `graphql_variables`

## Best Practice
- The test loader should ignore irrelevant fields based on the `protocol` value.
- Keep this file updated if you add new protocols or fields.

---

For questions or updates, contact the framework maintainers.

# Example Test Cases

## Example 1: GET /api/workitemnotification/v1/{aplid}
```json
{
    "test_id": "TC001",
    "service_name": "TEST12 - AssetMark - WorkItemNotification REST API 1.0",
    "workflow_mode": "parallel",
    "test_name": "GET /api/workitemnotification/v1/{aplid} [positive] (TC024)",
    "protocol": "REST",
    "test_type": ["Functional"],
    "mainURL": "{{api_base_url}}",
    "endpoint": "/api/workitemnotification/v1/{{aplid}}",
    "method": "GET",
    "headers_additional": {"Content-Type": "application/json"},
    "payload": null,
    "expected_status": "200",
    "expected_response_schema": "Workitemnotification\\schemas\\Schema_aplid_success.json",
    "expected_response": "Workitemnotification\\payloads\\Payload_aplid_response.json",
    "extract_values": [],
    "validate": {
        "performance": {"max_response_time_ms": 500},
        "security": {"checks": ["sql_injection", "xss"]},
        "data_comparison": {
            "source": "api_response",
            "target": "db_result",
            "format": "table",
            "key_field": ["id"],
            "fields_to_compare": ["name", "status"],
            "log_differences": true
        }
    },
    "test_data_file": "Workitemnotification\\data_driven\\Data_aplid.csv",
    "db_query": "",
    "db_type": "",
    "test_summary": "Test TC024: GET /api/workitemnotification/v1/{aplid} [positive] (TC024)"
}
```

## Example 2: POST /api/workitemnotification/v1/preferences/workitems/visibility
```json
{
    "test_id": "TC001",
    "service_name": "TEST12 - AssetMark - WorkItemNotification REST API 1.0",
    "workflow_mode": "parallel",
    "test_name": "POST /api/workitemnotification/v1/preferences/workitems/visibility [positive] (TC070)",
    "protocol": "REST",
    "test_type": ["Functional"],
    "mainURL": "{{api_base_url}}",
    "endpoint": "/api/workitemnotification/v1/preferences/workitems/visibility",
    "method": "POST",
    "headers_additional": {"Content-Type": "application/json"},
    "payload": "WorkItemNotification\\payloads\\Payload_preferences_workitems_visibility_request.json",
    "expected_status": "200",
    "expected_response_schema": "workitemnotification\\schemas\\Schema_preferences_workitems_visibility_success.json",
    "expected_response": "WorkItemNotification\\payloads\\Payload_preferences_workitems_visibility_response.json",
    "extract_values": [
        {"from": "response", "key": "success", "assign_to": "success_value"},
        {"from": "response", "record_count": true, "array_path": "data.items", "assign_to": "itemCount"},
        {"from": "db_result", "key": "0.APLID", "assign_to": "APLID_value"}
    ],
    "validate": {
        "performance": {"max_response_time_ms": 500},
        "security": {"checks": ["sql_injection", "xss"]},
        "data_comparison": {
            "source": "api_response",
            "target": "db_result",
            "format": "table",
            "key_field": ["id"],
            "fields_to_compare": [
                {"source": "status", "target": "db_status"},
                {"source": "name", "target": "db_name"}
            ],
            "log_differences": true
        }
    },
    "test_data_file": "",
    "db_query": "",
    "db_type": "",
    "test_summary": "Test TC070: POST /api/workitemnotification/v1/preferences/workitems/visibility [positive] (TC070)"
}
```

## fields_to_compare Variations

- As a list of strings (compare same-named fields):
```json
"fields_to_compare": ["name", "status"]
```
- As a list of mappings (compare different-named fields):
```json
"fields_to_compare": [
    {"source": "status", "target": "db_status"},
    {"source": "name", "target": "db_name"}
]
```
- As a single string (compare one field):
```json
"fields_to_compare": "name"
```
- As a single mapping:
```json
"fields_to_compare": {"source": "status", "target": "db_status"}
```

---

## Extract Values - Examples

The `extract_values` field supports extracting values from API responses and database results for use in subsequent tests. It now includes **record count extraction** for arrays in both REST (JSON) and SOAP (XML) responses.

### Example 1: Regular Value Extraction (REST)

```json
"extract_values": [
    {"from": "response", "key": "user.id", "assign_to": "userId"},
    {"from": "response", "key": "data.0.name", "assign_to": "firstName"}
]
```

### Example 2: Record Count Extraction (REST JSON)

```json
"extract_values": [
    {"from": "response", "record_count": true, "array_path": "users", "assign_to": "userCount"},
    {"from": "response", "record_count": true, "array_path": "data.items", "assign_to": "itemCount"}
]
```

**REST/JSON Response Example:**
```json
{
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "data": {
        "items": [
            {"sku": "A1"},
            {"sku": "A2"},
            {"sku": "A3"}
        ]
    }
}
```
- `userCount` will be `2`
- `itemCount` will be `3`

### Example 3: Record Count Extraction (SOAP XML)

```json
"extract_values": [
    {"from": "response", "record_count": true, "array_path": "Body.Response.Users.User", "assign_to": "userCount"},
    {"from": "response", "record_count": true, "array_path": "//Item", "assign_to": "itemCount"}
]
```

**SOAP/XML Response Example:**
```xml
<Envelope>
    <Body>
        <Response>
            <Users>
                <User><id>1</id><name>Alice</name></User>
                <User><id>2</id><name>Bob</name></User>
                <User><id>3</id><name>Charlie</name></User>
            </Users>
        </Response>
    </Body>
</Envelope>
```
- `userCount` will be `3`
- Supports both dot notation (`Body.Response.Users.User`) and XPath (`//User`)

### Example 4: Database Value Extraction

```json
"extract_values": [
    {
        "from": "db_result",
        "query": "default",
        "assign": [
            {"key": "0.APLID", "assign_to": "applicationId"},
            {"key": "0.Status", "assign_to": "dbStatus"}
        ]
    }
]
```

### Example 5: Database Record Count Extraction

```json
"extract_values": [
    {
        "from": "db_result",
        "record_count": true,
        "array_path": "",
        "assign_to": "dbRecordCount"
    }
]
```

**Database Result Example:**
```python
[
    {"id": 1, "name": "Alice", "status": "active"},
    {"id": 2, "name": "Bob", "status": "active"},
    {"id": 3, "name": "Charlie", "status": "inactive"}
]
```
- `dbRecordCount` will be `3`
- Leave `array_path` empty or use root path for top-level db_result arrays
- For nested db results, use dot notation: `"data.records"`

### Example 6: Combined Extraction (REST + DB + Record Count)

```json
"extract_values": [
    {"from": "response", "key": "success", "assign_to": "isSuccess"},
    {"from": "response", "record_count": true, "array_path": "data.users", "assign_to": "apiUserCount"},
    {"from": "db_result", "record_count": true, "array_path": "", "assign_to": "dbUserCount"},
    {"from": "db_result", "query": "audit_query", "assign": [{"key": "0.id", "assign_to": "auditId"}]}
]
```

**Use Case:** Compare API response count with database count for validation

**Key Features:**
- `record_count`: Boolean flag - set to `true` to enable array counting
- `array_path`: Path to the array (dot notation for JSON, XPath for XML)
  - For `db_result`: Leave empty `""` for top-level array, or use dot notation for nested data
  - For `response`: Use dot notation for JSON or XPath for XML
- Works automatically for REST (JSON), SOAP (XML), and database results
- Returns `0` if array not found or path is invalid

---

## Data Comparison Array - Extended Examples

The `data_comparison` field now supports an **array format** that enables multiple comparisons with any combination of data sources in a single test case.

### Supported Data Source Combinations

All combinations of the following data sources are supported:
- `api_response` - The response from the API call
- `api_request` - The request payload sent to the API
- `db_result` - Database query result (supports named queries via `source_query`/`target_query`)

### Example 1: Multiple Comparisons in Single Test

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "source_query": "default",
            "target_query": "default",
            "key_field": ["id"],
            "fields_to_compare": [
                {"source": "name", "target": "db_name"},
                {"source": "status", "target": "db_status"}
            ],
            "log_differences": true,
            "comparison_name": "Response vs Database comparison"
        },
        {
            "source": "api_request",
            "target": "api_response",
            "key_field": ["userId"],
            "fields_to_compare": ["email", "phone"],
            "log_differences": true,
            "comparison_name": "Request echo validation"
        }
    ]
}
```

### Example 2: API Request vs API Response

Validate that the API response contains all fields sent in the request:

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_request",
            "target": "api_response",
            "key_field": ["id"],
            "fields_to_compare": [
                {"source": "name", "target": "name"},
                {"source": "email", "target": "email"},
                {"source": "status", "target": "status"}
            ],
            "log_differences": true,
            "comparison_name": "Request fields in response"
        }
    ]
}
```

### Example 3: API Response vs DB Result (Named Queries)

Compare response with specific database query result:

```json
"db_queries": {
    "user_query": "SELECT id, name, email FROM users WHERE id = {{user_id}}",
    "audit_query": "SELECT * FROM audit_log WHERE user_id = {{user_id}}"
},
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "target_query": "user_query",
            "key_field": ["id"],
            "fields_to_compare": ["name", "email"],
            "log_differences": true,
            "comparison_name": "Response vs User table"
        }
    ]
}
```

### Example 4: DB Result vs DB Result

Compare results from two different database queries:

```json
"db_queries": {
    "source_db": "SELECT id, name FROM source_table WHERE active = 1",
    "target_db": "SELECT id, name FROM target_table WHERE synced = 1"
},
"validate": {
    "data_comparison": [
        {
            "source": "db_result",
            "target": "db_result",
            "source_query": "source_db",
            "target_query": "target_db",
            "key_field": ["id"],
            "fields_to_compare": ["name"],
            "log_differences": true,
            "comparison_name": "Source vs Target DB sync validation"
        }
    ]
}
```

### Example 5: API Request vs DB Result

Validate that request data was properly stored in database:

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_request",
            "target": "db_result",
            "target_query": "default",
            "key_field": ["userId"],
            "fields_to_compare": [
                {"source": "name", "target": "user_name"},
                {"source": "email", "target": "user_email"}
            ],
            "log_differences": true,
            "comparison_name": "Request data persisted in DB"
        }
    ]
}
```

---

## Record Count Comparison - NEW Feature

The `data_comparison` now supports **record count comparison** to validate that the number of records matches between different data sources.

### Example 1: API Response vs Database Record Count

Validate that API returns same number of records as database:

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "compare_record_count": true,
            "source_array_path": "users",
            "target_array_path": "",
            "log_differences": true,
            "comparison_name": "User count: API vs DB"
        }
    ]
}
```

**API Response:**
```json
{
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ]
}
```

**Database Result:**
```python
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]
```

**Result:** ✅ PASSED - Both have 3 records

### Example 2: Nested Array Count Comparison

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "compare_record_count": true,
            "source_array_path": "data.items",
            "target_array_path": "results",
            "log_differences": true,
            "comparison_name": "Item count comparison"
        }
    ]
}
```

### Example 3: SOAP Response vs Database Count

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "compare_record_count": true,
            "source_array_path": "Body.Response.Users.User",
            "target_array_path": "",
            "log_differences": true,
            "comparison_name": "SOAP user count vs DB"
        }
    ]
}
```

### Example 3b: Using Named Database Queries

```json
"db_queries": {
    "default": "SELECT * FROM users WHERE active = 1",
    "audit_query": "SELECT * FROM audit_users WHERE status = 'active'"
},
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "target_query": "audit_query",
            "compare_record_count": true,
            "source_array_path": "users",
            "target_array_path": "",
            "log_differences": true,
            "comparison_name": "API vs Audit table count"
        }
    ]
}
```

### Example 4: Database to Database Count Comparison

Compare record counts between two database queries:

```json
"db_queries": {
    "source_table": "SELECT * FROM source_users WHERE synced = 0",
    "target_table": "SELECT * FROM target_users WHERE imported = 1"
},
"validate": {
    "data_comparison": [
        {
            "source": "db_result",
            "target": "db_result",
            "source_query": "source_table",
            "target_query": "target_table",
            "compare_record_count": true,
            "source_array_path": "",
            "target_array_path": "",
            "log_differences": true,
            "comparison_name": "Source vs Target DB count"
        }
    ]
}
```

### Example 5: Combined Field and Count Comparison

Perform both field-level and count comparisons:

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_response",
            "target": "db_result",
            "compare_record_count": true,
            "source_array_path": "users",
            "target_array_path": "",
            "log_differences": true,
            "comparison_name": "User count validation"
        },
        {
            "source": "api_response",
            "target": "db_result",
            "key_field": [{"source": "id", "target": "id"}],
            "fields_to_compare": [
                {"source": "name", "target": "name"},
                {"source": "status", "target": "status"}
            ],
            "log_differences": true,
            "comparison_name": "User fields validation"
        }
    ]
}
```

### Record Count Comparison Configuration

- **`compare_record_count`**: Boolean - set to `true` to enable count comparison mode
- **`source_array_path`**: Path to array in source data
  - REST/JSON: Use dot notation (e.g., `"users"`, `"data.items"`)
  - SOAP/XML: Use dot notation or XPath (e.g., `"Body.Users.User"`, `"//User"`)
  - Database: Leave empty `""` for top-level, or use dot notation for nested
- **`target_array_path`**: Path to array in target data (same format as source)
- **`source`**: Source data type (`api_response`, `api_request`, or `db_result`)
- **`target`**: Target data type (`api_response`, `api_request`, or `db_result`)
- **`source_query`**: Named query for source (when using `db_result`)
- **`target_query`**: Named query for target (when using `db_result`)

### When to Use Record Count Comparison

- ✅ Validate API pagination returns expected number of records
- ✅ Ensure data sync between API and database
- ✅ Verify filtering/search operations return correct result count
- ✅ Validate bulk operations processed all records
- ✅ Compare SOAP response element counts with database

---

## Example 5: API Request vs DB Result (Original Content)

```json
"validate": {
    "data_comparison": [
        {
            "source": "api_request",
            "target": "db_result",
            "key_field": ["userId"],
            "fields_to_compare": [
                {"source": "name", "target": "user_name"},
                {"source": "email", "target": "email_address"}
            ],
            "log_differences": true,
            "comparison_name": "Request data persisted to DB"
        }
    ]
}
```

### Example 6: Backward Compatible Single Object Format

For backward compatibility, you can still use the single object format:

```json
"validate": {
    "data_comparison": {
        "source": "api_response",
        "target": "db_result",
        "key_field": ["id"],
        "fields_to_compare": ["name", "status"],
        "log_differences": true
    }
}
```

### Key Features

1. **Multiple Comparisons**: Execute multiple comparisons in sequence within a single test
2. **Any Combination**: Compare any data source with any other data source
3. **Named Queries**: Use `source_query` and `target_query` to specify which DB query result to use
4. **Descriptive Names**: Use `comparison_name` to identify each comparison in logs and reports
5. **Backward Compatible**: Old single-object format still works
6. **Flexible Field Mapping**: Supports direct field names or source/target mappings
7. **Nested Field Support**: Use dot notation for nested fields (e.g., "user.profile.email")

### Notes

- The `api_request` is automatically captured and stored in the test context before API execution
- DB query results are stored in context with their query names (or "default" for unnamed queries)
- All comparisons are executed in sequence; any failure will fail the entire test
- Each comparison logs its results independently for easier debugging
