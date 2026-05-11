# Complete Start-to-End Execution Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Test Execution](#test-execution)
5. [Viewing Reports](#viewing-reports)
6. [Advanced Execution](#advanced-execution)
7. [CI/CD Execution](#cicd-execution)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Install Python (3.8 or higher)
```powershell
# Download from https://www.python.org/downloads/
# During installation:
☑️ Check "Add Python to PATH"
☑️ Check "Install pip"

# Verify installation
python --version  # Should show Python 3.8+
pip --version     # Should show pip version
```

### 2. Install Git
```powershell
# Download from https://git-scm.com/downloads
# Verify installation
git --version
```

### 3. Install Node.js (for Allure CLI - optional)
```powershell
# Download from https://nodejs.org/
# Verify installation
node --version
npm --version

# Install Allure CLI globally
npm install -g allure-commandline
allure --version
```

### 4. Install VS Code (recommended)
```powershell
# Download from https://code.visualstudio.com/
# Install Python extension (ms-python.python)
# Install Playwright Test extension (ms-playwright.playwright)
```

---

## Initial Setup

### Step 1: Clone Repository
```powershell
# Navigate to your workspace directory
cd C:\Users\YourName\vsCode-workspace

# Clone repository from Azure DevOps
git clone https://dev.azure.com/AssetmarkInc/Core/_git/DM1TestAutomation
cd DM1TestAutomation

# Verify files
dir  # Should see pyproject.toml, tests/, pages/, utils/, etc.
```

### Step 2: Create Virtual Environment
```powershell
# Create virtual environment (one-time setup)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
.\venv\Scripts\Activate.ps1

# Verify activation (prompt should show (venv))
# Example: (venv) PS C:\Users\...\DM1TestAutomation>
```

### Step 3: Install Dependencies
```powershell
# Make sure virtual environment is activated (you see (venv) in prompt)

# Install all dependencies (runtime + dev tools)
pip install -e .[dev]

# This installs:
# - Playwright, pytest, pytest-bdd, pytest-xdist
# - Allure reporting
# - Code quality tools (black, flake8, mypy, etc.)
# - Database, API testing libraries
# - All dependencies from pyproject.toml

# Verify installation
pip list  # Should show all installed packages
```

### Step 4: Install Playwright Browsers
```powershell
# Install Chromium, Firefox, WebKit browsers
playwright install

# Install only Chromium (faster, recommended for CI)
playwright install chromium

# This downloads browser binaries (~300MB)
# Location: %USERPROFILE%\AppData\Local\ms-playwright
```

### Step 5: Verify Installation
```powershell
# Check Playwright version
playwright --version

# Check pytest version
pytest --version

# Check if all dependencies installed correctly
python -c "import playwright; import pytest; import allure; print('✓ All imports successful')"
```

---

## Environment Configuration

### Step 1: Select Environment
```powershell
# Available environments:
# - test11 (default)
# - test12
# - silo
# - qa
# - prod

# Set environment variable (Windows PowerShell)
$env:TEST_ENV = "test11"

# Verify environment
echo $env:TEST_ENV
```

### Step 2: Configure Test Data
```powershell
# Environment configs are in config/ folder:
# - config/env.test11.yaml
# - config/env.test12.yaml
# - config/env.silo.yaml
# - config/env.qa.yaml
# - config/env.prod.yaml

# Test data CSV files in data/ folder:
# - data/oam/test_data.test11.csv
# - data/oam/test_data.test12.csv
# - data/oam/test_data.silo.csv
# - data/oam/test_data.qa.csv
# - data/oam/test_data.prod.csv

# Review/edit test data
notepad data\test_data.test11.csv
```

### Step 3: Configure Screenshots (Optional)
```powershell
# Enable screenshots for EVERY step (debugging)
$env:SCREENSHOT_EACH_STEP = "true"

# Disable step screenshots (only on failure - default)
$env:SCREENSHOT_EACH_STEP = "false"
# or remove variable
Remove-Item Env:\SCREENSHOT_EACH_STEP
```

### Step 4: Database Configuration (Optional)
```powershell
# If using database tests, configure connection in:
# config/env.test11.yaml

database:
  server: "your-server.database.windows.net"
  database: "your-database"
  username: "your-username"
  password: "your-password"
```

---

## Test Execution

### Sequential Execution (Default)

#### Run All Tests
```powershell
# Run all tests in tests/ directory (BDD + API + Database)
pytest tests/ -v

# Run only BDD feature tests
pytest tests/bdd/features/ -v

# Run only API tests
pytest tests/api/ -v
```

#### Run Specific Test File
```powershell
# Run specific feature test
pytest tests/bdd/features/test_add_ach.py -v

# Run specific test by name
pytest tests/bdd/features/test_add_ach.py::test_add_ach_instruction -v
```

#### Run Tests by Marker
```powershell
# Run smoke tests only
pytest tests/ -v -m smoke

# Run regression tests
pytest tests/ -v -m regression

# Run login tests
pytest tests/ -v -m login

# Run Roth conversion tests
pytest tests/ -v -m roth_conversion

# Run environment-specific tests
pytest tests/ -v -m test11
pytest tests/ -v -m prod
```

#### Run with Allure Report
```powershell
# Run tests and generate Allure results
pytest tests/bdd/features/ -v --alluredir=reports/allure-results

# Generate and view HTML report
allure serve reports/allure-results

# Generate static HTML report
allure generate reports/allure-results --clean -o reports/allure-report

# Open report in browser
start reports/allure-report/index.html
```

### Parallel Execution (Faster)

#### Basic Parallel Execution
```powershell
# Auto-detect CPU cores and run in parallel
pytest tests/bdd/features/ -v -n auto

# Use specific number of workers (e.g., 4 processes)
pytest tests/bdd/features/ -v -n 4

# Parallel execution reduces total execution time
# Example: 100 tests × 30s = 3000s sequential
#          100 tests ÷ 4 workers = 750s parallel
```

#### Parallel with Markers
```powershell
# Parallel smoke tests
pytest tests/ -v -n auto -m smoke

# Parallel regression suite
pytest tests/ -v -n auto -m regression
```

#### Parallel with Allure
```powershell
# Parallel execution with Allure reporting
pytest tests/bdd/features/ -v -n auto --alluredir=reports/allure-results

# Generate report
allure serve reports/allure-results
```

### Debugging Execution

#### Debug Mode (No Parallel)
```powershell
# Run with Python debugger (pdb)
pytest tests/bdd/features/test_add_ach.py -v --pdb

# When test fails, drops into debugger
# Commands:
#   n - next line
#   c - continue
#   p variable_name - print variable
#   q - quit
```

#### Headed Mode (See Browser)
```powershell
# Run with visible browser (not headless)
pytest tests/bdd/features/test_add_ach.py -v --headed

# Slow motion for debugging (1000ms delay)
pytest tests/bdd/features/test_add_ach.py -v --headed --slowmo 1000

# Take screenshot on every step
pytest tests/bdd/features/test_add_ach.py -v --screenshot-each-step
```

#### Verbose Output
```powershell
# Extra verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -v -s

# Show full traceback
pytest tests/ -v --tb=long
```

### Browser Selection

```powershell
# Run with Chromium (default)
pytest tests/ -v --browser chromium

# Run with Firefox
pytest tests/ -v --browser firefox

# Run with WebKit (Safari)
pytest tests/ -v --browser webkit

# Run with all browsers
pytest tests/ -v --browser chromium --browser firefox --browser webkit
```

### Video Recording

```powershell
# Videos are automatically recorded (configured in pyproject.toml)
# Videos saved to: reports/videos/

# View videos after test execution
start reports/videos/

# Video recording settings in conftest.py:
# - "on": Always record
# - "off": Never record
# - "retain-on-failure": Only keep failed test videos (default)
```

---

## Viewing Reports

### Allure Report (Recommended)

#### Option 1: Auto-Generated Report (After pytest_sessionfinish hook)
```powershell
# Run tests (report auto-generates at end)
pytest tests/bdd/features/ -v

# Report automatically created at:
# reports/allure-report/index.html

# Open in browser
start reports/allure-report/index.html

# Or use timestamped version
start reports/allure-report/index_2026-01-29_14-30-45.html
```

#### Option 2: Serve Report (Interactive)
```powershell
# Run tests with Allure results
pytest tests/bdd/features/ -v --alluredir=reports/allure-results

# Serve report (opens browser automatically)
allure serve reports/allure-results

# Server runs on http://localhost:port
# Press Ctrl+C to stop server
```

#### Option 3: Generate Static Report
```powershell
# Generate HTML report
allure generate reports/allure-results --clean -o reports/allure-report

# Open report
start reports/allure-report/index.html
```

### Pytest HTML Report

```powershell
# HTML report auto-generated (configured in pyproject.toml)
# Location: reports/pytest_report.html

# Open report
start reports/pytest_report.html
```

### JUnit XML Report

```powershell
# JUnit XML auto-generated (for CI/CD integration)
# Location: reports/junit/junit-report.xml

# View XML
notepad reports/junit/junit-report.xml
```

### Video Reports

```powershell
# Videos saved to reports/videos/
# Organized by worker for parallel execution:
# - reports/videos/gw0/
# - reports/videos/gw1/
# - reports/videos/gw2/

# Open videos folder
start reports/videos/
```

### Performance Reports (if using @pytest.mark.performance)

```powershell
# Performance metrics saved to reports/performance/
# JSON files with metrics for each test

# View performance report
start reports/performance/
```

---

## Advanced Execution

### Multi-Environment Execution

```powershell
# Run tests on test11 environment
$env:TEST_ENV = "test11"
pytest tests/ -v -m test11

# Run tests on prod environment
$env:TEST_ENV = "prod"
pytest tests/ -v -m prod

# Run on multiple environments sequentially
$environments = @("test11", "test12", "silo")
foreach ($env in $environments) {
    $env:TEST_ENV = $env
    pytest tests/ -v -m $env --alluredir=reports/allure-results-$env
}
```

### Retry Flaky Tests

```powershell
# Auto-retry failed tests (configured in conftest.py)
# Default: 2 retries with 1s delay

# Override retry count
pytest tests/ -v --reruns 3

# Override retry delay
pytest tests/ -v --reruns 2 --reruns-delay 2

# Disable retries
pytest tests/ -v --reruns 0
```

### Distributed Execution (Multiple Machines)

```powershell
# Run on remote worker (requires rsync or SSH setup)
pytest tests/ -v --tx ssh=user@remotehost

# Distribute tests across multiple machines
pytest tests/ -v --tx ssh=user@host1 --tx ssh=user@host2
```

### Custom Test Groups (xdist)

```powershell
# Tests auto-grouped by type (auth, api, ui, database)
# Configured in conftest.py pytest_collection_modifyitems hook

# Run specific group
pytest tests/ -v -n auto --dist loadgroup
```

### Coverage Report

```powershell
# Run with code coverage
pytest tests/ -v --cov=pages --cov=utils --cov-report=html

# View coverage report
start htmlcov/index.html

# Coverage report also in terminal
pytest tests/ -v --cov=pages --cov=utils --cov-report=term-missing
```

### Performance Monitoring

```powershell
# Run performance tests
pytest tests/ -v -m performance

# Performance budgets configured in:
# config/performance_budgets.yaml

# Results saved to:
# reports/performance/
```

---

## CI/CD Execution

### Azure Pipeline (Docker)

```yaml
# Pipeline file: azure-pipelines/azurePipeline-docker.yaml

# Trigger pipeline in Azure DevOps
# Or run locally with Docker:

# Build Docker image
docker build -t dm1-test-automation .

# Run tests in Docker container
docker run --rm dm1-test-automation pytest tests/ -v -n auto
```

### Azure Pipeline (Native)

```yaml
# Pipeline file: FormsAndTracking.yaml

# Runs on azure-pipelines agent
# Steps:
# 1. Install Python
# 2. Create venv
# 3. Install dependencies
# 4. Install Playwright browsers
# 5. Run tests
# 6. Publish Allure report
# 7. Publish test results
```

### GitHub Actions (Example)

```yaml
# .github/workflows/tests.yml
name: Playwright Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m venv venv
          .\venv\Scripts\Activate.ps1
          pip install -e .[dev]
          playwright install chromium

      - name: Run tests
        run: |
          .\venv\Scripts\Activate.ps1
          pytest tests/ -v -n auto --alluredir=allure-results

      - name: Upload Allure results
        uses: actions/upload-artifact@v3
        with:
          name: allure-results
          path: allure-results
```

### Make Commands (Makefile)

```powershell
# If using Makefile (Linux/Mac/WSL)

# Install dependencies
make install

# Run tests
make test

# Run with coverage
make coverage

# Generate report
make report

# Clean artifacts
make clean
```

---

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
```powershell
# Problem: ModuleNotFoundError: No module named 'playwright'
# Solution: Activate virtual environment and install dependencies

.\venv\Scripts\Activate.ps1
pip install -e .[dev]
```

#### 2. Playwright Browsers Not Found
```powershell
# Problem: Playwright browser executable not found
# Solution: Install browsers

playwright install chromium
```

#### 3. Execution Policy Error
```powershell
# Problem: Cannot activate venv (execution policy)
# Solution: Change execution policy

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Port Already in Use
```powershell
# Problem: allure serve fails (port in use)
# Solution: Kill process or use different port

# Find process on port 8080
netstat -ano | findstr :8080

# Kill process
taskkill /PID <pid> /F

# Or generate static report instead
allure generate reports/allure-results -o reports/allure-report
```

#### 5. Tests Stuck/Hanging
```powershell
# Problem: Tests hang during execution
# Solution: Check timeout settings, run with --headed to see what's happening

pytest tests/ -v --headed --timeout=60
```

#### 6. Session/Authentication Issues
```powershell
# Problem: Session expired or authentication fails
# Solution: Delete saved sessions and re-authenticate

# Delete session files
Remove-Item -Recurse -Force tests\.auth\

# Run test again (will re-authenticate)
pytest tests/bdd/features/test_add_ach.py -v
```

#### 7. Parallel Execution Conflicts
```powershell
# Problem: Tests fail in parallel but pass sequentially
# Solution: Run sequentially or check for shared state

# Run without parallel
pytest tests/ -v

# Or mark test as serial
@pytest.mark.serial
def test_must_run_alone():
    pass
```

#### 8. Database Connection Errors
```powershell
# Problem: Database connection timeout
# Solution: Check database config, verify network connectivity

# Test database connection
python -c "from utils.database import Database; db = Database(); print('✓ Connected')"

# Check config file
notepad config\env.test11.yaml
```

---

## Quick Reference Commands

### Daily Workflow
```powershell
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Pull latest changes
git pull

# 3. Install any new dependencies
pip install -e .[dev]

# 4. Run tests
pytest tests/bdd/features/ -v -n auto

# 5. View report
allure serve reports/allure-results

# 6. Deactivate environment (when done)
deactivate
```

### Pre-Commit
```powershell
# Run pre-commit hooks manually
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install

# Update hooks
pre-commit autoupdate
```

### Code Quality
```powershell
# Format code
black .

# Check linting
flake8 pages/ utils/ tests/

# Type checking
mypy pages/ utils/

# Security scan
bandit -r pages/ utils/
```

---

## Complete Example Session

```powershell
# ============================================
# COMPLETE START-TO-END EXECUTION EXAMPLE
# ============================================

# 1. Open PowerShell
# 2. Navigate to project
cd C:\Users\Amit.Malik\vsCode-workspace\ES2PythonPlaywright\DM1TestAutomation

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Verify environment
python --version
playwright --version

# 5. Set environment
$env:TEST_ENV = "test11"

# 6. Run smoke tests (fast validation)
pytest tests/ -v -n auto -m smoke

# 7. Run full regression suite
pytest tests/bdd/features/ -v -n auto --alluredir=reports/allure-results

# 8. View results
allure serve reports/allure-results

# 9. If issues found, run specific test in debug mode
pytest tests/bdd/features/test_add_ach.py -v --headed --screenshot-each-step

# 10. Check videos for failed tests
start reports/videos/

# 11. Review Allure report for details
start reports/allure-report/index.html

# 12. Commit changes (if you made fixes)
git add .
git commit -m "fix: resolved test issues"
git push

# 13. Deactivate environment
deactivate

# ============================================
# SESSION COMPLETE
# ============================================
```

---

## Execution Time Estimates

| Test Scope | Sequential | Parallel (4 workers) |
|------------|-----------|---------------------|
| Single test | ~30s | ~30s |
| Smoke tests (10) | ~5 min | ~2 min |
| Regression (50) | ~25 min | ~8 min |
| Full suite (100+) | ~50 min | ~15 min |

*Times are approximate and depend on network, database, and application performance*

---

## Support & Documentation

- **Framework Guide**: `docs/FRAMEWORK_GUIDE.md`
- **BDD Guide**: `docs/BDD_GUIDE.md`
- **Debugging Guide**: `docs/DEBUGGING_GUIDE.md`
- **Parallel Execution**: `docs/PARALLEL_EXECUTION_GUIDE.md`
- **Environment Setup**: `docs/ENVIRONMENT_GUIDE.md`
- **Allure Reporting**: `docs/allureReadme.md`
- **Auto-Healing Guide**: `docs/AUTO_HEALING_GUIDE.md`

---

**Last Updated**: January 29, 2026
**Framework Version**: 1.0.0
**Playwright Version**: 1.42.0+
