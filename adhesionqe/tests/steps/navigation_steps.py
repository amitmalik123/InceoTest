from playwright.sync_api import Page
from pytest_bdd import then, when

from pages.account_detail_page import AccountDetailPage
from pages.account_list_page import AccountListPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@then("I should see the Account List page")
def verify_account_list_page_loaded(authenticated_page: Page):
    """Verify Account List page is loaded"""
    logger.info(f"Verifying Account List page loaded - URL: {authenticated_page.url}")
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)


@then("User is on the accountlist tab and search with the accountNo")
def verify_account_list_page_loaded_and_search(
    authenticated_page: Page, account_list_page: AccountListPage, test_context
):
    """Verify Account List page is loaded and search for client"""
    client_id = test_context["test_data"]["client_id"]
    #  client_id = test_context["excel_data"]["Shell"][1]["clientId"]
    logger.info(
        f"Account list loaded at {authenticated_page.url} - Searching for client: {client_id}"
    )
    account_list_page.search_client(client_id)


@then("User should click on searched account and navigate to account wizard page")
def click_searched_account_and_navigate_to_wizard(
    authenticated_page: Page,
    account_list_page: AccountListPage,
    account_detail_page: AccountDetailPage,
    test_context,
):
    """Click on searched account and navigate to account wizard page"""
    logger.info(f"Selecting account and navigating to wizard from {authenticated_page.url}")
    account_list_page.select_account(
        test_context["test_data"]["account_name"], test_context["test_data"]["client_id"]
    )
    account_detail_page.click_account_wizard()


@then("I verify account wizard page is loaded")
def verify_account_wizard_page_is_loaded(authenticated_page: Page, account_wizard_page):
    """Verify Account Wizard page is loaded"""
    logger.info(f"Verifying Account Wizard page is loaded at {authenticated_page.url}")
    account_wizard_page.verify_account_wizard_page_loaded()
