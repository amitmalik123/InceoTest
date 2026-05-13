---
description: 'pytest testing conventions and best practices for Python projects'
applyTo: '**/test_*.py,**/*_test.py,**/conftest.py,**/tests/**/*.py'
---

# pytest Testing Conventions

This instruction file defines testing standards for Python projects using pytest, Allure reporting, and python-dotenv for configuration management.

## Test Framework Structure

### Test File Naming

**Modules:**
- `test_*.py` - Test modules (preferred)
- `*_test.py` - Alternative test module naming

**Classes:**
- `Test*` - Test classes (e.g., `TestAccountService`)

**Functions:**
- `test_*` - Test functions (e.g., `test_create_account_success`)

**Example Structure:**
```
tests/
├── conftest.py                    # Shared fixtures
├── pytest.ini                     # pytest configuration
├── test_account_service.py        # Unit tests
├── test_authentication_api.py     # Integration tests
└── ui/
    ├── test_login_flow.py         # UI tests
    └── conftest.py                # UI-specific fixtures
```

## Test Function Organization

### AAA Pattern (Arrange-Act-Assert)

All tests must follow the AAA pattern:

```python
def test_create_account_with_valid_data():
    # Arrange - Set up test data and dependencies
    account_service = AccountService()
    account_data = {
        'name': 'Test Account',
        'type': 'checking'
    }

    # Act - Execute the code under test
    result = account_service.create_account(account_data)

    # Assert - Verify the outcome
    assert result is not None
    assert result.id > 0
    assert result.name == 'Test Account'
```

### Test Class Organization

Group related tests in classes:

```python
import pytest

class TestAccountService:
    """Tests for AccountService."""

    @pytest.fixture
    def account_service(self):
        """Fixture for AccountService instance."""
        return AccountService()

    def test_create_account_success(self, account_service):
        # Test implementation
        pass

    def test_create_account_invalid_name(self, account_service):
        # Test implementation
        pass
```

## Fixtures

### Fixture Scopes

Choose appropriate scope for fixtures:

```python
import pytest

@pytest.fixture(scope='function')  # Default: run before/after each test
def clean_database():
    """Clean database before each test."""
    db.clear()
    yield
    # Cleanup after test

@pytest.fixture(scope='class')  # Run once per test class
def database_connection():
    """Establish database connection for test class."""
    conn = db.connect()
    yield conn
    conn.close()

@pytest.fixture(scope='module')  # Run once per test module
def api_client():
    """Create API client for test module."""
    client = APIClient()
    yield client
    client.shutdown()

@pytest.fixture(scope='session')  # Run once per test session
def test_configuration():
    """Load test configuration once for entire session."""
    return load_config()
```

### Fixture Dependencies

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def database():
    """Provide database connection."""
    return Database()

@pytest.fixture
def account_repository(database):
    """Provide AccountRepository with database dependency."""
    return AccountRepository(database)

@pytest.fixture
def account_service(account_repository):
    """Provide AccountService with repository dependency."""
    return AccountService(account_repository)
```

### conftest.py Organization

**Root conftest.py:**
```python
# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line('markers', 'smoke: Smoke tests')
    config.addinivalue_line('markers', 'regression: Regression tests')
    config.addinivalue_line('markers', 'integration: Integration tests')
    config.addinivalue_line('markers', 'slow: Slow-running tests')

@pytest.fixture(scope='session')
def base_url():
    """Provide application base URL from environment."""
    url = os.getenv('APP_BASE_URL')
    if not url:
        pytest.fail('APP_BASE_URL environment variable not set')
    return url

@pytest.fixture(scope='session')
def api_key():
    """Provide API key from environment."""
    key = os.getenv('API_KEY')
    if not key:
        pytest.fail('API_KEY environment variable not set')
    return key
```

**Module-specific conftest.py:**
```python
# tests/ui/conftest.py
import pytest
from playwright.sync_api import Page

@pytest.fixture
def accounts_page(page: Page):
    """Provide AccountsPage page object."""
    from pages.accounts_page import AccountsPage
    return AccountsPage(page)
```

## Parametrization

### Basic Parametrize

Test multiple inputs with `@pytest.mark.parametrize`:

```python
import pytest

