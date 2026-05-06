# Fixtures Guide

This document provides comprehensive information about the fixtures available in the test framework.

## Directory Structure

```
fixtures/
├── __init__.py
├── ui/
│   ├── __init__.py
│   └── browser_fixtures.py    # UI testing fixtures
└── api/
    ├── __init__.py
    └── api_fixtures.py         # API testing fixtures
```

## UI Fixtures (fixtures/ui/browser_fixtures.py)

### Browser and Context Fixtures

#### `browser()`
- **Scope**: Session
- **Purpose**: Provides a Playwright browser instance
- **Configuration**: Uses config.BROWSER (chromium/firefox/webkit)
- **Cleanup**: Automatically closes browser after tests

#### `context(browser)`
- **Scope**: Function
- **Purpose**: Creates a new browser context for test isolation
- **Features**:
  - Configurable viewport
  - Recording traces on failure
  - Recording videos on failure
  - Screenshots on failure
- **Cleanup**: Automatically closes context

#### `page(context)`
- **Scope**: Function
- **Purpose**: Creates a new page in the browser context
- **Features**:
  - Default timeout from config
  - Automatic screenshot on failure
  - Automatic cleanup
- **Usage**:
  ```python
  def test_example(page):
      page.goto("https://example.com")
  ```

### Authentication Fixtures

#### `authenticated_page(page)`
- **Scope**: Function
- **Purpose**: Provides a page with logged-in user
- **Process**:
  1. Navigates to login page
  2. Logs in with TEST_USERNAME/TEST_PASSWORD
  3. Waits for navigation completion
- **Usage**:
  ```python
  def test_with_auth(authenticated_page):
      authenticated_page.goto("/dashboard")
  ```

#### `admin_authenticated_page(page)`
- **Scope**: Function
- **Purpose**: Provides a page with logged-in admin user
- **Credentials**: Uses ADMIN_USERNAME/ADMIN_PASSWORD from config
- **Usage**: Similar to authenticated_page but with admin privileges

### Storage State Fixtures

#### `user_storage_state(browser)`
- **Scope**: Session
- **Purpose**: Saves authenticated user state for reuse
- **File**: `.auth/user_state.json`
- **Benefit**: Skip login for faster tests

#### `admin_storage_state(browser)`
- **Scope**: Session
- **Purpose**: Saves authenticated admin state for reuse
- **File**: `.auth/admin_state.json`

#### `page_with_storage_state(browser, user_storage_state)`
- **Scope**: Function
- **Purpose**: Creates page with pre-authenticated user state
- **Usage**:
  ```python
  def test_fast_auth(page_with_storage_state):
      # Already logged in, no need for login steps
      page_with_storage_state.goto("/dashboard")
  ```

### Viewport Fixtures

#### `mobile_page(context)`
- **Scope**: Function
- **Purpose**: Provides a page with mobile viewport (375x667)
- **Use Case**: Mobile responsive testing
- **Usage**:
  ```python
  def test_mobile_layout(mobile_page):
      mobile_page.goto("/")
      assert mobile_page.locator(".mobile-menu").is_visible()
  ```

#### `tablet_page(context)`
- **Scope**: Function
- **Purpose**: Provides a page with tablet viewport (768x1024)
- **Use Case**: Tablet responsive testing

### Network Fixtures

#### `page_with_network_interception(context)`
- **Scope**: Function
- **Purpose**: Provides a page with network interception capabilities
- **Features**:
  - Intercepts all requests
  - Logs request URL and method
  - Useful for API call verification
- **Usage**:
  ```python
  def test_api_calls(page_with_network_interception):
      page_with_network_interception.goto("/")
      # All network requests are logged
  ```

### Page Object Fixtures

#### `login_page(page)`
- **Scope**: Function
- **Purpose**: Provides LoginPage object
- **Usage**:
  ```python
  def test_login(login_page):
      login_page.navigate()
      login_page.login("user", "pass")
  ```

