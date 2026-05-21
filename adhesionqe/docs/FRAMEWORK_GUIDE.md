# UI Automation Framework - Complete Guide

## 📋 Table of Contents
1. [Framework Architecture](#1-framework-architecture)
2. [Key Features](#2-key-features)
3. [Folder Structure](#3-folder-structure)
4. [Setup & Installation](#4-setup--installation)
5. [Configuration](#5-configuration)
6. [Running Tests](#6-running-tests)
7. [Reporting & Observability](#7-reporting--observability)
8. [Code Quality](#8-code-quality)
9. [CI/CD Pipeline](#9-cicd-pipeline)
10. [Best Practices](#10-best-practices)

---

## 1. Framework Architecture

### Technology Stack

This framework is built on a robust, modern technology stack designed for scalability, maintainability, and enterprise-grade reliability.

#### Core Technologies
*   **Language**: Python 3.8+ (Recommended: Python 3.12+)
*   **Browser Automation**: [Playwright](https://playwright.dev/python/) 1.42.0+ (Sync API)
    - Fast, reliable, and capable automation across all modern browsers
    - Built-in auto-waiting and retry mechanisms
    - Network interception and mocking capabilities
*   **Test Framework**: [pytest](https://docs.pytest.org/) 8.0.0+
    - Industry-standard Python testing framework
    - Rich plugin ecosystem
    - Parallel test execution support
*   **BDD Framework**: [pytest-bdd](https://pytest-bdd.readthedocs.io/) 7.0.0+
    - Gherkin syntax support (`.feature` files)
    - Given/When/Then step definitions
    - Business-readable test scenarios

#### Design Patterns & Principles
*   **Page Object Model (POM)**: Encapsulates UI interactions within page classes
    - Separates test logic from page-specific details
    - Promotes code reusability and maintainability
    - `BasePage` class provides common functionality (logging, waits, assertions)
*   **Environment Abstraction**: YAML-based configuration per environment
*   **Data-Driven Testing**: CSV-based test data injection
*   **Centralized Logging**: Structured logging with timestamps and levels

#### Supporting Technologies
*   **Configuration Management**: PyYAML for environment configs
*   **Parallel Execution**: pytest-xdist for concurrent test runs
*   **Metrics & Observability**: InfluxDB integration for performance tracking
*   **Reporting**: Allure Framework, pytest-html, JUnit XML
*   **Code Quality**: Black, Flake8, Pylint, Bandit, Isort

---

## 2. Key Features

### 🎯 Core Capabilities

#### 1. **Behavior Driven Development (BDD)**
*   Write tests in plain English using Gherkin syntax
*   Feature files with Given/When/Then scenarios
*   Step definitions in Python for implementation
*   Business stakeholders can understand test scenarios
*   Example feature file: `tests/bdd/features/roth_conversion.feature`

#### 2. **Cross-Browser Testing**
*   **Supported Browsers**: Chromium, Firefox, WebKit (Safari)
*   Configurable per environment via YAML
*   Headless and headed execution modes
*   Browser context configuration with HTTPS error handling
*   Command: `pytest --browser=firefox --headed`

#### 3. **Parallel Execution**
*   Run tests concurrently using `pytest-xdist`
*   Configurable worker count (default: auto-detect CPU cores)
*   Reduces total execution time significantly
*   Example: `pytest -n 4` (4 parallel workers)
*   Automatic test distribution across workers

#### 4. **Multi-Environment Support**
*   Seamless switching between environments:
    - `test11` / `test12` (Development)
    - `qa` (QA Testing)
    - `silo` (Isolated Testing)
    - `prod` (Production Validation)
*   Environment-specific configuration files:
    - `config/env.test11.yaml`
    - `config/env.qa.yaml`
    - `config/env.prod.yaml`
*   Environment-specific test data: `data/test_data.{env}.csv`
*   Dynamic environment selection: `set TEST_ENV=qa` (Windows) or `export TEST_ENV=qa` (Linux/Mac)

#### 5. **Rich Reporting Suite**

##### Allure Framework
*   **Interactive HTML Reports** with:
    - Test execution timeline and history
    - Step-by-step breakdown with screenshots
    - Video recordings attached to failed tests
    - Historical trends and statistics
    - Categorization by feature/suite/severity
    - Retry information
*   **Commands**:
    ```bash
    # Generate and view report
    allure serve reports/allure-results

    # Generate static report
    allure generate reports/allure-results -o reports/allure-report --clean
    ```

##### HTML Report (pytest-html)
*   Single-file summary report: `reports/pytest_report.html`
*   Embedded screenshots and logs
*   Self-contained and portable
*   Perfect for email attachments

##### JUnit XML
*   Standard CI/CD format: `reports/junit.xml`
*   Integration with Azure DevOps, Jenkins, GitLab CI
*   Test result publishing in pipelines

#### 6. **Visual Debugging**
*   **Screenshots**:
    - Automatic capture on test failure
    - Embedded in Allure and HTML reports
    - Stored in test artifacts
*   **Video Recording**: Configurable modes via pytest options:
    - `--video=on` - Record all tests
    - `--video=retain-on-failure` - Keep only failed test videos (default)
    - `--video=off` - No video recording
*   **Playwright Traces**: Detailed execution traces for post-mortem
    - Timeline view of all actions
    - Network requests/responses with headers and payloads
    - Console logs and JavaScript errors
    - DOM snapshots at each step
    - Command: `--tracing=retain-on-failure`

#### 7. **Centralized Logging System**
*   **Implementation**: `utils/logger.py`
*   **Features**:
    - Consistent formatting across all modules
    - Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
    - Console output with timestamps
    - Integration with pytest's log capture
    - Logger instances per page class for granular debugging
*   **Usage in Page Objects**:
    ```python
    self.logger.info("Navigating to login page")
    self.logger.warning("Element not found, retrying...")
    self.logger.error("Login failed", exc_info=True)
    ```
*   **Pytest Configuration**:
    - `log_cli = true` - Enable live console logging
    - `log_cli_level = "INFO"` - Default log level
    - View logs with: `pytest --log-cli-level=DEBUG`

#### 8. **Metrics & Observability (InfluxDB Integration)**
*   **Implementation**: `utils/influx_reporter.py`
*   **Features**:
    - Real-time metrics tracking to InfluxDB
    - Test execution duration per test
    - Pass/fail rates over time
    - Environment-specific metrics
    - Build-level aggregation
    - Automatic test deduplication (handles retries)
    - Direct artifact URLs from Azure Pipelines
*   **Tracked Metrics**:
    - Test name, status, duration
    - Environment, build ID, build reason
    - Browser type, timestamps
    - Links to reports and artifacts
*   **Configuration** (Environment Variables):
    ```bash
    INFLUXDB_URL=http://localhost:8086
    INFLUXDB_TOKEN=your-token
    INFLUXDB_ORG=default
    INFLUXDB_BUCKET=test-results
    ```

#### 9. **Code Quality Tools**
*   **Black** (v24.2.0+): Opinionated code formatter (PEP 8 compliant)
    - Line length: 100 characters
    - Consistent style across codebase
*   **Flake8** (v7.0.0+): Style guide enforcement
    - Line length checks, unused imports, whitespace issues
*   **Pylint** (v3.0.0+): Comprehensive static code analysis
    - Code smells, bugs, design issues
*   **Bandit** (v1.7.5+): Security vulnerability scanning
    - SQL injection, hardcoded passwords, insecure functions
*   **Isort** (v5.13.0+): Import statement organization
    - Profile: black-compatible
*   **Mypy** (v1.8.0+): Optional static type checking

#### 10. **CI/CD Integration**
*   **Azure Pipelines** configuration: `azurePipeline.yaml`
*   **Features**:
    - Custom Linux agent pool: `ubuntu2204-qa`
    - Parameterized builds (environment, pytest markers, worker count)
    - Dynamic variable setup based on Build.Reason
    - Artifact publishing (test results, reports, videos, traces)
    - InfluxDB metrics push
*   **Pipeline Parameters**:
    - `environment`: test11 / test12 / qa / silo / prod
    - `marker`: pytest markers (smoke, regression, e2e, etc.)
    - `workers`: Parallel worker count (default: 4)

---

## 3. Folder Structure

```
DM_Automation_new/
│
├── config/                          # Environment-specific configurations
│   ├── env.prod.yaml               # Production environment config
│   ├── env.qa.yaml                 # QA environment config
│   ├── env.silo.yaml               # Silo environment config
│   ├── env.test11.yaml             # Test11 environment config
│   └── env.test12.yaml             # Test12 environment config
│
├── data/                            # Test data files (CSV format)
│   ├── test_data.prod.csv          # Production test data
│   ├── test_data.qa.csv            # QA test data
│   ├── test_data.silo.csv          # Silo test data
│   ├── test_data.test11.csv        # Test11 test data
│   └── test_data.test12.csv        # Test12 test data
│
├── pages/                           # Page Object Model classes
│   ├── __init__.py
│   ├── base_page.py                # Base class with common functionality
│   ├── login_page.py               # Login page interactions
│   ├── clients_page.py             # Clients page interactions
│   ├── account_list_page.py        # Account list page interactions
│   ├── account_detail_page.py      # Account detail page interactions
│   ├── roth_conversion_page.py     # Roth conversion page interactions
│   └── tracking_center_page.py     # Tracking center page interactions
│
├── tests/                           # Test scripts and features
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures and pytest hooks
│   │                               # - browser_context_args (HTTPS error handling)
│   │                               # - test_context, test_data fixtures
│   │                               # - Page object fixtures
│   │                               # - Environment marker setup
│   ├── bdd/                        # BDD tests using pytest-bdd
│   │   ├── __init__.py
│   │   ├── features/               # Gherkin .feature files
│   │   │   └── roth_conversion.feature
│   │   └── steps/                  # Python step definitions
│   │       └── test_roth_conversion_steps.py
│   └── ui/                         # Standard UI tests (non-BDD)
│       └── test_roth_conversion_cucumber.py
│
├── utils/                           # Utility helper modules
│   ├── __init__.py
│   ├── logger.py                   # Centralized logging configuration
│   ├── settings.py                 # Environment configuration loader
│   └── influx_reporter.py          # InfluxDB metrics reporter
│
├── reports/                         # Generated test reports (auto-created)
│   ├── allure-results/             # Allure raw results (JSON)
│   ├── allure-report/              # Allure HTML report (generated)
│   ├── pytest_report.html          # pytest-html report
│   ├── junit.xml                   # JUnit XML report
│   ├── flake8-report.txt           # Flake8 linting report
│   ├── pylint-report.txt           # Pylint analysis report
│   └── bandit-report.json          # Bandit security report
│
├── test-results/                    # Playwright test artifacts
│   └── (videos, traces, screenshots per test)
│
├── fixtures/                        # Test fixtures (optional)
│
├── src/                             # Legacy/alternate test location
│   └── testScript/
│
├── tools/                           # Helper tools and scripts
│
├── azurePipeline.yaml              # Azure DevOps CI/CD pipeline definition
├── pyproject.toml                  # Project dependencies and tool configs
├── requirements.txt                # Python dependencies (pip format)
├── run_tests.bat                   # Windows helper script for local execution
├── generate_allure_report.bat      # Windows script to generate Allure report
├── sonar-project.properties        # SonarQube configuration
│
└── Documentation Files:
    ├── README.md                    # Project overview
    ├── FRAMEWORK_DOCUMENTATION.md   # Framework documentation (this file)
    ├── BDD_GUIDE.md                # BDD testing guide
    ├── TESTING_GUIDE.md            # Testing strategy guide
    ├── ENVIRONMENT_GUIDE.md        # Environment configuration guide
    ├── DEBUGGING_GUIDE.md          # Debugging and troubleshooting
    ├── AZURE_PIPELINE_GUIDE.md     # Azure Pipeline usage guide
    ├── TAG_USAGE_GUIDE.md          # Pytest markers/tags guide
    ├── CODE_QUALITY_REPORT.md      # Linting results report
    └── SETUP_SUMMARY.md            # Setup completion summary
```

### Key Directory Details

*   **config/**: YAML files with environment-specific URLs, timeouts, browser settings
*   **data/**: CSV files with test data (usernames, account numbers, amounts)
*   **pages/**: Page Object classes - each class represents a web page and its interactions
*   **tests/bdd/**: BDD tests with Gherkin features and Python step definitions
*   **tests/ui/**: Traditional pytest tests (non-BDD style)
*   **utils/**: Reusable utilities (logging, settings loader, metrics reporter)
*   **reports/**: All test execution reports and artifacts

---

## 4. Setup & Installation

### Prerequisites

*   **Python 3.8 or higher** (Recommended: Python 3.12.6)
*   **Git** for version control
*   **Node.js** (Optional, for Allure CLI)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://dev.azure.com/AssetmarkInc/Core/_git/DM1TestAutomation
cd DM_Automation_new
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 3. Upgrade pip, setuptools, and wheel
```bash
python -m pip install --upgrade pip setuptools wheel
```

#### 4. Install Project Dependencies
```bash
# Install framework in editable mode (recommended for development)
pip install -e .

# Install development dependencies (linting, code quality tools)
pip install -e .[dev]
```

#### 5. Install Playwright Browsers
```bash
# Install all browsers (Chromium, Firefox, WebKit)
playwright install

# Or install specific browser
playwright install chromium
```

#### 6. Verify Installation
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify Playwright
playwright --version
```

#### 7. Install Allure CLI (Optional, for report generation)
```bash
# Using npm (requires Node.js)
npm install -g allure-commandline

# Verify installation
allure --version
```

### Quick Start Test
```bash
# Run a quick smoke test to verify setup
pytest tests/ui/ -v --headed -k "login" --tb=short
```

---

## 5. Configuration

### 5.1 Environment Configuration

#### Environment YAML Files (`config/env.{env}.yaml`)

Each environment has a dedicated configuration file:

**Example: `config/env.qa.yaml`**
```yaml
# QA Environment Configuration
environment: qa

# Application settings
application:
  base_url: "https://wrmqa.schwabplan.com/"
  timeout: 30000  # milliseconds

# Browser settings
browser:
  browser_type: "chromium"  # chromium, firefox, webkit
  headless: false
  slow_mo: 0
  viewport:
    width: 1280
    height: 720
  args:
    - "--start-maximized"

# Test settings
test:
  screenshot_on_failure: true
  video: "retain-on-failure"  # on, off, retain-on-failure
  trace: "retain-on-failure"   # on, off, retain-on-failure

# Reporting
reporting:
  allure_results: "reports/allure-results"
  html_report: "reports/pytest_report.html"

# Data
data:
  test_data_csv: "data/test_data.qa.csv"
```

#### Switching Environments

```bash
# Windows
set TEST_ENV=qa
pytest

# Linux/Mac
export TEST_ENV=qa
pytest

# Or inline
TEST_ENV=prod pytest -m smoke
```

### 5.2 Test Data Configuration

#### CSV Test Data Files (`data/test_data.{env}.csv`)

**Example: `data/test_data.qa.csv`**
```csv
username,password,client_name,account_number,conversion_amount
testuser@example.com,SecurePass123,John Doe,123456789,5000.00
```

### 5.3 Pytest Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = """
-v
--tb=short
--strict-markers
--disable-warnings
--browser=chromium
--video=retain-on-failure
--screenshot=on
--tracing=retain-on-failure
--html=reports/pytest_report.html
--self-contained-html
--alluredir=reports/allure-results
"""

markers = [
    "smoke: Quick smoke tests",
    "regression: Full regression suite",
    "e2e: End-to-end tests",
    "test11: Tests for test11 environment",
    "qa: Tests for QA environment",
    # ... more markers
]

log_cli = true
log_cli_level = "INFO"
timeout = 300
```

### 5.4 Browser Context Configuration (`tests/conftest.py`)

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context to ignore HTTPS errors"""
    return {
        **browser_context_args,
        "ignore_https_errors": True
    }
```

---

## 6. Running Tests

### 6.1 Basic Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/ui/test_roth_conversion_cucumber.py

# Run specific test function
pytest tests/ui/test_roth_conversion_cucumber.py::test_successfully_complete_roth_ira_conversion
```

### 6.2 Environment Selection

```bash
# Windows
set TEST_ENV=qa
pytest

# Linux/Mac
export TEST_ENV=qa
pytest

# Inline
TEST_ENV=silo pytest -v
```

### 6.3 Browser Configuration

```bash
# Run in headed mode (visible browser)
pytest --headed

# Run in headless mode
pytest --headless

# Specific browser
pytest --browser=firefox
pytest --browser=webkit

# Multiple browsers
pytest --browser=chromium --browser=firefox
```

### 6.4 Parallel Execution

```bash
# Auto-detect CPU cores
pytest -n auto

# Specific number of workers
pytest -n 4

# Parallel with environment
set TEST_ENV=qa
pytest -n 4 -v
```

### 6.5 Marker/Tag Filtering

```bash
# Run smoke tests
pytest -m smoke

# Run regression tests
pytest -m regression

# Run e2e tests
pytest -m e2e

# Multiple markers (OR)
pytest -m "smoke or regression"

# Multiple markers (AND)
pytest -m "smoke and roth_conversion"

# Exclude markers
pytest -m "not slow"
```

### 6.6 Feature File Execution (BDD)

```bash
# Run specific feature
pytest tests/bdd/features/roth_conversion.feature

# Run all BDD tests
pytest tests/bdd/

# BDD with markers
pytest tests/bdd/ -m smoke
```

### 6.7 Video and Tracing Options

```bash
# Video recording
pytest --video=on              # Record all
pytest --video=retain-on-failure  # Only failed (default)
pytest --video=off             # No recording

# Tracing
pytest --tracing=on            # Trace all
pytest --tracing=retain-on-failure  # Only failed (default)
pytest --tracing=off           # No tracing

# Combined
pytest --video=on --tracing=on --headed
```

### 6.8 Reporting Options

```bash
# Generate Allure and HTML reports
pytest --alluredir=reports/allure-results --html=reports/pytest_report.html

# With JUnit XML
pytest --junitxml=reports/junit.xml
```

### 6.9 Logging Options

```bash
# Enable live logging
pytest --log-cli-level=INFO

# Debug level logging
pytest --log-cli-level=DEBUG

# Suppress warnings
pytest --disable-warnings
```

### 6.10 Helper Scripts

#### Windows: `run_tests.bat`
```batch
@echo off
python -m pytest -v --headed --log-cli-level=INFO
```

Usage:
```cmd
run_tests.bat
```

---

## 7. Reporting & Observability

### 7.1 Allure Reports

#### Generate and View Report
```bash
# Serve interactive report (auto-opens browser)
allure serve reports/allure-results

# Generate static HTML report
allure generate reports/allure-results -o reports/allure-report --clean

# Open generated report
allure open reports/allure-report
```

#### Helper Script (Windows): `generate_allure_report.bat`
```batch
@echo off
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

#### Allure Features
*   Test execution timeline
*   Categorization by features, suites, severity
*   Step-by-step breakdown
*   Attached screenshots, videos, traces
*   Historical trends (with Allure Server)
*   Retry information
*   Environment details

### 7.2 HTML Report

```bash
# Report location
reports/pytest_report.html

# Open in default browser (Windows)
start reports/pytest_report.html

# Open in default browser (Mac)
open reports/pytest_report.html

# Open in default browser (Linux)
xdg-open reports/pytest_report.html
```

### 7.3 JUnit XML Report

```bash
# Report location
reports/junit.xml

# Used by CI/CD systems (Azure DevOps, Jenkins, etc.)
```

### 7.4 InfluxDB Metrics

#### Configuration (Environment Variables)
```bash
# Set in CI/CD pipeline or local environment
export INFLUXDB_URL=http://influxdb.example.com:8086
export INFLUXDB_TOKEN=your-token-here
export INFLUXDB_ORG=your-org
export INFLUXDB_BUCKET=test-results
export ENVIRONMENT=qa
export BUILD_ID=12345
```

#### Run Reporter
```bash
# After test execution
python utils/influx_reporter.py
```

#### Metrics Tracked
*   Test name, status (passed/failed), duration
*   Environment, build ID, build reason
*   Browser type
*   Timestamps (start, stop)
*   Artifact URLs (Azure Pipelines)

### 7.5 Logging Output

```bash
# View logs during execution
pytest --log-cli-level=INFO

# Logs are also captured in reports:
# - Console output in Allure
# - Test output in HTML report
# - Jenkins/Azure DevOps pipeline logs
```

---

## 8. Code Quality

### 8.1 Code Formatting

```bash
# Format code with Black
black .

# Check formatting without changes
black --check .

# Organize imports with Isort
isort .

# Check import order
isort --check-only .
```

### 8.2 Linting

```bash
# Run Flake8 (style enforcement)
flake8

# Save report to file
flake8 > reports/flake8-report.txt

# Run Pylint (static analysis)
pylint pages tests utils

# Save report
pylint pages tests utils > reports/pylint-report.txt
```

### 8.3 Security Scanning

```bash
# Run Bandit (security issues)
bandit -r .

# Save JSON report
bandit -r . -f json -o reports/bandit-report.json

# Save text report
bandit -r . -o reports/bandit-report.txt
```

### 8.4 Type Checking (Optional)

```bash
# Run Mypy
mypy pages tests utils

# With stricter checks
mypy --strict pages tests utils
```

### 8.5 Combined Quality Check

```bash
# Run all code quality checks
black --check .
isort --check-only .
flake8
pylint pages tests utils
bandit -r .
```

### 8.6 Auto-Fix Common Issues

```bash
# Format and organize
black .
isort .

# Fix Flake8 issues automatically (using autoflake)
pip install autoflake
autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .
```

### 8.7 Pre-Commit Workflow

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.0
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

Install and run:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 9. CI/CD Pipeline

### 9.1 Azure Pipeline Configuration

**File**: `azurePipeline.yaml`

#### Pipeline Structure
```yaml
pool:
  name: 'ubuntu2204-qa'
  timeoutInMinutes: 10

trigger: none  # Manual trigger only

parameters:
  - name: environment
    displayName: 'Environment'
    type: string
    default: 'test11'
    values: ['test11', 'test12', 'silo', 'prod', 'qa']

  - name: marker
    displayName: 'Pytest Marker'
    type: string
    default: 'smoke'

  - name: workers
    displayName: 'Parallel Workers'
    type: string
    default: '4'

jobs:
  - job: RunPytestBDDTests
    displayName: 'Run Playwright Pytest BDD Tests'

    steps:
      # Setup Python, install dependencies
      # Run pytest with parameters
      # Generate Allure reports
      # Push metrics to InfluxDB
      # Publish artifacts
```

### 9.2 Pipeline Parameters

*   **environment**: Target environment (test11, test12, qa, silo, prod)
*   **marker**: Pytest marker/tag to filter tests (smoke, regression, e2e, etc.)
*   **workers**: Number of parallel workers (default: 4)

### 9.3 Running Pipeline

1.  Navigate to Azure DevOps: https://dev.azure.com/AssetmarkInc/Core/_build
2.  Select the pipeline
3.  Click "Run pipeline"
4.  Select parameters:
    - Environment: `qa`
    - Marker: `smoke`
    - Workers: `4`
5.  Click "Run"

### 9.4 Pipeline Workflow

1.  **Checkout Code**: Clone repository
2.  **Setup Python**: Install Python 3.12
3.  **Install Dependencies**: `pip install -e .`
4.  **Install Playwright**: `playwright install`
5.  **Install Allure CLI**: Download and setup Allure
6.  **Run Tests**: Execute pytest with parameters
    ```bash
    pytest -m ${{ parameters.marker }} \
           -n ${{ parameters.workers }} \
           -v --headed \
           --video=retain-on-failure \
           --tracing=retain-on-failure \
           --alluredir=reports/allure-results
    ```
7.  **Generate Allure Report**: Create HTML report
8.  **Push Metrics**: Send results to InfluxDB
9.  **Publish Artifacts**:
    - Test Results (JUnit XML)
    - Pytest HTML Report
    - Allure Report
    - Allure Results (JSON)
    - Videos and Traces

### 9.5 Viewing Pipeline Results

*   **Test Results**: Published to Azure DevOps Tests tab
*   **Artifacts**: Download from pipeline run artifacts
*   **Allure Report**: Published as artifact, can be extracted and viewed
*   **Logs**: View detailed execution logs in pipeline console

---

## 10. Best Practices

### 10.1 Test Design

*   **Use Page Object Model**: Keep page interactions separate from test logic
*   **Write Descriptive Test Names**: Clear naming for test functions and scenarios
*   **Use Markers/Tags**: Categorize tests (smoke, regression, e2e)
*   **Keep Tests Independent**: Tests should not depend on execution order
*   **Use Fixtures**: Leverage pytest fixtures for setup/teardown
*   **Data-Driven Testing**: Use CSV files for test data

### 10.2 Code Quality

*   **Follow PEP 8**: Use Black formatter for consistency
*   **Organize Imports**: Use Isort to maintain import order
*   **Document Code**: Add docstrings to classes and methods
*   **Handle Exceptions**: Use try-except blocks where appropriate
*   **Log Important Actions**: Use logger for debugging
*   **Avoid Hardcoded Values**: Use configuration files

### 10.3 Debugging

*   **Use `--headed` Mode**: Visualize browser actions during development
*   **Enable Tracing**: Use `--tracing=on` for detailed execution traces
*   **Increase Logging**: Use `--log-cli-level=DEBUG` for verbose output
*   **Slow Down Execution**: Use `slow_mo` in browser config for visual debugging
*   **Inspect Failures**: Check screenshots, videos, and traces
*   **Use `page.pause()`**: Add breakpoints in tests for debugging

### 10.4 Performance

*   **Run Tests in Parallel**: Use `-n auto` or `-n 4` for faster execution
*   **Headless Mode in CI**: Use `--headless` in pipelines for speed
*   **Selective Video Recording**: Use `--video=retain-on-failure`
*   **Optimize Waits**: Use explicit waits instead of fixed sleeps
*   **Reuse Browser Contexts**: Leverage fixtures and scopes

### 10.5 Maintenance

*   **Keep Dependencies Updated**: Regularly update packages
*   **Run Code Quality Checks**: Use pre-commit hooks
*   **Review Test Results**: Monitor InfluxDB metrics and trends
*   **Clean Up Reports**: Archive old reports, keep workspace clean
*   **Document Changes**: Update documentation when adding features
*   **Version Control**: Commit changes frequently with descriptive messages

---

## 📚 Additional Resources

*   **Playwright Documentation**: https://playwright.dev/python/
*   **pytest Documentation**: https://docs.pytest.org/
*   **pytest-bdd Documentation**: https://pytest-bdd.readthedocs.io/
*   **Allure Framework**: https://docs.qameta.io/allure/
*   **Azure Pipelines YAML**: https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema

---

## 🆘 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Reinstall in editable mode
pip install -e .
```

**2. Playwright Browsers Missing**
```bash
playwright install
```

**3. Environment Not Found**
```bash
# Verify TEST_ENV is set correctly
echo %TEST_ENV%  # Windows
echo $TEST_ENV   # Linux/Mac

# Check config file exists
ls config/env.qa.yaml
```

**4. Allure Command Not Found**
```bash
# Install Allure CLI
npm install -g allure-commandline
```

**5. Tests Timing Out**
```bash
# Increase timeout in pyproject.toml
timeout = 600
```

---

**Last Updated**: December 2025
**Framework Version**: 1.0.0
**Python Version**: 3.12+
