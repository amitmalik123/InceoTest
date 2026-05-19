from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

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


@then("I should see the Account Detail page")
def verify_account_detail_page_loaded(authenticated_page: Page, account_detail_page):
    """Verify Account Detail page is loaded"""
    logger.info("Verifying Account Detail page is loaded")
    account_detail_page.navigate()
    authenticated_page.wait_for_load_state("domcontentloaded")
