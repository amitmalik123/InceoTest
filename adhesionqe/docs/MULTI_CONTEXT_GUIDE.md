# Multiple Contexts and Pages Guide

## Overview

By default, pytest-playwright provides **one context and one page per test**. This guide explains when and how to use multiple contexts and pages.

---

## When to Use Multiple Pages (Same Context)

✅ **Use multiple pages when you need:**
- Multiple browser tabs in the **same session**
- Same cookies/authentication across tabs
- User opens links in new tabs
- Side-by-side comparison of pages
- Working with popups/windows

### Example Scenarios:
- Opening account details in a new tab while keeping the list open
- Comparing two reports side-by-side
- Handling popup windows (e.g., payment confirmation)
- Testing "Open in New Window" functionality

### Code Example:
```python
def test_multi_tab_workflow(page, new_page):
    # Main tab
    page.goto("/accounts")
    page.click("text=Account #12345")

    # Open details in new tab (same session)
    details_tab = new_page()
    details_tab.goto("/accounts/12345/details")

    # Both tabs share same session/cookies
    assert page.is_logged_in()
    assert details_tab.is_logged_in()
```

---

## When to Use Multiple Contexts (Different Sessions)

✅ **Use multiple contexts when you need:**
- **Different users** simultaneously
- **Isolated sessions** (no shared cookies)
- Different authentication states
- Cross-user permissions testing
- Concurrent operations testing

### Example Scenarios:
- Admin vs regular user permissions
- Two advisors editing the same account
- Logged-in vs logged-out state comparison
- Testing session conflicts
- Multi-tenant scenarios

### Code Example:
```python
def test_admin_vs_user(page, new_context):
    # Regular user (default context)
    page.goto("/login")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("button[type=submit]")

    # Admin user (new context = separate session)
    admin_context = new_context()
    admin_page = admin_context.new_page()
    admin_page.goto("/login")
    admin_page.fill("#username", "admin")
    admin_page.fill("#password", "admin_pass")
    admin_page.click("button[type=submit]")

    # Test different permissions
    assert not page.locator(".admin-panel").is_visible()
    assert admin_page.locator(".admin-panel").is_visible()
```

---

## Available Fixtures

### 1. `new_page` - Create Additional Pages

**Purpose**: Create multiple pages within the same context

**Returns**: Function that creates a new page

**Auto-cleanup**: Yes

```python
def test_example(page, new_page):
    # Main page
    page.goto("/dashboard")

    # Additional pages (same session)
    tab2 = new_page()
    tab2.goto("/reports")

    tab3 = new_page()
    tab3.goto("/settings")

    # All share same session
```

### 2. `new_context` - Create Additional Contexts

**Purpose**: Create multiple contexts (isolated sessions)

**Returns**: Function that creates a new context

**Auto-cleanup**: Yes

**Parameters**: Accepts any browser context options

```python
def test_example(page, new_context):
    # Default context
    page.goto("/dashboard")

    # New context with custom options
    mobile_context = new_context(
        viewport={'width': 375, 'height': 667},
        user_agent='Mobile Safari'
    )
    mobile_page = mobile_context.new_page()
    mobile_page.goto("/mobile-dashboard")

    # Isolated context (incognito)
    incognito_context = new_context()
    incognito_page = incognito_context.new_page()
    incognito_page.goto("/login")
```

### 3. `multi_user_contexts` - Pre-configured User Contexts

**Purpose**: Quick setup for admin and user testing

**Returns**: Dict with 'admin' and 'user' contexts

**Auto-cleanup**: Yes

```python
def test_example(multi_user_contexts):
    admin_page = multi_user_contexts['admin'].new_page()
    user_page = multi_user_contexts['user'].new_page()

    # Login both
    # ... login logic ...

    # Test different experiences
    admin_page.goto("/admin-panel")
    user_page.goto("/user-dashboard")
```

---

## Decision Tree

```
Do you need multiple browser instances?
├─ NO → Are they the same user/session?
│       ├─ YES → Use `new_page` (multiple tabs, same session)
│       └─ NO → Use `new_context` (multiple sessions, isolated)
└─ YES → Use multiple test runs or parallel execution
```

### Quick Decision Guide:

| Scenario | Use This | Why |
|----------|----------|-----|
| Open link in new tab | `new_page` | Same session, multiple tabs |
| Compare two pages side-by-side | `new_page` | Same user viewing both |
| Popup window | `new_page` | Part of same workflow |
| Admin vs User | `new_context` | Different permissions |
| Two different users | `new_context` | Isolated sessions |
| Incognito mode | `new_context` | No shared cookies |
| Concurrent edits | `new_context` | Test race conditions |
| Session isolation test | `new_context` | Verify no cross-talk |

---

## Architecture Comparison

### Current Simple Structure (Single Context)
```
Test
└── Browser (pytest-playwright)
    └── Context (default)
        └── Page (default)
            └── Your Page Objects
```

**Good for**: 90% of tests, simple workflows

### Enhanced Structure (Multiple Pages)
```
Test
└── Browser
    └── Context (default, shared session)
        ├── Page 1 (main tab)
        ├── Page 2 (second tab)
        └── Page 3 (popup)
```

