# Enhanced Framework Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Test Cases (JSON)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ service_name: "work_item_notification"                   │   │
│  │ db_type: "postgresql"                                    │   │
│  │ db_connection_name: "parties"                            │   │
│  │ db_query: "SELECT * FROM parties WHERE id = '{{id}}'"    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    test_api_generic.py                           │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Enhanced Client        │  │  Enhanced DB Integration     │  │
│  │  Fixture                │  │  - Supports all db_types     │  │
│  │  - Service name support │  │  - Named connections         │  │
│  │  - Multiple endpoints   │  │  - Auto query rendering      │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴────────────────────┐
          │                                        │
          ▼                                        ▼
┌──────────────────────┐                ┌──────────────────────────┐
│  ApiClientFactory    │                │  DatabaseClientFactory   │
│  ┌────────────────┐  │                │  ┌────────────────────┐  │
│  │ Client Pool    │  │                │  │ Connection Pool    │  │
│  │ - service1     │  │                │  │ - mssql:tc         │  │
│  │ - service2     │  │                │  │ - postgresql:p     │  │
│  │ - default      │  │                │  │ - mongodb:mc       │  │
│  └────────────────┘  │                │  └────────────────────┘  │
└──────────────────────┘                └──────────────────────────┘
          │                                        │
          ▼                                        ▼
┌──────────────────────┐                ┌──────────────────────────┐
│  config.TSADEV.yaml  │                │  config.TSADEV.yaml      │
│  ┌────────────────┐  │                │  ┌────────────────────┐  │
│  │ api_endpoints: │  │                │  │ db_connections:    │  │
│  │   service1:    │  │                │  │   mssql:           │  │
│  │     base_url   │  │                │  │     tracking_ctr   │  │
│  │     auth_token │  │                │  │   postgresql:      │  │
│  │     timeout    │  │                │  │     parties        │  │
│  │   service2:    │  │                │  │     securities     │  │
│  │     ...        │  │                │  │   mongodb:         │  │
│  └────────────────┘  │                │  │     main_cluster   │  │
└──────────────────────┘                │  └────────────────────┘  │
          │                              └──────────────────────────┘
          ▼                                        │
┌──────────────────────┐                          ▼
│  ApiClient           │                ┌──────────────────────────┐
│  - base_url          │                │  Database Clients        │
│  - auth_token        │                │  ┌────────────────────┐  │
│  - timeout           │                │  │ MSSQLClient        │  │
│  - retry_count       │                │  │ PostgreSQLClient   │  │
│  - request()         │                │  │ SQLiteClient       │  │
└──────────────────────┘                │  │ MongoDBClient      │  │
          │                              │  │ CosmosDBClient     │  │
          ▼                              │  └────────────────────┘  │
┌──────────────────────┐                │  All extend:             │
│  External APIs       │                │  DatabaseClient (ABC)    │
│  - Work Item Notif   │                └──────────────────────────┘
│  - User Service      │                          │
│  - Third Party       │                          ▼
└──────────────────────┘                ┌──────────────────────────┐
                                        │  Database Servers        │
                                        │  - MSSQL Server          │
                                        │  - PostgreSQL Server     │
                                        │  - MongoDB Cluster       │
                                        │  - CosmosDB Account      │
                                        │  - SQLite Files          │
                                        └──────────────────────────┘
```

## Component Relationships

### 1. Configuration Layer
```yaml
config.TSADEV.yaml
├── api_endpoints (Multiple API services)
│   ├── work_item_notification
│   ├── user_service
│   └── third_party_api
└── db_connections (Multiple database connections)
    ├── mssql
    │   ├── tracking_center
    │   └── another_db
    ├── postgresql
    │   ├── parties
    │   └── securities_hub
    ├── mongodb
    │   └── main_cluster
    ├── cosmosdb
    │   └── primary
    └── sqlite
        └── test_users
```

### 2. Factory Pattern
```
Test Case
    │
    ├── service_name ──────► ApiClientFactory.get_client(service_name)
    │                            │
    │                            ├── Load config
    │                            ├── Check pool (cache)
    │                            └── Return ApiClient
    │
    └── db_type + db_connection_name ──► DatabaseClientFactory.get_client(db_type, conn_name)
                                              │
                                              ├── Load config
                                              ├── Check pool (cache)
                                              ├── Substitute env vars
                                              └── Return specific client
                                                  (MSSQL/PostgreSQL/MongoDB/etc.)
```

### 3. Connection Flow

#### API Request Flow
```
1. Test fixture requests client(service_name)
2. ApiClientFactory checks pool
   - If exists: Return cached client
   - If not: Create new client
