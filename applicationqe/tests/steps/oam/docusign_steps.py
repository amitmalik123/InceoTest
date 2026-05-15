"""
DocuSign-related step definitions for BDD tests
"""
import allure
from datetime import datetime
from playwright.sync_api import Page
from pytest_bdd import then, when, parsers

from locators import docusign_locators
from pages.oam.docusign_page import DocuSignPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.soft_assertions_enhanced import EnhancedSoftAssertions

logger = get_allure_logger(__name__)

@when("User confirm and Continue the docusign Review and continue dialog")
def user_confirm_and_continue(authenticated_page: Page, test_context):
    """Check ERSD consent checkbox and click Continue button in the DocuSign Review and Continue dialog
    
    Args:
        authenticated_page: Playwright Page object
        test_context: Test context containing the new_docusign_page object from previous step
    """
    logger.info(">>> ENTERED STEP: user_confirm_and_continue")
    
    # Retrieve the DocuSignPage object from test_context
    # If not found, fall back to using authenticated_page directly
    docusign_page = test_context.get("new_docusign_page")
    if docusign_page:
        logger.info("[DEBUG] Using new_docusign_page from test_context")
    else:
        logger.info("[DEBUG] new_docusign_page not in test_context, creating default DocuSignPage")
        from pages.docusign_page import DocuSignPage
        docusign_page = DocuSignPage(authenticated_page)
    
    # Check the ERSD consent checkbox
    logger.info("Checking Electronic Record and Signature Disclosure consent...")
    docusign_page.check_ersd_consent_checkbox(timeout=10000)
    
    # Click the Continue button
    logger.info("Clicking Continue button...")
    docusign_page.click_ersd_continue_button(timeout=30000)
    
    logger.info("[PASS] DocuSignPage: ERSD Consent Confirmed.")


@when("User Finish the DocuSign process")
def user_finish_the_docusign_process(authenticated_page: Page, test_context):
    """Fetch D-number and click the Finish button to complete the DocuSign signing process.
    
    This step:
    1. Fetches the D-number (document tracking number) from the page (REQUIRED - hard failure if not successful)
    2. Stores it in test_context['d_number'] for later verification
    3. Clicks the Finish button to complete DocuSign process
    
    Args:
        authenticated_page: Playwright Page object
        test_context: Test context containing the new_docusign_page object from previous step
        
    Uses framework utilities:
    - docusign_page.get_d_number(): Fetches D-number using WaitContext with 60s timeout for robust element detection
    - logger: Unified logging with Allure integration
    
    Raises:
        AssertionError: If D-number cannot be fetched (hard failure - step will not proceed to Finish button)
    """
    logger.info(">>> ENTERED STEP: user_finish_the_docusign_process")
    
    # Retrieve the DocuSignPage object from test_context
    # If not found, fall back to using authenticated_page directly
    docusign_page = test_context.get("new_docusign_page")
    if docusign_page:
        logger.info("[DEBUG] Using new_docusign_page from test_context")
    else:
        logger.info("[DEBUG] new_docusign_page not in test_context, creating default DocuSignPage")
        from pages.docusign_page import DocuSignPage
        docusign_page = DocuSignPage(authenticated_page)
    
    with allure.step("Fetch D-number and finish DocuSign process"):
        # Step 1: Fetch D-number before finishing (HARD REQUIREMENT - must succeed)
        # Idempotent check: Only fetch D-number once per scenario
        if "d_number" not in test_context:
            logger.info("Step 1: Fetching D-number from DocuSign page (REQUIRED - 60s timeout)...")
            try:
                d_number = docusign_page.get_d_number(timeout=60000)  # 60s timeout
                test_context['d_number'] = d_number
                logger.info(f"[PASS] DocuSignPage: D-Number Fetched and Stored: {d_number}")
            except Exception as e:
                logger.error(f"✗ FAILED to fetch D-number (HARD FAILURE): {e}")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="D-Number Fetch Failed", attachment_type=allure.attachment_type.PNG)
                raise AssertionError(f"[FAIL] DocuSignPage: D-Number Fetch Required — D-number could not be fetched before completing DocuSign process. Details: {e}") from e
        else:
            # D-number already fetched in this scenario, skip re-fetch
            d_number = test_context['d_number']
            logger.info(f"Step 1: [SKIP] D-number already fetched in scenario (idempotent protection): {d_number}")
        
        # Step 2: Click the Finish button (only proceeds if D-number was successfully fetched)
        logger.info("Step 2: Clicking Finish button to complete DocuSign process...")
        docusign_page.click_finish_button(timeout=30000)
        logger.info("[PASS] DocuSignPage: DocuSign Process Finished.")

