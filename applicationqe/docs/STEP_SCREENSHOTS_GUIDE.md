# Automatic Step Screenshots Guide

## Overview

This framework now supports **automatic screenshots** after each BDD step with:
- ✅ **Toggle control** (enable/disable via env var or CLI)
- ✅ **Always screenshot on failure** (cannot be disabled)
- ✅ **Integrated with AllureLogger** (clean, simple API)
- ✅ **Per-step control** (disable for specific steps)
- ✅ **Zero boilerplate** in step files

---

## Quick Start

### Method 1: Environment Variable (Recommended)
```bash
# Linux/Mac
export SCREENSHOT_EACH_STEP=true
pytest

# Windows PowerShell
$env:SCREENSHOT_EACH_STEP="true"
pytest

# Windows CMD
set SCREENSHOT_EACH_STEP=true
pytest
```

### Method 2: Command-Line Flag
```bash
pytest --screenshot-each-step
```

### Method 3: Programmatic Control
```python
# In conftest.py
from utils.allure_logger import enable_step_screenshots

def pytest_configure(config):
    enable_step_screenshots(True)  # Enable for all tests
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│         AllureLogger.step()                         │
│  ┌───────────────────────────────────────────────┐  │
│  │  1. Execute step logic                        │  │
│  │  2. Catch any exceptions                      │  │
│  │  3. Take screenshot if:                       │  │
│  │     - SCREENSHOT_EACH_STEP=true (all steps)   │  │
│  │     - OR step failed (always)                 │  │
│  │  4. Attach to Allure with status              │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Default Behavior

| Scenario | Screenshot Taken? |
|----------|-------------------|
| **Step succeeds** + `SCREENSHOT_EACH_STEP=false` | ❌ No |
| **Step succeeds** + `SCREENSHOT_EACH_STEP=true` | ✅ Yes |
| **Step fails** + `SCREENSHOT_EACH_STEP=false` | ✅ Yes (always) |
| **Step fails** + `SCREENSHOT_EACH_STEP=true` | ✅ Yes (always) |

---

## Usage

### Updated Step Files

```python
from playwright.sync_api import Page
from pytest_bdd import when, then
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context['test_data']['client_id']

    # Pass page to enable auto-screenshot
    with logger.step("Search for client", page=page):
        logger.info(f"Searching for: {client_id}")
        logger.attach_text(client_id, "Client ID")

        account_list_page.search_client(client_id)
        # Screenshot automatically taken here based on config


@then("I should see the Account List page")
def verify_account_list(page: Page):
    """Verify Account List page is loaded"""
    with logger.step("Verify Account List page", page=page):
        page.wait_for_load_state("domcontentloaded")
        logger.info("Account List page loaded")
        # Screenshot automatically taken here
```

### Disable Auto-Screenshot for Specific Step

```python
@when("I click logout")
def click_logout(page: Page, tracking_center_page):
    """Click logout - no screenshot needed"""
    # Disable auto-screenshot with auto_screenshot=False
    with logger.step("Click logout", page=page, auto_screenshot=False):
        tracking_center_page.click_logout()
        # No automatic screenshot (even if SCREENSHOT_EACH_STEP=true)
```

### Manual Screenshot Control

```python
@when("I perform complex action")
def complex_action(page: Page):
    """Multiple screenshots at different points"""
    with logger.step("Perform complex action", page=page, auto_screenshot=False):
        # Take screenshots manually at specific points
        logger.info("Starting action")
        logger.attach_screenshot(page, "Before Action")

        # ... do something ...

        logger.attach_screenshot(page, "After Step 1")

        # ... do more ...

        logger.attach_screenshot(page, "Final Result")
```

---

## Configuration

### conftest.py Addition

Add this to your `tests/conftest.py`:

```python
import pytest
from utils.allure_logger import reset_step_counter, enable_step_screenshots


def pytest_addoption(parser):
    """Add command-line option for step screenshots"""
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step"
    )


def pytest_configure(config):
    """Configure screenshot settings"""
    import os

    # Check CLI option or environment variable
    screenshot_each_step = (
        config.getoption("--screenshot-each-step", default=False)
        or os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes")
    )

    enable_step_screenshots(screenshot_each_step)

    status = "ENABLED for ALL steps" if screenshot_each_step else "ENABLED on failure only"
    print(f"\n📸 Step Screenshots: {status}\n")


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter():
    """Reset step counter before each test"""
    reset_step_counter()
    yield
```

---

## Allure Report Output

### With `SCREENSHOT_EACH_STEP=true`

```
Test: Search for Client

  Step 1: Login to application
    ✓ Screenshot

  Step 2: Navigate to Account List
    ✓ Screenshot

  Step 3: Search for client
    📎 Client ID: ABC123
    ✓ Screenshot

  Step 4: Verify results
    ✓ Screenshot