@pytest.mark.parametrize('value,expected', [
    (0, 'zero'),
    (1, 'one'),
    (5, 'five'),
    (-1, 'negative')
])
def test_number_to_string(value, expected):
    """Test number to string conversion."""
    result = number_to_string(value)
    assert result == expected
```

### Named Parameters (IDs)

Use `id` for readable test names:

```python
@pytest.mark.parametrize('name,expected_error', [
    pytest.param('', 'Name is required', id='empty_name'),
    pytest.param(None, 'Name is required', id='null_name'),
    pytest.param('AB', 'Name too short', id='name_too_short'),
    pytest.param('X' * 256, 'Name too long', id='name_exceeds_max')
])
def test_validate_account_name(name, expected_error):
    """Test account name validation."""
    with pytest.raises(ValidationError, match=expected_error):
        validate_account_name(name)
```

### Multiple Parameters

Parametrize multiple arguments:

```python
@pytest.mark.parametrize('name', ['Test Account', 'Savings', 'Retirement'])
@pytest.mark.parametrize('account_type', ['checking', 'savings', 'retirement'])
def test_create_account_combinations(name, account_type):
    """Test all combinations of name and type."""
    # Creates 3 × 3 = 9 test cases
    account = create_account(name, account_type)
    assert account.name == name
    assert account.type == account_type
```

## Markers

### Standard Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.smoke
def test_critical_path():
    """Smoke test for critical functionality."""
    pass

@pytest.mark.regression
def test_bug_fix():
    """Regression test for previous bug."""
    pass

@pytest.mark.integration
def test_database_integration():
    """Integration test with database."""
    pass

@pytest.mark.slow
def test_performance_intensive():
    """Slow test that takes significant time."""
    pass

@pytest.mark.skip(reason='Feature not yet implemented')
def test_future_feature():
    """Test for upcoming feature."""
    pass

@pytest.mark.skipif(os.getenv('CI') == 'true', reason='Skip in CI environment')
def test_local_only():
    """Test that only runs locally."""
    pass

@pytest.mark.xfail(reason='Known bug in external library')
def test_known_failure():
    """Test expected to fail."""
    pass
```

### Running Tests by Marker

```bash
# Run smoke tests only
pytest -m smoke

# Run regression tests only
pytest -m regression

# Run multiple markers
pytest -m "smoke or regression"

# Exclude markers
pytest -m "not slow"

# Complex marker expressions
pytest -m "smoke and not integration"
```

## Allure Reporting Integration

### Allure Decorators

Use Allure decorators for rich reporting:

```python
import allure
import pytest

@allure.feature('Account Management')
@allure.story('Create Account')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('Create account with valid data returns success')
@allure.description('Test verifies that creating an account with valid data returns a success response with account ID')
@allure.tag('api', 'smoke', 'accounts')
@allure.label('owner', 'qa-team')
@allure.link('https://jira.example.com/ISSUE-123', name='User Story')
@allure.issue('BUG-456', 'Related Bug')
@allure.testcase('TC-789', 'Test Case Document')
def test_create_account_valid_data(api_client):
    """Test account creation with valid data."""
    # Arrange
    account_data = {'name': 'Test Account', 'type': 'checking'}

    # Act
    with allure.step('Send POST request to create account'):
        response = api_client.post('/api/accounts', json=account_data)

    # Assert
    with allure.step('Verify response status is 201'):
        assert response.status_code == 201

    with allure.step('Verify account ID is returned'):
        assert 'id' in response.json()
        assert response.json()['id'] > 0
```

### Allure Severity Levels

```python
import allure

# Critical functionality - system unusable if fails
@allure.severity(allure.severity_level.BLOCKER)

# Critical business logic
@allure.severity(allure.severity_level.CRITICAL)

# Important functionality
@allure.severity(allure.severity_level.NORMAL)

# Minor issues
@allure.severity(allure.severity_level.MINOR)

# Cosmetic issues
@allure.severity(allure.severity_level.TRIVIAL)
```

### Allure Steps

Use `allure.step()` for detailed test flow:

