import allure
from playwright.sync_api import Page
from pytest_bdd import when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I select account number option')
def select_account_number_option(page: Page, account_number_page, test_context):
    """Read account_number_option from test data and act accordingly."""
    option = test_context.get('test_data', {}).get('account_number_option', 'retain')
    with allure.step(f"Select account number option: {option}"):
        logger.info(f"Account number option from test data: {option}")
        account_number_page.select_account_number_option(option)
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Account Number - {option}", attachment_type=allure.attachment_type.PNG)
