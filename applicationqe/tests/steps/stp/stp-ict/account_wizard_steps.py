import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I click on Account Wizard')
def click_on_account_wizard(page: Page, account_detail_page):
    """Click on Account Wizard link"""
    with allure.step("Click on Account Wizard"):
        logger.info("Clicking Account Wizard")
        account_detail_page.click_account_wizard()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account Wizard Modal", attachment_type=allure.attachment_type.PNG)


@when('I select Funded account option')
def select_funded_account_option(account_detail_page):
    """Select the Funded radio option"""
    with allure.step("Select Funded account option"):
        logger.info("Selecting Funded account option")
        account_detail_page.select_funded_radio()


@when('I select Move Assets Between Accounts')
def select_move_assets_between_accounts(account_detail_page):
    """Select Move Assets Between Accounts option"""
    with allure.step("Select Move Assets Between Accounts"):
        logger.info("Selecting Move Assets Between Accounts")
        account_detail_page.select_move_assets_between_accounts()


@when('I select Roth IRA Conversion')
def select_roth_ira_conversion(page: Page, account_detail_page):
    """Select Roth IRA Conversion option"""
    with allure.step("Select Roth IRA Conversion"):
        logger.info("Selecting Roth IRA Conversion")
        account_detail_page.select_roth_ira_conversion()
        page.wait_for_timeout(500)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account Wizard - Roth IRA Selected", attachment_type=allure.attachment_type.PNG)


@when('I click Next on Account Wizard')
def click_next_on_account_wizard(account_detail_page):
    """Click Next button on Account Wizard"""
    with allure.step("Click Next on Account Wizard"):
        logger.info("Clicking Next on Account Wizard")
        account_detail_page.click_next()


@when('I click on Change Investments')
def click_on_change_investments(page: Page, account_detail_page):
    """Click Change Investments — browser navigates automatically to SelectAccount with correct BngClientID."""
    with allure.step("Click on Change Investments"):
        logger.info("Clicking on Change Investments")
        account_detail_page.click_change_investment()
        allure.attach(page.screenshot(), name="Change Investments Clicked", attachment_type=allure.attachment_type.PNG)


@when('I click on Source account')
def click_on_source_account(page: Page, select_source_account_page, test_context):
    """Select source account checkbox and continue.

    The browser is already on SelectAccount?BngClientID=... after clicking
    Change Investments — do NOT navigate again or the BngClientID is lost.
    """
    with allure.step("Click on Source account"):
        # Wait for the page the browser already navigated to
        page.wait_for_load_state('networkidle', timeout=30000)
        logger.info(f"Select Source Account page ready. URL: {page.url}")

        account_number = (
            test_context.get('test_data', {}).get('source_accountnumber')
            or test_context.get('test_data', {}).get('source_account')
            or test_context.get('test_data', {}).get('account_number')
        )
        logger.info(f"Selecting source account: {account_number}")
        select_source_account_page.select_account_checkbox(account_number)
        select_source_account_page.click_next()
        allure.attach(page.screenshot(), name="Source Account Selected", attachment_type=allure.attachment_type.PNG)


@then('I should see the Roth Conversion page')
def verify_roth_conversion_page_loaded(page: Page, roth_conversion_page):
    """Verify Roth Conversion page is loaded"""
    with allure.step("Verify Roth Conversion page"):
        # Page should already be on Roth Conversion after clicking Next
        # Just wait for it to load instead of navigating
        page.wait_for_load_state('networkidle', timeout=30000)
        page.wait_for_timeout(1000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Roth Conversion Page - Initial", attachment_type=allure.attachment_type.PNG)
        logger.info("Roth Conversion page loaded")
