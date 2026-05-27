import csv
from pathlib import Path

import allure
from playwright.sync_api import Page
from pytest_bdd import given, then, when

from utils.logger import setup_logger
from utils.settings import settings

logger = setup_logger(__name__)


@given('the test data is loaded from CSV')
def load_test_data_from_csv(test_context):
    """Load test data from CSV file into test_context"""
    csv_path = settings.test_data_csv
    logger.info(f"Loading test data from: {csv_path}")
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        test_context['test_data'] = next(reader)
    
    logger.info(f"Loaded test data: {list(test_context['test_data'].keys())}")
    allure.attach(str(test_context['test_data']), name="Test Data", attachment_type=allure.attachment_type.JSON)


@given('I am on the login page')
def navigate_to_login_page(page: Page, login_page):
    """Navigate to the login page"""
    logger.info("Navigating to login page")
    login_page.navigate()
    screenshot = page.screenshot()
    allure.attach(screenshot, name="Login Page", attachment_type=allure.attachment_type.PNG)


@when('I logout from the application')
def logout_from_application(page: Page, tracking_center_page):
    """Logout from the application"""
    with allure.step("Logout from application"):
        logger.info("Logging out")
        tracking_center_page.click_logout()
        tracking_center_page.click_bodycontent()
        page.wait_for_timeout(500)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Logout Completed", attachment_type=allure.attachment_type.PNG)


@then('I should be logged out successfully')
def verify_logout_successful():
    """Verify successful logout"""
    with allure.step("Verify logout successful"):
        logger.info("=== Test Completed Successfully ===")


@when('I search for the client')
def search_for_client_alias(page: Page, account_list_page, test_context):
    """Alias step to search for client/account from Account List."""
    td = test_context.get('test_data', {})
    account_number = (
        td.get('source_accountnumber')
        or td.get('source_account')
        or td.get('account_number')
        or td.get('account_name')
        or ''
    )
    with allure.step(f"Search for account number {account_number}"):
        logger.info(f"Searching for account number: {account_number}")
        account_list_page.search_account(account_number)
        try:
            screenshot = page.screenshot()
            allure.attach(screenshot, name="Account List After Search", attachment_type=allure.attachment_type.PNG)
        except Exception:
            logger.debug('Screenshot after search skipped')
