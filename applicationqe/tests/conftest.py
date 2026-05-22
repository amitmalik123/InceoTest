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

import csv
import logging
import os
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

# Ensure application root is in sys.path
_APP_ROOT = Path(__file__).resolve().parent.parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

# Keep branch fixture registration behavior
from tests.fixtures.assertion_fixtures import *  # noqa: F401, F403
from tests.fixtures.auth_fixtures import *  # noqa: F401, F403
from tests.fixtures.browser_fixtures import *  # noqa: F401, F403
from tests.fixtures.data_fixtures import *  # noqa: F401, F403
from tests.fixtures.db_fixtures import *  # noqa: F401, F403
from tests.fixtures.hooks_fixtures import *  # noqa: F401, F403
from tests.fixtures.page_fixtures import *  # noqa: F401, F403

# Optional STP fixture import from develop branch
try:
    from fixtures.stp import *  # noqa: F401, F403
except Exception:
    pass

# Settings import compatibility across branches
try:
    from config.PortfolioReporting.settings import get_settings
except Exception:
    from config.settings import get_settings

from utils.allure_logger import enable_step_screenshots
from utils.flaky_test_tracker import get_tracker

try:
    from utils.excel_utils import excel_report
except Exception:
    class _NoopExcelReport:
        test_results = []

        def clear_test_results(self):
            return None

        def collect_result_from_item(self, item, rep):
            return None

        def generate_excel_report(self):
            return None

    excel_report = _NoopExcelReport()

try:
    from utils.settings import Settings
except Exception:
    class Settings:
        def __init__(self, env: str = "test11"):
            cfg = get_settings()
            self.env = env
            self.login_url = getattr(cfg, "login_url", "")
            self.test_data_csv = str(
                _APP_ROOT / "data" / "PortfolioReporting" / f"test_data.{env}.csv"
            )

try:
    from pages.stp.shared.login_page import LoginPage
except Exception:
    from pages.PortfolioReporting.login_page import LoginPage

try:
    from utils.performance_monitor import PerformanceBudget, PerformanceMonitor
except Exception:
    class PerformanceBudget:
        pass

    class PerformanceMonitor:
        def __init__(self, page, budget=None):
            self.page = page
            self.budget = budget

        def start_monitoring(self):
            return None

        def collect_metrics(self, test_name=None, environment=None):
            return {}

        def save_metrics(self, metrics, filename=None):
            return None

        def generate_report(self, metrics):
            return ""

        def validate_budget(self, metrics):
            return None


logger = logging.getLogger(__name__)

env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=env)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_PATH = str(_PROJECT_ROOT / "downloads" / "ACH PDF")
AUTH_STATE_DIR = Path("tests/.auth")


