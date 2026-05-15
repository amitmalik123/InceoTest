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

from config.oam.settings import Settings, get_settings
from pages.oam.login_page import LoginPage
from fixtures.browser_fixtures import apply_context_listeners, apply_route_blocks

# Use centralized Settings singleton
settings = get_settings()

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


# Load application configurations from YAML
APP_CONFIGS = _load_app_configs(settings)


def _get_session_file(
    username: str, app_name: str, worker_id: str, role: Optional[str] = None
) -> Path:
    """
    Generate session file path based on role, username, app, and worker.
    Format: {role}_{app_name}_{username}_{worker_id}.json
    """
    # Build session file name with role prefix if available

    # if role:
    #     base_name = f"{role}_{app_name}_{username}"
    # else:
    #     base_name = f"{app_name}_{username}"

    base_name = f"{username}"

    if worker_id != "master":
        return AUTH_STATE_DIR / f"{base_name}_{worker_id}.json"
    return AUTH_STATE_DIR / f"{base_name}.json"


def _dismiss_ketch_consent(page: Page) -> None:
    """
    Dismiss Ketch cookie consent dialog ("We value your privacy") if present.
    This appears after SSO login on eWealthManager pages.
    """
    try:
        accept_btn = page.get_by_role("button", name="Accept All")
        if accept_btn.count() > 0 and accept_btn.first.is_visible(timeout=3000):
            print("[SESSION] Ketch cookie consent detected - clicking 'Accept All'")
            accept_btn.first.click(timeout=5000)
            page.wait_for_timeout(500)
            print("[SESSION] Ketch cookie consent dismissed")
    except Exception:
        pass  # No Ketch consent present, continue


