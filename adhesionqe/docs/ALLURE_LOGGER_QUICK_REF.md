# AllureLogger - Quick Reference

## Setup

```python
from utils.allure_logger import get_allure_logger
logger = get_allure_logger(__name__)
```

## Common Patterns

### Test Steps
```python
@when("I search for the client")
def search_for_client(page, account_list_page, test_context):
    client_id = test_context['test_data']['client_id']

    with logger.step(f"Search for client {client_id}"):
        logger.info(f"Searching for: {client_id}")
        logger.attach_text(client_id, "Client ID")
        account_list_page.search_client(client_id)
        logger.attach_screenshot(page, "After Search")
```

### Page Objects
```python
class AccountPage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_allure_logger(self.__class__.__name__)

    def search(self, client_id: str):
        self.logger.info(f"Searching for: {client_id}")
        try:
            self.search_input.fill(client_id)
            self.logger.info("Search successful")
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
```

### Utilities
```python
class APIClient:
    def __init__(self):
        self.logger = get_allure_logger(self.__class__.__name__)

    def create_account(self, data: dict):
        self.logger.info("Creating account")
        self.logger.attach_json(data, "Request")
        # ... API call ...
        self.logger.attach_json(response, "Response")
        return response
```

## API Cheat Sheet

### Logging
```python
logger.debug("msg")         # Console only
logger.info("msg")          # Console only
logger.warning("msg")       # Console + Allure ⚠️
logger.error("msg")         # Console + Allure ❌
logger.critical("msg")      # Console + Allure 🔥

# Force Allure attachment
logger.info("msg", attach_to_allure=True)
```

### Attachments
```python
logger.attach_text("text", "Name")
logger.attach_json({"key": "val"}, "Name")
logger.attach_screenshot(page, "Name")
logger.attach_html("<h1>Hi</h1>", "Name")
```

### Steps
```python
with logger.step("Step name"):
    # Actions here
```

## Do's and Don'ts

### ✅ DO
- Use `logger.step()` in test steps
- Use simple logging in pages
- Attach screenshots after important actions
- Use descriptive attachment names

### ❌ DON'T
- Don't use `allure.step()` in page objects
- Don't import `allure` in pages/utilities
- Don't nest steps too deeply
- Don't attach every log to Allure

## Migration Quick Tips

### Replace Imports
```python
# Old
from utils.logger import setup_logger
import allure
logger = setup_logger(__name__)

# New
from utils.allure_logger import get_allure_logger
logger = get_allure_logger(__name__)
```

### Replace Steps
```python
# Old
with allure.step("Do something"):

# New
with logger.step("Do something"):
```

### Replace Attachments
```python
# Old
allure.attach(text, name="X", attachment_type=allure.attachment_type.TEXT)
screenshot = page.screenshot()
allure.attach(screenshot, name="Y", attachment_type=allure.attachment_type.PNG)

# New
logger.attach_text(text, "X")
logger.attach_screenshot(page, "Y")
```

## Complete Example

```python
from playwright.sync_api import Page
from pytest_bdd import when, then
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

@when("I login")
def login(page: Page, login_page, test_context):
    username = test_context['username']

    with logger.step(f"Login as {username}"):
        logger.info(f"Logging in: {username}")
        logger.attach_text(username, "Username")

        login_page.enter_credentials(username, "password")
        logger.attach_screenshot(page, "Credentials Entered")

        login_page.click_submit()
        logger.attach_screenshot(page, "After Login")

@then("I should see the home page")
def verify_home_page(page: Page):
    with logger.step("Verify home page"):
        page.wait_for_load_state("domcontentloaded")
        logger.attach_screenshot(page, "Home Page")
        logger.info("Login successful")
```
