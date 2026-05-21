# Session Storage Testing Guide

## Overview
This guide demonstrates Playwright's authentication state management - **THE KEY FEATURE** that allows you to login once and reuse the session across all tests.

---

## Key Concept: Authentication State

### Traditional Approach ❌
```python
def test_feature_1(page):
    page.goto("login")
    page.fill("username", "...")
    page.fill("password", "...")
    page.click("submit")  # Login every time!
    # Test feature 1

def test_feature_2(page):
    page.goto("login")
    page.fill("username", "...")  # Login again!
    page.fill("password", "...")
    page.click("submit")
    # Test feature 2
```

**Problem**: Every test logs in → Slow, redundant, wastes time!

### Playwright Approach ✅
```python
@pytest.fixture(scope="session")
def setup_auth_state(browser):
    # Login ONCE per test session
    # Save session to file

def test_feature_1(authenticated_page):
    # Already logged in! No login step!
    # Test feature 1

def test_feature_2(authenticated_page):
    # Still logged in! Session reused!
    # Test feature 2
```

**Benefit**: Login ONCE → All tests reuse session → 10x faster!

---

## How It Works

### Step 1: Setup Authentication (Once)
```python
# conftest.py
@pytest.fixture(scope="session")
def setup_auth_state(browser):
    """
    Runs ONCE per test session
    Logs in and saves session to tests/.auth/regular_user.json
    """
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("login_url")
    page.fill("username", "user")
    page.fill("password", "pass")
    page.click("submit")

    # Save authentication state
    context.storage_state(path="tests/.auth/regular_user.json")

    context.close()
```

### Step 2: Reuse Session (All Tests)
```python
@pytest.fixture
def authenticated_page(browser, setup_auth_state):
    """
    Every test gets this fixture
    Loads saved session from file
    NO LOGIN REQUIRED!
    """
    context = browser.new_context(
        storage_state="tests/.auth/regular_user.json"  # Load session!
    )
    page = context.new_page()
    yield page
    context.close()
```

### Step 3: Use in Tests
```python
def test_my_feature(authenticated_page):
    # No login step - just start testing!
    authenticated_page.goto("dashboard")
    # Test your feature...
```

---

## What's Stored?

The `tests/.auth/regular_user.json` file contains:

```json
{
  "cookies": [
    {"name": "sessionId", "value": "abc123..."},
    {"name": "authToken", "value": "xyz789..."}
  ],
  "origins": [
    {
      "origin": "https://your-app.com",
      "localStorage": [
        {"name": "user", "value": "{...}"}
      ],
      "sessionStorage": [
        {"name": "token", "value": "..."}
      ]
    }
  ]
}
```

This includes:
- 🍪 Cookies
- 💾 localStorage data
- 📦 sessionStorage data
- 🔐 Authentication tokens

---

## Running the Tests

### Test 1: Create Authentication State
```powershell
# First run creates the auth state file
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_create_auth_state -v --headed --slowmo=500
```

**What happens:**
1. `setup_auth_state` fixture runs (login happens)
2. Session saved to `tests/.auth/regular_user.json`
3. Test verifies file exists and contains data

**Expected Output:**
```
✅ Auth state file exists: tests/.auth/regular_user.json
✅ Contains 5 cookies
✅ Contains 1 storage origins
✅ Sample cookie: sessionId
```

---

### Test 2: Verify Session Reuse
```powershell
# This test uses saved session - NO LOGIN!
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_authenticated_page_reuses_session -v --headed
```

**What happens:**
1. Test loads session from file
2. No login step - directly authenticated
3. Navigates to dashboard
4. Verifies not redirected to login

**Expected Output:**
```
✅ Current URL: https://test11.ewealthmanager.com/dashboard
✅ Screenshot saved to: reports/authenticated_page.png
✅ Session reused successfully - NO LOGIN REQUIRED!
```

---

