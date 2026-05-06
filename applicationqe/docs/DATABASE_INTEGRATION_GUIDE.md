# Database Integration Quick Reference

## Structure

```
queries/
└── sql_queries.yaml          # Centralized SQL queries (all environments)

config/
├── env.test11.yaml           # Environment-specific DB config
├── env.test12.yaml
└── env.prod.yaml

tests/bdd/steps/
└── database_steps.py         # Reusable database step definitions
```

## Configuration

### 1. Add DB Connection to Environment File
**File:** `config/env.test11.yaml`

```yaml
database:
  azure_sql:
    server: "sqlwfitest.database.windows.net"
    database: "Transfer"
    username: "user@domain.com"
    password: "password"
    driver: "{ODBC Driver 17 for SQL Server}"
    authentication: "ActiveDirectoryPassword"
```

### 2. Add Queries to Central File
**File:** `queries/sql_queries.yaml`

```yaml
transfer:
  transfer_audit: "SELECT status, * FROM [dbo].[TransferInfoAudit]"
  transfer_by_id: "SELECT * FROM [dbo].[TransferInfo] WHERE TransferInfo_ID = ?"

roth_conversion:
  conversion_audit: "SELECT * FROM [dbo].[TransferInfoAudit] WHERE TransferType = 'Roth Conversion'"
```

## Usage in BDD Features

### Example 1: Simple Database Verification
```gherkin
Scenario: Verify Roth Conversion in database
  When I verify the Roth Conversion status in database
  Then the transfer status should be in the database
```

### Example 2: Verify Minimum Record Count
```gherkin
Scenario: Check transfer audit records
  When I verify the transfer status in database
  Then the database should contain at least 100 records
```

### Example 3: Generic Query Verification
```gherkin
Scenario: Custom database check
  When I verify the database using query from "transfer.transfer_audit"
  Then the database should contain records
```

## Available Step Definitions

### When Steps (Execute Query)
- `When I verify the Roth Conversion status in database`
- `When I verify the transfer status in database`
- `When I verify the account details in database`
- `When I verify the database using query from "<category>.<query_name>"`

### Then Steps (Verify Results)
- `Then the database should contain records`
- `Then the transfer status should be in the database`
- `Then the database should contain at least {count} records`

## Adding New Queries

### Step 1: Add Query to YAML
**File:** `queries/sql_queries.yaml`

```yaml
your_category:
  your_query: "SELECT * FROM [dbo].[YourTable]"
```

### Step 2: Use in Feature File
```gherkin
When I verify the database using query from "your_category.your_query"
Then the database should contain records
```

### Step 3 (Optional): Create Custom Step
**File:** `tests/bdd/steps/database_steps.py`

```python
@when("I verify the custom data in database")
def verify_custom_data(test_context):
    """Verify custom data in database"""
    verify_database_with_query(test_context, "your_category", "your_query")
```

## Parameterized Queries

For queries with parameters, use `?` placeholders:

```yaml
account:
  account_by_id: "SELECT * FROM [dbo].[Account] WHERE AccountNumber = ?"
```

Then in step definition:
```python
@when("I verify account {account_number} in database")
def verify_account_by_number(test_context, account_number):
    """Verify specific account"""
    db = SQLDatabase(...)
    db.connect()
    query = settings.database_queries.get("account", {}).get("account_by_id")
    results = db.execute_query(query, params=(account_number,))
    test_context["database_results"] = results
```

## Test Context

Database results are stored in `test_context["database_results"]` for further assertions:

```python
@then("the account status should be active")
def verify_account_active(test_context):
    results = test_context["database_results"]
    assert results[0].Status == "Active"
```

## Benefits

✅ **No Duplication** - Database logic in one place
✅ **Reusable** - Use across all BDD scenarios
✅ **Environment-Agnostic** - Queries work on all envs
✅ **Easy to Maintain** - Update query in one file
✅ **Type-Safe** - Centralized query definitions
