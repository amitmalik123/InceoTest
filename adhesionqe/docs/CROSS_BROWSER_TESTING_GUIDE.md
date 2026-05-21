# Cross-Browser Testing Guide

## Overview

The framework now supports **cross-browser testing** with multiple browsers:
- **Chromium** (default)
- **Microsoft Edge** (Chromium-based)
- **Both** (run tests on both browsers)

Tests will be executed on the selected browser(s), providing comprehensive browser compatibility coverage.

---

## 🎯 Quick Start

### Local Execution

#### Test on Chromium (Default)
```bash
pytest tests/ui/test_add_ach.py --browser=chromium
```

#### Test on Microsoft Edge
```bash
pytest tests/ui/test_add_ach.py --browser=msedge
```

#### Test on Both Browsers
```bash
pytest tests/ui/test_add_ach.py --browser=chromium --browser=msedge
```

#### Test with Headed Mode
```bash
pytest tests/ui/test_add_ach.py --browser=msedge --headed --slowmo=500
```

---

## 🔧 CI/CD Configuration

### Azure Pipeline Parameters

When running the pipeline manually, select the browser from the dropdown:

**Parameter:** `browser`

**Options:**
- `chromium` - Run tests on Chromium only (default)
- `msedge` - Run tests on Microsoft Edge only
- `both` - Run tests on both browsers sequentially

**Example:**
```yaml
# Manual pipeline run configuration
Environment: test11
Marker: add_ach
Workers: 2
Browser: both  # ← Select browser here
```

### Pipeline Behavior

**Browser Selection Logic:**
```bash
# Single browser (Chromium)
pytest tests/ui/ --browser chromium -n 2

# Single browser (Edge)
pytest tests/ui/ --browser msedge -n 2

# Both browsers (cross-browser testing)
pytest tests/ui/ --browser chromium --browser msedge -n 2
```

**Browser Installation:**
- `chromium` → Installs Chromium only
- `msedge` → Installs Microsoft Edge only
- `both` → Installs both browsers

---

## 📊 How It Works

### 1. Browser Parameter

The `--browser` flag accepts multiple values:

```python
# pytest-playwright automatically parametrizes tests across browsers
@pytest.mark.parametrize("browser_name", ["chromium", "msedge"])
def test_example(browser_name):
    # Test runs once per browser
    pass
```

When you pass `--browser chromium --browser msedge`, pytest-playwright:
1. Parametrizes each test with both browser engines
2. Runs the test suite twice (once per browser)
3. Reports results separately for each browser

### 2. Browser Context

The framework uses Playwright's browser context for isolation:

```python
# conftest.py already configured
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }
```

Each browser run gets:
- ✅ Isolated cookies and session storage
- ✅ Separate video recordings
- ✅ Independent traces and screenshots
- ✅ Parallel execution support

### 3. Parallel Execution with Cross-Browser

**Combine browsers + parallel workers:**

```bash
# 2 workers × 2 browsers = 4 concurrent test executions
pytest tests/ui/ --browser chromium --browser msedge -n 2 --dist loadscope
```

**Distribution Strategy:**
- `loadscope` - Groups tests by scenario/class
- Each browser runs independently
- Workers are shared across browser executions

---

## 🎭 Browser-Specific Configuration

### Install Browsers Locally

```bash
# Install Chromium only
npx playwright install chromium

# Install Microsoft Edge only
npx playwright install msedge

# Install both browsers
npx playwright install chromium msedge

# Install all browsers (includes Firefox, WebKit)
npx playwright install
```

### Browser Capabilities

| Browser   | Engine    | JavaScript | CSS Grid | Web Components | Download Speed |
|-----------|-----------|------------|----------|----------------|----------------|
| Chromium  | Blink     | V8         | ✅       | ✅             | Fast           |
| Edge      | Blink     | V8         | ✅       | ✅             | Fast           |

**Note:** Both browsers use the same engine (Chromium/Blink), so results should be nearly identical. Cross-browser testing with Edge validates:
- Browser-specific rendering differences
- Edge-specific extensions/features
- Corporate environment compatibility

---

## 📈 Reporting

### Allure Reports

Tests executed on different browsers are **tagged separately** in Allure:

```json
{
  "name": "test_add_ach_instruction[chromium]",
  "parameters": [
    {
      "name": "browser_name",
      "value": "chromium"
    }
  ]
}
```

**View results per browser:**
- Filter by parameter: `browser_name=chromium`
- Compare pass rates between browsers
- Identify browser-specific failures

### JUnit XML Reports

Browser information is included in test names:

```xml
<testcase name="test_add_ach_instruction[chromium]" classname="tests.ui.test_add_ach"/>
<testcase name="test_add_ach_instruction[msedge]" classname="tests.ui.test_add_ach"/>
```

### InfluxDB Metrics

Browser tag is automatically captured:

```python
# Flaky test tracker includes browser
tracker.record_flaky_test(
    test_name=item.nodeid,  # Includes [chromium] or [msedge]
    # ...
)
```

**Grafana Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "flaky_tests")
  |> filter(fn: (r) => r.test_name =~ /\[chromium\]/)
```

---

## 🧪 Example Test Execution

### Local Testing

```bash
# Single browser, single test
pytest tests/ui/test_add_ach.py::test_add_ach_instruction --browser=msedge -v

# Cross-browser, all tests in directory
pytest tests/ui/ --browser chromium --browser msedge -v

# Cross-browser + parallel + headed
pytest tests/ui/test_add_ach.py \
  --browser chromium \
  --browser msedge \
  -n 2 \
  --headed \
  --slowmo=300
