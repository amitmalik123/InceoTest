"""
Global Test Configuration

This conftest.py contains ONLY:
- Pytest hooks (configure, collection, execution, reporting)
- Global test infrastructure

Fixture Organization:
- Page object fixtures: tests/fixtures/page_fixtures.py
- Test data fixtures: tests/fixtures/data_fixtures.py
- Database fixtures: tests/fixtures/db_fixtures.py
- Authentication fixtures: tests/fixtures/auth_fixtures.py
- Browser fixtures: tests/fixtures/browser_fixtures.py
- BDD hooks: tests/fixtures/hooks_fixtures.py
- Assertion utilities: tests/fixtures/assertion_fixtures.py
"""

import os
import subprocess
from collections.abc import Generator
from pathlib import Path

import sys
import getpass
import os

import logging


import allure
import pytest
from playwright.sync_api import Page
import csv

# Import all STP fixtures to make them available to all tests
from fixtures.STP import *  # noqa: F401, F403
from config.settings import get_settings
from utils.allure_logger import enable_step_screenshots
from utils.excel_utils import excel_report
from utils.flaky_test_tracker import get_tracker
from utils.settings import Settings
from pages.stp.shared.login_page import LoginPage

# Setup logger
logger = logging.getLogger(__name__)
# Ensure applicationqe root is in path for STP monorepo structure
_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_APP_ROOT))


env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=env)

# Use __file__-anchored path so it resolves correctly regardless of the
# working directory pytest was launched from (important on CI/CD agents).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_PATH = str(_PROJECT_ROOT / "downloads" / "ACH PDF")

AUTH_STATE_DIR = Path("tests/.auth")

