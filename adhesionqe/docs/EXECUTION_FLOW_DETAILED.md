# Detailed Execution Flow - Step by Step

This document explains the EXACT execution sequence when you run a test, showing which file, function, and fixture executes at each step.

---

## Execution Command
```powershell
pytest tests/bdd/features/test_add_ach.py -v
```

---

## Complete Execution Flow

### Phase 1: Pytest Initialization (Before Any Tests)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: pytest starts, loads configuration                      │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `pyproject.toml`
**Action**: Pytest reads configuration from `[tool.pytest.ini_options]`
- Loads markers (smoke, regression, etc.)
- Loads addopts (--alluredir, --video, etc.)
- Sets timeout, log settings

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: pytest loads conftest.py files (bottom-up)              │
└─────────────────────────────────────────────────────────────────┘
```

**Files loaded in order**:
1. `tests/conftest.py` (root conftest)
2. `tests/bdd/conftest.py` (if exists)
3. `tests/bdd/features/conftest.py` (if exists)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: pytest_addoption() hook                                 │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_addoption(parser)`
**Line**: 43-50
**Action**: Registers custom CLI options
- Adds `--screenshot-each-step` option to parser

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: pytest_configure() hook                                 │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_configure(config)`
**Line**: 53-77
**Action**:
1. Registers custom markers (env, app, performance, lighthouse)
2. Reads `--screenshot-each-step` CLI flag or `SCREENSHOT_EACH_STEP` env var
3. Calls `enable_step_screenshots(screenshot_each_step)` → `utils/allure_logger.py`
4. Prints screenshot configuration status
5. Sets up auto-retry for flaky tests (config.option.reruns = 2)

**Variables set**:
- `STEP_SCREENSHOTS_ENABLED` (in allure_logger.py) = True/False

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Module imports and initialization                       │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py` (top of file)
**Lines**: 1-37
**Action**: Import statements execute
1. `from utils.settings import Settings` → Creates Settings object
2. `Settings(env=env)` → Reads `config/env.test11.yaml`
3. `from tests.ui_fixtures.data_fixtures import *` → Loads data fixtures
4. `from tests.ui_fixtures.page_fixtures import *` → Loads page fixtures
5. `APP_CONFIGS = _load_app_configs(settings)` (line 258) → Loads app configurations

**Files read**:
- `config/env.test11.yaml` (or env specified in TEST_ENV)
- `data/test_data.test11.csv`

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: pytest_sessionstart() hook                              │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_sessionstart(session)`
**Line**: 80-105
**Action**: Clears old Allure results
1. Checks if `reports/allure-results` exists
2. Removes all files in directory (keeps directory)
3. Creates directory if doesn't exist
4. Prints cleanup message

**Directory modified**: `reports/allure-results/`

---

### Phase 2: Test Collection

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: pytest_collection() - Discover tests                    │
└─────────────────────────────────────────────────────────────────┘
```

**Action**: Pytest discovers test files
1. Scans `tests/bdd/features/test_add_ach.py`
2. Finds test functions matching `test_*` pattern
3. pytest-bdd plugin converts BDD scenarios to test functions

