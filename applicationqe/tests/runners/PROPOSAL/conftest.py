"""
PROPOSAL-specific conftest.

Overrides test_context so PROPOSAL tests always authenticate as Internal Admin,
pulling credentials from config/PROPOSAL/env.{env}.yaml instead of the Excel
file. PROPOSAL steps carry their own workflow data inline — no Excel row needed.

Also overrides authenticated_page to inject the Switch ID step after login,
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
def authenticated_page(browser, browser_context_args, request) -> Generator[Page, None, None]:
    """
    PROPOSAL override of authenticated_page.

    Extends the base auth flow with a Switch ID step so the session is saved
    with the advisor context already selected — required because the admin
    account lands on /ChangeRole/i after login, making /en.aspx return 404
    until an advisor is impersonated.
    """
    from config.settings import get_settings
    from fixtures.auth_fixtures import (
        APP_CONFIGS,
        _get_session_file,
        _perform_login,
        _stop_tracing,
    )
    from fixtures.browser_fixtures import apply_context_listeners, apply_route_blocks
    from filelock import FileLock

    settings = get_settings()
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    app_name = "ewm"
    app_config = APP_CONFIGS[app_name]
    test_data = {"UserRole": "Internal Admin"}

    username = settings.internal_admin_username
    advisor_id = settings.config.get("test_user", {}).get("advisor_id", "")

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
    print(f"[SESSION] Advisor ID: {advisor_id}")
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
                    login_success = _perform_login(temp_page, app_config, test_data)

                    if login_success and advisor_id:
                        # Perform Switch ID before saving session state
                        try:
                            print(f"[SESSION] Performing Switch ID to: {advisor_id}")
                            from pages.PROPOSAL.switch_id_page import SwitchIDPage
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

    print(f"[SESSION] Navigating to: {app_config.home_url}")
    page.goto(app_config.home_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    print("[SESSION] Ready for test execution!")

    yield page

    _stop_tracing(context, tracing_option, request)
    page.close()
    context.close()


# ---------------------------------------------------------------------------
# Session teardown
# Each task runs in its own browser context concurrently via ThreadPoolExecutor.
# To add future cleanup tasks: define a new _teardown_* function and add it
# to the `tasks` dict in proposal_teardown.
# ---------------------------------------------------------------------------

TEST_PORTFOLIOS = ["Widget Test Portfolio", "E2E Test Portfolio"]
TEST_CLIENTS = ["Guy NAWE2E", "Guy PeE2E", "Guy NAWTMS"]


def _teardown_portfolios(session_file: Path, headless: bool = True) -> None:
    """Delete test portfolios via the Portfolio Engine API.
    Navigates only to the home page — no Portfolio Engine popup needed.
    Runs in its own thread with a dedicated sync_playwright instance.
    """
    from playwright.sync_api import sync_playwright
    from urllib.parse import urlparse
    from config.settings import get_settings

    settings = get_settings()
    home_url = settings.config.get("applications", {}).get("ewm", {}).get("home_url", "")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()
        try:
            page.goto(home_url, wait_until="domcontentloaded")
            parsed = urlparse(page.url)
            origin = f"{parsed.scheme}://{parsed.netloc}"

            resp = page.request.get(f"{origin}/api/pe/v2/portfolios")
            if not resp.ok:
                logger.warning(f"[TEARDOWN] Portfolio API returned {resp.status}")
                return

            data = resp.json()
            portfolios = data if isinstance(data, list) else [data]
            to_delete = [pf for pf in portfolios if pf.get("name") in TEST_PORTFOLIOS]

            if not to_delete:
                logger.info("[TEARDOWN] No test portfolios found")
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
    """Delete test clients via EwM UI.
    Runs in its own thread with a dedicated sync_playwright instance.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as _PwTimeout
    from pages.PROPOSAL.ewm_page import EwmPage
    from utils.PROPOSAL.helper_functions import navigate_to_home_page

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=str(session_file), ignore_https_errors=True)
        page = context.new_page()
        ewm_page = EwmPage(page)
        try:
            for client_name in TEST_CLIENTS:
                try:
                    # Grid displays "LastName, FirstName"
                    parts = client_name.split(" ")
                    display_name = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else client_name

                    navigate_to_home_page(page)
                    ewm_page.search_for_client(client_name)

                    try:
                        ewm_page.no_results_message.wait_for(state="visible", timeout=5000)
                        logger.info(f"[TEARDOWN] Client not found: {client_name}")
                        continue
                    except _PwTimeout:
                        pass  # Results exist

                    # Count once — deleted rows stay visible in the grid until re-login,
                    # so we step through each row by index rather than always clicking .first.
                    count = ewm_page.client_grid_cells.filter(has_text=display_name).count()

                    for i in range(count):
                        if i > 0:
                            # Navigate back to the search page; grid is stale but row order
                            # is preserved — previously deleted rows stay at their index.
                            navigate_to_home_page(page)
                            ewm_page.search_for_client(client_name)

                        cell = ewm_page.client_grid_cells.filter(has_text=display_name).nth(i)
                        try:
                            cell.wait_for(state="visible", timeout=5000)
                            cell.click()
                            ewm_page.delete_client_link.wait_for(state="visible", timeout=5000)
                            ewm_page.delete_client()
                            logger.info(f"[TEARDOWN] Deleted client: {client_name}")
                        except _PwTimeout:
                            logger.warning(f"[TEARDOWN] Skipping stale row {i} for {client_name}")
                            continue
                except Exception as e:
                    logger.warning(f"[TEARDOWN] Could not delete client {client_name}: {e}")
        finally:
            page.close()
            context.close()
            browser.close()


@pytest.fixture(scope="session", autouse=True)
def proposal_teardown(pytestconfig):
    """Run all teardown tasks concurrently after the full PROPOSAL suite."""
    yield  # All tests run first

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from config.settings import get_settings
    from fixtures.auth_fixtures import _get_session_file
    from utils.PROPOSAL.proposal_pdf_utils import cleanup_downloads

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
