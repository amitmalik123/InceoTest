from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I click on Account Wizard")
def click_on_account_wizard(authenticated_page: Page, account_detail_page):
    """Click on Account Wizard link"""
    logger.info("Clicking Account Wizard")
    account_detail_page.click_account_wizard()


@when("I select Funded account option")
def select_funded_account_option(authenticated_page: Page, account_detail_page):
    """Select the Funded radio option"""
    logger.info("Selecting Funded account option")
    account_detail_page.select_funded_radio()


@when("I select Move Assets Between Accounts")
def select_move_assets_between_accounts(authenticated_page: Page, account_detail_page):
    """Select Move Assets Between Accounts option"""
    logger.info("Selecting Move Assets Between Accounts")
    account_detail_page.select_move_assets_between_accounts()


@when("I select Roth IRA Conversion")
def select_roth_ira_conversion(authenticated_page: Page, account_detail_page):
    """Select Roth IRA Conversion option"""
    logger.info("Selecting Roth IRA Conversion")
    account_detail_page.select_roth_ira_conversion()


@when("I click Next on Account Wizard")
def click_next_on_account_wizard(authenticated_page: Page, account_detail_page):
    """Click Next button on Account Wizard"""
    logger.info("Clicking Next on Account Wizard")
    account_detail_page.click_next()


@then("I should see the Roth Conversion page")
def verify_roth_conversion_page_loaded(authenticated_page: Page, roth_conversion_page):
    """Verify Roth Conversion page is loaded"""
    logger.info("Verifying Roth Conversion page is loaded")
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)


@then("User should pick account information from the selected account")
def pick_account_information_from_selected_account(authenticated_page: Page, account_wizard_page):
    """Pick account information from the selected account"""
    account_details_mimo1 = account_wizard_page.fetch_selected_account_information()
    account_name = account_details_mimo1[0]
    logger.info(f"Account information fetched - Account Name: {account_name}")


@then(
    "User checks Toggle Functionality for Specific User and Click on Add ACH Instructions on Account Wizard"
)
def check_and_click_add_ach_instruction_link(authenticated_page: Page, account_wizard_page):
    """Check toggle functionality and click Add ACH Instructions link"""
    logger.info("Checking the Functionality of the Toggle Button")
    account_wizard_page.click_add_ach_instructions()
    logger.info("Add ACH Instructions link clicked")
