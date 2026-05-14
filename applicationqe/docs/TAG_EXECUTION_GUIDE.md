# Tag-Based Test Execution Guide

## Overview

Run specific tests based on tags/markers instead of executing entire feature files. This is the **practical approach** for:
- ✅ Quick smoke tests before commits
- ✅ Critical path validation before deployment
- ✅ Feature-specific testing during development
- ✅ Environment-specific test runs
- ✅ Selective regression testing

---

## Quick Start

### Command Line Execution

```bash
# Run ONLY smoke tests
pytest -m smoke

# Run ONLY critical tests
pytest -m critical

# Run ACH-specific tests
pytest -m add_ach

# Run regression suite
pytest -m regression
```

### VS Code Debug Mode

Press `F5` and select:
- **Debug Smoke Tests** - Run all smoke tests
- **Debug Critical Tests** - Run all critical tests
- **Debug ACH Tests** - Run ACH feature tests
- **Debug Regression Tests** - Run full regression suite

### PowerShell Scripts

```powershell
# Run smoke tests
.\run_smoke_tests.ps1

# Run critical tests
.\run_critical_tests.ps1

# Run ACH tests
.\run_ach_tests.ps1

# Run regression tests
.\run_regression_tests.ps1
```

---

## Available Tags/Markers

Your framework has these markers configured:

| Marker | Description | Use Case |
|--------|-------------|----------|
| `smoke` | Quick smoke tests | Before commit, daily sanity |
| `regression` | Full regression suite | Before deployment |
| `critical` | Critical path tests | Production validation |
| `e2e` | End-to-end workflows | Integration testing |
| `add_ach` | ACH feature tests | ACH development |
| `ach` | ACH functionality | ACH testing |
| `roth_conversion` | Roth IRA conversion | Roth feature |
| `login` | Login functionality | Auth testing |
| `navigation` | Navigation tests | Menu/routing |
| `account` | Account management | Account features |
| `wizard` | Account wizard flow | Wizard testing |
| `slow` | Tests that take long | Exclude for quick runs |
| `test11` | Test11 environment | Environment-specific |
| `test12` | Test12 environment | Environment-specific |
| `silo` | Silo environment | Environment-specific |
| `prod` | Production environment | Prod validation |
| `performance` | Performance monitoring | Performance testing |
| `skip_ci` | Skip in CI | CI exclusions |

---

## Feature File Tags

Your `add_ACH.feature` has:

```gherkin
@e2e @add_ach @critical
Feature: Add ACH E2E flow

  @smoke @regression @ach
  Scenario: Successfully complete Add ACH flow
```

This means the scenario has **ALL** these markers:
- From Feature level: `e2e`, `add_ach`, `critical`
- From Scenario level: `smoke`, `regression`, `ach`

You can run it using any of these markers!

---

## Practical Usage Examples

### 1. Before Code Commit (Fast - 1-2 minutes)

```bash
# Run smoke tests only
pytest -m smoke -v

# Run smoke tests (exclude slow ones)
pytest -m "smoke and not slow" -v
```

### 2. Before Pull Request (Medium - 5-10 minutes)

```bash
# Run smoke OR critical tests
pytest -m "smoke or critical" -v

# Run critical path tests
pytest -m critical -v
```

### 3. Before Deployment (Full - 20-30 minutes)

```bash
# Run full regression suite
pytest -m regression -v

# Run regression with parallel execution
pytest -m regression -n 4 -v
```

### 4. Feature Development (ACH)

```bash
# Run only ACH tests in headed mode
pytest -m add_ach --headed --slowmo=500 -v

# Run ACH smoke tests
pytest -m "add_ach and smoke" -v
```

### 5. Environment-Specific Testing

```bash
# Run tests for test11 environment
pytest -m test11 -v

# Run test11 smoke tests
TEST_ENV=test11 pytest -m "test11 and smoke" -v

# Run production validation tests
TEST_ENV=prod pytest -m "prod and critical" -v
```

### 6. Nightly Regression (Automated)

```bash
# Run regression excluding slow tests
pytest -m "regression and not slow" -n 4 -v

# Run e2e tests for all environments
pytest -m e2e -v
```

---

## Combining Markers (Boolean Logic)

