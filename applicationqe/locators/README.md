# Locators Package

This package centralizes all locator definitions for page objects.
Each module in this package corresponds to a page object and contains all locators for that page.

## Structure

Each locator module (e.g., login_locators.py) contains:

1. Locators as constants (for static selectors):
   ```python
   STATUS_LABEL = "span:has-text('Status:') + label"
   NOTES_GRID_TABLE = "table#TrackingCenterItemDetailNotesGrid"
   ```

2. Locator initialization functions (for dynamic Playwright locators):
   ```python
   def initialize_locators(page: Page) -> Dict[str, Locator]:
       return {
           "username_field": page.get_by_label("Username"),
           "password_field": page.get_by_label("Password"),
       }
   ```

## Usage Patterns

### Pattern 1: Using Module Constants
```python
from locators import item_detail_locators

status_locator_string = item_detail_locators.STATUS_LABEL
status_element = page.locator(item_detail_locators.STATUS_LABEL)
```

### Pattern 2: Using Initialization Functions
```python
from locators import login_locators

locators = login_locators.initialize_locators(page)
username_field = locators["username_input_field"]
password_field = locators["password_input_field"]
```

## Page Files Usage

Each page object imports and uses locators from its corresponding locator module:

```python
from locators import login_locators

class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = login_locators.initialize_locators(page)
        self.username_input = locators["username_input_field"]
        self.password_input = locators["password_input_field"]
```

## Current Locator Modules

✓ item_detail_locators.py        - Tracking Center Item Detail page locators
✓ clients_locators.py            - Clients page locators
✓ login_locators.py              - Login page locators
✓ account_list_locators.py       - Account List page locators
✓ docusign_locators.py           - DocuSign page locators
✓ account_wizard_locators.py     - Account Wizard page locators

## Adding New Locators

When adding locators for a new page:

1. Create a new file: `locators/{page_name}_locators.py`

2. Add locator definitions:
   ```python
   # For static selectors
   ELEMENT_NAME = "css-selector-or-xpath"
   
   # For dynamic Playwright locators
   def initialize_locators(page: Page) -> Dict[str, Locator]:
       return {
           "element_name": page.get_by_role(...),
       }
   ```

3. Update `locators/__init__.py` to export the new module

4. Update the corresponding page file to import and use the locators

5. Remove locator definitions from the page file (move to locators file)

## Benefits

✓ Centralized locator management - Easy to find and update selectors
✓ Separation of concerns - Page logic separated from locator definitions
✓ Reusability - Locators can be used in multiple places
✓ Maintainability - Changes to selectors affect all usages
✓ Consistency - Standard pattern across all pages
✓ Scalability - Easy to manage as project grows