@pytest.fixture(scope="session")
def test_environment(request):
    """Provide the test environment as a fixture."""
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Launch browser in headed mode with a maximized window."""
    return {
        **browser_type_launch_args,
        "headless": False,
        "args": [
            "--start-maximized",
            "--disable-features=Translate",  # Disable translation prompts
        ],
    }


@pytest.fixture(scope="session")
def all_test_data():
    """Load ALL test data rows from CSV (one row per role/user)"""
    csv_path = settings.test_data_csv
    data_rows = []
    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data_rows.append(row)
    return data_rows


@pytest.fixture(scope="function")
def test_data(all_test_data, request):
    """Select a single test data row from CSV by role, or default to first row."""
    role = getattr(request, "param", None)
    if role:
        for row in all_test_data:
            if row.get("role") == role:
                return row
        raise ValueError(f"Role '{role}' not found in test data CSV")
    return all_test_data[0] if all_test_data else {}


@pytest.fixture
def test_context(test_data):
    """Context dictionary to share test data and state across BDD steps."""
    return {"test_data": test_data}


@pytest.fixture(scope="session", autouse=True)
def setup_all_sessions(browser, all_test_data, request):
    """
    Pre-create session files ONLY for roles used in the current test run.
    For BDD tests: Skips auto-creation (roles are loaded dynamically in steps).
    For parametrized tests: Creates sessions for detected roles.
    Autouse=True means it runs automatically before any tests.
    """
    from datetime import datetime
    
    AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect unique roles from the test session
    roles_to_create = set()
    
    if hasattr(request.session, 'items'):
        for item in request.session.items:
            # Method 1: Check callspec params (pytest parametrize)
            if hasattr(item, 'callspec') and hasattr(item.callspec, 'params'):
                if 'role' in item.callspec.params:
                    role = item.callspec.params['role']
                    roles_to_create.add(role)
    
    # For BDD tests, skip auto-session creation (roles are loaded dynamically)
    if not roles_to_create:
        logger.info("[SESSION SETUP] BDD test detected - skipping auto-session creation")
        logger.info("[SESSION SETUP] Sessions will be created on-demand for efficiency")
        yield  # Still need to yield even if skipping
        return
    
    print(f"\n{'=' * 60}")
    print(f"[SESSION SETUP] Pre-creating sessions for roles: {sorted(roles_to_create)}")
    print(f"{'=' * 60}")
    
    created_sessions = []
    
    for test_data_row in all_test_data:
        role = test_data_row.get("role", "unknown")
        
        # Skip roles not in the test run
        if role not in roles_to_create:
            continue
            
        username = test_data_row.get("username", "unknown")
        password = test_data_row.get("password", "")
        
        # Determine navigation type based on role
        # Roles that require new navigation: manage_bene, secondary_login, etc.
        NEW_NAV_ROLES = ["manage_bene", "secondary_login"]
        use_new_nav = role in NEW_NAV_ROLES
        
        # Use role-specific session filename to avoid conflicts when same username has multiple roles
        session_file = AUTH_STATE_DIR / f"{username}_{role}.json"
        
        # Skip if session already exists and is fresh
        if session_file.exists():
            file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
            file_age_hours = file_age.total_seconds() / 3600
            if file_age_hours < 8:  # 8 hour TTL
                print(f"[SESSION SETUP] ✓ Session exists for {username} (role: {role})")
                created_sessions.append((username, role, False))
                continue
            else:
                print(f"[SESSION SETUP] Session expired for {username}, recreating...")
                session_file.unlink()
        
        # Create new session
        try:
            nav_type = "new nav" if use_new_nav else "standard"
            print(f"[SESSION SETUP] Creating session for {username} (role: {role}, nav: {nav_type})...")
            
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            # Login
            login_page = LoginPage(page)
            if use_new_nav:
                login_page.navigate_to_new_nav()
            else:
                login_page.navigate()
            login_page.accept_cookies()
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_sign_in()
            login_page.submit_login_form()
            
            # Check if login successful
            current_url = page.url
            if "login" not in current_url.lower():
                # Save session
                context.storage_state(path=str(session_file))
                print(f"[SESSION SETUP] ✓ Session saved: {username}")
                created_sessions.append((username, role, True))
            else:
                print(f"[SESSION SETUP] ✗ Login failed for {username}")
                created_sessions.append((username, role, False))
            
            page.close()
            context.close()
            
        except Exception as e:
            print(f"[SESSION SETUP] ✗ Error creating session for {username}: {e}")
            created_sessions.append((username, role, False))
    
    print(f"{'=' * 60}")
    print(f"[SESSION SETUP] Summary:")
    for username, role, success in created_sessions:
        status = "✓" if success else "✗"
        print(f"  {status} {username} (role: {role})")
    print(f"{'=' * 60}\n")
    
    yield


# Pytest configuration hooks
def pytest_addoption(parser) -> None:
    """Add custom command-line options"""
    parser.addoption(
        "--env",
        action="store",
        default="test11",
        help="Specify the test environment (e.g., test01, test11, prod). Default is test11.",
    )
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step (can be slow, use for debugging)",
    )


def pytest_configure(config) -> None:
    """Register custom markers and configure retry behavior"""
    config.addinivalue_line("markers", "env(name): mark test to run only on specific environment")
    config.addinivalue_line("markers", "performance: mark test for performance monitoring")
    config.addinivalue_line("markers", "lighthouse: mark test for Lighthouse audit")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "add_ach: mark test as add ACH flow")
    config.addinivalue_line("markers", "critical: mark test as critical")
    config.addinivalue_line("markers", "FullRegression: mark test for full regression")
    config.addinivalue_line("markers", "CancelSWP: mark test for Cancel SWP flow")
    config.addinivalue_line(
        "markers", "app(name): mark test to run with specific application (default: ewm)"
    )

    # Configure step screenshots - Priority: CLI > ENV VAR > CONFIG FILE
    settings_instance = get_settings()
    screenshot_each_step = (
        config.getoption("--screenshot-each-step", default=False)
        or os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes", "on")
        or settings_instance.screenshot_each_step
    )
    enable_step_screenshots(screenshot_each_step)

    # Print screenshot configuration
    status = "ENABLED for ALL steps" if screenshot_each_step else "ENABLED on failure only"
    print(f"\n{'=' * 60}")
    print(f"Step Screenshots: {status}")
    print(f"{'=' * 60}")

    # Enable automatic reruns for flaky test detection
    # This can be overridden with --reruns CLI argument
    # Skip reruns if --pdb is enabled (debug mode)
    if not config.option.reruns and not config.option.usepdb:
        config.option.reruns = 1  # Retry failed tests up to 1 time
        config.option.reruns_delay = 1  # 1 second delay between retries


def pytest_sessionstart(session) -> None:
    """
    Hook that runs before test session starts.
    Clears old Allure results, videos, and traces to ensure fresh artifacts for each run.
    Only the controller (or single-process run) performs cleanup — workers skip it.
    """
    # In xdist, workers skip cleanup to avoid racing with other workers
    if hasattr(session.config, "workerinput"):
        return

    import shutil

    from utils.download_utils import _get_default_download_dir

    dirs_to_clean = [
        "reports/allure-results",
        "reports/videos",
        "reports/traces",
        _get_default_download_dir(),
    ]

    files_to_clean = [
        "reports/network_errors_*.log",  # Worker-isolated log files
    ]

    # Reset Excel report collector for this session
    excel_report.clear_test_results()

    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                print(f"\nCleared old artifacts from {dir_path}")
            except Exception as e:
                print(f"\nWarning: Failed to clear {dir_path}: {e}")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"\nCreated directory: {dir_path}")

    for file_pattern in files_to_clean:
        import glob as _glob

        matched = _glob.glob(file_pattern)
        for file_path in matched:
            try:
                os.remove(file_path)
                print(f"\nCleared old log: {file_path}")
            except Exception as e:
                print(f"\nWarning: Failed to clear {file_path}: {e}")


def pytest_bdd_apply_tag(tag, function):
    """Handle @prod_order_N tags from PROD feature files.

    Stores the order number on the test function instead of registering
    a real pytest marker, so --strict-markers is not triggered.
    """
    if tag.startswith("prod_order_"):
        suffix = tag[len("prod_order_"):]
        if suffix.isdigit():
            function.__prod_order__ = int(suffix)
            return True  # handled — do NOT create a pytest marker
    return None  # let pytest-bdd handle all other tags normally


def pytest_collection_modifyitems(config, items) -> None:  # noqa: C901
    """
    Consolidated hook for test collection modification.

    Handles:
    - Environment markers
    - Retry tracking initialization
    - Parallel execution (xdist) grouping
    - Slow test detection
    - PROD scenario execution order (@prod_order_N tags)
    """
    current_env = get_settings().env
    available_apps = set(get_settings().get_available_apps())


    for item in items:
        # 1. Initialize retry tracking for flaky test detection
        item.execution_count = 0
        item.failed_count = 0
        item.start_time = None

        # 1b. Auto-map feature file tags to @pytest.mark.app()
        # If a scenario is tagged @crm, @ewm, etc. and that tag matches
        # a configured app name, add the app marker automatically.
        if not item.get_closest_marker("app"):
            for mark in item.iter_markers():
                if mark.name in available_apps:
                    item.add_marker(pytest.mark.app(mark.name))
                    break

        # 2. Add environment markers
        if current_env == "test11":
            item.add_marker(pytest.mark.test11)
        elif current_env == "test12":
            item.add_marker(pytest.mark.test12)
        elif current_env == "silo":
            item.add_marker(pytest.mark.silo)
        elif current_env == "prod":
            item.add_marker(pytest.mark.prod)

        # 3. Auto-assign xdist groups for parallel execution
        # Skip if test is marked as serial (must run alone)
        if "serial" not in [mark.name for mark in item.iter_markers()]:
            # Determine group based on test characteristics
            test_name = item.nodeid.lower()

            if "login" in test_name or "auth" in test_name:
                group = "auth"
            elif "api" in test_name:
                group = "api"
            elif "ui" in test_name:
                group = "ui"
            elif "database" in test_name or "db" in test_name:
                group = "database"
            else:
                group = "default"

            # Add xdist_group marker if not already present
            if not any(mark.name == "xdist_group" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.xdist_group(group))

        # 4. Mark slow tests (parametrized tests with many parameters)
        if hasattr(item, "callspec") and item.callspec and len(item.callspec.params) > 5:
            item.add_marker(pytest.mark.slow)

    # 5. Sort PROD scenarios by @prod_order_N tag
    prod_items = [i for i in items if any(m.name == "prod" for m in i.iter_markers())]
    non_prod_items = [i for i in items if i not in prod_items]
    prod_items.sort(key=lambda i: getattr(getattr(i, "function", None), "__prod_order__", 999))
    items[:] = non_prod_items + prod_items


def pytest_runtest_setup(item) -> None:
    """Called before each test execution (including retries)"""
    from datetime import datetime

    item.execution_count += 1
    item.start_time = datetime.now()


# Playwright configuration fixtures
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments to disable PDF viewer"""

    return {
        **browser_type_launch_args,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-pdf-viewer",
            "--disable-features=PdfViewerPlugin",
            "--disable-features=PluginPowerSaver",
        ]
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    context_args = {
        **browser_context_args,
        "ignore_https_errors": True,

        "no_viewport": True,

        "accept_downloads": True,
        "viewport": {"width": 1920, "height": 1080},
    }

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    if worker_id != "master":
        record_video_dir = f"reports/videos/{worker_id}"
    else:
        record_video_dir = "reports/videos"

    if record_video_dir:
        context_args["record_video_dir"] = record_video_dir

    return context_args
    


