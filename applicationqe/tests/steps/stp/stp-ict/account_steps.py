import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


def _get_search_account_number(test_context) -> str:
    test_data = test_context.get('test_data', {})
    return str(
        test_data.get('account_number')
        or test_data.get('source_accountnumber')
        or test_data.get('client_id')
        or ''
    ).strip()


@when('I search for the account number')
def search_for_account_number(page: Page, account_list_page, test_context):
    """Search for account using account number in Account List search box."""
    account_number = _get_search_account_number(test_context)
    with allure.step(f"Search for account number {account_number}"):
        logger.info(f"Searching for account number: {account_number}")
        allure.attach(account_number, name="Account Number", attachment_type=allure.attachment_type.TEXT)
        account_list_page.search_account(account_number)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account List After Search", attachment_type=allure.attachment_type.PNG)


@when('I search for the client')
def search_for_client(page: Page, account_list_page, test_context):
    """Alias step: Search for the client (maps to account number search)."""
    return search_for_account_number(page, account_list_page, test_context)


@when('I click on the searched account row')
def click_searched_account_row(page: Page, account_list_page, test_context):
    """Click the row that matches the searched account number."""
    account_number = _get_search_account_number(test_context)
    account_display = test_context.get('test_data', {}).get('account_name') or account_number
    with allure.step(f"Select account {account_display}"):
        logger.info(f"Selecting account: {account_display}")
        allure.attach(account_display, name="Account Name", attachment_type=allure.attachment_type.TEXT)
        allure.attach(account_number, name="Searched Account Number", attachment_type=allure.attachment_type.TEXT)
        account_list_page.select_account(
            account_display,
            account_number
        )
        allure.attach(page.screenshot(), name="Account Row Selected", attachment_type=allure.attachment_type.PNG)


@when('I select the client account')
def select_client_account(page: Page, account_list_page, test_context):
    """Alias step to select the client account from search results."""
    return click_searched_account_row(page, account_list_page, test_context)


@then('I should see the Account Detail page')
def verify_account_detail_page_loaded(page: Page, account_detail_page):
    """Verify Account Detail page is loaded after selecting searched row."""
    with allure.step("Verify Account Detail page"):
        account_detail_page.wait_for_account_detail_loaded()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account Detail Page", attachment_type=allure.attachment_type.PNG)
        logger.info("Account Detail page loaded")
