# Exact Execution Order - Fixture Dependency Chain

This document shows the PRECISE execution order starting from your conftest.py line 173, tracing through pytest-playwright plugin.

---

## Starting Point: Test Execution Begins

When you run: `pytest tests/bdd/features/test_add_ach.py -v`

pytest needs to resolve fixtures for your test function, which might look like:
```python
def test_add_ach_instruction(page, add_ach_instruction_page, test_data):
    # test code
```

---

## Execution Order - Line by Line

### Step 1: Pytest Analyzes Fixture Dependencies

**Action**: pytest builds dependency graph
```
test_add_ach_instruction needs:
  └─ page
      └─ context (pytest-playwright)
          └─ browser (pytest-playwright)
              └─ launch_browser (pytest-playwright)
                  └─ browser_type (pytest-playwright)
                      └─ playwright (pytest-playwright)
                  └─ browser_type_launch_args (pytest-playwright)
          └─ browser_context_args (pytest-playwright + YOUR OVERRIDE)
```

pytest resolves fixtures in **dependency order** (deepest first)

---

### Step 2: playwright fixture (session scope)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 196-199

```python
@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    pw = sync_playwright().start()  # ← LINE 197 EXECUTES
    yield pw
    pw.stop()
```

**Execution**:
1. Line 197: `sync_playwright().start()` - Starts Playwright sync API
2. This launches playwright server process
3. Returns `Playwright` object with `.chromium`, `.firefox`, `.webkit` attributes

**Status**: Playwright server running ✓

---

### Step 3: browser_name fixture (from parametrization)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 62-65

```python
def pytest_generate_tests(metafunc: Any) -> None:
    if "browser_name" in metafunc.fixturenames:
        browsers = metafunc.config.option.browser or ["chromium"]  # ← LINE 64
        metafunc.parametrize("browser_name", browsers, scope="session")
```

**Execution**:
- Line 64: Reads `--browser` CLI option or defaults to `["chromium"]`
- Creates parametrized fixture: `browser_name = "chromium"`

**Value**: `browser_name = "chromium"`

---

### Step 4: browser_type fixture (session scope)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 202-203

```python
@pytest.fixture(scope="session")
def browser_type(playwright: Playwright, browser_name: str) -> BrowserType:
    return getattr(playwright, browser_name)  # ← LINE 203 EXECUTES
```

**Execution**:
1. Depends on: `playwright` (Step 2) and `browser_name` (Step 3)
2. Line 203: `getattr(playwright, "chromium")` - Gets ChromiumBrowserType
3. Returns BrowserType object

**Returns**: `playwright.chromium` (BrowserType instance)

---

### Step 5: browser_type_launch_args fixture (session scope)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 129-144

```python
@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: Any) -> Dict:
    launch_options = {}  # ← LINE 130
    headed_option = pytestconfig.getoption("--headed")  # ← LINE 131
    if headed_option:  # ← LINE 132
        launch_options["headless"] = False
    elif VSCODE_PYTHON_EXTENSION_ID in sys.argv[0] and _is_debugger_attached():
        launch_options["headless"] = False
    browser_channel_option = pytestconfig.getoption("--browser-channel")  # ← LINE 137
    if browser_channel_option:
        launch_options["channel"] = browser_channel_option
    slowmo_option = pytestconfig.getoption("--slowmo")  # ← LINE 140
    if slowmo_option:
        launch_options["slow_mo"] = slowmo_option
    return launch_options  # ← LINE 143
```

**Execution**:
1. Line 130: Initialize empty dict
2. Line 131: Check `--headed` flag (False if not provided)
3. Line 132: If not headed, check VSCode debugger (usually False)
4. Line 137: Check `--browser-channel` (usually None)
5. Line 140: Check `--slowmo` (usually None)
6. Line 143: Return `{}` (empty dict = default headless chromium)

**Returns**: `{}` (or `{"headless": False}` if --headed flag used)

---