@pytest.fixture
def download_handler(page: Page):
   
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    
    downloads = []
    
    def handle_download(download):
        """Handle download event and save to custom location"""
        file_path = os.path.join(DOWNLOAD_PATH, download.suggested_filename)
        download.save_as(file_path)
        downloads.append(file_path)
    
    page.on("download", handle_download)
    
    yield {
        "download_path": DOWNLOAD_PATH,
        "downloads": downloads

    }


# Session Storage - works WITH existing login steps
@pytest.fixture
def page(context, browser, test_context, request):

    import os
    from datetime import datetime

    # Get worker ID for parallel execution support
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Try to get test data from test_context first (BDD role-based loading)
    # Fall back to test_data fixture if not available
    if "test_data" in test_context:
        test_data = test_context["test_data"]
        print(f"[SESSION] Using test data from test_context (role-based)")
    else:
        # Fallback for non-BDD tests - this shouldn't happen in BDD tests
        print(f"[SESSION] WARNING: test_context['test_data'] not found, using default")
        test_data = {}

    username = test_data.get("username", "default_user")
    current_role = test_data.get("role", "default")

    # Make session file role-specific AND worker-specific to avoid conflicts
    # Same username can have different roles with different navigation URLs
    if worker_id != "master":
        session_file = AUTH_STATE_DIR / f"{username}_{current_role}_{worker_id}.json"
    else:
        session_file = AUTH_STATE_DIR / f"{username}_{current_role}.json"

    print(f"\n{'=' * 60}")
    print("[SESSION DEBUG] page fixture called")
    print(f"[SESSION DEBUG] Worker ID: {worker_id}")
    print(f"[SESSION DEBUG] Username: {username}")
    print(f"[SESSION DEBUG] Session file path: {session_file}")
    print(f"[SESSION DEBUG] Session file exists: {session_file.exists()}")

    # Check if session is too old (expired)
    session_max_age_hours = 8
    if session_file.exists():
        file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
        file_age_hours = file_age.total_seconds() / 3600
        print(f"[SESSION DEBUG] Session file age: {file_age_hours:.1f} hours")

        if file_age_hours > session_max_age_hours:
            print(f"[SESSION DEBUG] Session is too old (>{session_max_age_hours}h), deleting...")
            session_file.unlink()
            print("[SESSION DEBUG] Deleted stale session file")

    print(f"{'=' * 60}")

    # Check if we have saved session for this user
    if session_file.exists():
        print(f"\n[SESSION] Loading saved session for: {username}")
        # Create new context with saved session
        context_with_session = browser.new_context(
            storage_state=str(session_file), ignore_https_errors=True
        )
        page = context_with_session.new_page()

        # Determine navigation URL based on role
        NEW_NAV_ROLES = ["manage_bene", "secondary_login"]
        current_role = test_data.get("role", "")
        use_new_nav = current_role in NEW_NAV_ROLES
        
        if use_new_nav:
            base_url = "https://app.test01.assetmark.com/clients"
            print(f"[SESSION] Role '{current_role}' - Using new nav URL")
        else:
            base_url = settings.login_url.replace("/ewmLogin/account/login", "/en.aspx")
        
        print(f"[SESSION] Navigating to: {base_url}")
        _navigate_with_fallback(
            page, base_url,
            username=username,
            password=test_data.get("password", "default_password"),
            session_file=session_file,
            browser=browser,
            use_new_nav=use_new_nav,
        )

        current_url = page.url
        print(f"[SESSION] Current URL after navigation: {current_url}")

        # Check if session is valid (not redirected back to login)
        if "login" in current_url.lower():
            print("[SESSION] Session expired! Redirected to login page.")
            print("[SESSION] Deleting expired session and re-logging in...")
            page.close()
            context_with_session.close()
            session_file.unlink()  # Delete expired session

            # Fall through to login below (session_file.exists() will be False now)
        else:
            print("[SESSION] Session activated - already logged in!")
            # Verify we're logged in as the correct user
            try:
                page_content = page.content()
                if username not in page_content:
                    print(f"[SESSION] WARNING: Session may be for a different user. Forcing re-login...")
                    page.close()
                    context_with_session.close()
                    session_file.unlink()
                    # Fall through to login below
                else:
                    yield page
                    page.close()
                    context_with_session.close()
                    return
            except Exception as e:
                print(f"[SESSION] Could not verify user, proceeding with session: {e}")
                yield page
                page.close()
                context_with_session.close()
                return

    # No session OR session expired - LOGIN HERE and save session
    if not session_file.exists():
        print(f"\n[SESSION] No session found for: {username}")
        print("[SESSION] Logging in and creating session...")

        page = context.new_page()

        # Determine navigation type based on role
        # Roles that require new navigation: manage_bene, secondary_login, etc.
        NEW_NAV_ROLES = ["manage_bene", "secondary_login"]
        current_role = test_data.get("role", "")
        use_new_nav = current_role in NEW_NAV_ROLES

        # Perform login using LoginPage methods
        try:
            login_page = LoginPage(page)
            if use_new_nav:
                nav_type = "new nav"
                print(f"[SESSION] Role '{current_role}' requires new navigation")
                login_page.navigate_to_new_nav()
            else:
                nav_type = "standard"
                login_page.navigate()
            
            print(f"[SESSION] Using {nav_type} navigation")
            login_page.accept_cookies()
            login_page.enter_username(username)
            login_page.enter_password(test_data.get("password", "default_password"))
            login_page.click_sign_in()
            login_page.submit_login_form()

            print(f"[SESSION] Login completed for: {username}")

            # Check if login successful
            current_url = page.url
            print(f"[SESSION] Current URL after login: {current_url}")
            if "login" not in current_url.lower():
                # Save session
                AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
                context.storage_state(path=str(session_file))
                print(f"[SESSION] Login successful! Session saved: {session_file.name}")
                print(f"[SESSION] Session file size: {session_file.stat().st_size} bytes")
            else:
                print("[SESSION] Login may have failed - still on login page")

        except Exception as e:
            print(f"[SESSION] Login error: {e}")

        # Maximize window if running in headed mode
        try:
            # For Chromium/Chrome, the --start-maximized flag handles this
            # For additional safety, we can also try to maximize via JavaScript
            is_headless = page.context.browser._impl._launch_args.get("headless", True)
            if not is_headless:
                print("[SESSION] Running in HEADED mode - window should be maximized")
                # Attempt to maximize window size (works with no_viewport: True)
                viewport_size = page.viewport_size
                if viewport_size:
                    print(f"[SESSION] Viewport size: {viewport_size['width']}x{viewport_size['height']}")
                else:
                    print("[SESSION] Viewport is unrestricted (no_viewport: True)")
        except Exception as e:
            print(f"[SESSION] Could not check viewport: {e}")

        yield page

        page.close()


