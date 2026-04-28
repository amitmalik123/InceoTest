import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I select the destination account')
def select_destination_account(roth_conversion_page, test_context):
    """Select the destination account for conversion"""
    with allure.step(f"Select destination account {test_context['test_data']['destination_account']}"):
        logger.info(f"Selecting destination account: {test_context['test_data']['destination_account']}")
        allure.attach(test_context['test_data']['destination_account'], name="Destination Account", attachment_type=allure.attachment_type.TEXT)
        roth_conversion_page.select_destination_account(test_context['test_data']['destination_account'])


@when('I verify the destination account is correct')
def verify_destination_account_correct(page: Page, roth_conversion_page, test_context):
    """Verify the selected destination account"""
    with allure.step("Verify destination account"):
        logger.info("Verifying destination account")
        roth_conversion_page.verify_destination_account(test_context['test_data']['destination_account'])
        page.wait_for_timeout(500)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Roth Conversion - Destination Selected", attachment_type=allure.attachment_type.PNG)


@when('I click Next on destination selection')
def click_next_on_destination_selection(roth_conversion_page):
    """Click Next after selecting destination"""
    with allure.step("Click Next on destination selection"):
        logger.info("Clicking Next on destination selection")
        roth_conversion_page.verify_next_button_visible()
        roth_conversion_page.click_next()


@when('I select Convert Portion option')
def select_convert_portion_option(page: Page, roth_conversion_page):
    """Select the Convert Portion option"""
    with allure.step("Select Convert Portion option"):
        page.wait_for_timeout(1000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Roth Conversion - Amount Entry Page", attachment_type=allure.attachment_type.PNG)
        logger.info("Selecting Convert Portion option")
        roth_conversion_page.select_convert_portion()


@when('I enter the conversion amount')
def enter_conversion_amount(roth_conversion_page, test_context):
    """Enter the conversion amount"""
    with allure.step(f"Enter conversion amount: {test_context['test_data']['conversion_amount']}"):
        logger.info(f"Entering amount: {test_context['test_data']['conversion_amount']}")
        allure.attach(test_context['test_data']['conversion_amount'], name="Conversion Amount", attachment_type=allure.attachment_type.TEXT)
        roth_conversion_page.enter_amount(test_context['test_data']['conversion_amount'])


@when('I select Do Not Withhold for federal and state taxes')
def select_do_not_withhold_taxes(page: Page, roth_conversion_page):
    """Select Do Not Withhold for both federal and state"""
    with allure.step("Select Do Not Withhold for federal and state"):
        logger.info("Selecting Do Not Withhold for taxes")
        roth_conversion_page.select_do_not_withhold()
        page.wait_for_timeout(500)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Roth Conversion - Amount and Withholding Set", attachment_type=allure.attachment_type.PNG)


@when('I click Next on conversion details')
def click_next_on_conversion_details(page: Page, roth_conversion_page):
    """Click Next after entering conversion details"""
    with allure.step("Click Next on conversion details"):
        logger.info("Clicking Next on conversion details")
        roth_conversion_page.click_next()
        page.wait_for_timeout(1000)


@then('I should either see STR review message or proceed to tracking')
def handle_str_review_or_proceed(page: Page, roth_conversion_page):
    """Handle STR review if it appears"""
    with allure.step("Handle STR review or proceed"):
        try:
            str_message = (
                'Your request will require additional review to ensure the existing source and/or destination account is still eligible due to recent actions on the account(s). Please refer to the Tracking Center for any additional requirements and an updated status.'
            )
            logger.info("Checking for STR review requirement")
            screenshot = page.screenshot()
            allure.attach(screenshot, name="STR Review Message", attachment_type=allure.attachment_type.PNG)
            roth_conversion_page.verify_str_button_visible()
            roth_conversion_page.verify_str_message(str_message)
            roth_conversion_page.click_str_button()
            logger.info("STR button found and clicked - submission requires additional review")
        except Exception as e:
            logger.info(f"STR button not found (this is expected for some accounts): {e}")
            screenshot = page.screenshot()
            allure.attach(screenshot, name="Conversion Submitted (No STR Review)", attachment_type=allure.attachment_type.PNG)
            logger.info("Proceeding without STR review")