```python
import allure

def test_user_registration_flow():
    """Test complete user registration flow."""

    with allure.step('Navigate to registration page'):
        page.goto('/register')

    with allure.step('Fill registration form'):
        page.fill('#email', 'user@example.com')
        page.fill('#password', 'SecurePass123')
        page.fill('#confirm-password', 'SecurePass123')

    with allure.step('Submit registration form'):
        page.click('#submit-btn')

    with allure.step('Verify success message appears'):
        assert page.get_by_text('Registration successful').is_visible()
```

### Allure Attachments

Attach data to test reports:

```python
import allure
import json

def test_api_response():
    """Test API response format."""
    response = api_client.get('/api/accounts')

    # Attach JSON response
    allure.attach(
        json.dumps(response.json(), indent=2),
        name='api_response',
        attachment_type=allure.attachment_type.JSON
    )

    # Attach screenshot
    screenshot_bytes = page.screenshot()
    allure.attach(
        screenshot_bytes,
        name='page_screenshot',
        attachment_type=allure.attachment_type.PNG
    )

    # Attach text logs
    allure.attach(
        'Log content here',
        name='application_logs',
        attachment_type=allure.attachment_type.TEXT
    )
```

## Environment Configuration with python-dotenv

### .env File Usage

**NEVER commit secrets to version control:**

```bash
# .env (NOT committed, in .gitignore)
APP_BASE_URL=https://app.dev.example.com
API_BASE_URL=https://api.dev.example.com
API_KEY=your-secret-api-key-here
TEST_USER=test.user@example.com
TEST_PASSWORD=SecureTestPassword123
DB_HOST=localhost
DB_NAME=test_database
DB_USER=test_user
DB_PASSWORD=test_db_password
TEST_ENV=dev
```

**Provide .env.example template (committed):**

```bash
# .env.example (committed as template)
APP_BASE_URL=https://app.example.com
API_BASE_URL=https://api.example.com
API_KEY=your-api-key
TEST_USER=your-test-user
TEST_PASSWORD=your-test-password
DB_HOST=localhost
DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_password
TEST_ENV=dev
```

### Loading Environment Variables

```python
import os
from dotenv import load_dotenv

# Load .env file (typically in conftest.py)
load_dotenv()

# Access environment variables with defaults
base_url = os.getenv('APP_BASE_URL', 'http://localhost:3000')
api_key = os.getenv('API_KEY')

# Fail fast if required variables are missing
if not api_key:
    raise ValueError('API_KEY environment variable is required')

# Use in tests
def test_api_endpoint():
    """Test API endpoint."""
    response = requests.get(
        f"{os.getenv('API_BASE_URL')}/accounts",
        headers={'Authorization': f"Bearer {os.getenv('API_KEY')}"}
    )
    assert response.status_code == 200
```

### conftest.py Configuration Loading

```python
# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv

# Load environment variables once at session start
load_dotenv()

@pytest.fixture(scope='session', autouse=True)
def validate_environment():
    """Validate required environment variables are set."""
    required_vars = ['APP_BASE_URL', 'API_BASE_URL', 'API_KEY', 'TEST_USER', 'TEST_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        pytest.fail(f"Missing required environment variables: {', '.join(missing_vars)}")

@pytest.fixture(scope='session')
def config():
    """Provide configuration dictionary."""
    return {
        'app_base_url': os.getenv('APP_BASE_URL'),
        'api_base_url': os.getenv('API_BASE_URL'),
        'api_key': os.getenv('API_KEY'),
        'test_user': os.getenv('TEST_USER'),
        'test_password': os.getenv('TEST_PASSWORD'),
        'environment': os.getenv('TEST_ENV', 'dev')
    }
```

## Assertion Patterns

### Basic Assertions

```python
# Equality
assert result == expected

# Identity
assert result is None
assert result is not None

# Membership
assert 'id' in response.json()
assert item in collection

# Boolean
assert is_valid
assert not is_invalid

# Comparison
assert count > 0
assert value <= max_value
```

### Exception Assertions

```python
import pytest

# Assert exception is raised
with pytest.raises(ValueError):
    validate_account_name('')

# Assert exception with message match
with pytest.raises(ValidationError, match='Name is required'):
    validate_account_name(None)

# Assert exception and inspect
with pytest.raises(ValueError) as exc_info:
    process_invalid_data()

assert 'invalid data' in str(exc_info.value)
```

