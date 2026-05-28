# Debugging Guide

> **Troubleshooting and Debugging Billing SGM Test Failures**

---

## Table of Contents

1. [Quick Diagnostics Checklist](#quick-diagnostics-checklist)
2. [Understanding Test Output](#understanding-test-output)
3. [Common Failures and Fixes](#common-failures-and-fixes)
4. [Using Headed Mode](#using-headed-mode)
5. [Reading Failure Screenshots](#reading-failure-screenshots)
6. [Reading the Log File](#reading-the-log-file)
7. [Debugging Imports and Collection Errors](#debugging-imports-and-collection-errors)
8. [Debugging BDD Step Matching](#debugging-bdd-step-matching)
9. [Debugging Playwright Timeouts](#debugging-playwright-timeouts)
10. [Debugging CSV / Data Issues](#debugging-csv--data-issues)

---

## Quick Diagnostics Checklist

Before deep-diving into a failure:

```
☐ tests/runners/ collected without errors?  →  pytest tests/runners/ --collect-only -q
☐ Credentials configured?                  →  Check env.qa.local.yaml or env vars
☐ App URL reachable?                        →  curl https://app-billing-ui-test.azurewebsites.net/
☐ CSV has data rows?                        →  Open the relevant *_data.csv and verify
☐ __pycache__ stale?                        →  Delete all __pycache__ dirs and retry
☐ Running from billingqe/ root?             →  cd billingqe before running pytest
```

---

## Understanding Test Output

Each BDD scenario produces structured log output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENARIO START : Create Model Family with valid data
  Feature      : Create Model Family
━━━ ...
  ▸ STEP: Given the user is logged into the application
  ✓ PASS: Given the user is logged into the application
  ▸ STEP: When the user fills in the family form ...
  ✗ FAIL: When the user fills in the family form ... — TimeoutError: ...
  📸 Failure screenshot: reports/.../FAIL_Create_Model_..._20260527_092314.png
```

| Symbol | Meaning |
|--------|--------|
| `▸ STEP` | Step is about to execute |
| `✓ PASS` | Step completed successfully |
| `✗ FAIL` | Step raised an exception |
| `📸` | Failure screenshot captured |

---

## Common Failures and Fixes

### `FileNotFoundError: search_family.feature`

```
FileNotFoundError: No such file or directory: '...search_family.feature'
```

**Cause:** `FEATURE_DIR` in the runner resolves to the wrong location (often `applicationqe` from stale bytecode).  
**Fix:**
```bash
# Delete all Python caches under billingqe
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
pytest tests/runners/ --collect-only
```

---

### `ValueError: Missing credentials`

```
ValueError: Missing credentials. Set BILLING_USERNAME and BILLING_PASSWORD env vars
```

**Fix:** Create `env.qa.local.yaml` with credentials, or set env vars:
```bash
export BILLING_USERNAME=user@company.com
export BILLING_PASSWORD=secret
```

---

### `StepDefinitionNotFoundError`

```
pytest_bdd.exceptions.StepDefinitionNotFoundError: Step definition is not found: ...
```

**Cause:** The Gherkin step text does not match any decorated function.  
**Fix:**
1. Check for typos between feature file and step file
2. Confirm the step module is imported in `tests/conftest.py`
3. Confirm `sys.path` includes the SGM step directory

---

### `PluginValidationError` for BDD hooks

```
plugy._manager.PluginValidationError: ... hookimpl definition: ... argument 'X' not in hookspec
```

**Cause:** Hook function has a renamed/extra parameter not in the pytest-bdd hookspec.  
**Fix:** Hook signatures in `fixtures/hooks_fixtures.py` must exactly match:
```python
def pytest_bdd_before_scenario(request, feature, scenario): ...
def pytest_bdd_before_step(request, feature, scenario, step, step_func): ...
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception): ...
```

---

### `TimeoutError` on login or form element

```
playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded.
```

**Fix options:**
1. Run in **headed mode** to watch the browser: `pytest --headed`
2. Check network connectivity to the app URL
3. Verify Azure AD login isn't blocked by MFA or IP restriction
4. Increase timeout in the relevant page object method
5. Check for modal dialogs blocking the UI (inspect screenshot)

---

### `AssertionError` with multiple soft assertion failures

```
AssertionError: 3 soft assertion(s) failed:
  - Family name not visible in results
  - Status column missing
  - Filter button disabled
```

**Cause:** `soft_assert.assert_all()` is called at fixture teardown collecting all accumulated failures.  
**Fix:** Review each bullet — each represents a separate verification failure in the page object method.

---

## Using Headed Mode

For interactive debugging, run the browser in headed mode:

```bash
pytest tests/runners/.../test_create_family_bdd_runner.py --headed -s
```

`--headed` launches Chromium visibly with `slow_mo=200` (200 ms between actions). Combined with `-s` (no output capture), you can watch every action and read console output.

To pause execution at a specific point, insert in a step or page object:
```python
self.page.pause()   # Opens Playwright Inspector
```

---

## Reading Failure Screenshots

Screenshots are saved automatically on step failure:

```
reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots/
FAIL_Create_Model_Family_w_When_the_user_fills_in_20260527_092314.png
```

Naming format: `FAIL_<scenario_name_40chars>_<step_name_30chars>_<YYYYMMDD_HHMMSS>.png`

Open the PNG to see the exact browser state when the failure occurred. Common things to look for:
- Unexpected modal / dialog blocking interaction
- Dropdown not populated (missing prerequisite data)
- Login page — session not established
- Error toast or validation message visible

---

## Reading the Log File

The DEBUG log file at `reports/.../pytest.log` contains the full trace including page object logs:

```bash
# Tail the log during a run
Get-Content reports/billing/platformrevenuedashboard/strategistgroupmodel/pytest.log -Wait -Tail 50

# Search for a specific failure
Select-String -Path reports/.../pytest.log -Pattern "FAIL|ERROR|TimeoutError"
```

Log format:
```
2026-05-27 09:24:30 [    INFO] ━━━ SCENARIO START : Search Family...
2026-05-27 09:24:30 [    INFO]   ▸ STEP: Given the user is logged into the application
2026-05-27 09:24:32 [    INFO] Navigating to: https://app-billing-ui-test...
2026-05-27 09:24:33 [    INFO] Navigation completed. Current URL: https://...
```

---

## Debugging Imports and Collection Errors

```bash
# Verbose collection with full traceback
pytest tests/runners/ --collect-only --tb=long

# Check what sys.path looks like at test time
pytest tests/runners/ --collect-only -s 2>&1 | Select-String "sys.path"

# Confirm conftest is loaded
pytest tests/runners/ --co -v 2>&1 | Select-String "conftest"
```

If tests are unexpectedly loading from `applicationqe`:
1. Ensure you are in `billingqe/` directory when running pytest
2. Delete all `__pycache__` directories
3. Confirm `pytest.ini` has `pythonpath = .`
4. Confirm `tests/conftest.py` removes `applicationqe` from `sys.path`

---

## Debugging BDD Step Matching

To see what steps pytest-bdd discovers:

```bash
pytest tests/runners/.../test_create_family_bdd_runner.py --bdd-generate --collect-only
```

To manually verify a step string matches, compare the exact text (including spaces and punctuation) between:
- The Gherkin step in the `.feature` file
- The string argument in the `@when("...")` decorator in the step file

Note: `Given`, `When`, `Then`, `And`, `But` are interchangeable keywords in pytest-bdd — only the string content matters for matching.

---

## Debugging Playwright Timeouts

For hard-to-reproduce timing issues:

```python
# In the page object, add explicit waits before the failing action
self.page.wait_for_load_state("networkidle", timeout=15000)
self.page.wait_for_timeout(500)  # Brief pause for animations
```

Use Playwright Trace Viewer for visual step-by-step replay:

```bash
# Enable tracing in browser_fixtures.py (or conftest)
context.tracing.start(screenshots=True, snapshots=True)
# ... run test ...
context.tracing.stop(path="trace.zip")

# View trace
playwright show-trace trace.zip
```

---

*Last updated: May 2026*