### OR - Run tests with either marker

```bash
# Run tests marked as smoke OR critical
pytest -m "smoke or critical"

# Run ACH OR Roth conversion tests
pytest -m "add_ach or roth_conversion"
```

### AND - Run tests with both markers

```bash
# Run tests that are BOTH smoke AND critical
pytest -m "smoke and critical"

# Run ACH tests that are also regression tests
pytest -m "add_ach and regression"
```

### NOT - Exclude tests with marker

```bash
# Run all tests EXCEPT slow ones
pytest -m "not slow"

# Run smoke tests but exclude CI-skip tests
pytest -m "smoke and not skip_ci"
```

### Complex Expressions

```bash
# Run tests that are:
# - Either smoke OR critical
# - AND not slow
# - AND for test11 environment
pytest -m "(smoke or critical) and not slow and test11"

# Run e2e tests that are critical but not slow
pytest -m "e2e and critical and not slow"
```

---

## Running Specific Files with Markers

```bash
# Run smoke tests from specific file
pytest tests/ui/test_add_ach.py -m smoke

# Run ACH and regression tests from file
pytest tests/ui/test_add_ach.py -m "ach and regression"

# Run all BDD tests with smoke marker
pytest tests/bdd/ -m smoke

# Run specific file, specific marker, debug mode
pytest tests/ui/test_add_ach.py -m smoke --headed --slowmo=1000 -v
```

---

## Debug Mode with Markers

### VS Code Launch Configurations

Press **F5** and select from dropdown:

1. **Debug Smoke Tests**
   - Runs: `pytest -m smoke`
   - Use: Quick validation during development

2. **Debug Critical Tests**
   - Runs: `pytest -m critical`
   - Use: Validate critical paths

3. **Debug ACH Tests**
   - Runs: `pytest -m add_ach`
   - Use: ACH feature development

4. **Debug Regression Tests**
   - Runs: `pytest -m regression`
   - Use: Full regression validation

5. **Debug E2E Tests**
   - Runs: `pytest -m e2e`
   - Use: End-to-end workflow validation

6. **Debug Current Test File**
   - Runs: Current file only
   - Use: Debug specific test file

### Custom Debug Configuration

Add to [.vscode/launch.json](.vscode/launch.json):

```json
{
  "name": "Debug Custom Marker",
  "type": "debugpy",
  "request": "launch",
  "module": "pytest",
  "args": [
    "-m", "your_marker_here",
    "-v",
    "-s",
    "--headed",
    "--browser=chromium"
  ],
  "console": "integratedTerminal",
  "justMyCode": false
}
```

---

## PowerShell Runner Scripts

### Quick Runners

Created for you:

| Script | Command | Use Case |
|--------|---------|----------|
| [run_smoke_tests.ps1](run_smoke_tests.ps1) | `pytest -m smoke` | Quick validation |
| [run_critical_tests.ps1](run_critical_tests.ps1) | `pytest -m critical` | Critical path |
| [run_ach_tests.ps1](run_ach_tests.ps1) | `pytest -m add_ach` | ACH development |
| [run_regression_tests.ps1](run_regression_tests.ps1) | `pytest -m regression` | Full regression |

### Usage:

```powershell
# Execute smoke tests
.\run_smoke_tests.ps1

# Execute with PowerShell
powershell -File run_smoke_tests.ps1
```

### Create Custom Runners

```powershell
# run_my_custom_tests.ps1
pytest -m "your_marker" -v --html=reports/custom_report.html
```

---

## Viewing Available Markers

### List All Markers

```bash
# See all registered markers
pytest --markers
```

Output:
```
@pytest.mark.smoke: Quick smoke tests for critical functionality
@pytest.mark.regression: Full regression test suite
@pytest.mark.add_ach: Add ACH instructions related tests
...
```

### See Which Tests Match Marker (Dry Run)

```bash
# See what tests would run with smoke marker
pytest -m smoke --collect-only

# See what tests would run with complex expression
pytest -m "smoke and not slow" --collect-only
```

---

## Adding Tags to Feature Files

### Feature-Level Tags (Apply to ALL scenarios)

```gherkin
@e2e @critical
Feature: My Feature

  Scenario: Test 1
    # Inherits: @e2e @critical

  Scenario: Test 2
    # Inherits: @e2e @critical
```

