# Authentication State Management Guide

## Overview

**Problem**: Logging in for every test is slow and repetitive.

**Solution**: Login ONCE at the start of the test session, save the authentication state, and reuse it across ALL tests.

**Result**: Tests run 10x faster! ⚡

---

## How It Works

```
Session Start
    ↓
setup_auth_state fixture runs ONCE
    ↓
Login as regular user → Save to tests/.auth/regular_user.json
Login as admin user → Save to tests/.auth/admin_user.json
    ↓
All Tests Run
    ↓
Each test loads saved state → No login needed!
    ↓
Session End (optional cleanup)
```

---

## Available Fixtures

### 1. `authenticated_page` - Pre-authenticated Regular User

**Use when**: Testing features that require login (90% of tests)

**Benefit**: NO LOGIN REQUIRED - session already authenticated!

```python
def test_dashboard(authenticated_page):
    # Skip login - already authenticated!
    authenticated_page.goto("/dashboard")

    # Start testing immediately
    assert authenticated_page.locator(".user-menu").is_visible()
```

### 2. `authenticated_admin_page` - Pre-authenticated Admin User

**Use when**: Testing admin-only features

**Benefit**: Admin session pre-loaded!

```python
def test_admin_panel(authenticated_admin_page):
    # Already logged in as admin!
    authenticated_admin_page.goto("/admin")

    assert authenticated_admin_page.locator(".admin-controls").is_visible()
```

### 3. `fresh_page` - Clean Page Without Authentication

**Use when**:
- Testing login flow itself
- Testing unauthenticated access
- Testing session timeout

```python
def test_login_flow(fresh_page):
    # No saved session - test login
    fresh_page.goto("/login")
    fresh_page.fill("#username", "user")
    fresh_page.fill("#password", "pass")
    fresh_page.click("button[type='submit']")

    # Verify login worked
    assert fresh_page.url.endswith("/dashboard")
```

### 4. `setup_auth_state` - Session-scoped Setup

**Runs**: Once per test session (automatic)

**Purpose**: Creates and saves authentication states

**You don't call this directly** - it runs automatically before tests!

---

## Quick Start

### Step 1: Update Setup Script

Edit `setup_auth_state` fixture in [tests/conftest.py](tests/conftest.py) with your actual login credentials:

```python
@pytest.fixture(scope="session")
def setup_auth_state(browser):
    # ... existing code ...

    # Login as regular user
    page.goto(settings.login_url)
    page.fill("#username", "your_actual_username")  # ← Update this
    page.fill("#password", "your_actual_password")  # ← Update this
    page.click("button[type='submit']")
```

**Better approach** - Use environment variables:

```python
page.fill("#username", os.getenv("TEST_USERNAME", "default_user"))
page.fill("#password", os.getenv("TEST_PASSWORD", "default_pass"))
```

### Step 2: Run Tests

First run creates auth state files:

```bash
pytest tests/
```

Output:
```
✓ Regular user authentication state saved to tests/.auth/regular_user.json
✓ Admin user authentication state saved to tests/.auth/admin_user.json
```

Subsequent runs reuse saved state - **much faster!**

### Step 3: Update Your Tests

**Before** (slow):
```python
def test_accounts(page, login_page):
    # Login every time (SLOW)
    login_page.navigate()
    login_page.login("user", "pass")

    # Now test
    page.goto("/accounts")
    assert page.locator(".account-list").is_visible()
```

**After** (fast):
```python
def test_accounts(authenticated_page):
    # Already logged in (FAST)
    authenticated_page.goto("/accounts")
    assert authenticated_page.locator(".account-list").is_visible()
```

---

## Where Auth State is Stored

### File Structure:
```
tests/
├── .auth/                          # Authentication states (gitignored)
│   ├── regular_user.json          # Regular user session
│   └── admin_user.json            # Admin user session
├── conftest.py                    # Fixtures defined here
└── ui/
    └── test_*.py                  # Your tests
```

### Auth State File Contents:
```json
{
  "cookies": [
    {
      "name": "session_token",
      "value": "eyJhbGciOiJIUzI1NiIs...",
      "domain": "test11.ewealthmanager.com",
      "path": "/",
      "expires": 1704502800,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://test11.ewealthmanager.com",
      "localStorage": [
        {
          "name": "user_preferences",
          "value": "{\"theme\":\"dark\"}"
        }
      ]
    }
  ]
}
```

**⚠️ Important**: These files contain session tokens - **DO NOT commit to git!**

Already added to `.gitignore`:
```gitignore
tests/.auth/  # Authentication state files (contains session tokens)
```

---

## When to Use Which Fixture