**File**: `tests/bdd/features/test_add_ach.py`
**Found**:
- `test_add_ach_instruction()` scenario
- Associated step definitions from `tests/bdd/steps/*.py`

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: pytest_collection_modifyitems() hook                    │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_collection_modifyitems(config, items)`
**Line**: 108-163
**Action**: For each collected test:
1. **Initialize retry tracking**:
   - `item.execution_count = 0`
   - `item.failed_count = 0`
   - `item.start_time = None`

2. **Add environment markers**:
   - Reads `TEST_ENV` environment variable
   - Adds marker: `item.add_marker(pytest.mark.test11)` (if TEST_ENV=test11)

3. **Auto-assign xdist groups** (for parallel execution):
   - Analyzes test name
   - Assigns group: "auth", "api", "ui", "database", or "default"
   - Adds marker: `item.add_marker(pytest.mark.xdist_group(group))`

4. **Mark slow tests**:
   - If test has >5 parameters, adds `pytest.mark.slow`

**Test item modified**: Markers added for execution strategy

---

### Phase 3: Session-Level Fixtures (Once per Test Session)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: browser_context_args fixture (scope="session")          │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `browser_context_args(browser_context_args, request)`
**Line**: 173-196
**Scope**: session (runs once, shared across all tests)
**Action**:
1. Gets worker ID: `os.environ.get("PYTEST_XDIST_WORKER", "master")`
2. Sets video directory based on worker (e.g., `reports/videos/gw0/`)
3. Creates context args dict:
   ```python
   {
       **browser_context_args,  # Playwright defaults
       "ignore_https_errors": True,
       "record_video_dir": "reports/videos/gw0"
   }
   ```
4. Returns context_args

**Variables created**:
- `context_args` dict with browser configuration

**Note**: This fixture is provided by pytest-playwright but we override it to customize

---

### Phase 4: Test-Level Fixtures (Before Each Test)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 10: reset_step_screenshot_counter fixture (autouse=True)   │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `reset_step_screenshot_counter()`
**Line**: 700-703
**Scope**: function (runs before each test)
**Action**: Calls `reset_step_counter()` from utils/allure_logger.py
- Resets `_step_counter = 0` in allure_logger module

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 11: test_data fixture                                      │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/ui_fixtures/data_fixtures.py`
**Function**: `test_data(request)`
**Scope**: function
**Action**:
1. Gets environment from `TEST_ENV` env var (default: "test11")
2. Loads CSV file: `data/test_data.test11.csv`
3. Reads first row of test data (username, password, client_id, etc.)
4. Returns dict: `{"username": "...", "password": "...", ...}`

**Returns**: Dictionary with test data

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 12: browser fixture (from pytest-playwright)               │
└─────────────────────────────────────────────────────────────────┘
```

**File**: pytest-playwright plugin (internal)
**Scope**: session
**Action**:
1. Launches browser using `browser_context_args` from Step 9
2. Creates Chromium browser instance (default)
3. Browser runs in headless mode (unless `--headed` flag)

**Object created**: `Browser` instance (Playwright API)

**This is where the browser actually starts** 🚀

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 13: authenticated_page fixture                             │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `authenticated_page(browser, test_data, request)`
**Line**: 284-365
**Scope**: function (runs for each test)
**Dependencies**: Requires `browser` (Step 12) and `test_data` (Step 11)

**Detailed execution**:

**13.1** Get worker ID for parallel execution
```python
worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")  # "master" or "gw0", "gw1", etc.
```

**13.2** Get app name from test marker (default: "ewm")
```python
app_marker = request.node.get_closest_marker("app")
app_name = app_marker.args[0] if app_marker else "ewm"
```

**13.3** Get app configuration (from APP_CONFIGS loaded in Step 5)
```python
app_config = APP_CONFIGS[app_name]  # AppConfig object
# Contains: login_url, home_url, login_page_class, timeout
```

**13.4** Get username and session file path
```python
username = test_data.get("username", "default_user")
session_file = _get_session_file(username, app_name, worker_id)
# Returns: Path("tests/.auth/ewm_testuser_master.json")
```

**13.5** Check if session file exists and is valid (< 8 hours old)
```python
if session_file.exists():
    file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
    file_age_hours = file_age.total_seconds() / 3600

    if file_age_hours > 8:
        session_file.unlink()  # Delete old session
```

**13.6a** If valid session exists → Load saved session
```python
context = browser.new_context(
    storage_state=str(session_file),  # Load cookies/localStorage
    ignore_https_errors=True
)
page = context.new_page()
page.goto(app_config.home_url, timeout=30000)  # Navigate to home
page.wait_for_load_state("domcontentloaded", timeout=10000)

# Verify session still valid
if "login" not in page.url.lower():
    # Session valid! Return page
    yield page  # Test executes here ← MAIN TEST EXECUTION POINT
    page.close()
    context.close()
    return
```

**13.6b** If no session or expired → Perform login
```python
context = browser.new_context(ignore_https_errors=True)
page = context.new_page()

# Call login function
login_success = _perform_login(page, app_config, test_data)
```

**13.7** _perform_login() executes (if needed)
```python
# File: tests/conftest.py, Line: 271-283
# Function: _perform_login(page, app_config, test_data)

login_page = app_config.login_page_class(page)  # Creates LoginPage instance
login_page.navigate()  # Goes to login URL
login_page.accept_cookies()  # Clicks cookie banner
login_page.enter_username(test_data.get("username"))
login_page.enter_password(test_data.get("password"))
login_page.click_sign_in()
login_page.submit_login_form()

