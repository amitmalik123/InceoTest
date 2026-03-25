# Cross-Browser Testing - Quick Reference

## 🎯 Command Cheat Sheet

### Local Execution

```bash
# Single Browser
pytest --browser=chromium              # Chromium (default)
pytest --browser=msedge                # Microsoft Edge

# Cross-Browser
pytest --browser chromium --browser msedge

# With Parallel Workers
pytest --browser chromium --browser msedge -n 2

# Headed Mode (Visual)
pytest --browser=msedge --headed --slowmo=500

# Specific Test File
pytest tests/ui/test_add_ach.py --browser=msedge
```

### CI/CD Execution

**Pipeline Parameters:**
- Browser: `chromium` | `msedge` | `both`
- Workers: `1` | `2` | `4` | `auto`
- Marker: `add_ach` | `roth_conversion` | `all_tests`

**Result:** Tests run on selected browser(s) with parallel execution

---

## 📦 Browser Installation

```bash
# Local
npx playwright install chromium         # Chromium only
npx playwright install msedge           # Edge only
npx playwright install chromium msedge  # Both browsers

# CI/CD (Automatic)
# Handled by pipeline based on browser parameter
```

---

## 🔍 How Tests Are Named

When using cross-browser testing, tests are parametrized:

**Single Browser:**
```
test_add_ach.py::test_add_ach_instruction PASSED
```

**Cross-Browser:**
```
test_add_ach.py::test_add_ach_instruction[chromium] PASSED
test_add_ach.py::test_add_ach_instruction[msedge] PASSED
```

Each browser run is tracked separately in reports (Allure, JUnit, InfluxDB).

---

## 📊 Reporting & Tracking

### Allure Reports
- Filter by parameter: `browser_name=chromium` or `browser_name=msedge`
- Compare pass rates between browsers
- View browser-specific screenshots/traces

### InfluxDB Metrics
```flux
# Filter flaky tests by browser
from(bucket: "AutomationData")
  |> filter(fn: (r) => r._measurement == "flaky_tests")
  |> filter(fn: (r) => r.test_name =~ /\[msedge\]/)
```

### Grafana Dashboard
- Create browser comparison panels
- Track Edge vs Chromium pass rates
- Monitor browser-specific failures

---

## ⚙️ Configuration Files

### pyproject.toml
```toml
# Browser NOT hardcoded - pass at runtime
addopts = """
-v
--video=on
--screenshot=on
"""
```

### FormsAndTracking.yaml
```yaml
# Browser parameter with dropdown
parameters:
  - name: browser
    displayName: "Browser to Test"
    values:
      - chromium  # Default
      - msedge    # Edge only
      - both      # Cross-browser
```

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| "Browser not found" | Run `npx playwright install msedge` |
| Tests run twice on same browser | Check `--browser` passed only once |
| Slow cross-browser tests | Add `-n auto` for parallel execution |
| Edge failure in CI/CD | Check pipeline logs for installation errors |

---

## 🚀 Best Practices

1. **Development:** Use `--browser=chromium` for fast feedback
2. **Pre-merge:** Run cross-browser tests (`both`)
3. **CI/CD:** Default to `chromium`, use `both` for regression
4. **Debugging:** Use `--headed --slowmo=500` with specific browser
5. **Parallel:** Combine browsers + workers for speed

---

## 📝 Example Workflow

### Development Phase
```bash
# Quick local test
pytest tests/ui/test_add_ach.py --browser=chromium -v
```

### Before Commit
```bash
# Cross-browser validation
pytest tests/ui/ --browser chromium --browser msedge -n 2 -v
```

### CI/CD Pipeline
```
Trigger: Manual run
Parameters:
  - Environment: test11
  - Marker: all_tests
  - Workers: 4
  - Browser: both  ← Cross-browser testing
```

### After Failure
```bash
# Debug Edge-specific issue
pytest tests/ui/test_failing.py --browser=msedge --headed --slowmo=500
```

---

## 🎭 Supported Browsers

| Browser | Flag | Engine | Status |
|---------|------|--------|--------|
| Chromium | `chromium` | Blink/V8 | ✅ Supported |
| Microsoft Edge | `msedge` | Blink/V8 | ✅ Supported |

**Note:** Both use Chromium engine. For WebKit/Firefox support, see Playwright docs.

---

**Quick Help:**
- 📖 Full Guide: [CROSS_BROWSER_TESTING_GUIDE.md](CROSS_BROWSER_TESTING_GUIDE.md)
- 🔧 Framework Guide: [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)
- 🐛 Debugging: [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)