```

### CI/CD Testing

**Trigger Pipeline:**
1. Go to Azure DevOps → Pipelines
2. Click "Run pipeline"
3. Select parameters:
   - Environment: `test11`
   - Marker: `add_ach`
   - Workers: `2`
   - **Browser: `both`** ← Cross-browser testing

**Expected Output:**
```
Installing both Chromium and Edge...
✓ Chromium installed
✓ Microsoft Edge installed

Running tests with marker: add_ach
Cross-browser testing: Chromium and Microsoft Edge
Parallel execution enabled: 2 workers

pytest -m "add_ach" \
  --browser chromium \
  --browser msedge \
  -n 2 \
  --dist loadscope

test_add_ach.py::test_add_ach_instruction[chromium] PASSED
test_add_ach.py::test_add_ach_instruction[msedge] PASSED
```

---

## 🔍 Debugging Cross-Browser Issues

### Browser-Specific Failures

If a test fails on one browser but not the other:

1. **Check browser console logs:**
   ```python
   page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}"))
   ```

2. **Compare screenshots:**
   - `test-results/screenshots/chromium/`
   - `test-results/screenshots/msedge/`

3. **Review traces:**
   - Open trace viewer: `npx playwright show-trace trace.zip`
   - Compare browser-specific network activity

4. **Check Allure report:**
   - Filter by browser parameter
   - Compare execution times
   - Review attached artifacts

### Common Browser Differences

Even with the same engine, browsers can differ in:

| Aspect           | Potential Difference | Solution                        |
|------------------|----------------------|---------------------------------|
| User Agent       | Different strings    | Don't rely on UA sniffing      |
| Default Settings | Privacy/tracking     | Set explicit context options   |
| Extensions       | Edge has built-in    | Use clean context              |
| File Paths       | Download location    | Configure download behavior    |

---

## 🚀 Best Practices

### 1. Default to Chromium for Speed
```bash
# Fast feedback during development
pytest tests/ui/ --browser=chromium -n auto
```

### 2. Run Cross-Browser Before Merge
```bash
# Ensure compatibility before PR merge
pytest tests/ui/ --browser chromium --browser msedge -v
```

### 3. Use Headed Mode for Debugging
```bash
# Debug browser-specific issues visually
pytest tests/ui/test_failing.py --browser=msedge --headed --slowmo=500
```

### 4. Leverage Parallel Execution
```bash
# Maximize efficiency with both browsers and workers
pytest tests/ui/ --browser chromium --browser msedge -n 4 --dist loadscope
```

### 5. Tag Browser-Specific Tests
```python
@pytest.mark.msedge_only
def test_edge_specific_feature(page):
    """Test that only runs on Edge"""
    pass
```

Then run:
```bash
pytest -m msedge_only --browser=msedge
```

---

## 📝 Configuration Summary

### pyproject.toml
```toml
[tool.pytest.ini_options]
addopts = """
-v
--tb=short
--strict-markers
--disable-warnings
--video=on
--screenshot=on
--tracing=retain-on-failure
"""
# Note: --browser is NOT hardcoded, pass it at runtime
```

### azurePipeline.yaml
```yaml
parameters:
  - name: browser
    displayName: "Browser to Test"
    type: string
    default: "chromium"
    values:
      - chromium
      - msedge
      - both
```

### Local .bashrc / .zshrc (Optional)
```bash
# Alias for cross-browser testing
alias pytest-cross="pytest --browser chromium --browser msedge -v"
alias pytest-edge="pytest --browser msedge --headed --slowmo=500"
```

---

## 🆘 Troubleshooting

### Issue: "Browser executable not found"

**Solution:** Install the browser first
```bash
npx playwright install msedge
```

### Issue: "Tests run twice on same browser"

**Cause:** Browser parameter passed multiple times

**Fix:** Check command - only pass `--browser chromium` once
```bash
# ❌ Wrong
pytest --browser chromium --browser chromium

# ✅ Correct
pytest --browser chromium --browser msedge
```

### Issue: "Cross-browser tests are slow"

**Solution:** Enable parallel execution
```bash
pytest --browser chromium --browser msedge -n auto --dist loadscope
```

### Issue: "Edge-specific failure in CI/CD"

**Debug Steps:**
1. Check pipeline logs for browser installation
2. Verify Edge was actually used (check test name suffix)
3. Download test artifacts (screenshot, trace, video)
4. Run same test locally with `--browser=msedge --headed`

---

## 📚 Additional Resources

- [Playwright Browsers Documentation](https://playwright.dev/docs/browsers)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Cross-Browser Testing Best Practices](https://playwright.dev/docs/test-use-options#browser-options)

---

## ✅ Quick Reference

| Task                          | Command                                                    |
|-------------------------------|------------------------------------------------------------|
| Test on Chromium              | `pytest --browser=chromium`                               |
| Test on Edge                  | `pytest --browser=msedge`                                 |
| Cross-browser testing         | `pytest --browser chromium --browser msedge`              |
| Cross-browser + parallel      | `pytest --browser chromium --browser msedge -n 2`         |
| Install Edge browser          | `npx playwright install msedge`                           |
| Debug Edge visually           | `pytest --browser=msedge --headed --slowmo=500`           |
| CI/CD cross-browser           | Set pipeline parameter: `browser = both`                  |
| Filter Allure by browser      | `browser_name=chromium` or `browser_name=msedge`          |

---

**Happy Cross-Browser Testing! 🎭🚀**