# Check if login successful
current_url = page.url
return "login" not in current_url.lower()
```

**13.8** Save session state (if login successful)
```python
if login_success:
    AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(session_file))  # Save cookies/localStorage to JSON
```

**13.9** Yield page to test
```python
yield page  # ← TEST EXECUTES HERE (BDD steps run)
```

**13.10** Cleanup (after test completes)
```python
page.close()
context.close()
```

**Objects created**:
- `context`: BrowserContext instance
- `page`: Page instance (this is what test functions receive)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 14: page fixture (backward compatibility wrapper)          │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `page(authenticated_page)`
**Line**: 368-375
**Action**: Simply returns authenticated_page
- Provides backward compatibility for tests using `page` instead of `authenticated_page`

**Returns**: Same `page` object from Step 13

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 15: Page Object fixtures (e.g., add_ach_instruction_page)  │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/ui_fixtures/page_fixtures.py`
**Function**: `add_ach_instruction_page(page)` (and others)
**Scope**: function
**Dependencies**: Requires `page` from Step 14

**Example**:
```python
@pytest.fixture
def add_ach_instruction_page(page):
    from pages.add_ach_instruction import AddAchInstruction
    return AddAchInstruction(page)
```

**Action**:
1. Imports page object class
2. Instantiates class with `page` object
3. Returns page object instance

**Objects created**: Page object instances (AddAchInstruction, AccountDetailPage, etc.)

---

### Phase 5: Test Execution

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 16: pytest_runtest_setup() hook                            │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_runtest_setup(item)`
**Line**: 166-170
**Action**:
1. Increments execution count: `item.execution_count += 1`
2. Records start time: `item.start_time = datetime.now()`

**Variables updated**: item.execution_count, item.start_time

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 17: BDD Scenario starts                                    │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/bdd/features/test_add_ach.py`
**Scenario**: Defined in `.feature` file, converted to test function by pytest-bdd

**Example scenario**:
```gherkin
Scenario: Add ACH instruction
    Given I am logged into the application
    When I navigate to account detail page for client "12345"
    And I add a new ACH instruction with routing "123456789" and account "987654321"
    Then the ACH instruction should be saved successfully
```

**Converted to**: `test_add_ach_instruction(page, add_ach_instruction_page, test_data)`

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 18: BDD STEP 1 - "Given I am logged into the application"  │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/bdd/steps/login_steps.py`
**Function**: Step definition decorated with `@given(...)`
**Line**: Find step matching pattern

**Step execution**:
```python
@given("I am logged into the application")
def logged_in(page):
    logger = get_allure_logger(__name__)
    logger.info("User already authenticated via session fixture")
    # No action needed - authenticated_page fixture handles login
```

**What happens**:
1. **get_allure_logger(__name__)** called
   - File: `utils/allure_logger.py`
   - Returns: AllureLogger instance for "tests.bdd.steps.login_steps"

2. **logger.info("...")** called
   - File: `utils/allure_logger.py`, method: `info()`
   - Action:
     - Logs to console via Python logging
     - Calls `allure.attach()` with message (because `attach_to_allure=True` by default)
     - Attaches text to Allure report

**Console output**:
```
2026-01-29 14:30:45 [    INFO] User already authenticated via session fixture
```

**Allure report**: Text attachment added with message

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 18.1: pytest_bdd_after_step() hook                         │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_bdd_after_step(request, feature, scenario, step, step_func)`
**Line**: 712-742
**Action**: Runs AFTER each BDD step completes

1. Check if screenshots enabled:
   ```python
   screenshot_enabled = os.getenv("SCREENSHOT_EACH_STEP", "false").lower() == "true"
   ```

2. Get page object from fixtures:
   ```python
   page = request.node.funcargs.get("page")
   ```

3. Check if step failed:
   ```python
   step_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
   ```

4. Take screenshot if enabled or step failed:
   ```python
   if screenshot_enabled or step_failed:
       screenshot = page.screenshot()
       status = "❌ FAILED" if step_failed else "✓"
       step_name = f"{step.keyword} {step.name}"
       allure.attach(
           screenshot,
           name=f"{status} {step_name}",
           attachment_type=allure.attachment_type.PNG,
       )
   ```