### Step 6: launch_browser fixture (session scope)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 206-214

```python
@pytest.fixture(scope="session")
def launch_browser(
    browser_type_launch_args: Dict,
    browser_type: BrowserType,
) -> Callable[..., Browser]:
    def launch(**kwargs: Dict) -> Browser:  # ← LINE 211 DEFINES FUNCTION
        launch_options = {**browser_type_launch_args, **kwargs}  # ← LINE 212
        browser = browser_type.launch(**launch_options)  # ← LINE 213
        return browser

    return launch  # ← LINE 216 RETURNS FUNCTION (NOT CALLED YET)
```

**Execution**:
1. Depends on: `browser_type_launch_args` (Step 5) and `browser_type` (Step 4)
2. Line 211-214: Defines inner function `launch()`
3. Line 216: Returns function reference (NOT executed yet)

**Returns**: Function object `launch` (will be called in next step)

---

### Step 7: browser fixture (session scope) - BROWSER LAUNCHES HERE 🚀

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 217-226

```python
@pytest.fixture(scope="session")
def browser(launch_browser: Callable[[], Browser]) -> Generator[Browser, None, None]:
    browser = launch_browser()  # ← LINE 218 EXECUTES → CALLS launch() from Step 6
    yield browser  # ← LINE 219 YIELDS TO TESTS
    browser.close()
    try:
        artifacts_folder.cleanup()
    except (PermissionError, NotADirectoryError):
        pass
```

**Execution**:
1. Depends on: `launch_browser` (Step 6)
2. **Line 218**: `launch_browser()` calls the `launch()` function from Step 6
   - This executes Line 212-213 from Step 6:
     ```python
     launch_options = {**browser_type_launch_args, **kwargs}  # {}
     browser = browser_type.launch(**launch_options)  # ← BROWSER LAUNCHES HERE!
     ```
   - `browser_type.launch({})` starts Chromium browser process
   - Browser executable launched (headless by default)

3. Line 219: `yield browser` - Pauses here, returns Browser object to dependent fixtures

**Returns**: `Browser` instance (Chromium running in background)

**THIS IS WHERE THE BROWSER ACTUALLY STARTS** 🎯

---

### Step 8: browser_context_args fixture (session scope) - DUAL DEFINITION!

**IMPORTANT**: This fixture exists in TWO places:

#### 8a. pytest-playwright's DEFAULT definition

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 173-188

```python
@pytest.fixture(scope="session")
def browser_context_args(
    pytestconfig: Any,
    playwright: Playwright,
    device: Optional[str],
    base_url: Optional[str],
) -> Dict:
    context_args = {}  # ← LINE 179
    if device:  # ← LINE 180
        context_args.update(playwright.devices[device])
    if base_url:  # ← LINE 182
        context_args["base_url"] = base_url

    video_option = pytestconfig.getoption("--video")  # ← LINE 184
    capture_video = video_option in ["on", "retain-on-failure"]  # ← LINE 185
    if capture_video:  # ← LINE 186
        context_args["record_video_dir"] = artifacts_folder.name

    return context_args  # ← LINE 188
```

**BUT** this is OVERRIDDEN by your conftest.py!

#### 8b. YOUR OVERRIDE in conftest.py

**File**: `tests/conftest.py`
**Line**: 172-205

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):  # ← LINE 173
    """
    Configure browser context with worker-specific output directories for parallel execution
    """
    import os  # ← LINE 177

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")  # ← LINE 180

    # Make output directories worker-specific to avoid conflicts
    if worker_id != "master":  # ← LINE 183
        record_video_dir = f"reports/videos/{worker_id}"  # ← LINE 184

    else:
        record_video_dir = "reports/videos"  # ← LINE 187

    # Base browser context args (from pytest-playwright)
    context_args = {
        **browser_context_args,  # ← LINE 200 - UNPACKS DEFAULT FROM 8a
        "ignore_https_errors": True,  # ← LINE 201 - ADDS YOUR CUSTOM SETTING
    }

    # Add video recording if configured
    if record_video_dir:  # ← LINE 204
        context_args["record_video_dir"] = record_video_dir  # ← LINE 205

    return context_args  # ← LINE 207
