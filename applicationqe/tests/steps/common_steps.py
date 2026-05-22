from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from config.settings import get_settings
from fixtures.browser_fixtures import apply_route_blocks, apply_context_listeners
from pages.login_page import LoginPage
from pages.ewm.lookup_page import LookupPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('Internal Admin user impersonates into an agent account "{mode}"'))
def internal_admin_impersonates_agent(lookup_page, test_context, mode, browser_context_args):
    """Login as Internal Admin, select role, and impersonate into an agent account.

    Modes:
        click agent           – navigates the current tab to admin login and impersonates.
        click broker dealer   – opens a new browser context so the agent's current page
                                is preserved, then logs in as admin, searches the agent,
                                and clicks the SSO user ID for Broker Dealer.
    """
    test_data = test_context.get("test_data", {})
    user_id = test_data.get("UserID")
    if not user_id:
        raise ValueError(
            "Could not resolve agent id from test data. "
            "Expected column: UserID"
        )

    settings = get_settings()

    if mode == "click broker dealer":
        current_page = lookup_page.page
        browser = current_page.context.browser

        new_context = browser.new_context(**browser_context_args)
        apply_route_blocks(new_context)
        apply_context_listeners(new_context)
        page = new_context.new_page()

        # Store for subsequent steps
        test_context["admin_browser_context"] = new_context
        test_context["admin_page"] = page

        admin_lookup = LookupPage(page)
    else:
        page = lookup_page.page
        admin_lookup = lookup_page

    # Login as Internal Admin
    with logger.step("Login as Internal Admin", page=page, screenshot=True):
        login_page = LoginPage(page, base_url=settings.base_url)
        login_page.navigate()
        login_page.accept_cookies()
        login_page.enter_username(settings.internal_admin_username)
        login_page.enter_password(settings.internal_admin_password)
        login_page.click_sign_in()
        login_page.accept_cookies()
        logger.info(f"Internal Admin login completed. URL: {page.url}")

    with logger.step("Internal Admin impersonates into an agent account", page=page, screenshot=True):
        logger.info(f"Choosing admin role and impersonating agent: {user_id}")
        admin_lookup.choose_role()
        if mode == "click broker dealer":
            admin_lookup.impersonate_broker_dealer(user_id)
        else:
            admin_lookup.impersonate_agent(user_id)


@then("User clicks on SSO user ID")
def user_clicks_on_sso_user_id(lookup_page):
    """Click the SSO user ID link on the lookup page."""
    with logger.step("User clicks on SSO user ID", page=lookup_page.page, screenshot=True):
        lookup_page.click_sso_user_id()


@then("Navigate to tracking center page")
def navigate_to_tracking_center_page(tracking_center_page):
    """Navigate to tracking center page by clicking the Tracking Center tab"""
    with logger.step("Navigate to tracking center page", page=tracking_center_page.page):
        logger.info("Navigating to tracking center page")
        tracking_center_page.click_tracking_center_tab()


@when(parsers.parse('User wait for "{seconds}" seconds'))
def user_wait_for_seconds(page: Page, seconds: str):
    """Wait for the specified number of seconds"""
    seconds_int = int(seconds)
    wait_time = seconds_int * 1000
    with logger.step(f"User wait for {seconds_int} seconds", page=page):
        logger.info(f"Waiting for {seconds_int} second(s) ({wait_time} ms)")
        page.wait_for_timeout(wait_time)


@when("User logs in as agent in a new browser context")
def step_login_agent_new_context(page: Page, test_context, browser_context_args):
    """Create a new browser context and login as agent using Excel credentials."""
    test_data = test_context.get("test_data", {})
    settings = get_settings()
    logger.info("[STEP] User logs in as agent in a new browser context - BEGIN")

    browser = page.context.browser
    assert browser, "Browser instance is unexpectedly None"

    new_context = browser.new_context(**browser_context_args)
    apply_route_blocks(new_context)
    apply_context_listeners(new_context)
    new_page = new_context.new_page()

    base_url = settings.base_url
    login_page = LoginPage(new_page, base_url=base_url)
    login_page.navigate()
    login_page.accept_cookies()

    username = (test_data.get("username") or test_data.get("UserName") or "").strip()
    password = (test_data.get("password") or test_data.get("Password") or "").strip()
    login_page.enter_username(username)
    login_page.enter_password(password)
    login_page.click_sign_in()

    logger.info(f"[new-ctx] Agent login successful. URL: {new_page.url}")

    # Wait for post-login redirects to settle before navigating
    new_page.wait_for_load_state("domcontentloaded", timeout=15000)

    # Navigate to /home with retry — pipeline environments can be slow
    for attempt in range(1, 4):
        try:
            logger.info(f"[new-ctx] Navigating to /home (attempt {attempt}/3)")
            new_page.goto(f"{base_url}home", wait_until="domcontentloaded", timeout=60000)
            break
        except Exception as e:
            logger.warning(f"[new-ctx] goto /home attempt {attempt} failed: {e}")
            if attempt == 3:
                raise
            new_page.wait_for_timeout(attempt * 5000)

    new_page.wait_for_load_state("domcontentloaded", timeout=15000)

    # Store in test_context for subsequent steps
    test_context["new_browser_context"] = new_context
    test_context["new_page"] = new_page

    logger.info("[STEP] User logs in as agent in a new browser context - END")
