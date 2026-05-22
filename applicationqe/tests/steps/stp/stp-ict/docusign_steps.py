import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from locators.stp.stp_ict import ict_docusign_locators as docusign_locators
from utils.logger import setup_logger

logger = setup_logger(__name__)


@then("User should be redirected to the DocuSign page")
def user_should_be_redirected_to_docusign_page(page: Page, docusign_page, test_context):
    logger.info(">>> STEP: User should be redirected to the DocuSign page")
    docusign_page.verify_docusign_page_loaded(timeout=30000)
    current_url = page.url
    assert docusign_locators.DOCUSIGN_URL_PATTERN in current_url, \
        f"[FAIL] DocuSignPage: Expected URL to contain '{docusign_locators.DOCUSIGN_URL_PATTERN}', got '{current_url}'"
    logger.info(f"Confirmed redirected to DocuSign: {current_url}")
    with allure.step("DocuSign page loaded"):
        allure.attach(page.screenshot(), name="DocuSign Page Loaded",
                      attachment_type=allure.attachment_type.PNG)


@then("Verify docusign Review and continue dialog text")
def verify_docusign_review_and_continue_dialog_text(page: Page, docusign_page, test_context):
    logger.info(">>> STEP: Verify docusign Review and continue dialog text")
    actual_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
    test_data = test_context.get("test_data", {})
    expected_text = test_data.get("Expected_docusign_ReviewAndContinue_Text", "").strip()
    if expected_text:
        assert expected_text in actual_text, \
            f"[FAIL] DocuSignPage: Review dialog text mismatch. Expected to contain: '{expected_text}', got: '{actual_text}'"
        logger.info("Review and Continue dialog text verified against test data")
    else:
        logger.info(f"No expected text in test data. Dialog text recorded: '{actual_text[:100]}'")
    with allure.step("DocuSign Review Dialog"):
        allure.attach(page.screenshot(), name="DocuSign Review Dialog",
                      attachment_type=allure.attachment_type.PNG)


@then("Verify As_authorized_by stamp presence")
def verify_as_authorized_by_stamp_presence(page: Page, docusign_page, test_context):
    logger.info(">>> STEP: Verify As_authorized_by stamp presence")
    STAMPING_TEXT = "As authorized by"
    test_data = test_context.get("test_data", {})
    as_authorized_by_value = test_data.get("As_authorized_by_stamp_present", "").strip()
    if not as_authorized_by_value:
        logger.info("'As_authorized_by_stamp_present' not in test data — skipping stamp check")
        return
    should_be_present = as_authorized_by_value.lower() == "yes"
    stamping_locator = docusign_page.get_stamping_element(STAMPING_TEXT)
    count = stamping_locator.count()
    if should_be_present:
        assert count > 0, \
            f"[FAIL] DocuSignPage: '{STAMPING_TEXT}' stamp expected PRESENT but not found"
        logger.info(f"'{STAMPING_TEXT}' stamp confirmed present (count={count})")
    else:
        assert count == 0, \
            f"[FAIL] DocuSignPage: '{STAMPING_TEXT}' stamp expected ABSENT but found {count}"
        logger.info(f"'{STAMPING_TEXT}' stamp correctly absent")


@when("User confirm and Continue the docusign Review and continue dialog")
def user_confirm_and_continue(page: Page, docusign_page):
    logger.info(">>> STEP: User confirm and Continue the docusign Review and continue dialog")
    docusign_page.check_ersd_consent_checkbox(timeout=10000)
    docusign_page.click_ersd_continue_button(timeout=10000)
    logger.info("ERSD consent confirmed and Continue clicked")
    with allure.step("ERSD Confirmed"):
        allure.attach(page.screenshot(), name="DocuSign - ERSD Confirmed",
                      attachment_type=allure.attachment_type.PNG)


@when("User Finish the DocuSign process")
def user_finish_the_docusign_process(page: Page, docusign_page):
    logger.info(">>> STEP: User Finish the DocuSign process")
    docusign_page.click_finish_button(timeout=10000)
    logger.info("DocuSign process finished")
    with allure.step("DocuSign Finished"):
        allure.attach(page.screenshot(), name="DocuSign - Finished",
                      attachment_type=allure.attachment_type.PNG)


@then("Verify request pop up")
def verify_request_popup(page: Page, docusign_page):
    logger.info(">>> STEP: Verify request pop up")
    docusign_page.verify_request_submitted_popup(timeout=15000)
    logger.info("Request Submitted popup verified")
    with allure.step("Request Submitted Popup"):
        allure.attach(page.screenshot(), name="Request Submitted Popup",
                      attachment_type=allure.attachment_type.PNG)


@when("User click on D number")
def user_click_on_d_number(page: Page, docusign_page, test_context):
    logger.info(">>> STEP: User click on D number")
    d_number = docusign_page.get_d_number_and_click(test_context)
    logger.info(f"D# {d_number} clicked — navigating to Tracking Center")
    with allure.step(f"D# {d_number} clicked"):
        allure.attach(page.screenshot(), name="D# Link Clicked",
                      attachment_type=allure.attachment_type.PNG)


@then("User should be redirected to Tracking Center Item Detail page")
def user_should_be_redirected_to_tracking_center(page: Page):
    logger.info(">>> STEP: User should be redirected to Tracking Center Item Detail page")
    page.wait_for_url(lambda url: 'TrackingCenter' in url, timeout=30000)
    page.wait_for_load_state('domcontentloaded', timeout=30000)
    logger.info(f"Tracking Center Item Detail reached: {page.url}")
    with allure.step("Tracking Center Loaded"):
        allure.attach(page.screenshot(), name="Tracking Center Item Detail",
                      attachment_type=allure.attachment_type.PNG)
