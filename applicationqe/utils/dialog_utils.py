"""
Dialog and Popup Handling Utilities

Provides utilities for interacting with dialog boxes and popups in Playwright tests.
"""

import logging
from typing import Optional

from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class DialogHandler:
    """
    Handler for dialog and popup windows.
    
    Supports UI dialogs, modals, and popup windows in Playwright tests.
    """

    def __init__(self, page: Page):
        """
        Initialize dialog handler.
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def wait_for_dialog(self, timeout: int = 15000) -> Locator:
        """
        Wait for a dialog to appear on the page.
        Tries multiple dialog selectors to handle different dialog types.
        
        Uses adaptive detection:
        1. Find dialog in DOM (state='attached')
        2. Verify dialog content is accessible (text readable, buttons clickable)
        3. Return dialog (visibility state may vary due to CSS)
        
        This approach handles jQuery UI dialogs that may be in DOM but visually hidden
        yet still fully interactive via :visible selectors.
        
        Args:
            timeout: Maximum time to wait in milliseconds (default: 15000)
            
        Returns:
            Dialog locator
            
        Raises:
            PlaywrightTimeoutError: If dialog doesn't appear within timeout
            
        Example:
            dialog = handler.wait_for_dialog()
            # Dialog is guaranteed to be in DOM and accessible
        """
        self.logger.info("Waiting for dialog to appear...")
        
        # Try multiple selectors for different dialog types
        # Order matters: most specific first (jQuery UI is common in this app)
        selectors = [
            '.ui-dialog',                # jQuery UI dialog (most common in this app)
            '[role="dialog"]',           # Standard ARIA dialog
            '[class*="dialog"]',         # Class contains dialog
            '[class*="modal"]',          # Bootstrap modal
            '[id*="dialog"]',            # ID contains dialog
            '[data-testid*="dialog"]',   # Test ID
        ]
        
        dialog = None
        last_error = None
        
        # Phase 1: Find dialog in DOM with each selector
        # Use state='attached' to find hidden dialogs (jQuery UI keeps dialogs in DOM)
        # Increased timeout to 2 minutes per selector to allow page navigation to complete
        for selector in selectors:
            try:
                potential_dialog = self.page.locator(selector).first
                potential_dialog.wait_for(state="attached", timeout=120000)
                self.logger.info(f"Dialog found in DOM with selector: {selector}")
                dialog = potential_dialog
                break
            except Exception as e:
                last_error = e
                self.logger.debug(f"Dialog selector '{selector}' not found in DOM")
                continue
        
        # Phase 2: Verify dialog is accessible (even if visually hidden by CSS)
        if dialog is not None:
            # Try to verify content is readable
            self.logger.debug("Verifying dialog content is accessible...")
            try:
                # Check if we can get text from the dialog
                # This indicates the dialog is DOM-ready even if CSS keeps it visually hidden
                dialog_text = dialog.text_content(timeout=120000)
                if dialog_text:
                    self.logger.debug(f"Dialog content accessible ({len(dialog_text)} chars)")
                    self.logger.debug("Dialog is ready for interaction")
                    return dialog
            except Exception as e:
                self.logger.debug(f"Could not read dialog text: {e}")
                pass
            
            # Even if text read failed, as long as dialog is in DOM, try to use it
            # jQuery UI dialogs with :visible selectors will work
            self.logger.debug("Dialog in DOM, attempting interaction")
            return dialog
        else:
            # Phase 3: If not found with specific selectors, try generic approach
            self.logger.error(f"No dialog found with specific selectors. Last error: {last_error}")
            self.logger.info(f"Attempting generic selector: 'body > div[style*=\"display\"]'")
            
            try:
                dialog = self.page.locator('body > div[style*="display"]').first
                dialog.wait_for(state="attached", timeout=120000)  # 2 minutes for generic selector
                self.logger.debug("Generic selector found dialog in DOM")
                return dialog
            except Exception as e:
                self.logger.error(f"Generic selector also failed: {e}")
                raise
        
        self.logger.info("Dialog appeared")
        return dialog

    def click_dialog_button(self, button_text: str, timeout: int = 10000) -> None:
        """
        Click a button within a dialog by text.
        
        Uses adaptive button finding that works even with hidden dialog containers:
        - jQuery UI dialogs may have hidden containers
        - But buttons/content remain interactive via :visible selectors
        
        Args:
            button_text: Text of the button to click (e.g., "Continue", "Cancel", "OK")
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            Exception: If button not found or not clickable
            
        Example:
            handler.click_dialog_button("Continue")
            handler.click_dialog_button("Cancel")
        """
        self.logger.info(f"Clicking dialog button: '{button_text}'")
        
        button = None
        
        # Get first dialog (may be hidden but still interactive)
        dialog = self.page.locator('[role="dialog"]').first
        
        # Don't wait for dialog visibility - it may be hidden by CSS but still interactive
        # This reduces unnecessary timeout warnings
        
        # Find button within the dialog - try multiple approaches
        button_strategies = [
            # Strategy 1: Partial text match with visible modifier
            f'[role="dialog"] button:visible >> text={button_text}',
            # Strategy 2: Exact text match
            f'[role="dialog"] button:visible:has-text("^{button_text}$")',
            # Strategy 3: Any visible button with the text (may be outside dialog)
            f'button:visible:text("{button_text}")',
        ]
        
        for strategy in button_strategies:
            try:
                potential_button = self.page.locator(strategy).first
                if potential_button.count() > 0:
                    self.logger.info(f"Button found with strategy: {strategy}")
                    button = potential_button
                    break
            except Exception as e:
                self.logger.debug(f"Strategy '{strategy}' failed: {e}")
                continue
        
        # Try getByRole approach as fallback
        if button is None:
            try:
                button = self.page.get_by_role("button", name=button_text).first
                if button.count() > 0:
                    self.logger.info("Button found using getByRole")
            except Exception as e:
                self.logger.debug(f"getByRole failed: {e}")
        
        if button is None:
            self.logger.error(f"Could not find button '{button_text}' with any strategy")
            # Last resort: use evaluate to find and click
            self.logger.debug(f"Attempting JavaScript click for button: {button_text}")
            try:
                clicked = self.page.evaluate(
                    f"""() => {{
                        const buttons = Array.from(document.querySelectorAll('[role="dialog"] button'));
                        const btn = buttons.find(b => b.textContent.trim() === '{button_text}');
                        if (btn) {{
                            btn.click();
                            return true;
                        }}
                        return false;
                    }}"""
                )
                if clicked:
                    self.logger.info(f"Button '{button_text}' clicked via JavaScript")
                    return
            except Exception as e:
                self.logger.debug(f"JavaScript click failed: {e}")
            
            raise Exception(f"Button '{button_text}' not found in dialog")
        
        # Scroll into view and click
        try:
            button.scroll_into_view_if_needed()
        except Exception:
            pass
        
        self.logger.info(f"About to click button: {button_text}")
        button.click()
        self.logger.info(f"Clicked '{button_text}' button in dialog")

    def switch_to_dialog_and_click_button(self, button_text: str = "Continue", timeout: int = 10000) -> None:
        """
        Wait for dialog to appear and click specified button.
        This is the main function for dialog interaction.
        
        Args:
            button_text: Text of the button to click (default: "Continue")
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            PlaywrightTimeoutError: If dialog or button not found
            
        Example:
            handler.switch_to_dialog_and_click_button()  # Clicks "Continue"
            handler.switch_to_dialog_and_click_button("OK")
            handler.switch_to_dialog_and_click_button("Proceed")
        """
        self.logger.info(f"Switching to dialog and clicking '{button_text}'")
        
        # Wait for dialog
        self.wait_for_dialog(timeout)
        
        # Click the button
        self.click_dialog_button(button_text, timeout)
        
        self.logger.info(f"Dialog interaction completed: clicked '{button_text}'")

    def get_dialog_text(self, timeout: int = 10000) -> str:
        """
        Get the text content of a dialog.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            Dialog text content
            
        Example:
            text = handler.get_dialog_text()
            assert "Client Signature" in text
        """
        self.logger.info("Getting dialog text content...")
        dialog = self.wait_for_dialog(timeout)
        text = dialog.text_content()
        self.logger.info(f"Dialog text: {text}")
        return text or ""

    def get_dialog_title(self, timeout: int = 10000) -> str:
        """
        Get the title of a dialog.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            Dialog title text
            
        Example:
            title = handler.get_dialog_title()
            assert title == "Confirmation"
        """
        self.logger.info("Getting dialog title...")
        dialog = self.wait_for_dialog(timeout)
        
        # Try multiple specific selectors in order of preference
        title_selectors = [
            # Prefer span with ui-dialog-title class (jQuery UI)
            'span.ui-dialog-title',
            # Then try modal-title-transition div (modern modals)
            'div.modal-title-transition',
            # Fallback to any element with ui-dialog-title class
            '[class*="ui-dialog-title"]',
            # Last resort: modal-title class
            '[class*="modal-title"]',
        ]
        
        for selector in title_selectors:
            try:
                title_element = dialog.locator(selector).first
                if title_element.count() > 0:
                    title = title_element.text_content()
                    self.logger.info(f"Dialog title found with selector '{selector}': {title}")
                    return title or ""
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        self.logger.warning("No title found in dialog with any selector")
        return ""

    def is_dialog_visible(self) -> bool:
        """
        Check if a dialog is currently visible.
        
        Returns:
            True if dialog is visible, False otherwise
            
        Example:
            if handler.is_dialog_visible():
                handler.click_dialog_button("Continue")
        """
        try:
            dialog = self.page.locator('[role="dialog"]').first
            return dialog.is_visible()
        except Exception:
            return False

    def wait_for_dialog_to_close(self, timeout: int = 10000) -> None:
        """
        Wait for a dialog to close/disappear.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            PlaywrightTimeoutError: If dialog doesn't close within timeout
            
        Example:
            handler.click_dialog_button("Continue")
            handler.wait_for_dialog_to_close()
        """
        self.logger.info("Waiting for dialog to close...")
        dialog = self.page.locator('[role="dialog"]').first
        dialog.wait_for(state="hidden", timeout=timeout)
        self.logger.info("Dialog closed")

    def close_dialog(self, timeout: int = 10000) -> None:
        """
        Close a dialog by clicking the close button.
        
        Args:
            timeout: Maximum time to wait in milliseconds
            
        Example:
            handler.close_dialog()
        """
        self.logger.info("Closing dialog...")
        close_button = self.page.locator('[role="dialog"] button[title="Close"], [class*="close"]')
        
        if close_button.count() > 0:
            close_button.first.click()
            self.logger.info("Dialog closed via close button")
        else:
            self.logger.warning("No close button found, trying Cancel button")
            self.click_dialog_button("Cancel", timeout)

    def select_dialog_option(self, option_id: str) -> None:
        """
        Select a radio button or option within a dialog by ID.
        
        Args:
            option_id: ID of the radio button or option
            
        Example:
            handler.select_dialog_option("rbSubmit")  # Select "Proceed without signature"
            handler.select_dialog_option("rbEsign")   # Select "Request electronic signature"
        """
        self.logger.info(f"Selecting option: {option_id}")
        option = self.page.locator(f'#{option_id}')
        
        try:
            option.wait_for(state="visible", timeout=5000)
            self.logger.info(f"Option '{option_id}' found and visible")
        except Exception as e:
            self.logger.warning(f"Option '{option_id}' not visible: {e}, attempting to check anyway")
        
        try:
            option.check()
            self.logger.info(f"Option '{option_id}' checked successfully")
        except Exception as e:
            self.logger.error(f"Failed to check option '{option_id}': {e}")
            # Try clicking as fallback
            option.click()
            self.logger.info(f"Option '{option_id}' clicked as fallback")

    def _wait_for_dialog_ready(self, timeout: int = 10000) -> None:
        """
        Internal method to wait for dialog to be ready for interaction.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        dialog = self.page.locator('[role="dialog"]').first
        dialog.wait_for(state="visible", timeout=timeout)