### Test 3: Fresh Page (No Session)
```powershell
# Compare: page WITHOUT saved session
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_fresh_page_has_no_session -v --headed
```

**What happens:**
1. Test uses `fresh_page` fixture (no auth state)
2. Should redirect to login page
3. Demonstrates difference between authenticated vs fresh pages

---

### Test 4: Multiple Pages, Same Session
```powershell
# Multiple browser contexts sharing same session
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_multiple_authenticated_pages_share_session -v --headed
```

**What happens:**
1. Creates 2 separate browser contexts
2. Both load same auth state file
3. Both are authenticated
4. Demonstrates session sharing

**Expected Output:**
```
✅ Page 1 URL: https://test11.ewealthmanager.com/
✅ Page 2 URL: https://test11.ewealthmanager.com/
✅ Multiple pages successfully reused same session!
```

---

### Run All Session Storage Tests
```powershell
# Run entire test suite
pytest tests/ui/test_session_storage_demo.py -v --headed --slowmo=500
```

---

## Practical Usage Examples

### Example 1: BDD Test with Authentication
```python
# tests/ui/test_add_ach.py
def test_add_ach_authenticated(authenticated_page, bdd_context):
    """
    BDD test that uses authenticated session
    NO LOGIN STEP IN FEATURE FILE!
    """
    scenarios('../bdd/features/add_ACH.feature')
```

### Example 2: Multiple User Sessions
```python
def test_admin_vs_regular_user(authenticated_page, authenticated_admin_page):
    """
    Test with 2 different users simultaneously
    Both use saved sessions - no login steps!
    """
    # Regular user page
    authenticated_page.goto("dashboard")
    regular_data = authenticated_page.locator(".user-data").text_content()

    # Admin user page
    authenticated_admin_page.goto("admin-panel")
    admin_data = authenticated_admin_page.locator(".admin-data").text_content()

    # Compare behavior
    assert regular_data != admin_data
```

### Example 3: Performance Comparison
```python
def test_speed_improvement():
    """
    Session reuse is ~10x faster than logging in every time
    """
    # Login every time: ~5-10 seconds
    # Session reuse: ~0.5-1 second
    # Improvement: 90%+ faster!
```

---

## File Structure

```
DM1TestAutomation/
├── tests/
│   ├── .auth/                          # Authentication states (gitignored)
│   │   ├── regular_user.json           # Regular user session
│   │   └── admin_user.json             # Admin user session
│   ├── conftest.py                     # Fixtures (setup_auth_state, authenticated_page)
│   └── ui/
│       └── test_session_storage_demo.py  # Session storage tests
└── .gitignore                          # Excludes tests/.auth/
```

---

## Available Fixtures

### Authentication Fixtures

| Fixture | Purpose | Login Required? | Use Case |
|---------|---------|-----------------|----------|
| `authenticated_page` | Pre-authenticated regular user | ❌ No | Most tests |
| `authenticated_admin_page` | Pre-authenticated admin user | ❌ No | Admin tests |
| `fresh_page` | Clean page, no auth | ✅ Yes | Testing login flow |
| `new_page(context)` | New tab, same session | ❌ No | Multiple tabs |
| `new_context(browser)` | New session, different user | ✅ Yes | Multi-user tests |

### Session Management Fixtures

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `setup_auth_state` | Session | Creates auth state files (runs once) |
| `browser` | Function | Provided by pytest-playwright |
| `context` | Function | Provided by pytest-playwright |
| `page` | Function | Provided by pytest-playwright |

---

## Configuration

### Current Setup (test11 environment)

**File**: `tests/conftest.py`
```python
# Login credentials from data/test_data.test11.csv
LOGIN_URL = "https://test11.ewealthmanager.com/ewmLogin/account/login"
USERNAME = "T11_AGA1G1_Perf"
PASSWORD = "QAAdminUser_33a"

# Auth state storage
AUTH_STATE_DIR = Path("tests/.auth")
REGULAR_USER_STATE = AUTH_STATE_DIR / "regular_user.json"
ADMIN_USER_STATE = AUTH_STATE_DIR / "admin_user.json"
```

