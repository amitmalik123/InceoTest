# Auto-Healing Test Automation - Complete Guide

## 📖 Table of Contents
- [What is Auto-Healing?](#what-is-auto-healing)
- [Implementation Architecture](#implementation-architecture)
- [How It Works](#how-it-works)
- [Execution Guide](#execution-guide)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

---

## 🎯 What is Auto-Healing?

Auto-healing is an intelligent feature that automatically fixes broken test selectors when web page structure changes. Instead of tests failing due to minor UI changes, the framework attempts to locate elements using alternative strategies.

### Common Scenarios Where Auto-Healing Helps

1. **ID/Class Changes**: Developer changes element IDs or classes
2. **Structure Refactoring**: Page HTML structure is reorganized
3. **Dynamic Content**: Elements are rendered dynamically with changing attributes
4. **Localization**: Text changes but functionality remains the same
5. **A/B Testing**: Different page variations with similar functionality

### Benefits

✅ **Reduced Maintenance**: Tests self-repair instead of breaking
✅ **Faster Feedback**: Tests continue running despite minor changes
✅ **Learning System**: Stores successful alternatives for future use
✅ **Detailed Reporting**: Know when and how healing occurred
✅ **Easy Integration**: Works with existing page objects

---

## 🏗️ Implementation Architecture

### Components

```
utils/
├── auto_healing.py          # Core healing engine and strategies
└── locator_storage.json     # Stores learned alternative selectors

pages/
└── auto_healing_page.py     # Enhanced base page with healing

tests/
└── examples/
    └── test_auto_healing_examples.py  # Example tests
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Test Script                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 AutoHealingPage                             │
│  (Enhanced page object with healing capabilities)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              AutoHealingEngine                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  1. Try original selector                        │      │
│  │  2. Check stored alternatives                    │      │
│  │  3. Try healing strategies:                      │      │
│  │     - TestIdStrategy                             │      │
│  │     - LabelStrategy                              │      │
│  │     - PlaceholderStrategy                        │      │
│  │     - RoleStrategy                               │      │
│  │     - TextContentStrategy                        │      │
│  │     - SimilarElementStrategy                     │      │
│  │  4. Store successful alternative                 │      │
│  └──────────────────────────────────────────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Locator Storage (JSON)                         │
│  Persistent storage of successful alternative selectors     │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ How It Works

### Healing Process Flow

1. **Initial Attempt**: Try the original selector
   ```python
   locator = page.locator("#login-button")
   ```

2. **Failure Detection**: Selector doesn't find element
   ```
   Element not found with original selector: #login-button
   ```

3. **Check Storage**: Look for previously successful alternative
   ```python
   stored_selector = storage.get("#login-button")
   # Returns: button[type='submit']:has-text('Login')
   ```

4. **Try Stored Alternative**: Use if available
   ```python
   locator = page.locator(stored_alternative)
   ```

5. **Healing Strategies**: If no stored alternative, try strategies in order:

   a. **TestIdStrategy** - Find by `data-testid` attribute
   ```python
   page.get_by_test_id("login-btn")
   ```

   b. **LabelStrategy** - Find by associated label
   ```python
   page.get_by_label("Username")
   ```

   c. **PlaceholderStrategy** - Find by placeholder text
   ```python
   page.get_by_placeholder("Enter username")
   ```

   d. **RoleStrategy** - Find by ARIA role
   ```python
   page.get_by_role("button", name="Login")
   ```

   e. **TextContentStrategy** - Find by visible text
   ```python
   page.get_by_text("Login", exact=False)
   ```

   f. **SimilarElementStrategy** - Find similar elements by tag
   ```python
   page.locator("button").first
   ```

6. **Store Success**: Save working alternative for future use
   ```json
   {
     "md5_hash": {
       "original": "#login-button",
       "selector": "button:has-text('Login')",
       "strategy": "text_content",
       "timestamp": 1702989234.567,
       "success_count": 1
     }
   }
   ```

7. **Return Locator**: Provide healed locator to test
   ```python
   return healed_locator, was_healed=True
   ```

### Healing Strategies Explained

#### 1. TestIdStrategy
**Priority**: Highest
**Use Case**: Best practice - elements with `data-testid` attributes

```html
<!-- Before -->
<button id="btn-123">Submit</button>

<!-- After (ID changed) -->
<button data-testid="submit-btn">Submit</button>
```

**Healing**: Finds by `data-testid="submit-btn"`

#### 2. LabelStrategy
**Priority**: High
**Use Case**: Form inputs with associated labels

```html
<!-- Before -->
<input id="user-input" name="username" />

<!-- After (ID changed) -->
<label for="username-field">Username</label>
<input id="username-field" name="user" />
```

**Healing**: Finds by label text "Username"

#### 3. PlaceholderStrategy
**Priority**: High
**Use Case**: Input fields with placeholder text

```html
<!-- Before -->
<input id="email-input" placeholder="Enter email" />

<!-- After (ID changed) -->
<input class="email-field" placeholder="Enter email" />
```

**Healing**: Finds by placeholder "Enter email"

#### 4. RoleStrategy
**Priority**: Medium
**Use Case**: Elements with ARIA roles

```html
<!-- Before -->
<button class="btn-primary">Submit</button>

<!-- After (class changed) -->
<button class="submit-btn" role="button">Submit</button>
```

**Healing**: Finds by role="button" and text "Submit"

#### 5. TextContentStrategy
**Priority**: Medium
**Use Case**: Elements with unique, stable text

```html
<!-- Before -->
<a class="nav-link" id="about">About Us</a>

<!-- After (class and ID changed) -->
<a class="menu-item" href="/about">About Us</a>
```

**Healing**: Finds by text "About Us"

#### 6. SimilarElementStrategy
**Priority**: Lowest
**Use Case**: Last resort - similar element structure

```html
<!-- Before -->
<button id="submit-btn">Submit</button>

<!-- After (attributes changed) -->
<button class="submit-button">Submit</button>
```

**Healing**: Finds first `<button>` element

---

## 🚀 Execution Guide

### Step 1: Basic Setup

```python
from playwright.sync_api import Page
from pages.auto_healing_page import AutoHealingPage

def test_login(page: Page):
    # Create auto-healing page
    healing_page = AutoHealingPage(page)

    # Use it like normal page object
    healing_page.navigate("https://yourapp.com/login")
    healing_page.fill("#username", "user@example.com")
    healing_page.click("#login-button")
```

### Step 2: Run Tests

```powershell
# Run with auto-healing enabled (default)
pytest tests/test_login.py -v

# Run example tests
pytest tests/examples/test_auto_healing_examples.py -v -s

# Run with detailed output
pytest tests/ -v -s --log-cli-level=INFO
```

### Step 3: View Healing Statistics

```python
def test_with_stats(page: Page):
    healing_page = AutoHealingPage(page)

    # ... perform test actions ...

    # Get statistics
    stats = healing_page.get_healing_stats()
    print(f"Healed {stats['successful_heals']} selectors")
    print(f"Success rate: {stats['success_rate']:.2%}")
```

### Step 4: Review Stored Alternatives

Check `locator_storage.json`:

```json
{
  "abc123def456": {
    "original": "#old-button-id",
    "selector": "button:has-text('Submit')",
    "strategy": "text_content",
    "timestamp": 1702989234.567,
    "success_count": 5
  }
}
```

---

## 💻 Usage Examples

### Example 1: Basic Auto-Healing

```python
from pages.auto_healing_page import AutoHealingPage

def test_basic_healing(page: Page):
    """Demonstrate basic auto-healing"""
    healing_page = AutoHealingPage(page)
    healing_page.navigate("https://example.com")

    # Even if selector changes, healing finds it
    healing_page.click("button#submit")  # Auto-heals if needed
```

### Example 2: Conditional Healing

```python
def test_conditional_healing(page: Page):
    """Enable/disable healing dynamically"""
    healing_page = AutoHealingPage(page, enable_healing=True)

    # Critical element - don't heal
    healing_page.click("#critical-button", heal=False)

    # Less critical - allow healing
    healing_page.click("#optional-button", heal=True)
```

### Example 3: Monitoring Healing Activity

```python
def test_monitor_healing(page: Page):
    """Track healing activity"""
    healing_page = AutoHealingPage(page)
    healing_page.navigate("https://example.com")

    # Reset stats
    healing_page.reset_healing_stats()

    # Perform actions
    healing_page.click("button#btn1")
    healing_page.fill("input#field1", "test")
    healing_page.click("a#link1")

    # Check what was healed
    stats = healing_page.get_healing_stats()

    if stats['total_heals'] > 0:
        print(f"⚠️  {stats['total_heals']} selectors required healing")
        print(f"✅ {stats['successful_heals']} were successfully healed")
        print(f"❌ {stats['failed_heals']} could not be healed")
```

### Example 4: Form Filling with Healing

```python
def test_form_with_healing(page: Page):
    """Fill form with auto-healing"""
    healing_page = AutoHealingPage(page)
    healing_page.navigate("https://example.com/form")

    # These will heal if selectors change
    healing_page.fill("input[name='email']", "user@example.com")
    healing_page.fill("input[name='password']", "password123")
    healing_page.check_checkbox("#terms")
    healing_page.click("button[type='submit']")

    # Verify (also with healing)
    assert healing_page.is_visible(".success-message")
```

### Example 5: Page Object Integration

```python
class LoginPage(AutoHealingPage):
    """Login page with auto-healing"""

    def __init__(self, page: Page):
        super().__init__(page, enable_healing=True)
        self.url = "https://example.com/login"

    def login(self, username: str, password: str):
        """Login with credentials"""
        self.navigate(self.url)
        self.fill("#username", username)  # Auto-heals
        self.fill("#password", password)  # Auto-heals
        self.click("#login-btn")          # Auto-heals

    def is_logged_in(self) -> bool:
        """Check if login successful"""
        return self.is_visible(".dashboard")  # Auto-heals

# Usage
def test_login_with_healing(page: Page):
    login_page = LoginPage(page)
    login_page.login("user@example.com", "password")
    assert login_page.is_logged_in()
```

### Example 6: Parallel Tests with Healing

```python
import pytest

@pytest.mark.parallel
def test_parallel_with_healing(page: Page):
    """Auto-healing works in parallel execution"""
    healing_page = AutoHealingPage(page)
    healing_page.navigate("https://example.com")

    # Each worker has independent healing engine
    healing_page.click("button")

    # Stats are per-worker
    stats = healing_page.get_healing_stats()
    print(f"Worker healed {stats['successful_heals']} selectors")
```

---

## ⚙️ Configuration

### Enable/Disable Healing

```python
# Enable healing (default)
healing_page = AutoHealingPage(page, enable_healing=True)

# Disable healing
healing_page = AutoHealingPage(page, enable_healing=False)

# Toggle at runtime
healing_page.disable_healing()
healing_page.enable_healing_feature()
```

### Custom Storage Location

```python
from utils.auto_healing import AutoHealingEngine

# Custom storage path
engine = AutoHealingEngine(storage_path="custom_locators.json")
```

### Per-Element Healing Control

```python
# Allow healing for this element
healing_page.click("#dynamic-button", heal=True)

# Don't heal this critical element
healing_page.click("#payment-submit", heal=False)
```

### Custom Timeouts

```python
# Find with custom timeout
element = healing_page.find_element("#slow-loading", timeout=10000)

# Click with custom timeout
healing_page.click("#button", timeout=5000)
```

---

## 📊 Monitoring & Reporting

### Get Healing Statistics

```python
stats = healing_page.get_healing_stats()

# Available metrics:
# - total_heals: Total healing attempts
# - successful_heals: Successful healing attempts
# - failed_heals: Failed healing attempts
# - success_rate: Percentage (0.0 to 1.0)
# - stored_alternatives: Number of stored alternatives
```

### Log Output Example

```
WARNING: Attempting to heal selector: #old-button-id
INFO: Found element using text_content: Submit
INFO: Successfully healed using text_content: button:has-text('Submit')
```

### Storage File Format

```json
{
  "hash_key": {
    "original": "#original-selector",
    "selector": "healed-selector",
    "strategy": "strategy_name",
    "timestamp": 1702989234.567,
    "success_count": 3
  }
}
```

---

## 🎓 Best Practices

### 1. Use Stable Selectors First

```python
# ✅ Good - uses data-testid
page.get_by_test_id("login-button")

# ⚠️ Acceptable - may need healing
page.locator("#btn-123")

# ❌ Avoid - very fragile
page.locator("div > div > button:nth-child(3)")
```

### 2. Don't Rely Only on Healing

Auto-healing is a safety net, not a replacement for good selectors:

```python
# Write tests with good selectors
# Let healing handle unexpected changes
```

### 3. Monitor Healing Activity

```python
@pytest.fixture(autouse=True)
def log_healing(page, request):
    """Log healing activity after each test"""
    yield

    if hasattr(request.node, 'healing_page'):
        stats = request.node.healing_page.get_healing_stats()
        if stats['total_heals'] > 0:
            print(f"\n⚠️ Test healed {stats['total_heals']} selectors")
```

### 4. Review and Update Selectors

```python
# Periodically review locator_storage.json
# Update test selectors to use successful alternatives
# This reduces healing overhead
```

### 5. Critical Elements = No Healing

```python
# For critical actions (payment, delete, etc.), disable healing
healing_page.click("#confirm-payment", heal=False)
```

### 6. Test Healing in CI/CD

```yaml
# In CI pipeline
- name: Run tests with healing
  run: pytest --log-file=healing.log

- name: Check healing activity
  run: |
    if grep -q "Successfully healed" healing.log; then
      echo "⚠️ Some selectors were healed - review needed"
    fi
```

### 7. Use Healing Statistics for Alerts

```python
def test_with_alert(page: Page):
    healing_page = AutoHealingPage(page)
    # ... test actions ...

    stats = healing_page.get_healing_stats()

    # Alert if too many heals
    if stats['success_rate'] < 0.5:
        pytest.fail("Too many healing failures - selectors need update")
```

---

## 🔧 Troubleshooting

### Issue: Healing Not Working

**Solution**: Check if healing is enabled
```python
healing_page = AutoHealingPage(page, enable_healing=True)
# Or
healing_page.enable_healing_feature()
```

### Issue: Wrong Element Found

**Solution**: Use more specific selectors or disable healing
```python
# Be more specific
healing_page.click("button.submit:has-text('Login')", heal=True)

# Or disable for this element
healing_page.click("button", heal=False)
```

### Issue: Slow Tests Due to Healing

**Solution**: Reduce timeouts or update selectors
```python
# Shorter timeout
healing_page.find_element("#btn", timeout=2000)

# Or update selector in test to stored alternative
```

### Issue: Storage File Getting Large

**Solution**: Clear old entries periodically
```python
from utils.auto_healing import AutoHealingEngine

engine = AutoHealingEngine()
engine.clear_storage()  # Clear all
```

---

## 📈 Advanced Usage

### Custom Healing Strategy

```python
from utils.auto_healing import HealingStrategy

class CustomStrategy(HealingStrategy):
    def __init__(self):
        super().__init__("custom")

    def find_element(self, page, original_selector):
        # Your custom logic
        return page.locator("custom-selector")

# Add to engine
engine.strategies.insert(0, CustomStrategy())  # High priority
```

### Conditional Healing Based on Environment

```python
import os

# Disable healing in production
enable_healing = os.getenv("ENV") != "production"
healing_page = AutoHealingPage(page, enable_healing=enable_healing)
```

### Integration with Existing Page Objects

```python
from pages.base_page import BasePage
from utils.auto_healing import AutoHealingEngine

class EnhancedBasePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.healing_engine = AutoHealingEngine()

    def click(self, selector: str, **kwargs):
        try:
            super().click(selector, **kwargs)
        except Exception:
            # Try healing
            healed, _ = self.healing_engine.find_element(self.page, selector)
            if healed:
                healed.click()
            else:
                raise
```

---

## 🎉 Summary

Auto-healing provides:
- ✅ **Resilient tests** that handle UI changes
- ✅ **Reduced maintenance** through automatic adaptation
- ✅ **Learning system** that improves over time
- ✅ **Detailed tracking** of healing activity
- ✅ **Easy integration** with existing tests

**Start using auto-healing today to make your tests more robust!**

```powershell
# Try the examples
pytest tests/examples/test_auto_healing_examples.py -v -s
```

See `tests/examples/test_auto_healing_examples.py` for complete examples.
