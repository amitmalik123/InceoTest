"""
DocuSign-related step definitions for BDD tests
"""
import allure
from datetime import datetime
from playwright.sync_api import Page
from pytest_bdd import then, when, parsers

from pages.docusign_page import DocuSignPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions, SoftAssertions

logger = get_allure_logger(__name__)

@when("User confirm and Continue the docusign Review and continue dialog")
def user_confirm_and_continue(authenticated_page: Page, docusign_page):
    """Check ERSD consent checkbox and click Continue button in the DocuSign Review and Continue dialog"""
    logger.info(">>> ENTERED STEP: user_confirm_and_continue")
    
    # Check the ERSD consent checkbox
    logger.info("Checking Electronic Record and Signature Disclosure consent...")
    docusign_page.check_ersd_consent_checkbox(timeout=10000)
    
    # Click the Continue button
    logger.info("Clicking Continue button...")
    docusign_page.click_ersd_continue_button(timeout=10000)
    
    logger.info("✓ User confirmed and clicked Continue button")


@when("User Finish the DocuSign process")
def user_finish_the_docusign_process(authenticated_page: Page, docusign_page):
    """Click the Finish button to complete the DocuSign signing process"""
    logger.info(">>> ENTERED STEP: user_finish_the_docusign_process")
    
    # Click the Finish button
    logger.info("Clicking Finish button to complete DocuSign process...")
    docusign_page.click_finish_button(timeout=10000)
    
    logger.info("✓ User finished the DocuSign process")

@then("User should be redirected to the DocuSign page")
def user_should_be_redirected_to_docusign_page(authenticated_page: Page, docusign_page):
    """Verify that the user is redirected to the DocuSign page"""
    logger.info(">>> ENTERED STEP: user_should_be_redirected_to_docusign_page")
    
    # Wait for DocuSign page to load
    logger.info("Waiting for DocuSign page to load...")
    docusign_page.verify_docusign_page_loaded(timeout=30000)
    
    # Compare current URL with DocuSign URL pattern
    current_url = authenticated_page.url
    docusign_url_pattern = DocuSignPage.DOCUSIGN_URL_PATTERN
    logger.info(f"Comparing current URL: {current_url} with pattern: {docusign_url_pattern}")
    
    assert docusign_url_pattern in current_url, \
        f"[FAIL] DocuSignPage: Page Redirect — Expected: URL contains '{docusign_url_pattern}', Actual: '{current_url}'. Details: Page must redirect to DocuSign signing interface. Locator: window.location.href."
    
    logger.info("✓ User successfully redirected to DocuSign page")