def _perform_login(page: Page, app_config: AppConfig, test_data: dict) -> bool:
    """
    Perform login using the app-specific login page.
    Takes screenshot on failure for diagnostics.

    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        # Derive base_url from login_url (strip the path portion)
        from urllib.parse import urlparse

        parsed = urlparse(app_config.login_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/"

        username = test_data.get("username", "default_user")
        password = test_data.get("password", "default_password")
        
        print(f"[SESSION] Logging in with: {username}")
        
        login_page = app_config.login_page_class(page, base_url=base_url)
        login_page.navigate()
        print(f"[SESSION] Navigated to: {page.url}")
        
        login_page.accept_cookies()
        print("[SESSION] Cookies accepted")
        
        login_page.enter_username(username)
        print("[SESSION] Username entered")
        
        login_page.enter_password(password)
        print("[SESSION] Password entered")
        
        login_page.click_sign_in()
        print("[SESSION] Sign-in clicked, waiting for navigation...")

        # Check if login successful:
        # After SSO, we may land on a different domain than home_url
        # (e.g. ewm3.assetmark.net instead of ewealthmanager.com)
        # Success = no longer on a login/SSO page
        current_url = page.url
        page_title = page.title()
        print(f"[SESSION] Post-login URL: {current_url}")
        print(f"[SESSION] Post-login page title: {page_title}")
        
        # login.assetmark.com is the Silo/prod SSO domain (Azure AD B2C / Okta)
        login_indicators = ["account/login", "ewmlogin", "test-login.assetmark.com", "login.assetmark.com"]
        is_still_on_login = any(ind in current_url.lower() for ind in login_indicators)
        
        if not is_still_on_login:
            print("[SESSION] Login successful - navigated away from login page")
            return True
        else:
            print(f"[SESSION] Login failed - still on login page: {current_url}")
            print(f"[SESSION] Page title: {page_title}")
            
            # Capture page content for debugging
            try:
                page_text = page.inner_text()
                print(f"[SESSION] Page text content (first 500 chars): {page_text[:500]}")
            except Exception as e:
                print(f"[SESSION] Could not get page text: {e}")
            
            # Take screenshot of failed login for diagnostics
            try:
                screenshot = page.screenshot()
                print("[SESSION] Screenshot taken for failed login")
                # Store for later attachment if needed
                return False
            except Exception as screenshot_err:
                print(f"[SESSION] Could not take screenshot: {screenshot_err}")
            return False
            
    except Exception as e:
        print(f"[SESSION] Login error: {type(e).__name__}: {e}")
        # Try to take screenshot for diagnostics
        try:
            screenshot = page.screenshot()
            print(f"[SESSION] Screenshot of error state: {len(screenshot)} bytes")
        except Exception as screenshot_err:
            print(f"[SESSION] Could not take screenshot of error: {screenshot_err}")
        return False


@pytest.fixture
def authenticated_page(browser, browser_context_args, test_data, request) -> Generator[Page, None, None]:
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

    # Validate test_data early - missing credentials will fail login
    if not test_data:
        raise ValueError(
            "test_data fixture is empty or None. Check that test_data fixture is properly configured "
            "and test CSV data is loaded."
        )
    
    username = test_data.get("username")
    password = test_data.get("password")
    if not username or not password:
        raise ValueError(
            f"test_data missing credentials. Username: {username}, Password: {'*' * len(password or '')}\n"
            f"Full test_data: {list(test_data.keys())}\n"
            f"Check that CSV data matches scenario name."
        )

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Get app from marker or use default
    app_marker = request.node.get_closest_marker("app")
    app_name = app_marker.args[0] if app_marker else "ewm"

    # Get app configuration
    if app_name not in APP_CONFIGS:
        raise ValueError(f"Unknown app: {app_name}. Available: {list(APP_CONFIGS.keys())}")

    app_config = APP_CONFIGS[app_name]
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
        page.goto(app_config.home_url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Dismiss Ketch cookie consent if it appears after navigation
        _dismiss_ketch_consent(page)

        # Verify session is still valid - check we're not on a login/SSO page
        # login.assetmark.com is the Silo/prod SSO domain (Azure AD B2C / Okta)
        login_indicators = ["account/login", "ewmlogin", "test-login.assetmark.com", "login.assetmark.com"]
        is_on_login = any(ind in page.url.lower() for ind in login_indicators)
        if not is_on_login:
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

    # No session or expired - perform login in TEMPORARY context
    if not session_file.exists():
        print(f"[SESSION] No valid session, logging in to {app_name}...")

        # Create temporary context for login (no video/trace needed)
        temp_context = browser.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()

        login_success = _perform_login(temp_page, app_config, test_data)

        if login_success:
            # Save session from login context
            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            temp_context.storage_state(path=str(session_file))
            print("[SESSION] Login successful! Session saved.")
        else:
            print("[SESSION] Login failed - still on login page")
            # Take screenshot of failed login state for diagnostics and ATTACH TO ALLURE
            screenshot_bytes = None
            try:
                screenshot_bytes = temp_page.screenshot()
                print(f"[SESSION] Failed login screenshot captured ({len(screenshot_bytes)} bytes)")
                # ATTACH to Allure report
                import allure
                allure.attach(
                    screenshot_bytes,
                    name="Failed Login Screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
                print("[SESSION] Screenshot attached to Allure report")
            except Exception as e:
                print(f"[SESSION] Could not capture/attach failed login screenshot: {e}")
            
            # Also capture HTML source for debugging
            try:
                html_source = temp_page.content()
                import allure
                allure.attach(
                    html_source,
                    name="Failed Login Page HTML",
                    attachment_type=allure.attachment_type.HTML,
                )
                print("[SESSION] HTML source attached to Allure report")
            except Exception as e:
                print(f"[SESSION] Could not capture HTML: {e}")
            
            temp_page.close()
            temp_context.close()
            
            # Provide detailed error message with diagnostic info
            error_msg = (
                f"Login failed - cannot proceed without authentication\n"
                f"  App: {app_name}\n"
                f"  Username: {username}\n"
                f"  Login URL: {app_config.login_url}\n"
                f"  Final URL: {temp_page.url}\n"
                f"  See Allure report for login screenshot and HTML source"
            )
            raise RuntimeError(error_msg)

        # Close temporary login context
        print("[SESSION] Closing login context...")
        temp_page.close()
        temp_context.close()

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
        page.goto(app_config.home_url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Dismiss Ketch cookie consent if it appears after login
        _dismiss_ketch_consent(page)
        print("[SESSION] Ready for test execution!")

        yield page

        _stop_tracing(context, tracing_option, request)
        page.close()
        context.close()


def _stop_tracing(context, tracing_option: str, request) -> None:
    """
    Stop tracing and save the trace file based on the tracing option.
    
    Report Directory:
    - OAM tests: traces stored in reports/oam/traces
    - Other tests: traces stored in reports/traces
    """
    if tracing_option == "off":
        return

    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    # Also check for setup failure
    if not failed:
        failed = getattr(getattr(request.node, "rep_setup", None), "failed", False)

    if tracing_option == "on" or (tracing_option == "retain-on-failure" and failed):
        trace_dir = Path("reports/traces")
        trace_dir.mkdir(parents=True, exist_ok=True)
        trace_path = trace_dir / f"{request.node.name}.zip"
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
def fresh_page(browser, browser_context_args) -> Generator[Page, None, None]:
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
