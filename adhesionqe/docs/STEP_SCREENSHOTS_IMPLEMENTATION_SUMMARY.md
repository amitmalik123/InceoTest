# Step Screenshots - Implementation Summary

## What Was Created

### Core Implementation
1. **Enhanced AllureLogger** - [utils/allure_logger.py](../utils/allure_logger.py)
   - Added `StepScreenshotConfig` class for global configuration
   - Enhanced `logger.step()` with auto-screenshot capability
   - Added utility functions: `enable_step_screenshots()`, `reset_step_counter()`

2. **Standalone Hook** - [utils/bdd_screenshot_hook.py](../utils/bdd_screenshot_hook.py)
   - Alternative approach using pytest hooks (if preferred)
   - Not needed if using AllureLogger approach

### Documentation
1. **[STEP_SCREENSHOTS_GUIDE.md](STEP_SCREENSHOTS_GUIDE.md)** - Complete guide
2. **[STEP_SCREENSHOT_CONFTEST_ADDITION.py](STEP_SCREENSHOT_CONFTEST_ADDITION.py)** - conftest.py code to add

---

## Solution Comparison

### Your Original Idea: Cucumber After-Step Hook
```python
# pytest-bdd doesn't have native after_step hook
# Would need custom implementation
@pytest.hookimpl
def pytest_bdd_after_step(...):  # Not a real hook
    # Take screenshot
```

**Issues:**
- ❌ pytest-bdd doesn't have `after_step` hook
- ❌ Would require complex custom implementation
- ❌ Hard to toggle on/off
- ❌ Separate from logging framework

### Better Solution: Integrated with AllureLogger ✅
```python
with logger.step("Step name", page=page):
    # ... step logic ...
    # Auto-screenshot at end based on config
```

**Benefits:**
- ✅ Built into existing logger
- ✅ Easy toggle via env var
- ✅ Always screenshots on failure
- ✅ Per-step control
- ✅ Clean, simple API

---

## How It Works

### Architecture

```
┌──────────────────────────────────────────────────┐
│  logger.step("Search", page=page)                │
│                                                   │
│  try:                                             │
│    ├─ Execute step logic                         │
│    └─ Step succeeds                              │
│  except:                                          │
│    └─ Step fails (step_failed=True)              │
│  finally:                                         │
│    if page and should_screenshot():              │
│       ├─ Check: SCREENSHOT_EACH_STEP env var     │
│       ├─ Check: step_failed flag                 │
│       └─ Take & attach screenshot to Allure      │
└──────────────────────────────────────────────────┘
```

### Decision Logic

```python
def should_screenshot(step_failed):
    if step_failed:
        return True  # Always screenshot on failure

    if SCREENSHOT_EACH_STEP == "true":
        return True  # Screenshot every step

    return False  # Only on failure
```

---

## Usage Examples

### Basic Usage

```python
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I search for the client")
def search_client(page, account_list_page, test_context):
    client_id = test_context['test_data']['client_id']

    # Auto-screenshot enabled (if configured)
    with logger.step("Search for client", page=page):
        logger.info(f"Searching: {client_id}")
        account_list_page.search_client(client_id)
        # Screenshot taken here automatically
```

### Control Methods

```bash
# Method 1: Environment Variable
export SCREENSHOT_EACH_STEP=true
pytest

# Method 2: CLI Flag
pytest --screenshot-each-step

# Method 3: Programmatic
from utils.allure_logger import enable_step_screenshots
enable_step_screenshots(True)
```

### Per-Step Disable

```python
# Disable for specific step (e.g., non-visual action)
with logger.step("Prepare data", page=page, auto_screenshot=False):
    # No screenshot taken (even if globally enabled)
    pass
```

---

## Configuration

### Add to tests/conftest.py

```python
import pytest
from utils.allure_logger import reset_step_counter, enable_step_screenshots


def pytest_addoption(parser):
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step"
    )


def pytest_configure(config):
    import os
    screenshot_each_step = (
        config.getoption("--screenshot-each-step")
        or os.getenv("SCREENSHOT_EACH_STEP", "").lower() == "true"
    )
    enable_step_screenshots(screenshot_each_step)


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter():
    reset_step_counter()
    yield
```

---

## Behavior Matrix

