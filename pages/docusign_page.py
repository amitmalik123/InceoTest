"""
DocuSign Page Object
Handles interactions with the DocuSign signing interface
"""
from __future__ import annotations
import re
from datetime import datetime
from typing import Callable, Optional

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.helpers import get_locator_attribute

logger = get_allure_logger(__name__)


class DocuSignPage(BasePage):
    """Page object for DocuSign signing page"""
    
    DOCUSIGN_URL_PATTERN = "https://apps-d.docusign.com/"
    
    # ========================================================================================
    # LOCATORS - All page element locators defined at class level for easy maintenance
    # ========================================================================================
    
    # ERSD Consent checkbox and related text
    ERSD_CONSENT_TEXT = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."
    
    # Button locators
    FINISH_BUTTON = '#action-bar-btn-finish'
    SEND_NOW_BUTTON_PATTERN = "Send Now"
    CONFIRM_CODE_BUTTON_PATTERN = "Confirm Code"
    RESEND_CODE_BUTTON_PATTERN = "Resend Code"
    SIGN_HERE_BUTTON_PATTERN = r"Required\s*-\s*Sign Here"
    SIGNATURE_APPLIED_BUTTON_PATTERN = r"Required\s*-\s*Signature Applied"
    
    # Dialog locators
    REVIEW_CONTINUE_DIALOG = '[aria-label="Review and continue"]'
    DIALOG_CONTENT_P_TAG = 'p[data-qa="email-message-content"]'
    
    # Sign button and signature elements
    SIGN_BUTTON = '//div[@data-type="SignHere"]/button'
    SIGNATURE_TAB_BUTTON = "//button[contains(@data-qa,'signature-tab-required')]"
    DATE_SIGNED_INPUT = "//div[@data-type='DateSigned']/descendant::input"
    
    # Session timeout banner
    SESSION_TIMEOUT_BANNER = "#ds_hldrBdy_lblHeaderText"
    
    # Stamping element (dynamic text-based locator)
    STAMPING_ELEMENT_TEXT_KEY = "As authorized by"  # Used with get_by_text()
    
    # OTP field (dynamic regex pattern)
    OTP_FIELD_NAME_PATTERN = "verification code"  # Used with get_by_role()

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

    def verify_docusign_page_loaded(self, timeout: int = 30000):
        """
        Wait for DocuSign page to load and take screenshot for evidence.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.verify_docusign_page_loaded()
        """
        logger.info("Waiting for DocuSign page to load...")
        
        # Wait for navigation to DocuSign
        self.page.wait_for_url(lambda url: self.DOCUSIGN_URL_PATTERN in url, timeout=timeout)
        
        logger.info("DocuSign page URL detected")
        
        # Wait for page to be fully loaded before taking screenshot (intelligent wait)
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        logger.info("DocuSign page fully loaded")
        
        # Take screenshot for evidence
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name="DocuSign Page Loaded",
            attachment_type=allure.attachment_type.PNG
        )

    def check_ersd_consent_checkbox(self, timeout: int = 10000):
        """
        Check the Electronic Record and Signature Disclosure consent checkbox.
        Locates and clicks on the consent text itself.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.check_ersd_consent_checkbox()
        """
        logger.info("Checking ERSD consent checkbox...")
        
        # Locate the label text and click on it to check the checkbox
        consent_text = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."
        label_locator = self.page.get_by_text(consent_text)
        
        # Wait for label to be visible
        label_locator.wait_for(state="visible", timeout=timeout)
        logger.debug("ERSD consent text is visible")
        
        # Click on the text to check the checkbox
        logger.info("Clicking on ERSD consent text")
        label_locator.click()
        logger.info("✓ ERSD consent checkbox checked")

    def click_ersd_continue_button(self, timeout: int = 10000):
        """
        Click the Continue button in the ERSD modal.
        Uses Playwright get_by_role to locate the button by its text.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_ersd_continue_button()
        """
        logger.info("Clicking ERSD Continue button...")
        
        # Locate the Continue button by role and name
        continue_button = self.page.get_by_role("button", name="Continue")
        
        # Wait for button to be visible and enabled
        continue_button.wait_for(state="visible", timeout=timeout)
        logger.debug("ERSD Continue button is visible")
        
        # Click the button
        logger.info("Clicking Continue button")
        continue_button.click()
        logger.info("✓ ERSD Continue button clicked")

    def click_finish_button(self, timeout: int = 10000):
        """
        Click the Finish button in the top right header to complete the DocuSign process.
        Targets the action-bar Finish button specifically (not the bottom or slide-up bar buttons).
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_finish_button()
        """
        logger.info("Clicking top right header Finish button...")
        
        # Locate the top right header Finish button by id attribute
        # This targets the action-bar-btn-finish specifically, not the bottom or slide-up-bar finish buttons
        finish_button = self.page.locator('#action-bar-btn-finish')
        
        # Wait for button to be visible and enabled
        finish_button.wait_for(state="visible", timeout=timeout)
        logger.debug("Header Finish button is visible")
        
        # Click the button
        logger.info("Clicking top right header Finish button")
        finish_button.click()
        logger.info("✓ DocuSign top right header Finish button clicked")

    def get_stamping_element(self, stamping_text: str):
        """
        Get locator for a stamping element by its text.
        Useful for verifying document stamps and signatures.
        
        Args:
            stamping_text: The text to search for (e.g., "As authorized by")
            
        Returns:
            Playwright Locator object for the stamping element
            
        Example:
            locator = docusign_page.get_stamping_element("As authorized by")
            assert locator.count() == 1
        """
        logger.info(f"Getting stamping element locator for: '{stamping_text}'")
        
        # Use Playwright's get_by_text to find the stamping element
        stamping_locator = self.page.get_by_text(stamping_text, exact=False)
        
        return stamping_locator

    def fetch_docusign_review_and_continue_dialog_text(self, timeout: int = 10000) -> str:
        """
        Fetch the text from the 'Review and continue' dialog.
        
        Locates the dialog by aria-label, then extracts text from p tag with data-qa attribute.
        Returns the text content for assertion/verification in calling code.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            The text content from the dialog's content element (stripped)
            
        Raises:
            AssertionError: If dialog or content element not found
            
        Example:
            dialog_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
            # Use assertions on the returned text in calling code
        """
        logger.info("Fetching DocuSign Review and Continue dialog text...")
        
        # Locate the dialog by aria-label
        dialog_locator = self.page.locator('[aria-label="Review and continue"]')
        
        # Verify dialog is present
        try:
            dialog_locator.wait_for(state="visible", timeout=timeout)
            logger.info("✓ Review and Continue dialog is present")
        except:
            logger.error("✗ Review and Continue dialog not found")
            raise AssertionError('[FAIL] DocuSignPage: Review and Continue Dialog Presence — Expected: dialog with aria-label="Review and continue" found, Actual: dialog not found. Details: Review and Continue dialog must be visible. Locator: [aria-label="Review and continue"].')
        
        # Get the text from the p tag with data-qa="email-message-content"
        content_locator = dialog_locator.locator('p[data-qa="email-message-content"]')
        
        # Wait for content to be visible
        try:
            content_locator.wait_for(state="visible", timeout=timeout)
            logger.debug("Content p tag is visible")
        except:
            logger.error("✗ Content p tag not found within the dialog")
            raise AssertionError('[FAIL] DocuSignPage: Dialog Content Element — Expected: p[data-qa="email-message-content"] found, Actual: element not found. Details: Content element must exist in the Review and Continue dialog. Locator: p[data-qa="email-message-content"].')
        
        # Get the actual text
        dialog_text = (content_locator.text_content() or "").strip()
        logger.info(f"✓ Dialog text fetched: '{dialog_text}'")
        
        return dialog_text

    def click_sign_button(self, timeout: int = 10000):
        """
        Click the Sign button (div with text 'Sign') on the DocuSign page.
        Locates a div element containing the text 'Sign' using CSS selector.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_sign_button()
        """
        logger.info("Clicking Sign button...")
        
        # Locate the Sign button/div by finding a div with text 'Sign'
        sign_button = self.page.locator('//div[@data-type="SignHere"]/button')
        
        # Wait for the button to be visible
        sign_button.wait_for(state="visible", timeout=timeout)
        logger.debug("Sign button is visible")
        
        # Click the button
        logger.info("Clicking Sign button")
        sign_button.click()
        logger.info("✓ Sign button clicked")

    def get_signature_tab_attributes(self, timeout: int = 10000) -> dict:
        """
        Get signature tab attributes to verify signature and date have been added.
        
        Fetches aria-invalid and class attributes from the signature tab button and parent div.
        Uses framework utilities (wait_for_element, get_locator_attribute) for robust operations.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            Dictionary with keys:
            - 'aria_invalid': aria-invalid attribute value (should be "false" if valid)
            - 'parent_class': class attribute value of parent div (indicates fill status)
            
        Raises:
            PlaywrightTimeoutError: If signature tab button not found
            ValueError: If required attributes not found
            
        Example:
            sig_attrs = docusign_page.get_signature_tab_attributes()
            assert sig_attrs.get('aria_invalid') == 'false'
        """
        logger.info("Retrieving signature tab attributes...")
        
        try:
            # STEP 1: Locate the signature tab button using XPath
            # XPath: //button[contains(@data-qa,'signature-tab-required')]
            logger.debug("Locating signature tab button...")
            sig_button_xpath = "//button[contains(@data-qa,'signature-tab-required')]"
            sig_button = self.page.locator(sig_button_xpath)
            
            # Wait for button to be present in DOM using BasePage utility
            logger.debug("Waiting for signature button to be attached...")
            self.wait_for_element(sig_button, state='attached', timeout=timeout)
            logger.debug("✓ Signature tab button found")
            
            # STEP 2: Get aria-invalid attribute from the button using utility function
            logger.debug("Fetching aria-invalid attribute using utility function...")
            aria_invalid = get_locator_attribute(
                locator=sig_button,
                attribute_name='aria-invalid',
                element_name='signature button',
                timeout=timeout
            )
            logger.info(f"Signature button aria-invalid: '{aria_invalid}'")
            
            # STEP 3: Get parent div and fetch its class attribute using utility function
            logger.debug("Locating parent div of signature button...")
            parent_div = sig_button.locator('xpath=..').first
            
            # Wait for parent div to be present
            self.wait_for_element(parent_div, state='attached', timeout=timeout)
            logger.debug("✓ Parent div found")
            
            # Get class attribute from parent div using utility function
            logger.debug("Fetching parent div class attribute using utility function...")
            parent_class = get_locator_attribute(
                locator=parent_div,
                attribute_name='class',
                element_name='parent div',
                timeout=timeout
            )
            logger.info(f"Parent div class: '{parent_class}'")
            
            # Return attributes as dictionary
            result = {
                'aria_invalid': aria_invalid,
                'parent_class': parent_class
            }
            
            logger.info(f"✓ Signature tab attributes retrieved: {result}")
            return result
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve signature tab attributes: {e}")
            raise

    def get_date_signed_value(self, timeout: int = 10000) -> Optional[str]:
        """
        Get the Date Signed value from the DocuSign document.
        
        Locates the input element inside a div with data-type='DateSigned' and fetches its value.
        Uses framework utilities (wait_for_element, get_locator_attribute) for robust operations.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            The value of the Date Signed input field (e.g., "3/11/2026") or None if not found
            
        Raises:
            PlaywrightTimeoutError: If the date signed input not found
            
        Example:
            date_signed = docusign_page.get_date_signed_value()
            assert date_signed and len(date_signed) > 0
        """
        logger.info("Retrieving Date Signed value...")
        
        try:
            # STEP 1: Locate the Date Signed div using XPath
            logger.debug("Locating Date Signed div...")
            date_signed_xpath = "//div[@data-type='DateSigned']/descendant::input"
            date_signed_input = self.page.locator(date_signed_xpath)
            
            # Wait for input to be present in DOM using BasePage utility
            logger.debug("Waiting for Date Signed input to be attached...")
            self.wait_for_element(date_signed_input, state='attached', timeout=timeout)
            logger.debug("✓ Date Signed input element found")
            
            # STEP 2: Get the value attribute from the input using utility function
            logger.debug("Fetching value attribute from Date Signed input using utility function...")
            date_value = get_locator_attribute(
                locator=date_signed_input,
                attribute_name='value',
                element_name='Date Signed input',
                timeout=timeout
            )
            logger.info(f"Date Signed value: '{date_value}'")
            
            logger.info(f"✓ Date Signed value retrieved: '{date_value}'")
            return date_value
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve Date Signed value: {e}")
            raise

    def complete_docusign_signing_with_otp(
        self,
        fetch_otp: Callable[[], Optional[str]],
        send_now_timeout: int = 10_000,
        otp_field_timeout: int = 10_000,
        consent_timeout: int = 20_000,
        continue_timeout: int = 10_000,
        finish_timeout: int = 10_000,
        session_timeout: int = 20_000,
        session_timeout_check: bool = False,
    ) -> Optional[str]:
        """Complete the full authorized signer DocuSign flow using an OTP callback.

        This method encapsulates the common sequence used for the authorized
        signer flow:

        1. Click the "Send Now" button to trigger the OTP email
        2. Invoke ``fetch_otp`` to retrieve the OTP (typically from Outlook)
        3. Enter the OTP in the verification textbox and click "Confirm Code"
          4. Run the standard ERSD + Continue + Finish sequence, unless the
              DocuSign session has already timed out after OTP entry.

        The ``fetch_otp`` callback is responsible for interacting with the
        email system (e.g. OutlookOtpPage) and must return a 6-digit OTP
        string. If it returns ``None`` or an empty string, this method raises
        ``RuntimeError``.
        """
        logger.info("Starting authorized signer DocuSign flow with OTP...")

        # Ensure the DocuSign page is fully loaded before interacting.
        self.page.wait_for_load_state("networkidle")

        # 1) Click the "Send Now" button to send the verification email.
        send_now_button = self.page.get_by_role("button", name="Send Now")
        send_now_button.wait_for(state="visible", timeout=send_now_timeout)
        send_now_button.click()
        logger.info("Clicked 'Send Now' button on DocuSign.")

        # 2) Fetch OTP using the provided callback (typically from Outlook).
        otp = fetch_otp()
        if not otp:
            logger.error(
                "No OTP fetched from email; cannot complete authorized signer verification."
            )
            raise RuntimeError(
                "No OTP fetched from authorized signer email; see OTP provider logs for details."
            )

        # 3) Enter OTP and confirm on the DocuSign verification page.
        otp_input = self.page.get_by_role(
            "textbox", name=re.compile("verification code", re.I)
        )
        otp_input.wait_for(state="visible", timeout=otp_field_timeout)
        otp_input.fill(otp)
        logger.info("Filled DocuSign verification code textbox with OTP.")

        confirm_button = self.page.get_by_role(
            "button", name=re.compile("Confirm Code", re.I)
        )
        confirm_button.wait_for(state="visible", timeout=otp_field_timeout)       
        confirm_button.click()
        logger.info("Clicked 'Confirm Code' button on DocuSign.")

        # If DocuSign reports that the code is incorrect, trigger the
        # resend flow and submit a fresh OTP from the same provider.
        self.handle_incorrect_otp_and_resend_code(
            fetch_otp=fetch_otp,
            otp_field_timeout=otp_field_timeout,
            resend_popup_timeout=otp_field_timeout,
        )

        # 3a) Check for a DocuSign session timeout banner after OTP entry
        # before proceeding to ERSD/Finish. When the session has timed
        # out, DocuSign shows a message like:
        #   <span id="ds_hldrBdy_lblHeaderText">Your session has timed out.</span>
        # In that case, return a sentinel string so callers can react
        # appropriately instead of attempting to continue the flow.
        if session_timeout_check:
            timeout_banner = self.page.locator("#ds_hldrBdy_lblHeaderText")
            try:
                timeout_banner.wait_for(state="visible", timeout=session_timeout)
                banner_text = timeout_banner.inner_text().strip().lower()
                if "session has timed out" in banner_text:
                    logger.error(
                        "DocuSign session has timed out after OTP entry; "
                        "skipping ERSD/Finish steps."
                    )
                    return "Session time out"
            except PlaywrightTimeoutError:
                # No visible timeout banner; proceed with the normal flow.
                pass

        # 4) Run the standard ERSD + Continue + Finish sequence.
        logger.info("Completing DocuSign ERSD consent and Finish sequence...")
        self.complete_ersd_and_finish(
            consent_timeout=consent_timeout,
            continue_timeout=continue_timeout,
            finish_timeout=finish_timeout,
        )
        logger.info("✓ Authorized signer DocuSign flow with OTP completed")
        return None
    
    def handle_incorrect_otp_and_resend_code(
        self,
        fetch_otp: Callable[[], Optional[str]],
        otp_field_timeout: int = 2_000,
        resend_popup_timeout: int = 10_000,
    ) -> None:
        """Handle an incorrect OTP by resending and submitting a new one.

        Workflow (based on the Playwright recorder steps):

        1. Detect the "Code is incorrect" message.
        2. Click the main "Resend Code" button.
        3. Verify the "Resend Code" popup header is visible.
        4. Click "Resend Code" again in the popup to trigger a new OTP.
        5. Fetch the latest OTP via ``fetch_otp`` and submit it.

        If the error message is not present, this method returns
        immediately without doing anything.
        """
        # 1) Look for the error message indicating the OTP was incorrect.
        error_paragraph = self.page.get_by_role("paragraph")
        try:
            error_paragraph.wait_for(state="visible", timeout=otp_field_timeout)
            error_text = error_paragraph.inner_text().strip().lower()
        except PlaywrightTimeoutError:
            logger.info(
                "No OTP error paragraph became visible after confirming code; "
                "assuming code was accepted."
            )
            return

        if "code is incorrect" not in error_text:
            logger.info(
                "OTP error paragraph visible but does not contain 'Code is incorrect'; "
                f"text was: '{error_text}'"
            )
            return

        logger.warning("DocuSign reported 'Code is incorrect'; starting resend-code flow.")

        # 2) Click the main "Resend Code" button on the page.
        resend_button = self.page.get_by_role(
            "button", name=re.compile("Resend Code", re.I)
        )
        resend_button.wait_for(state="visible", timeout=otp_field_timeout)
        resend_button.click()
        logger.info("Clicked primary 'Resend Code' button.")

        # 3) Verify the popup heading "Resend Code" is visible.
        popup_header_span = (
            self.page.get_by_role("heading", name=re.compile("Resend Code", re.I))
            .locator("span")
        )
        popup_header_span.wait_for(state="visible", timeout=resend_popup_timeout)
        logger.info("'Resend Code' confirmation popup header is visible.")

        # 4) Click "Resend Code" again in the popup to actually send a new code.
        resend_button_popup = self.page.get_by_role(
            "button", name=re.compile("Resend Code", re.I)
        )
        resend_button_popup.wait_for(state="visible", timeout=resend_popup_timeout)
        resend_button_popup.click()
        logger.info("Confirmed 'Resend Code' in the popup dialog.")

        # 5) Fetch the latest OTP and submit it.
        new_otp = fetch_otp()
        if not new_otp:
            logger.error(
                "No OTP fetched after requesting resend; cannot complete verification."
            )
            raise RuntimeError(
                "No OTP fetched after DocuSign resend; see OTP provider logs for details."
            )

        otp_input = self.page.get_by_role(
            "textbox", name=re.compile("verification code", re.I)
        )
        otp_input.wait_for(state="visible", timeout=otp_field_timeout)
        otp_input.fill(new_otp)
        logger.info("Filled DocuSign verification code textbox with resent OTP.")

        confirm_button = self.page.get_by_role(
            "button", name=re.compile("Confirm Code", re.I)
        )
        confirm_button.wait_for(state="visible", timeout=otp_field_timeout)
        confirm_button.click()
        logger.info("Clicked 'Confirm Code' button after resending OTP.")

    def complete_ersd_and_finish(
        self,
        consent_timeout: int = 20000,
        continue_timeout: int = 10000,
        finish_timeout: int = 10000,
    ) -> None:
        """Complete the standard ERSD + Continue + Finish flow.

        This is a convenience wrapper that performs the common sequence
        of actions required after the user enters the DocuSign OTP:

        1. Check the Electronic Record and Signature Disclosure consent
        2. Click the ERSD Continue button
        3. Complete any required inline recipient signature
        4. Click the top right header Finish button

        Timeouts are in milliseconds to align with Playwright's API.
        """
        logger.info("Starting DocuSign ERSD consent and Finish sequence...")
        try:
            self.check_ersd_consent_checkbox(timeout=consent_timeout)
            self.click_ersd_continue_button(timeout=continue_timeout)

            self.complete_recipient_signature_if_required(timeout=finish_timeout)

            self.click_finish_button(timeout=finish_timeout)
            logger.info("✓ Completed DocuSign ERSD consent and Finish sequence")
        except Exception as ex:
            logger.error(f"Error during DocuSign ERSD consent and Finish sequence: {ex}")
            # Re-raise so callers can decide how to handle failures
            raise

    def complete_recipient_signature_if_required(self, timeout: int = 10_000) -> None:
        """Wait for Finish and complete inline signing when required.

        Behaviour:

        1. Wait for the main Finish button (header action bar) to be
           visible, using the full ``timeout``.
        2. Using only a short timeout (up to 2 seconds), check for the
           optional inline "Required - Sign Here" button and click it
           when present.
        3. After clicking, wait (with the same short timeout) for the
           "Required - Signature Applied" indicator.

        If no required-sign button appears within the short timeout,
        the method simply logs and returns so flows without inline
        signatures do not incur the full ``timeout``. A missing Finish
        button will still raise an error via Playwright's timeout.
        """
        # 1) Ensure the header Finish button is present before we try
        # to reason about the document surface and optional inline
        # signing steps. If this times out, let the exception bubble up
        # so the overall flow fails visibly.
        finish_button = self.page.locator('#action-bar-btn-finish')
        finish_button.wait_for(state="visible", timeout=timeout)
        logger.debug("Header Finish button is visible after ERSD Continue")

        # 2) Use a short timeout window to detect the optional
        # "Required - Sign Here" step so scenarios without inline
        # signing do not pay the full timeout cost.
        short_sign_timeout = min(2000, timeout)

        try:
            # Look for the inline "Required - Sign Here" button.
            sign_here_button = self.page.get_by_role(
                "button", name=re.compile(r"Required\s*-\s*Sign Here", re.I)
            )

            try:
                sign_here_button.wait_for(state="visible", timeout=short_sign_timeout)
            except PlaywrightTimeoutError:
                logger.info(
                    "DocuSign: no 'Required - Sign Here' button visible within short timeout; "
                    "assuming no inline recipient signature is required."
                )
                return

            logger.info("DocuSign: 'Required - Sign Here' button visible; clicking to sign.")
            sign_here_button.click()

            # After clicking, wait for the signature-applied state to
            # confirm that the inline signing step has completed.
            signature_applied_button = self.page.get_by_role(
                "button", name=re.compile(r"Required\s*-\s*Signature Applied", re.I)
            )
            try:
                signature_applied_button.wait_for(state="visible", timeout=short_sign_timeout)
                logger.info("DocuSign: 'Required - Signature Applied' state confirmed.")
            except PlaywrightTimeoutError as ex:
                logger.warning(
                    "DocuSign: 'Required - Signature Applied' indicator did not appear within "
                    f"short timeout after signing; proceeding anyway: {ex}"
                )

        except Exception as ex:
            # Fully defensive: do not fail entire flow if this optional
            # inline signing logic encounters an unexpected condition.
            logger.warning(
                f"DocuSign: error while handling inline recipient signature; "
                f"continuing to Finish step: {ex}"
            )

    def close(self) -> None:
        """Close the underlying DocuSign Playwright page.

        This allows callers (like OutlookOtpPage) to call
        docusign_page.close() in a symmetric way to page.close().
        """
        try:
            self.page.close()
        except Exception as ex:
            logger.error(f"Error while closing DocuSign page: {ex}")

    def complete_signing_with_outlook_otp(
        self,
        max_wait_time_in_seconds: int = 60,
        session_timeout_check: bool = False,
    ) -> Optional[str]:
        """End-to-end DocuSign signing using an OTP fetched from Outlook.

        This is a convenience wrapper around ``complete_docusign_signing_with_otp``
        that wires up the standard OutlookPage-based OTP retrieval.
        The OutlookPage import is local to avoid circular imports.
        """

        def _fetch_otp() -> Optional[str]:
            # Local import to prevent circular dependency at module load time.
            from pages.outlook_page import OutlookPage

            otp_page = OutlookPage.from_config(self.page)
            submitting_time = datetime.now().time()
            return otp_page.get_otp_with_retry(
                submitting_time, max_wait_time_in_seconds=max_wait_time_in_seconds
            )

        return self.complete_docusign_signing_with_otp(
            fetch_otp=_fetch_otp,
            session_timeout_check=session_timeout_check,
        )  