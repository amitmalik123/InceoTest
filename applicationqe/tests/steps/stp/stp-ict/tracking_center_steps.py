import time

import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then

from utils.logger import setup_logger

logger = setup_logger(__name__)


@then("Item Detail D number should be same as request submitted pop up D number")
def verify_item_detail_d_number_matches_request_submitted_pop_up_d_number(page: Page, tracking_center_page, test_context):
    """Verify D-number on Item Detail matches the D-number stored from Request Submitted popup."""
    with allure.step("Verify D number matches request submitted pop up D number"):
        logger.info(">>> STEP: Verify D number matches request submitted pop up D number")
        expected_d_number = test_context.get('d_number', '')
        if not expected_d_number:
            raise AssertionError(
                "D-number was not stored from request submitted popup. "
                "Ensure 'User click on D number' step ran before this verification."
            )
        logger.info(f"Expected D-number: {expected_d_number}")
        # Save HTML for diagnostics
        try:
            with open('reports/tracking_center_detail.html', 'w', encoding='utf-8') as f:
                f.write(tracking_center_page.page.content())
        except Exception:
            pass
        actual_d_number = tracking_center_page.get_d_number()
        logger.info(f"Actual D-number from Tracking Center: {actual_d_number}")
        assert expected_d_number == actual_d_number, \
            f"[FAIL] TrackingCenter: D-number mismatch — Expected: '{expected_d_number}', Actual: '{actual_d_number}'"
        logger.info(f"D-number verified: {actual_d_number}")
        allure.attach(page.screenshot(), name="Tracking Center - D Number Verified",
                      attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('Verify Tracking Center Item Detail status should be "{expected_status}"'))
def verify_tracking_center_item_detail_status(page: Page, tracking_center_page, expected_status):
    """Poll (refresh) until status matches expected value, up to 60 seconds."""
    with allure.step(f'Verify Tracking Center Item Detail status should be "{expected_status}"'):
        logger.info(f'>>> STEP: Verify Tracking Center Item Detail status should be "{expected_status}"')
        max_attempts = 12
        delay_seconds = 5.0
        last_actual = ""
        for attempt in range(1, max_attempts + 1):
            try:
                tracking_center_page.refresh_page()
                last_actual = tracking_center_page.get_status()
                logger.info(f"Attempt {attempt}/{max_attempts}: status='{last_actual}'")
                if last_actual == expected_status:
                    logger.info(f"Status matches expected: '{expected_status}'")
                    allure.attach(page.screenshot(), name=f"Status - {expected_status}",
                                  attachment_type=allure.attachment_type.PNG)
                    return
            except Exception as e:
                logger.warning(f"Attempt {attempt} error: {e}")
            if attempt < max_attempts:
                time.sleep(delay_seconds)
        raise AssertionError(
            f"[FAIL] TrackingCenter: Status '{expected_status}' not reached after {max_attempts} attempts. "
            f"Last actual: '{last_actual}'"
        )


@then("I should see the item number as B# in Tracking Center")
def verify_item_number_becomes_b_number(page: Page, tracking_center_page):
    """Poll until the item number flips from D# to B# (allow up to 10 minutes)."""
    with allure.step("Wait for item number to become B#"):
        logger.info(">>> STEP: I should see the item number as B# in Tracking Center")
        b_number = tracking_center_page.wait_for_b_number(timeout_ms=600000, poll_ms=10000)
        logger.info(f"Item number flipped to B#: {b_number}")
        allure.attach(page.screenshot(), name=f"B Number Confirmed - {b_number}",
                      attachment_type=allure.attachment_type.PNG)
