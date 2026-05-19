from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I navigate to Tracking Center")
def navigate_to_tracking_center(authenticated_page: Page, tracking_center_page):
    """Navigate to Tracking Center"""
    logger.info("Navigating to Tracking Center")
    tracking_center_page.navigate()


@then("I should see the Roth Conversion entry for the client")
def verify_roth_conversion_entry_exists(
    authenticated_page: Page, tracking_center_page, test_context
):
    """Verify the Roth Conversion entry exists in Tracking Center"""
    logger.info("Verifying Roth Conversion entry in Tracking Center")
    tracking_center_page.verify_account_src(test_context["test_data"]["client_id"])


@then(parsers.parse('I should see "{text}" in the tracking details'))
def verify_text_in_tracking_details(authenticated_page: Page, tracking_center_page, text):
    """Verify specific text in tracking details"""
    logger.info(f"Verifying tracking details contain: {text}")
    tracking_center_page.verify_roth_str(text)