**Screenshot taken**: If SCREENSHOT_EACH_STEP=true, screenshot saved to Allure

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 19: BDD STEP 2 - "When I navigate to account detail..."    │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/bdd/steps/navigation_steps.py`
**Function**: Step definition for navigation

**Step execution**:
```python
@when('I navigate to account detail page for client "{client_id}"')
def navigate_to_account_detail(page, account_detail_page, client_id):
    logger = get_allure_logger(__name__)
    logger.info(f"Navigating to account detail for client: {client_id}")

    # Call page object method
    account_detail_page.navigate_to_client(client_id)
```

**Call chain**:
1. **get_allure_logger(__name__)** → Returns logger
2. **logger.info(...)** → Logs message + Allure attachment
3. **account_detail_page.navigate_to_client(client_id)** → Calls page object

**Page object execution**:
```python
# File: pages/account_detail_page.py
# Method: navigate_to_client(client_id)

def navigate_to_client(self, client_id):
    logger = get_allure_logger(__name__)
    logger.info(f"Searching for client: {client_id}")

    # Playwright actions
    self.page.goto(f"/clients/{client_id}")
    self.page.wait_for_load_state("domcontentloaded")

    logger.info("Account detail page loaded")
```

**Browser actions**:
1. `page.goto()` → Navigates browser to URL
2. `page.wait_for_load_state()` → Waits for page to load

**After step completes** → `pytest_bdd_after_step()` hook runs again (Step 18.1)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 20: BDD STEP 3 - "And I add a new ACH instruction..."      │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/bdd/steps/manage_instruction_steps.py`
**Function**: Step definition for adding ACH

**Step execution**:
```python
@when('I add a new ACH instruction with routing "{routing}" and account "{account}"')
def add_ach_instruction(page, add_ach_instruction_page, routing, account):
    logger = get_allure_logger(__name__)
    logger.info(f"Adding ACH instruction - Routing: {routing}, Account: {account}")

    # Call page object methods
    add_ach_instruction_page.click_add_instruction()
    add_ach_instruction_page.enter_routing_number(routing)
    add_ach_instruction_page.enter_account_number(account)
    add_ach_instruction_page.click_save()
```

**Page object execution**:
```python
# File: pages/add_ach_instruction.py

def click_add_instruction(self):
    logger = get_allure_logger(__name__)
    logger.info("Clicking add instruction button")
    self.page.locator("#add-instruction-btn").click()

def enter_routing_number(self, routing):
    logger = get_allure_logger(__name__)
    logger.info(f"Entering routing number: {routing}")
    self.page.locator("#routing-number").fill(routing)

def enter_account_number(self, account):
    logger = get_allure_logger(__name__)
    logger.info(f"Entering account number: {account}")
    self.page.locator("#account-number").fill(account)

def click_save(self):
    logger = get_allure_logger(__name__)
    logger.info("Clicking save button")
    self.page.locator("#save-btn").click()
```

**Browser actions**:
1. `.click()` → Clicks button
2. `.fill()` → Types text into input field
3. `.click()` → Clicks save button

**After step completes** → `pytest_bdd_after_step()` hook runs again

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 21: BDD STEP 4 - "Then the ACH instruction should be..."   │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/bdd/steps/common_steps.py` or `manage_instruction_steps.py`
**Function**: Assertion step

**Step execution**:
```python
@then("the ACH instruction should be saved successfully")
def verify_ach_saved(page):
    logger = get_allure_logger(__name__)
    logger.info("Verifying ACH instruction saved")

    # Playwright assertion
    success_message = page.locator(".success-message")
    assert success_message.is_visible(), "Success message not visible"

    logger.info("ACH instruction saved successfully")
```

**Browser actions**:
1. `.locator()` → Finds element
2. `.is_visible()` → Checks if element visible
3. `assert` → Python assertion (fails test if False)

**After step completes** → `pytest_bdd_after_step()` hook runs again

**All BDD steps completed** ✓

---

### Phase 6: Test Teardown

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 22: authenticated_page fixture cleanup                     │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `authenticated_page()` (after yield)
**Line**: 360-365
**Action**:
```python
page.close()     # Close page/tab
context.close()  # Close browser context
```

**Browser state**: Page closed, context closed (browser still running for next test)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 23: pytest_runtest_makereport() hook                       │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_runtest_makereport(item, call)`
**Line**: 754-806
**Action**: Runs during test teardown to generate report