@then("Verify As_authorized_by stamp presence")
def verify_as_authorized_by_stamp_presence(authenticated_page: Page, docusign_page, test_context):
    """Verify 'As authorized by' stamping presence based on test data.
    
    Reads 'As_authorized_by_stamp_present' from test_data CSV ('Yes' or 'No')
    and verifies the presence or absence of the 'As authorized by' stamp on DocuSign page.
    """
    # Static stamping text - always checking for this exact text
    STAMPING_TEXT = "As authorized by"
    
    # Get test data
    test_data = test_context.get("test_data", {})
    as_authorized_by_value = test_data.get("As_authorized_by_stamp_present", "").strip()
    
    if not as_authorized_by_value:
        raise KeyError("Test data must include 'As_authorized_by_stamp_present' column for this step")
    
    # Determine expected presence based on test data
    should_be_present = as_authorized_by_value.lower() == "yes"
    expected_count = 1 if should_be_present else 0
    
    with allure.step(f"Verify '{STAMPING_TEXT}' stamp {'PRESENT' if should_be_present else 'NOT PRESENT'}"):
        logger.info(f">>> ENTERED STEP: verify_as_authorized_by_stamp_presence")
        logger.info(f"As_authorized_by_stamp_present from test data: '{as_authorized_by_value}'")
        logger.info(f"Expected state: '{STAMPING_TEXT}' should be {'PRESENT' if should_be_present else 'NOT PRESENT'}")
        
        # Get stamping element locator using page object method
        stamping_locator = docusign_page.get_stamping_element(STAMPING_TEXT)
        
        # Use SoftAssertions utility to verify element count (non-blocking)
        logger.info("Step 1: Verifying stamping presence using soft assertions...")
        soft_assert = SoftAssertions()
        soft_assert.assert_count(
            stamping_locator,
            expected_count=expected_count,
            message=f"[FAIL] DocuSignPage: Stamping Presence — Expected: '{STAMPING_TEXT}' count={expected_count}, Actual: count != {expected_count}. Details: '{STAMPING_TEXT}' stamp should be {'PRESENT' if should_be_present else 'NOT PRESENT'} (As_authorized_by_stamp_present='{as_authorized_by_value}'). Locator: document-stamping-area."
        )
        
        # Verify soft assertions
        logger.info("Step 2: Verifying soft assertions...")
        try:
            soft_assert.assert_all()
            logger.info(f"✓ Soft assertion PASSED: '{STAMPING_TEXT}' stamp verification")
        except Exception as soft_assert_error:
            logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
            allure.attach(
                str(soft_assert_error),
                name="As_authorized_by Stamp - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        result_text = "IS PRESENT" if should_be_present else "IS NOT PRESENT"
        logger.info(f"✓ Verified: '{STAMPING_TEXT}' stamp {result_text}")
        # Take screenshot for Allure reporting
        logger.info("Step 3: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name=f"As_authorized_by Stamp - {result_text}", attachment_type=allure.attachment_type.PNG)


@then("Verify docusign Review and continue dialog text")
def verify_docusign_review_and_continue_dialog_text(authenticated_page: Page, docusign_page, test_context):
    """Verify the Review and Continue dialog text matches expected value from test data.
    
    Reads 'Expected_docusign_ReviewAndContinue_Text' from test_data CSV
    and verifies it matches the text fetched from the dialog using soft assertions.
    
    Uses framework utilities:
    - docusign_page.fetch_docusign_review_and_continue_dialog_text(): Fetches dialog text
    - SoftAssertions: Non-blocking assertions that collect failures
    - Framework logging via setup_logger
    """
    logger.info(">>> ENTERED STEP: verify_docusign_review_and_continue_dialog_text")
    
    # Get expected text from test data
    test_data = test_context.get("test_data", {})
    expected_text = test_data.get("Expected_docusign_ReviewAndContinue_Text", "").strip()
    
    if not expected_text:
        raise KeyError("Test data must include 'Expected_docusign_ReviewAndContinue_Text' column for this step")
    
    with allure.step("Verify Review and Continue dialog text"):
        logger.info(f"Expected text from test data: '{expected_text}'")
        
        # STEP 1: Fetch the dialog text using page object method
        logger.info("Step 1: Fetching dialog text...")
        try:
            actual_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
            logger.info(f"Step 1: Dialog text fetched successfully: '{actual_text}'")
        except Exception as e:
            logger.error(f"✗ Failed to fetch dialog text: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Fetch Failed", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            raise
        
        # STEP 2: Use SoftAssertions to verify text matches expected value
        logger.info("Step 2: Verifying dialog text using soft assertions...")
        soft_assert = SoftAssertions()
        soft_assert.assert_equal(
            actual_text,
            expected_text,
            message=f"[FAIL] DocuSignPage: Review and Continue Dialog Text — Expected: '{expected_text}', Actual: '{actual_text}'. Details: Review and Continue dialog text must match expected value from test data. Locator: p[data-qa='email-message-content']."
        )
        
        # STEP 3: Verify soft assertions
        logger.info("Step 3: Verifying soft assertions...")
        try:
            soft_assert.assert_all()
            logger.info(f"✓ Soft assertion PASSED: Dialog text matches expected value")
        except Exception as soft_assert_error:
            logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
            allure.attach(
                str(soft_assert_error),
                name="Review and Continue Dialog - Text Verification Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        # STEP 4: Take screenshot for Allure reporting
        logger.info("Step 4: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Text Verified", attachment_type=allure.attachment_type.PNG)
        
        logger.info("✓ Review and Continue dialog text verification passed")


@when("User add Signature")
def user_add_signature(authenticated_page: Page, docusign_page):
    """Complete the DocuSign signature process: Finish -> Click Sign -> Finish
    
    Uses framework utilities:
    - docusign_page.click_finish_button(): Clicks top right Finish button
    - docusign_page.click_sign_button(): Clicks Sign button/div
    - Framework logging via get_allure_logger
    """
    logger.info(">>> ENTERED STEP: user_add_signature")
    logger.info("Starting signature addition process: Finish -> Sign -> Finish")
    
    # STEP 1: Click Finish button (first call)
    logger.info("Step 1: Clicking Finish button (initial)...")
    docusign_page.click_finish_button(timeout=10000)
    
    # STEP 2: Click on Sign button/div
    logger.info("Step 2: Clicking Sign button...")
    docusign_page.click_sign_button(timeout=10000)
    
    # Take screenshot for audit trail
    authenticated_page.wait_for_timeout(1000)
    screenshot = authenticated_page.screenshot()
    allure.attach(screenshot, name="Signature Process Completed", attachment_type=allure.attachment_type.PNG)
    
    logger.info("✓ User signature addition process completed successfully")


@then("Signature and today's date should be added on the document")
def verify_signature_and_date_added_on_document(authenticated_page: Page, docusign_page):
    """Verify that signature and today's date have been added on the document.
    
    Fetches signature tab attributes (aria-invalid and parent div class) using page object method.
    Verifies that the Date Signed value matches today's date in M/D/YYYY format (e.g., 3/11/2026).
    Uses SoftAssertions utility to verify all conditions are met.
    
    Uses framework utilities:
    - docusign_page.get_signature_tab_attributes(): Fetches aria-invalid and class attributes
    - docusign_page.get_date_signed_value(): Fetches Date Signed input value
    - SoftAssertions: Non-blocking assertions that collect failures
    - Framework logging via setup_logger
    """
    logger.info(">>> ENTERED STEP: verify_signature_and_date_added_on_document")
    logger.info("Verifying signature and today's date have been added on the document")
    
    with allure.step("Verify Signature and today's date added on document"):
        # STEP 1: Get signature tab attributes using page object method
        logger.info("Step 1: Retrieving signature tab attributes...")
        sig_attributes = docusign_page.get_signature_tab_attributes(timeout=10000)
        
        aria_invalid = sig_attributes.get('aria_invalid', '')
        parent_class = sig_attributes.get('parent_class', '')
        
        logger.info(f"Signature tab aria-invalid: '{aria_invalid}'")
        logger.info(f"Parent div class: '{parent_class}'")
        
        # STEP 1b: Get Date Signed value using page object method
        logger.info("Step 1b: Retrieving Date Signed value...")
        date_signed_value = docusign_page.get_date_signed_value(timeout=10000)
        logger.info(f"Date Signed value: '{date_signed_value}'")
        
        # STEP 1c: Get today's date in M/D/YYYY format for comparison
        logger.info("Step 1c: Formatting today's date for comparison...")
        today_date = datetime.now().strftime('%m/%d/%Y')
        # Remove leading zero from month if present (M/D/YYYY format, not MM/DD/YYYY)
        today_date_formatted = today_date.lstrip('0').replace('/0', '/').replace('0', '', 1)
        # More precise approach: split and rejoin without leading zeros
        month, day, year = today_date.split('/')
        today_date_formatted = f"{int(month)}/{int(day)}/{year}"
        
        logger.info(f"Today's date in M/D/YYYY format: '{today_date_formatted}'")
        
        # STEP 2: Use SoftAssertions to verify signature field is valid
        logger.info("Step 2: Verifying signature field validity using soft assertions...")
        soft_assert = SoftAssertions()
        
        # Assert aria-invalid is "false" (indicating the field is valid/filled)
        soft_assert.assert_equal(
            aria_invalid,
            "false",
            message=f"[FAIL] DocuSignPage: Signature Field Validity — Expected: aria-invalid='false', Actual: aria-invalid='{aria_invalid}'. Details: Signature field must be marked as valid after signature is added. Locator: [data-qa='signature-tab']."
        )
        
        # Assert parent div class contains 'signed' indicating the signature has been added
        soft_assert.assert_true(
            'signed' in parent_class.lower(),
            message=f"[FAIL] DocuSignPage: Signature Status Class — Expected: parent-class contains 'signed', Actual: parent-class='{parent_class}'. Details: Parent div class must indicate signed status after signature is added. Locator: [data-qa='signature-tab'].parent()."
        )
        
        # Assert date signed value is present and not empty
        soft_assert.assert_true(
            date_signed_value and len(date_signed_value.strip()) > 0,
            message=f"[FAIL] DocuSignPage: Date Signed Field Population — Expected: date_signed_value is not empty, Actual: date_signed_value='{date_signed_value}'. Details: Date Signed field must be populated with a valid date value. Locator: input[name='DateSigned']."
        )
        
        # Assert date signed value matches today's date in M/D/YYYY format
        soft_assert.assert_equal(
            date_signed_value,
            today_date_formatted,
            message=f"[FAIL] DocuSignPage: Signature Date Validation — Expected: date_signed='{today_date_formatted}' (today M/D/YYYY), Actual: date_signed='{date_signed_value}'. Details: Document signature must be dated with today's date. Locator: input[name='DateSigned']."
        )
        
        # STEP 3: Take screenshot for audit trail
        logger.info("Step 3: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot,
            name="Signature and Date Verification",
            attachment_type=allure.attachment_type.PNG
        )
        
        # STEP 4: Verify all soft assertions - raises SoftAssertionError if any failed
        try:
            soft_assert.assert_all()
            logger.info(f"✓ SOFT ASSERTION PASSED: Signature and date verified as added on document")
            logger.info(f"  - Signature field is valid (aria-invalid=false)")
            logger.info(f"  - Parent div class is set: '{parent_class}'")
            logger.info(f"  - Date Signed is set: '{date_signed_value}'")
            logger.info(f"  - Date Signed matches today's date: '{today_date_formatted}'")
        except Exception as e:
            logger.error(f"✗ Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name="Signature Verification - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"✓ Step completed successfully - Signature and date verification PASSED")

