# Test Tag and Marker Guide

## Quick Command Reference

### Run by Marker
```powershell
pytest -m smoke              # Smoke tests
pytest -m regression         # Regression tests
pytest -m roth_conversion    # Roth conversion tests
pytest -m critical           # Critical tests
pytest -m e2e                # End-to-end tests
pytest -m slow               # Slow tests
```

### Run by Environment
```powershell
pytest -m test11             # Test11 environment
pytest -m test12             # Test12 environment
pytest -m silo               # Silo environment
pytest -m prod               # Production environment
```

### Combine Markers
```powershell
pytest -m "smoke and critical"           # Both smoke AND critical
pytest -m "regression and not slow"      # Regression but NOT slow
pytest -m "roth_conversion or account"   # Either marker
pytest -m "(smoke or critical) and not slow"  # Complex expression
```

### By Environment + Marker
```powershell
$env:TEST_ENV = "test11"; pytest -m "smoke and test11"
$env:TEST_ENV = "test12"; pytest -m regression
```

## Available Markers

| Marker | Description |
|--------|-------------|
| `smoke` | Quick smoke tests for critical functionality |
| `regression` | Full regression test suite |
| `roth_conversion` | Roth IRA conversion related tests |
| `login` | Login functionality tests |
| `navigation` | Navigation and menu tests |
| `account` | Account management tests |
| `wizard` | Account wizard flow tests |
| `conversion` | Asset conversion tests |
| `tracking` | Tracking center tests |
| `e2e` | End-to-end workflow tests |
| `critical` | Critical path tests |
| `slow` | Tests that take longer to execute |
| `test11` | Test11 environment |
| `test12` | Test12 environment |
| `silo` | Silo environment |
| `prod` | Production environment |

## Feature File Tags

Tags in feature files become pytest markers automatically:

```gherkin
@e2e @roth_conversion @critical
Feature: Roth IRA Conversion Flow

  @smoke @regression @conversion
  Scenario: Successfully complete Roth IRA conversion
```

## Add Markers to Python Tests

```python
import pytest

@pytest.mark.smoke
@pytest.mark.login
def test_login():
    pass

@pytest.mark.regression
@pytest.mark.account
@pytest.mark.slow
def test_full_account_search():
    pass
```

## Useful Commands

```powershell
# List all markers
pytest --markers

# See which tests would run (dry-run)
pytest -m smoke --collect-only

# Run specific file with markers
pytest tests/ui/test_roth_conversion_cucumber.py -m smoke -v

# Generate report with specific markers
pytest -m smoke --html=reports/smoke.html --alluredir=reports/allure-smoke

# Run tests matching keyword
pytest -k "roth" -v
pytest -k "conversion or login" -v
```

## CI/CD Examples

```yaml
# Smoke tests
- name: Smoke Tests
  run: pytest -m smoke -v

# Regression on specific environment
- name: Regression Test12
  env:
    TEST_ENV: test12
  run: pytest -m regression -v

# Critical tests on all environments
- name: Critical Tests
  run: |
    $env:TEST_ENV = "test11"; pytest -m critical
    $env:TEST_ENV = "test12"; pytest -m critical
```

## Best Practices

1. Tag all scenarios with appropriate markers
2. Use multiple tags for better filtering
3. Separate smoke/regression in CI
4. Environment-specific markers added automatically
5. Use `--collect-only` to verify marker selection
