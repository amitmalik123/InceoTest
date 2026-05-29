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

import pytest
from playwright.sync_api import Page

from config.settings import Settings, get_settings
from pages.oam.login_page import LoginPage
import os

import pytest
from filelock import FileLock
from playwright.sync_api import Page

from config.settings import Settings, get_settings
from pages.login_page import LoginPage
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
            from config.settings import get_settings
            settings = get_settings()
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

        # Wait for SSO redirect chain to complete (Okta → test-login.assetmark.com → app).
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
    app_name = app_marker.args[0] if app_marker else "ewm"

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
        from config.settings import get_settings
        settings = get_settings()
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


@pytest.fixture
def page(authenticated_page: Page) -> Page:
    """Backward-compatible page fixture that returns authenticated page."""
    return authenticated_page