### Changing Environments

To use different environment (qa, silo, prod):

1. Update credentials in `conftest.py`:
```python
# For QA environment
LOGIN_URL = settings.login_url  # From env.qa.yaml
USERNAME = "qa_user"
PASSWORD = "qa_password"
```

2. Delete old auth states:
```powershell
Remove-Item tests\.auth\*.json
```

3. Run setup again:
```powershell
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_create_auth_state -v
```

---

## Troubleshooting

### Problem: Auth state file not created

**Solution:**
```powershell
# Check setup_auth_state fixture runs
pytest tests/ui/test_session_storage_demo.py -v -s --setup-show

# Look for "SETUP    S setup_auth_state" in output
```

### Problem: Test redirects to login page

**Causes:**
1. Auth state file doesn't exist
2. Session expired
3. Wrong credentials

**Solution:**
```powershell
# Delete and recreate auth state
Remove-Item tests\.auth\*.json
pytest tests/ui/test_session_storage_demo.py::TestSessionStorage::test_create_auth_state -v --headed --slowmo=500

# Watch login process to verify it works
```

### Problem: Tests are slow

**Check:**
```powershell
# Verify using authenticated_page, not fresh_page
grep -r "def test.*fresh_page" tests/

# Should use authenticated_page for most tests
```

### Problem: Login selectors don't match

**Solution:**
Update `tests/conftest.py`:
```python
# Try different selectors
page.fill("input[name='userName']", username)  # Current
page.fill("input[id='username']", username)    # Alternative
page.fill("#username", username)               # CSS selector
```

---

## Performance Benefits

### Test Suite Example

**Without Session Reuse:**
```
100 tests × 5 seconds per login = 500 seconds (8.3 minutes)
```

**With Session Reuse:**
```
1 login × 5 seconds + 100 tests × 0.5 seconds = 55 seconds
```

**Improvement: 90% faster! ⚡**

---

## Best Practices

### ✅ Do This
- Use `authenticated_page` for most tests
- Keep auth state files in `.gitignore`
- Use `setup_auth_state` fixture (session-scoped)
- Run auth setup once, reuse everywhere

### ❌ Don't Do This
- Don't login in every test
- Don't commit auth state files to git
- Don't use `fresh_page` for regular tests
- Don't create multiple auth states unnecessarily

---

## Next Steps

1. **Run the demo tests**:
   ```powershell
   pytest tests/ui/test_session_storage_demo.py -v --headed
   ```

2. **Update your existing tests**:
   ```python
   # Before
   def test_my_feature(page):
       page.goto("login")
       # login steps...

   # After
   def test_my_feature(authenticated_page):
       # No login - start testing!
   ```

3. **Measure improvement**:
   ```powershell
   # Before (with login)
   Measure-Command { pytest tests/ui/test_add_ach.py }

   # After (with session reuse)
   Measure-Command { pytest tests/ui/test_add_ach.py }
   ```

---

## Summary

✅ **Session Storage = Login Once, Test Everywhere**

- Authentication state saved to `tests/.auth/regular_user.json`
- All tests reuse this session automatically
- No login steps needed in tests
- 10x faster test execution
- Playwright handles cookies, localStorage, sessionStorage

🎯 **This is THE KEY FEATURE of Playwright** - Use it in all your tests!

---

## Related Documentation

- [AUTHENTICATION_STATE_GUIDE.md](AUTHENTICATION_STATE_GUIDE.md) - Complete auth state guide
- [MULTI_CONTEXT_GUIDE.md](MULTI_CONTEXT_GUIDE.md) - Multiple users/sessions
- [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) - Overall framework architecture
- [Playwright Storage State Docs](https://playwright.dev/docs/auth)