3. Load config.api_endpoints[service_name]
4. Substitute environment variables
5. Create ApiClient with config
6. Store in pool
7. Return to test
8. Test makes request
9. ApiClient handles retry logic
10. Returns response
```

#### Database Query Flow
```
1. Test case specifies db_type and db_connection_name
2. DatabaseClientFactory checks pool
   - If exists: Return cached connection
   - If not: Create new connection
3. Load config.db_connections[db_type][connection_name]
4. Substitute environment variables
5. Create specific client (MSSQL/PostgreSQL/etc.)
6. Auto-connect to database
7. Store in pool
8. Return to test
9. Test executes query
10. Results returned
11. Connection kept open (pooled)
12. At session end: All connections closed
```

## Data Flow Example

### Complete Test Execution Flow

```
1. pytest starts
   │
2. conftest.py loads config
   │
3. Test case loaded from JSON
   ├── service_name: "work_item_notification"
   ├── db_type: "postgresql"
   ├── db_connection_name: "parties"
   └── db_query: "SELECT * FROM parties WHERE id = '{{party_id}}'"
   │
4. Test fixture requests client
   │
5. ApiClientFactory.get_client('work_item_notification')
   ├── Load api_endpoints.work_item_notification
   ├── base_url: "https://..."
   ├── auth_token: "${WORK_ITEM_AUTH_TOKEN}" → "actual_token"
   └── Return ApiClient
   │
6. Make API request
   ├── GET https://.../api/parties/12345
   └── Response: {"partyId": "12345", "name": "ABC Corp"}
   │
7. DatabaseClientFactory.get_client('postgresql', 'parties')
   ├── Load db_connections.postgresql.parties
   ├── host: "psql-server.postgres.database.azure.com"
   ├── password: "${PG_PARTIES_PASSWORD}" → "actual_password"
   ├── Create PostgreSQLClient
   ├── Connect to database
   └── Return client
   │
8. Execute database query
   ├── Query: "SELECT * FROM parties WHERE id = '12345'"
   └── Result: [{"party_id": "12345", "party_name": "ABC Corp"}]
   │
9. Validate data comparison
   ├── API response vs DB result
   ├── Compare fields
   └── Test passes/fails
   │
10. Test completes
    │
11. Connection stays in pool (reused by next test)
    │
12. pytest session ends
    │
13. conftest.pytest_sessionfinish
    │
14. DatabaseClientFactory.close_all()
    └── All connections closed
```

## Key Design Patterns

### 1. Factory Pattern
- `DatabaseClientFactory` creates appropriate database clients
- `ApiClientFactory` creates configured API clients
- Centralizes object creation logic

### 2. Strategy Pattern
- `DatabaseClient` abstract base class
- Different strategies for different databases (MSSQL, PostgreSQL, etc.)
- Uniform interface: `query()`, `execute()`, `close()`

### 3. Singleton Pattern (Modified)
- Factory classes maintain singleton pools
- Connections reused across tests
- Cleared at session end

### 4. Template Method Pattern
- Base `DatabaseClient` defines workflow
- Subclasses implement specific connection logic
- Context manager support built-in

## Benefits of This Architecture

1. **Loose Coupling**: Tests don't know about database connection details
2. **High Cohesion**: Related functionality grouped in factories
3. **Open/Closed**: Easy to add new database types without changing existing code
4. **DRY**: Configuration centralized, no duplication
5. **Testability**: Easy to mock factories for unit testing
6. **Performance**: Connection pooling reduces overhead
7. **Maintainability**: Clear separation of concerns

## Environment Configuration

```
┌──────────────┐
│   .env       │
│  ENV_NAME=   │ ──────┐
│  TSADEV      │       │
└──────────────┘       │
                       ▼
┌─────────────────────────────────────┐
│  config.TSADEV.yaml                 │
│  ┌───────────────────────────────┐  │
│  │ db_connections:               │  │
│  │   postgresql:                 │  │
│  │     parties:                  │  │
│  │       password: "${PG_PWD}"   │◄─┼─── Environment Variable
│  └───────────────────────────────┘  │     Substitution
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  DatabaseClientFactory              │
│  _substitute_env_vars()             │
│  - Replaces ${PG_PWD} with actual   │
│  - Builds connection string         │
└─────────────────────────────────────┘
```

## Extension Points

### Adding New Database Type

1. Create new client class extending `DatabaseClient`
2. Implement `connect()`, `query()`, `execute()`, `close()`
3. Add to `DatabaseClientFactory.get_client()` switch
4. Add configuration schema to config YAML
5. Update documentation

### Adding New API Endpoint

1. Add to `api_endpoints` in config YAML
2. Use in test cases with `service_name`
3. No code changes needed!

---

This architecture provides a flexible, maintainable, and scalable foundation for testing multiple APIs and databases!