@pytest.fixture(scope="session")
def all_test_data():
    """Load ALL test data rows from CSV (one row per role/user)."""
    csv_path = settings.test_data_csv
    data_rows = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as file:
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
    Pre-create session files only for roles used in the current test run.
    """
    from datetime import datetime

    AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)

    roles_to_create = set()
    if hasattr(request.session, "items"):
        for item in request.session.items:
            if hasattr(item, "callspec") and hasattr(item.callspec, "params"):
                if "role" in item.callspec.params:
                    roles_to_create.add(item.callspec.params["role"])

    if not roles_to_create:
        logger.info("[SESSION SETUP] BDD test detected - skipping auto-session creation")
        logger.info("[SESSION SETUP] Sessions will be created on-demand for efficiency")
        yield
        return

    print(f"\n{'=' * 60}")
    print(f"[SESSION SETUP] Pre-creating sessions for roles: {sorted(roles_to_create)}")
    print(f"{'=' * 60}")

    created_sessions = []

    for test_data_row in all_test_data:
        role = test_data_row.get("role", "unknown")
        if role not in roles_to_create:
            continue

        username = test_data_row.get("username", "unknown")
        password = test_data_row.get("password", "")

        new_nav_roles = ["manage_bene", "secondary_login"]
        use_new_nav = role in new_nav_roles

        session_file = AUTH_STATE_DIR / f"{username}_{role}.json"

        if session_file.exists():
            file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
            if file_age.total_seconds() / 3600 < 8:
                print(f"[SESSION SETUP] Session exists for {username} (role: {role})")
                created_sessions.append((username, role, False))
                continue
            print(f"[SESSION SETUP] Session expired for {username}, recreating...")
            session_file.unlink()

        try:
            nav_type = "new nav" if use_new_nav else "standard"
            print(
                f"[SESSION SETUP] Creating session for {username} (role: {role}, nav: {nav_type})..."
            )

            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

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

            if "login" not in page.url.lower():
                context.storage_state(path=str(session_file))
                print(f"[SESSION SETUP] Session saved: {username}")
                created_sessions.append((username, role, True))
            else:
                print(f"[SESSION SETUP] Login failed for {username}")
                created_sessions.append((username, role, False))

            page.close()
            context.close()

        except Exception as e:
            print(f"[SESSION SETUP] Error creating session for {username}: {e}")
            created_sessions.append((username, role, False))

    print(f"{'=' * 60}")
    print("[SESSION SETUP] Summary:")
    for username, role, success in created_sessions:
        status = "OK" if success else "FAIL"
        print(f"  {status} {username} (role: {role})")
    print(f"{'=' * 60}\n")

    yield


# Pytest configuration hooks
def pytest_addoption(parser) -> None:
    """Add custom command-line options."""
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step (can be slow, use for debugging)",
    )


def pytest_configure(config) -> None:
    """Register custom markers and configure retry behavior."""
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

    settings_instance = get_settings()
    screenshot_each_step = (
        config.getoption("--screenshot-each-step", default=False)
        or os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes", "on")
        or getattr(settings_instance, "screenshot_each_step", False)
    )
    enable_step_screenshots(screenshot_each_step)

    status = "ENABLED for ALL steps" if screenshot_each_step else "ENABLED on failure only"
    print(f"\n{'=' * 60}")
    print(f"Step Screenshots: {status}")
    print(f"{'=' * 60}")

    if not config.option.reruns and not config.option.usepdb:
        config.option.reruns = 1
        config.option.reruns_delay = 1


def pytest_sessionstart(session) -> None:
    """
    Hook that runs before test session starts.
    Clears old Allure results, videos, and traces to ensure fresh artifacts for each run.
    Only the controller (or single-process run) performs cleanup - workers skip it.
    """
    if hasattr(session.config, "workerinput"):
        return

    import shutil

    try:
        from utils.download_utils import _get_default_download_dir
        default_download_dir = _get_default_download_dir()
    except Exception:
        default_download_dir = DOWNLOAD_PATH

    dirs_to_clean = [
        "reports/allure-results",
        "reports/videos",
        "reports/traces",
        default_download_dir,
    ]

    files_to_clean = [
        "reports/network_errors_*.log",
    ]

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
    """Handle @prod_order_N tags from PROD feature files."""
    if tag.startswith("prod_order_"):
        suffix = tag[len("prod_order_") :]
        if suffix.isdigit():
            function.__prod_order__ = int(suffix)
            return True
    return None


def pytest_collection_modifyitems(config, items) -> None:  # noqa: C901
    """
    Consolidated hook for test collection modification.
    """
    current_env = get_settings().env
    available_apps = set(get_settings().get_available_apps())

    for item in items:
        item.execution_count = 0
        item.failed_count = 0
        item.start_time = None

        if not item.get_closest_marker("app"):
            for mark in item.iter_markers():
                if mark.name in available_apps:
                    item.add_marker(pytest.mark.app(mark.name))
                    break

        if current_env == "test11":
            item.add_marker(pytest.mark.test11)
        elif current_env == "test12":
            item.add_marker(pytest.mark.test12)
        elif current_env == "silo":
            item.add_marker(pytest.mark.silo)
        elif current_env == "prod":
            item.add_marker(pytest.mark.prod)

        if "serial" not in [mark.name for mark in item.iter_markers()]:
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

            if not any(mark.name == "xdist_group" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.xdist_group(group))

        if hasattr(item, "callspec") and item.callspec and len(item.callspec.params) > 5:
            item.add_marker(pytest.mark.slow)

    prod_items = [i for i in items if any(m.name == "prod" for m in i.iter_markers())]
    non_prod_items = [i for i in items if i not in prod_items]
    prod_items.sort(key=lambda i: getattr(getattr(i, "function", None), "__prod_order__", 999))
    items[:] = non_prod_items + prod_items


def pytest_runtest_setup(item) -> None:
    """Called before each test execution (including retries)."""
    from datetime import datetime

    item.execution_count += 1
    item.start_time = datetime.now()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments to disable PDF viewer."""
    return {
        **browser_type_launch_args,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-pdf-viewer",
            "--disable-features=PdfViewerPlugin",
            "--disable-features=PluginPowerSaver",
        ],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    """Configure context args with downloads/video and viewport."""
    context_args = {
        **browser_context_args,
        "ignore_https_errors": True,
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
        file_path = os.path.join(DOWNLOAD_PATH, download.suggested_filename)
        download.save_as(file_path)
        downloads.append(file_path)

    page.on("download", handle_download)

    yield {
        "download_path": DOWNLOAD_PATH,
        "downloads": downloads,
    }


@pytest.fixture
def page(context, browser, test_context, request):
    """Session-storage aware page fixture."""
    from datetime import datetime

    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    if "test_data" in test_context:
        test_data_row = test_context["test_data"]
        print("[SESSION] Using test data from test_context (role-based)")
    else:
        print("[SESSION] WARNING: test_context['test_data'] not found, using default")
        test_data_row = {}

    username = test_data_row.get("username", "default_user")
    current_role = test_data_row.get("role", "default")

    # If scenario-specific test data is unavailable, fall back to the stable
    # authenticated_page fixture flow instead of attempting invalid default login.
    login_url = str(getattr(settings, "login_url", ""))
    if username == "default_user" or not login_url.startswith("http"):
        print("[SESSION] Fallback to authenticated_page due to missing/invalid test data")
        yield request.getfixturevalue("authenticated_page")
        return

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

    if session_file.exists():
        print(f"\n[SESSION] Loading saved session for: {username}")
        context_with_session = browser.new_context(
            storage_state=str(session_file), ignore_https_errors=True
        )
        pg = context_with_session.new_page()

        new_nav_roles = ["manage_bene", "secondary_login"]
        current_role = test_data_row.get("role", "")
        use_new_nav = current_role in new_nav_roles

        if use_new_nav:
            base_url = "https://app.test01.assetmark.com/clients"
            print(f"[SESSION] Role '{current_role}' - Using new nav URL")
        else:
            base_url = settings.login_url.replace("/ewmLogin/account/login", "/en.aspx")

        print(f"[SESSION] Navigating to: {base_url}")
        _navigate_with_fallback(
            pg,
            base_url,
            username=username,
            password=test_data_row.get("password", "default_password"),
            session_file=session_file,
            browser=browser,
            use_new_nav=use_new_nav,
        )

        current_url = pg.url
        print(f"[SESSION] Current URL after navigation: {current_url}")

        if "login" in current_url.lower():
            print("[SESSION] Session expired! Redirected to login page.")
            print("[SESSION] Deleting expired session and re-logging in...")
            pg.close()
            context_with_session.close()
            session_file.unlink()
        else:
            print("[SESSION] Session activated - already logged in!")
            try:
                page_content = pg.content()
                if username not in page_content:
                    print(
                        "[SESSION] WARNING: Session may be for a different user. Forcing re-login..."
                    )
                    pg.close()
                    context_with_session.close()
                    session_file.unlink()
                else:
                    yield pg
                    pg.close()
                    context_with_session.close()
                    return
            except Exception as e:
                print(f"[SESSION] Could not verify user, proceeding with session: {e}")
                yield pg
                pg.close()
                context_with_session.close()
                return

    if not session_file.exists():
        print(f"\n[SESSION] No session found for: {username}")
        print("[SESSION] Logging in and creating session...")

        pg = context.new_page()

        new_nav_roles = ["manage_bene", "secondary_login"]
        current_role = test_data_row.get("role", "")
        use_new_nav = current_role in new_nav_roles

        try:
            login_page = LoginPage(pg)
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
            login_page.enter_password(test_data_row.get("password", "default_password"))
            login_page.click_sign_in()
            login_page.submit_login_form()

            print(f"[SESSION] Login completed for: {username}")

            current_url = pg.url
            print(f"[SESSION] Current URL after login: {current_url}")
            if "login" not in current_url.lower():
                AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
                context.storage_state(path=str(session_file))
                print(f"[SESSION] Login successful! Session saved: {session_file.name}")
                print(f"[SESSION] Session file size: {session_file.stat().st_size} bytes")
            else:
                print("[SESSION] Login may have failed - still on login page")

        except Exception as e:
            print(f"[SESSION] Login error: {e}")

        yield pg
        pg.close()


@pytest.fixture
def fresh_page(browser):
    """Provides a fresh page without authentication."""
    context = browser.new_context(ignore_https_errors=True)
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture
def new_context(browser):
    """Create additional browser contexts for multi-session scenarios."""
    contexts = []

    def _create_context(**kwargs):
        context_args = {"ignore_https_errors": True, **kwargs}
        ctx = browser.new_context(**context_args)
        contexts.append(ctx)
        return ctx

    yield _create_context

    for ctx in contexts:
        ctx.close()


@pytest.fixture
def new_page(context):
    """Create additional pages within the same context for multi-tab scenarios."""
    pages = []

    def _create_page():
        new_pg = context.new_page()
        pages.append(new_pg)
        return new_pg

    yield _create_page

    for pg in pages:
        pg.close()


@pytest.fixture
def multi_user_contexts(browser):
    """Pre-configured contexts for multi-user testing."""
    contexts = {
        "admin": browser.new_context(ignore_https_errors=True, storage_state=None),
        "user": browser.new_context(ignore_https_errors=True, storage_state=None),
    }

    yield contexts

    for ctx in contexts.values():
        ctx.close()


@pytest.fixture
def performance_monitor(page: Page, request):
    """Performance monitor fixture."""
    has_performance_marker = request.node.get_closest_marker("performance")

    if has_performance_marker:
        budget = PerformanceBudget()
        monitor = PerformanceMonitor(page, budget=budget)
        monitor.start_monitoring()

        yield monitor

        try:
            test_name = request.node.name
            metrics = monitor.collect_metrics(test_name=test_name, environment=env)
            monitor.save_metrics(metrics, filename=f"{test_name}.json")
            report = monitor.generate_report(metrics)
            print(report)
            monitor.validate_budget(metrics)

        except Exception as e:
            print(f"Warning: Failed to collect performance metrics: {e}")
    else:
        yield None


@pytest.fixture
def performance_budget():
    """Performance budget fixture."""
    return PerformanceBudget()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator:
    """
    Pytest hook to:
    1. Capture screenshot on test failure (Allure report)
    2. Detect flaky tests by tracking retries and failures
    """
    if call.when == "call":
        from datetime import datetime

        duration_ms = 0
        if hasattr(item, "start_time") and item.start_time:
            duration_ms = int((datetime.now() - item.start_time).total_seconds() * 1000)

        if call.excinfo is not None:
            item.failed_count += 1

        if call.excinfo is None and item.execution_count > 1 and item.failed_count > 0:
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

    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)

    if rep.failed and rep.when in ("call", "setup") and "page" in item.funcargs:
        pg = item.funcargs["page"]
        try:
            screenshot_bytes = pg.screenshot()
            allure.attach(
                screenshot_bytes,
                name=f"screenshot-{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")

    if rep.when == "call":
        excel_report.collect_result_from_item(item, rep)

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
    if not getattr(tracker, "flaky_tests", None):
        return
    worker_file = Path(f"reports/flaky_results_{worker_id}.json")
    worker_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(worker_file, "w", encoding="utf-8") as f:
            json.dump(tracker.flaky_tests, f, default=str)
    except Exception:
        pass