### Scenario-Level Tags (Apply to specific scenario)

```gherkin
Feature: My Feature

  @smoke @regression
  Scenario: Important test
    # Has: @smoke @regression

  @slow
  Scenario: Time-consuming test
    # Has: @slow
```

### Combining Both

```gherkin
@e2e @critical
Feature: My Feature

  @smoke @regression
  Scenario: Test 1
    # Has: @e2e @critical @smoke @regression

  @slow
  Scenario: Test 2
    # Has: @e2e @critical @slow
```

---

## Best Practices

### ✅ DO:
- Use `smoke` for quick validation (1-5 minutes)
- Use `critical` for must-pass tests
- Use `regression` for comprehensive testing
- Use `slow` to mark time-consuming tests
- Combine markers for flexibility: `@smoke @regression @ach`
- Run `smoke` tests before commits
- Run `critical` tests before deployments
- Use `-m "not slow"` for quick iterations

### ❌ DON'T:
- Over-tag tests (keep it meaningful)
- Forget to register markers in `pyproject.toml`
- Run full suite when developing (use specific markers)
- Skip smoke tests before committing
- Use inconsistent marker names

---

## Common Workflows

### Developer Daily Workflow

```bash
# Morning: Run smoke tests
pytest -m smoke

# During development: Run feature-specific tests
pytest -m add_ach --headed

# Before commit: Run smoke + critical
pytest -m "smoke or critical"

# Before push: Run regression
pytest -m regression
```

### CI/CD Pipeline

```yaml
# .gitlab-ci.yml or similar

stages:
  - smoke
  - regression
  - performance

smoke_tests:
  script:
    - pytest -m "smoke and not skip_ci" -v

regression_tests:
  script:
    - pytest -m "regression and not skip_ci" -n 4 -v

performance_tests:
  script:
    - pytest -m performance -v
```

### Release Validation

```bash
# 1. Smoke test (2 min)
pytest -m smoke -v

# 2. Critical path (5 min)
pytest -m critical -v

# 3. Full regression (20 min)
pytest -m regression -v

# 4. Performance test (10 min)
pytest -m performance -v
```

---

## Troubleshooting

### Marker Not Found

**Error**: `'marker_name' not a registered marker`

**Fix**: Add to `pyproject.toml`:

```toml
markers = [
    "your_marker: Description of your marker",
]
```

### No Tests Collected

**Error**: `collected 0 items`

**Reasons**:
1. Tag doesn't exist in feature files
2. Marker expression has typo
3. Tests don't match marker

**Debug**:
```bash
# See what would be collected
pytest -m your_marker --collect-only -v
```

### Wrong Tests Running

**Issue**: Different tests run than expected

**Check**:
1. Feature file tags are correct
2. Marker expression syntax is correct
3. Use `--collect-only` to verify

---

## Summary

### What You Can Do Now:

✅ Run tests by tags: `pytest -m smoke`
✅ Combine markers: `pytest -m "smoke or critical"`
✅ Exclude tests: `pytest -m "regression and not slow"`
✅ Debug by tags: Use VS Code launch configurations
✅ Quick runners: Execute PowerShell scripts
✅ Environment-specific: `pytest -m test11`

### Key Commands:

| Goal | Command |
|------|---------|
| Quick validation | `pytest -m smoke` |
| Before deployment | `pytest -m critical` |
| Full regression | `pytest -m regression` |
| Feature testing | `pytest -m add_ach` |
| Fast iteration | `pytest -m "smoke and not slow"` |
| Environment | `pytest -m test11` |
| Debug | Press F5 → Select marker |

### Files Created:

- ✅ [run_smoke_tests.ps1](run_smoke_tests.ps1)
- ✅ [run_critical_tests.ps1](run_critical_tests.ps1)
- ✅ [run_ach_tests.ps1](run_ach_tests.ps1)
- ✅ [run_regression_tests.ps1](run_regression_tests.ps1)
- ✅ [.vscode/launch.json](.vscode/launch.json) - Updated with marker configs
- ✅ [run_by_tags_examples.sh](run_by_tags_examples.sh) - Example commands

**This is the practical approach!** 🎯
