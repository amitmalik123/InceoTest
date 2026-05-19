# Allure Logger - Best Practices Guide

## Problem with Old Approach

### Issues
1. **Too Verbose** - Repetitive `allure.step()`, `allure.attach()` everywhere
2. **Tight Coupling** - Step files handle both logging AND reporting
3. **No Reusability** - Pages/utilities can't contribute to Allure easily
4. **Inconsistent** - Different patterns in different files

### Old Pattern (BAD ❌)
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
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Account List After Search",
            attachment_type=allure.attachment_type.PNG
        )
```

**Problems:**
- 15 lines for simple action
- Imports `allure` in every file
- Manual screenshot handling
- Verbose attachment syntax

---

## New Solution: AllureLogger

### Benefits ✅
1. **Clean & Concise** - Single import, unified API
2. **Separation of Concerns** - Pages log, steps create report structure
3. **Works Everywhere** - Pages, utilities, fixtures, steps
4. **Flexible** - Control what goes to Allure vs console
5. **Type-Safe** - Better IDE support

### Installation

```python
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)
```

---

## Usage Patterns

### 1. Test Steps (BDD Step Definitions)

**Use `logger.step()` context manager for test steps:**

```python
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context['test_data']['client_id']

    with logger.step(f"Search for client {client_id}"):
        logger.info(f"Searching for client: {client_id}")
        logger.attach_text(client_id, "Client ID")

        account_list_page.search_client(client_id)
        logger.attach_screenshot(page, "Account List After Search")
```

**Benefits:**
- 8 lines vs 15 lines
- Cleaner, more readable
- Consistent pattern

---

### 2. Page Objects

**Pages should NOT use `logger.step()` - only log actions:**

```python
from utils.allure_logger import get_allure_logger

class AccountListPage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_allure_logger(self.__class__.__name__)

    def search_client(self, client_id: str) -> None:
        """Search for a client by ID"""
        # Simple logging - no allure.step() in pages
        self.logger.info(f"Searching for client: {client_id}")

        try:
            self.search_input.fill(client_id)
            self.search_input.press("Enter")
            self.logger.info(f"Search completed for: {client_id}")
        except Exception as e:
            # Errors auto-attach to Allure
            self.logger.error(f"Search failed: {str(e)}")
            raise
```

**Why no steps in pages?**
- Pages are reusable components
- Steps belong in test logic, not page objects
- Cleaner separation of concerns

---

### 3. Utilities

**Utilities can log important data to Allure:**

```python
from utils.allure_logger import get_allure_logger

class DatabaseHelper:
    def __init__(self):
        self.logger = get_allure_logger(self.__class__.__name__)

    def get_user_data(self, user_id: str) -> dict:
        """Fetch user data from database"""
        self.logger.info(f"Fetching data for user: {user_id}")

        try:
            user_data = self._query_db(user_id)

            # Attach to Allure for debugging
            self.logger.attach_json(user_data, f"User Data - {user_id}")
            return user_data

        except Exception as e:
            self.logger.error(f"Database query failed: {str(e)}")
            raise
```

---

### 4. Fixtures

**Fixtures can use steps for setup/teardown:**

```python
import pytest
from utils.allure_logger import get_allure_logger

logger = get_allure_logger("fixtures")

@pytest.fixture
def authenticated_page(page: Page):
    """Fixture that provides an authenticated page"""
    with logger.step("Setup authenticated session"):
        logger.info("Loading authentication state")
        page.goto("https://example.com")
        logger.attach_screenshot(page, "Initial Page Load")

        yield page

        logger.info("Tearing down session")
```

---

## API Reference

### Logging Methods

```python
# Basic logging
logger.debug("Debug message")              # Console only by default
logger.info("Info message")                # Console only by default
logger.warning("Warning message")          # Console + Allure by default
logger.error("Error message")              # Console + Allure by default
logger.critical("Critical message")        # Console + Allure by default

# Force attach to Allure
logger.info("Important info", attach_to_allure=True)
logger.debug("Debug data", attach_to_allure=True)

# Prevent Allure attachment
logger.warning("Minor warning", attach_to_allure=False)
```

### Allure Attachments

```python
# Text
logger.attach_text("Some text", "Attachment Name")

# JSON data
logger.attach_json({"key": "value"}, "JSON Data")

# Screenshot
logger.attach_screenshot(page, "Screenshot Name")

# HTML
logger.attach_html("<h1>Test</h1>", "HTML Content")

# Generic data
logger.attach_data(some_data, "Data Name", "TEXT")
```

### Context Manager (Steps)

```python
# Use in test steps only
with logger.step("Step description"):
    # Actions here
    pass

# Control console logging
with logger.step("Step description", log=False):
    # Won't log to console, only Allure
    pass
