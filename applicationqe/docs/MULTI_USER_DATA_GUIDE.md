# Multi-User Test Data Management Guide

## Overview

This guide explains how to manage multiple test data sets and multi-user session handling in the framework.

---

## CSV Data Structure

### Current Implementation

**File**: `data/test_data.test11.csv`

```csv
username,password,client_id,account_name,destination_account,conversion_amount,user_type,test_scenario
T11_AGA1G1_Perf,QAAdminUser_33a,13222266,Carmen E Tucker Individual,13443983,1000,advisor,add_ach
T11_User2_Test,QAAdminUser_33a,13222267,John Doe IRA,13443984,2000,client,roth_conversion
T11_User3_Test,QAAdminUser_33a,13222268,Jane Smith Trust,13443985,3000,admin,account_management
```

**Benefits:**
- ✅ Multiple users for different test scenarios
- ✅ Each user can have unique test data
- ✅ Support for data-driven testing
- ✅ Easy to add new users without code changes

---

## Test Data Fixtures

### 1. `test_data_all` - All Rows (Session Scope)

```python
@pytest.fixture(scope="session")
def test_data_all():
    """Load ALL rows from CSV - loaded once per session"""
    # Returns: [
    #   {"username": "T11_AGA1G1_Perf", "password": "...", ...},
    #   {"username": "T11_User2_Test", "password": "...", ...},
    #   {"username": "T11_User3_Test", "password": "...", ...}
    # ]
```

### 2. `test_data` - First Row (Backward Compatibility)

```python
@pytest.fixture(scope="session")
def test_data(test_data_all):
    """Get first row - for existing tests"""
    # Returns: {"username": "T11_AGA1G1_Perf", "password": "...", ...}
```

### 3. Helper Functions

```python
# Get data by username
get_test_data_by_username(test_data_all, "T11_User2_Test")

# Get data by index
get_test_data_by_index(test_data_all, 1)  # Second row
```

---

## Usage Examples

### Example 1: Use Default User (Existing Tests)

```python
@when("I search for account")
def search_account(test_data, account_list_page):
    # Uses first row from CSV (T11_AGA1G1_Perf)
    account_no = test_data.get("client_id")
    account_list_page.search(account_no)
```

**Session File Created**: `tests/.auth/ewm_T11_AGA1G1_Perf_gw0.json`

---

### Example 2: Use Specific User by Username

```python
from tests.ui_fixtures.data_fixtures import get_test_data_by_username

@when("I login as client user")
def login_as_client(test_data_all, authenticated_page):
    # Get specific user data
    client_data = get_test_data_by_username(test_data_all, "T11_User2_Test")

    # authenticated_page will use client_data credentials
    # Session file: tests/.auth/ewm_T11_User2_Test_gw0.json
```

---

### Example 3: Parametrize Tests with Multiple Users

```python
import pytest
from tests.ui_fixtures.data_fixtures import get_test_data_by_index

@pytest.mark.parametrize("user_index", [0, 1, 2])
def test_multi_user_scenario(user_index, test_data_all, authenticated_page):
    """Test runs 3 times with different users"""
    user_data = get_test_data_by_index(test_data_all, user_index)

    print(f"Testing with user: {user_data['username']}")
    print(f"User type: {user_data['user_type']}")

    # Each user gets their own session file
    # tests/.auth/ewm_T11_AGA1G1_Perf_gw0.json
    # tests/.auth/ewm_T11_User2_Test_gw0.json
    # tests/.auth/ewm_T11_User3_Test_gw0.json
```

---

### Example 4: BDD with Multiple Users

**Feature File**: `tests/bdd/features/multi_user.feature`

```gherkin
@multi_user
Feature: Multi-user account management

  Scenario Outline: Test with different user roles
    Given I am logged in as "<user_type>" user
    When I perform account operation
    Then operation should succeed for "<user_type>"

  Examples:
    | user_type |
    | advisor   |
    | client    |
    | admin     |
```

**Step Definition**:

```python
from tests.ui_fixtures.data_fixtures import get_test_data_by_username

@given('I am logged in as "{user_type}" user')
def login_as_user_type(user_type, test_data_all, authenticated_page):
    # Find user by user_type column
    user_data = next(
        (row for row in test_data_all if row['user_type'] == user_type),
        None
    )

    if not user_data:
        raise ValueError(f"No user found with type: {user_type}")

    # authenticated_page will handle login with this user's credentials
    # Each user gets separate session file
```

---

## Session Management for Multiple Users

### How It Works

**Session File Naming**: `{app}_{username}_{worker}.json`

**Example Files Created**:
```
tests/.auth/
├── ewm_T11_AGA1G1_Perf_gw0.json     # User 1, Worker 0
├── ewm_T11_User2_Test_gw0.json      # User 2, Worker 0
├── ewm_T11_User3_Test_gw0.json      # User 3, Worker 0
├── ewm_T11_AGA1G1_Perf_gw1.json     # User 1, Worker 1 (parallel)
└── ewm_T11_User2_Test_gw1.json      # User 2, Worker 1 (parallel)
```

### Key Points

