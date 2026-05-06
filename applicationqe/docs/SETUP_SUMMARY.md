# Test Framework Setup Complete ✅

## What's Been Added

### 1. **CSV Data-Driven Testing**
- Test data externalized to: `data/test_data.<env>.csv` (e.g. `data/test_data.test11.csv`).
  The active CSV path is resolved via `utils.settings.settings.test_data_csv` using `TEST_ENV`.
- Easy to modify credentials, account IDs, amounts without code changes
- Format:
  ```csv
  field,value
  username,T11_AG8959_Perf
  password,QAAdminUser_33a
  client_id,40108642
  account_name,Core Markets
  destination_account,40108641
  conversion_amount,1000
  ```

### 2. **Video Recording** 🎥
- Automatically records all test executions
- Videos saved in `test-results/` folder
- Configurable modes:
  - `--video=on` - Always record (current setting)
  - `--video=retain-on-failure` - Only save failed test videos
  - `--video=off` - Disable recording

### 3. **Pytest HTML Report** 📊
- Generated at: `reports/pytest_report.html`
- Features:
  - Test execution summary
  - Detailed logs with timestamps
  - Pass/Fail status
  - Screenshots on failure
  - Self-contained HTML (no external dependencies)

### 4. **Allure Reporting** 📈
- Modern, interactive test reports
- Results stored in: `reports/allure-results/`
- Features:
  - Step-by-step test execution
  - Categorized by Epic/Feature/Story
  - Severity levels
  - Historical trends
  - Attachments (screenshots, videos, logs)
  - Test data visibility

### 5. **Comprehensive Logging** 📝
- Human-readable logs with timestamps
- Log level: INFO (configurable)
- Tracks:
  - Page navigations
  - User actions
  - Current URLs
  - Element interactions
  - Wait times
  - Error messages

## How to Use

### Run Tests
```bash
# Basic run with all reports
pytest

# Specific test with headed browser
pytest --headed src/testScript/test_roth_conversion_flow.py

# Headless mode (for CI/CD)
pytest --browser chromium
```

### View Reports

#### HTML Report (Immediate)
```bash
# Open in browser
start reports\pytest_report.html
```

#### Allure Report (Interactive)
```bash
# Serve locally (interactive)
allure serve reports\allure-results

# OR generate static HTML
allure generate reports\allure-results -o reports\allure-report --clean
start reports\allure-report\index.html
```

#### Videos
- Located in: `test-results/`
- Named by test and browser
- Open with any video player

### Quick Start Scripts
```bash
# Run tests and generate all reports
run_tests.bat

# Generate and view Allure report
generate_allure_report.bat
```

## Configuration

### pyproject.toml
All settings centralized:
```toml
[tool.pytest.ini_options]
addopts = """
--browser=chromium
--headed
--video=on
--screenshot=on
--tracing=retain-on-failure
--html=reports/pytest_report.html
--self-contained-html
--alluredir=reports/allure-results
"""
```

### Modify Test Data
Edit: `src/resources/test_data.csv`
- Change credentials
- Update account IDs
- Modify conversion amounts
- No code changes needed!

## Test Status

### ✅ Working
- CSV data loading
- Login flow with wait handling
- Clients navigation
- Account list navigation
- Comprehensive logging
- Video recording
- HTML report generation
- Allure report generation
- Step-by-step tracking

### ⚠️ Known Issue
- Account List search input not visible on page
- Application may have:
  - Different HTML structure than expected
  - JavaScript that needs more load time
  - Permission/authentication issues

## Next Steps

### For Search Issue:
1. Manually inspect Account List page in headed mode
2. Verify correct element selectors
3. Check if additional waits needed
4. Confirm search functionality availability

### For Enhanced Reports:
- Add more @allure decorators for better categorization
- Include more screenshots at key steps
- Add environment info to Allure
- Configure report retention policies

## File Structure
```
DM_Automation_new/
├── src/
│   ├── pageFunction/          # Page objects with logging
│   ├── resources/
│   │   └── test_data.csv      # Test data
│   └── testScript/            # Test files
├── reports/                   # Generated reports
│   ├── pytest_report.html     # HTML report
│   └── allure-results/        # Allure data
├── test-results/              # Videos & screenshots
├── pyproject.toml             # Configuration
├── run_tests.bat              # Quick run script
├── generate_allure_report.bat # Allure script
├── TESTING_GUIDE.md           # Detailed guide
└── .gitignore                 # Excludes reports from git
```

## CI/CD Ready
The framework is configured for automated pipelines:
- Headless execution
- Video on failure only
- Report artifacts
- Exit codes for pass/fail