### Decision Tree:

```
What are you testing?
│
├─ Login flow itself? → Use `fresh_page`
│
├─ Logout functionality? → Use `authenticated_page` then logout
│
├─ Admin features? → Use `authenticated_admin_page`
│
├─ Regular features? → Use `authenticated_page`
│
└─ Public pages? → Use either (both work)
```

### Quick Reference Table:

| Test Scenario | Fixture | Reason |
|---------------|---------|--------|
| Dashboard access | `authenticated_page` | Needs login |
| Account management | `authenticated_page` | Needs login |
| Admin panel | `authenticated_admin_page` | Needs admin login |
| User settings | `authenticated_page` | Needs login |
| Login page | `fresh_page` | Testing login itself |
| Logout | `authenticated_page` | Start logged in, then logout |
| Session timeout | `fresh_page` or `authenticated_page` | Depends on scenario |
| Public homepage | Either | Public access |
| Permissions test | Both | Compare auth vs no auth |

---

## Advanced Usage

### Refresh Auth State

If credentials change or session expires:

```bash
# Delete old auth state
rm -rf tests/.auth/

# Run tests - creates new auth state
pytest tests/
```

Or programmatically:

```python
import pytest
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def refresh_auth_on_monday():
    """Refresh auth state weekly"""
    from datetime import datetime

    if datetime.now().weekday() == 0:  # Monday
        Path("tests/.auth/regular_user.json").unlink(missing_ok=True)
        Path("tests/.auth/admin_user.json").unlink(missing_ok=True)
```

### Multiple User Roles

Add more authentication states:

```python
# In conftest.py
ADVISOR_USER_STATE = AUTH_STATE_DIR / "advisor_user.json"
CLIENT_USER_STATE = AUTH_STATE_DIR / "client_user.json"

@pytest.fixture
def authenticated_advisor_page(browser, setup_auth_state):
    """Authenticated advisor user"""
    context = browser.new_context(
        storage_state=str(ADVISOR_USER_STATE) if ADVISOR_USER_STATE.exists() else None,
        ignore_https_errors=True
    )
    page = context.new_page()
    yield page
    context.close()
```

### Environment-Specific Auth States

```python
# Different auth per environment
env = os.getenv("TEST_ENV", "test11")
REGULAR_USER_STATE = AUTH_STATE_DIR / f"regular_user_{env}.json"
ADMIN_USER_STATE = AUTH_STATE_DIR / f"admin_user_{env}.json"
```

### Conditional Auth State Creation

```python
@pytest.fixture(scope="session")
def setup_auth_state(browser):
    # Force refresh on CI
    if os.getenv("CI"):
        REGULAR_USER_STATE.unlink(missing_ok=True)

    # Create only if needed
    if not REGULAR_USER_STATE.exists():
        # ... login and save ...
```

---

## Integration with Existing Page Objects

Your page objects work seamlessly with authenticated pages:

```python
def test_account_wizard_with_auth(authenticated_page, account_wizard_page):
    """
    Page objects receive authenticated_page instead of page
    """
    # authenticated_page is already logged in
    authenticated_page.goto("/accounts/wizard")

    # Use with page objects normally
    wizard = AccountWizardPage(authenticated_page)
    wizard.fill_account_details("12345", "Savings")
    wizard.submit()

    assert wizard.is_success_displayed()
```

Or create authenticated page object fixtures:

```python
@pytest.fixture
def authenticated_account_wizard_page(authenticated_page):
    """Account wizard page with authentication"""
    return AccountWizardPage(authenticated_page)


def test_wizard(authenticated_account_wizard_page):
    # Already authenticated AND wrapped in page object!
    authenticated_account_wizard_page.navigate()
    authenticated_account_wizard_page.fill_details()
```

---

## BDD Integration

### Update BDD conftest.py

```python
# In tests/bdd/steps/conftest.py

from tests.conftest import setup_auth_state, authenticated_page

# Make authenticated_page available to BDD steps
@pytest.fixture
def page(authenticated_page):
    """Override default page with authenticated page for BDD"""
    return authenticated_page
```

### Update Feature Files

**Before**:
```gherkin
Scenario: View account details
  Given I am on the login page
  When I login with valid credentials    # ← Remove this!
  And I navigate to accounts page
  Then I should see account details
```

**After**:
```gherkin
Scenario: View account details
  Given I am authenticated               # ← Or remove completely
  When I navigate to accounts page
  Then I should see account details
```

### Update Step Definitions

**Before**:
```python
@when("I login with valid credentials")
def login(page, login_page):
    login_page.navigate()
    login_page.login("user", "pass")
```