#### `home_page(page)`
- **Scope**: Function
- **Purpose**: Provides HomePage object
- **Usage**:
  ```python
  def test_home(home_page):
      home_page.navigate()
      assert home_page.is_welcome_displayed()
  ```

### Test Data Fixtures

#### `test_user_data()`
- **Scope**: Function
- **Purpose**: Provides test user data dictionary
- **Returns**:
  ```python
  {
      'username': 'test_user',
      'password': 'test_password',
      'email': 'test@example.com'
  }
  ```

#### `admin_user_data()`
- **Scope**: Function
- **Purpose**: Provides admin user data dictionary

### Utility Fixtures

#### `wait_for_element(page)`
- **Scope**: Function
- **Purpose**: Provides a helper function to wait for elements
- **Usage**:
  ```python
  def test_wait(page, wait_for_element):
      page.goto("/")
      element = wait_for_element(".loading-complete")
  ```

#### `take_screenshot(page)`
- **Scope**: Function
- **Purpose**: Provides a function to take screenshots
- **Parameters**: filename (optional)
- **Usage**:
  ```python
  def test_screenshot(page, take_screenshot):
      page.goto("/")
      take_screenshot("homepage.png")
  ```

## API Fixtures (fixtures/api/api_fixtures.py)

### Session Fixtures

#### `api_session()`
- **Scope**: Function
- **Purpose**: Provides a requests.Session for API calls
- **Features**:
  - Pre-configured headers
  - Connection pooling
  - Automatic cleanup
- **Usage**:
  ```python
  def test_api(api_session):
      response = api_session.get("/api/endpoint")
  ```

#### `api_base_url()`
- **Scope**: Session
- **Purpose**: Provides API base URL from config
- **Returns**: Config.API_BASE_URL

### Authentication Fixtures

#### `api_auth_token(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Obtains user authentication token
- **Process**:
  1. Sends login request with TEST_USERNAME/TEST_PASSWORD
  2. Extracts token from response
- **Usage**:
  ```python
  def test_with_auth(api_session, api_auth_token):
      headers = {'Authorization': f'Bearer {api_auth_token}'}
      response = api_session.get("/api/protected", headers=headers)
  ```

#### `admin_api_token(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Obtains admin authentication token
- **Credentials**: Uses ADMIN_USERNAME/ADMIN_PASSWORD

#### `authenticated_api_session(api_session, api_auth_token)`
- **Scope**: Function
- **Purpose**: Provides session with authentication token pre-configured
- **Usage**:
  ```python
  def test_authenticated(authenticated_api_session):
      # Token already set in headers
      response = authenticated_api_session.get("/api/protected")
  ```

### HTTP Method Helper Fixtures

#### `api_get(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Helper function for GET requests
- **Usage**:
  ```python
  def test_get(api_get):
      response = api_get("/users", params={'page': 1})
      assert response.status_code == 200
  ```

#### `api_post(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Helper function for POST requests
- **Usage**:
  ```python
  def test_create(api_post):
      data = {'name': 'John', 'email': 'john@example.com'}
      response = api_post("/users", json=data)
      assert response.status_code == 201
  ```

#### `api_put(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Helper function for PUT requests

#### `api_delete(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Helper function for DELETE requests

#### `api_patch(api_session, api_base_url)`
- **Scope**: Function
- **Purpose**: Helper function for PATCH requests

### Test Data Creation Fixtures

#### `create_test_user(authenticated_api_session)`
- **Scope**: Function
- **Purpose**: Creates a test user via API and cleans up after test
- **Returns**: User data dictionary
- **Cleanup**: Automatically deletes user after test
- **Usage**:
  ```python
  def test_user_operations(create_test_user):
      user = create_test_user
      # Use user data for testing
      # User is automatically deleted after test
  ```

#### `create_test_data(authenticated_api_session)`
- **Scope**: Function
- **Purpose**: Creates multiple test records
- **Cleanup**: Automatically deletes all created records