def _merge_worker_files() -> None:
    """Merge worker-isolated log/data files into canonical files after parallel runs."""
    import glob as _glob

    merge_specs = [
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
    Only runs on the controller (or single-process run) - workers skip it.
    """
    if hasattr(session.config, "workerinput"):
        return

    _merge_worker_files()
    _merge_worker_excel_results()
    _merge_worker_flaky_results()

    import json
    import platform
    import shutil
    from datetime import datetime

    try:
        report_path = excel_report.generate_excel_report()
        if report_path:
            print(f"Excel Report: {report_path.absolute()}")
    except Exception as e:
        print(f"\nWARNING: Failed to generate Excel report: {e}\n")

    try:
        from pages.base_page import BasePage

        healing_engine = BasePage._healing_engine
        if healing_engine:
            stats = healing_engine.get_stats()

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

            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            healing_report_path = reports_dir / "auto_healing_report.json"
            with open(healing_report_path, "w", encoding="utf-8") as f:
                json.dump(healing_report, f, indent=2)

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
                    f"  - {test['name']}: {test['failed']}/{test['attempts']} failures -> {test['status']}"
                )
            print(f"{'=' * 60}\n")

            tracker.push_to_influxdb()
        else:
            print("\nOK: No flaky tests detected in this session\n")
    except Exception as e:
        print(f"\nWARNING: Failed to track flaky tests: {e}\n")

    allure_results_dir = "reports/allure-results"
    allure_report_dir = "reports/allure-report"

    if not os.path.exists(allure_results_dir):
        print(f"\nWarning: Allure results directory not found: {allure_results_dir}")
        return

    result_files = [f for f in os.listdir(allure_results_dir) if f.endswith("-result.json")]
    if not result_files:
        print(f"\nWarning: No Allure result files found in {allure_results_dir}")
        return

    print(f"\nGenerating Allure HTML report from {len(result_files)} test results...")

    try:
        is_windows = platform.system() == "Windows"

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
            shell=is_windows,
        )

        if result.returncode == 0:
            import glob

            report_path = os.path.abspath(allure_report_dir)
            index_path = os.path.join(report_path, "index.html")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timestamped_index = os.path.join(report_path, f"index_{timestamp}.html")

            try:
                shutil.copy2(index_path, timestamped_index)

                try:
                    timestamped_files = sorted(
                        glob.glob(os.path.join(report_path, "index_*.html")),
                        key=os.path.getmtime,
                        reverse=True,
                    )
                    files_to_remove = timestamped_files[10:]
                    for old_file in files_to_remove:
                        os.remove(old_file)
                        print(f"   Cleaned up old report: {os.path.basename(old_file)}")
                except Exception:
                    pass

                print("Allure report generated successfully!")
                print(f"Report location: {report_path}")
                print(f"Main report: file:///{index_path.replace(os.sep, '/')}")
                print(f"Timestamped: file:///{timestamped_index.replace(os.sep, '/')}")

                timestamped_files = glob.glob(os.path.join(report_path, "index_*.html"))
                if len(timestamped_files) > 1:
                    print(f"Historical reports: {len(timestamped_files)} available (keeping last 10)")

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


def _navigate_with_fallback(
    page, url: str, username: str, password: str, session_file: Path, browser, use_new_nav: bool
) -> bool:
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
            page.context.clear_cookies()
            try:
                page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            except Exception:
                pass

            if session_file.exists():
                session_file.unlink()
                print("[NAV] Deleted stale session file")

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

            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            page.context.storage_state(path=str(session_file))
            print("[NAV] Fresh login successful, session saved")
            return True
        except Exception as fallback_err:
            print(f"[NAV] Fallback login also failed: {fallback_err}")
            return False


@pytest.fixture
def vcr_config():
    """VCR configuration for recording HTTP interactions."""
    return {"filter_headers": ["authorization"]}
