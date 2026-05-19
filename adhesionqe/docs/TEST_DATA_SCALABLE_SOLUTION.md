# Scalable Test Data Management - Query-Based Approach

## Problem with Index-Based Access ❌

```python
# BAD: Hard to maintain when CSV has 100+ rows
user_data = get_test_data_by_index(test_data_all, 47)  # Which user is this?
```

**Issues:**
- Need to know exact row number
- Adding/removing rows breaks tests
- Not readable - no context about which data
- Doesn't scale to large datasets

---

## Solution: Query-Based Access ✅

### TestDataManager - Query ANY Field!

```python
# Get data by test scenario - NO INDEX NEEDED!
data = test_data_manager.get_by(test_scenario="add_ach")

# Get data by user type
data = test_data_manager.get_by(user_type="advisor")

# Get data by multiple criteria
data = test_data_manager.get_by(user_type="advisor", test_scenario="add_ach")

# Filter ALL rows matching criteria
all_advisors = test_data_manager.filter_by(user_type="advisor")
```

---

## CSV Structure Example

```csv
username,password,client_id,account_name,user_type,test_scenario,priority
T11_Advisor1,Pass1,13222266,Carmen Tucker,advisor,add_ach,high
T11_Client1,Pass2,13222267,John Doe IRA,client,roth_conversion,high
T11_Admin1,Pass3,13222268,Jane Smith,admin,account_mgmt,medium
T11_Advisor2,Pass4,13222269,Bob Johnson,advisor,add_wire,low
T11_Client2,Pass5,13222270,Alice Brown,client,withdrawal,medium
```

---

## Usage Examples

### Example 1: BDD Feature - Query by Scenario

**Feature File:**
```gherkin
@add_ach
Scenario: Add ACH with advisor user
  Given I am using test data for scenario "add_ach"
  When I navigate to Clients menu
  Then I should see correct account data
```

**What Happens:**
1. Step finds row where `test_scenario="add_ach"`
2. Returns: `{"username": "T11_Advisor1", "user_type": "advisor", ...}`
3. No need to know it's row 0!

---

### Example 2: BDD Feature - Query by User Type

**Feature File:**
```gherkin
@client_test
Scenario: Client performs Roth conversion
  Given I am using test data for user type "client"
  When I perform Roth conversion
  Then conversion succeeds
```

**What Happens:**
1. Step finds row where `user_type="client"`
2. Returns first client user found
3. Could be row 1, row 50, doesn't matter!

---

### Example 3: Python Test - Query by Any Field

```python
def test_advisor_add_ach(test_data_manager):
    # Get advisor user for add_ach scenario
    advisor = test_data_manager.get_by(
        user_type="advisor",
        test_scenario="add_ach"
    )

    assert advisor['username'] == "T11_Advisor1"
    assert advisor['test_scenario'] == "add_ach"
```

---

### Example 4: Get ALL Matching Rows

```python
def test_all_advisors(test_data_manager):
    # Get ALL advisor users, regardless of row number
    all_advisors = test_data_manager.filter_by(user_type="advisor")

    print(f"Found {len(all_advisors)} advisor users")
    # Returns: [
    #   {"username": "T11_Advisor1", ...},
    #   {"username": "T11_Advisor2", ...}
    # ]

    for advisor in all_advisors:
        print(f"Testing with: {advisor['username']}")
```

---

### Example 5: Parametrize by Scenario

```python
import pytest

# Get all unique scenarios from CSV
def pytest_generate_tests(metafunc):
    if "scenario_data" in metafunc.fixturenames:
        data_manager = TestDataManager(load_csv())
        scenarios = data_manager.get_scenarios()
        metafunc.parametrize("scenario_data", scenarios)

@pytest.mark.parametrize("scenario_name", ["add_ach", "roth_conversion", "add_wire"])
def test_scenario(scenario_name, test_data_manager):
    # Automatically runs 3 times with different scenarios
    data = test_data_manager.get_by(test_scenario=scenario_name)

    print(f"Testing scenario: {scenario_name}")
    print(f"Username: {data['username']}")
    print(f"User type: {data['user_type']}")
```

---

### Example 6: Dynamic Filtering

```python
def test_high_priority_scenarios(test_data_manager):
    # Get all high priority test data
    high_priority = test_data_manager.filter_by(priority="high")

    for data in high_priority:
        run_test_with_data(data)
```

---

## TestDataManager API Reference

### `get_by(**criteria)` → dict | None

Get FIRST row matching ALL criteria.

```python
# Single criteria
data = test_data_manager.get_by(test_scenario="add_ach")

# Multiple criteria (AND condition)
data = test_data_manager.get_by(
    user_type="advisor",
    test_scenario="add_ach",
    priority="high"
)

# Returns None if not found
data = test_data_manager.get_by(test_scenario="unknown")  # None
```

---

### `filter_by(**criteria)` → list[dict]

Get ALL rows matching ALL criteria.

```python
# All advisors
advisors = test_data_manager.filter_by(user_type="advisor")

# All high priority tests
high_priority = test_data_manager.filter_by(priority="high")

# Combination
advisor_ach = test_data_manager.filter_by(
    user_type="advisor",
    test_scenario="add_ach"
)
```

---

### `get_all()` → list[dict]

Get all test data rows.

```python
all_data = test_data_manager.get_all()
print(f"Total rows: {len(all_data)}")
```

