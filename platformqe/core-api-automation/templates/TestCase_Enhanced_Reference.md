# Test Case JSON Reference - Enhanced Database and API Support

## Quick Reference Guide

This guide shows how to configure test cases to use multiple database connections and API endpoints.

---

## Test Case Structure

```json
{
  "test_id": "TC001",
  "test_name": "Test Case Name",
  "test_type": ["functional", "regression"],
  "service_name": "work_item_notification",  // NEW: Specifies which API endpoint to use
  "endpoint": "/api/endpoint",
  "method": "GET",
  
  // Database configuration (NEW)
  "db_type": "mssql",                        // Database type: mssql, postgresql, mongodb, cosmosdb, sqlite
  "db_connection_name": "tracking_center",   // Named connection from config
  "db_query": "SELECT * FROM table WHERE id = '{{variable}}'",
  
  // Validation configuration
  "validate": {
    "data_comparison": {
      "source": "api_response",              // or "api_request"
      "key_field": ["id"],
      "fields_to_compare": [
        {"source": "apiField", "target": "dbField"}
      ]
    }
  }
}
```

---

## Field Descriptions

### service_name (NEW)
Specifies which API endpoint configuration to use from `config.yaml`:
- Maps to `api_endpoints.<service_name>` in config
- Each service can have its own base_url, auth_token, timeout, retry_count
- If not specified, uses legacy `api_base_url` from config

**Example:**
```json
"service_name": "work_item_notification"
```

Maps to config:
```yaml
api_endpoints:
  work_item_notification:
    base_url: "https://app-workitemnotifsvc-test-test12.azurewebsites.net"
    auth_token: "${WORK_ITEM_AUTH_TOKEN}"
```

### db_type (NEW)
Specifies the type of database to query. Supported values:
- `mssql` - Microsoft SQL Server
- `postgresql` (or `postgres`) - PostgreSQL
- `mongodb` - MongoDB (requires pymongo)
- `cosmosdb` - Azure CosmosDB (requires azure-cosmos)
- `sqlite` - SQLite

**Example:**
```json
"db_type": "postgresql"
```

### db_connection_name (NEW)
Specifies which named connection to use from the config file.

**Example:**
```json
"db_connection_name": "parties"
```

Maps to config:
```yaml
db_connections:
  postgresql:
    parties:
      host: "psql-server.postgres.database.azure.com"
      database: "parties"
      user: "username"
      password: "${PG_PASSWORD}"
```

### db_query
SQL or NoSQL query to execute against the database.
- Supports Jinja2 template variables: `{{variable_name}}`
- For SQL databases: Standard SQL syntax
- For MongoDB: JSON filter query
- For CosmosDB: SQL API query

**SQL Example:**
```json
"db_query": "SELECT * FROM Users WHERE UserId = '{{user_id}}' AND Status = 'Active'"
```

**MongoDB Example:**
```json
"db_query": "{\"userId\": \"{{user_id}}\", \"status\": \"active\"}"
```

---

## Complete Test Case Examples

### Example 1: PostgreSQL with Azure AD Authentication

```json
{
  "test_id": "TC_AZURE_PG_001",
  "test_name": "Validate Party Data with Azure AD PostgreSQL",
  "test_type": ["functional", "azure_auth"],
  "service_name": "work_item_notification",
  "endpoint": "/api/parties/{{party_id}}",
  "method": "GET",
  "test_data_file": "WorkItemNotification/party_test_data.csv",
  
  "db_type": "postgresql",
  "db_connection_name": "parties_azure_ad",
  "db_query": "SELECT party_id, party_name, email, status FROM parties WHERE party_id = '{{party_id}}'",
  
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "key_field": ["partyId"],
      "fields_to_compare": [
        {"source": "partyId", "target": "party_id"},
        {"source": "name", "target": "party_name"},
        {"source": "email", "target": "email"},
        {"source": "status", "target": "status"}
      ]
    }
  }
}
```

**Required Config (config.yaml):**
```yaml
db_connections:
  parties_azure_ad:
    type: postgresql
    host: "myserver.postgres.database.azure.com"
    database: "parties"
    username: "myuser@mydomain.com"
    password: "AZURE_AD"  # Triggers Azure AD authentication
    port: 5432
    use_azure_auth: true

api_endpoints:
  work_item_notification:
    base_url: "https://app-workitemnotifsvc-test.azurewebsites.net"
    auth_token: "${WORK_ITEM_AUTH_TOKEN}"
```

**Prerequisites:**
- Azure CLI installed: `az --version`
- Logged in to Azure: `az login`
- User has Azure AD database permissions

### Example 2: Azure API with Azure AD Token

```json
{
  "test_id": "TC_AZURE_API_001",
  "test_name": "List Azure Subscriptions using Azure AD",
  "test_type": ["functional", "azure_auth"],
  "service_name": "azure_resource_manager",
  "endpoint": "/subscriptions?api-version=2020-01-01",
  "method": "GET",
  
  "validate": {
    "status_code": 200,
    "schema_validation": {
      "value": ["object"],
      "value[0].subscriptionId": "string",
      "value[0].displayName": "string",
      "value[0].state": "string"
    }
  }
}
```