# test_data fixture moved to tests/bdd/steps/conftest.py to avoid duplication


# REMOVED: Complex authenticated_page fixture - now using simple page override


@pytest.fixture
def fresh_page(browser):
    """
    Provides a fresh page WITHOUT authentication.
    Use this when you need to test login flow or unauthenticated access.

    Usage:
        def test_login(fresh_page):
            fresh_page.goto("/login")
            # No session - test login flow
    """
    context = browser.new_context(ignore_https_errors=True, no_viewport=True)
    page = context.new_page()

    # Log window state
    try:
        is_headless = browser._impl._launch_args.get("headless", True)
        if not is_headless:
            print("[FRESH_PAGE] Running in HEADED mode - window should be maximized")
            viewport_size = page.viewport_size
            if viewport_size:
                print(f"[FRESH_PAGE] Viewport size: {viewport_size['width']}x{viewport_size['height']}")
            else:
                print("[FRESH_PAGE] Viewport is unrestricted (no_viewport: True)")
    except Exception as e:
        print(f"[FRESH_PAGE] Could not check viewport: {e}")

    yield page

    context.close()


# Advanced fixtures for multiple contexts and pages
@pytest.fixture
def new_context(browser):
    """
    Create additional browser contexts for multi-session scenarios.

    Usage:
        def test_multi_user(page, new_context):
            # First user (default page)
            page.goto("/dashboard")

            # Second user (new context)
            admin_page = new_context.new_page()
            admin_page.goto("/admin")
    """
    contexts = []

    def _create_context(**kwargs):
        context_args = {"ignore_https_errors": True, **kwargs}
        ctx = browser.new_context(**context_args)
        contexts.append(ctx)
        return ctx

    yield _create_context

    # Cleanup all created contexts
    for ctx in contexts:
        ctx.close()