```

### With `SCREENSHOT_EACH_STEP=false` (Default)

```
Test: Search for Client

  Step 1: Login to application
    (no screenshot)

  Step 2: Navigate to Account List
    (no screenshot)

  Step 3: Search for client
    📎 Client ID: ABC123
    (no screenshot unless failed)

  Step 4: Verify results - FAILED
    ❌ Error: Element not found
    ❌ FAILED Screenshot  ← Automatically taken on failure
```

---

## Advanced Usage

### Per-Test Control

```python
def test_with_screenshots(page):
    """This test takes screenshots after each step"""
    from utils.allure_logger import enable_step_screenshots

    enable_step_screenshots(True)  # Enable for this test only

    # ... test steps ...


def test_without_screenshots(page):
    """This test only screenshots on failure"""
    from utils.allure_logger import enable_step_screenshots

    enable_step_screenshots(False)  # Disable for this test

    # ... test steps ...
```

### Check Current Configuration

```python
from utils.allure_logger import get_step_screenshot_config

config = get_step_screenshot_config()
print(f"Enabled: {config.enabled}")
print(f"Step counter: {config.step_counter}")
```

---

## Comparison: Old vs New

### Old Approach ❌

```python
@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    with allure.step("Search for client"):
        logger.info(f"Searching for: {test_context['test_data']['client_id']}")
        allure.attach(
            test_context["test_data"]["client_id"],
            name="Client ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        account_list_page.search_client(test_context["test_data"]["client_id"])

        # Manual screenshot every time (no control)
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account List After Search",
            attachment_type=allure.attachment_type.PNG,
        )
```

**Problems:**
- Screenshot ALWAYS taken (even when not needed)
- No toggle control
- 18 lines of code
- Repetitive boilerplate

### New Approach ✅

```python
@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    client_id = test_context['test_data']['client_id']

    with logger.step("Search for client", page=page):
        logger.info(f"Searching for: {client_id}")
        logger.attach_text(client_id, "Client ID")
        account_list_page.search_client(client_id)
        # Auto-screenshot based on config (or on failure)
```

**Benefits:**
- ✅ Screenshot controlled by toggle
- ✅ Always screenshots on failure
- ✅ 7 lines of code (61% reduction)
- ✅ Clean and readable

---

## Best Practices

### ✅ DO

1. **Pass `page` parameter to enable auto-screenshot**
   ```python
   with logger.step("Step name", page=page):
       # Auto-screenshot enabled
   ```

2. **Use toggle for debugging/CI differences**
   ```bash
   # Local debugging - take all screenshots
   export SCREENSHOT_EACH_STEP=true
   pytest

   # CI pipeline - only on failure (faster)
   pytest
   ```

3. **Disable for fast/non-visual steps**
   ```python
   with logger.step("Prepare test data", page=page, auto_screenshot=False):
       # No screenshot needed for data preparation
   ```

### ❌ DON'T

1. **Don't manually screenshot in every step**
   ```python
   # BAD
   with logger.step("Search"):
       # ...
       logger.attach_screenshot(page, "After Search")  # Redundant if auto-screenshot enabled
   ```

2. **Don't forget to pass page parameter**
   ```python
   # BAD - no auto-screenshot
   with logger.step("Search"):  # Missing page=page
       # ...

   # GOOD
   with logger.step("Search", page=page):
       # Auto-screenshot works
   ```

---

## Environment Variables Reference

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `SCREENSHOT_EACH_STEP` | `true`, `false`, `1`, `0`, `yes`, `no` | `false` | Enable screenshots after every step |

---

## CLI Reference

```bash
# Enable screenshots for all steps
pytest --screenshot-each-step

# Normal run (only screenshot on failure)
pytest

# Specific test with screenshots
pytest tests/test_search.py --screenshot-each-step

# Parallel with screenshots
pytest -n 4 --screenshot-each-step
```

---

## Summary

### Key Features

1. **Toggle Control**
   - Environment variable: `SCREENSHOT_EACH_STEP=true`
   - CLI flag: `--screenshot-each-step`
   - Programmatic: `enable_step_screenshots(True)`

2. **Smart Defaults**
   - Success: Screenshot only if enabled
   - Failure: **Always** screenshot (cannot disable)

3. **Zero Boilerplate**
   - Just pass `page` parameter: `logger.step("Step", page=page)`
   - Automatic screenshot handling

4. **Flexible**
   - Per-step control: `auto_screenshot=False`
   - Per-test control: `enable_step_screenshots()`
   - Global control: Environment variable

### Migration Path

1. Replace manual screenshots with `logger.step("Step", page=page)`
2. Remove explicit `page.screenshot()` and `allure.attach()` calls
3. Control via `SCREENSHOT_EACH_STEP` environment variable
4. Enjoy cleaner code and flexible screenshot control! 🚀