### Warnings Assertions

```python
import pytest
import warnings

# Assert warning is raised
with pytest.warns(UserWarning):
    deprecated_function()

# Assert warning message
with pytest.warns(UserWarning, match='deprecated'):
    old_api_call()
```

## pytest Configuration

### pytest.ini

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Additional options
addopts =
    -v
    --strict-markers
    --tb=short
    --alluredir=allure-results

# Markers
markers =
    smoke: Smoke tests
    regression: Regression tests
    integration: Integration tests
    ui: UI tests
    api: API tests
    slow: Slow-running tests

# Test paths
testpaths = tests

# Minimum Python version
minversion = 3.8
```

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--alluredir=allure-results"
]
markers = [
    "smoke: Smoke tests",
    "regression: Regression tests",
    "integration: Integration tests",
    "ui: UI tests",
    "api: API tests",
    "slow: Slow-running tests"
]
```

## AssetMark-Specific Requirements

### Security Requirements

❌ **NEVER hardcode credentials:**
```python
# BAD - Hardcoded credentials
username = 'admin@example.com'
password = 'hardcoded_password'
api_key = 'sk-1234567890'
```

✅ **ALWAYS use environment variables:**
```python
# GOOD - Environment variables via python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('TEST_USER')
password = os.getenv('TEST_PASSWORD')
api_key = os.getenv('API_KEY')
```

### Fixture Patterns

Use fixtures for setup/teardown:

```python
@pytest.fixture
def authenticated_api_client():
    """Provide authenticated API client."""
    client = APIClient(
        base_url=os.getenv('API_BASE_URL'),
        api_key=os.getenv('API_KEY')
    )
    client.authenticate(
        username=os.getenv('TEST_USER'),
        password=os.getenv('TEST_PASSWORD')
    )
    yield client
    # Cleanup
    client.logout()
```

### Test Naming

Use descriptive test names:

```python
# Pattern: test_<what>_<condition>_<expected_result>

def test_create_account_with_valid_data_returns_success():
    """Test creating account with valid data returns success."""
    pass

def test_create_account_with_empty_name_raises_validation_error():
    """Test creating account with empty name raises ValidationError."""
    pass

def test_get_accounts_with_invalid_token_returns_401():
    """Test getting accounts with invalid token returns 401."""
    pass
```

## Running Tests

### Command-Line Options

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_accounts.py

# Run specific test
pytest tests/test_accounts.py::test_create_account_success

# Run tests matching pattern
pytest -k "account"

# Run with markers
pytest -m smoke
pytest -m "regression and not slow"

# Verbose output
pytest -v
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Parallel execution
pytest -n auto  # Requires pytest-xdist

# Generate Allure report
pytest --alluredir=./allure-results
allure serve ./allure-results
```

## Best Practices Summary

### DO:
✅ Use AAA pattern (Arrange-Act-Assert)
✅ Use descriptive test names
✅ Use fixtures for setup/teardown
✅ Use parametrize for data-driven tests
✅ Use markers to categorize tests
✅ Use Allure decorators for rich reporting
✅ Load credentials from environment variables (python-dotenv)
✅ Use proper fixture scoping
✅ Write isolated tests (no dependencies between tests)
✅ Capture screenshots on failure (UI tests)

### DON'T:
❌ Hardcode credentials or API keys
❌ Write tests that depend on execution order
❌ Use vague test names ('test_1', 'test_case')
❌ Skip Allure decorators (provide context)
❌ Use sleep() for waits (use proper wait conditions)
❌ Commit .env files to version control
❌ Write tests without assertions
❌ Mix unit and integration tests in same file
❌ Ignore test failures
❌ Write tests without cleanup

## Summary

Follow pytest conventions with:
- **AAA pattern** for test structure
- **Fixtures** for setup/teardown with proper scoping
- **Parametrize** for data-driven tests
- **Markers** for test categorization
- **Allure decorators** for rich reporting
- **python-dotenv** for secure configuration
- **Descriptive naming** for clarity
- **No hardcoded secrets** ever

These conventions ensure maintainable, secure, and well-documented test suites.


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