@pytest.fixture
def new_page(context):
    """
    Create additional pages within the same context for multi-tab scenarios.

    Usage:
        def test_multi_tab(page, new_page):
            # Main tab
            page.goto("/accounts")

            # Second tab (same session/cookies)
            tab2 = new_page()
            tab2.goto("/reports")

            # Work with both tabs
            assert page.url.endswith("/accounts")
            assert tab2.url.endswith("/reports")
    """
    pages = []

    def _create_page():
        new_pg = context.new_page()
        pages.append(new_pg)
        return new_pg

    yield _create_page

    # Cleanup all created pages
    for pg in pages:
        pg.close()


@pytest.fixture
def multi_user_contexts(browser):
    """
    Pre-configured contexts for multi-user testing.

    Returns dict with 'admin' and 'user' contexts.

    Usage:
        def test_admin_vs_user(multi_user_contexts):
            admin_page = multi_user_contexts['admin'].new_page()
            user_page = multi_user_contexts['user'].new_page()

            # Different sessions, different cookies
            admin_page.goto("/admin/dashboard")
            user_page.goto("/user/dashboard")
    """
    contexts = {
        "admin": browser.new_context(ignore_https_errors=True, storage_state=None),  # Fresh session
        "user": browser.new_context(ignore_https_errors=True, storage_state=None),  # Fresh session
    }

    yield contexts

    # Cleanup
    for ctx in contexts.values():
        ctx.close()


# Performance monitoring fixtures
@pytest.fixture
def performance_monitor(page: Page, request):
    """
    Performance monitor fixture.

    Automatically monitors performance for tests marked with @pytest.mark.performance
    """
    # Check if test has performance marker
    has_performance_marker = request.node.get_closest_marker("performance")

    if has_performance_marker:
        # Create performance budget (can be customized per test)
        budget = PerformanceBudget()

        # Initialize monitor
        monitor = PerformanceMonitor(page, budget=budget)
        monitor.start_monitoring()

        yield monitor

        # Collect and save metrics after test
        try:
            test_name = request.node.name
            metrics = monitor.collect_metrics(test_name=test_name, environment=env)

            # Save metrics
            monitor.save_metrics(metrics, filename=f"{test_name}.json")

            # Generate and print report
            report = monitor.generate_report(metrics)
            print(report)

            # Validate budget (will log warnings if violated)
            monitor.validate_budget(metrics)

        except Exception as e:
            print(f"Warning: Failed to collect performance metrics: {e}")
    else:
        yield None


@pytest.fixture
def performance_budget():
    """
    Performance budget fixture.

    Returns default budget, can be overridden in tests.
    """
    return PerformanceBudget()


