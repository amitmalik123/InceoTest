# Automatic BDD Step Screenshots

## Overview
The framework automatically captures and attaches screenshots to Allure reports for each BDD step using pytest-bdd hooks. No manual code changes required in your step definitions.

## How It Works

### pytest-bdd Hooks
Three hooks in [tests/conftest.py](tests/conftest.py) automatically wrap BDD steps:

1. **`pytest_bdd_before_step`** - Creates an Allure step context BEFORE each step executes
2. **`pytest_bdd_after_step`** - Takes screenshot and closes the step context AFTER execution
3. **`pytest_bdd_step_error`** - Captures failure screenshot when a step fails

### Configuration Priority

The framework reads screenshot settings in this order (highest to lowest priority):

1. **CLI argument**: `pytest --screenshot-each-step`
2. **Environment variable**: `SCREENSHOT_EACH_STEP=true`
3. **Config file**: `config/env.{environment}.yaml`

### Enabling Screenshots

#### Option 1: Config File (Recommended)
Edit your environment config file (e.g., [config/env.test11.yaml](../config/env.test11.yaml)):

```yaml
# Test settings
test:
  screenshot_on_failure: true
  screenshot_each_step: true  # Set to true to enable
  video: "on"
  trace: "retain-on-failure"
```

Then run tests normally:
```bash
pytest tests/bdd/
```

#### Option 2: Environment Variable (Temporary Override)
```bash
# Windows PowerShell
$env:SCREENSHOT_EACH_STEP="true"
pytest tests/bdd/

# Linux/Mac
export SCREENSHOT_EACH_STEP=true
pytest tests/bdd/
```

#### Option 3: CLI Argument
```bash
pytest --screenshot-each-step tests/bdd/
```

### Configuration Files

Screenshot settings are available in all environment configs:
- [config/env.test11.yaml](../config/env.test11.yaml)
- [config/env.test12.yaml](../config/env.test12.yaml)
- [config/env.qa.yaml](../config/env.qa.yaml)
- [config/env.silo.yaml](../config/env.silo.yaml)
- [config/env.prod.yaml](../config/env.prod.yaml)

**Note**: For production environments, keep `screenshot_each_step: false` to avoid performance impact and large report sizes.

## Features

### Automatic Step Wrapping
- Every BDD step (Given/When/Then/And) is automatically wrapped in an `allure.step()` context
- All logs and actions within the step appear nested under that step in the Allure report
- No need to manually add `with_logger_step()` or `allure.step()` decorators

### Screenshot Capture
- Screenshots taken AFTER each step completes (showing the result)
- Attached inside the step context (not at test level)
- Named "Screenshot" in the Allure report
- PNG format, typically 80-100KB per screenshot

### Failure Screenshots
- Automatically captured when a step fails
- Named "FAILED Screenshot" for easy identification
- Exception propagated normally after screenshot capture

## Example Output

### Allure Report Structure
```
Test: test_successfully_complete_add_ach_flow
├── When I navigate to Clients menu
│   ├── Info (text logs)
│   └── Screenshot (image/png)  ← Automatic
├── And I click on Account List
│   ├── Info (text logs)
│   └── Screenshot (image/png)  ← Automatic
└── Then I should see Account Details
    ├── Info (text logs)
    └── Screenshot (image/png)  ← Automatic
```

### Before vs After

**Before (without hooks):**
```
Test: test_add_ach
├── Info log 1
├── Info log 2
├── Info log 3
└── Info log 4
```
All logs at test level, hard to find specific step actions.

**After (with hooks):**
```
Test: test_add_ach
├── When I navigate to Clients menu
│   ├── Info: Navigating to clients menu
│   ├── Info: ClientsPage navigate - Current URL
│   ├── Info: Clicking Clients link
│   └── Screenshot
├── And I click on Account List
│   ├── Info: Clicking Account List
│   ├── Info: Account List link clicked
│   └── Screenshot
```
Clear step separation, easy navigation, visual confirmation at each step.

## Implementation Details

### Fixture Access
The hooks use `request.getfixturevalue("page")` to access the Playwright page object:

```python
# Get page object from pytest request fixture
page = None
try:
    page = request.getfixturevalue("page")
except Exception:
    # Fallback to funcargs if needed
    if hasattr(request, "node") and hasattr(request.node, "funcargs"):
        page = request.node.funcargs.get("page")
```

### Step Context Management
A global dictionary tracks active step contexts:

```python
_active_allure_steps = {}

# In before_step:
step_key = f"{id(request.node)}_{step.name}"
allure_step_context = allure.step(step_name)
allure_step_context.__enter__()
_active_allure_steps[step_key] = allure_step_context

# In after_step:
allure_step_context = _active_allure_steps.pop(step_key)
allure_step_context.__exit__(None, None, None)
```

## Verification

### Check PNG Files Created
```powershell
Get-ChildItem reports/allure-results/ -Filter *.png | Measure-Object -Property Length -Sum
```

### Check Allure JSON Attachments
```powershell
Get-Content reports/allure-results/*-result.json | ConvertFrom-Json |
  Select-Object -ExpandProperty steps |
  Select-Object name, @{N='Attachments';E={$_.attachments | Select-Object name, type}}
```

Should show `type: "image/png"` for screenshot attachments.

## Benefits

1. **Zero Code Changes** - Works automatically for all existing BDD tests
2. **Clear Test Organization** - Steps clearly separated in reports
3. **Visual Verification** - Screenshot at each step shows actual UI state
4. **Easy Debugging** - Quickly identify which step failed and see the state
5. **Consistent Reporting** - All tests follow same structure

## Performance Impact

- Screenshot capture adds ~0.5-1 second per step
- PNG files are ~80-100KB each
- For a 10-step test with screenshots enabled: ~15-20 seconds total
- Recommended for debugging and smoke tests, disable for large regression suites

## Troubleshooting

### Screenshots Not Appearing
1. Check environment variable is set: `echo $env:SCREENSHOT_EACH_STEP`
2. Verify page fixture is available in test
3. Check allure-results directory for PNG files
4. Review test output for any screenshot errors

### Unicode/Encoding Errors
All emojis have been removed from print statements to prevent Windows cp1252 encoding issues.

### Step Context Not Closing
If `_active_allure_steps` grows without bound, check for exceptions in step execution that prevent `after_step` hook from running.

## Related Documentation

- [ALLURE_LOGGER_GUIDE.md](ALLURE_LOGGER_GUIDE.md) - Manual allure logging and steps
- [BDD_GUIDE.md](BDD_GUIDE.md) - BDD framework overview
- [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) - Debugging strategies
