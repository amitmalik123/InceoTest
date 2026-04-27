import csv
import json
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
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in CSV test data file: {csv_path}")

    scenario_name = test_context.get('scenario_name')
    csv_row_number = test_context.get('csv_row_number')
    csv_absolute_row_number = test_context.get('csv_absolute_row_number')
    selected_row = None

    # Absolute CSV row number is 1-based including the header row.
    if isinstance(csv_absolute_row_number, int):
        row_index = csv_absolute_row_number - 2
        if row_index < 0 or row_index >= len(rows):
            raise IndexError(
                f"Requested absolute CSV row {csv_absolute_row_number} is out of range. "
                f"Available absolute rows: 2-{len(rows) + 1}"
            )
        selected_row = rows[row_index]
        logger.info(f"Using configured absolute CSV row #{csv_absolute_row_number} for test data")

    # Row number is 1-based for data rows (excluding header).
    if selected_row is None and isinstance(csv_row_number, int):
        row_index = csv_row_number - 1
        if row_index < 0 or row_index >= len(rows):
            raise IndexError(
                f"Requested CSV row {csv_row_number} is out of range. Available rows: 1-{len(rows)}"
            )
        selected_row = rows[row_index]
        logger.info(f"Using configured CSV row #{csv_row_number} for test data")

    if selected_row is None and scenario_name:
        selected_row = next((row for row in rows if row.get('name') == scenario_name), None)
        if selected_row:
            logger.info(f"Using scenario-matched CSV row for: {scenario_name}")

    if selected_row is None:
        selected_row = rows[0]
        logger.info("Using default CSV row #1 for test data")

    destination_account_name = selected_row.get('accounts.destinationAccountName', '')
    destination_account_number = selected_row.get('accounts.destinationAccountNumber', '')

    if (not destination_account_name or not destination_account_number) and selected_row.get('accounts.destinationAccounts'):
        try:
            destination_accounts = json.loads(selected_row['accounts.destinationAccounts'])
            if destination_accounts:
                first_destination = destination_accounts[0]
                destination_account_name = destination_account_name or first_destination.get('accountName', '')
                destination_account_number = destination_account_number or first_destination.get('accountNumber', '')
        except Exception:
            logger.warning("Could not parse accounts.destinationAccounts JSON from CSV row")

    source_account_name = selected_row.get('accounts.sourceAccountName', '')
    source_account_client_name = selected_row.get('accounts.sourceAccountDetails.clientName', '')
    # Some rows do not populate sourceAccountDetails.clientName; derive a usable search key from account name.
    derived_client_name = source_account_name.split(',', 1)[0].strip() if source_account_name else ''
    client_id = source_account_client_name or derived_client_name

    test_context['test_data'] = {
        'username': selected_row['credentials.username'],
        'password': selected_row['credentials.password'],
        'client_id': client_id,
        'account_name': source_account_name,
        'destination_account': destination_account_name,
        'destination_account_number': destination_account_number,
        'conversion_amount': selected_row['transactionDetails.amount'],
        'urls': {
            'baseUrl': selected_row['urls.baseUrl'],
            'journalTransferUrl': selected_row['urls.journalTransferUrl'],
            'loginUrl': selected_row['urls.loginUrl']
        }
    }
    
    logger.info(f"Loaded test data: {list(test_context['test_data'].keys())}")
    allure.attach(str(test_context['test_data']), name="Test Data", attachment_type=allure.attachment_type.JSON)


@given('I am on the login page')
def navigate_to_login_page(page: Page, login_page):
    """Navigate to the login page"""
    logger.info("Navigating to login page")
    login_page.navigate_to_login(settings.login_url)
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

