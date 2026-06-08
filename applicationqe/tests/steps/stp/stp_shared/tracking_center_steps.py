import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I navigate to Tracking Center")
def navigate_to_tracking_center(page: Page, tracking_center_page):
    logger.info("Navigating to Tracking Center")
    tracking_center_page.navigate()


@then("I should see the Roth Conversion entry for the client")
def verify_roth_conversion_entry_exists(page: Page, tracking_center_page, test_context):
    logger.info("Verifying Roth Conversion entry in Tracking Center")
    tracking_center_page.verify_account_src(test_context["test_data"]["client_id"])


@then(parsers.parse('I should see "{text}" in the tracking details'))
def verify_text_in_tracking_details(page: Page, tracking_center_page, text):
    with allure.step(f"Verify tracking details contain: {text}"):
        logger.info(f"Verifying tracking details: {text}")
        tracking_center_page.verify_roth_str(text)
        page.wait_for_timeout(500)
        allure.attach(
            page.screenshot(),
            name="Tracking Center - Roth Conversion Verified",
            attachment_type=allure.attachment_type.PNG,
        )


@when(parsers.parse('User visits Tracking center to verify Address details for "{test}" and click View Btn'))
@then(parsers.parse('User visits Tracking center to verify Address details for "{test}" and click View Btn'))
def visit_tracking_center_verify_address_and_click_view(page: Page, tracking_center_page, test_context: dict, test: str):
    with allure.step(f"Visit Tracking center to verify Address details for {test} and click View Btn"):
        test_data = test_context.get('test_data', {})
        tracking_center_page.navigate_and_verify_address_then_view(
            item_number=test_context.get('address_change_item_number', ''),
            test=test,
            mailing_after=test_context.get('mailing_after', []),
            legal_after=test_context.get('legal_after', []),
            display_only_mailing=test_context.get('display_only_mailing_address', False),
            agent_id=test_data.get('advisor_id', ''),
        )
        allure.attach(
            page.screenshot(),
            name=f"Tracking Center - View Documents - {test}",
            attachment_type=allure.attachment_type.PNG,
        )
