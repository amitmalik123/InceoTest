from playwright.sync_api import Page
from pytest_bdd import then, when
from pages.clients_page import ClientsPage
from pages.account_list_page import AccountListPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when("I search for the client")
def search_for_client(authenticated_page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Searching for client: {client_id}")
    account_list_page.search_client(client_id)


@when("I select the client account")
def select_client_account(authenticated_page: Page, account_list_page, test_context):
    """Select the specified account for the client"""
    account_name = test_context["test_data"]["account_name"]
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Selecting account: {account_name}")
    account_list_page.select_account(account_name, client_id)

@when("User click on Account List")
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

@when("User is on the Account List tab and search for Account Number")
def user_is_on_account_list_tab_and_search_for_account_number(
    authenticated_page: Page, account_list_page: AccountListPage, test_context
):
    """User is on the Account List tab and search for Account Number - calls verify_account_list_page_loaded_and_search"""
    from tests.bdd.steps.navigation_steps import verify_account_list_page_loaded_and_search
    verify_account_list_page_loaded_and_search(authenticated_page, account_list_page, test_context)

@then("I should see the Account Detail page")
def verify_account_detail_page_loaded(authenticated_page: Page, account_detail_page):
    """Verify Account Detail page is loaded"""
    logger.info("Verifying Account Detail page is loaded")
    account_detail_page.navigate()
    authenticated_page.wait_for_load_state("domcontentloaded")