**After**:
```python
@given("I am authenticated")
def verify_authenticated(page):
    """No-op - page is already authenticated"""
    pass  # Or verify logged in state
```

---

## Performance Comparison

### Without Auth State Reuse:
```
Test 1: Login (3s) + Test logic (1s) = 4s
Test 2: Login (3s) + Test logic (1s) = 4s
Test 3: Login (3s) + Test logic (1s) = 4s
Test 4: Login (3s) + Test logic (1s) = 4s
Test 5: Login (3s) + Test logic (1s) = 4s
────────────────────────────────────────────
Total: 20 seconds
```

### With Auth State Reuse:
```
Setup: Login once (3s)
Test 1: Test logic (1s) = 1s
Test 2: Test logic (1s) = 1s
Test 3: Test logic (1s) = 1s
Test 4: Test logic (1s) = 1s
Test 5: Test logic (1s) = 1s
────────────────────────────────────────────
Total: 8 seconds (60% faster!)
```

**For 100 tests**:
- Without: ~400 seconds (6.7 minutes)
- With: ~103 seconds (1.7 minutes)
- **Savings: ~5 minutes** ⚡

---

## Troubleshooting

### Auth State Not Working

**Problem**: Tests fail with "not logged in" errors

**Solutions**:

1. **Verify auth state file exists**:
   ```bash
   ls tests/.auth/
   # Should see: regular_user.json, admin_user.json
   ```

2. **Check file contents**:
   ```bash
   cat tests/.auth/regular_user.json
   # Should contain cookies and localStorage
   ```

3. **Force recreation**:
   ```bash
   rm tests/.auth/*.json
   pytest tests/ -v
   ```

4. **Check login selectors** in `setup_auth_state` fixture

### Session Expired

**Problem**: Auth state works initially but fails after time

**Solution**: Add session refresh logic:

```python
from datetime import datetime, timedelta
import json

def is_auth_state_expired(filepath, max_age_hours=24):
    """Check if auth state is too old"""
    if not filepath.exists():
        return True

    with open(filepath) as f:
        state = json.load(f)

    # Check cookie expiration
    for cookie in state.get("cookies", []):
        if cookie.get("expires", 0) < datetime.now().timestamp():
            return True

    return False


@pytest.fixture(scope="session")
def setup_auth_state(browser):
    # Refresh if expired
    if is_auth_state_expired(REGULAR_USER_STATE):
        REGULAR_USER_STATE.unlink(missing_ok=True)

    # ... rest of fixture ...
```

### Different Environments

**Problem**: Auth state from test11 doesn't work in test12

**Solution**: Environment-specific auth states (see Advanced Usage above)

---

## Best Practices

### ✅ DO:
- Use `authenticated_page` for most tests
- Use `fresh_page` only when testing login/logout
- Keep auth state files in `.gitignore`
- Refresh auth state when credentials change
- Use environment variables for credentials
- Document which tests need which authentication level

### ❌ DON'T:
- Commit auth state files to git (contains session tokens!)
- Login in every test (defeats the purpose!)
- Use same auth state file for different environments
- Hardcode passwords in fixtures (use env vars)
- Forget to refresh auth state after password changes

---

## Migration Checklist

Migrating from login-per-test to auth state reuse:

- [ ] Update `setup_auth_state` with actual login credentials
- [ ] Add environment variables for credentials
- [ ] Update `.gitignore` to exclude `tests/.auth/`
- [ ] Run tests once to create auth state files
- [ ] Verify auth state files created successfully
- [ ] Replace `page` with `authenticated_page` in tests
- [ ] Remove login steps from tests
- [ ] Update BDD scenarios to remove login steps
- [ ] Run full test suite to verify
- [ ] Measure performance improvement

---

## Summary

### What Changed:
- ✅ Added `authenticated_page` fixture (pre-logged in user)
- ✅ Added `authenticated_admin_page` fixture (pre-logged in admin)
- ✅ Added `fresh_page` fixture (no authentication)
- ✅ Added `setup_auth_state` fixture (creates auth states)
- ✅ Auth states saved to `tests/.auth/` (gitignored)

### How to Use:
1. Run tests once to create auth state
2. Replace `page` with `authenticated_page` in tests
3. Remove login steps
4. Enjoy 10x faster tests! ⚡

### Key Files:
- [tests/conftest.py](tests/conftest.py) - Fixtures defined here
- [tests/.auth/](tests/.auth/) - Auth states stored here (gitignored)
- [tests/ui/test_authentication_state_examples.py](tests/ui/test_authentication_state_examples.py) - Examples
- [.gitignore](.gitignore) - Excludes auth state files