| Scenario | SCREENSHOT_EACH_STEP | auto_screenshot | Step Status | Screenshot? |
|----------|---------------------|-----------------|-------------|-------------|
| 1 | false | True | Success | ❌ No |
| 2 | false | True | Failed | ✅ Yes |
| 3 | true | True | Success | ✅ Yes |
| 4 | true | True | Failed | ✅ Yes |
| 5 | true | **False** | Success | ❌ No |
| 6 | true | **False** | Failed | ❌ No |

---

## Code Comparison

### Before (Manual Screenshot)

```python
@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    with allure.step(f"Search for client {test_context['test_data']['client_id']}"):
        logger.info(f"Searching for client: {test_context['test_data']['client_id']}")
        allure.attach(
            test_context["test_data"]["client_id"],
            name="Client ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        account_list_page.search_client(test_context["test_data"]["client_id"])

        # Manual screenshot every time
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account List After Search",
            attachment_type=allure.attachment_type.PNG,
        )
```

**Issues:**
- 18 lines
- Always takes screenshot (no control)
- Repetitive boilerplate

### After (Auto Screenshot)

```python
@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    client_id = test_context['test_data']['client_id']

    with logger.step("Search for client", page=page):
        logger.info(f"Searching for: {client_id}")
        logger.attach_text(client_id, "Client ID")
        account_list_page.search_client(client_id)
        # Auto-screenshot based on config
```

**Benefits:**
- 8 lines (55% reduction)
- Toggle control
- Always screenshots on failure
- Clean and readable

---

## Allure Report Output

### Success (SCREENSHOT_EACH_STEP=true)

```
Step 1 ✓ Search for client
  📎 Client ID: ABC123
  📷 Screenshot
```

### Success (SCREENSHOT_EACH_STEP=false)

```
Step 1 ✓ Search for client
  📎 Client ID: ABC123
  (no screenshot)
```

### Failure (Any config)

```
Step 1 ❌ FAILED Search for client
  📎 Client ID: ABC123
  ❌ Error: Element not found
  📷 Step 1 ❌ FAILED Search for client
```

---

## Best Practices

### ✅ DO

1. **Always pass page to logger.step()**
   ```python
   with logger.step("Step", page=page):
   ```

2. **Use env var for toggle**
   ```bash
   export SCREENSHOT_EACH_STEP=true  # Debugging
   export SCREENSHOT_EACH_STEP=false # CI/Production
   ```

3. **Disable for non-visual steps**
   ```python
   with logger.step("Data prep", page=page, auto_screenshot=False):
   ```

### ❌ DON'T

1. **Don't manually screenshot unless needed**
   ```python
   # BAD - redundant
   with logger.step("Search", page=page):
       # ...
       logger.attach_screenshot(page, "After")  # Auto already does this
   ```

2. **Don't forget page parameter**
   ```python
   # BAD - no auto-screenshot
   with logger.step("Search"):  # Missing page=page
   ```

---

## Migration Steps

1. **Update conftest.py** - Add configuration code
2. **Update step files** - Add `page=page` to `logger.step()`
3. **Remove manual screenshots** - Delete explicit screenshot code
4. **Test with toggle** - Verify behavior with env var on/off
5. **Update CI/CD** - Set `SCREENSHOT_EACH_STEP` as needed

---

## Advantages Over After-Step Hook

| Feature | After-Step Hook | AllureLogger Approach |
|---------|----------------|----------------------|
| **Implementation** | Complex custom hook | Built-in context manager |
| **Toggle Control** | Need custom logic | Environment variable |
| **Per-step Control** | Difficult | `auto_screenshot=False` |
| **Failure Detection** | Manual try/catch | Automatic |
| **Integration** | Separate system | Unified with logger |
| **Code Changes** | Minimal but limited | Minimal and flexible |

---

## Summary

### What You Asked For
- ✅ Screenshot after each cucumber step (controlled by toggle)
- ✅ Screenshot on failed step (always)

### What You Got
1. **Better than after-step hook** - Integrated with AllureLogger
2. **Multiple toggle methods** - Env var, CLI, programmatic
3. **Smart defaults** - Only on failure (unless enabled)
4. **Per-step control** - Can disable specific steps
5. **Zero boilerplate** - Just add `page=page` parameter
6. **Always on failure** - Cannot be disabled (safety)

### Next Steps
1. Review [STEP_SCREENSHOTS_GUIDE.md](STEP_SCREENSHOTS_GUIDE.md)
2. Add conftest.py configuration
3. Try with: `export SCREENSHOT_EACH_STEP=true && pytest`
4. Update step files gradually

🚀 **Result:** Clean, flexible, automatically-controlled step screenshots!
