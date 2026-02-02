# Enhanced Database and API Client Framework

This document describes the enhanced database and API client framework that supports multiple servers, database connections, and API endpoints with Azure AD authentication.

## Overview
The framework provides:
- **Multi-database support**: MSSQL, PostgreSQL, SQLite, MongoDB, CosmosDB
- **Multi-API endpoint support**: Configure multiple services with different auth, timeouts, and base URLs
- **Azure AD authentication**: Passwordless authentication for PostgreSQL and Azure APIs
- **Connection pooling**: Efficient resource management with factory pattern
- **Centralized configuration**: Environment-specific YAML configs with secrets support

## Table of Contents
- [Database Client](#database-client)
  - [Supported Databases](#supported-databases)
  - [Azure AD Authentication](#azure-ad-authentication)
  - [Configuration](#database-configuration)
  - [Usage Examples](#database-usage-examples)
- [API Client](#api-client)
  - [Multiple Service Support](#multiple-service-support)
  - [Configuration](#api-configuration)
  - [Usage Examples](#api-usage-examples)
- [Test Case Examples](#test-case-examples)
- [Test Helpers Integration](#test-helpers-integration)

---

## Database Client

### Supported Databases

The framework supports the following database types:
- **MSSQL** (Microsoft SQL Server)
- **PostgreSQL** (with Azure AD authentication support)
- **SQLite**
- **MongoDB** (requires `pymongo`)
- **CosmosDB** (requires `azure-cosmos`)

### Azure AD Authentication

The framework supports **Azure Active Directory (Azure AD) authentication** for:
- **PostgreSQL**: Authenticate to Azure Database for PostgreSQL using Azure AD tokens
- **API Endpoints**: Authenticate to Azure APIs using Azure AD tokens

**Prerequisites:**
- Azure CLI must be installed: https://aka.ms/installazurecliwindows
- User must be logged in: `az login`

**Benefits:**
- ✅ No need to store database passwords
- ✅ Token auto-refresh
- ✅ Centralized identity management
- ✅ Enhanced security with Azure AD
- ✅ Support for Managed Identities

### Database Configuration

Configure database connections in your `config.TSADEV.yaml` (or environment-specific config):

```yaml
db_connections:
  # MSSQL Connections - Multiple servers and databases
  mssql:
    tracking_center:
      driver: "ODBC Driver 17 for SQL Server"
      server: "t12ewmdba"
      database: "TrackingCenter"
      trusted_connection: true
    
    another_mssql_db:
      driver: "ODBC Driver 17 for SQL Server"
      server: "server2"
      database: "AnotherDB"
      user: "username"
      password: "${MSSQL_PASSWORD}"
  
  # PostgreSQL Connections - Multiple servers and databases
  postgresql:
    parties:
      host: "psql-custodialdataops-dev01-ncus.postgres.database.azure.com"
      port: 5432
      database: "parties"
      user: "psql-custodialdataops-dev01-ncus-parties-rw"
      password: "${PG_PARTIES_PASSWORD}"
      sslmode: "require"
    
    securities_hub:
      host: "psql-platform-dev01-ncus.postgres.database.azure.com"
      port: 5432
      database: "securitieshub"
      user: "psql-platform-dev01-ncus-securitieshub-ro"
      password: "${PG_SECURITIES_PASSWORD}"
      sslmode: "require"
    
    # Azure AD Authentication (no password needed)
    parties_azure_ad:
      host: "psql-server.postgres.database.azure.com"
      port: 5432
      database: "parties"
      user: "admin@azuread"  # Azure AD user
      password: "AZURE_AD"    # Placeholder - will use Azure AD token
      sslmode: "require"
      use_azure_auth: true    # Enable Azure AD authentication
  
  # CosmosDB Connections
  cosmosdb:
    primary:
      endpoint: "https://cosmos-primary-dev.documents.azure.com:443/"
      key: "${COSMOS_PRIMARY_KEY}"
      database: "main_db"
      container: "default_container"
  
  # MongoDB Connections
  mongodb:
    main_cluster:
      connection_string: "mongodb://${MONGO_USER}:${MONGO_PASSWORD}@mongo-main-dev.azure.com:27017/main_db?authSource=admin"
      database: "main_db"
      collection: "default_collection"
  
  # SQLite Connections
  sqlite:
    test_users:
      path: "testdata/users.db"
```

**Environment Variables:**
- Use `${VAR_NAME}` syntax to reference environment variables
- Environment variables are automatically substituted at runtime

### Database Usage Examples

#### 1. Using DatabaseClientFactory (Recommended)

```python
from framework.clients.db_client import DatabaseClientFactory

# Get MSSQL client for 'tracking_center' connection
db = DatabaseClientFactory.get_client('mssql', 'tracking_center')
results = db.query("SELECT * FROM users WHERE id = ?", (123,))
print(results)
# Don't close manually - factory manages connections

# Get PostgreSQL client for 'parties' connection
pg_db = DatabaseClientFactory.get_client('postgresql', 'parties')
results = pg_db.query("SELECT * FROM parties WHERE id = %s", (456,))
print(results)
```

#### 2. Using Azure AD Authentication for PostgreSQL

```python
from framework.clients.db_client import DatabaseClientFactory

# Connect to PostgreSQL using Azure AD authentication
# No password needed - uses Azure CLI login
db = DatabaseClientFactory.get_client('postgresql', 'parties_azure_ad')
results = db.query("SELECT * FROM parties WHERE status = %s", ('active',))
print(results)

# The framework automatically:
# 1. Checks if you're logged in to Azure CLI
# 2. Generates an access token for PostgreSQL
# 3. Uses the token instead of password
# 4. Connects securely to the database
```

**Prerequisites for Azure AD Authentication:**
```bash
# Install Azure CLI
# Download from: https://aka.ms/installazurecliwindows

# Login to Azure
az login

# Verify login
az account show

# Now you can use Azure AD authentication in your tests
```

#### 3. Using Context Manager

```python
from framework.clients.db_client import DatabaseClientFactory

# Context manager automatically manages connection
with DatabaseClientFactory.get_connection('mssql', 'tracking_center') as db:
    results = db.query("SELECT * FROM users")
    for row in results:
        print(row)
# Connection is automatically released (but kept in pool)
```

#### 3. Direct Client Usage

```python
from framework.clients.db_client import MSSQLClient, PostgreSQLClient

# MSSQL - Manual configuration
config = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'TestDB',
    'trusted_connection': True
}
db = MSSQLClient(config=config)
db.connect()
results = db.query("SELECT * FROM users")
db.close()

# PostgreSQL - Manual configuration
pg_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'testdb',
    'user': 'postgres',
    'password': 'password',
    'sslmode': 'prefer'
}
pg_db = PostgreSQLClient(config=pg_config)
pg_db.connect()
results = pg_db.query("SELECT * FROM users")
pg_db.close()
```

#### 4. NoSQL Databases

```python
from framework.clients.db_client import DatabaseClientFactory

# MongoDB
mongo_db = DatabaseClientFactory.get_client('mongodb', 'main_cluster')
results = mongo_db.query({'status': 'active'})

# CosmosDB
cosmos_db = DatabaseClientFactory.get_client('cosmosdb', 'primary')
results = cosmos_db.query("SELECT * FROM c WHERE c.status = 'active'")
```

#### 5. Closing All Connections

```python
from framework.clients.db_client import DatabaseClientFactory

# At the end of test session (automatically done in conftest.py)
DatabaseClientFactory.close_all()
```

---

## API Client

### API Configuration

Configure API endpoints in your `config.TSADEV.yaml`:

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
    verify: true
  
  # Azure AD authenticated API
  azure_resource_manager:
    base_url: "https://management.azure.com"
    auth_token: "AZURE_AD"  # Placeholder - will use Azure AD token
    timeout: 30
    retry_count: 3
    use_azure_auth: true    # Enable Azure AD authentication
    azure_resource: "https://management.azure.com/"  # Resource for token
  
  third_party_api:
    base_url: "https://api.external-service.com"
    auth_token: "${EXTERNAL_API_KEY}"
    timeout: 30
    retry_count: 3

# Legacy configuration (still supported)
api_base_url: "https://default-api.azurewebsites.net"
auth_token: "${DEFAULT_AUTH_TOKEN}"
```

### API Usage Examples

#### 1. Using ApiClientFactory (Recommended)

```python
from framework.clients.api_client import ApiClientFactory

# Get API client for specific service
client = ApiClientFactory.get_client('work_item_notification')
response = client.request('GET', '/api/workitems')
print(response.json())

# POST request
response = client.request('POST', '/api/workitems', json={
    'title': 'New Work Item',
    'status': 'pending'
})
```

#### 2. Using Default/Legacy Client

```python
from framework.clients.api_client import ApiClientFactory

# Uses api_base_url from config
client = ApiClientFactory.get_client()
response = client.request('GET', '/api/users')
```

#### 3. Direct ApiClient Usage

```python
from framework.clients.api_client import ApiClient

# Manual configuration
client = ApiClient(
    base_url='https://api.example.com',
    auth_token='your_token',
    timeout=30,
    retry_count=3,
    verify=False
)
response = client.request('GET', '/api/endpoint')
```

#### 4. Using Azure AD Authentication for APIs

```python
from framework.clients.api_client import ApiClientFactory

# Connect to Azure Resource Manager API using Azure AD
# No static token needed - uses Azure CLI login
client = ApiClientFactory.get_client('azure_resource_manager')
response = client.request('GET', '/subscriptions?api-version=2020-01-01')
print(response.json())

# The framework automatically:
# 1. Checks if you're logged in to Azure CLI
# 2. Generates an access token for the Azure resource
# 3. Uses the token in Authorization header
# 4. Makes authenticated API calls
```

**Supported Azure Resources for Token Generation:**
- `https://management.azure.com/` - Azure Resource Manager
- `https://ossrdbms-aad.database.windows.net` - PostgreSQL/MySQL
- `https://database.windows.net/` - Azure SQL
- `https://vault.azure.net` - Azure Key Vault
- `https://storage.azure.com/` - Azure Storage

**Configuration Example:**
```yaml
api_endpoints:
  azure_keyvault:
    base_url: "https://myvault.vault.azure.net"
    auth_token: "AZURE_AD"
    use_azure_auth: true
    azure_resource: "https://vault.azure.net"
```

---

## Test Case Examples

### Example 1: PostgreSQL with Azure AD Authentication

```json
{
  "test_id": "TC_DB_AZURE_001",
  "test_name": "Fetch Parties using Azure AD - PostgreSQL",
  "service_name": "work_item_notification",
  "endpoint": "/api/parties/{{party_id}}",
  "method": "GET",
  "db_type": "postgresql",
  "db_connection_name": "parties_azure_ad",
  "db_query": "SELECT * FROM parties WHERE party_id = '{{party_id}}'",
  "validate": {
    "data_comparison": {
      "source": "api_response",
      "key_field": ["partyId"],
      "fields_to_compare": [
        {"source": "name", "target": "party_name"},
        {"source": "status", "target": "status"}
      ]
    }
  }
}
```

**Config for Azure AD PostgreSQL:**
```yaml
db_connections:
  parties_azure_ad:
    type: postgresql
    host: "myserver.postgres.database.azure.com"
    database: "parties"
    username: "myuser@mydomain.com"
    password: "AZURE_AD"  # Triggers Azure AD auth
    port: 5432
    use_azure_auth: true

db_queries:
  parties_azure_ad:
    select: "SELECT * FROM parties WHERE created_date >= CURRENT_DATE - INTERVAL '30 days'"
```

### Example 2: API with Azure AD Authentication

```json
{
  "test_id": "TC_API_AZURE_001",
  "test_name": "List Azure Subscriptions using Azure AD",
  "service_name": "azure_resource_manager",
  "endpoint": "/subscriptions?api-version=2020-01-01",
  "method": "GET",
  "validate": {
    "status_code": 200,
    "schema_validation": {
      "value": ["object"],
      "value[0].subscriptionId": "string",
      "value[0].displayName": "string"
    }
  }
}
```

**Config for Azure AD API:**
```yaml
api_endpoints:
  azure_resource_manager:
    base_url: "https://management.azure.com"
    auth_token: "AZURE_AD"
    use_azure_auth: true
    azure_resource: "https://management.azure.com/"
```

### Example 3: MSSQL Database Query with API Validation

```json
{
  "test_id": "TC_DB_001",
  "test_name": "Validate User Data - MSSQL",
  "service_name": "user_service",
  "endpoint": "/api/users/{{user_id}}",
  "method": "GET",
  "db_type": "mssql",
  "db_connection_name": "tracking_center",
  "db_query": "SELECT * FROM Users WHERE UserId = '{{user_id}}'",
  "validate": {
    "data_comparison": {
      "source": "api_response",
      "key_field": ["userId"],
      "fields_to_compare": [
        {"source": "name", "target": "UserName"},
        {"source": "email", "target": "Email"}
      ]
    }
  }
}
```

### Example 4: PostgreSQL Database Query

```json
{
  "test_id": "TC_DB_002",
  "test_name": "Validate Party Data - PostgreSQL",
  "service_name": "work_item_notification",
  "endpoint": "/api/parties/{{party_id}}",
  "method": "GET",
  "db_type": "postgresql",
  "db_connection_name": "parties",
  "db_query": "SELECT * FROM parties WHERE party_id = '{{party_id}}'",
  "validate": {
    "data_comparison": {
      "source": "api_response",
      "key_field": ["partyId"],
      "fields_to_compare": [
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
  "test_id": "TC_DB_003",
  "test_name": "Validate Document - MongoDB",
  "service_name": "user_service",
  "endpoint": "/api/documents/{{doc_id}}",
  "method": "GET",
  "db_type": "mongodb",
  "db_connection_name": "main_cluster",
  "db_query": "{\"_id\": \"{{doc_id}}\", \"status\": \"active\"}",
  "validate": {
    "data_comparison": {
      "source": "api_response",
      "key_field": ["_id"],
      "fields_to_compare": ["title", "status", "createdDate"]
    }
  }
}
```

### Example 4: Multiple Database Connections in One Test

```python
# In test code
from framework.clients.db_client import DatabaseClientFactory

# Query MSSQL
mssql_db = DatabaseClientFactory.get_client('mssql', 'tracking_center')
users = mssql_db.query("SELECT * FROM Users WHERE Status = 'Active'")

# Query PostgreSQL
pg_db = DatabaseClientFactory.get_client('postgresql', 'parties')
parties = pg_db.query("SELECT * FROM parties WHERE user_id = %s", (user_id,))

# Cross-database validation
for user in users:
    party = next((p for p in parties if p['user_id'] == user['UserId']), None)
    assert party is not None, f"No party found for user {user['UserId']}"
```

### Example 5: Using Multiple API Endpoints

```python
# In test code
from framework.clients.api_client import ApiClientFactory

# Get user from user service
user_client = ApiClientFactory.get_client('user_service')
user_response = user_client.request('GET', '/api/users/123')
user_data = user_response.json()

# Create work item in notification service
notif_client = ApiClientFactory.get_client('work_item_notification')
work_item_response = notif_client.request('POST', '/api/workitems', json={
    'userId': user_data['id'],
    'title': 'Test Work Item'
})
```

---

## Key Features

### 1. Connection Pooling
- Database connections are pooled and reused across tests
- Reduces connection overhead and improves performance
- Automatically closed at end of test session

### 2. Environment Variable Substitution
- Use `${VAR_NAME}` in configuration files
- Automatically replaced with environment variables
- Supports secure credential management

### 3. Multiple Database Support
- SQL databases: MSSQL, PostgreSQL, SQLite
- NoSQL databases: MongoDB, CosmosDB
- Extensible architecture for adding new database types

### 4. Multiple API Endpoints
- Configure multiple API services in one config file
- Each service can have its own authentication, timeout, retry settings
- Automatic retry logic for failed requests

### 5. Backward Compatibility
- Legacy MSSQLClient and create_postgres_connection still work
- Gradual migration path to new factory pattern
- Old test cases continue to work without changes

---

## Best Practices

1. **Use Factory Pattern**: Always use `DatabaseClientFactory` and `ApiClientFactory` for production code
2. **Named Connections**: Use descriptive connection names (e.g., 'tracking_center', 'parties')
3. **Environment Variables**: Store sensitive data in environment variables, not in config files
4. **Connection Pooling**: Let the factory manage connections - don't close them manually in tests
5. **Error Handling**: Always wrap database/API calls in try-except blocks for better error messages
6. **Parameterized Queries**: Use parameterized queries to prevent SQL injection
7. **Context Managers**: Use `with DatabaseClientFactory.get_connection()` for temporary connections

---

## Troubleshooting

### Issue: "No configuration found for mssql:connection_name"
**Solution**: Ensure the connection name exists in your config file under `db_connections.mssql`

### Issue: "pymongo is required for MongoDB support"
**Solution**: Install pymongo: `pip install pymongo`

### Issue: "azure-cosmos is required for CosmosDB support"
**Solution**: Install azure-cosmos: `pip install azure-cosmos`

### Issue: Environment variables not substituted
**Solution**: Ensure environment variables are set before running tests. Check `.env` file.

### Issue: Connection timeout
**Solution**: Increase timeout in config or check network connectivity to database server

### Issue: Azure AD authentication fails
**Solution**: 
1. Verify Azure CLI is installed: `az --version`
2. Check Azure login status: `az account show`
3. Login if needed: `az login`
4. Verify correct subscription: `az account set --subscription <subscription-id>`

### Issue: "Azure authentication not available" error
**Solution**: 
1. Install Azure CLI from https://learn.microsoft.com/cli/azure/install-azure-cli
2. Ensure `framework/common/azure_auth.py` exists
3. If module import fails, check Python environment and dependencies

### Issue: Azure AD token expired
**Solution**: Azure CLI tokens auto-refresh. If issues persist:
```bash
az logout
az login
```

### Issue: Wrong Azure resource for token
**Solution**: Verify the `azure_resource` matches the service:
- PostgreSQL/MySQL: `https://ossrdbms-aad.database.windows.net`
- Azure Resource Manager: `https://management.azure.com/`
- Key Vault: `https://vault.azure.net`
- Azure SQL: `https://database.windows.net/`

---

## Migration Guide

### From Old MSSQLClient to Factory

**Before:**
```python
from framework.clients.db_client import MSSQLClient
db = MSSQLClient()
db.connect()
results = db.query("SELECT * FROM users")
db.close()
```

**After:**
```python
from framework.clients.db_client import DatabaseClientFactory
db = DatabaseClientFactory.get_client('mssql', 'tracking_center')
results = db.query("SELECT * FROM users")
# No need to close - factory manages connections
```

### From Old ApiClient to Factory

**Before:**
```python
from framework.clients.api_client import ApiClient
client = ApiClient(api_base_url, auth_token)
response = client.request('GET', '/api/users')
```

**After:**
```python
from framework.clients.api_client import ApiClientFactory
client = ApiClientFactory.get_client('user_service')
response = client.request('GET', '/api/users')
```

---

## Test Helpers Integration

The framework uses modular test_helpers for test execution. These helpers work seamlessly with the API and database clients:

### test_client_manager.py
- Manages API client pool using `ApiClientFactory`
- Creates clients based on `service_name` from test cases
- Handles authentication, timeouts, and retries per service

### test_db_manager.py
- Manages database connection pool using `DatabaseClientFactory`
- Executes queries specified in test cases
- Handles Jinja2 template rendering for dynamic queries
- Supports data comparison between API responses and DB results

### Example Test Case Integration

```json
{
  "test_id": "TC001",
  "service_name": "parties",
  "endpoint": "/api/parties/{{party_id}}",
  "method": "GET",
  "db_type": "postgresql",
  "db_connection_name": "parties",
  "db_query": "SELECT * FROM parties WHERE id = '{{party_id}}'",
  "validate": {
    "data_comparison": {
      "source": "api_response",
      "fields_to_compare": ["partyId", "name", "status"]
    }
  }
}
```

**Test Execution Flow:**
1. **test_case_loader** loads test case from JSON
2. **test_client_manager** creates API client for "parties" service
3. **test_payload_manager** renders endpoint with context variables
4. API request executed via **api_client**
5. **test_db_manager** creates DB client for PostgreSQL "parties" connection
6. **test_db_manager** renders and executes DB query
7. **test_validation_manager** compares API response with DB results
8. **test_result_collector** aggregates and reports results

---

## Installation Requirements

```bash
# Install all requirements
pip install -r requirements.txt

# Includes:
# - pyodbc (MSSQL)
# - psycopg2-binary (PostgreSQL)
# - azure-identity (Azure AD authentication)
# - requests (API client)
# - pyyaml (configuration)
# - jinja2 (templating)
# - pytest, allure-pytest (testing)
# - locust (performance testing)

# Optional: NoSQL databases (uncomment in requirements.txt)
# - pymongo (MongoDB)
# - azure-cosmos (CosmosDB)

# SQLite support is built-in with Python
```

---

## Support

For questions or issues with the enhanced database and API client framework:
- Review the main [README.md](../../README.md) for usage examples
- Check [ARCHITECTURE.md](../../ARCHITECTURE.md) for technical details
- Consult [TestCase_Enhanced_Reference.md](../../templates/TestCase_Enhanced_Reference.md) for test case examples
- Contact the framework maintainers or create an issue in the repository
