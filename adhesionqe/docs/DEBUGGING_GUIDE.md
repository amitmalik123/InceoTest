# Pytest-Playwright Debugging Guide

## ✅ SOLVED: Event Loop Conflict

### Problem
`RuntimeError: Cannot run the event loop while another loop is running`

This occurred when both `pytest-playwright` and `pytest-asyncio` tried to manage the asyncio event loop simultaneously.

### Solution
**Convert all tests and page objects to use Playwright's SYNC API instead of async.**

### Root Cause (Historical)
- pytest-playwright's `page` fixture creates and manages an event loop
- pytest-asyncio also tries to create/manage an event loop
- These two plugins had an **unsolvable conflict** when using async API
- Solution: Use sync API to avoid event loops entirely

### Working Configuration

**Versions:**
- pytest: 8.4.2 (< 9.0.0)
- pytest-playwright: 0.4.4
- playwright: 1.57.0
- pytest-asyncio: 0.21.1 (optional, not used with sync API)

**pyproject.toml configuration:**
```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"  # Prevents interference with sync tests
```

**Test structure (SYNC API - NO async/await):**
```python
from playwright.sync_api import Page

def test_example(page: Page):
    page.goto("https://example.com")
    assert page.title() == "Example Domain"
```

### Debugging Commands

1. **Check installed plugins:**
```bash
python -m pip list | findstr /I "pytest"
```

2. **Verify pytest loads plugins correctly:**
```bash
pytest --trace-config | Select-String "plugin"
```

3. **Run with maximum verbosity:**
```bash
pytest -vvv --tb=long --capture=no test_file.py
```

4. **Test with simple example first** before running complex tests

### Common Pitfalls

❌ **Don't use:**
- Async API (`playwright.async_api`) with pytest-playwright
- `async def` / `await` in tests or page objects
- `@pytest.mark.asyncio` decorators
- Class-based tests with autouse async fixtures

✅ **Do use:**
- Sync API (`playwright.sync_api`) for all tests and page objects
- Regular `def` functions (not `async def`)
- Function-level tests
- Exact version pins for compatibility

### If Tests Still Fail

1. Create minimal test file:
```python
# test_minimal.py
import pytest

async def test_page_loads(page):
    await page.goto("https://playwright.dev")
    print(await page.title())
```

2. Run it:
```bash
pytest -vv test_minimal.py
```

3. If minimal test passes, issue is in your test code (not setup)
4. If minimal test fails, reinstall dependencies:
```bash
python -m pip uninstall -y pytest pytest-playwright pytest-asyncio playwright
python -m pip install pytest==8.4.2 pytest-playwright==0.4.4 pytest-asyncio==0.21.1 playwright
python -m playwright install
```
