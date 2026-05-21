# Environment Configuration Guide

## Available Environments

The framework supports multiple environments with specific URLs:

| Environment | Config File | Base URL | Login URL |
|------------|-------------|----------|-----------|
| **Test11** (Default) | `env.test11.yaml` | https://test11.ewealthmanager.com/ | https://test11.ewealthmanager.com/ewmLogin/account/login |
| **Test12** | `env.test12.yaml` | https://test12.ewealthmanager.com/ | https://test12.ewealthmanager.com/ewmLogin/account/login |
| **Silo** | `env.silo.yaml` | https://silo.ewealthmanager.com/ | https://silo.ewealthmanager.com/ewmLogin/account/login |
| **Prod** | `env.prod.yaml` | https://wrmqa.schwabplan.com/ | https://wrmqa.schwabplan.com/ewmLogin/account/login |
| **QA** | `env.qa.yaml` | https://wrmqa.schwabplan.com/ | (QA environment) |

## How to Use Different Environments

### Method 1: Set Environment Variable (Recommended)

```bash
# Windows PowerShell
$env:TEST_ENV = "test11"
pytest tests/ui/test_roth_conversion_cucumber.py -v

$env:TEST_ENV = "test12"
pytest tests/ui/test_roth_conversion_cucumber.py -v

$env:TEST_ENV = "silo"
pytest tests/ui/test_roth_conversion_cucumber.py -v

$env:TEST_ENV = "prod"
pytest tests/ui/test_roth_conversion_cucumber.py -v
```

```bash
# Windows CMD
set TEST_ENV=test11
pytest tests/ui/test_roth_conversion_cucumber.py -v

set TEST_ENV=test12
pytest tests/ui/test_roth_conversion_cucumber.py -v
```

```bash
# Linux/Mac
export TEST_ENV=test11
pytest tests/ui/test_roth_conversion_cucumber.py -v
```

### Method 2: Modify conftest.py

Update `tests/conftest.py` to read from environment variable:

```python
import os
from utils.settings import Settings

# Get environment from environment variable or use default
env = os.getenv('TEST_ENV', 'test11')
settings = Settings(env=env)
```

### Method 3: Direct Import in Test Files

For ad-hoc testing in specific files:

```python
from utils.settings import Settings

# Use specific environment
settings = Settings(env='test12')
login_page.navigate(settings.login_url)
```

### Method 4: Pytest Custom Option

Add to `conftest.py`:

```python
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="test11",
        help="Environment to run tests: test11, test12, silo, prod"
    )

@pytest.fixture(scope="session")
def environment(request):
    return request.config.getoption("--env")
```

Then run:
```bash
pytest --env=test11 tests/ui/ -v
pytest --env=test12 tests/ui/ -v
pytest --env=silo tests/ui/ -v
pytest --env=prod tests/ui/ -v
```

## Configuration File Structure

Each environment file (`config/env.{environment}.yaml`) contains:

```yaml
environment: test11

application:
  base_url: "https://test11.ewealthmanager.com/"
  login_url: "https://test11.ewealthmanager.com/ewmLogin/account/login"
  timeout: 30000

browser:
  browser_type: "chromium"
  headless: false
  viewport:
    width: 1280
    height: 720

test:
  screenshot_on_failure: true
  video: "on"
  trace: "retain-on-failure"

reporting:
  allure_results: "reports/allure-results"
  html_report: "reports/pytest_report.html"

data:
  test_data_csv: "data/test_data.<env>.csv"  # Example: data/test_data.test11.csv
```

## Accessing Configuration in Code

```python
from utils.settings import settings

# Access URLs
base_url = settings.base_url
login_url = settings.login_url

# Access browser settings
browser_type = settings.browser_type
headless = settings.headless

# Access test data
test_data_path = settings.test_data_csv

# Access timeouts
timeout = settings.timeout
```

## Environment-Specific Test Data

You can also create environment-specific test data files:

```
data/
├── test_data.<env>.csv     # Per-environment CSVs (e.g. test_data.test11.csv)
├── test_data.test11.csv    # Test11 specific
├── test_data.test12.csv    # Test12 specific
├── test_data.silo.csv      # Silo specific
└── test_data.prod.csv      # Prod specific
```

Update `env.{environment}.yaml`:
```yaml
data:
  test_data_csv: "data/test_data.test11.csv"
```

## Quick Environment Switching Examples

### Run same test on different environments:

```bash
# Test on Test11
$env:TEST_ENV = "test11"; pytest tests/ui/test_roth_conversion_cucumber.py -v

# Test on Test12
$env:TEST_ENV = "test12"; pytest tests/ui/test_roth_conversion_cucumber.py -v

# Test on Silo
$env:TEST_ENV = "silo"; pytest tests/ui/test_roth_conversion_cucumber.py -v

# Test on Prod (use carefully!)
$env:TEST_ENV = "prod"; pytest tests/ui/test_roth_conversion_cucumber.py -v
```

### Generate reports for specific environment:

```bash
$env:TEST_ENV = "test11"
pytest --alluredir=reports/allure-results-test11
allure serve reports/allure-results-test11
```

## Best Practices

1. **Default to Test11**: The framework defaults to test11 for development
2. **Use Environment Variables**: Set `TEST_ENV` for easy switching
3. **Prod Caution**: Always review tests before running on prod
4. **Separate Reports**: Use different report directories per environment
5. **Environment-Specific Data**: Create separate test data for each environment if needed
6. **CI/CD Integration**: Pass environment as parameter in CI/CD pipelines

## CI/CD Integration Example

```yaml
# GitHub Actions / Azure DevOps
- name: Run Tests on Test11
  run: |
    $env:TEST_ENV = "test11"
    pytest tests/ --alluredir=reports/test11

- name: Run Tests on Test12
  run: |
    $env:TEST_ENV = "test12"
    pytest tests/ --alluredir=reports/test12
```

## Troubleshooting

**Issue:** Environment file not found
```
FileNotFoundError: Configuration file not found: config/env.test11.yaml
```
**Solution:** Ensure the environment file exists in `config/` directory

**Issue:** Wrong URL being used
**Solution:** Verify `TEST_ENV` variable is set correctly and matches config filename

**Issue:** Settings not updating
**Solution:** Restart Python session or reimport settings module
