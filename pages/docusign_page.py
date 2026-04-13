"""
DocuSign Page Object
Handles interactions with the DocuSign signing interface
"""
from __future__ import annotations
import os
import re
import time
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Optional

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import get_settings
from pages.base_page import BasePage
from locators import docusign_locators
from utils.allure_logger import get_allure_logger
from utils.helpers import get_locator_attribute

if TYPE_CHECKING:
    from pages.outlook_page import OutlookPage

logger = get_allure_logger(__name__)


class DocuSignPage(BasePage):
    """Page object for DocuSign signing page"""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self._initialize_locators()
        self._last_send_now_epoch = None
    
    def _initialize_locators(self) -> None:
        """Initialize all locator properties for Send Now and Resend Code buttons."""
        # Send Now button with multiple locator strategies
        self.send_now_button = self.page.locator('button[data-qa*="send-now"]')
        self.send_now_button_by_role = self.page.get_by_role("button", name=docusign_locators.SEND_NOW_BUTTON_PATTERN)
        self.send_now_button_text = self.page.get_by_text(docusign_locators.SEND_NOW_BUTTON_PATTERN)
        
        # Resend Code button with multiple locator strategies
        self.resend_code_button = self.page.locator('button[data-qa*="resend-code"]')
        self.resend_code_primary_button = self.page.get_by_role("button", name=docusign_locators.RESEND_CODE_BUTTON_PATTERN)
        
        # Fallback locator for Send Now button variants
        self.send_now_fallback_buttons = self.page.get_by_role("button").filter(has_text=re.compile("Send Now|send now", re.IGNORECASE))
    
    @staticmethod
    def get_email() -> str:
        """Get Outlook email from settings configuration.
        
        Returns:
            Encrypted email address from settings
        """
        settings = get_settings()
        return settings.outlook_email or ""
    
    @staticmethod
    def get_password() -> str:
        """Get Outlook password from settings configuration.
        
        Returns:
            Encrypted password from settings
        """
        settings = get_settings()
        return settings.outlook_password or ""
    
    def _init_locators(self, page: Page) -> None:
        """Reinitialize locators for a new page (for context switching).
        
        Args:
            page: Playwright Page instance to bind locators to
        """
        self.page = page
        self._initialize_locators()
    
    def submit_otp(self, otp_code: str, timeout: int = 10000) -> None:
        """Submit OTP code to the verification code field in DocuSign.
        
        Args:
            otp_code: The 6-digit OTP code to submit
            timeout: Maximum time to wait for field in milliseconds
            
        Raises:
            RuntimeError: If OTP code is incorrect or submission fails
        """
        logger.info(f"Submitting OTP code to DocuSign")
        
        try:
            # Locate the OTP input field by role and name pattern
            otp_field = self.page.get_by_role("textbox", name=re.compile(docusign_locators.OTP_FIELD_NAME_PATTERN, re.IGNORECASE))
            
            # Wait for field to be visible
            otp_field.wait_for(state="visible", timeout=timeout)
            logger.debug("OTP field is visible")
            
            # Fill the OTP code
            otp_field.fill(otp_code)
            logger.info(f"OTP code entered")
            
            # Wait a moment for the field to process
            self.page.wait_for_timeout(1000)
            
            # Click the Confirm Code button to submit
            confirm_button = self.page.get_by_role("button", name=docusign_locators.CONFIRM_CODE_BUTTON_PATTERN)
            confirm_button.wait_for(state="visible", timeout=timeout)
            logger.debug("Confirm Code button is visible")
            
            confirm_button.click()
            logger.info("Confirm Code button clicked")
            
            # Wait for submission to complete
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            logger.error(f"Failed to submit OTP: {str(e).splitlines()[0]}")
            raise RuntimeError(f"Code is incorrect or submission failed: {e}")

    def verify_docusign_page_loaded(self, timeout: int = 60000):
        """
        Wait for DocuSign page to load and take screenshot for evidence.
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 60000ms = 60 seconds)
            
        Example:
            docusign_page.verify_docusign_page_loaded()
        """
        logger.info("Waiting for DocuSign page to load...")
        logger.info(f"[OTP_DEBUG] Page load timeout: {timeout}ms ({timeout/1000}s)")
        
        # Check if we're already on DocuSign page to avoid unnecessary waits
        current_url = self.page.url
        if docusign_locators.DOCUSIGN_URL_PATTERN in current_url:
            logger.info(f"[OTP_DEBUG] Already on DocuSign page: {current_url}")
            
            # Still wait for networkidle to ensure page is fully loaded
            try:
                self.page.wait_for_load_state("networkidle", timeout=timeout)
                logger.info("DocuSign page is fully loaded (networkidle)")
            except Exception as e:
                logger.warning(f"[OTP_DEBUG] Page didn't reach complete networkidle state: {str(e)[:100]}")
                # Don't fail here - page might already be interactive enough
        else:
            logger.info(f"[OTP_DEBUG] Not yet on DocuSign page. Current URL: {current_url}")
            
            # Wait for navigation to DocuSign
            self.page.wait_for_url(lambda url: docusign_locators.DOCUSIGN_URL_PATTERN in url, timeout=timeout)
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
        label_locator = self.page.get_by_text(docusign_locators.ERSD_CONSENT_TEXT)
        
        # Wait for label to be visible
        label_locator.wait_for(state="visible", timeout=timeout)
        logger.debug("ERSD consent text is visible")
        
        # Click on the text to check the checkbox
        logger.info("Clicking on ERSD consent text")
        label_locator.click()
        logger.info("✓ ERSD consent checkbox checked")

    def click_ersd_continue_button(self, timeout: int = 30000):
        """
        Click the Continue button in the ERSD modal.
        Uses Playwright get_by_role to locate the button by its text.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_ersd_continue_button()
        """
        logger.info("Clicking ERSD Continue button...")
        
        # CRITICAL: Wait for page to be fully loaded and stable (especially for headless mode)
        logger.info("Waiting for page to be fully loaded and network idle...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page reached networkidle state")
        except Exception as e:
            logger.warning(f"Page didn't reach networkidle: {e}, continuing anyway")
        
        # Wait a bit for modal to initialize after network idle
        import time
        time.sleep(1)
        
        # Locate the Continue button by role and name
        continue_button = self.page.get_by_role("button", name="Continue")
        
        # Wait for button to be visible and enabled
        continue_button.wait_for(state="visible", timeout=timeout)
        logger.debug("ERSD Continue button is visible")
        
        # Click the button
        logger.info("Clicking Continue button")
        continue_button.click()
        logger.info("✓ ERSD Continue button clicked")

    def click_finish_button(self, timeout: int = 30000):
        """
        Click the Finish button in the top right header to complete the DocuSign process.
        
        Uses scoped search within action-button-wrapper div for reliability:
        1. Locate the action-button-wrapper container
        2. Within that div, find the Finish button by role
        3. Click with page stability checks and clickability verification
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_finish_button()
        """
        logger.info("Clicking Finish button...")
        
        # CRITICAL: Wait for page to be fully loaded and stable
        logger.info("Waiting for page to be fully loaded (networkidle)...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page reached networkidle state")
        except Exception as e:
            logger.warning(f"Page didn't reach networkidle: {e}, continuing anyway")
        
        # Wait for DocuSign interface to initialize
        # Extended delay for headless mode compatibility (may be slower)
        import time
        time.sleep(3)
        
        finish_button = None
        
        # Strategy 1: Scoped search - get button within action-button-wrapper div (MOST ROBUST)
        # try:
        #     logger.info("Strategy 1: Using scoped search within action-button-wrapper div...")
        #     action_btn_wrapper = self.page.locator(docusign_locators.ACTION_BUTTON_WRAPPER)
        #     action_btn_wrapper.wait_for(state="visible", timeout=5000)
            
        #     # Search for Finish button within the scoped div
        #     finish_button = action_btn_wrapper.get_by_role("button", name=docusign_locators.FINISH_BUTTON_TEXT)
        #     finish_button.wait_for(state="visible", timeout=5000)
        #     logger.debug("✓ Found using scoped get_by_role")
        # except Exception as e:
        #     logger.debug(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Full page search with data-qa selector (fallback)
        if finish_button is None:
            try:
                logger.info("Strategy 2: Using full page CSS selector")
                finish_button = self.page.locator(docusign_locators.FINISH_BUTTON)
                finish_button.wait_for(state="visible", timeout=5000)
                logger.debug("✓ Found using CSS selector")
            except Exception as e:
                logger.debug(f"Strategy 2 failed: {e}")
        
        # If all strategies failed, log debug info and fail
        if finish_button is None:
            logger.error("✗ Could not find Finish button")
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Finish Button Not Found", attachment_type=allure.attachment_type.PNG)
            except Exception as screenshot_error:
                logger.warning(f"Could not capture screenshot: {screenshot_error}")
            
            raise PlaywrightTimeoutError(
                f"[FAIL] DocuSignPage: Finish Button Not Found — "
                f"Scoped search within action-button-wrapper failed. Timeout: {timeout}ms."
            )
        
        # CRITICAL: Ensure button is clickable before attempting click
        # In headless mode, button may be visible but not yet interactive
        logger.info("Ensuring Finish button is clickable...")
        try:
            # Wait for button to be enabled (not disabled)
            # This is more strict than visibility - button must be interactive
            finish_button.wait_for(state="visible", timeout=5000)
            
            # Additional check: verify button is not disabled
            is_disabled = finish_button.is_disabled()
            if is_disabled:
                logger.warning("Finish button appears to be disabled, waiting for it to become enabled...")
                # Give it more time to become enabled
                time.sleep(2)
                is_disabled = finish_button.is_disabled()
                if is_disabled:
                    logger.error("Finish button is still disabled, cannot click")
                    raise PlaywrightTimeoutError("Finish button is disabled and cannot be clicked")
            
            # Scroll button into view to ensure it's in viewport
            finish_button.scroll_into_view_if_needed()
            logger.debug("Button scrolled into view")
            
        except Exception as e:
            logger.warning(f"Error verifying button clickability: {e}")
        
        # Click the button with retry for headless mode resilience
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Clicking Finish button (attempt {attempt + 1}/{max_retries})...")
                finish_button.click(timeout=5000)
                logger.info("✓ Finish button clicked successfully")
                break
            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Wait before retry - button might still be initializing
                    time.sleep(2)
                else:
                    # All retries exhausted
                    logger.error(f"✗ Failed to click Finish button after {max_retries} attempts")
                    raise PlaywrightTimeoutError(
                        f"[FAIL] DocuSignPage: Could not click Finish Button — "
                        f"Failed after {max_retries} retry attempts. Timeout: {timeout}ms."
                    )
        
        # CRITICAL: After finishing DocuSign, wait for page to return and stabilize
        # The Request dialog may be hidden initially and needs render time
        logger.info("Waiting for page to return from DocuSign and stabilize...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.debug("Page returned and reached networkidle")
        except Exception as e:
            logger.debug(f"Page didn't reach networkidle: {e}")
        
        # Give dialog time to render and become visible
        # Extended for headless mode
        time.sleep(3)
        logger.info("✓ Page stabilization complete, dialog should be rendering")

    def click_adopt_and_sign(self, timeout: int = 30000):
        """
        Click the 'Adopt and Sign' button in the Adopt Signature modal.
        Uses Playwright role-based locator for accessibility and resilience.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            PlaywrightTimeoutError: If the Adopt and Sign button is not found or not visible
            
        Example:
            docusign_page.click_adopt_and_sign()
        """
        logger.info("Clicking Adopt and Sign button...")
        
        # CRITICAL: Wait for page to be fully loaded and stable (especially for headless mode)
        logger.info("Waiting for page to be fully loaded and network idle...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page reached networkidle state")
        except Exception as e:
            logger.warning(f"Page didn't reach networkidle: {e}, continuing anyway")
        
        # Wait a bit for modal to initialize after network idle
        import time
        time.sleep(1)
        
        try:
            # First, wait for the Adopt Signature modal to be visible
            modal_locator = self.page.locator(docusign_locators.ADOPT_SIGNATURE_MODAL)
            modal_locator.wait_for(state="visible", timeout=timeout)
            logger.debug("Adopt Signature modal is visible")
            
            # Locate the Adopt and Sign button by role and name (most semantic approach)
            adopt_sign_button = self.page.get_by_role(
                "button", 
                name=docusign_locators.ADOPT_AND_SIGN_BUTTON_TEXT
            )
            
            # Wait for button to be visible and enabled
            adopt_sign_button.wait_for(state="visible", timeout=timeout)
            logger.debug("Adopt and Sign button is visible")
            
            # Click the button
            logger.info("Clicking Adopt and Sign button")
            adopt_sign_button.click()
            logger.info("✓ Adopt and Sign button clicked")
            
            # Wait for modal to close and signature to be adopted
            self.page.wait_for_timeout(1000)
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Failed to locate Adopt and Sign button within timeout: {str(e).splitlines()[0]}")
            raise
        except Exception as e:
            logger.error(f"Error clicking Adopt and Sign button: {str(e).splitlines()[0]}")
            raise

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
        dialog_locator = self.page.locator(docusign_locators.REVIEW_CONTINUE_DIALOG)
        
        # Verify dialog is present
        try:
            dialog_locator.wait_for(state="visible", timeout=timeout)
            logger.info("✓ Review and Continue dialog is present")
        except:
            logger.error("✗ Review and Continue dialog not found")
            raise AssertionError('[FAIL] DocuSignPage: Review and Continue Dialog Presence — Expected: dialog with aria-label="Review and continue" found, Actual: dialog not found. Details: Review and Continue dialog must be visible. Locator: [aria-label="Review and continue"].')
        
        # Get the text from the p tag with data-qa="email-message-content"
        content_locator = dialog_locator.locator(docusign_locators.DIALOG_CONTENT_P_TAG)
        
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

    def click_sign_button(self, timeout: int = 30000):
        """
        Click the Sign button (div with text 'Sign') on the DocuSign page.
        Locates a div element containing the text 'Sign' using CSS selector.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            docusign_page.click_sign_button()
        """
        logger.info("Clicking Sign button...")
        
        # CRITICAL: Wait for page to be fully loaded and stable (especially for headless mode)
        logger.info("Waiting for page to be fully loaded and network idle...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page reached networkidle state")
        except Exception as e:
            logger.warning(f"Page didn't reach networkidle: {e}, continuing anyway")
        
        # Wait a bit for interface to initialize after network idle
        import time
        time.sleep(1)
        
        # Locate the Sign button/div by finding a div with text 'Sign'
        sign_button = self.page.locator(docusign_locators.SIGN_BUTTON)
        
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
            sig_button = self.page.locator(docusign_locators.SIGNATURE_TAB_BUTTON)
            
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
            date_signed_input = self.page.locator(docusign_locators.DATE_SIGNED_INPUT)
            
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

    def close(self) -> None:
        """Close the underlying DocuSign Playwright page.

        This allows callers (like OutlookOtpPage) to call
        docusign_page.close() in a symmetric way to page.close().
        """
        try:
            self.page.close()
        except Exception as ex:
            logger.error(f"Error while closing DocuSign page: {ex}")

        """End-to-end DocuSign signing using an OTP fetched from Outlook.

        This is a convenience wrapper around ``complete_docusign_signing_with_otp``
        that wires up the standard OutlookPage-based OTP retrieval.
        The OutlookPage import is local to avoid circular imports.
        """


    def otp_verification(self, outlook_page: Optional[Page] = None) -> None:
        """Run Send Now + OTP submission flow using existing Outlook page.
        
        Args:
            outlook_page: Existing Outlook page (optional). If not provided, will look for
                         any existing Outlook page in the context. If none found, will create new.
        """
        logger.info("[common_otp] Start")
        outlook_page_to_close = False
        new_outlook_page_opened = None
        
        try:
            # Get the list of pages BEFORE clicking Send Now to detect if a new one opens
            pages_before = set(self.page.context.pages)
            
            # Click Send Now to trigger OTP email
            self.click_send_now()
            logger.info("Send Now clicked to trigger OTP email")
            
            # Check if a new page opened after clicking Send Now
            self.page.wait_for_timeout(2000)  # Wait briefly for new page to open
            pages_after = set(self.page.context.pages)
            new_pages = pages_after - pages_before
            
            if new_pages and outlook_page is not None:
                # A new page opened but we have an existing Outlook page
                # Close the new page and use the existing one
                new_outlook_page_opened = list(new_pages)[0]
                logger.info("New page opened after Send Now, but existing outlook_page provided; closing new page")
                try:
                    new_outlook_page_opened.close()
                except Exception as e:
                    logger.warning(f"Error closing new Outlook page: {e}")
                new_outlook_page_opened = None
            
            # Get Outlook page - use provided one or find existing one
            if outlook_page is None:
                # Try to find existing Outlook page in context
                outlook_pages = [p for p in self.page.context.pages 
                                if "outlook" in p.url.lower() or "mail" in p.url.lower()]
                if outlook_pages:
                    outlook_page = outlook_pages[0]
                    logger.info("Found existing Outlook page in context")
                else:
                    # Create new page only if none exists
                    outlook_page = self.page.context.new_page()
                    outlook_page_to_close = True
                    logger.info("Created new Outlook page")
            else:
                # Use the provided Outlook page - bring it to front
                logger.info("Using provided Outlook page; bringing to front")
                outlook_page.bring_to_front()
            
            # Get credentials from settings
            outlook_email = self.get_email()
            outlook_password = self.get_password()
            logger.info("Retrieved Outlook credentials from settings")
            
            # Lazy import to avoid circular import
            from pages.outlook_page import OutlookPage
            
            # Initialize Outlook page object
            outlook_otp = OutlookPage.from_config(outlook_page)
            logger.info("Initialized OutlookPage object with existing page")
            
            # Fetch and submit OTP
            otp_submitted = self.fetch_and_submit_otp(
                outlook_otp,
                email=outlook_email,
                password=outlook_password,
                timeout=180.0,
                refresh_interval=5.0,
                preferred_sender=getattr(self, "_preferred_otp_sender", None),
                max_attempts=2,
            )

            if not otp_submitted:
                raise RuntimeError("OTP retrieval failed during e-signature flow")

            logger.info("[common_otp] Completed")
        finally:
            # Only close the Outlook page if we created it
            if outlook_page_to_close and outlook_page:
                logger.info("[common_otp] Closing Outlook page that was created")
                try:
                    outlook_page.close()
                except Exception as e:
                    logger.warning(f"Error closing Outlook page: {e}")
            # Bring DocuSign page back to front
            try:
                self.page.bring_to_front()
            except Exception as e:
                logger.warning(f"Error bringing DocuSign page to front: {e}")

    def _fetch_and_submit_otp_from_outlook(self, outlook_page: Optional[Page] = None) -> None:
        """Fetch OTP from Outlook and submit it in DocuSign.
        
        Args:
            outlook_page: Existing Outlook page (optional). If not provided, will look for
                         any existing Outlook page in the context. If none found, will create new.
        """
        outlook_page_to_close = False
        
        try:
            logger.info("Starting OTP flow")
            
            # Get Outlook page - use provided one or find existing one
            if outlook_page is None:
                # Try to find existing Outlook page in context
                outlook_pages = [p for p in self.page.context.pages 
                                if "outlook" in p.url.lower() or "mail" in p.url.lower()]
                if outlook_pages:
                    outlook_page = outlook_pages[0]
                    logger.info("Found existing Outlook page in context")
                else:
                    # Create new page only if none exists
                    outlook_page = self.page.context.new_page()
                    outlook_page_to_close = True
                    logger.info("Created new Outlook page")
            
            # Get credentials from settings
            outlook_email = self.get_email()
            outlook_password = self.get_password()
            logger.info("Retrieved Outlook credentials from settings")

            # Lazy import to avoid circular import
            from pages.outlook_page import OutlookPage
            
            # Initialize Outlook page with credentials
            outlook_otp = OutlookPage.from_config(outlook_page)
            logger.info("Initialized OutlookPage object with existing page")

            otp_submitted = self.fetch_and_submit_otp(
                outlook_otp,
                email=outlook_email,
                password=outlook_password,
                timeout=180.0,
                refresh_interval=5.0,
                preferred_sender=getattr(self, "_preferred_otp_sender", None),
                max_attempts=2,
            )

            if not otp_submitted:
                logger.error("Failed to fetch OTP from Outlook")
                raise RuntimeError("OTP retrieval failed during e-signature flow")

            logger.info("OTP flow completed")

        except Exception as e:
            logger.warning(f"Outlook OTP flow failed: {str(e).splitlines()[0]}")
            raise  # Re-raise the exception to stop execution
        finally:
            # Only close the Outlook page if we created it
            if outlook_page_to_close and outlook_page:
                logger.info("Closing Outlook page that was created")
                try:
                    outlook_page.close()
                except Exception as e:
                    logger.warning(f"Error closing Outlook page: {e}")

    def fetch_and_submit_otp(
        self,
        outlook_otp: "OutlookPage",
        email: str = None,
        password: str = None,
        timeout: float = 120.0,
        refresh_interval: float = 5.0,
        preferred_sender: str = None,
        max_attempts: int = 2,
    ) -> bool:
        """Fetch and submit OTP with retry attempts using existing Outlook page.
        
        **Important**: This method expects the OutlookPage object to be initialized with
        an already-open Outlook page (either passed from test step or created if needed).
        
        Args:
            outlook_otp: OutlookPage instance initialized with existing page
            email: Email address (optional, uses settings if not provided)
            password: Password (optional, uses settings if not provided)
            timeout: Total timeout in seconds
            refresh_interval: Page refresh interval in seconds
            preferred_sender: Preferred email sender for OTP filtering
            max_attempts: Maximum retry attempts for OTP submission
            
        Returns:
            True if OTP submitted successfully, False otherwise
            
        Note:
            - Does NOT create new Outlook pages or close existing ones
            - Reuses Outlook tab opened by previous test steps
            - OutlookPage initialization happens in caller (otp_verification)
        """
        max_missing_otp_resends = 2
        max_incorrect_otp_resends = 3
        max_total_attempts = max(max_attempts, 1 + max_missing_otp_resends + max_incorrect_otp_resends)

        missing_otp_resends = 0
        incorrect_otp_resends = 0
        attempt = 0

        while attempt < max_total_attempts:
            attempt += 1
            otp_code = outlook_otp.get_otp_with_retry(
                email=email,
                password=password,
                timeout=timeout,
                refresh_interval=refresh_interval,
                sent_after_epoch=getattr(self, "_last_send_now_epoch", None),
                preferred_sender=preferred_sender,
                outlook_page=outlook_otp.page,  # Pass the existing Outlook page to avoid creating new one
            )

            if not otp_code:
                if missing_otp_resends < max_missing_otp_resends:
                    missing_otp_resends += 1
                    logger.warning(
                        f"OTP not fetched on attempt {attempt}; triggering resend "
                        f"({missing_otp_resends}/{max_missing_otp_resends})"
                    )
                    self._click_resend_code_button()
                    continue
                continue

            try:
                # Ensure submit happens on current DocuSign/review page
                self._init_locators(self.page)
                self.submit_otp(otp_code)
                logger.info("OTP submitted successfully")
                return True
            except RuntimeError as otp_error:
                message = str(otp_error)
                if "Code is incorrect" in message:
                    if incorrect_otp_resends < max_incorrect_otp_resends:
                        incorrect_otp_resends += 1
                        logger.warning(
                            f"Incorrect OTP on attempt {attempt}; triggering resend "
                            f"({incorrect_otp_resends}/{max_incorrect_otp_resends})"
                        )
                        self._click_resend_code_button()
                        continue
                    self.assert_true(False, "OTP verification failed after max incorrect-OTP retries")
                raise

        logger.error(
            f"OTP attempts exhausted without success | attempts={attempt}, "
            f"missing_otp_resends={missing_otp_resends}/{max_missing_otp_resends}, "
            f"incorrect_otp_resends={incorrect_otp_resends}/{max_incorrect_otp_resends}"
        )
        return False

    def _click_resend_code_button(self) -> None:
        """Click Resend Code when OTP is incorrect."""
        resend_button = self.resend_code_button
        resend_button.wait_for(state="visible", timeout=10000)
        resend_button.click(timeout=5000)
        self.page.wait_for_timeout(3000)

        resend_primary_button = self.resend_code_primary_button
        resend_primary_button.wait_for(state="visible", timeout=10000)
        resend_primary_button.click(timeout=5000)

        self._last_send_now_epoch = time.time()
        self.page.wait_for_timeout(3000)
        logger.info("Clicked Resend Code")

    def click_send_now(self) -> None:
        """Click the Send Now button to trigger OTP email in DocuSign"""
        try:
            for locator, label in (
                (self.send_now_button, "data-qa locator"),
                (self.send_now_button_by_role, "role locator"),
                (self.send_now_button_text, "text locator"),
            ):
                try:
                    locator.wait_for(state="visible", timeout=10000)
                    if not locator.is_enabled():
                        continue
                    locator.scroll_into_view_if_needed()
                    locator.click(timeout=5000)
                    self._last_send_now_epoch = time.time()
                    logger.info("Send Now Button Clicked")
                    self.wait_for_timeout(15000)
                    return
                except Exception:
                    continue

            # Final fallback: pick any visible+enabled Send Now-like button and click first match
            fallback_buttons = self.send_now_fallback_buttons
            fallback_count = fallback_buttons.count()
            for index in range(fallback_count):
                candidate = fallback_buttons.nth(index)
                try:
                    if candidate.is_visible(timeout=1000) and candidate.is_enabled(timeout=1000):
                        candidate.scroll_into_view_if_needed()
                        candidate.click(timeout=5000)
                        self._last_send_now_epoch = time.time()
                        logger.info("Send Now Button Clicked")
                        self.wait_for_timeout(15000)
                        return
                except Exception:
                    continue

            raise RuntimeError("Send Now button not found or not visible")
        except Exception as e:
            try:
                os.makedirs("reports/screenshots", exist_ok=True)
                screenshot_path = f"reports/screenshots/send_now_missing_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.error(f"Send Now button FAILED - screenshot saved: {screenshot_path}")
                logger.error(f"Current URL: {self.page.url}")
            except Exception as screenshot_error:
                logger.warning(f"Failed to capture Send Now screenshot: {screenshot_error}")
            logger.error(f"ERROR: {str(e).splitlines()[0]}")
            raise