# Pytest hooks for screenshot on failure and flaky test detection
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator:
    """
    Pytest hook to:
    1. Capture screenshot on test failure (Allure report)
    2. Detect flaky tests by tracking retries and failures
    """
    # Flaky test detection logic (BEFORE yielding to other hooks)
    if call.when == "call":  # Only track the actual test execution
        from datetime import datetime

        duration_ms = 0
        if hasattr(item, "start_time") and item.start_time:
            duration_ms = int((datetime.now() - item.start_time).total_seconds() * 1000)

        # Track failed attempts
        if call.excinfo is not None:
            item.failed_count += 1

        # Detect flaky test: passed after one or more failures
        if call.excinfo is None and item.execution_count > 1 and item.failed_count > 0:
            # This test is flaky - it failed at least once but eventually passed
            tracker = get_tracker()

            error_msg = ""
            if hasattr(call, "excinfo") and call.excinfo:
                error_msg = str(call.excinfo.value)

            tracker.record_flaky_test(
                test_name=item.nodeid,
                test_id=item.nodeid,
                total_attempts=item.execution_count,
                failed_attempts=item.failed_count,
                final_status="passed",
                duration_ms=duration_ms,
                error_message=error_msg,
            )

    # Screenshot capture logic
    outcome = yield
    rep = outcome.get_result()

    # Store report on node so fixtures can check pass/fail status (used by _stop_tracing)
    setattr(item, f"rep_{rep.when}", rep)

    # Only take screenshot on failure or error (including setup failures)
    if rep.failed and rep.when in ("call", "setup") and "page" in item.funcargs:
        page = item.funcargs["page"]
        try:
            # Take screenshot and attach to Allure
            screenshot_bytes = page.screenshot()
            allure.attach(
                screenshot_bytes,
                name=f"screenshot-{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")

    # Collect data for Excel report (only on the final call phase outcome)
    if rep.when == "call":
        excel_report.collect_result_from_item(item, rep)

    # In xdist workers, serialize collected results to per-worker file for merge
    if rep.when == "call" and os.environ.get("PYTEST_XDIST_WORKER"):
        _flush_worker_results()
        _flush_worker_flaky_data()


def _flush_worker_results() -> None:
    """Write current worker's collected Excel results to a per-worker JSON file."""
    import json

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    worker_file = Path(f"reports/excel_results_{worker_id}.json")
    worker_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        results = excel_report.test_results
        if results:
            with open(worker_file, "w", encoding="utf-8") as f:
                json.dump(results, f, default=str)
    except Exception:
        pass


def _flush_worker_flaky_data() -> None:
    """Write current worker's flaky test data to a per-worker JSON file."""
    import json

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    tracker = get_tracker()
    if not tracker.flaky_tests:
        return
    worker_file = Path(f"reports/flaky_results_{worker_id}.json")
    worker_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(worker_file, "w", encoding="utf-8") as f:
            json.dump(tracker.flaky_tests, f, default=str)
    except Exception:
        pass


def _merge_worker_files() -> None:
    """Merge worker-isolated log/data files into canonical files after parallel runs.

    Each worker writes to ``<name>_gw0.log``, ``<name>_gw1.log``, etc.
    This function appends all worker fragments into the canonical file
    and removes the fragments. Called once by the controller in ``pytest_sessionfinish``.
    """
    import glob as _glob

    merge_specs = [
        # (canonical_path, glob_pattern)
        ("reports/network_errors.log", "reports/network_errors_*.log"),
        ("reports/http_errors.log", "reports/http_errors_*.log"),
    ]

    for canonical, pattern in merge_specs:
        worker_files = sorted(_glob.glob(pattern))
        if not worker_files:
            continue

        canonical_path = Path(canonical)
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        with open(canonical_path, "a", encoding="utf-8") as out:
            for wf in worker_files:
                try:
                    with open(wf, "r", encoding="utf-8") as inp:
                        out.write(inp.read())
                    os.remove(wf)
                except Exception as e:
                    print(f"Warning: Failed to merge {wf}: {e}")


def _merge_worker_excel_results() -> None:
    """Merge per-worker Excel result JSON files into the controller's excel_report."""
    import glob as _glob
    import json

    worker_files = sorted(_glob.glob("reports/excel_results_*.json"))
    for wf in worker_files:
        try:
            with open(wf, "r", encoding="utf-8") as f:
                results = json.load(f)
            if results:
                excel_report.test_results.extend(results)
            os.remove(wf)
        except Exception as e:
            print(f"Warning: Failed to merge Excel results from {wf}: {e}")


