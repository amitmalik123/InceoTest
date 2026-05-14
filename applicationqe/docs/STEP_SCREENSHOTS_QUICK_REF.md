# Step Screenshots - Quick Reference

## Enable/Disable

```bash
# Enable for all steps
export SCREENSHOT_EACH_STEP=true
pytest

# Or CLI
pytest --screenshot-each-step

# Disable (default - only on failure)
export SCREENSHOT_EACH_STEP=false
pytest
```

## Step File Usage

```python
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I search for the client")
def search_client(page, account_list_page, test_context):
    # Pass page to enable auto-screenshot
    with logger.step("Search for client", page=page):
        logger.info("Searching...")
        account_list_page.search_client(client_id)
        # Screenshot auto-taken here (if enabled or failed)
```

## Behavior

| Config | Step Status | Screenshot? |
|--------|-------------|-------------|
| SCREENSHOT_EACH_STEP=false | Success | ❌ No |
| SCREENSHOT_EACH_STEP=false | Failed | ✅ Yes |
| SCREENSHOT_EACH_STEP=true | Success | ✅ Yes |
| SCREENSHOT_EACH_STEP=true | Failed | ✅ Yes |

## Per-Step Control

```python
# Disable for specific step
with logger.step("Fast step", page=page, auto_screenshot=False):
    # No screenshot even if globally enabled
    pass

# Without page = no auto-screenshot
with logger.step("No page step"):
    # No screenshot capability
    pass
```

## conftest.py Setup

```python
import pytest
from utils.allure_logger import reset_step_counter, enable_step_screenshots

def pytest_addoption(parser):
    parser.addoption("--screenshot-each-step", action="store_true", default=False)

def pytest_configure(config):
    import os
    enabled = (config.getoption("--screenshot-each-step")
               or os.getenv("SCREENSHOT_EACH_STEP", "").lower() == "true")
    enable_step_screenshots(enabled)

@pytest.fixture(autouse=True)
def reset_step_screenshot_counter():
    reset_step_counter()
    yield
```

## Key Points

- ✅ **Always screenshots on failure** (cannot disable)
- ✅ **Toggle for success screenshots** (env var or CLI)
- ✅ **Pass `page` parameter** to enable auto-screenshot
- ✅ **Use `auto_screenshot=False`** to disable specific steps
- ✅ **Zero manual screenshot code** needed

## Migration

```python
# Before
with allure.step("Search"):
    account_list_page.search_client(client_id)
    screenshot = page.screenshot()
    allure.attach(screenshot, name="After", ...)

# After
with logger.step("Search", page=page):
    account_list_page.search_client(client_id)
    # Auto-screenshot handled
```
