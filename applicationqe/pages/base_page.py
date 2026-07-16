# pages/base_page.py

"""
Base Page class with common functionality for all page objects
"""

import logging
import os
import random
import re
import string
import time
from typing import Any, Callable, List, Literal, Optional, Union

import allure
from playwright.sync_api import Download, Error as PlaywrightError
from playwright.sync_api import FrameLocator, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common functionality like navigation, waits, and assertions.
    """

    _healing_engine: Optional[AutoHealingEngine] = None  # Shared across all page objects

    def __init__(self, page: Page, base_url: Optional[str] = None, home_url: Optional[str] = None):
        self.page = page
        self.context = page  # alias so pages can use either self.page or self.context
        # Accept either base_url or home_url; both refer to the application root URL.
        self.base_url = base_url or home_url or ""
        self.home_url = self.base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.promo_chat_close_icon: Locator = page.locator("#promoChatCloseIcon > g > path")
        self.chat_close_icon: Locator = page.locator("button#xBtnSvg path[fill='black']")

        # Initialize healing engine once
        if BasePage._healing_engine is None:
            BasePage._healing_engine = AutoHealingEngine("locator_mappings.json")
            self.logger.info("Auto-healing engine initialized")

        # Auto-accept Ketch cookie banner (handles shadow DOM)
        page.add_init_script("""
            (function setupKetchObserver() {
                function tryAccept() {
                    const root = document.querySelector('#lanyard_root');
                    if (!root) return false;
                    const shadow = root.shadowRoot;
                    const buttons = shadow
                        ? shadow.querySelectorAll('button')
                        : root.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.textContent.trim().includes('Accept All')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
                function startObserver() {
                    if (tryAccept()) return;
                    const observer = new MutationObserver(() => {
                        if (tryAccept()) observer.disconnect();
                    });
                    observer.observe(document.body || document.documentElement, { childList: true, subtree: true });
                }
                if (document.body) {
                    startObserver();
                } else {
                    document.addEventListener('DOMContentLoaded', startObserver);
                }
            })();
        """)

    # ------------------------------------------------------------------
    # Auto-healing helper
    # ------------------------------------------------------------------

    def _heal_and_retry(self, locator: Locator, action_fn: Callable[[Locator], Any]) -> Any:
        """Try *action_fn* on *locator*; on failure, auto-heal and retry.

        Args:
            locator: Original Playwright locator.
            action_fn: Receives a (possibly healed) locator and performs the
                       desired interaction.  Its return value is propagated.

        Returns:
            Whatever *action_fn* returns.

        Raises:
            The original exception when every healing strategy fails.
        """
        try:
            return action_fn(locator)
        except (PlaywrightError, PlaywrightTimeoutError, Exception):
            self.logger.warning("Action failed with original locator")
            self.logger.info("≡ƒöº Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Strategy 1: text-based name extraction
            if "name=" in selector_str:
                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    self.logger.info(f"Trying text-based healing with: '{text}'")
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Auto-healing SUCCESS - Found by text '{text}'")
                        return action_fn(healed)

            # Strategy 2: AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, _ = self._healing_engine.find_element(self.page, selector_str)
                if healed_locator:
                    self.logger.info("Auto-healing SUCCESS using healing engine!")
                    return action_fn(healed_locator)

            self.logger.error("Auto-healing FAILED - element not found")
            raise

    def navigate_to(
        self,
        url: str,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded",
    ) -> None:
        """Navigate to a specific URL"""
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def scroll_to_top(self) -> None:
        """Reset viewport to top on page and iframe content (if present)."""

        try:
            self.page.evaluate(
                """
                () => {
                    if (history && 'scrollRestoration' in history) {
                        history.scrollRestoration = 'manual';
                    }

                    const root = document.scrollingElement || document.documentElement || document.body;
                    if (root) root.scrollTop = 0;
                    document.documentElement.scrollTop = 0;
                    if (document.body) document.body.scrollTop = 0;
                    window.scrollTo(0, 0);

                    // If focus sits inside a scrollable container, reset those ancestors too.
                    let node = document.activeElement;
                    while (node && node !== document.body) {
                        if (node.scrollTop > 0) node.scrollTop = 0;
                        node = node.parentElement;
                    }
                }
                """
            )
        except Exception:
            pass

        try:
            if self.page.locator("#iframeWrapper").count() > 0:
                self.page.frame_locator("#iframeWrapper").locator("body").evaluate(
                    """
                    el => {
                        const doc = el.ownerDocument;
                        const win = doc.defaultView;
                        const root = doc.scrollingElement || doc.documentElement || doc.body;

                        if (root) root.scrollTop = 0;
                        doc.documentElement.scrollTop = 0;
                        if (doc.body) doc.body.scrollTop = 0;
                        if (win) win.scrollTo(0, 0);

                        // Reset focused input ancestors (modal/body containers).
                        let node = doc.activeElement;
                        while (node && node !== doc.body) {
                            if (node.scrollTop > 0) node.scrollTop = 0;
                            node = node.parentElement;
                        }
                    }
                    """
                )
        except Exception:
            pass

    def active_root(self) -> Union[Page, FrameLocator]:
        """
        Return the active root context: iframe if present, otherwise page.
        Automatically detects whether we're in navbar flow (iframe) or smoke flow (page).
        All pages should use this method to ensure dual-flow compatibility.
        """
    #    self.wait_for_load_state("domcontentloaded", timeout=30000)
        try:
            iframe_wrapper = self.page.locator("#iframeWrapper")
            if iframe_wrapper.count() > 0:
                self.logger.debug("Active root: iframe (#iframeWrapper detected)")
                # Wait for iframe to be visible and ready
                iframe_wrapper.wait_for(state="visible", timeout=5000)
                return self.page.frame_locator("#iframeWrapper")
        except Exception:
            pass
        self.logger.debug("Active root: page (no iframe, using top-level DOM)")
        return self.page
    
    def get_In_new_tab(
        self,
        url: str,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded",
        timeout: int = 30000,
    ) -> Page:
        """
        Open a new browser tab and navigate to the provided URL.

        Args:
            url: Target URL to open in the new tab
            wait_until: Load state to wait for after navigation
            timeout: Navigation timeout in milliseconds

        Returns:
            New Page object
        """
        self.logger.info(f"Opening new tab and navigating to: {url}")

        new_tab = self.page.context.new_page()
        new_tab.goto(url, wait_until=wait_until, timeout=timeout)

        self.logger.info(f"New tab opened successfully. Current URL: {new_tab.url}")
        return new_tab

    # dynamic wait method(condition based)
    def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "domcontentloaded",
        timeout: int = 30000,
    ) -> None:
        """Wait for page to reach specified load state"""
        self.page.wait_for_load_state(state, timeout=timeout)

    # static wait method
    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a specific amount of time"""
        self.page.wait_for_timeout(milliseconds)

    def switch_to_new_tab_and_close(self) -> None:
        """Close newly opened tabs and return focus to the original page."""
        current_page = self.page
        pages = list(current_page.context.pages)

        for tab in pages:
            if tab != current_page:
                try:
                    tab.close()
                except Exception as e:
                    self.logger.warning(f"Failed to close tab: {str(e).splitlines()[0]}")

        try:
            current_page.bring_to_front()
        except Exception:
            pass

    def _wait_for_dom_settled(self, timeout: int = 5000) -> None:
        """Best-effort guard against clicking during in-progress navigation."""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            pass

    def click(self, locator: Locator, timeout: int = 10000, no_wait_after: bool = False) -> None:
        """Click an element with wait and logging - includes auto-healing"""
        click_kwargs = {}
        if no_wait_after:
            click_kwargs["no_wait_after"] = True
        try:
            self._wait_for_dom_settled(timeout=min(timeout, 5000))
            locator.wait_for(state="visible", timeout=timeout)
            try:
                locator.scroll_into_view_if_needed(timeout=min(timeout, 3000))
            except Exception:
                pass
            locator.click(timeout=timeout, **click_kwargs)
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"Click failed with original locator: {str(e).splitlines()[0]}")
            self._wait_for_dom_settled(timeout=min(timeout, 5000))
            # Quick fallback for actionable-but-flaky elements (viewport overlays, animations, hidden-tab controls)
            try:
                locator.click(timeout=min(timeout, 5000), force=True, **click_kwargs)
                return
            except Exception:
                pass

            # JS click fallback for elements blocked by overlays or iframes
            try:
                locator.evaluate("el => el.click()")
                self.logger.info("Γ£ô JS click fallback succeeded")
                return
            except Exception:
                pass

            # Scroll + JS click fallback for off-screen elements
            try:
                locator.scroll_into_view_if_needed(timeout=min(timeout, 3000))
                locator.evaluate("el => el.click()")
                self.logger.info("Γ£ô Scroll + JS click fallback succeeded")
                return
            except Exception:
                pass

            self.logger.info("≡ƒöº Auto-healing: Trying alternative strategies...")

            # Extract the name/text from original get_by_role locator
            selector_str = str(locator)

            # Strategy 1: Try get_by_text with extracted name
            if "name=" in selector_str:
                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    self.logger.info(f"Trying text-based healing with: '{text}'")
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Γ£ô Auto-healing SUCCESS - Found by text '{text}'")
                        healed.click(timeout=min(timeout, 5000))
                        return

            # Strategy 2: Use AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Γ£ô Auto-healing SUCCESS using healing engine!")
                    healed_locator.wait_for(state="visible", timeout=timeout)
                    healed_locator.click(timeout=min(timeout, 5000))
                    return

            self.logger.error("Γ£ù Auto-healing FAILED - element not found")
            raise

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        """Fill a text field with wait and logging - includes auto-healing"""
        self.logger.info("Filling field with text")
        try:
            locator.wait_for(state="visible", timeout=timeout)
            locator.fill(text)
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"Fill failed with original locator: {str(e).splitlines()[0]}")
            self.logger.info("Attempting auto-healing...")

            selector_str = str(locator)
            if self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )

                if healed_locator:
                    self.logger.info("Γ£ô Auto-healing successful! Filling healed element...")
                    healed_locator.wait_for(state="visible", timeout=timeout)
                    healed_locator.fill(text)
                    return

            self.logger.error("Γ£ù Auto-healing failed - element not found")
            raise

    def tab_out(self, locator: Optional[Locator] = None, timeout: int = 10000) -> None:
        """Tab out either from a specific element or from current keyboard focus."""
        try:
            if locator is not None:
                self.logger.info("Pressing Tab on element")
                locator.wait_for(state="visible", timeout=timeout)
                locator.press("Tab")
            else:
                self.logger.info("Pressing Tab from current focus")
                self.page.keyboard.press("Tab")
        except Exception as e:
            self.logger.warning(f"Tab out failed: {e}")

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        """Get text content from an element with auto-healing"""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return locator.text_content() or ""
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"get_text failed with original locator: {str(e).splitlines()[0]}")
            self.logger.info("≡ƒöº Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Try text-based healing
            if "name=" in selector_str:
                import re

                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Γ£ô Auto-healing SUCCESS - Found by text '{text}'")
                        return healed.text_content() or ""

            # Use AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Γ£ô Auto-healing SUCCESS using healing engine!")
                    return healed_locator.text_content() or ""

            self.logger.error("Γ£ù Auto-healing FAILED - element not found")
            raise

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        """Check if element is visible"""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(
        self,
        locator: Locator,
        state: Literal["attached", "detached", "hidden", "visible"] = "visible",
        timeout: int = 10000,
    ) -> None:
        """Wait for element to reach specified state with auto-healing"""
        self.logger.info(f"Waiting for element to be {state}")
        try:
            locator.wait_for(state=state, timeout=timeout)
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"wait_for_element failed with original locator: {str(e).splitlines()[0]}")
            self.logger.info("≡ƒöº Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Try text-based healing
            if "name=" in selector_str:
                import re

                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Γ£ô Auto-healing SUCCESS - Found by text '{text}'")
                        healed.wait_for(state=state, timeout=timeout)
                        return

            # Use AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Γ£ô Auto-healing SUCCESS using healing engine!")
                    healed_locator.wait_for(state=state, timeout=timeout)
                    return

            self.logger.error("Γ£ù Auto-healing FAILED - element not found")
            raise



    def close_chat_popups(self) -> None:
        """Close promo/secondary chat popups and cookie consent banners if visible."""
        # Dismiss Ketch "Accept All" cookie consent banner
        try:
            accept_all = self.page.locator("#ketch-banner-button-primary")
            if accept_all.is_visible():
                accept_all.click(timeout=3000)
                self.logger.info("Ketch Accept All cookie banner dismissed")
        except Exception:
            pass

        # Dismiss legacy "Allow All" cookie popup
        try:
            allow_all = self.page.get_by_role("button", name="Allow All")
            if allow_all.is_visible():
                allow_all.click(timeout=3000)
                self.logger.info("Allow All cookie popup dismissed")
        except Exception:
            pass

        try:
            if self.promo_chat_close_icon.is_visible():
                self.promo_chat_close_icon.click(timeout=3000)
                self.logger.info("Promo chat popup closed")
        except Exception:
            pass

        try:
            if self.chat_close_icon.is_visible():
                self.chat_close_icon.click(timeout=3000)
                self.logger.info("Secondary chat popup closed")
        except Exception:
            pass

    def highlight_and_screenshot(
        self,
        locator: Locator,
        name: str,
        color: str = "green",
        border_width: str = "3px",
        take_screenshot: bool = True,
    ) -> Optional[bytes]:
        """
        Highlight an element with a colored border and optionally take a screenshot.

        Usage patterns:
            # Highlight + screenshot (default)
            self.highlight_and_screenshot(my_locator, "step_name")

            # Highlight only (no screenshot)
            self.highlight_and_screenshot(my_locator, "step_name", take_screenshot=False)

            # Highlight in red + screenshot
            self.highlight_and_screenshot(my_locator, "error_field", color="red")

        Args:
            locator: Playwright Locator to highlight
            name: Name for the Allure screenshot attachment
            color: Border color (e.g. 'green', 'red', '#FF0000')
            border_width: CSS border width (default '3px')
            take_screenshot: If True, take screenshot and attach to Allure. If False, only highlight.

        Returns:
            Screenshot bytes if take_screenshot is True, else None
        """
        style_js = (
            f"el => {{ "
            f"el.style.outline = '{border_width} solid {color}'; "
            f"el.style.outlineOffset = '2px'; "
            f"el.style.boxShadow = '0 0 10px 4px {color}'; "
            f"}}"
        )
        restore_js = "el => { el.style.outline = ''; el.style.outlineOffset = ''; el.style.boxShadow = ''; }"

        try:
            locator.first.scroll_into_view_if_needed(timeout=3000)
            locator.first.evaluate(style_js)
            self.logger.info(f"Highlighted '{name}' in {color}")

            if take_screenshot:
                self.page.wait_for_timeout(300)
                screenshot_bytes = self.page.screenshot()
                allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)
                self.logger.info(f"Screenshot '{name}' attached to Allure")
                locator.first.evaluate(restore_js)
                return screenshot_bytes
            else:
                self.page.wait_for_timeout(300)
                locator.first.evaluate(restore_js)
                return None
        except Exception as e:
            self.logger.warning(f"highlight_and_screenshot failed for '{name}': {str(e).splitlines()[0]}")
            if take_screenshot:
                screenshot_bytes = self.page.screenshot()
                allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)
                return screenshot_bytes
            return None

    def screenshot(self, name: str) -> bytes:
        """Take a screenshot and return bytes"""
        self.logger.info(f"Taking screenshot: {name}")
        return self.page.screenshot()

    def screenshot_with_allure(self, name: str, path: Optional[str] = None) -> bytes:
        """
        Take a screenshot, optionally save to disk, and attach to Allure report.

        Args:
            name: Name for the Allure attachment
            path: Optional file path to save screenshot to disk

        Returns:
            Screenshot bytes
        """
        self.logger.info(f"Taking screenshot: {name}")
        if path:
            screenshot_bytes = self.page.screenshot(path=path)
            self.logger.info(f"Screenshot saved: {path}")
        else:
            screenshot_bytes = self.page.screenshot()

        # Attach to Allure report
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)
        return screenshot_bytes

    def capture_additional_screenshot(
        self,
        name: str,
        path: Optional[str] = None,
        full_page: bool = True,
    ) -> bytes:
        """Capture an additional screenshot and attach it to Allure."""
        self.logger.info(f"Capturing additional screenshot: {name}")
        screenshot_bytes = self.page.screenshot(path=path, full_page=full_page)
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)
        return screenshot_bytes

    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    def go_back(self) -> None:
        """Navigate back in browser history"""
        self.logger.info("Navigating back")
        self.page.go_back()

    def refresh(self) -> None:
        """Refresh the current page"""
        self.logger.info("Refreshing page")
        self.page.reload()

    def empty_field(self, locator: Locator) -> None:
        """
        Clear a field by clicking and filling with empty string.
        Useful for input fields that need explicit clearing.

        Args:
            locator: Playwright locator for the field to clear
        """
        self.logger.info("Clearing field")
        locator.click()
        locator.fill("")
    
    def generate_random_data(self, size: int) -> str:
        """
        Generate random data for test purposes.

        Args:
            size: Length of the random string to generate

        Returns:
            str: Random string of lowercase ASCII characters
        """
        return ''.join(random.choices(string.ascii_lowercase, k=size))

    def hide_chatbot(self) -> None:
        """
        Hide the chatbot element using CSS display none.
        Attempts to find and hide the chatbot by CSS selector #chatpillid
        """
        try:
            chatbot_locator = self.page.locator("#chatpillid")
            
            # Check if element is visible before attempting to hide
            try:
                chatbot_locator.wait_for(state="visible", timeout=5000)
                is_displayed = True
            except PlaywrightTimeoutError:
                is_displayed = False
            
            if is_displayed:
                # Hide the chatbot using JavaScript
                self.page.evaluate(
                    "element => element.setAttribute('style','display: none !important;')",
                    chatbot_locator.element_handle()
                )
                self.logger.info("Chatbot element hidden successfully")
            else:
                self.logger.info("Chatbot element not visible, skipping hide operation")
                
        except Exception as e:
            self.logger.info(f"Could not hide chatbot: {str(e).splitlines()[0]}")

    # ==================== MODAL/DIALOG HANDLING ====================

    def wait_for_dialog(self, dialog_locator: Locator, timeout: int = 10000) -> None:
        """
        Wait for a modal/dialog to appear and be visible.
        
        Args:
            dialog_locator: Playwright locator for the dialog
            timeout: Timeout in milliseconds
        """
        dialog_locator.wait_for(state="visible", timeout=timeout)

    def close_dialog(self, dialog_locator: Locator, close_button_locator: Locator, timeout: int = 10000) -> None:
        """
        Close a modal/dialog by clicking the close button and wait for dismissal.
        
        Args:
            dialog_locator: Playwright locator for the dialog
            close_button_locator: Playwright locator for the close button
            timeout: Timeout in milliseconds
        """
        self.logger.info("Closing dialog")
        close_button_locator.click()
        # Wait for dialog to disappear
        dialog_locator.wait_for(state="hidden", timeout=timeout)
        self.logger.info("Dialog closed successfully")

    def handle_modal_with_action(self, dialog_locator: Locator, action_locator: Locator, close_button_locator: Locator) -> None:
        """
        Open modal, perform an action, and close it.
        
        Args:
            dialog_locator: Playwright locator for the dialog
            action_locator: Playwright locator for the action element (button to click)
            close_button_locator: Playwright locator for the close button
        """
        self.logger.info("Handling modal with action")
        self.wait_for_dialog(dialog_locator)
        action_locator.click()
        self.logger.info("Action performed on modal")
        self.close_dialog(dialog_locator, close_button_locator)

    # ==================== FORM HANDLING ====================

    def select_radio_button(self, radio_locator: Locator, label: str) -> None:
        """
        Select a radio button by its label text.
        
        Args:
            radio_locator: Playwright locator for radio button group
            label: Label text to match
        """
        self.logger.info(f"Selecting radio button: {label}")
        radio = self.page.get_by_label(label, exact=True)
        radio.click()
        self.logger.info(f"Radio button '{label}' selected")

    def select_checkbox(self, checkbox_locator: Locator, check: bool = True) -> None:
        """
        Check or uncheck a checkbox.
        
        Args:
            checkbox_locator: Playwright locator for the checkbox
            check: True to check, False to uncheck
        """
        action = "Checking" if check else "Unchecking"
        self.logger.info(f"{action} checkbox")
        if check:
            checkbox_locator.check()
        else:
            checkbox_locator.uncheck()
        self.logger.info(f"Checkbox {'checked' if check else 'unchecked'}")

    # ==================== DROPDOWN/SELECT ====================

    def select_dropdown_by_value(self, select_locator: Locator, value: str) -> None:
        """
        Select option from dropdown/select by value attribute.
        
        Args:
            select_locator: Playwright locator for the select element
            value: Value attribute to select
        """
        self.logger.info(f"Selecting dropdown option by value: {value}")
        select_locator.select_option(value)
        self.logger.info(f"Dropdown option '{value}' selected")

    def select_by_visible_text(self, select_locator: Locator, visible_text: str) -> None:
        """
        Select dropdown option by visible text (mirrors Java Selenium selectByValue behavior).
        This method:
        - Waits for element to be clickable
        - Clicks to open dropdown
        - Selects by matching visible text
        - Waits 500ms after selection
        - Clicks element again to close
        
        Args:
            select_locator: Playwright locator for the select element
            visible_text: Visible text of the option to select
        """
        self.logger.info(f"Selecting dropdown option by visible text: {visible_text}")
        
        # Wait for element to be clickable and click
        select_locator.wait_for(state="visible", timeout=20000)
        select_locator.click()
        
        # Select by label (visible text)
        select_locator.select_option(label=visible_text)
        
        # Wait for UI to update
        self.wait_for_timeout(500)
        
        # Click again to close/confirm
        select_locator.click()
        
        self.logger.info(f"Dropdown option '{visible_text}' selected successfully")

    # ==================== WAIT STRATEGIES ====================

    def wait_for_spinner(self, spinner_locator: Locator, timeout: int = 30000) -> None:
        """
        Wait for a loading spinner to disappear.
        
        Args:
            spinner_locator: Playwright locator for the spinner
            timeout: Timeout in milliseconds
        """
        try:
            spinner_locator.wait_for(state="hidden", timeout=timeout)
        except PlaywrightTimeoutError:
            pass

    def wait_for_ajax(self, timeout: int = 30000) -> None:
        """
        Wait for AJAX requests to complete using JavaScript.
        
        Args:
            timeout: Timeout in milliseconds
        """
        self.logger.info("Waiting for AJAX requests to complete")
        try:
            self.page.wait_for_function(
                "() => (typeof jQuery !== 'undefined') ? (jQuery.active === 0) : true",
                timeout=timeout
            )
            self.logger.info("AJAX requests completed")
        except Exception as e:
            self.logger.warning(f"AJAX wait failed: {e}, continuing anyway")

    
    def keyboard_click(self, locator: Locator, timeout: int = 10000) -> None:
        """
        Perform Ctrl+click on an element.
        Mirrors Selenium action chain: keyDown(CONTROL).click(element).keyUp(CONTROL).

        Args:
            locator: Playwright locator to click
            timeout: Timeout in milliseconds
        """
        try:
            locator.wait_for(state="visible", timeout=timeout)
            locator.click(modifiers=["Control"])
        except Exception as e:
            self.logger.warning(f"Keyboard click failed: {e}")
            raise

    def wait_and_click(self, locator: Locator, timeout: int = 10000, max_retries: int = 3) -> None:
        """
        Wait for element and click with retry logic.
        
        Args:
            locator: Playwright locator for the element
            timeout: Timeout per attempt in milliseconds
            max_retries: Maximum retry attempts
        """
        for attempt in range(max_retries):
            try:
                self._wait_for_dom_settled(timeout=min(timeout, 5000))
                locator.wait_for(state="visible", timeout=timeout)
                try:
                    locator.click(timeout=timeout)
                except Exception:
                    locator.click(timeout=min(timeout, 5000), force=True)
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Click attempt {attempt + 1} failed: {str(e).splitlines()[0]}, retrying...")
                    self.wait_for_timeout(1000)  # Wait 1 second before retry
                else:
                    self.logger.error(f"Click failed after {max_retries} attempts")
                    raise

    # ==================== VERIFICATION/ASSERTIONS ====================

    def is_element_visible(self, locator: Locator, max_wait_time: int = 10, poll_time: int = 1) -> bool:
        """
        Check whether an element becomes visible within the given time.

        Args:
            locator: Playwright locator for the element
            max_wait_time: Maximum wait time in seconds
            poll_time: Poll interval in seconds

        Returns:
            True if the element is visible, False otherwise
        """
        end_time = time.monotonic() + max_wait_time
        while time.monotonic() <= end_time:
            try:
                if locator.is_visible():
                    return True
            except Exception:
                pass
            time.sleep(poll_time)
        return False

    def wait_for_element_to_be_visible(self, locator: Locator, max_wait_time: int = 10, poll_time: int = 1) -> Optional[Locator]:
        """
        Wait for element to become visible with polling and return the locator.
        Mirrors Java waitForElementToBeVisible behavior.

        Args:
            locator: Playwright locator for the element
            max_wait_time: Maximum wait time in seconds
            poll_time: Poll interval in seconds

        Returns:
            Locator if element becomes visible, None if timeout
        """
        end_time = time.monotonic() + max_wait_time
        while time.monotonic() <= end_time:
            try:
                if locator.is_visible():
                    return locator
            except Exception as e:
                self.logger.debug(f"Element not visible yet: {e}")
            time.sleep(poll_time)
        
        self.logger.info(f"Exception: Element is not visible. Locator = {locator}, Timeout = {max_wait_time}s")
        return None

    def wait_for_element_to_be_invisible(self, locator: Locator, max_wait_time: int = 30, poll_time: int = 1) -> bool:
        """
        Wait for element to become invisible with polling.
        Mirrors Java waitForElementToBeInVisible behavior.

        Args:
            locator: Playwright locator for the element
            max_wait_time: Maximum wait time in seconds
            poll_time: Poll interval in seconds

        Returns:
            True if element becomes invisible, False if still visible after timeout
        """
        end_time = time.monotonic() + max_wait_time
        while time.monotonic() <= end_time:
            try:
                if not locator.is_visible():
                    return True
            except Exception:
                # If element not found, it's considered invisible
                return True
            time.sleep(poll_time)
        
        self.logger.info(f"Exception: Element is still visible. Locator = {locator}, Timeout = {max_wait_time}s")
        return False

    def wait_for_spinner_to_disappear(self, timeout: int = 30) -> None:
        """
        Wait for common loading indicators to disappear in page and iframe content.

        Args:
            timeout: Maximum wait time in seconds
        """
        spinner_selectors = [
            "#theLoadingImage",
            "div[class*='loading-indicator-component__spinner']",
            ".loading-indication-component.isVisible",
            "#chatspinnerid.amk-chat-custom-spinner svg[class*='rotate']",
        ]

        found_spinner = False

        for selector in spinner_selectors:
            page_spinner = self.page.locator(selector)
            try:
                if page_spinner.count() > 0:
                    found_spinner = True
                    page_spinner.first.wait_for(state="hidden", timeout=timeout * 1000)
            except Exception as e:
                self.logger.warning(
                    f"Spinner wait timed out for selector '{selector}' on page: {str(e).splitlines()[0]}"
                )

            try:
                iframe = self.page.locator("#iframeWrapper")
                if iframe.count() > 0:
                    iframe_spinner = self.page.frame_locator("#iframeWrapper").locator(selector)
                    if iframe_spinner.count() > 0:
                        found_spinner = True
                        iframe_spinner.first.wait_for(state="hidden", timeout=timeout * 1000)
            except Exception as e:
                self.logger.warning(
                    f"Spinner wait timed out for selector '{selector}' in iframe: {str(e).splitlines()[0]}"
                )

        if found_spinner:
            self.logger.info("Spinner disappeared")
        else:
            self.logger.info("Spinner not found")

    def baw_spinner_loader(self, appear_timeout: int = 10000, disappear_timeout: int = 60000) -> None:
        """Wait for BAW loading spinner (loading_msg.gif) to appear then disappear."""
        spinner = self.page.locator("img[src*='loading_msg.gif']")
        try:
            spinner.wait_for(state="visible", timeout=appear_timeout)
            self.logger.info("BAW loading spinner appeared")
        except Exception:
            self.logger.info("BAW loading spinner did not appear (may have already passed)")
        try:
            spinner.wait_for(state="hidden", timeout=disappear_timeout)
            self.logger.info("BAW loading spinner has disappeared")
        except Exception as e:
            self.logger.warning(f"BAW loading spinner did not disappear within {disappear_timeout}ms: {e}")

    # ==================== WINDOW/TAB MANAGEMENT ====================

    def get_all_pages(self) -> list:
        """
        Get all open pages/tabs in the browser context.
        
        Returns:
            List of all open pages
        """
        self.logger.info("Getting all open pages")
        context = self.page.context
        pages = context.pages
        self.logger.info(f"Found {len(pages)} open page(s)")
        return pages

    def switch_to_new_window(self, index: int = -1) -> Page:
        """
        Switch to a new window/tab by index.
        
        Args:
            index: Index of the page to switch to (-1 for last/newest)
            
        Returns:
            The new page object
        """
        self.logger.info(f"Switching to page at index {index}")
        pages = self.get_all_pages()
        
        if len(pages) <= 1:
            self.logger.warning("No other pages found")
            return self.page
        
        new_page = pages[index]
        self.page = new_page
        self.logger.info(f"Switched to page: {new_page.url}")
        return new_page

    # ==================== COMMON HELPER METHODS ====================

    def select_option_from_list(
        self, dropdown_locator: Locator, list_locator: Locator, option_value: str, log_message: str
    ) -> None:
        """
        Helper to select option from dropdown list.
        Common pattern used across multiple pages.
        
        Args:
            dropdown_locator: Locator for the dropdown trigger element
            list_locator: Locator for the list of options
            option_value: The text value to select
            log_message: Message to log on success
        """
        try:
            dropdown_locator.wait_for(state="visible", timeout=5000)
            dropdown_locator.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            dropdown_locator.click(force=True)
            self.logger.info(f"Clicked dropdown for: {log_message}")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            list_locator.first.wait_for(state="visible", timeout=25000)
            options = list_locator.all()
            self.logger.info(f"Found {len(options)} options in dropdown")
            for option in options:
                if option.text_content().strip() == option_value:
                    option.scroll_into_view_if_needed()
                    option.click()
                    self.logger.info(f"{log_message}: {option_value}")
                    return
            self.logger.warning(f"Option '{option_value}' not found. Available: {[o.text_content().strip() for o in options[:10]]}")
            if options:
                options[0].click()
                self.logger.warning(f"Selected first option as fallback: {options[0].text_content().strip()}")
        except Exception as e:
            self.logger.error(f"Failed to select option '{option_value}' from dropdown: {str(e).splitlines()[0]}")
            raise

    def wait_for_loading_data(self, timeout: int = 15000) -> None:
        """
        Wait for data loading indicators to complete.
        Common pattern for AJAX/dynamic content loading.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        try:
            self.page.wait_for_function(
                """() => {
                    const spinners = document.querySelectorAll('[class*="spinner"], [class*="loading"]');
                    return Array.from(spinners).every(s => !s.offsetParent);
                }""",
                timeout=timeout,
            )
        except Exception as e:
            self.logger.warning(f"Loading data wait timed out: {str(e).splitlines()[0]}")
            pass

    def wait_for_all_spinners_to_disappear(self, timeout: int = 30000) -> None:
        """
        Wait for all loading spinners to disappear from the page.
        More comprehensive wait that checks multiple spinner patterns.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        try:
            # Match Java logic: wait for each known spinner/indicator to become invisible
            spinner_locator = self.page.locator("//div[contains(@class,'loading-indicator-component__spinner')]")
            indicator_locator = self.page.locator(
                "//*[contains(@class, 'loading-indication-component') and contains(@class, 'isVisible')]"
            )

            spinner_count = spinner_locator.count()
            indicator_count = indicator_locator.count()

            for i in range(spinner_count):
                spinner_locator.nth(i).wait_for(state="hidden", timeout=timeout)

            for i in range(indicator_count):
                indicator_locator.nth(i).wait_for(state="hidden", timeout=timeout)

            self.logger.info("All spinners disappeared")
        except Exception as e:
            self.logger.warning(f"Spinner wait timed out: {str(e).splitlines()[0]}")



    def switch_window(self, page_handle) -> None:
        """
        Switch to a different page/window in the context.
        Playwright doesn't support window handles like Selenium, but can manage multiple pages.
        This method attempts to focus on the target page.

        Args:
            page_handle: The page object or context to switch to
        """
        try:
            if hasattr(page_handle, 'bring_to_front'):
                # If it's a Page object, bring it to front
                page_handle.bring_to_front()
                self.logger.info("Switched to page: brought to front")
            else:
                self.logger.warning(f"Cannot switch to page handle: {page_handle}")
        except Exception as e:
            self.logger.warning(f"Error switching windows: {e}")

    def switch_to_parent_window(self, child_context=None) -> None:
        """Close a child browser context and switch focus back to this page.

        Args:
            child_context: Optional BrowserContext to close before switching.
                           If None, only brings the current page to the foreground.
        """
        if child_context:
            child_context.close()
            self.logger.info("Child browser context closed")
        self.page.bring_to_front()
        self.logger.info(f"Switched back to parent window. URL: {self.page.url}")

    def switch_to_page_by_title(self, page_title: str, timeout: int = 30) -> Page:
        """
        Find and switch to a page matching the given title.
        Mirrors Java switchTab implementation.

        Args:
            page_title: Expected target page title fragment
            timeout: Maximum time in seconds to wait for the page

        Returns:
            The target Playwright Page

        Raises:
            ValueError: If target page cannot be found
        """
        expected_title = page_title.lower()
        timeout_at = time.monotonic() + timeout

        while time.monotonic() < timeout_at:
            for candidate_page in self.page.context.pages:
                try:
                    candidate_page.wait_for_load_state("domcontentloaded", timeout=2000)
                except PlaywrightTimeoutError:
                    pass
                except Exception:
                    pass

                candidate_title = (candidate_page.title() or "").strip()
                if expected_title in candidate_title.lower():
                    candidate_page.bring_to_front()
                    self.logger.info(f"Switched to tab: {candidate_title}")
                    return candidate_page

            self.wait_for_timeout(1000)

        raise ValueError(
            f"Expected page '{page_title}' is not opened. Current title: {(self.page.title() or '').strip()}"
        )

    def accept_alert(self) -> None:
        """Register a one-time listener that automatically accepts the next JavaScript alert/confirm/prompt dialog."""

        def _accept(dialog):
            self.logger.info(f"Alert accepted: {dialog.message}")
            dialog.accept()

        self.page.once("dialog", _accept)

    def not_saved_error_locator(self) -> Locator:
        """Common locator for the unsaved-information banner."""
        return self.active_root().locator(
            ".error-text",
            has_text="The information above has NOT been saved",
        ).first

    def notSavedError(self, timeout: int = 5000) -> None:
        """Fail when the common unsaved-information banner is displayed."""
        error_banner = self.not_saved_error_locator()
        try:
            error_banner.wait_for(state="visible", timeout=timeout)
        except Exception:
            return
        msg = (error_banner.text_content() or "The information above has NOT been saved.").strip()
        self.logger.error(msg)
        raise AssertionError(msg)

    # ------------------------------------------------------------------
    # Base branch methods (auto-healing wrappers)
    # ------------------------------------------------------------------

    def check(self, locator: Locator, timeout: int = 10000) -> None:
        """Check a checkbox (no-op if already checked) with auto-healing."""
        self.logger.info("Checking checkbox (auto-healing)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.check()

        self._heal_and_retry(locator, _action)

    def uncheck(self, locator: Locator, timeout: int = 10000) -> None:
        """Uncheck a checkbox (no-op if already unchecked) with auto-healing."""
        self.logger.info("Unchecking checkbox (auto-healing)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.uncheck()

        self._heal_and_retry(locator, _action)

    def select_option(
        self,
        locator: Locator,
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        timeout: int = 10000,
    ) -> list[str]:
        """Select an option from a <select> dropdown with auto-healing.

        Provide exactly one of value, label, or index.
        Returns list of selected option values.
        """
        self.logger.info("Selecting option from dropdown")

        def _action(loc: Locator) -> list[str]:
            loc.wait_for(state="visible", timeout=timeout)
            if value is not None:
                return loc.select_option(value=value)
            elif label is not None:
                return loc.select_option(label=label)
            elif index is not None:
                return loc.select_option(index=index)
            raise ValueError("Provide one of: value, label, or index")

        return self._heal_and_retry(locator, _action)

    def scroll_into_view(self, locator: Locator, timeout: int = 10000) -> None:
        """Scroll the page until the element is visible in the viewport."""
        self.logger.info("Scrolling element into view")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="attached", timeout=timeout)
            loc.scroll_into_view_if_needed()

        self._heal_and_retry(locator, _action)

    def focus(self, locator: Locator, timeout: int = 10000) -> None:
        """Set focus on an element with auto-healing."""
        self.logger.info("Focusing element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.focus()

        self._heal_and_retry(locator, _action)

    def upload_file(
        self,
        file_path: str | list[str],
        locator: Optional[Locator] = None,
        trigger_locator: Optional[Locator] = None,
        timeout: int = 10000,
    ) -> None:
        """Upload file(s) via a file input or a file chooser dialog.

        Option A ΓÇô direct input: pass *locator* pointing to an ``<input type="file">``
        element. Uses ``set_input_files`` directly (works even when the input is hidden).

        Option B ΓÇô file chooser dialog: pass *trigger_locator* (the button/link that
        opens the OS file picker). The method listens for the ``filechooser`` event
        and calls ``set_files`` on the dialog.

        Provide exactly one of *locator* or *trigger_locator*.
        """
        paths = file_path if isinstance(file_path, list) else [file_path]
        self.logger.info(f"Uploading file(s): {paths}")

        if locator:
            def _action(loc: Locator) -> None:
                loc.wait_for(state="attached", timeout=timeout)
                loc.set_input_files(paths)

            self._heal_and_retry(locator, _action)

        elif trigger_locator:
            def _action(loc: Locator) -> None:
                with self.page.expect_file_chooser(timeout=timeout) as fc_info:
                    loc.click()
                file_chooser = fc_info.value
                file_chooser.set_files(paths)

            self._heal_and_retry(trigger_locator, _action)

        else:
            raise ValueError("Provide one of: locator (file input) or trigger_locator (button that opens picker)")

    # ------------------------------------------------------------------
    # Keyboard methods (from base branch)
    # ------------------------------------------------------------------

    def press_key(self, key: str, locator: Optional[Locator] = None, timeout: int = 10000) -> None:
        """Press a keyboard key (Enter, Escape, Tab, ArrowDown, etc.).

        If a locator is provided, the key press is scoped to that element with auto-healing.
        Otherwise, it fires on the page level.
        """
        self.logger.info(f"Pressing key: {key}")
        if locator:
            def _action(loc: Locator) -> None:
                loc.wait_for(state="visible", timeout=timeout)
                loc.press(key)

            self._heal_and_retry(locator, _action)
        else:
            self.page.keyboard.press(key)

    def type_text(self, locator: Locator, text: str, delay: int = 50, timeout: int = 10000) -> None:
        """Type text character-by-character into an element.

        Useful for inputs that rely on keydown/keyup events and don't work with fill().
        """
        self.logger.info("Typing text character-by-character")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()
            loc.press_sequentially(text, delay=delay)

        self._heal_and_retry(locator, _action)

    def keyboard_shortcut(self, keys: str) -> None:
        """Execute a keyboard shortcut (e.g., 'Control+a', 'Control+c', 'Meta+v').

        Uses Playwright's keyboard.press which accepts modifier+key combos.
        """
        self.logger.info(f"Keyboard shortcut: {keys}")
        self.page.keyboard.press(keys)

    # ------------------------------------------------------------------
    # Mouse methods (from base branch)
    # ------------------------------------------------------------------

    def double_click(self, locator: Locator, timeout: int = 10000) -> None:
        """Double-click an element with auto-healing."""
        self.logger.info("Double-clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.dblclick()

        self._heal_and_retry(locator, _action)

    def right_click(self, locator: Locator, timeout: int = 10000) -> None:
        """Right-click (context menu) an element with auto-healing."""
        self.logger.info("Right-clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click(button="right")

        self._heal_and_retry(locator, _action)

    def hover(self, locator: Locator, timeout: int = 10000) -> None:
        """Hover over an element with auto-healing."""
        self.logger.info("Hovering over element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.hover()

        self._heal_and_retry(locator, _action)

    def drag_and_drop(
        self, source: Locator, target: Locator, timeout: int = 10000
    ) -> None:
        """Drag source element and drop onto target element with auto-healing."""
        self.logger.info("Drag and drop")

        def _action(src: Locator) -> None:
            src.wait_for(state="visible", timeout=timeout)
            target.wait_for(state="visible", timeout=timeout)
            src.drag_to(target)

        self._heal_and_retry(source, _action)

    # ------------------------------------------------------------------
    # Download handling (from base branch)
    # ------------------------------------------------------------------

    def download_file(
        self,
        trigger_locator: Locator,
        save_path: Optional[str] = None,
        filename: Optional[str] = None,
        timeout: int = 30000,
    ) -> Download:
        """Click a link/button that triggers a download and return the Download object.

        Files are saved to the configured download directory by default (cleaned at session start).
        Pass *save_path* to override the full destination, or *filename* to override
        just the file name within the default downloads folder.

        Args:
            trigger_locator: Element that initiates the download.
            save_path: Optional full path to save the file (takes priority over *filename*).
            filename: Optional custom file name (used inside the configured download dir).
                      Defaults to the browser-suggested filename.
            timeout: Max wait for the download to start.

        Returns:
            Playwright Download object (has .path(), .suggested_filename, .url, etc.).
        """
        self.logger.info("Waiting for download...")

        with self.page.expect_download(timeout=timeout) as dl_info:
            trigger_locator.click()

        download = dl_info.value
        self.logger.info(f"Download started: {download.suggested_filename}")

        name = filename or download.suggested_filename
        from utils.download_utils import _DEFAULT_DOWNLOAD_DIR
        dest = save_path or f"{_DEFAULT_DOWNLOAD_DIR}/{name}"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        download.save_as(dest)
        self.logger.info(f"Download saved to: {dest}")

        return download

    # ------------------------------------------------------------------
    # Iframe support (from base branch)
    # ------------------------------------------------------------------

    def get_frame(self, selector: str) -> FrameLocator:
        """Get a FrameLocator for interacting with elements inside an iframe.

        Args:
            selector: CSS selector or iframe name/id.
                      e.g. "iframe#content", "iframe[name='main']", "#myFrame"

        Returns:
            FrameLocator that can chain .locator() calls inside the iframe.

        Usage::

            frame = self.get_frame("iframe#content")
            frame.locator("#submit").click()
        """
        self.logger.info(f"Accessing iframe: {selector}")
        return self.page.frame_locator(selector)

    # ------------------------------------------------------------------
    # Page-ready / resilient-click utilities
    # ------------------------------------------------------------------

    def _wait_for_page_ready(self, timeout: int = 30000) -> None:
        """Common wait pattern for page being ready"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            pass
        self.wait_for_loading_data()

    def _click_button_with_fallback(self, primary_locator: Locator, fallback_selectors: List[str],
                                     button_name: str, timeout: int = 10000) -> None:
        """Click button with fallback selectors if primary fails"""
        # Try primary locator
        try:
            if primary_locator.count() > 0 and primary_locator.first.is_visible(timeout=timeout):
                primary_locator.first.scroll_into_view_if_needed()
                primary_locator.first.click()
                logger.info(f"Clicked {button_name} with primary selector")
                return
        except Exception as e:
            logger.warning(f"{button_name} primary selector failed: {str(e)[:100]}")

        # Try fallback selectors
        root = self.active_root()
        for selector in fallback_selectors:
            try:
                btn = root.locator(selector).first
                if btn.count() > 0 and btn.is_visible(timeout=2000):
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    logger.info(f"Clicked {button_name} with fallback: {selector}")
                    return
            except Exception:
                continue

        raise RuntimeError(f"{button_name} not found with any selector")

    def _click_element_with_strategies(self, locator: Locator, name: str, timeout: int = 10000) -> None:
        """Try normal click, then force click, then JS click on the same element."""
        try:
            locator.scroll_into_view_if_needed()
            locator.click(timeout=timeout)
            logger.info(f"Clicked {name}")
            return
        except Exception as e:
            logger.warning(f"{name} normal click failed: {str(e)[:100]}")
        try:
            locator.click(force=True, timeout=timeout)
            logger.info(f"Clicked {name} via force click")
            return
        except Exception as e:
            logger.warning(f"{name} force click failed: {str(e)[:100]}")
        locator.evaluate("el => el.click()")
        logger.info(f"Clicked {name} via JS click")

    def _navigate_to_page(self, button_locator: Locator, page_name: str,
                          fallback_selectors: Optional[List[str]] = None) -> None:
        """Generic navigation to next page by clicking button"""
        # Wait for any in-progress navigation to finish before clicking
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        self._wait_for_page_ready()

        if fallback_selectors:
            self._click_button_with_fallback(button_locator, fallback_selectors, page_name)
        else:
            button_locator.wait_for(state="visible", timeout=10000)
            try:
                button_locator.click(timeout=15000)
            except Exception:
                logger.warning(f"{page_name} normal click timed out, trying no_wait_after")
                button_locator.click(no_wait_after=True, timeout=10000)
            logger.info(f"Clicked {page_name} button")

        self._wait_for_page_ready()
