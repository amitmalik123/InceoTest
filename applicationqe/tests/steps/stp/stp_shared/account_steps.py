import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from pages.stp.shared.account_detail_page import AccountDetailPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Searching for client: {client_id}")
    account_list_page.search_client(client_id)


@when("I select the client account")
def select_client_account(page: Page, account_list_page, test_context):
    """Select the specified account for the client"""
    account_name = test_context["test_data"]["account_name"]
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Selecting account: {account_name}")
    account_list_page.select_account(account_name, client_id)


@then("I should see the Account Detail page")
def verify_account_detail_page_loaded(page: Page, account_detail_page):
    """Verify Account Detail page is loaded"""
    logger.info("Verifying Account Detail page is loaded")
    account_detail_page.navigate()
    page.wait_for_load_state("domcontentloaded")


@when("User should click on Manage Beneficiaries link on Account Detail Page and redirect to manage bene page")
def click_manage_beneficiaries_link(page: Page, account_detail_page: AccountDetailPage, test_context):
    """Click on Manage Beneficiaries link and verify redirect to manage beneficiaries page"""
    with allure.step("Click on Manage Beneficiaries link and redirect to manage bene page"):
        # Use iframe context if it was stored by previous step
        if 'account_detail_page_iframe' in test_context:
            iframe_context = test_context['account_detail_page_iframe']
            account_detail_page = AccountDetailPage(iframe_context)
            logger.info("Using stored iframe context for Manage Beneficiaries link")
        
        logger.info("Clicking on Manage Beneficiaries link")
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Before Manage Beneficiaries Click", attachment_type=allure.attachment_type.PNG
        )
        
        # Click the Manage Beneficiaries link
        account_detail_page.manage_beneficiaries_link.click()
        
        # Wait for redirect and new page to load
        page.wait_for_load_state('networkidle', timeout=15000)
        logger.info(f"Redirected to Manage Beneficiaries page. Current URL: {page.url}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="After Manage Beneficiaries Redirect", attachment_type=allure.attachment_type.PNG
        )
