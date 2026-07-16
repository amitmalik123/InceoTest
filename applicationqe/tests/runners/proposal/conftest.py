"""
PROPOSAL-specific conftest.

Overrides test_context so PROPOSAL tests always authenticate as Internal Admin,
pulling credentials from config/proposal/env.{env}.yaml instead of the Excel
file. PROPOSAL steps carry their own workflow data inline — no Excel row needed.

Also overrides page fixture to inject the Switch ID step after login,
so the session is saved with advisor context already selected.
"""

import os
import logging
from collections.abc import Generator
from pathlib import Path
from datetime import datetime

import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


@pytest.fixture
def test_context():
    """Always resolve to Internal Admin for PROPOSAL tests."""
    return {"test_data": {"UserRole": "Internal Admin"}}


@pytest.fixture
def page(browser, browser_context_args, request) -> Generator[Page, None, None]:
    """
    PROPOSAL override of page fixture.

    Extends the base auth flow with a Switch ID step so the session is saved
    with the advisor context already selected — required because the admin
    account lands on /ChangeRole/i after login, making /en.aspx return 404
    until an advisor is impersonated.
    """
    from config.proposal.settings import get_settings
    from fixtures.auth_fixtures import (
        AppConfig,
        _get_session_file,
        _perform_login,
        _stop_tracing,
    )
    from fixtures.browser_fixtures import apply_context_listeners, apply_route_blocks
    from filelock import FileLock

    context = None
    page = None
    
    try:
        settings = get_settings()
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

        app_name = "ewm"

        # Build app_config from proposal settings (not from shared APP_CONFIGS dict)
        ewm_cfg = settings.get_app_config("ewm")
        login_page_class_name = ewm_cfg.get("login_page_class", "LoginPage")
        
        # Dynamically import the correct login page class
        if login_page_class_name == "NavbarLoginPage":
            from pages.ewm.navbar_login_page import NavbarLoginPage
            login_page_class = NavbarLoginPage
            is_navbar = True
        else:
            from pages.ewm.login_page import LoginPage
            login_page_class = LoginPage
            is_navbar = False
        
        app_config = AppConfig(
            name="ewm",
            login_url=ewm_cfg["login_url"],
            home_url=ewm_cfg["home_url"],
            login_page_class=login_page_class,
            timeout=ewm_cfg.get("timeout", 30000),
        )

        # Pass credentials directly so _perform_login doesn't fall back to shared settings
        # Test01 uses test_user (regular advisor); legacy uses internal_admin
        if is_navbar:
            test_user = settings.config.get("test_user", {})
            test_data = {
                "username": test_user.get("username") or settings.internal_admin_username,
                "password": test_user.get("password") or settings.internal_admin_password,
            }
            username = test_user.get("username") or settings.internal_admin_username
        else:
            test_data = {
                "username": settings.internal_admin_username,
                "password": settings.internal_admin_password,
            }
            username = settings.internal_admin_username

        advisor_id = settings.config.get("test_user", {}).get("advisor_id", "")
        test_env = os.environ.get("TEST_ENV")
        
        # Only perform Switch ID for legacy test environments (not navbar, not prod)
        # Navbar uses non-admin logins that don't have Switch ID capability
        should_switch_id = advisor_id and not is_navbar and test_env not in ("prod", "production", "silo")

        session_file = _get_session_file(username, app_name, worker_id)
        AUTH_STATE_DIR = Path("tests/.auth")
        session_max_age_hours = 8

        base_ctx_args = {k: v for k, v in browser_context_args.items()}
        tracing_option = request.config.getoption("--tracing", default="off")
        capture_trace = tracing_option in ("on", "retain-on-failure")

        print(f"\n{'=' * 60}")
        print(f"[SESSION] App: {app_name}")
        print(f"[SESSION] Worker: {worker_id}")
        print(f"[SESSION] Username: {username}")
        print(f"[SESSION] Environment: {test_env}")
        print(f"[SESSION] Advisor ID: {advisor_id} (Switch ID: {'yes' if should_switch_id else 'no'})")
        print(f"[SESSION] Session file: {session_file.name}")
        print(f"{'=' * 60}")

        # Expire stale sessions
        if session_file.exists():
            file_age = datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)
            if file_age.total_seconds() / 3600 > session_max_age_hours:
                print(f"[SESSION] Session too old, deleting...")
                session_file.unlink()

        # Try existing session
        if session_file.exists():
            print("[SESSION] Loading saved session...")
            context = browser.new_context(storage_state=str(session_file), **base_ctx_args)
            apply_route_blocks(context)
            apply_context_listeners(context)
            if capture_trace:
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()

            print(f"[SESSION] Navigating to: {app_config.home_url}")
            page.goto(app_config.home_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)

            if (
                "login" not in page.url.lower()
                and "changerole" not in page.url.lower()
                and page.url != "about:blank"
                and not page.url.endswith("/404")
            ):
                print("[SESSION] Session valid! Already authenticated.")
                
                # Progress through sidebar tour if present (for navbar environments on cached sessions)
                if is_navbar:
                    try:
                        modal_container = page.locator('[class*="containerStep"]')
                        if modal_container.is_visible(timeout=2000):
                            # Step 1: Click "Next" button
                            next_btn = page.locator('button:has-text("Next")').first
                            if next_btn.is_visible(timeout=2000):
                                next_btn.click(timeout=5000)
                                print("[SESSION] Clicked Next on sidebar tour (step 1)")
                                page.wait_for_timeout(500)
                            
                            # Step 2: Click "Finish" button
                            finish_btn = page.locator('button:has-text("Finish")').first
                            if finish_btn.is_visible(timeout=2000):
                                finish_btn.click(timeout=5000)
                                print("[SESSION] Clicked Finish on sidebar tour (step 2)")
                                page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"[SESSION] Tour progression skipped on cached session: {e}")
                
                yield page
                _stop_tracing(context, tracing_option, request)
                page.close()
                context.close()
                return
            else:
                print("[SESSION] Session expired, re-authenticating...")
                if capture_trace:
                    context.tracing.stop()
                page.close()
                context.close()
                session_file.unlink()

        # Login + Switch ID, then save session
        if not session_file.exists():
            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            lock_file = session_file.with_suffix(".lock")
            lock = FileLock(str(lock_file), timeout=120)

            with lock:
                if not session_file.exists():
                    print(f"[SESSION] Worker {worker_id} logging in to {app_name}...")

                    login_success = False
                    for attempt in range(1, 4):
                        temp_context = browser.new_context(ignore_https_errors=True)
                        temp_page = temp_context.new_page()
                        
                        # Branch on login type: navbar uses login_application(), legacy uses _perform_login()
                        if is_navbar:
                            try:
                                navbar_login = login_page_class(temp_page)
                                navbar_login.login_application(
                                    test_data["username"],
                                    test_data["password"],
                                )
                                # Wait for post-login landing before proceeding
                                temp_page.wait_for_url("**/dashboard**", timeout=30000)
                                
                                # Dismiss sidebar navigation tour modal by progressing through tour
                                # The tour has 2 steps: "Next" button on step 1, "Finish" button on step 2
                                try:
                                    modal_container = temp_page.locator('[class*="containerStep"]')
                                    if modal_container.is_visible(timeout=2000):
                                        # Step 1: Click "Next" button
                                        next_btn = temp_page.locator('button:has-text("Next")').first
                                        if next_btn.is_visible(timeout=2000):
                                            next_btn.click(timeout=5000)
                                            print("[SESSION] Clicked Next on sidebar tour (step 1)")
                                            temp_page.wait_for_timeout(500)
                                        
                                        # Step 2: Click "Finish" button
                                        finish_btn = temp_page.locator('button:has-text("Finish")').first
                                        if finish_btn.is_visible(timeout=2000):
                                            finish_btn.click(timeout=5000)
                                            print("[SESSION] Clicked Finish on sidebar tour (step 2)")
                                            temp_page.wait_for_timeout(1000)  # Wait for modal to close
                                except Exception as e:
                                    print(f"[SESSION] Tour progression skipped (not visible or already closed): {e}")
                                
                                login_success = True
                            except Exception as e:
                                print(f"[SESSION] Navbar login failed: {e}")
                                login_success = False
                        else:
                            login_success = _perform_login(temp_page, app_config, test_data)

                        if login_success and should_switch_id:
                            # Perform Switch ID before saving session state (only for test environments)
                            try:
                                print(f"[SESSION] Performing Switch ID to: {advisor_id}")
                                from pages.proposal.switch_id_page import SwitchIDPage
                                switch_id = SwitchIDPage(temp_page)
                                switch_id.select_id(advisor_id)
                                print(f"[SESSION] Switch ID complete. URL: {temp_page.url}")
                            except Exception as e:
                                print(f"[SESSION] Switch ID failed: {e}")
                                login_success = False

                        if login_success:
                            temp_context.storage_state(path=str(session_file))
                            print(f"[SESSION] Login + Switch ID successful on attempt {attempt}! Session saved.")
                        else:
                            print(f"[SESSION] Attempt {attempt}/3 failed")

                        temp_page.close()
                        temp_context.close()

                        if login_success:
                            break
                        import time; time.sleep(5 * attempt)

                    if not login_success:
                        raise RuntimeError("Login + Switch ID failed after 3 attempts")
                else:
                    print(f"[SESSION] Worker {worker_id} found session created by another worker.")

        # Create context with saved session (advisor context already set)
        print("[SESSION] Creating new context with saved session...")
        context = browser.new_context(storage_state=str(session_file), **base_ctx_args)
        apply_route_blocks(context)
        apply_context_listeners(context)
        if capture_trace:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        try:
            print(f"[SESSION] Navigating to: {app_config.home_url}")
            page.goto(app_config.home_url, wait_until="domcontentloaded", timeout=30000)
            
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                print(f"[SESSION] networkidle timeout (continuing with domcontentloaded): {e}")
            
            print(f"[SESSION] Page loaded. Current URL: {page.url}")
            
            # Check if we're still on login page
            if "login" in page.url.lower() or page.url.endswith("/404"):
                raise RuntimeError(f"Unexpected page after session load: {page.url}")
            
            print("[SESSION] Ready for test execution!")
            yield page
        finally:
            _stop_tracing(context, tracing_option, request)
            page.close()
            context.close()
    
    except Exception as e:
        print(f"[SESSION] FIXTURE ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        if page:
            page.close()
        if context:
            context.close()
        raise
# Each task runs in its own browser context concurrently via ThreadPoolExecutor.
# To add future cleanup tasks: define a new _teardown_* function and add it
# to the `tasks` dict in proposal_teardown.
# ---------------------------------------------------------------------------

TEST_PORTFOLIOS = ["Widget Test Portfolio", "E2E Test Portfolio"]
TEST_CLIENTS = ["Guy NAWE2E", "Guy PeE2E", "Guy NAWTMS"]


def _teardown_portfolios(session_file: Path, headless: bool = True) -> None:
    """Delete test portfolios via the Portfolio Engine API.
    Handles both navbar and legacy environments:
    - Navbar: Portfolio Engine API at ewm.{domain}/api/pe/v2/...
    - Legacy: Portfolio Engine API at {app_domain}/api/pe/v2/...
    Runs in its own thread with a dedicated sync_playwright instance.
    """
    from playwright.sync_api import sync_playwright
    from urllib.parse import urlparse
    from config.proposal.settings import get_settings

    settings = get_settings()
    ewm_cfg = settings.config.get("applications", {}).get("ewm", {})
    home_url = ewm_cfg.get("home_url", "")
    login_page_class_name = ewm_cfg.get("login_page_class", "LoginPage")
    is_navbar = login_page_class_name == "NavbarLoginPage"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()
        try:
            page.goto(home_url, wait_until="domcontentloaded")
            parsed = urlparse(page.url)
            
            # Determine API origin based on environment type
            if is_navbar:
                # For navbar, Portfolio Engine API is at ewm subdomain
                domain = parsed.netloc.replace("app.", "ewm.")
                origin = f"{parsed.scheme}://{domain}"
            else:
                # For legacy, API is at app origin
                origin = f"{parsed.scheme}://{parsed.netloc}"

            resp = page.request.get(f"{origin}/api/pe/v2/portfolios")
            if not resp.ok:
                logger.warning(f"[TEARDOWN] Portfolio API ({origin}) returned {resp.status}")
                return

            data = resp.json()
            portfolios = data if isinstance(data, list) else [data]
            to_delete = [pf for pf in portfolios if pf.get("name") in TEST_PORTFOLIOS]

            if not to_delete:
                logger.info(f"[TEARDOWN] No test portfolios found (API: {origin})")
                return

            for pf in to_delete:
                del_resp = page.request.delete(f"{origin}/api/pe/v2/portfolio/{pf['id']}")
                if del_resp.ok:
                    logger.info(f"[TEARDOWN] Deleted portfolio: {pf['name']}")
                else:
                    logger.warning(f"[TEARDOWN] Failed to delete portfolio {pf['name']}: {del_resp.status}")
        finally:
            page.close()
            context.close()
            browser.close()


def _teardown_clients(session_file: Path, headless: bool = True) -> None:
    """Delete test clients via Account Wizard UI.
    Searches for clients and deletes them one by one. The table updates
    dynamically after each delete. Uses the counter element to detect when
    no more results are available (more efficient than timeouts).
    Runs in its own thread with a dedicated sync_playwright instance.
    
    Handles both navbar and legacy environments:
    - Navbar: Navigate to dashboard, click "Manage Accounts" to load NAW in iframe
    - Legacy: Navigate directly to NAW URL
    """
    from playwright.sync_api import sync_playwright
    from pages.proposal.new_account_wizard_page import NewAccountWizardPage
    from pages.proposal.ewm_page import EwmPage
    from config.proposal.settings import get_settings

    settings = get_settings()
    ewm_cfg = settings.config.get("applications", {}).get("ewm", {})
    home_url = ewm_cfg.get("home_url", "")
    login_page_class_name = ewm_cfg.get("login_page_class", "LoginPage")
    is_navbar = login_page_class_name == "NavbarLoginPage"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()
        try:
            for client_name in TEST_CLIENTS:
                # Convert "FirstName LastName" → "LastName, FirstName" for the search box
                parts = client_name.split()
                if len(parts) >= 2:
                    search_name = f"{' '.join(parts[1:])}, {parts[0]}"
                else:
                    search_name = client_name

                try:
                    # Navigate to Account Wizard using helper function
                    from pages.proposal.helper_functions import navigate_to_account_wizard
                    navigate_to_account_wizard(page, home_url, is_navbar)
                    
                    # Create wizard_page AFTER navigation so active_root() detects the iframe
                    wizard_page = NewAccountWizardPage(page)
                    
                    # Loop until the counter reports 0 results
                    while True:
                        wizard_page.search_for_client_in_account_wizard(search_name)

                        total_count = wizard_page.get_total_clients_count()
                        if total_count == 0:
                            logger.info(f"[TEARDOWN] No more clients found: {search_name}")
                            break

                        try:
                            first_row = wizard_page.get_first_client_row()
                            first_row.click()
                            page.wait_for_load_state("domcontentloaded", timeout=10000)
                        except Exception as e:
                            logger.warning(f"[TEARDOWN] Failed to click client row: {e}")
                            break

                        try:
                            wizard_page.delete_client_from_account_wizard()
                            logger.info(f"[TEARDOWN] Deleted client: {search_name} ({total_count} remaining before delete)")
                        except Exception as e:
                            logger.warning(f"[TEARDOWN] Failed to delete client {search_name}: {e}")
                            break

                except Exception as e:
                    logger.warning(f"[TEARDOWN] Could not delete client {search_name}: {e}")
        finally:
            page.close()
            context.close()
            browser.close()


@pytest.fixture(scope="session", autouse=True)
def proposal_teardown(pytestconfig):
    """Run all teardown tasks concurrently after the full PROPOSAL suite."""
    yield  # All tests run first

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from config.proposal.settings import get_settings
    from fixtures.auth_fixtures import _get_session_file
    from pages.proposal.proposal_pdf_utils import cleanup_downloads

    settings = get_settings()
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    session_file = _get_session_file(settings.internal_admin_username, "ewm", worker_id)

    if not session_file.exists():
        logger.warning("[TEARDOWN] No session file found, skipping browser teardown")
        cleanup_downloads()
        return

    headless = not pytestconfig.getoption("--headed", default=False)

    # Add new teardown tasks here — each runs concurrently in its own thread
    # with its own sync_playwright instance. Non-browser tasks need no browser.
    tasks = {
        "portfolios": lambda: _teardown_portfolios(session_file, headless=headless),
        "clients":    lambda: _teardown_clients(session_file, headless=headless),
        "downloads":  cleanup_downloads,
    }

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {executor.submit(fn): name for name, fn in tasks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
                logger.info(f"[TEARDOWN] {name}: complete")
            except Exception as e:
                logger.warning(f"[TEARDOWN] {name}: failed — {e}")

    # Final cleanup: delete the session auth file
    try:
        if session_file.exists():
            session_file.unlink()
            logger.info(f"[TEARDOWN] Deleted session file: {session_file}")
    except Exception as e:
        logger.warning(f"[TEARDOWN] Failed to delete session file: {e}")