**Good for**: Multi-tab workflows, same user

### Advanced Structure (Multiple Contexts)
```
Test
└── Browser
    ├── Context 1 (Admin session)
    │   └── Page 1
    ├── Context 2 (User session)
    │   └── Page 2
    └── Context 3 (Guest session)
        └── Page 3
```

**Good for**: Multi-user testing, permission testing

---

## Best Practices

### ✅ DO:
- Use single context/page for simple tests (90% of cases)
- Use `new_page` for multi-tab workflows with same user
- Use `new_context` for different users/sessions
- Clean up contexts explicitly if not using fixtures
- Document why you need multiple contexts in test docstring

### ❌ DON'T:
- Create multiple contexts when multiple pages would work
- Share sensitive data between contexts (they're isolated)
- Forget that contexts are isolated (no cookie sharing)
- Over-complicate simple tests with multiple contexts
- Use multiple contexts for parallelization (use pytest-xdist instead)

---

## Performance Considerations

### Resource Usage:
- **Page**: ~5-10 MB RAM
- **Context**: ~50-100 MB RAM (includes isolated storage)
- **Browser**: ~200-500 MB RAM (shared across all contexts)

### Tips:
1. Reuse contexts when possible (session scope)
2. Use `new_page` instead of `new_context` when session sharing is OK
3. Close contexts/pages explicitly in long-running tests
4. Consider pytest-xdist for true parallelization instead of multiple contexts

---

## Real-World Examples for Your Framework

### Example 1: Advisor Opens Account in New Tab
```python
def test_advisor_opens_account_in_new_tab(page, new_page, login_page, account_list_page):
    """Advisor keeps list open while viewing account details in new tab"""

    # Login and navigate to account list
    login_page.navigate()
    login_page.login("advisor@test.com", "password")

    account_list_page.navigate()
    account_list_page.search_account("12345")

    # Open account in new tab
    account_details_tab = new_page()
    account_details_tab.goto("/account/12345/details")

    # Verify both tabs work
    assert account_list_page.is_account_visible("12345")
    assert "Account 12345" in account_details_tab.title()
```

### Example 2: Test Admin vs Regular User Permissions
```python
def test_admin_sees_delete_button_user_doesnt(page, new_context, login_page):
    """Verify admin permissions vs regular user"""

    # Regular user
    login_page.navigate()
    login_page.login("user@test.com", "password")
    page.goto("/accounts")
    user_sees_delete = page.locator("button:has-text('Delete')").is_visible()

    # Admin user (separate session)
    admin_context = new_context()
    admin_page = admin_context.new_page()
    admin_login = LoginPage(admin_page)
    admin_login.navigate()
    admin_login.login("admin@test.com", "admin_password")
    admin_page.goto("/accounts")
    admin_sees_delete = admin_page.locator("button:has-text('Delete')").is_visible()

    # Verify permissions
    assert user_sees_delete is False
    assert admin_sees_delete is True
```

### Example 3: Test Concurrent Account Modifications
```python
def test_concurrent_account_edits(new_context):
    """Test two advisors editing same account simultaneously"""

    # Advisor 1
    advisor1_context = new_context()
    advisor1_page = advisor1_context.new_page()
    advisor1_page.goto("/login")
    # ... login ...
    advisor1_page.goto("/account/12345/edit")

    # Advisor 2 (separate session)
    advisor2_context = new_context()
    advisor2_page = advisor2_context.new_page()
    advisor2_page.goto("/login")
    # ... login ...
    advisor2_page.goto("/account/12345/edit")

    # Both try to save - test conflict resolution
    advisor1_page.fill("#amount", "1000")
    advisor2_page.fill("#amount", "2000")

    advisor1_page.click("button:has-text('Save')")
    advisor2_page.click("button:has-text('Save')")

    # Verify conflict handling
    assert advisor2_page.locator(".conflict-warning").is_visible()
```

---

## Migration Guide

### If you have existing tests:

**Before (simple):**
```python
def test_simple(page, login_page):
    login_page.navigate()
    login_page.login("user", "pass")
    # ... test ...
```

**After (with multiple tabs):**
```python
def test_with_tabs(page, new_page, login_page):
    # Main tab
    login_page.navigate()
    login_page.login("user", "pass")

    # Additional tab
    reports_tab = new_page()
    reports_tab.goto("/reports")
```

**After (with multiple users):**
```python
def test_multi_user(page, new_context, login_page):
    # User 1
    login_page.navigate()
    login_page.login("user1", "pass")

    # User 2 (separate session)
    user2_context = new_context()
    user2_page = user2_context.new_page()
    user2_login = LoginPage(user2_page)
    user2_login.navigate()
    user2_login.login("user2", "pass")
```

---

## Summary

Your framework now supports:
- ✅ **Single page/context** (default, 90% of tests)
- ✅ **Multiple pages** (same session, multi-tab workflows)
- ✅ **Multiple contexts** (different sessions, multi-user testing)
- ✅ **Pre-configured contexts** (quick admin/user setup)

Choose based on your needs:
- **Simple test**: Use default `page`
- **Multi-tab**: Use `new_page`
- **Multi-user**: Use `new_context`
- **Admin vs User**: Use `multi_user_contexts`
