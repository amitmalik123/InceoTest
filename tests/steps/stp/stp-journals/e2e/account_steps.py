import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I search for the client')
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    with allure.step(f"Search for client {test_context['test_data']['client_id']}"):
        logger.info(f"Searching for client: {test_context['test_data']['client_id']}")
        allure.attach(test_context['test_data']['client_id'], name="Client ID", attachment_type=allure.attachment_type.TEXT)
        account_list_page.search_client(test_context['test_data']['client_id'])
        page.wait_for_timeout(1000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account List After Search", attachment_type=allure.attachment_type.PNG)


@when('I select the client account')
def select_client_account(account_list_page, test_context):
    """Select the specified account for the client"""
    with allure.step(f"Select account {test_context['test_data']['account_name']}"):
        logger.info(f"Selecting account: {test_context['test_data']['account_name']}")
        allure.attach(test_context['test_data']['account_name'], name="Account Name", attachment_type=allure.attachment_type.TEXT)
        account_list_page.select_account(
            test_context['test_data']['account_name'],
            test_context['test_data']['client_id']
        )


@then('I should see the Account Detail page')
def verify_account_detail_page_loaded(page: Page, account_detail_page):
    """Verify Account Detail page is loaded"""
    with allure.step("Verify Account Detail page"):
        account_detail_page.navigate()
        page.wait_for_timeout(1000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account Detail Page", attachment_type=allure.attachment_type.PNG)
        logger.info("Account Detail page loaded")