def _merge_worker_flaky_results() -> None:
    """Merge per-worker flaky test JSON files into the controller's tracker."""
    import glob as _glob
    import json

    tracker = get_tracker()
    worker_files = sorted(_glob.glob("reports/flaky_results_*.json"))
    for wf in worker_files:
        try:
            with open(wf, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                tracker.flaky_tests.update(data)
            os.remove(wf)
        except Exception as e:
            print(f"Warning: Failed to merge flaky results from {wf}: {e}")


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: C901
    """
    Hook that runs after all tests complete.
    Automatically generates Allure HTML report from JSON results.
    Also generates auto-healing report and flaky test summary.
    Only runs on the controller (or single-process run) — workers skip it.
    """
    # In xdist, workers skip report generation to avoid racing/duplicates
    if hasattr(session.config, "workerinput"):
        return

    # Merge worker-isolated files (xdist parallel support)
    _merge_worker_files()
    _merge_worker_excel_results()
    _merge_worker_flaky_results()

    import json
    import platform
    import shutil
    from datetime import datetime

    # Generate Excel Report
    try:
        report_path = excel_report.generate_excel_report()
        if report_path:
            print(f"Excel Report: {report_path.absolute()}")
    except Exception as e:
        print(f"\nWARNING: Failed to generate Excel report: {e}\n")

    # Generate Auto-Healing Report
    try:
        from pages.base_page import BasePage

        healing_engine = BasePage._healing_engine
        if healing_engine:
            stats = healing_engine.get_stats()

            # Prepare detailed healing report
            healing_report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_healing_attempts": stats.get("total_heals", 0),
                    "successful_heals": stats.get("successful_heals", 0),
                    "failed_heals": stats.get("failed_heals", 0),
                    "success_rate": f"{stats.get('success_rate', 0) * 100:.2f}%",
                    "stored_alternatives": stats.get("stored_alternatives", 0),
                },
                "healed_locators": [],
            }

            # Add details of all healed locators
            for key, locator_data in healing_engine.locator_storage.items():
                healing_report["healed_locators"].append(
                    {
                        "hash_key": key,
                        "original_selector": locator_data.get("original", "N/A"),
                        "healed_selector": locator_data.get("selector", "N/A"),
                        "strategy_used": locator_data.get("strategy", "N/A"),
                        "success_count": locator_data.get("success_count", 0),
                        "timestamp": datetime.fromtimestamp(
                            locator_data.get("timestamp", 0)
                        ).isoformat(),
                    }
                )

            # Save to reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            healing_report_path = reports_dir / "auto_healing_report.json"
            with open(healing_report_path, "w") as f:
                json.dump(healing_report, f, indent=2)

            # Print summary to console
            if stats.get("total_heals", 0) > 0:
                print(f"\n{'=' * 60}")
                print("AUTO-HEALING SUMMARY")
                print(f"{'=' * 60}")
                print(f"Total Healing Attempts: {stats['total_heals']}")
                print(f"Successful Heals: {stats['successful_heals']}")
                print(f"Failed Heals: {stats['failed_heals']}")
                print(f"Success Rate: {stats['success_rate'] * 100:.2f}%")
                print(f"Stored Alternatives: {stats['stored_alternatives']}")
                print(f"\nDetailed Report: {healing_report_path.absolute()}")
                print(f"{'=' * 60}\n")
            else:
                print("\nOK: No auto-healing attempts in this session\n")
    except Exception as e:
        print(f"\nWARNING: Failed to generate auto-healing report: {e}\n")

    # Push flaky test metrics to InfluxDB
    try:
        tracker = get_tracker()
        summary = tracker.get_flaky_summary()

        if summary["total_flaky_tests"] > 0:
            print(f"\n{'=' * 60}")
            print("WARNING: FLAKY TEST SUMMARY")
            print(f"{'=' * 60}")
            print(f"Total Flaky Tests: {summary['total_flaky_tests']}")
            for test in summary["flaky_tests"]:
                print(
                    f"  - {test['name']}: {test['failed']}/{test['attempts']} failures → {test['status']}"
                )
            print(f"{'=' * 60}\n")

            # Push to InfluxDB
            tracker.push_to_influxdb()
        else:
            print("\nOK: No flaky tests detected in this session\n")
    except Exception as e:
        print(f"\nWARNING: Failed to track flaky tests: {e}\n")

    allure_results_dir = "reports/allure-results"
    allure_report_dir = "reports/allure-report"

    # Only generate report if results directory exists and has files
    if not os.path.exists(allure_results_dir):
        print(f"\nWarning: Allure results directory not found: {allure_results_dir}")
        return

    # Check if there are any result files
    result_files = [f for f in os.listdir(allure_results_dir) if f.endswith("-result.json")]
    if not result_files:
        print(f"\nWarning: No Allure result files found in {allure_results_dir}")
        return

    print(f"\nGenerating Allure HTML report from {len(result_files)} test results...")

    try:
        # Use shell=True on Windows to find allure in PATH
        is_windows = platform.system() == "Windows"

        # Generate Allure HTML report with --single-file for direct browser opening
        result = subprocess.run(
            [
                "allure",
                "generate",
                allure_results_dir,
                "--clean",
                "--single-file",
                "-o",
                allure_report_dir,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            shell=is_windows,  # Required on Windows to find commands in PATH
        )

        if result.returncode == 0:
            import glob

            report_path = os.path.abspath(allure_report_dir)
            index_path = os.path.join(report_path, "index.html")

            # Create timestamped copy of the report
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timestamped_index = os.path.join(report_path, f"index_{timestamp}.html")

            try:
                shutil.copy2(index_path, timestamped_index)

                # Clean up old timestamped reports (keep last 10)
                try:
                    timestamped_files = sorted(
                        glob.glob(os.path.join(report_path, "index_*.html")),
                        key=os.path.getmtime,
                        reverse=True,  # Newest first
                    )
                    # Keep only the last 10
                    files_to_remove = timestamped_files[10:]
                    for old_file in files_to_remove:
                        os.remove(old_file)
                        print(f"   Cleaned up old report: {os.path.basename(old_file)}")
                except Exception:
                    # Non-critical error, just skip
                    pass

                print("Allure report generated successfully!")
                print(f"Report location: {report_path}")
                print(f"Main report: file:///{index_path.replace(os.sep, '/')}")
                print(f"Timestamped: file:///{timestamped_index.replace(os.sep, '/')}")

                # Show count of historical reports
                timestamped_files = glob.glob(os.path.join(report_path, "index_*.html"))
                timestamped_count = len(timestamped_files)
                if timestamped_count > 1:
                    print(f"Historical reports: {timestamped_count} available (keeping last 10)")

                print("\nAlternative commands:")
                print(f"   allure open {allure_report_dir}")
                print(f"   allure serve {allure_results_dir}")
            except Exception as e:
                print("Allure report generated successfully!")
                print(f"Report location: {report_path}")
                print(f"Open in browser: file:///{index_path.replace(os.sep, '/')}")
                print(f"Warning: Failed to create timestamped copy: {e}")
        else:
            print("Warning: Allure report generation failed:")
            print(f"   {result.stderr}")
    except FileNotFoundError:
        print("\nWarning: Allure CLI not found. Install it with:")
        print("   npm install -g allure-commandline")
        print("   or download from: https://github.com/allure-framework/allure2/releases")
    except subprocess.TimeoutExpired:
        print("\nWarning: Allure report generation timed out (>60s)")
    except Exception as e:
        print(f"\nWarning: Error generating Allure report: {e}")

    # Auto-push test execution metrics to InfluxDB (controlled by config toggle)
    try:
        from utils.influx_reporter import AllureToInfluxDB

        reporter = AllureToInfluxDB()
        if reporter.auto_push:
            reporter.allure_results_dir = allure_results_dir
            reporter.run()
        else:
            print("\nInfluxDB auto-push disabled (set 'auto_push': true in influxdb_config.json to enable)")
    except Exception as e:
        print(f"\nWARNING: Failed to push metrics to InfluxDB: {e}")


def _navigate_with_fallback(page, url: str, username: str, password: str,
                             session_file: Path, browser, use_new_nav: bool) -> bool:
    """
    Navigate to url with 60s timeout. On timeout, clears storage/cache and
    falls back to a fresh login. Returns True if navigation succeeded.
    """
    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        return True
    except Exception as nav_err:
        print(f"[NAV] Timeout navigating to {url}: {nav_err}")
        print("[NAV] Clearing cache and retrying with fresh login...")
        try:
            # Clear cookies/storage so stale state doesn't block retry
            page.context.clear_cookies()
            try:
                page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            except Exception:
                pass

            # Delete stale session file so a fresh one gets created
            if session_file.exists():
                session_file.unlink()
                print("[NAV] Deleted stale session file")

            # Navigate to login and re-authenticate
            login_page = LoginPage(page)
            if use_new_nav:
                login_page.navigate_to_new_nav()
            else:
                login_page.navigate()
            login_page.accept_cookies()
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_sign_in()
            login_page.submit_login_form()

            # Save fresh session
            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            page.context.storage_state(path=str(session_file))
            print("[NAV] Fresh login successful, session saved")
            return True
        except Exception as fallback_err:
            print(f"[NAV] Fallback login also failed: {fallback_err}")
            return False

@pytest.fixture
def vcr_config():
    """VCR configuration for recording HTTP interactions"""

    return {
        "filter_headers": ['authorization'],
    }


@pytest.fixture(scope="session")
def maximize_window_and_login(browser):
    """Maximize the browser window and perform login with default credentials."""
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})  # Maximize window

    # Use default credentials
    username = os.getenv("DEFAULT_USERNAME", "T11_AG8959_Perf")
    password = os.getenv("DEFAULT_PASSWORD", "QAAdminUser_33a")

    # Navigate to login page and perform login
    login_page = LoginPage(page)
    login_page.navigate_to_login(Settings().login_url)
    login_page.dismiss_cookie_consent()
    page.fill("input[name='username'], input[id='username']", username)
    page.fill("input[name='password'], input[id='password']", password)
    page.click("input[type='submit'], button[type='submit']")

    # Wait for successful login
    page.wait_for_url("**/en.aspx", timeout=30000)
    return page

    return {"filter_headers": ["authorization"]}

