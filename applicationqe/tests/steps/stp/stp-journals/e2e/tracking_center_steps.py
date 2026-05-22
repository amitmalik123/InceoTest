import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I navigate to Tracking Center')
def navigate_to_tracking_center(page: Page, tracking_center_page):
    """Navigate to Tracking Center"""
    with allure.step("Navigate to Tracking Center"):
        logger.info("Navigating to Tracking Center")
        tracking_center_page.navigate()
        page.wait_for_timeout(1000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Tracking Center Page", attachment_type=allure.attachment_type.PNG)


@then('I should see the Roth Conversion entry for the client')
def verify_roth_conversion_entry_exists(tracking_center_page, test_context):
    """Verify the Roth Conversion entry exists in Tracking Center"""
    with allure.step("Verify Roth Conversion entry in Tracking Center"):
        logger.info("Verifying Roth Conversion entry")
        tracking_center_page.verify_account_src(test_context['test_data']['client_id'])


@then(parsers.parse('I should see "{text}" in the tracking details'))
def verify_text_in_tracking_details(page: Page, tracking_center_page, text):
    """Verify specific text in tracking details"""
    with allure.step(f"Verify tracking details contain: {text}"):
        logger.info(f"Verifying tracking details: {text}")
        tracking_center_page.verify_roth_str(text)
        page.wait_for_timeout(500)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Tracking Center - Roth Conversion Verified", attachment_type=allure.attachment_type.PNG)

