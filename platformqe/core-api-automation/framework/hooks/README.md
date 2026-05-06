# Framework Hooks

## Overview

The `framework/hooks` module provides a **generic, reusable test setup and teardown system** that can be used by any service to **execute prerequisite API calls** (e.g., POST to create test data) before running tests.

## Architecture

```
framework/hooks/
├── __init__.py          # Module exports
├── config.py            # Service-specific hooks configuration
├── setup.py             # Test data setup via API calls (TestDataManager)
├── teardown.py          # Test cleanup (CleanupManager)
└── README.md            # This documentation
```

## Quick Start

### Basic Usage

```python
from framework.hooks import setup_test_data, teardown_test_data

# Run setup before tests - executes prerequisite API calls
setup_test_data('parties')

# Run teardown after tests  
teardown_test_data('parties')
```

### In pytest conftest.py

```python
import pytest
from framework.hooks import TestDataManager, CleanupManager

@pytest.fixture(scope="session")
def test_data_manager():
    """Session-scoped fixture for test data setup/teardown."""
    manager = TestDataManager('parties')
    manager.setup()
    yield manager
    
    cleanup = CleanupManager('parties', created_data=manager.created_data)
    cleanup.teardown()
```

## How It Works

The hooks execute **prerequisite test cases** before running the actual tests:

1. **Load test case** - Reads the POST test case JSON file
2. **Load payload** - Loads and renders the request payload with context variables
3. **Execute API call** - Makes the POST request to create test data
4. **Extract values** - Extracts IDs from the API response
5. **Update CSV** - Writes extracted IDs to the data-driven CSV file

## Configuration

Service-specific configurations are defined in `config.py`:

```python
SERVICE_DEFAULTS = {
    'parties': {
        'max_records': 10,
        'prerequisite_testcase': {
            'enabled': True,
            'count': 3,  # Number of times to execute (creates 3 party IDs)
            'testcase_file': 'parties/testcases/TestCase_Party_POST.json',
            'test_data_file': 'parties/data_driven/Data_parties_POST.csv',
            'extract_from_response': {
                'field': 'partyId',  # Field to extract from API response
                'assign_to': 'id'    # Variable name to use
            },
            'update_csv_file': 'parties/data_driven/Data_parties_GET.csv',
            'csv_columns': ['environment', 'id']
        }
    }
}
```

## Features

### TestDataManager

| Feature | Description |
|---------|-------------|
| Prerequisite Tests | Execute POST tests to create test data before running GET tests |
| Value Extraction | Extract IDs from API responses (supports nested fields) |
| CSV Updates | Dynamically update CSV files with extracted values |
| Multiple Executions | Run prerequisite tests multiple times (configurable count) |

### CleanupManager

| Feature | Description |
|---------|-------------|
| Data Deletion | Delete data created during test setup via API |
| CSV Restore | Restore original CSV files |
| Cache Clearing | Clear framework caches |

## Adding a New Service

1. Add the prerequisite configuration to `config.py`:
   ```python
   SERVICE_DEFAULTS = {
       'newservice': {
           'max_records': 10,
           'prerequisite_testcase': {
               'enabled': True,
               'count': 1,
               'testcase_file': 'newservice/testcases/TestCase_POST.json',
               'test_data_file': 'newservice/data_driven/Data_POST.csv',
               'extract_from_response': {
                   'field': 'id',
                   'assign_to': 'id'
               },
               'update_csv_file': 'newservice/data_driven/Data_GET.csv',
               'csv_columns': ['environment', 'id']
           }
       }
   }
   ```

2. Create the prerequisite test case file (`TestCase_POST.json`)

3. Create a conftest.py in your testdata folder:
   ```python
   import pytest
   from framework.hooks import TestDataManager

   def pytest_configure(config):
       testcase_file = getattr(config.option, 'testcase_file', '')
       if 'newservice' in testcase_file:
           manager = TestDataManager('newservice')
           manager.setup()
   ```

## Example Flow

For `parties` service:

1. **Setup runs** `TestCase_Party_POST.json` 3 times
2. **Creates** 3 new party IDs via POST API
3. **Extracts** `partyId` from each response
4. **Writes** to `Data_parties_GET.csv`:
   ```csv
   environment,id
   TSADEV,abc123
   TSADEV,def456
   TSADEV,ghi789
   ```
5. **Tests run** using the fresh party IDs
