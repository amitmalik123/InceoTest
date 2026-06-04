from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I select the destination account")
def select_destination_account(page: Page, roth_conversion_page, test_context):
    """Select the destination account for conversion"""
    destination_account = test_context["test_data"]["destination_account"]
    logger.info(f"Selecting destination account: {destination_account}")
    roth_conversion_page.select_destination_account(destination_account)


@when("I verify the destination account is correct")
def verify_destination_account_correct(page: Page, roth_conversion_page, test_context):
    """Verify the selected destination account"""
    logger.info("Verifying destination account")
    roth_conversion_page.verify_destination_account(
        test_context["test_data"]["destination_account"]
    )


@when("I click Next on destination selection")
def click_next_on_destination_selection(page: Page, roth_conversion_page):
    """Click Next after selecting destination"""
    logger.info("Clicking Next on destination selection")
    roth_conversion_page.verify_next_button_visible()
    roth_conversion_page.click_next()


@when("I select Convert Portion option")
def select_convert_portion_option(page: Page, roth_conversion_page):
    """Select the Convert Portion option"""
    logger.info("Selecting Convert Portion option")
    roth_conversion_page.select_convert_portion()


@when("I enter the conversion amount")
def enter_conversion_amount(roth_conversion_page, test_context):
    """Enter the conversion amount"""
    amount = test_context["test_data"]["conversion_amount"]
    logger.info(f"Entering conversion amount: {amount}")
    roth_conversion_page.enter_amount(amount)


@when("I select Do Not Withhold for federal and state taxes")
def select_do_not_withhold_taxes(page: Page, roth_conversion_page):
    """Select Do Not Withhold for both federal and state"""
    logger.info("Selecting Do Not Withhold for federal and state taxes")
    roth_conversion_page.select_do_not_withhold()


@when("I click Next on conversion details")
def click_next_on_conversion_details(page: Page, roth_conversion_page):
    """Click Next after entering conversion details"""
    logger.info("Clicking Next on conversion details")
    roth_conversion_page.click_next()


@then("I should either see STR review message or proceed to tracking")
def handle_str_review_or_proceed(page: Page, roth_conversion_page):
    """Handle STR review if it appears"""
    try:
        str_message = "Your request will require additional review to ensure the existing source and/or destination account is still eligible due to recent actions on the account(s). Please refer to the Tracking Center for any additional requirements and an updated status."
        logger.info("Checking for STR review requirement")
        roth_conversion_page.verify_str_button_visible()
        roth_conversion_page.verify_str_message(str_message)
        roth_conversion_page.click_str_button()
        logger.info("STR button found and clicked - submission requires additional review")
    except Exception:
        logger.info(
            "STR button not found (expected for some accounts) - Proceeding without STR review"
        )