### Validation Fixtures

#### `validate_response()`
- **Scope**: Function
- **Purpose**: Provides response validation helper function
- **Checks**:
  - Status code
  - Content type
  - Response time
- **Usage**:
  ```python
  def test_response_validation(api_get, validate_response):
      response = api_get("/users")
      validate_response(response, expected_status=200)
  ```

#### `validate_json_schema()`
- **Scope**: Function
- **Purpose**: Validates JSON response against schema
- **Usage**:
  ```python
  def test_schema(api_get, validate_json_schema):
      response = api_get("/users/1")
      schema = {'type': 'object', 'properties': {...}}
      validate_json_schema(response.json(), schema)
  ```

### Sample Data Fixtures

#### `sample_user_payload()`
- **Scope**: Function
- **Purpose**: Provides sample user data for API requests
- **Returns**:
  ```python
  {
      'username': 'api_test_user',
      'email': 'apitest@example.com',
      'first_name': 'API',
      'last_name': 'Test'
  }
  ```

#### `sample_product_payload()`
- **Scope**: Function
- **Purpose**: Provides sample product data

### Database Fixtures

#### `api_db_connection()`
- **Scope**: Function
- **Purpose**: Provides database connection for API tests
- **Use Case**: Verify API changes in database
- **Cleanup**: Automatically closes connection
- **Usage**:
  ```python
  def test_api_db_sync(api_post, api_db_connection):
      # Create user via API
      response = api_post("/users", json={'username': 'test'})
      user_id = response.json()['id']

      # Verify in database
      result = api_db_connection.execute_query(
          "SELECT * FROM users WHERE id = ?",
          (user_id,)
      )
      assert result[0]['username'] == 'test'
  ```

## Using Fixtures in Tests

### Basic Usage

```python
# UI Test Example
def test_login_functionality(page, login_page):
    login_page.navigate()
    login_page.login("user", "password")
    assert login_page.is_login_successful()

# API Test Example
def test_create_user(api_post, validate_response):
    data = {'username': 'newuser', 'email': 'new@example.com'}
    response = api_post("/users", json=data)
    validate_response(response, expected_status=201)
```

### Combining Fixtures

```python
def test_end_to_end(
    authenticated_page,
    api_post,
    api_db_connection
):
    # Create data via API
    response = api_post("/products", json={'name': 'Widget'})
    product_id = response.json()['id']

    # Verify in UI
    authenticated_page.goto(f"/products/{product_id}")
    assert authenticated_page.locator("h1").text_content() == "Widget"

    # Verify in database
    result = api_db_connection.execute_query(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )
    assert result[0]['name'] == 'Widget'
```

### Parameterizing Fixtures

```python
import pytest

@pytest.fixture
def custom_user_data():
    return {
        'username': 'custom_user',
        'role': 'admin'
    }

def test_with_custom_data(page, custom_user_data):
    # Use custom fixture
    pass
```

## Best Practices

### 1. Fixture Scope Selection
- **Session**: Use for expensive operations (browser launch, database connections)
- **Function**: Use for test isolation (page, context, API session)

### 2. Fixture Naming
- Use descriptive names that indicate what the fixture provides
- Prefix with fixture type: `api_*`, `test_*`, `sample_*`

### 3. Cleanup
- Always implement proper cleanup (yield, teardown)
- Use context managers where applicable
- Clean up in reverse order of creation

### 4. Fixture Dependencies
- Keep dependency chains reasonable
- Avoid circular dependencies
- Document complex dependency relationships

### 5. Performance Optimization
- Use session-scoped fixtures for shared resources
- Implement storage state for authentication
- Cache expensive computations

### 6. Test Isolation
- Each test should be independent
- Use function-scoped fixtures for test data
- Clean up after each test

## Troubleshooting

### Common Issues

#### Fixture Not Found
**Error**: `fixture 'fixture_name' not found`

