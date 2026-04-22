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
from utils.wait_utils import wait_for_condition, WaitTimeoutError

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

    def get_d_number(self, timeout: int = 60000) -> str:
        """
        Fetch the D-number (document tracking number) from the DocuSign page.
        
        Locates the span element that contains the D-number (e.g., D003525811, D003518970)
        using the XPath pattern: //span[starts-with(text(),"D00")]
        
        When multiple D-number spans exist on the page, fetches the FIRST VISIBLE one.
        
        Args:
            timeout: Maximum time to wait for the element in milliseconds (default: 60000ms = 60 seconds)
            
        Returns:
            The D-number text (e.g., "D003525811")
            
        Raises:
            AssertionError: If D-number span not found or text is empty (hard failure)
            
        Uses framework utilities:
        - logger: Unified logging with Allure integration
        - Playwright's wait_for(state="visible") for element visibility
        
        Example:
            d_number = docusign_page.get_d_number()  # Waits up to 60s for first visible D-number
            print(f"Document tracking number: {d_number}")
        """
        logger.info(f"Fetching D-number from DocuSign page (timeout: {timeout}ms = {timeout/1000}s)...")
        logger.info(f"  Locator: {docusign_locators.D_NUMBER_SPAN}")
        
        try:
            # Locate the D-number span using XPath and get the FIRST one
            # Use .first to handle cases where multiple D-number spans exist on page
            d_number_locator = self.page.locator(docusign_locators.D_NUMBER_SPAN).first
            
            # Step 1: Wait for first element to be visible using Playwright's built-in wait
            # This properly handles when multiple matching elements exist (gets first visible)
            logger.info(f"  Step 1: Waiting for first D-number span to be visible (up to {timeout/1000}s)...")
            timeout_sec = timeout / 1000.0
            try:
                d_number_locator.wait_for(state="visible", timeout=timeout)
                logger.info("  ✓ First D-number span is visible")
            except Exception as wait_error:
                logger.error(f"✗ D-number span did not appear within {timeout_sec}s")
                raise AssertionError(f"D-number span (locator: {docusign_locators.D_NUMBER_SPAN}) did not appear within {timeout_sec}s: {wait_error}")
            
            # Step 2: Extract the D-number text
            logger.info("  Step 2: Extracting D-number text from first visible span...")
            d_number_text = d_number_locator.text_content()
            
            if not d_number_text or not d_number_text.strip():
                raise AssertionError(f"D-number span found but text is empty. Locator: {docusign_locators.D_NUMBER_SPAN}")
            
            d_number = d_number_text.strip()
            logger.info(f"  ✓ D-number extracted: {d_number}")
            
            return d_number
            
        except Exception as e:
            logger.error(f"✗ Failed to get D-number: {e}")
            raise AssertionError(f"Failed to fetch D-number from DocuSign page: {e}") from e

    def verify_docusign_page_loaded(self, timeout: int = 120000):
        """
        Wait for DocuSign page to load and take screenshot for evidence.
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 120000ms = 120 seconds)
            
        Example:
            docusign_page.verify_docusign_page_loaded()
        """
        logger.info("Waiting for DocuSign page to load...")
        logger.info(f"[OTP_DEBUG] Page load timeout: {timeout}ms ({timeout/1000}s)")
        
        # Check if we're already on DocuSign page to avoid unnecessary waits
        current_url = self.page.url
        if any(p in current_url for p in docusign_locators.DOCUSIGN_URL_PATTERNS):
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
            self.page.wait_for_url(lambda url: any(p in url for p in docusign_locators.DOCUSIGN_URL_PATTERNS), timeout=timeout)
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

    def _verify_ersd_modal_visible(self, timeout: int = 10000) -> bool:
        """
        Verify that the ERSD (Electronic Record and Signature Disclosure) modal dialog is visible and ready.
        
        Uses multi-strategy approach:
        1. Primary: Check data-qa selector (most stable)
        2. Fallback: Check ARIA label (alternative implementation)
        3. Verify content is accessible (message text visible)
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            True if modal is visible and ready, False otherwise
            
        Raises:
            PlaywrightTimeoutError: If modal doesn't appear within timeout
        """
        logger.info("Verifying ERSD modal dialog is visible...")
        
        modal_locator = None
        
        # Strategy 1: Primary - Use data-qa selector (most reliable)
        try:
            logger.debug("Strategy 1: Checking data-qa='ersd-modal' selector...")
            dialog_primary = self.page.locator(docusign_locators.ERSD_MODAL_PRIMARY)
            dialog_primary.wait_for(state="visible", timeout=3000)
            modal_locator = dialog_primary
            logger.info("✓ ERSD modal found using primary data-qa selector")
        except PlaywrightTimeoutError:
            logger.debug("Primary selector timeout, trying fallback...")
        except Exception as e:
            logger.debug(f"Primary selector failed: {e}")
        
        # Strategy 2: Fallback - Use ARIA label
        if modal_locator is None:
            try:
                logger.debug("Strategy 2: Checking ARIA label selector...")
                dialog_fallback = self.page.locator(docusign_locators.ERSD_MODAL_ARIA)
                dialog_fallback.wait_for(state="visible", timeout=3000)
                modal_locator = dialog_fallback
                logger.info("✓ ERSD modal found using ARIA label selector (fallback)")
            except PlaywrightTimeoutError:
                logger.debug("Fallback selector timeout")
            except Exception as e:
                logger.debug(f"Fallback selector failed: {e}")
        
        # If modal not found, raise error
        if modal_locator is None:
            error_msg = (
                f"[FAIL] ERSD Modal Not Visible — Expected to find modal with "
                f"data-qa='ersd-modal' or aria-label='Review and continue', "
                f"but neither selector found within {timeout}ms. "
                "Possible causes: 1) Modal not yet rendered, 2) Page not fully loaded, "
                "3) Selector mismatch due to UI changes. Details: Modal must be in DOM and visible."
            )
            logger.error(error_msg)
            
            # Capture screenshot for debugging
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="ERSD Modal Not Found", attachment_type=allure.attachment_type.PNG)
            except Exception as screenshot_error:
                logger.warning(f"Could not capture screenshot: {screenshot_error}")
            
            raise PlaywrightTimeoutError(error_msg)
        
        # Verify modal content is accessible
        logger.debug("Verifying modal content is accessible...")
        try:
            content = modal_locator.locator(docusign_locators.DIALOG_CONTENT_P_TAG)
            content.wait_for(state="visible", timeout=2000)
            logger.debug("✓ Modal content (message text) is visible")
        except Exception as e:
            logger.warning(f"Could not verify modal content visibility: {e}")
        
        logger.info("[PASS] ERSD Modal Dialog is visible and ready")
        return True

    def check_ersd_consent_checkbox(self, timeout: int = 120000):
        """
        Check the ERSD consent checkbox with dynamic waiting and verification.
        
        Uses `wait_for_condition()` to dynamically poll for checkbox visibility over 120 seconds.
        
        Process:
        1. Dynamically wait for ERSD modal dialog to be visible (up to 120s)
        2. Locate checkbox using multi-strategy approach (data-qa, text fallback)
        3. Click checkbox to enable consent
        4. VERIFY checkbox is actually checked (state verification)
        5. Handle retry if state not confirmed
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 120000ms = 120 seconds)
            
        Raises:
            AssertionError: If dialog or checkbox not found after dynamic waiting
            
        Example:
            docusign_page.check_ersd_consent_checkbox()  # Dynamic wait up to 2 mins
        """
        logger.info(f">>> STEP: Checking ERSD consent checkbox (dynamic wait: {timeout}ms)")
        
        timeout_seconds = timeout / 1000  # Convert to seconds
        attempt_count = 0
        
        # STEP 1: Dynamically wait for dialog to be visible
        def dialog_visible() -> bool:
            """Poll for dialog visibility using multi-strategy."""
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count % 10 == 0:
                logger.info(f"⏳ Waiting for checkbox dialog... ({attempt_count * 2}s elapsed)")
            
            try:
                # Strategy 1: data-qa selector
                if self.page.locator(docusign_locators.ERSD_MODAL_PRIMARY).is_visible(timeout=500):
                    logger.debug(f"✓ Dialog found via data-qa (attempt {attempt_count})")
                    return True
            except:
                pass
            
            try:
                # Strategy 2: ARIA label
                if self.page.locator(docusign_locators.ERSD_MODAL_ARIA).is_visible(timeout=500):
                    logger.debug(f"✓ Dialog found via ARIA label (attempt {attempt_count})")
                    return True
            except:
                pass
            
            try:
                # Strategy 3: Generic role
                if self.page.locator('[role="dialog"]').first.is_visible(timeout=500):
                    logger.debug(f"✓ Dialog found via role selector (attempt {attempt_count})")
                    return True
            except:
                pass
            
            return False
        
        # Wait for dialog
        try:
            wait_for_condition(
                condition=dialog_visible,
                timeout=timeout_seconds,
                poll_interval=2.0,
                error_message=f"Dialog not found after {timeout_seconds}s"
            )
            logger.info(f"✓ Dialog visible (found in {attempt_count} attempts)")
        except WaitTimeoutError as e:
            logger.error(f"✗ Dialog timeout: {e}")
            
            # Debug capture
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Checkbox Dialog Not Found", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            
            raise AssertionError(
                f"[FAIL] ERSD Checkbox Dialog Not Visible after {timeout_seconds}s of dynamic waiting. "
                f"Strategies: data-qa, ARIA label, role=dialog. "
                f"Possible causes: 1) Dialog not rendering, 2) Page not fully loaded, 3) Selector mismatch"
            )
        
        # STEP 2: Locate checkbox using multi-strategy approach
        checkbox_locator = None
        
        # Strategy 1: Primary - Use data-qa selector (most reliable)
        try:
            logger.debug("Strategy 1: Locating checkbox with data-qa selector...")
            checkbox_primary = self.page.locator(docusign_locators.ERSD_CONSENT_CHECKBOX_PRIMARY)
            checkbox_primary.wait_for(state="attached", timeout=3000)
            checkbox_locator = checkbox_primary
            logger.info("✓ Checkbox found using primary data-qa selector")
        except Exception as e:
            logger.debug(f"Primary checkbox selector failed: {e}")
        
        # Strategy 2: Fallback - Use label text locator
        if checkbox_locator is None:
            try:
                logger.debug("Strategy 2: Locating checkbox using label text (fallback)...")
                checkbox_fallback = self.page.get_by_text(docusign_locators.ERSD_CONSENT_TEXT)
                checkbox_fallback.wait_for(state="visible", timeout=3000)
                checkbox_locator = checkbox_fallback
                logger.info("✓ Checkbox found using text-based selector (fallback)")
            except Exception as e:
                logger.debug(f"Fallback checkbox selector failed: {e}")
        
        # If checkbox not found, fail with diagnostic info
        if checkbox_locator is None:
            error_msg = (
                f"[FAIL] ERSD Consent Checkbox Not Found After Dialog Visible — "
                f"Expected: checkbox with data-qa='ersd-agree-checkbox' or text selector, "
                f"Actual: element not found. "
                f"Possible causes: 1) Modal not rendering checkbox, 2) Checkbox hidden by CSS, 3) Selector mismatch"
            )
            logger.error(error_msg)
            
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Checkbox Not Found", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            
            raise AssertionError(error_msg)
        
        # STEP 3: Click checkbox to enable consent
        logger.info("Clicking ERSD consent checkbox...")
        
        # CRITICAL: The label element intercepts pointer events, so we need to click the label
        # This allows the HTML for= attribute association to properly toggle the checkbox
        try:
            # Strategy 1: Try clicking the associated label (most reliable)
            logger.debug("Strategy 1: Attempting to click label element...")
            try:
                label_locator = self.page.locator(docusign_locators.ERSD_CONSENT_CHECKBOX_LABEL)
                label_locator.wait_for(state="visible", timeout=2000)
                label_locator.click()
                logger.info("✓ Checkbox clicked via label element")
            except Exception as label_error:
                logger.debug(f"Label click failed ({label_error}), trying checkbox directly...")
                
                # Strategy 2: Fallback - Click checkbox directly
                logger.debug("Strategy 2: Attempting to click checkbox input directly...")
                checkbox_locator.click()
                logger.info("✓ Checkbox clicked directly")
                
        except Exception as e:
            error_msg = f"Failed to click checkbox: {str(e).splitlines()[0]}"
            logger.error(error_msg)
            raise
        
        # STEP 4: CRITICAL - Verify checkbox is actually checked
        logger.info("Verifying checkbox is checked...")
        time.sleep(0.5)  # Brief wait for state change
        
        try:
            # If we used data-qa selector, check the input element directly
            if 'data-qa' in docusign_locators.ERSD_CONSENT_CHECKBOX_PRIMARY:
                checkbox_input = self.page.locator(docusign_locators.ERSD_CONSENT_CHECKBOX_PRIMARY)
                is_checked = checkbox_input.is_checked()
                logger.debug(f"Checkbox checked status: {is_checked}")
            else:
                # Alternative: check for checked attribute via evaluate
                is_checked = self.page.evaluate(
                    f"document.querySelector('{docusign_locators.ERSD_CONSENT_CHECKBOX_PRIMARY}')?.checked || false"
                )
                logger.debug(f"Checkbox checked (via evaluate): {is_checked}")
            
            if not is_checked:
                # Try alternative verification method
                logger.warning("Primary verification indicates unchecked state, attempting alternative check...")
                is_checked = self.page.evaluate(
                    "Array.from(document.querySelectorAll('input[type=\"checkbox\"]')).find(cb => cb.closest('[data-qa=\"ersd-modal\"]') && cb.checked) !== undefined"
                )
                logger.debug(f"Alternative check result: {is_checked}")
            
            if is_checked:
                logger.info("✓ VERIFIED: Checkbox is checked")
            else:
                # Try clicking again if first attempt didn't work
                logger.warning("Checkbox still unchecked, attempting second click...")
                checkbox_locator.click()
                time.sleep(0.5)
                
                # Verify again
                is_checked_retry = self.page.evaluate(
                    f"document.querySelector('{docusign_locators.ERSD_CONSENT_CHECKBOX_PRIMARY}')?.checked || false"
                )
                
                if not is_checked_retry:
                    error_msg = (
                        "[FAIL] ERSD Checkbox Not Checked — Checkbox was clicked but remains unchecked. "
                        "Possible causes: 1) Click didn't register, 2) Checkbox is disabled, 3) Event listener issue. "
                        "Verification: attempted .click() twice, both checks show unchecked state."
                    )
                    logger.error(error_msg)
                    raise AssertionError(error_msg)
                
                logger.info("✓ VERIFIED: Checkbox checked on retry")
        
        except Exception as e:
            error_msg = f"Failed to verify checkbox state: {str(e).splitlines()[0]}"
            logger.error(error_msg)
            raise
        
        logger.info("[PASS] ERSD Consent Checkbox: Verified as Checked")

    def click_ersd_continue_button(self, timeout: int = 120000):
        """
        Click the Continue button in the ERSD modal with dynamic waiting and verification.
        
        Uses `wait_for_condition()` to dynamically poll for button visibility over 120 seconds.
        
        Process:
        1. Wait for page to load (networkidle)
        2. Dynamically wait for ERSD modal to be visible (up to 120s)
        3. Locate button using multi-strategy approach (data-qa, get_by_role fallback)
        4. VERIFY button is enabled (must be clickable)
        5. Click button
        6. Verify state change after click
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 120000ms = 120 seconds)
            
        Raises:
            AssertionError: If modal or button not found after dynamic waiting
            
        Example:
            docusign_page.click_ersd_continue_button()  # Dynamic wait up to 2 mins
        """
        logger.info(f">>> STEP: Clicking ERSD Continue button (dynamic wait: {timeout}ms)")
        
        # STEP 1: Wait for page to be fully loaded and stable
        logger.info("Waiting for page to reach networkidle state...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.debug("✓ Page reached networkidle state")
        except Exception as e:
            logger.warning(f"Page didn't reach networkidle, continuing anyway: {str(e).splitlines()[0]}")
        
        # Brief wait for modal to initialize
        time.sleep(1)
        
        timeout_seconds = timeout / 1000  # Convert to seconds
        attempt_count = 0
        
        # STEP 2: Dynamically wait for button to be visible
        def button_visible_and_found() -> bool:
            """Poll for button visibility using multi-strategy."""
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count % 10 == 0:
                logger.info(f"⏳ Waiting for Continue button... ({attempt_count * 2}s elapsed)")
            
            try:
                # Strategy 1: data-qa selector
                btn = self.page.locator(docusign_locators.ERSD_CONTINUE_BUTTON_PRIMARY)
                if btn.is_visible(timeout=500):
                    logger.debug(f"✓ Button found via data-qa (attempt {attempt_count})")
                    return True
            except:
                pass
            
            try:
                # Strategy 2: get_by_role with button text
                btn = self.page.get_by_role("button", name=docusign_locators.ERSD_CONTINUE_BUTTON_TEXT)
                if btn.is_visible(timeout=500):
                    logger.debug(f"✓ Button found via get_by_role (attempt {attempt_count})")
                    return True
            except:
                pass
            
            return False
        
        # Wait for button to be visible
        try:
            wait_for_condition(
                condition=button_visible_and_found,
                timeout=timeout_seconds,
                poll_interval=2.0,
                error_message=f"Continue button not found after {timeout_seconds}s"
            )
            logger.info(f"✓ Continue button visible (found in {attempt_count} attempts)")
        except WaitTimeoutError as e:
            logger.error(f"✗ Button timeout: {e}")
            
            # Capture diagnostic info
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Continue Button Not Found - Screenshot", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            
            raise AssertionError(
                f"[FAIL] ERSD Continue Button Not Found after {timeout_seconds}s of dynamic waiting. "
                f"Strategies: data-qa, get_by_role. "
                f"Possible causes: 1) Modal not rendering button, "
                f"2) Consent checkbox not checked (button disabled until consent), 3) Page not loaded"
            )
        
        # STEP 3: Locate the button for interaction
        continue_button = None
        try:
            continue_button = self.page.locator(docusign_locators.ERSD_CONTINUE_BUTTON_PRIMARY)
            if not continue_button.is_visible():
                continue_button = self.page.get_by_role("button", name=docusign_locators.ERSD_CONTINUE_BUTTON_TEXT)
        except:
            continue_button = self.page.get_by_role("button", name=docusign_locators.ERSD_CONTINUE_BUTTON_TEXT)
        
        # STEP 4: CRITICAL - Verify button is enabled (not disabled)
        logger.info("Verifying Continue button is enabled...")
        try:
            is_enabled = continue_button.is_enabled()
            logger.debug(f"Button enabled status: {is_enabled}")
            
            if not is_enabled:
                error_msg = (
                    "[FAIL] ERSD Continue Button Disabled — Button found but is not clickable. "
                    "Probable cause: ERSD consent checkbox not checked. Consent MUST be checked before button becomes enabled. "
                    "Solution: Verify check_ersd_consent_checkbox() executed successfully."
                )
                logger.error(error_msg)
                raise AssertionError(error_msg)
            
            logger.info("✓ VERIFIED: Continue button is enabled")
        
        except Exception as e:
            if "disabled" in str(e).lower():
                error_msg = (
                    "[FAIL] Continue Button Check Failed — Button is disabled. "
                    f"Error: {str(e).splitlines()[0]}"
                )
                logger.error(error_msg)
                raise AssertionError(error_msg)
            logger.warning(f"Skipping enablement check, attempting click anyway: {e}")
        
        # STEP 5: Click the Continue button
        logger.info("Clicking Continue button...")
        try:
            continue_button.click()
            logger.info("✓ Continue button clicked")
        except Exception as e:
            error_msg = (
                f"Failed to click Continue button: {str(e).splitlines()[0]}. "
                "Possible causes: 1) Button not clickable, 2) Still initializing, 3) JavaScript error"
            )
            logger.error(error_msg)
            raise
        
        # STEP 6: Wait for state change after click
        logger.info("Waiting for page state change after button click...")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.debug("✓ Page reached networkidle after click")
        except Exception as e:
            logger.debug(f"Page didn't reach networkidle after click (expected, page may still be processing): {e}")
        
        time.sleep(1)  # Brief wait for any post-click animations
        
        logger.info("[PASS] ERSD Continue Button: Successfully Clicked and Verified")

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

    def fetch_docusign_review_and_continue_dialog_text(self, timeout: int = 120000) -> str:
        """
        Fetch the text from the 'Review and continue' dialog with dynamic waiting.
        
        Uses `wait_for_condition()` to dynamically poll for dialog visibility over 120 seconds.
        Multi-strategy approach:
        1. Primary: data-qa='ersd-modal' selector (most stable)
        2. Fallback 1: aria-label='Review and continue' (current DocuSign UI)
        3. Fallback 2: role='dialog' (generic fallback)
        
        If dialog not found after 120s:
        - Captures screenshot and page info for debugging
        - Includes diagnostic info in error message
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 120000ms = 120 seconds)
            
        Returns:
            The text content from the dialog's content element (stripped)
            
        Raises:
            AssertionError: If dialog or content element not found after polling
            
        Example:
            # Wait dynamically up to 2 minutes for dialog
            dialog_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
        """
        logger.info(f"Fetching DocuSign Review and Continue dialog text (dynamic wait: {timeout}ms)...")
        
        timeout_seconds = timeout / 1000  # Convert to seconds for wait_for_condition
        poll_interval = 2.0  # Poll every 2 seconds
        attempt_count = 0
        max_attempts = int(timeout_seconds / poll_interval)
        
        dialog_locator = None
        
        # Use wait_for_condition to dynamically poll for dialog visibility
        def find_and_verify_dialog() -> bool:
            """Poll for dialog using multi-strategy approach."""
            nonlocal dialog_locator, attempt_count
            attempt_count += 1
            
            if attempt_count % 10 == 0:  # Log every 10 attempts (~20 seconds)
                logger.info(f"⏳ Still waiting for dialog... ({attempt_count}/{max_attempts} attempts, {attempt_count * poll_interval:.0f}s elapsed)")
            
            # Strategy 1: Primary - data-qa selector
            try:
                test_dialog = self.page.locator(docusign_locators.ERSD_MODAL_PRIMARY)
                if test_dialog.is_visible(timeout=500):
                    dialog_locator = test_dialog
                    logger.debug(f"✓ Dialog found (attempt {attempt_count}): data-qa selector")
                    return True
            except:
                pass
            
            # Strategy 2: Fallback - ARIA label
            try:
                test_dialog = self.page.locator(docusign_locators.ERSD_MODAL_ARIA)
                if test_dialog.is_visible(timeout=500):
                    dialog_locator = test_dialog
                    logger.debug(f"✓ Dialog found (attempt {attempt_count}): ARIA label selector")
                    return True
            except:
                pass
            
            # Strategy 3: Fallback - generic role selector
            try:
                test_dialog = self.page.locator('[role="dialog"]').first
                if test_dialog.is_visible(timeout=500):
                    # Verify it contains expected content
                    content_check = test_dialog.locator(docusign_locators.DIALOG_CONTENT_P_TAG)
                    if content_check.count() > 0:
                        dialog_locator = test_dialog
                        logger.debug(f"✓ Dialog found (attempt {attempt_count}): generic role selector")
                        return True
            except:
                pass
            
            return False
        
        # Wait dynamically for dialog
        try:
            wait_for_condition(
                condition=find_and_verify_dialog,
                timeout=timeout_seconds,
                poll_interval=poll_interval,
                error_message=f"Dialog not found after {timeout_seconds}s of polling (multi-strategy: data-qa, ARIA label, role=dialog)"
            )
            logger.info(f"✓ Review and Continue dialog found after {attempt_count} polling attempts")
        except WaitTimeoutError as e:
            logger.error(f"✗ Dialog wait timeout after {timeout_seconds}s: {e}")
            
            # Capture diagnostic info on failure
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Dialog Not Found - Screenshot", attachment_type=allure.attachment_type.PNG)
                
                page_html = self.page.content()
                allure.attach(page_html, name="Dialog Not Found - Page HTML", attachment_type=allure.attachment_type.HTML)
                
                current_url = self.page.url
                logger.error(f"Current URL: {current_url}")
                allure.attach(f"URL: {current_url}", name="Dialog Not Found - URL", attachment_type=allure.attachment_type.TEXT)
            except Exception as debug_error:
                logger.warning(f"Could not capture diagnostic info: {debug_error}")
            
            error_msg = (
                f"[FAIL] DocuSignPage: Review and Continue Dialog Not Found — "
                f"Expected: dialog with data-qa='ersd-modal' OR aria-label='Review and continue' found, "
                f"Actual: dialog not found after {timeout_seconds}s of dynamic polling. "
                f"Strategies attempted: 1) data-qa selector, 2) ARIA label, 3) role=dialog. "
                f"Details: Dialog must be rendered and visible. Current URL: {self.page.url}"
            )
            raise AssertionError(error_msg)
        
        if dialog_locator is None:
            raise AssertionError("[INTERNAL ERROR] Dialog locator is None despite wait_for_condition success")
        
        # Get the text from the p tag with data-qa="email-message-content"
        logger.info("Fetching content from dialog...")
        try:
            content_locator = dialog_locator.locator(docusign_locators.DIALOG_CONTENT_P_TAG)
            content_locator.wait_for(state="visible", timeout=5000)
            logger.debug("✓ Content p tag is visible")
        except Exception as e:
            logger.error(f"✗ Content p tag not found within the dialog: {e}")
            
            # Capture screenshot showing dialog but missing content
            try:
                screenshot = self.page.screenshot()
                allure.attach(screenshot, name="Dialog Content Not Found", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            
            raise AssertionError(
                f"[FAIL] DocuSignPage: Dialog Content Element Not Found — "
                f"Expected: p[data-qa='email-message-content'] found within dialog, "
                f"Actual: element not found. Details: Content element must exist in the Review and Continue dialog."
            )
        
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