---

### `get_scenarios()` → list[str]

Get list of unique scenario names.

```python
scenarios = test_data_manager.get_scenarios()
# Returns: ["add_ach", "roth_conversion", "account_mgmt", "add_wire", "withdrawal"]
```

---

### `get_user_types()` → list[str]

Get list of unique user types.

```python
user_types = test_data_manager.get_user_types()
# Returns: ["advisor", "client", "admin"]
```

---

### Indexing Support

```python
# Also supports traditional indexing if needed
first_row = test_data_manager[0]
second_row = test_data_manager[1]

# Get count
count = len(test_data_manager)
```

---

## BDD Step Definitions

### Query by Scenario

```gherkin
Given I am using test data for scenario "add_ach"
Given I am using test data for scenario "roth_conversion"
```

### Query by User Type

```gherkin
Given I am using test data for user type "advisor"
Given I am using test data for user type "client"
Given I am using test data for user type "admin"
```

### Query by Username

```gherkin
Given I am using test data for username "T11_Advisor1"
```

---

## Real-World Example: Large CSV

**CSV with 100 rows:**
```csv
username,password,client_id,user_type,test_scenario,region,priority
User001,Pass001,10001,advisor,add_ach,west,high
User002,Pass002,10002,client,withdrawal,east,medium
... (98 more rows)
User100,Pass100,10100,admin,audit,south,low
```

**Old Way (BAD):**
```python
# Need to remember User050 is at row 49!
data = get_test_data_by_index(test_data_all, 49)
```

**New Way (GOOD):**
```python
# Just query what you need
data = test_data_manager.get_by(
    test_scenario="withdrawal",
    region="east"
)
# Finds User002 automatically, no matter which row it's in!
```

---

## Performance

### CSV Loading (Session Scope)

- **Loaded**: Once per test session
- **1 test**: 1 CSV read
- **1000 tests**: 1 CSV read (shared)
- **Performance**: O(1) for loading

### Querying

- **get_by()**: O(n) where n = number of rows
- **filter_by()**: O(n) where n = number of rows
- **Cached results**: Consider caching if same query repeated

**Note**: For 100-1000 rows, O(n) is perfectly fine. If you have 100,000+ rows, consider database or caching.

---

## Migration from Old Code

### Old Index-Based Code

```python
# Old
user1 = get_test_data_by_index(test_data_all, 0)
user2 = get_test_data_by_index(test_data_all, 1)
user3 = get_test_data_by_index(test_data_all, 2)
```

### New Query-Based Code

```python
# New - much clearer!
advisor = test_data_manager.get_by(user_type="advisor")
client = test_data_manager.get_by(user_type="client")
admin = test_data_manager.get_by(user_type="admin")
```

---

## Best Practices

### ✅ DO:

1. **Add descriptive columns** for easy querying:
   ```csv
   username,password,test_scenario,user_type,priority,region
   ```

2. **Use meaningful values**:
   ```csv
   test_scenario: add_ach, roth_conversion, withdrawal
   user_type: advisor, client, admin
   priority: high, medium, low
   ```

3. **Query by business meaning**:
   ```python
   # Good - readable and maintainable
   data = test_data_manager.get_by(test_scenario="add_ach")
   ```

4. **Add fallback handling**:
   ```python
   data = test_data_manager.get_by(test_scenario="add_ach")
   if not data:
       pytest.skip("No data available for add_ach scenario")
   ```

### ❌ DON'T:

1. **Don't use indices** (defeats the purpose):
   ```python
   # Bad - not scalable
   data = test_data_manager[47]
   ```

2. **Don't hardcode usernames** in tests:
   ```python
   # Bad
   data = test_data_manager.get_by(username="T11_Advisor1")

   # Good
   data = test_data_manager.get_by(user_type="advisor", test_scenario="add_ach")
   ```

---

## Extensibility

### Add Custom Query Methods

```python
class TestDataManager:
    # Existing methods...

    def get_high_priority(self):
        """Get all high priority test data"""
        return self.filter_by(priority="high")

    def get_by_region(self, region):
        """Get all data for specific region"""
        return self.filter_by(region=region)

    def get_advisor_for_scenario(self, scenario):
        """Get advisor user for specific scenario"""
        return self.get_by(user_type="advisor", test_scenario=scenario)
```

### Add Custom CSV Columns

```csv
username,password,test_scenario,environment,data_set,locale,permissions
User1,Pass1,add_ach,test11,dataset_A,en_US,read_write
```

Then query by any new field:
```python
data = test_data_manager.get_by(
    environment="test11",
    locale="en_US",
    permissions="read_write"
)
```

---

## Summary

| Feature | Index-Based | Query-Based |
|---------|-------------|-------------|
| Find data by scenario | ❌ Need to know row | ✅ `get_by(test_scenario="...")` |
| Find data by user type | ❌ Need to know row | ✅ `get_by(user_type="...")` |
| Scalability | ❌ Breaks with large CSV | ✅ Works with any size |
| Readability | ❌ `data[47]` unclear | ✅ `get_by(scenario="...")` clear |
| Maintenance | ❌ Breaks when rows change | ✅ Resilient to row changes |
| Flexibility | ❌ Fixed to index | ✅ Query ANY field |

**Recommendation**: Always use query-based approach with `TestDataManager` for scalable, maintainable tests!