**23.1** Flaky test detection (if test passed after retries)
```python
if call.when == "call":  # Actual test execution phase
    duration_ms = int((datetime.now() - item.start_time).total_seconds() * 1000)

    if call.excinfo is not None:
        item.failed_count += 1

    # Detect flaky: passed after failures
    if call.excinfo is None and item.execution_count > 1 and item.failed_count > 0:
        tracker = get_tracker()  # Get flaky test tracker
        tracker.record_flaky_test(
            test_name=item.nodeid,
            total_attempts=item.execution_count,
            failed_attempts=item.failed_count,
            final_status="passed",
            duration_ms=duration_ms
        )
```

**23.2** Screenshot on failure
```python
outcome = yield  # Get test result
rep = outcome.get_result()

if rep.when == "call" and rep.failed and "page" in item.funcargs:
    page = item.funcargs["page"]
    screenshot_bytes = page.screenshot()
    allure.attach(
        screenshot_bytes,
        name=f"screenshot-{item.name}",
        attachment_type=allure.attachment_type.PNG
    )
```

**Allure report**: Screenshot attached if test failed

---

### Phase 7: Session Teardown (After All Tests)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 24: browser fixture cleanup (pytest-playwright)            │
└─────────────────────────────────────────────────────────────────┘
```

**Plugin**: pytest-playwright
**Action**: Closes browser
- All contexts closed
- Browser process terminated
- Video files saved (if configured)

**Files created**:
- `reports/videos/test_add_ach.webm` (if video recording enabled)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 25: pytest_sessionfinish() hook                            │
└─────────────────────────────────────────────────────────────────┘
```

**File**: `tests/conftest.py`
**Function**: `pytest_sessionfinish(session, exitstatus)`
**Line**: 809-906
**Action**: Runs after ALL tests complete

**25.1** Push flaky test metrics to InfluxDB
```python
tracker = get_tracker()
summary = tracker.get_flaky_summary()

if summary["total_flaky_tests"] > 0:
    print(f"\n{'=' * 60}")
    print("⚠️  FLAKY TEST SUMMARY")
    print(f"Total Flaky Tests: {summary['total_flaky_tests']}")
    for test in summary["flaky_tests"]:
        print(f"  - {test['name']}: {test['failed']}/{test['attempts']}")
    print(f"{'=' * 60}\n")

    tracker.push_to_influxdb()  # Send metrics to InfluxDB
```

**25.2** Generate Allure HTML report automatically
```python
allure_results_dir = "reports/allure-results"
allure_report_dir = "reports/allure-report"

# Check if results exist
result_files = [f for f in os.listdir(allure_results_dir) if f.endswith("-result.json")]

if result_files:
    # Run allure generate command
    subprocess.run([
        "allure", "generate", allure_results_dir,
        "--clean", "--single-file",
        "-o", allure_report_dir
    ])

    # Create timestamped copy
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_index = f"index_{timestamp}.html"
    shutil.copy2("reports/allure-report/index.html",
                 f"reports/allure-report/{timestamped_index}")

    # Clean up old reports (keep last 10)
    # Print report location
    print(f"Report location: reports/allure-report/index.html")
```

**Files created**:
- `reports/allure-report/index.html`
- `reports/allure-report/index_2026-01-29_14-35-20.html`

**Console output**:
```
Allure report generated successfully!
Report location: C:\...\reports\allure-report
Main report: file:///C:/.../reports/allure-report/index.html
```

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 26: pytest exits, prints summary                           │
└─────────────────────────────────────────────────────────────────┘
```

**Action**: Pytest prints final summary
```
======================== test session starts =========================
platform win32 -- Python 3.11.0, pytest-8.0.0, pluggy-1.3.0
rootdir: C:\...\DM1TestAutomation
plugins: playwright-0.4.4, bdd-7.3.0, xdist-3.5.0, allure-pytest-2.13.0
collected 1 item

tests/bdd/features/test_add_ach.py::test_add_ach_instruction PASSED [100%]