**Required Config:**
```yaml
api_endpoints:
  azure_resource_manager:
    base_url: "https://management.azure.com"
    auth_token: "AZURE_AD"
    use_azure_auth: true
    azure_resource: "https://management.azure.com/"
```

### Example 3: MSSQL Query with API Validation

```json
{
  "test_id": "TC_USER_001",
  "test_name": "Validate User Data from MSSQL",
  "test_type": ["functional", "database"],
  "service_name": "user_service",
  "endpoint": "/api/users/{{user_id}}",
  "method": "GET",
  "test_data_file": "UserService/user_test_data.csv",
  
  "db_type": "mssql",
  "db_connection_name": "tracking_center",
  "db_query": "SELECT UserId, UserName, Email, IsActive FROM Users WHERE UserId = '{{user_id}}'",
  
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "key_field": ["userId"],
      "fields_to_compare": [
        {"source": "userId", "target": "UserId"},
        {"source": "name", "target": "UserName"},
        {"source": "email", "target": "Email"},
        {"source": "isActive", "target": "IsActive"}
      ]
    }
  }
}
```

### Example 3: MSSQL Query with API Validation

```json
{
  "test_id": "TC_USER_001",
  "test_name": "Validate User Data from MSSQL",
  "test_type": ["functional", "database"],
  "service_name": "user_service",
  "endpoint": "/api/users/{{user_id}}",
  "method": "GET",
  "test_data_file": "UserService/user_test_data.csv",
  
  "db_type": "mssql",
  "db_connection_name": "tracking_center",
  "db_query": "SELECT UserId, UserName, Email, IsActive FROM Users WHERE UserId = '{{user_id}}'",
  
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "key_field": ["userId"],
      "fields_to_compare": [
        {"source": "userId", "target": "UserId"},
        {"source": "name", "target": "UserName"},
        {"source": "email", "target": "Email"},
        {"source": "isActive", "target": "IsActive"}
      ]
    }
  }
}
```

### Example 4: PostgreSQL Query

```json
{
  "test_id": "TC_PARTY_001",
  "test_name": "Validate Party Data from PostgreSQL",
  "test_type": ["functional", "database"],
  "service_name": "work_item_notification",
  "endpoint": "/api/parties/{{party_id}}",
  "method": "GET",
  
  "db_type": "postgresql",
  "db_connection_name": "parties",
  "db_query": "SELECT party_id, party_name, party_type, created_date FROM parties WHERE party_id = '{{party_id}}'",
  
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "key_field": ["partyId"],
      "fields_to_compare": [
        {"source": "partyId", "target": "party_id"},
        {"source": "partyName", "target": "party_name"},
        {"source": "partyType", "target": "party_type"}
      ]
    }
  }
}
```

### Example 3: MongoDB Query

```json
{
  "test_id": "TC_DOC_001",
  "test_name": "Validate Document from MongoDB",
  "test_type": ["functional", "nosql"],
  "service_name": "document_service",
  "endpoint": "/api/documents/{{doc_id}}",
  "method": "GET",
  
  "db_type": "mongodb",
  "db_connection_name": "main_cluster",
  "db_query": "{\"_id\": \"{{doc_id}}\", \"status\": \"published\"}",
  
  "validate": {
    "status_code": 200,
    "data_comparison": {
      "source": "api_response",
      "key_field": ["_id"],
      "fields_to_compare": ["title", "status", "author", "publishedDate"]
    }
  }
}
```

### Example 4: Multiple Database Connections

```json
{
  "test_id": "TC_CROSS_001",
  "test_name": "Cross-Database Validation",
  "test_type": ["functional", "integration"],
  "service_name": "user_service",
  "endpoint": "/api/users/{{user_id}}/parties",
  "method": "GET",
  
  // First DB query - MSSQL
  "db_type": "mssql",
  "db_connection_name": "tracking_center",
  "db_query": "SELECT UserId, UserName FROM Users WHERE UserId = '{{user_id}}'",
  
  // Additional queries can be done in custom validation
  "custom_validations": [
    {
      "db_type": "postgresql",
      "db_connection_name": "parties",
      "db_query": "SELECT * FROM parties WHERE user_id = '{{user_id}}'"
    }
  ],
  
  "validate": {
    "status_code": 200
  }
}
```

### Example 5: No Database Query (API Only)

```json
{
  "test_id": "TC_API_001",
  "test_name": "API Test Without Database",
  "test_type": ["api", "smoke"],
  "service_name": "work_item_notification",
  "endpoint": "/api/health",
  "method": "GET",
  
  // No db_type or db_query - pure API test
  
  "validate": {
    "status_code": 200,
    "response_schema": {
      "type": "object",
      "properties": {
        "status": {"type": "string"},
        "version": {"type": "string"}
      }
    }
  }
}
```

---

## Configuration File Structure

### api_endpoints (NEW)