1. **Each Username = Separate Session**
   - User `T11_AGA1G1_Perf` → Session file `ewm_T11_AGA1G1_Perf_gw0.json`
   - User `T11_User2_Test` → Session file `ewm_T11_User2_Test_gw0.json`
   - **Both sessions maintained simultaneously** ✅

2. **Session Reuse**
   - If test uses same username again, existing session is reused
   - No re-login needed unless session expired (> 8 hours)

3. **Parallel Execution**
   - Each worker (gw0, gw1, etc.) gets its own session files
   - Prevents session conflicts in parallel runs

4. **Session Expiry**
   - Sessions expire after 8 hours
   - Expired sessions are deleted and re-created automatically

---

## Advanced: Dynamic User Selection

### Use Case: Test with Random User

```python
import random
from tests.ui_fixtures.data_fixtures import get_test_data_by_index

@pytest.fixture
def random_test_user(test_data_all):
    """Get random user from CSV"""
    index = random.randint(0, len(test_data_all) - 1)
    return get_test_data_by_index(test_data_all, index)

def test_with_random_user(random_test_user, authenticated_page):
    print(f"Testing with: {random_test_user['username']}")
    # Session file created for this specific user
```

---

## Best Practices

### ✅ DO:

1. **Add descriptive columns** to CSV for easy filtering:
   ```csv
   username,password,user_type,test_scenario,role,permissions
   ```

2. **Use meaningful usernames** that indicate purpose:
   ```
   T11_Advisor_HighValue    # For advisor tests with high-value accounts
   T11_Client_Restricted    # For client with restrictions
   ```

3. **Group related test data** by adding identifier columns:
   ```csv
   username,password,test_group,priority
   User1,Pass1,smoke,high
   User2,Pass2,regression,medium
   ```

4. **Use helper functions** for clean code:
   ```python
   def get_advisor_user(test_data_all):
       return next(row for row in test_data_all if row['user_type'] == 'advisor')
   ```

### ❌ DON'T:

1. **Don't hardcode usernames** in test code:
   ```python
   # Bad
   username = "T11_AGA1G1_Perf"

   # Good
   username = test_data.get("username")
   ```

2. **Don't reload CSV** in test functions:
   ```python
   # Bad - CSV already loaded!
   with open("data.csv") as f:
       data = csv.DictReader(f)

   # Good - Use fixture
   def test(test_data_all):
       ...
   ```

3. **Don't share sessions** between different users:
   - Framework handles this automatically
   - Each username gets its own session file

---

## Migration Guide

### Updating Existing Tests

**Old Approach** (single row):
```python
def test_example(test_data):
    username = test_data.get("username")
```

**New Approach** (still works - backward compatible):
```python
def test_example(test_data):
    username = test_data.get("username")  # Still uses first row
```

**New Approach** (multiple users):
```python
def test_example(test_data_all):
    # Use specific user
    user2 = get_test_data_by_index(test_data_all, 1)
    username = user2.get("username")
```

---

## Performance Metrics

### CSV Loading Performance

| Scenario | Before | After |
|----------|--------|-------|
| 1 test | 1 CSV read | 1 CSV read (session) |
| 100 tests | 100 CSV reads | 1 CSV read (session) |
| 1000 tests | 1000 CSV reads | 1 CSV read (session) |

**Improvement**: **99.9% reduction** in file I/O for large test suites! 🚀

### Session File Performance

| Users | Sessions Created | Login Operations |
|-------|------------------|------------------|
| 1 user, 100 tests | 1 | 1 (reused 99 times) |
| 3 users, 100 tests | 3 | 3 (each reused ~33 times) |
| 3 users, 4 workers | 12 | 12 (parallel isolation) |

---

## Troubleshooting

### Issue: Test using wrong user

**Problem**: Test is using first user instead of intended user

**Solution**: Make sure to inject `test_data_all` and select specific user:
```python
# Wrong
def test(test_data):  # Always uses first row

# Correct
def test(test_data_all):
    user = get_test_data_by_username(test_data_all, "T11_User2_Test")
```

### Issue: Session conflicts in parallel execution

**Problem**: Multiple workers sharing same session

**Solution**: Framework handles this automatically via worker-specific files:
- Worker 0: `ewm_username_gw0.json`
- Worker 1: `ewm_username_gw1.json`

### Issue: Session not updating after password change

**Solution**: Delete old session files or wait for 8-hour expiry:
```bash
rm -rf tests/.auth/*.json
```

---

## Summary

1. **CSV loaded ONCE** per test session (session scope)
2. **Multiple users supported** via CSV rows
3. **Each user gets own session file** - sessions maintained simultaneously
4. **Backward compatible** - existing tests still work
5. **Scalable** - handles 1000s of tests efficiently
6. **Flexible** - Use helper functions to access any user

**Session File Format**: `{app}_{username}_{worker}.json`

**Key Fixtures**:
- `test_data_all` - All CSV rows (for multi-user tests)
- `test_data` - First row (for existing tests)

**Helper Functions**:
- `get_test_data_by_username(test_data_all, username)`
- `get_test_data_by_index(test_data_all, index)`