```

---

## Best Practices

### ✅ DO

1. **Use `logger.step()` in:**
   - Test step definitions (BDD steps)
   - Fixtures (setup/teardown)
   - High-level test orchestration

2. **Use simple logging in:**
   - Page Objects
   - Utilities
   - Helper functions

3. **Attach screenshots after actions:**
   ```python
   account_list_page.search_client(client_id)
   logger.attach_screenshot(page, "After Search")
   ```

4. **Attach important data:**
   ```python
   logger.attach_json(test_data, "Test Data")
   logger.attach_text(client_id, "Client ID")
   ```

5. **Use descriptive names:**
   ```python
   logger.attach_screenshot(page, "Account List After Search")  # Good
   logger.attach_screenshot(page, "Screenshot1")               # Bad
   ```

### ❌ DON'T

1. **Don't use `allure.step()` in page objects**
   ```python
   # BAD
   class AccountPage:
       def click_button(self):
           with allure.step("Click button"):  # ❌ Don't do this
               self.button.click()

   # GOOD
   class AccountPage:
       def click_button(self):
           self.logger.info("Clicking button")  # ✅ Do this
           self.button.click()
   ```

2. **Don't import `allure` directly in pages/utilities**
   ```python
   # BAD
   import allure  # ❌

   # GOOD
   from utils.allure_logger import get_allure_logger  # ✅
   ```

3. **Don't nest steps excessively**
   ```python
   # BAD - Too much nesting
   with logger.step("Main"):
       with logger.step("Sub 1"):
           with logger.step("Sub 2"):  # ❌ Too deep
               pass

   # GOOD - Flat structure
   with logger.step("Login"):
       login_page.enter_credentials()
       login_page.click_submit()  # Pages handle their own logging
   ```

4. **Don't attach every single log to Allure**
   ```python
   # BAD - Too noisy
   logger.info("Starting", attach_to_allure=True)
   logger.info("Step 1", attach_to_allure=True)
   logger.info("Step 2", attach_to_allure=True)  # ❌ Clutters report

   # GOOD - Selective attachment
   logger.info("Starting")  # Console only
   logger.attach_screenshot(page, "After Action")  # Important visual
   ```

---

## Migration Strategy

### Phase 1: Update Step Files (Priority)

1. Replace imports:
   ```python
   # Old
   from utils.logger import setup_logger
   import allure
   logger = setup_logger(__name__)

   # New
   from utils.allure_logger import get_allure_logger
   logger = get_allure_logger(__name__)
   ```

2. Replace `allure.step()` with `logger.step()`:
   ```python
   # Old
   with allure.step("Search for client"):

   # New
   with logger.step("Search for client"):
   ```

3. Replace attachments:
   ```python
   # Old
   allure.attach(text, name="Name", attachment_type=allure.attachment_type.TEXT)
   screenshot = page.screenshot()
   allure.attach(screenshot, name="Name", attachment_type=allure.attachment_type.PNG)

   # New
   logger.attach_text(text, "Name")
   logger.attach_screenshot(page, "Name")
   ```

### Phase 2: Update Page Objects

1. Replace logger initialization:
   ```python
   # Old
   logger = logging.getLogger(__name__)

   # New
   self.logger = get_allure_logger(self.__class__.__name__)
   ```

2. Add error logging:
   ```python
   try:
       element.click()
   except Exception as e:
       self.logger.error(f"Click failed: {str(e)}")  # Auto-attaches to Allure
       raise
   ```

### Phase 3: Update Utilities

Similar to Page Objects - replace logger and add strategic attachments.

---

## Real-World Example

### Before (account_steps.py - OLD)

```python
import allure
from playwright.sync_api import Page
from pytest_bdd import when
from utils.logger import setup_logger

logger = setup_logger(__name__)

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
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account List After Search",
            attachment_type=allure.attachment_type.PNG
        )
```

### After (account_steps.py - NEW)

```python
from playwright.sync_api import Page
from pytest_bdd import when
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context['test_data']['client_id']

    with logger.step(f"Search for client {client_id}"):
        logger.info(f"Searching for client: {client_id}")
        logger.attach_text(client_id, "Client ID")

        account_list_page.search_client(client_id)
        logger.attach_screenshot(page, "Account List After Search")
```

**Improvements:**
- 50% less code
- More readable
- Easier to maintain
- Consistent pattern

---

## Summary

### When to Use What

| Context | Use | Don't Use |
|---------|-----|-----------|
| **Test Steps** | `logger.step()` context manager | Raw `allure.step()` |
| **Page Objects** | `logger.info/error/warning()` | `logger.step()` or `allure.step()` |
| **Utilities** | `logger.info()` + `attach_json()` | `logger.step()` |
| **Fixtures** | `logger.step()` for setup/teardown | N/A |
| **Screenshots** | `logger.attach_screenshot()` | Manual `page.screenshot()` + `allure.attach()` |

### Key Principles

1. **Steps belong in tests, not pages**
2. **Pages log actions, don't create report structure**
3. **Errors/warnings auto-attach to Allure**
4. **Screenshots are easy: `logger.attach_screenshot(page, "Name")`**
5. **One logger per class: `get_allure_logger(self.__class__.__name__)`**

---

## Next Steps

1. Review [ALLURE_LOGGER_EXAMPLE.py](ALLURE_LOGGER_EXAMPLE.py) for step file examples
2. Review [ALLURE_LOGGER_PAGE_UTILITY_EXAMPLES.py](ALLURE_LOGGER_PAGE_UTILITY_EXAMPLES.py) for page/utility examples
3. Start migrating one step file as proof of concept
4. Gradually migrate remaining files

---

**Questions?** Review the example files or check the `AllureLogger` class docstrings.
