# UI Automation Framework - Roth IRA Conversion Flow

## 1. Project Description

This project automates the end-to-end UI flow for performing a Roth IRA conversion in a financial web application. It validates user login, client and account navigation, asset movement, and conversion submission, ensuring the process works as expected. The framework leverages Playwright for browser automation, Python with pytest for test orchestration, and implements the Page Object Model for maintainable, scalable test code.

## 2. Project Structure

```
ui-automation-framework/
├── pyproject.toml
├── pytest.ini
├── README.md
└── src/
    ├── pageFunction/
    │   ├── login_page.py
    │   ├── clients_page.py
    │   ├── account_list_page.py
    │   ├── account_detail_page.py
    │   ├── roth_conversion_page.py
    │   └── tracking_center_page.py
    ├── testScript/
    │   └── test_roth_conversion_flow.py
    └── runner/
        └── pytest.ini
```

- **src/pageFunction/**: Contains all Page Object Model classes, each encapsulating UI interactions for a specific page.
- **src/testScript/**: Holds test scripts, with each file representing a test scenario or flow.
- **src/runner/**: Includes test runner configuration files (e.g., `pytest.ini`) for pytest options and markers.
- **pyproject.toml**: Project metadata and dependency management for reproducible environments.
- The structure follows standard Python package conventions for clarity and scalability.

## 3. Code Files Walkthrough

### Page Functions
- **login_page.py**: Implements the `LoginPage` class, providing async methods to interact with the login form, handle cookies, and submit credentials.
- **clients_page.py**: Defines the `ClientsPage` class, enabling navigation to the clients section and account list via UI elements.
- **account_list_page.py**: Contains the `AccountListPage` class, allowing client search and selection of specific accounts from the list.
- **account_detail_page.py**: Provides the `AccountDetailPage` class, automating the account wizard steps, including asset movement and Roth IRA conversion selection.
- **roth_conversion_page.py**: Implements the `RothConversionPage` class, handling destination account selection, conversion options, amount entry, and review submission.
- **tracking_center_page.py**: Defines the `TrackingCenterPage` class, verifying conversion status and handling logout actions.

### Test Scripts
- **test_roth_conversion_flow.py**: Orchestrates the full Roth IRA conversion scenario using pytest's async fixture for setup. It sequentially calls page object methods to simulate user actions and asserts expected outcomes at each step.

### Configuration
- **pytest.ini**: Configures pytest for test discovery, browser options, logging, timeouts, and custom markers for test categorization.
- **pyproject.toml**: Manages project dependencies, optional development tools, and pytest options for consistent environments and code quality.

**Test Execution Flow:**
- The test script imports all relevant page objects and uses a pytest fixture to instantiate them with the Playwright `Page` instance.
- Each test method performs UI actions by calling page object methods, ensuring separation of concerns and maintainability (Page Object Model).
- Assertions and verifications are performed using Playwright's expect API within page objects.
- Async functions and pytest-asyncio enable non-blocking browser automation and robust test orchestration.

## 4. Installation and Execution

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Node.js (for Playwright CLI, optional but recommended)

### Setup Instructions

1. **Create and activate a virtual environment** (recommended):
```bash
# if Python was not found; run without arguments to install from the #Microsoft Store, or disable this shortcut from Settings > Apps > #Advanced app settings > App execution aliases.

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. **Install project dependencies**:
```bash
pip install -e .
```
*Alternatively, if not using editable mode:*
```bash
pip install .
```
### execute modified
python -m pip install --upgrade pip setuptools wheel build
### Replace the backslash-escaped addopts with a TOML multiline string (safer/readable). Example change (apply to <>\pyproject.toml)
### [tool.pytest.ini_options]
<!-- testpaths = ["src/testScript"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = """
-v
--tb=short
--strict-markers
--disable-warnings
--asyncio-mode=auto
--browser=chromium
--headed=False
--screenshot=only-on-failure
--video=retain-on-failure
--tracing=retain-on-failure
""" -->
### and Run
pip install . -vvv

3. **Install Playwright browsers**:
```bash
playwright install
```

### Running Tests

**Run all tests:**
```bash
pytest
```
### added below to find packages in src
[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]

### Changed in test_ file
# ...existing code...
- from src.pageFunction.login_page import LoginPage
- from src.pageFunction.clients_page import ClientsPage
- from src.pageFunction.account_list_page import AccountListPage
- from src.pageFunction.account_detail_page import AccountDetailPage
- from src.pageFunction.roth_conversion_page import RothConversionPage
- from src.pageFunction.tracking_center_page import TrackingCenterPage
+ from pageFunction.login_page import LoginPage
+ from pageFunction.clients_page import ClientsPage
+ from pageFunction.account_list_page import AccountListPage
+ from pageFunction.account_detail_page import AccountDetailPage
+ from pageFunction.roth_conversion_page import RothConversionPage
+ from pageFunction.tracking_center_page import TrackingCenterPage
# ...existing code...

**Run a specific test file:**
```bash
pytest src/testScript/test_roth_conversion_flow.py
```

**Run a specific test class or method:**
```bash
pytest -k "TestRothConversionFlow"
pytest -k "test_roth_conversion_flow"
```

**Run tests in headed mode (show browser UI):**
```bash
pytest --headed=True
```

**Run with a specific browser:**
```bash
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit
```

**Run tests in parallel:**
```bash
pytest -n auto
```

**Generate an HTML report:**
```bash
pytest --html=report.html --self-contained-html
```

**Common pytest options:**
- `-v`: Verbose output
- `--tb=short`: Short traceback format
- `--disable-warnings`: Suppress warnings
- `--strict-markers`: Enforce marker usage
- `--screenshot=only-on-failure`: Save screenshots for failed tests
- `--video=retain-on-failure`: Save videos for failed tests
- `--tracing=retain-on-failure`: Save Playwright traces for failed tests

### Viewing Results
- Test results are displayed in the terminal.
- Screenshots, videos, and traces for failed tests are saved in the `test-results/` directory.
- HTML reports can be opened in any browser for detailed results.

### Troubleshooting Tips
- If Playwright browsers are not installed, run `playwright install` again.
- For dependency issues, ensure your virtual environment is activated and Python version is >=3.8.
- For async test errors, verify that `pytest-asyncio` is installed and `asyncio_mode` is set to `auto` in configuration.