```yaml
api_endpoints:
  work_item_notification:
    base_url: "https://app-workitemnotifsvc-test-test12.azurewebsites.net"
    auth_token: "${WORK_ITEM_AUTH_TOKEN}"
    timeout: 30
    retry_count: 3
    verify: false
  
  user_service:
    base_url: "https://api-users-dev.azurewebsites.net"
    auth_token: "${USER_SERVICE_TOKEN}"
    timeout: 60
    retry_count: 5
```

### db_connections (NEW)

```yaml
db_connections:
  mssql:
    tracking_center:
      driver: "ODBC Driver 17 for SQL Server"
      server: "t12ewmdba"
      database: "TrackingCenter"
      trusted_connection: true
    
    another_db:
      driver: "ODBC Driver 17 for SQL Server"
      server: "server2"
      database: "AnotherDB"
      user: "username"
      password: "${MSSQL_PASSWORD}"
  
  postgresql:
    parties:
      host: "psql-server.postgres.database.azure.com"
      port: 5432
      database: "parties"
      user: "username"
      password: "${PG_PARTIES_PASSWORD}"
      sslmode: "require"
  
  mongodb:
    main_cluster:
      connection_string: "mongodb://${MONGO_USER}:${MONGO_PASSWORD}@server:27017/db"
      database: "main_db"
      collection: "default_collection"
  
  sqlite:
    test_db:
      path: "testdata/test.db"
```

---

## Variable Substitution

All query strings and endpoint URLs support Jinja2 template variables:

**Test Data (CSV):**
```csv
user_id,expected_name
12345,John Doe
67890,Jane Smith
```

**Test Case:**
```json
{
  "endpoint": "/api/users/{{user_id}}",
  "db_query": "SELECT * FROM Users WHERE UserId = '{{user_id}}' AND Name = '{{expected_name}}'"
}
```

**Rendered (for first row):**
- Endpoint: `/api/users/12345`
- Query: `SELECT * FROM Users WHERE UserId = '12345' AND Name = 'John Doe'`

---

## Backward Compatibility

### Legacy Format (Still Supported)

**Old test case format:**
```json
{
  "test_id": "TC001",
  "endpoint": "/api/users",
  "method": "GET",
  "db_type": "mssql",  // Will use first/default MSSQL connection
  "db_query": "SELECT * FROM Users"
}
```

**Old config format:**
```yaml
api_base_url: "https://api.example.com"
auth_token: "${AUTH_TOKEN}"
db_connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server;DATABASE=db;Trusted_Connection=yes;"
```

---

## Best Practices

1. **Named Connections**: Use descriptive connection names (e.g., 'tracking_center', 'parties')
2. **Service Names**: Use meaningful service names (e.g., 'user_service', 'work_item_notification')
3. **Environment Variables**: Store credentials in environment variables using `${VAR_NAME}` syntax
4. **Parameterized Queries**: Use `{{variable}}` for dynamic values to prevent SQL injection
5. **Test Data Files**: Store test data in CSV files and reference them with `test_data_file`
6. **Query Comments**: Add comments in SQL for complex queries (database-specific syntax)

---

## Common Patterns

### Pattern 1: API Response vs Database Comparison
```json
"validate": {
  "data_comparison": {
    "source": "api_response",
    "key_field": ["id"],
    "fields_to_compare": [
      {"source": "apiFieldName", "target": "db_column_name"}
    ]
  }
}
```

### Pattern 2: API Request vs Database Comparison
```json
"validate": {
  "data_comparison": {
    "source": "api_request",  // Compare what was sent vs what's in DB
    "key_field": ["id"],
    "fields_to_compare": ["field1", "field2"]
  }
}
```

### Pattern 3: Multiple Fields as Key
```json
"validate": {
  "data_comparison": {
    "key_field": ["userId", "accountId"],  // Composite key
    "fields_to_compare": ["status", "balance"]
  }
}
```

---

## Troubleshooting

### Error: "No configuration found for mssql:connection_name"
**Fix**: Add the connection to `db_connections.mssql` in your config file

### Error: "API endpoint 'service_name' not found"
**Fix**: Add the service to `api_endpoints` in your config file

### Error: "pymongo is required for MongoDB support"
**Fix**: Run `pip install pymongo`

### Query not rendering variables
**Fix**: Use double curly braces: `{{variable}}` not `{variable}`

### Connection timeout
**Fix**: Increase timeout in api_endpoints config or check network connectivity

---

## Quick Command Reference

```bash
# Run tests for specific service
pytest --service-name work_item_notification

# Run tests with specific test type
pytest --test-type functional

# Run specific test case
pytest --test-id TC001

# Run tests with specific test case file
pytest --testcase-file testdata/my_test_cases.json
```

---

## Summary

The enhanced framework provides:
- ✅ Multiple database type support (MSSQL, PostgreSQL, MongoDB, CosmosDB, SQLite)
- ✅ Named database connections for easy switching
- ✅ Multiple API endpoints with individual configurations
- ✅ Connection pooling for better performance
- ✅ Environment variable substitution for security
- ✅ Backward compatibility with existing test cases
- ✅ Automatic connection management and cleanup

Start using the new features by adding `service_name`, `db_type`, and `db_connection_name` to your test cases!