@then("User should be redirected to the DocuSign page")
def user_should_be_redirected_to_docusign_page(authenticated_page: Page, docusign_page):
    """Verify that the user is redirected to the DocuSign page"""
    logger.info(">>> ENTERED STEP: user_should_be_redirected_to_docusign_page")
    
    # Check if already on DocuSign page before waiting (page may have already loaded)
    current_url = authenticated_page.url
    docusign_keyword = docusign_locators.DOCUSIGN_URL_KEYWORD
    
    if docusign_keyword in current_url:
        logger.info(f"[FAST PATH] Already on DocuSign page: {current_url}")
    else:
        # Wait for DocuSign page to load (120 second timeout)
        logger.info("Waiting for DocuSign page to load...")
        docusign_page.verify_docusign_page_loaded(timeout=120000)
        current_url = authenticated_page.url
    
    logger.info(f"Comparing current URL: {current_url} with keyword: '{docusign_keyword}'")
    
    assert docusign_keyword in current_url, \
        f"[FAIL] DocuSignPage: Page Redirect — Expected: URL contains '{docusign_keyword}', Actual: '{current_url}'. Details: Page must redirect to DocuSign signing interface. Locator: window.location.href."
    
    logger.info("[PASS] DocuSignPage: Page Redirection Verified.")


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
        logger.info("Step 1: Verifying As Authorized by stamping presence using soft assertions...")
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        soft_assert.assert_count(
            stamping_locator,
            expected_count=expected_count,
            message=f"[FAIL] DocuSignPage: As Authorized by Stamping Presence — Expected: '{STAMPING_TEXT}' count={expected_count}, Actual: count != {expected_count}. Details: '{STAMPING_TEXT}' stamp should be {'PRESENT' if should_be_present else 'NOT PRESENT'} (As_authorized_by_stamp_present='{as_authorized_by_value}'). Locator: document-stamping-area."
        )
        
        # Verify soft assertions
        logger.info("Step 2: Verifying soft assertions...")
        try:
            soft_assert.assert_all()
            logger.info(f"[PASS] DocuSignPage: Stamping Verification Completed.")
        except Exception as soft_assert_error:
            logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
            allure.attach(
                str(soft_assert_error),
                name="As_authorized_by Stamp - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        result_text = "IS PRESENT" if should_be_present else "IS NOT PRESENT"
        logger.info(f"[PASS] DocuSignPage: Stamping Presence Verified.")
        # Take screenshot for Allure reporting
        logger.info("Step 3: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name=f"As_authorized_by Stamp - {result_text}", attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('Verify docusign Review and continue dialog text "{expected_text}"'))
def verify_docusign_review_and_continue_dialog_text(authenticated_page: Page, docusign_page, test_context, expected_text: str):
    """Verify the Review and Continue dialog text matches expected value from feature file.
    
    Takes expected text as a parameter from the feature file step
    and verifies it matches the text fetched from the dialog using soft assertions.
    
    Intelligently selects which DocuSign page to use:
    - If test_context["new_docusign_page"] exists: Use the new page (from "Review Document" link)
    - Otherwise: Use the docusign_page fixture (original page)
    
    Args:
        authenticated_page: Playwright Page object for screenshots
        docusign_page: DocuSignPage fixture for DocuSign interactions (fallback if no new page)
        test_context: Test context containing optional new_docusign_page from previous step
        expected_text: Expected dialog text passed from feature file step
    
    Uses framework utilities:
    - docusign_page.fetch_docusign_review_and_continue_dialog_text(): Fetches dialog text
    - SoftAssertions: Non-blocking assertions that collect failures
    - Framework logging via setup_logger
    """
    logger.info(">>> ENTERED STEP: verify_docusign_review_and_continue_dialog_text")
    logger.info(f"Expected text from feature file: '{expected_text}'")
    
    if not expected_text:
        raise ValueError("Expected text parameter is required for this step")
    
    # Select which DocuSignPage object to use
    page_obj = test_context.get("new_docusign_page")
    if page_obj:
        logger.info("[DEBUG] Using new_docusign_page from test_context (from 'Review Document' link)")
    else:
        logger.info("[DEBUG] Using docusign_page fixture (original page, no 'Review Document' link used)")
        page_obj = docusign_page
    
    with allure.step("Verify Review and Continue dialog text"):
        logger.info(f"Expected text from test data: '{expected_text}'")
        
        # STEP 1: Verify DocuSign page is loaded
        logger.info("Step 1: Verifying DocuSign page is loaded...")
        try:
            page_obj.verify_docusign_page_loaded(timeout=120000)
            logger.info("Step 1: DocuSign page loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load DocuSign page: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="DocuSign Page Load Failed", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            raise
        
        # STEP 2: Verify ERSD modal is visible
        logger.info("Step 2: Verifying ERSD modal is visible...")
        try:
            page_obj._verify_ersd_modal_visible(timeout=120000)
            logger.info("Step 2: ERSD modal verified as visible")
        except Exception as e:
            logger.error(f"✗ ERSD modal not visible: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="ERSD Modal Visibility Failed", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            raise
        
        # STEP 3: Fetch the dialog text using page object method
        logger.info("Step 3: Fetching dialog text...")
        try:
            actual_text = page_obj.fetch_docusign_review_and_continue_dialog_text()
            logger.info(f"Step 3: Dialog text fetched successfully: '{actual_text}'")
        except Exception as e:
            logger.error(f"✗ Failed to fetch dialog text: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Fetch Failed", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            raise
        
        # STEP 4: Use SoftAssertions to verify text matches expected value
        logger.info("Step 4: Verifying dialog text using soft assertions...")
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        soft_assert.assert_equal(
            actual_text,
            expected_text,
            message=f"[FAIL] DocuSignPage: Review and Continue Dialog Text — Expected: '{expected_text}', Actual: '{actual_text}'. Details: Review and Continue dialog text must match expected value from test data. Locator: p[data-qa='email-message-content']."
        )
        
        # STEP 5: Verify soft assertions
        logger.info("Step 5: Verifying soft assertions...")
        try:
            soft_assert.assert_all()
            logger.info(f"[PASS] DocuSignPage: Dialog Text Verification Completed.")
        except Exception as soft_assert_error:
            logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
            allure.attach(
                str(soft_assert_error),
                name="Review and Continue Dialog - Text Verification Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        # STEP 6: Take screenshot for Allure reporting
        logger.info("Step 6: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Text Verified", attachment_type=allure.attachment_type.PNG)
        
        logger.info("✓ Review and Continue dialog text verification passed")


@when("User add Signature")
def user_add_signature(authenticated_page: Page, docusign_page):
    """Complete the DocuSign signature process: Finish -> Click Sign -> Finish
    
    Uses framework utilities:
    - docusign_page.click_finish_button(): Clicks Finish button
    - docusign_page.click_sign_button(): Clicks Sign button/div
    - Framework logging via get_allure_logger
    """
    logger.info(">>> ENTERED STEP: user_add_signature")
    logger.info("Starting signature addition process: Finish -> Sign -> Finish")
    
    # STEP 1: Click Finish button (first call)
    logger.info("Step 1: Clicking Finish button (initial)...")
    docusign_page.click_finish_button(timeout=30000)
    
    # STEP 2: Click on Sign button/div
    logger.info("Step 2: Clicking Sign button...")
    docusign_page.click_sign_button(timeout=30000)
    
    # Take screenshot for audit trail
    authenticated_page.wait_for_timeout(1000)
    screenshot = authenticated_page.screenshot()
    allure.attach(screenshot, name="Signature Process Completed", attachment_type=allure.attachment_type.PNG)
    
    logger.info("[PASS] DocuSignPage: Signature Addition Process Completed.")


@when("User click on Sign and add signature")
def user_click_on_sign_and_add_signature(authenticated_page: Page, docusign_page, test_context):
    """Click on the Sign button to add signature to the document.
    
    Supports both single page (authenticated_page) and multi-page scenarios (new_docusign_page).
    Calls the page object method to locate and click the Sign button/div in DocuSign.
    
    Uses framework utilities:
    - docusign_page.click_sign_button(): Clicks Sign button in document
    - Framework logging via get_allure_logger
    
    Example (in feature file):
        And User click on Sign and add signature
    """
    logger.info(">>> ENTERED STEP: user_click_on_sign_and_add_signature")
    
    # Retrieve the DocuSignPage object from test_context (may be new page from Review Document link)
    # If not found, fall back to using authenticated_page directly
    docusign_page = test_context.get("new_docusign_page")
    if docusign_page:
        logger.info("[DEBUG] Using new_docusign_page from test_context")
    else:
        logger.info("[DEBUG] new_docusign_page not in test_context, creating default DocuSignPage")
        from pages.docusign_page import DocuSignPage
        docusign_page = DocuSignPage(authenticated_page)
    
    with allure.step("User click on Sign button and add signature"):
        logger.info("Clicking Sign button to add signature...")
        docusign_page.click_sign_button(timeout=30000)
        
        # Click the Adopt and Sign button to confirm signature
        logger.info("Clicking Adopt and Sign button to confirm signature...")
        docusign_page.click_adopt_and_sign(timeout=30000)
        
        # Wait a moment for the signature to be registered
        authenticated_page.wait_for_timeout(1000)
        
        # Take screenshot for audit trail
        logger.info("Taking screenshot after signature added...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot,
            name="Signature Added",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("[PASS] DocuSignPage: Sign Button Clicked and Signature Added.")


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
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        
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
            logger.info(f"[PASS] DocuSignPage: Signature and Date Verification Completed.")
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
        
        logger.info(f"[PASS] DocuSignPage: Signature and Date Verification Passed.")


@when("User click on Review Document and submit the otp")
def user_click_review_document_and_submit_opt(authenticated_page: Page, docusign_page, test_context):
    """Click on Review Document link and submit OTP for document signing.
    
    This step performs the complete end-to-end OTP verification and DocuSign signing workflow:
    1. Click the Review Document link in the authorized signer email (opens DocuSign in new tab)
    2. Perform OTP verification from Outlook and submit to DocuSign
    3. Complete the document signing process
    
    The Outlook page is expected to already be open from the prior step
    'User login to the email and search the authorized signer email' which
    searches for and opens the authorized signer email.
    
    Args:
        authenticated_page: Playwright Page object for the main DocuSign page (not used in this flow)
        docusign_page: DocuSignPage fixture for DocuSign interactions
        test_context: Test context dictionary containing the stored outlook_email_page
        
    Workflow:
        1. Retrieve stored outlook_email_page from test_context (created in previous step)
        2. Click 'Review Document' link in email, opens DocuSign in new tab
        3. Retrieve OTP from Outlook and submit to DocuSign
        4. Complete OTP verification and signing process
    """
    logger.info(">>> ENTERED STEP: user_click_review_document_and_submit_opt")
    
    with allure.step("User perform advisor signature 'by mail' method"):
        try:
            # Retrieve the stored outlook email page from test_context
            # This was created and stored by the previous step:
            # "User login to the email and search the authorized signer email"
            outlook_email_page = test_context.get("outlook_email_page")
            if not outlook_email_page:
                raise ValueError(
                    "outlook_email_page not found in test_context. "
                    "Ensure the step 'User login to the email and search the authorized signer email' "
                    "runs before this step to create and store the email page."
                )
            
            # Verify the page is still open before proceeding
            if outlook_email_page.is_closed():
                raise RuntimeError(
                    "outlook_email_page has been closed. "
                    "The page must remain open between steps for this workflow."
                )
            
            logger.info("Retrieved stored outlook_email_page from test_context")
            
            # STEP 1: Click Review Document link in the email to open DocuSign in new tab
            logger.info("STEP 1: Clicking 'Review Document' link in authorized signer email...")
            
            # Bring the Outlook email page to the foreground
            outlook_email_page.bring_to_front()
            logger.info("Brought outlook email page to foreground")
            
            # Click the REVIEW DOCUMENT link which opens DocuSign in a new page context
            review_link = outlook_email_page.get_by_role("link", name="REVIEW DOCUMENT")
            review_link.wait_for(timeout=15000)
            
            # Get the new page that opens when we click the link
            with outlook_email_page.context.expect_page() as new_page_info:
                review_link.click()
                new_docusign_page = new_page_info.value
            
            logger.info("[PASS] DocuSign page opened from email 'Review Document' link")
            
            # STEP 2: Create DocuSignPage wrapper around the new page for OTP workflow
            logger.info("STEP 2: Initializing DocuSignPage object for new DocuSign tab...")
            new_docusign_page_obj = DocuSignPage(new_docusign_page)
            logger.info("[PASS] DocuSignPage object initialized")
            
            # Store the new DocuSignPage object in test_context so subsequent steps can use it
            # This is critical because verification steps need to reference the SAME page object
            test_context["new_docusign_page"] = new_docusign_page_obj
            logger.info("[DEBUG] Stored new_docusign_page in test_context for subsequent verification steps")
            
            # STEP 3: Perform OTP verification and signing workflow
            # This retrieves OTP from Outlook and submits it to DocuSign
            logger.info("STEP 3: Initiating OTP verification and signing workflow...")
            new_docusign_page_obj.otp_verification(outlook_page=outlook_email_page)
            logger.info("[PASS] OTP verification and signing workflow completed")
            
            logger.info("[PASS] DocuSignPage: Advisor Signature 'By Mail' Method Completed Successfully.")
            
        except Exception as e:
            logger.error(f"[FAIL] Advisor signature 'by mail' workflow failed: {str(e).splitlines()[0]}")
            allure.attach(
                str(e),
                name="Advisor Signature 'By Mail' - Error Details",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@when("User click on send now and fetch OTP from mail")
def user_click_on_send_now_and_fetch_otp_from_mail(authenticated_page: Page, docusign_page, test_context):
    """Click Send Now button and fetch OTP code from email for client signing verification.
    
    This step handles the OTP verification workflow where the client needs to verify
    their identity via OTP fetched from email, then submit it to DocuSign for continuing
    the signing process using Playwright browser automation.
    
    Workflow:
    1. Click Send Now button to trigger OTP email send
    2. Create new Outlook browser tab and login
    3. Navigate to OTP folder to search for OTP email
    4. Wait for and extract 6-digit OTP code from email body
    5. Return to DocuSign and submit OTP
    
    Args:
        authenticated_page: Playwright Page object (current DocuSign page)
        docusign_page: DocuSignPage fixture for DocuSign interactions
        test_context: Test context dictionary
        
    Uses framework utilities:
    - OutlookPage: Playwright-based Outlook browser automation (from_config, login_outlook, get_otp_with_retry)
    - docusign_page methods: click_send_now(), submit_otp()
    - time module: For timing OTP retrieval
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots and error details for reporting
    
    Example feature file usage:
        When User click on send now and fetch OTP from mail
    """
    import time
    from pages.outlook_page import OutlookPage
    
    logger.info(">>> ENTERED STEP: user_click_on_send_now_and_fetch_otp_from_mail")
    
    with allure.step("User click on send now and fetch OTP from mail"):
        outlook_page = None
        try:
            # Get the DocuSignPage object
            page_obj = test_context.get("new_docusign_page")
            if page_obj:
                logger.info("[DEBUG] Using new_docusign_page from test_context")
            else:
                logger.info("[DEBUG] Using docusign_page fixture")
                page_obj = docusign_page
            
            logger.info(">>> STEP 1: Click Send Now to trigger OTP email...")
            page_obj.click_send_now()
            logger.info("✓ Send Now clicked - OTP email triggered")
            
            # Record the time when OTP was sent (for filtering in Outlook)
            otp_sent_time = time.time()
            
            logger.info(">>> STEP 2: Create new Outlook browser tab and login...")
            # Initialize OutlookPage object for OTP retrieval
            outlook_obj = OutlookPage.from_config(authenticated_page)
            
            # Login to Outlook and get the Outlook page
            outlook_page = outlook_obj.login_outlook(context_message="OTP verification for client signing")
            logger.info("✓ Successfully logged into Outlook")
            
            logger.info(">>> STEP 3: Search for OTP email and extract code...")
            # Get OTP from inbox using the existing Outlook page
            # This method waits for the OTP email and extracts the code
            otp_code = outlook_obj.get_otp_with_retry(
                email=None,  # Will use config from from_config
                password=None,  # Will use config from from_config
                timeout=120,  # 2 minutes timeout
                refresh_interval=5,  # Check every 5 seconds
                sent_after_epoch=otp_sent_time,
                outlook_page=outlook_page  # Use the already-logged-in page
            )
            
            if not otp_code:
                raise RuntimeError("Failed to retrieve OTP from Outlook")
            
            logger.info(f"✓ OTP code retrieved: {otp_code}")
            
            logger.info(">>> STEP 4: Close Outlook and return to DocuSign...")
            # Close Outlook page
            if outlook_page:
                try:
                    outlook_page.close()
                except Exception as e:
                    logger.warning(f"Error closing Outlook page: {e}")
                outlook_page = None
            
            # Bring DocuSign page to front
            page_obj.page.bring_to_front()
            logger.info("✓ Returned to DocuSign page")
            
            logger.info(">>> STEP 5: Submit OTP to DocuSign...")
            page_obj.submit_otp(otp_code=otp_code, timeout=30000)
            logger.info("✓ OTP submitted to DocuSign")
            
            logger.info("[PASS] OTP verification workflow completed successfully")
            
            # Capture screenshot for Allure reporting (with headless mode compatibility)
            time.sleep(1.0)  # [HEADLESS_COMPAT] Pre-wait for fonts to render
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Send_Now_OTP_Fetch_Completed",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as screenshot_err:
                logger.warning(f"[HEADLESS_COMPAT] Screenshot failed on first attempt: {str(screenshot_err)[:100]}")
                time.sleep(2.0)  # [HEADLESS_COMPAT] Extra wait for retry
                try:
                    screenshot = authenticated_page.screenshot()
                    allure.attach(
                        screenshot,
                        name="Send_Now_OTP_Fetch_Completed",
                        attachment_type=allure.attachment_type.PNG
                    )
                except:
                    logger.warning("[HEADLESS_COMPAT] Screenshot unavailable in headless mode, continuing without screenshot")
            
            logger.info("[PASS] Send Now and Fetch OTP Completed Successfully.")
            
        except Exception as e:
            logger.error(f"[FAIL] Send Now and Fetch OTP workflow failed: {str(e).splitlines()[0]}")
            # Capture error screenshot with headless mode compatibility
            time.sleep(1.0)  # [HEADLESS_COMPAT] Pre-wait for fonts to render
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Send_Now_Fetch_OTP_Failed",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as screenshot_err:
                logger.warning(f"[HEADLESS_COMPAT] Error screenshot failed: {str(screenshot_err)[:100]}")
                time.sleep(2.0)  # [HEADLESS_COMPAT] Extra wait for retry
                try:
                    screenshot = authenticated_page.screenshot()
                    allure.attach(
                        screenshot,
                        name="Send_Now_Fetch_OTP_Failed",
                        attachment_type=allure.attachment_type.PNG
                    )
                except:
                    logger.warning("[HEADLESS_COMPAT] Error screenshot unavailable in headless mode")
            allure.attach(
                str(e),
                name="Send_Now_Fetch_OTP_Error_Details",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"Send Now and Fetch OTP workflow failed: {e}") from e
        finally:
            # Ensure Outlook page is closed
            if outlook_page:
                try:
                    outlook_page.close()
                except:
                    pass


@when("User Finish later the DocuSign process")
def user_finish_later_docusign_process(authenticated_page: Page, docusign_page, test_context):
    """Finish later the DocuSign process and fetch D-number.
    
    This step defers the completion of the signing process by:
    1. Fetching the D-number (document tracking number) from the page (REQUIRED - hard failure if not successful)
    2. Storing it in test_context['d_number'] for later verification
    3. Clicking the 'Other Actions' dropdown button
    4. Selecting 'Finish Later' option from the menu
    
    Uses dynamic waiting (60 seconds) to account for page load delays when the menu appears.
    
    Args:
        authenticated_page: Playwright Page object for screenshots
        docusign_page: DocuSignPage fixture for DocuSign interactions
        test_context: Test context dictionary
        
    Uses framework utilities:
    - docusign_page.get_d_number(): Fetches D-number using WaitContext with 60s timeout for robust element detection
    - docusign_page.click_other_actions_button(): Clicks the 'Other Actions' dropdown menu
    - docusign_page.click_finish_later_option(): Clicks the 'Finish Later' option with dynamic wait
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots for reporting
    
    Example (in feature file):
        When User Finish later the DocuSign process
    """
    logger.info(">>> ENTERED STEP: user_finish_later_docusign_process")
    
    with allure.step("User Finish later the DocuSign process and fetch D-number"):
        try:
            # Retrieve the DocuSignPage object from test_context (may be new page from multistep flows)
            # If not found, fall back to using docusign_page fixture
            page_obj = test_context.get("new_docusign_page")
            if page_obj:
                logger.info("[DEBUG] Using new_docusign_page from test_context")
            else:
                logger.info("[DEBUG] Using docusign_page fixture")
                page_obj = docusign_page
            
            # Step 1: Fetch D-number before finishing (HARD REQUIREMENT - must succeed)
            # Idempotent check: Only fetch D-number once per scenario
            if "d_number" not in test_context:
                logger.info("STEP 1: Fetching D-number from DocuSign page (REQUIRED - 60s timeout)...")
                try:
                    d_number = page_obj.get_d_number(timeout=60000)  # 60s timeout
                    test_context['d_number'] = d_number
                    logger.info(f"[PASS] DocuSignPage: D-Number Fetched and Stored: {d_number}")
                except Exception as e:
                    logger.error(f"✗ FAILED to fetch D-number (HARD FAILURE): {e}")
                    screenshot = authenticated_page.screenshot()
                    allure.attach(screenshot, name="D-Number Fetch Failed", attachment_type=allure.attachment_type.PNG)
                    raise AssertionError(f"[FAIL] DocuSignPage: D-Number Fetch Required — D-number could not be fetched before completing Finish Later process. Details: {e}") from e
            else:
                # D-number already fetched in this scenario, skip re-fetch
                d_number = test_context['d_number']
                logger.info(f"STEP 1: [SKIP] D-number already fetched in scenario (idempotent protection): {d_number}")
            
            # Step 2: Click the 'Other Actions' button to open the menu
            logger.info("STEP 2: Clicking 'Other Actions' button...")
            page_obj.click_other_actions_button(timeout=60000)
            logger.info("✓ 'Other Actions' button clicked successfully")
            
            # Step 3: Click the 'Finish Later' option with dynamic waiting (60 seconds)
            logger.info("STEP 3: Clicking 'Finish Later' option (dynamic wait: 60s)...")
            page_obj.click_finish_later_option(timeout=60000)
            logger.info("✓ 'Finish Later' option clicked successfully")
            
            # Take screenshot for audit trail
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Finish_Later_Completed",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] DocuSignPage: Deferred completion (Finish Later) process completed successfully")
            
        except Exception as e:
            logger.error(f"[FAIL] Failed to complete Finish Later process: {e}")
            
            # Attach screenshot for debugging
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Finish_Later_Failed_Screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as screenshot_error:
                logger.warning(f"Could not capture screenshot: {screenshot_error}")
            
            # Raise assertion error for test failure
            raise AssertionError(f"Failed to complete Finish Later process: {e}") from e