========================= 1 passed in 12.34s =========================
```

**Exit code**: 0 (success) or 1 (failure)

---

## Complete Call Stack Visualization

### When BDD Step Executes: "When I add ACH instruction..."

```
pytest (main process)
  └─ tests/conftest.py::pytest_runtest_setup()
      └─ tests/bdd/features/test_add_ach.py::test_add_ach_instruction()
          ├─ Fixture resolution:
          │   ├─ tests/conftest.py::page() → authenticated_page()
          │   │   ├─ Fixture: browser (pytest-playwright)
          │   │   ├─ Fixture: test_data (data_fixtures.py)
          │   │   └─ Creates: Page object
          │   └─ tests/ui_fixtures/page_fixtures.py::add_ach_instruction_page()
          │       └─ Creates: AddAchInstruction(page)
          │
          └─ BDD Step execution:
              └─ tests/bdd/steps/manage_instruction_steps.py::add_ach_instruction()
                  ├─ utils/allure_logger.py::get_allure_logger(__name__)
                  │   └─ Returns: AllureLogger instance
                  │
                  ├─ allure_logger.info("Adding ACH...")
                  │   ├─ logging.Logger.info() → Console output
                  │   └─ allure.attach() → Allure report
                  │
                  └─ add_ach_instruction_page.click_add_instruction()
                      └─ pages/add_ach_instruction.py::click_add_instruction()
                          ├─ utils/allure_logger.py::get_allure_logger(__name__)
                          ├─ logger.info("Clicking add button...")
                          │   ├─ logging.Logger.info()
                          │   └─ allure.attach()
                          │
                          └─ self.page.locator("#add-btn").click()
                              └─ Playwright: Browser action (click button)
                                  └─ CDP command to Chrome DevTools Protocol
                                      └─ Browser: Button clicked

  └─ tests/conftest.py::pytest_bdd_after_step()
      └─ page.screenshot() if enabled
          └─ allure.attach(screenshot) → Allure report
```

---

## Execution Time Breakdown

| Phase | Time | Description |
|-------|------|-------------|
| Pytest init | 0.1s | Load config, plugins |
| Collection | 0.2s | Find tests, BDD scenarios |
| Session fixtures | 0.5s | Browser launch |
| Test fixtures | 2.0s | Login, session management |
| BDD steps | 8.0s | Actual test execution |
| Teardown | 0.5s | Close page, context |
| Report gen | 1.0s | Allure HTML generation |
| **TOTAL** | **12.3s** | Full test execution |

---

## Files Involved in Single Test Execution

### Configuration Files (Read)
1. `pyproject.toml` - Pytest config
2. `config/env.test11.yaml` - Environment config
3. `data/test_data.test11.csv` - Test data

### Python Files (Executed)
1. `tests/conftest.py` - Main configuration, hooks, fixtures
2. `tests/ui_fixtures/data_fixtures.py` - Test data fixture
3. `tests/ui_fixtures/page_fixtures.py` - Page object fixtures
4. `tests/bdd/features/test_add_ach.py` - Test file
5. `tests/bdd/steps/login_steps.py` - Login step definitions
6. `tests/bdd/steps/navigation_steps.py` - Navigation step definitions
7. `tests/bdd/steps/manage_instruction_steps.py` - ACH step definitions
8. `tests/bdd/steps/common_steps.py` - Common step definitions
9. `pages/login_page.py` - Login page object
10. `pages/account_detail_page.py` - Account detail page object
11. `pages/add_ach_instruction.py` - ACH instruction page object
12. `utils/allure_logger.py` - Logging utility
13. `utils/settings.py` - Settings management
14. `utils/flaky_test_tracker.py` - Flaky test detection

### Files Created (Output)
1. `reports/allure-results/*.json` - Allure test results
2. `reports/allure-report/index.html` - Allure HTML report
3. `reports/videos/test_add_ach.webm` - Video recording
4. `reports/pytest_report.html` - Pytest HTML report
5. `reports/junit/junit-report.xml` - JUnit XML
6. `tests/.auth/ewm_testuser_master.json` - Session state

---

## Key Takeaways

1. **Browser launches once** in pytest-playwright plugin (Step 12)
2. **Login happens once per test** via authenticated_page fixture (Step 13)
3. **Each BDD step** triggers step function → page object → Playwright action (Steps 18-21)
4. **Screenshots taken automatically** after each step via pytest_bdd_after_step hook (Step 18.1)
5. **Allure report generated automatically** at session end (Step 25)
6. **Flaky tests detected** and tracked via pytest_runtest_makereport hook (Step 23)

---

**Last Updated**: January 29, 2026
