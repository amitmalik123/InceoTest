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

import os
from pathlib import Path

import pytest
from playwright.sync_api import Page

from pages.stp.shared.login_page import LoginPage
from utils.settings import Settings

# Get environment from environment variable or use default (test11)
env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=env)

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


def _get_session_file(username: str, app_name: str, worker_id: str, role: str = None) -> Path:
    """
    Generate session file path based on role, username, app, and worker.
    Format: {role}_{app_name}_{username}_{worker_id}.json
    """
    # Build session file name with role prefix if available
    if role:
        base_name = f"{role}_{app_name}_{username}"
    else:
        base_name = f"{app_name}_{username}"

    if worker_id != "master":
        return AUTH_STATE_DIR / f"{base_name}_{worker_id}.json"
    return AUTH_STATE_DIR / f"{base_name}.json"


def _perform_login(page: Page, app_config: AppConfig, test_data: dict) -> bool:
    """
    Perform login using the app-specific login page.

    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        login_page = app_config.login_page_class(page)
        login_page.navigate()
        login_page.accept_cookies()
        login_page.enter_username(test_data.get("username", "default_user"))
        login_page.enter_password(test_data.get("password", "default_password"))
        login_page.click_sign_in()
        #    login_page.submit_login_form()

        # Check if login successful
        current_url = page.url
        return "login" not in current_url.lower()
    except Exception as e:
        print(f"[SESSION] Login error: {e}")
        return False


@pytest.fixture
def authenticated_page(browser, test_data, request):
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

    # Get app configuration
    if app_name not in APP_CONFIGS:
        raise ValueError(f"Unknown app: {app_name}. Available: {list(APP_CONFIGS.keys())}")

    app_config = APP_CONFIGS[app_name]
    username = test_data.get("username", "default_user")
    role = test_data.get("role", None)  # Get role from test data
    session_file = _get_session_file(username, app_name, worker_id, role)
    session_max_age_hours = 8

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
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()

        # Navigate to home URL to activate session
        print(f"[SESSION] Navigating to: {app_config.home_url}")
        page.goto(app_config.home_url, timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Verify session is still valid
        if "login" not in page.url.lower():
            print("[SESSION] Session valid! Already authenticated.")
            yield page
            page.close()
            context.close()
            return
        else:
            # Session expired - close this context and delete session file
            print("[SESSION] Session expired, deleting and re-authenticating...")
            page.close()
            context.close()
            session_file.unlink()
            # Fall through to login block below

    # No session or expired - perform login in TEMPORARY context
    if not session_file.exists():
        print(f"[SESSION] No valid session, logging in to {app_name}...")

        # Create temporary context for login
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
            temp_page.close()
            temp_context.close()
            raise RuntimeError("Login failed - cannot proceed without authentication")

        # Close temporary login context
        print("[SESSION] Closing login context...")
        temp_page.close()
        temp_context.close()

        # Create NEW context with saved session (consistent with session-exists path)
        print("[SESSION] Creating new context with saved session...")
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()

        # Navigate to home page
        print(f"[SESSION] Navigating to: {app_config.home_url}")
        page.goto(app_config.home_url, timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        print("[SESSION] Ready for test execution!")

        yield page

        page.close()
        context.close()


# Backward compatible 'page' fixture (uses default app)
@pytest.fixture
def page(authenticated_page):
    """
    Default page fixture - uses 'ewm' app for backward compatibility.

    For multi-app tests, use 'authenticated_page' with @pytest.mark.app() instead.
    """
    return authenticated_page


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
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    yield page

    context.close()
