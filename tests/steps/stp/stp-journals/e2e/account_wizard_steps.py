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
        page.wait_for_timeout(1000)
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

