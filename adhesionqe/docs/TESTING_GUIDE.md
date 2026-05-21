# Run Tests with Reporting

## Prerequisites
- Install Allure command-line tool:
  - Windows: `scoop install allure` or download from https://github.com/allure-framework/allure2/releases
  - Mac: `brew install allure`
  - Linux: Download and extract from releases page

## Running Tests

### Basic Test Run (with all reports)
```bash
pytest
```

### Run with specific options
```bash
# Run in headless mode
pytest --browser chromium

# Run with headed browser
pytest --headed

# Run with slow motion (for debugging)
pytest --slowmo=500

# Run specific test
pytest src/testScript/test_roth_conversion_flow.py

# Run with markers
pytest -m smoke
pytest -m regression
```

## Reports Generated

### 1. **Pytest HTML Report**
- Location: `reports/pytest_report.html`
- Open directly in browser
- Contains test results, logs, and screenshots on failure

### 2. **Allure Report**
- Raw results: `reports/allure-results/`
- Generate and view report:
```bash
# Generate Allure report
allure serve reports/allure-results

# Or generate static report
allure generate reports/allure-results -o reports/allure-report --clean
```

### 3. **Video Recordings**
- Location: `test-results/` folder
- Videos are recorded for all tests (configurable in pyproject.toml)
- Change `--video=on` to `--video=retain-on-failure` to save only on failures

### 4. **Screenshots**
- Location: `test-results/` folder
- Screenshots taken on test actions and failures
- Attached to both HTML and Allure reports

## Test Data
- Test data is environment-specific and stored in: `data/test_data.<env>.csv` (for example `data/test_data.test11.csv`).
  Use the `TEST_ENV` environment variable and `utils.settings.settings.test_data_csv` to resolve the current CSV path.
- Edit CSV file to change test credentials, account IDs, amounts, etc.

## Configuration
All test configurations are in `pyproject.toml`:
- Browser settings
- Video/screenshot options
- Report locations
- Logging levels
- Timeouts

## Example: Complete Test Run with Reports
```bash
# 1. Run tests
pytest -v --headed

# 2. View HTML report
start reports/pytest_report.html

# 3. View Allure report
allure serve reports/allure-results
```

## CI/CD Integration
For CI/CD pipelines, use headless mode and save artifacts:
```bash
pytest --browser chromium --video=retain-on-failure
```
Then collect artifacts from:
- `reports/pytest_report.html`
- `reports/allure-results/`
- `test-results/` (videos/screenshots)