```

**EXECUTION ORDER**:

1. **pytest-playwright's browser_context_args (8a) executes FIRST** (as dependency)
   - Line 179-188 in pytest_playwright.py
   - Returns dict (might include `record_video_dir` if `--video` flag used)
   - This is passed as parameter `browser_context_args` to your fixture

2. **YOUR browser_context_args (8b) executes SECOND** (overrides)
   - Line 173: Receives default args as first parameter
   - Line 177: Import os
   - Line 180: Get worker ID (e.g., "master" or "gw0")
   - Line 183-187: Determine video directory based on worker
   - Line 200: Unpack default args using spread operator `**browser_context_args`
   - Line 201: Add `ignore_https_errors: True`
   - Line 204-205: Override video directory with worker-specific path
   - Line 207: Return merged dict

**Returns**:
```python
{
    "record_video_dir": "reports/videos",  # Your custom path
    "ignore_https_errors": True,           # Your custom setting
    # Plus any defaults from pytest-playwright (device, base_url if set)
}
```

---

### Step 9: context fixture (function scope)

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 229-307

```python
@pytest.fixture
def context(
    browser: Browser,
    browser_context_args: Dict,
    pytestconfig: Any,
    request: pytest.FixtureRequest,
) -> Generator[BrowserContext, None, None]:
    pages: List[Page] = []  # ← LINE 235

    browser_context_args = browser_context_args.copy()  # ← LINE 237
    context_args_marker = next(request.node.iter_markers("browser_context_args"), None)  # ← LINE 238
    additional_context_args = context_args_marker.kwargs if context_args_marker else {}  # ← LINE 239
    browser_context_args.update(additional_context_args)  # ← LINE 240

    context = browser.new_context(**browser_context_args)  # ← LINE 242 CREATES CONTEXT!
    context.on("page", lambda page: pages.append(page))  # ← LINE 243

    tracing_option = pytestconfig.getoption("--tracing")  # ← LINE 245
    capture_trace = tracing_option in ["on", "retain-on-failure"]  # ← LINE 246
    if capture_trace:  # ← LINE 247
        context.tracing.start(
            title=slugify(request.node.nodeid),
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    yield context  # ← LINE 254 YIELDS TO TEST

    # ... teardown code after test (lines 256-307)
```

**Execution**:
1. Depends on: `browser` (Step 7) and `browser_context_args` (Step 8)
2. Line 235: Initialize empty pages list
3. Line 237: Copy browser_context_args dict
4. Line 238-239: Check for test-specific `@pytest.mark.browser_context_args()` marker
5. Line 240: Merge any marker kwargs into context_args
6. **Line 242**: `browser.new_context(**browser_context_args)`
   - Creates new browser context with your settings:
     ```python
     browser.new_context(
         record_video_dir="reports/videos",
         ignore_https_errors=True
     )
     ```
   - This creates an isolated browser session (cookies, localStorage, etc.)
7. Line 243: Register page event handler to track pages
8. Line 245-252: Start tracing if `--tracing` flag enabled
9. Line 254: `yield context` - Pauses, returns BrowserContext to dependent fixtures

**Returns**: `BrowserContext` instance

---

### Step 10: page fixture (function scope) - FROM PYTEST-PLAYWRIGHT

**File**: `.venv/Lib/site-packages/pytest_playwright/pytest_playwright.py`
**Line**: 318-320

```python
@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()  # ← LINE 319 CREATES PAGE/TAB
    yield page
```

**Execution**:
1. Depends on: `context` (Step 9)
2. Line 319: `context.new_page()` - Creates new page (tab) in context
3. Line 320: `yield page` - Returns Page object

**Returns**: `Page` instance (blank page/tab)

**BUT WAIT** - Your conftest.py has another fixture that OVERRIDES this!

---

### Step 11: authenticated_page fixture (function scope) - YOUR OVERRIDE

**File**: `tests/conftest.py`
**Line**: 284-365

```python
@pytest.fixture
def authenticated_page(browser, test_data, request):  # ← LINE 284
    import os
    from datetime import datetime

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")  # ← LINE 289

    # Get app from marker or use default
    app_marker = request.node.get_closest_marker("app")  # ← LINE 292
    app_name = app_marker.args[0] if app_marker else "ewm"  # ← LINE 293

    # Get app configuration
    app_config = APP_CONFIGS[app_name]  # ← LINE 296 (loaded in module init)
    username = test_data.get("username", "default_user")  # ← LINE 301
    session_file = _get_session_file(username, app_name, worker_id)  # ← LINE 302

    # Check if session file exists and is valid
    if session_file.exists():  # ← LINE 310
        # ... session age check (lines 311-316)

        # Load saved session
        context = browser.new_context(  # ← LINE 320 CREATES CONTEXT WITH SESSION!
            storage_state=str(session_file),
            ignore_https_errors=True
        )
        page = context.new_page()  # ← LINE 323 CREATES PAGE
        page.goto(app_config.home_url, timeout=30000)  # ← LINE 326 NAVIGATES!
        page.wait_for_load_state("domcontentloaded", timeout=10000)  # ← LINE 327

        # Verify session still valid
        if "login" not in page.url.lower():  # ← LINE 330
            yield page  # ← LINE 332 RETURNS AUTHENTICATED PAGE
            page.close()
            context.close()
            return

    # No session or expired - perform login
    context = browser.new_context(ignore_https_errors=True)  # ← LINE 345
    page = context.new_page()  # ← LINE 346

    login_success = _perform_login(page, app_config, test_data)  # ← LINE 348 LOGS IN

    if login_success:  # ← LINE 350
        # Save session
        context.storage_state(path=str(session_file))  # ← LINE 353

    yield page  # ← LINE 356 RETURNS PAGE TO TEST

    page.close()  # ← LINE 358 (after test)
    context.close()
```

**Execution**:
1. Depends on: `browser` (Step 7) and `test_data` (loaded from CSV)
2. Line 289: Get worker ID
3. Line 292-293: Get app name from test marker
4. Line 296: Get app config (login_url, home_url, etc.)
5. Line 301-302: Get username and session file path

**Path A - Session exists** (subsequent test runs):
- Line 320: Create context with saved session (cookies/localStorage)
- Line 323: Create page
- Line 326: Navigate to home URL
- Line 327: Wait for page load
- Line 330-332: If URL doesn't contain "login", yield page (AUTHENTICATED)

**Path B - No session** (first run):
- Line 345: Create fresh context
- Line 346: Create page
- Line 348: Call `_perform_login()` which:
  - Navigates to login page
  - Fills username/password
  - Clicks sign in
  - Waits for redirect
- Line 353: Save session state to JSON file
- Line 356: Yield page (AUTHENTICATED)

**Returns**: `Page` instance (authenticated and ready to use)

---

### Step 12: page fixture (function scope) - YOUR WRAPPER

**File**: `tests/conftest.py`
**Line**: 368-375

```python
@pytest.fixture
def page(authenticated_page):  # ← LINE 369
    """
    Default page fixture - uses 'ewm' app for backward compatibility.
    """
    return authenticated_page  # ← LINE 374
```

**Execution**:
1. Depends on: `authenticated_page` (Step 11)
2. Line 374: Simply returns the authenticated page

**Returns**: Same `Page` instance from Step 11

**This is what your test receives!**

---

### Step 13: Page Object Fixtures (e.g., add_ach_instruction_page)

**File**: `tests/ui_fixtures/page_fixtures.py`

```python
@pytest.fixture
def add_ach_instruction_page(page):
    from pages.add_ach_instruction import AddAchInstruction
    return AddAchInstruction(page)  # ← INSTANTIATES PAGE OBJECT
```

**Execution**:
1. Depends on: `page` (Step 12)
2. Imports page object class
3. Creates instance with page object

**Returns**: Page object instance

---

### Step 14: TEST EXECUTES

**File**: `tests/bdd/features/test_add_ach.py`

```python
def test_add_ach_instruction(page, add_ach_instruction_page, test_data):
    # ← ALL FIXTURES RESOLVED, TEST RUNS HERE
```

**Execution**: Your BDD steps execute with:
- `page`: Authenticated Page object (from Step 12)
- `add_ach_instruction_page`: Page object wrapper (from Step 13)
- `test_data`: Test data dict (from CSV)

---

## Complete Execution Timeline

```
Time  | Step | File                           | Line | Action
------|------|--------------------------------|------|---------------------------
0.0s  | 1    | pytest                         | -    | Analyze dependencies
0.1s  | 2    | pytest_playwright.py           | 197  | sync_playwright().start()
0.2s  | 3    | pytest_playwright.py           | 64   | browser_name = "chromium"
0.3s  | 4    | pytest_playwright.py           | 203  | getattr(playwright, "chromium")
0.4s  | 5    | pytest_playwright.py           | 130  | browser_type_launch_args = {}
0.5s  | 6    | pytest_playwright.py           | 216  | Return launch function
0.6s  | 7    | pytest_playwright.py           | 218  | browser_type.launch() 🚀 BROWSER STARTS
1.5s  | 8a   | pytest_playwright.py           | 179  | Default browser_context_args
1.6s  | 8b   | conftest.py                    | 173  | YOUR browser_context_args override
1.7s  | 9    | pytest_playwright.py           | 242  | browser.new_context()
1.8s  | 10   | pytest_playwright.py           | 319  | context.new_page() (not used)
2.0s  | 11   | conftest.py                    | 320  | YOUR browser.new_context() + login
4.0s  | 12   | conftest.py                    | 374  | Return authenticated_page
4.1s  | 13   | page_fixtures.py               | -    | Create page objects
4.2s  | 14   | test_add_ach.py                | -    | TEST RUNS ✓
```

---

## Key Insights

1. **conftest.py line 173 is NOT where browser starts**
   - It only CONFIGURES browser context settings
   - Actual browser launch is at pytest_playwright.py line 218

2. **Fixture override mechanism**:
   - pytest-playwright defines `browser_context_args` (default)
   - Your conftest.py OVERRIDES it by accepting default as parameter
   - Your version executes AFTER default, merges settings

3. **Two context creations**:
   - pytest_playwright.py line 242: Creates context (not used by your tests)
   - conftest.py line 320/345: Creates context with session state (used by tests)

4. **Execution order is dependency-driven**:
   - pytest resolves deepest dependencies first (playwright → browser → context → page)
   - Session-scoped fixtures run once
   - Function-scoped fixtures run per test

---

## Answering Your Question

**"from conftest.py line 173...navigates to pytest-playwright.py line 173"**

**NOT EXACTLY**. Here's what actually happens:

1. conftest.py line 173 (`browser_context_args`) needs pytest-playwright's `browser_context_args` as dependency
2. pytest-playwright.py line 173 executes FIRST (creates default args)
3. Then conftest.py line 173 executes (receives default, adds your overrides)
4. Next: pytest-playwright.py line 242 (`browser.new_context()`) uses your merged args
5. Then: conftest.py line 320 (`browser.new_context()`) creates YOUR context with session

**Execution sequence**:
```
pytest_playwright.py line 173 (default args)
    ↓
conftest.py line 173 (merge with your overrides)
    ↓
pytest_playwright.py line 242 (create context - not used)
    ↓
conftest.py line 320 (create YOUR context with session)
    ↓
conftest.py line 356 (yield page to test)
```

---

**Last Updated**: January 29, 2026
