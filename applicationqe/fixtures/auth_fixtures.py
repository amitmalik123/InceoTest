"""
Authentication and Session Management Fixtures

This module contains:
- AppConfig class for multi-application configuration
- Session file management (_get_session_file)
- Login execution logic (_perform_login)
- authenticated_page fixture (main auth fixture)
- page fixture (backward compatible)
- fresh_page fixture (for login testing)

These fixtures handle authentication state persistence and multi-app support.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Optional
import logging
import os

from filelock import FileLock
import pytest
from playwright.sync_api import Page

from config.settings import Settings, get_settings
from pages.ewm.login_page import LoginPage
from fixtures.browser_fixtures import apply_context_listeners, apply_route_blocks

# Authentication state directory
AUTH_STATE_DIR = Path("tests/.auth")


# Session Storage Configuration
class AppConfig:
    """Configuration for different applications loaded from YAML config"""

    def __init__(
        self, name: str, login_url: str, home_url: str, login_page_class, timeout: int = 30000
    ):
        self.name = name
        self.login_url = login_url
        self.home_url = home_url
        self.login_page_class = login_page_class
        self.timeout = timeout


def _load_app_configs(settings_obj: Settings) -> dict:
    """
    Load application configurations from YAML config files.

    Returns:
        dict: Dictionary of AppConfig objects keyed by app name
    """
    import importlib

    app_configs = {}

    # Get all configured apps from YAML
    for app_name in settings_obj.get_available_apps():
        app_data = settings_obj.get_app_config(app_name)

        # Dynamically import the login page class
        login_page_class_name = app_data.get("login_page_class", "LoginPage")
        try:
            # Import from pages module
            pages_module = importlib.import_module("pages")
            login_page_class = getattr(pages_module, login_page_class_name)
        except (ImportError, AttributeError):
            # Fallback to LoginPage if class not found
            login_page_class = LoginPage
            print(f"Warning: Could not import {login_page_class_name}, using LoginPage")

        app_configs[app_name] = AppConfig(
            name=app_data["name"],
            login_url=app_data["login_url"],
            home_url=app_data["home_url"],
            login_page_class=login_page_class,
            timeout=app_data.get("timeout", 30000),
        )

    return app_configs


def _get_session_file(
    username: str, app_name: str, worker_id: str, role: Optional[str] = None
) -> Path:
    """
    Generate session file path based on username.
    All parallel workers share the same session file so only one Okta login
    is performed; the rest reuse the saved session.
    """
    base_name = f"{username}"
    return AUTH_STATE_DIR / f"{base_name}.json"


def _perform_login(page: Page, app_config: AppConfig, test_data: dict) -> bool:
    """
    Perform login using the app-specific login page.

    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        settings = get_settings()
        # Derive base_url from login_url (strip the path portion)
        from urllib.parse import urlparse

        parsed = urlparse(app_config.login_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/"

        login_page = app_config.login_page_class(page, base_url=base_url)
        login_page.navigate()
        login_page.accept_cookies()

        # For Internal Admin scenarios, use environment config credentials instead of Excel
        user_role = (test_data.get("UserRole") or test_data.get("userRole") or "").strip()
        if user_role.lower() in ("internal admin", "internaladmin", "internal_admin"):
            username = settings.internal_admin_username
            password = settings.internal_admin_password
        else:
            username = (test_data.get("username") or test_data.get("UserName") or "").strip()
            password = (test_data.get("password") or test_data.get("Password") or "").strip()
        if not username or not password:
            raise RuntimeError(
                "Missing login credentials in test data or config. "
                "Expected username/UserName and password/Password in Excel, "
                "or internal_admin config in env YAML for Internal Admin role."
            )

        login_page.enter_username(username)
        login_page.enter_password(password)

        # Ketch banner can load asynchronously after navigate; dismiss before sign-in
        login_page.accept_cookies()

        login_page.click_sign_in()

        # Wait for SSO redirect chain to complete (Okta ΓåÆ test-login.assetmark.com ΓåÆ app).
        # The intermediate SSO page URL still contains "login", so an immediate check
        # returns False.  Under parallel execution (4 workers hitting Okta concurrently)
        # the redirect chain is slower and this wait is essential.
        if "login" in page.url.lower():
            try:
                page.wait_for_url(
                    lambda url: "login" not in url.lower(),
                    timeout=60000,
                )
            except Exception:
                print(f"[SESSION] SSO redirect did not complete, final URL: {page.url}")

        # Dismiss OneTrust cookie consent overlay (appears post-login on first session)
        login_page.dismiss_onetrust()

        return "login" not in page.url.lower()
    except Exception as e:
        print(f"[SESSION] Login error: {e}")
        return False


@pytest.fixture
def authenticated_page(browser, browser_context_args, test_context, request) -> Generator[Page, None, None]:
    """
    Flexible authenticated page fixture supporting multiple applications.

    Usage:
        @pytest.mark.app("ewm")  # Default app
        def test_ewm(authenticated_page):
            authenticated_page.goto("/accounts")

        @pytest.mark.app("app2")  # Different app
        def test_app2(authenticated_page):
            authenticated_page.goto("/dashboard")
    """
    import os
    from datetime import datetime

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Get app from marker or use default
    app_marker = request.node.get_closest_marker("app")
    if app_marker:
        app_name = app_marker.args[0]
    elif request.node.get_closest_marker("baw") or request.node.get_closest_marker("BAW"):
        app_name = "baw"
    else:
        app_name = "ewm"

    # Get app configuration (deferred to avoid import-time env var requirement)
    settings = get_settings()
    app_configs = _load_app_configs(settings)
    if app_name not in app_configs:
        raise ValueError(f"Unknown app: {app_name}. Available: {list(app_configs.keys())}")

    app_config = app_configs[app_name]
    test_data = test_context.get("test_data", {})

    # For Internal Admin scenarios, use environment config credentials
    user_role = (test_data.get("UserRole") or test_data.get("userRole") or "").strip()
    if user_role.lower() in ("internal admin", "internaladmin", "internal_admin"):
        username = settings.internal_admin_username
    else:
        username = (test_data.get("username") or test_data.get("UserName") or "").strip()
    role = test_data.get("role")  # Get role from test data
    session_file = _get_session_file(username, app_name, worker_id, role)
    session_max_age_hours = 8

    # Build context args: inherit video/viewport/recording settings from browser_context_args
    # but exclude record_video_dir for the temporary login context
    base_ctx_args = {k: v for k, v in browser_context_args.items()}

    # Read tracing config from pytest CLI options
    tracing_option = request.config.getoption("--tracing", default="off")
    capture_trace = tracing_option in ("on", "retain-on-failure")

    print(f"\n{'=' * 60}")
    print(f"[SESSION] App: {app_name}")
    print(f"[SESSION] Worker: {worker_id}")
    print(f"[SESSION] Role: {role}")
    print(f"[SESSION] Username: {username}")
    print(f"[SESSION] Session file: {session_file.name}")
    print(f"{'=' * 60}")

    # Check if session is too old
    if session_file.exists():
        file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
        file_age_hours = file_age.total_seconds() / 3600

        if file_age_hours > session_max_age_hours:
            print(f"[SESSION] Session too old ({file_age_hours:.1f}h), deleting...")
            session_file.unlink()

    # Try to load existing session
    if session_file.exists():
        print("[SESSION] Loading saved session...")
        context = browser.new_context(storage_state=str(session_file), **base_ctx_args)
        apply_route_blocks(context)
        apply_context_listeners(context)
        if capture_trace:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        # Navigate to home URL to activate session
        print(f"[SESSION] Navigating to: {app_config.home_url}")
        page.goto(app_config.home_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Verify session is still valid
        if "login" not in page.url.lower():
            print("[SESSION] Session valid! Already authenticated.")
            yield page
            # Save trace on failure if configured
            _stop_tracing(context, tracing_option, request)
            page.close()
            context.close()
            return
        else:
            # Session expired - close this context and delete session file
            print("[SESSION] Session expired, deleting and re-authenticating...")
            if capture_trace:
                context.tracing.stop()  # discard trace from expired session attempt
            page.close()
            context.close()
            session_file.unlink()
            # Fall through to login block below

    # No session or expired - perform login with cross-worker coordination.
    # FileLock ensures only one worker logs in per username; others block
    # until the session file is written, then reuse it.
    if not session_file.exists():
        AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
        lock_file = session_file.with_suffix(".lock")
        lock = FileLock(str(lock_file), timeout=120)

        with lock:
            # Double-check: another worker may have created the session while we waited
            if not session_file.exists():
                print(f"[SESSION] Worker {worker_id} acquired lock, logging in to {app_name}...")

                login_success = False
                for attempt in range(1, 4):
                    temp_context = browser.new_context(ignore_https_errors=True)
                    temp_page = temp_context.new_page()
                    login_success = _perform_login(temp_page, app_config, test_data)
                    if login_success:
                        temp_context.storage_state(path=str(session_file))
                        print(f"[SESSION] Login successful on attempt {attempt}! Session saved.")
                    else:
                        print(f"[SESSION] Login attempt {attempt}/3 failed")
                    temp_page.close()
                    temp_context.close()
                    if login_success:
                        break
                    import time; time.sleep(5 * attempt)

                if not login_success:
                    raise RuntimeError("Login failed after 3 attempts - cannot proceed without authentication")
            else:
                print(f"[SESSION] Worker {worker_id} found session created by another worker.")

        # Create NEW context with saved session and full recording settings
        print("[SESSION] Creating new context with saved session...")
        context = browser.new_context(storage_state=str(session_file), **base_ctx_args)
        apply_route_blocks(context)
        apply_context_listeners(context)
        if capture_trace:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        # Navigate to home page
        print(f"[SESSION] Navigating to: {app_config.home_url}")
        page.goto(app_config.home_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        print("[SESSION] Ready for test execution!")

        yield page

        _stop_tracing(context, tracing_option, request)
        page.close()
        context.close()


def _stop_tracing(context, tracing_option: str, request) -> None:
    """Stop tracing and save the trace file based on the tracing option."""
    if tracing_option == "off":
        return

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    # Also check for setup failure
    if not failed:
        failed = getattr(getattr(request.node, "rep_setup", None), "failed", False)

    if tracing_option == "on" or (tracing_option == "retain-on-failure" and failed):
        trace_dir = Path("reports/traces")
        trace_dir.mkdir(parents=True, exist_ok=True)
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
        trace_path = trace_dir / f"{worker_id}_{request.node.name}.zip"
        try:
            context.tracing.stop(path=str(trace_path))
            print(f"[TRACE] Saved: {trace_path}")
        except Exception as e:
            print(f"[TRACE] Failed to save: {e}")
    else:
        try:
            context.tracing.stop()  # Stop without saving
        except Exception:
            pass


@pytest.fixture
def fresh_page(browser, browser_context_args, request) -> Generator[Page, None, None]:
    """
    Provides a fresh page WITHOUT authentication.
    Use this when you need to test login flow or unauthenticated access.

    Usage:
        def test_login(fresh_page):
            fresh_page.goto("/login")
            # No session - test login flow
    """
    context = browser.new_context(**browser_context_args)
    apply_route_blocks(context)
    apply_context_listeners(context)
    page = context.new_page()

    yield page

    context.close()


def _navigate_with_fallback(page, url: str, username: str, password: str,
                             session_file: Path, browser, use_new_nav: bool) -> bool:
    """Navigate to url with 60s timeout; falls back to fresh login on failure."""
    from pages.ewm.login_page import LoginPage as STPLoginPage

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
            login_pg = STPLoginPage(page)
            if use_new_nav:
                login_pg.navigate_to_new_nav()
            else:
                login_pg.navigate()
            login_pg.accept_cookies()
            login_pg.enter_username(username)
            login_pg.enter_password(password)
            login_pg.click_sign_in()
            login_pg.submit_login_form()
            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            page.context.storage_state(path=str(session_file))
            print("[NAV] Fresh login successful, session saved")
            return True
        except Exception as fallback_err:
            print(f"[NAV] Fallback login also failed: {fallback_err}")
            return False


@pytest.fixture
def page(context, browser, test_context, request):
    """STP session-based page fixture with role-aware authentication and session persistence."""
    from datetime import datetime
    from pages.ewm.login_page import LoginPage as STPLoginPage
    from utils.settings import Settings as STPSettings

    stp_settings = STPSettings(env=os.getenv("TEST_ENV", "test11"))
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    if "test_data" in test_context:
        test_data = test_context["test_data"]
        print("[SESSION] Using test data from test_context (role-based)")
    else:
        print("[SESSION] WARNING: test_context['test_data'] not found, using default")
        test_data = {}

    username = test_data.get("username", "default_user")
    current_role = test_data.get("role", "default")

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

    NEW_NAV_ROLES = ["manage_bene", "secondary_login"]

    if session_file.exists():
        print(f"\n[SESSION] Loading saved session for: {username}")
        context_with_session = browser.new_context(
            storage_state=str(session_file), ignore_https_errors=True
        )
        page = context_with_session.new_page()

        current_role = test_data.get("role", "")
        use_new_nav = current_role in NEW_NAV_ROLES

        if use_new_nav:
            base_url = "https://app.test01.assetmark.com/clients"
            print(f"[SESSION] Role '{current_role}' - Using new nav URL")
        else:
            base_url = stp_settings.login_url.replace("/ewmLogin/account/login", "/en.aspx")

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

        if "login" in current_url.lower():
            print("[SESSION] Session expired! Redirected to login page.")
            print("[SESSION] Deleting expired session and re-logging in...")
            page.close()
            context_with_session.close()
            session_file.unlink()
        else:
            print("[SESSION] Session activated - already logged in!")
            try:
                page_content = page.content()
                if username not in page_content:
                    print("[SESSION] WARNING: Session may be for a different user. Forcing re-login...")
                    page.close()
                    context_with_session.close()
                    session_file.unlink()
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

    if not session_file.exists():
        print(f"\n[SESSION] No session found for: {username}")
        print("[SESSION] Logging in and creating session...")

        page = context.new_page()
        current_role = test_data.get("role", "")
        use_new_nav = current_role in NEW_NAV_ROLES

        try:
            login_page = STPLoginPage(page)
            if use_new_nav:
                print(f"[SESSION] Role '{current_role}' requires new navigation")
                login_page.navigate_to_new_nav()
                nav_type = "new nav"
            else:
                login_page.navigate()
                nav_type = "standard"

            print(f"[SESSION] Using {nav_type} navigation")
            login_page.accept_cookies()
            login_page.enter_username(username)
            login_page.enter_password(test_data.get("password", "default_password"))
            login_page.click_sign_in()
            login_page.submit_login_form()

            print(f"[SESSION] Login completed for: {username}")

            current_url = page.url
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

        yield page
        page.close()


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_all_sessions(browser, all_test_data, request):
    """
    Pre-create session files ONLY for roles used in the current test run.
    For BDD tests: Skips auto-creation (roles are loaded dynamically in steps).
    For parametrized tests: Creates sessions for detected roles.
    Autouse=True means it runs automatically before any tests.
    """
    from datetime import datetime
    from pages.ewm.login_page import LoginPage as STPLoginPage

    AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Collect unique roles from the test session
    roles_to_create = set()

    if hasattr(request.session, 'items'):
        for item in request.session.items:
            if hasattr(item, 'callspec') and hasattr(item.callspec, 'params'):
                if 'role' in item.callspec.params:
                    roles_to_create.add(item.callspec.params['role'])

    # For BDD tests, skip auto-session creation (roles are loaded dynamically)
    if not roles_to_create:
        logger.info("[SESSION SETUP] BDD test detected - skipping auto-session creation")
        logger.info("[SESSION SETUP] Sessions will be created on-demand for efficiency")
        yield
        return

    print(f"\n{'=' * 60}")
    print(f"[SESSION SETUP] Pre-creating sessions for roles: {sorted(roles_to_create)}")
    print(f"{'=' * 60}")

    created_sessions = []
    NEW_NAV_ROLES = ["manage_bene", "secondary_login"]

    for test_data_row in all_test_data:
        role = test_data_row.get("role", "unknown")
        if role not in roles_to_create:
            continue

        username = test_data_row.get("username", "unknown")
        password = test_data_row.get("password", "")
        use_new_nav = role in NEW_NAV_ROLES
        session_file = AUTH_STATE_DIR / f"{username}_{role}.json"

        if session_file.exists():
            file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
            if file_age.total_seconds() / 3600 < 8:
                print(f"[SESSION SETUP] \u2713 Session exists for {username} (role: {role})")
                created_sessions.append((username, role, False))
                continue
            else:
                print(f"[SESSION SETUP] Session expired for {username}, recreating...")
                session_file.unlink()

        try:
            nav_type = "new nav" if use_new_nav else "standard"
            print(f"[SESSION SETUP] Creating session for {username} (role: {role}, nav: {nav_type})...")

            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            login_page = STPLoginPage(page)
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
                print(f"[SESSION SETUP] \u2713 Session saved: {username}")
                created_sessions.append((username, role, True))
            else:
                print(f"[SESSION SETUP] \u2717 Login failed for {username}")
                created_sessions.append((username, role, False))

            page.close()
            context.close()

        except Exception as e:
            print(f"[SESSION SETUP] \u2717 Error creating session for {username}: {e}")
            created_sessions.append((username, role, False))

    print(f"{'=' * 60}")
    print("[SESSION SETUP] Summary:")
    check_mark = '\u2713'
    cross_mark = '\u2717'
    for username, role, success in created_sessions:
        mark = check_mark if success else cross_mark
        print(f"  {mark} {username} (role: {role})")
    print(f"{'=' * 60}\n")

    yield