**Solution**: Ensure the fixture is imported in conftest.py:
```python
pytest_plugins = [
    'fixtures.ui.browser_fixtures',
    'fixtures.api.api_fixtures',
]
```

#### Fixture Scope Mismatch
**Error**: `ScopeMismatch: You tried to access function-scoped fixture with a session-scoped fixture`

**Solution**: Match fixture scopes appropriately or use a broader scope.

#### Authentication Failures
**Error**: Login fixtures fail or return invalid tokens

**Solution**:
1. Check credentials in config/.env
2. Verify API endpoints are correct
3. Check if authentication method has changed

### Debugging Fixtures

Enable verbose output:
```bash
pytest -v --fixtures  # List all available fixtures
pytest -v --setup-show  # Show fixture setup/teardown
pytest -v -s  # Show print statements in fixtures
```

## Configuration

### Environment Variables (.env)

```bash
# Application URLs
BASE_URL=https://your-app-url.com
API_BASE_URL=https://api.your-app.com

# Test Credentials
TEST_USERNAME=test_user
TEST_PASSWORD=test_password
ADMIN_USERNAME=admin_user
ADMIN_PASSWORD=admin_password

# Browser Settings
BROWSER=chromium
HEADLESS=false
TIMEOUT=30000

# API Configuration
API_KEY=your_api_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=db_user
DB_PASSWORD=db_password
```

## Adding New Fixtures

### UI Fixture Example

```python
# In fixtures/ui/browser_fixtures.py

@pytest.fixture(scope="function")
def custom_viewport_page(context):
    """Page with custom viewport size"""
    page = context.new_page(
        viewport={'width': 1920, 'height': 1080}
    )
    yield page
    page.close()
```

### API Fixture Example

```python
# In fixtures/api/api_fixtures.py

@pytest.fixture(scope="function")
def custom_api_client(api_session, api_base_url):
    """Custom API client with special configuration"""
    client = APIClient(api_session, api_base_url)
    client.session.headers.update({
        'Custom-Header': 'value'
    })
    yield client
```

## Examples

### Full UI Test Example

```python
def test_complete_user_journey(
    authenticated_page,
    test_user_data,
    take_screenshot
):
    """Test complete user workflow"""
    # Navigate to dashboard
    authenticated_page.goto("/dashboard")
    take_screenshot("dashboard.png")

    # Navigate to profile
    authenticated_page.click("text=Profile")
    authenticated_page.wait_for_url("**/profile")

    # Update profile
    authenticated_page.fill("#email", test_user_data['email'])
    authenticated_page.click("button[type=submit]")

    # Verify success
    assert authenticated_page.locator(".success-message").is_visible()
```

### Full API Test Example

```python
def test_complete_api_workflow(
    authenticated_api_session,
    sample_user_payload,
    validate_response,
    api_db_connection
):
    """Test complete API CRUD workflow"""
    # Create
    response = authenticated_api_session.post(
        "/api/users",
        json=sample_user_payload
    )
    validate_response(response, expected_status=201)
    user_id = response.json()['id']

    # Read
    response = authenticated_api_session.get(f"/api/users/{user_id}")
    validate_response(response, expected_status=200)

    # Update
    response = authenticated_api_session.put(
        f"/api/users/{user_id}",
        json={'email': 'updated@example.com'}
    )
    validate_response(response, expected_status=200)

    # Verify in database
    result = api_db_connection.execute_query(
        "SELECT email FROM users WHERE id = ?",
        (user_id,)
    )
    assert result[0]['email'] == 'updated@example.com'

    # Delete
    response = authenticated_api_session.delete(f"/api/users/{user_id}")
    validate_response(response, expected_status=204)
```

---

For more information, see:
- [README.md](README.md) - Project overview
- [BDD_GUIDE.md](BDD_GUIDE.md) - BDD testing guide
- [pytest fixtures documentation](https://docs.pytest.org/en/stable/fixture.html)
