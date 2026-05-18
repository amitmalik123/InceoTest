from playwright.sync_api import Page
from pytest_bdd import then, when

from pages.PR.clients_page import ClientsPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when("I navigate to Clients menu")
def navigate_to_clients_menu(authenticated_page: Page, clients_page: ClientsPage, soft_assert):
    """Navigate to clients menu and verify page is ready"""
    logger.info("Navigating to clients menu")
    clients_page.navigate()
    clients_page.click_clients()

    # Hard assertions - fail immediately if critical navigation broke
    Assertions.assert_true(
        "ewealthmanager.com" in authenticated_page.url,
        "Not on eWealthManager domain after navigation",
    )
    Assertions.assert_true(
        "login" not in authenticated_page.url.lower(), "Redirected to login page unexpectedly"
    )

    # Soft assertions - collect UI checks, reported together at test end
    soft_assert.assert_true(clients_page.clients_link.is_visible(), "Clients link not visible")
    soft_assert.assert_true(
        clients_page.account_list_link.is_visible(), "Account List link not visible"
    )
    soft_assert.assert_true(
        authenticated_page.title() != "", "Page title is empty after navigation"
    )

    logger.info(f"Clients menu navigation verified - URL: {authenticated_page.url}")


@when("I click on Account List")
def click_on_account_list(authenticated_page: Page, clients_page: ClientsPage, soft_assert):
    """Click on Account List and verify page loads"""
    logger.info("Clicking Account List")
    clients_page.click_account_list()

    # Wait for navigation to complete
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)

    # Hard assertion - page must load
    Assertions.assert_true(
        authenticated_page.url is not None, "Page URL is None after clicking Account List"
    )

    # Soft assertions - verify Account List page elements
    soft_assert.assert_true(
        "login" not in authenticated_page.url.lower(),
        "Redirected to login page after clicking Account List",
    )
    soft_assert.assert_true(
        authenticated_page.title() != "", "Page title is empty on Account List page"
    )

    logger.info(f"Account List page loaded - URL: {authenticated_page.url}")
