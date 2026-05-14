# pages/base_page.py

"""
Base Page class with common functionality for all page objects
"""

import logging
from typing import Literal, Optional, Union

import allure
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, FrameLocator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common functionality like navigation, waits, and assertions.
    
    Supports both Page and FrameLocator contexts:
    - Page: for regular scenarios (existing 9 scenarios)
    - FrameLocator: for iframe scenarios (new manage_bene scenario)
    """

    _healing_engine: Optional[AutoHealingEngine] = None  # Shared across all page objects

    def __init__(self, context: Union[Page, FrameLocator], base_url: Optional[str] = None):
        self.context = context
        self.page = context if isinstance(context, Page) else None
        self.base_url = base_url or ""
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize healing engine once
        if BasePage._healing_engine is None:
            BasePage._healing_engine = AutoHealingEngine("locator_mappings.json")
            self.logger.info("Auto-healing engine initialized")

    def navigate_to(
        self,
        url: str,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
    ) -> None:
        """Navigate to a specific URL (Page context only)"""
        if not self.page:
            self.logger.warning("navigate_to called on FrameLocator context - skipping")
            return
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def dismiss_cookie_banner(self) -> None:
        """Dismiss the OneTrust privacy consent banner if present."""
        if not self.page:
            return
        try:
            accept_btn = self.page.locator("button.save-preference-btn-handler")
            accept_btn.wait_for(state="visible", timeout=8000)
            accept_btn.click()
            self.page.locator(".onetrust-pc-dark-filter").wait_for(state="hidden", timeout=8000)
            self.logger.info("Cookie consent banner dismissed")
        except Exception:
            pass  # Banner not present or button not found

        # Fallback: force-hide via JS if the dark filter overlay is still blocking
        try:
            dark_filter = self.page.locator(".onetrust-pc-dark-filter")
            if dark_filter.count() > 0 and dark_filter.is_visible():
                self.page.evaluate(
                    """() => {
                        const el = document.querySelector('.onetrust-pc-dark-filter');
                        if (el) el.style.display = 'none';
                        const sdk = document.getElementById('onetrust-consent-sdk');
                        if (sdk) sdk.style.display = 'none';
                    }"""
                )
                self.logger.info("OneTrust overlay force-hidden via JS")
        except Exception:
            pass

        # Ketch privacy banner — click "Accept All" if present
        try:
            ketch_btn = self.page.locator("#ketch-banner-button-primary")
            if ketch_btn.count() > 0:
                ketch_btn.wait_for(state="visible", timeout=5000)
                ketch_btn.click()
                self.page.locator("#ketch-consent-banner").wait_for(state="hidden", timeout=5000)
                self.logger.info("Ketch privacy banner dismissed")
        except Exception:
            pass

    # dynamic wait method(condition based)
    def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: int = 30000,
    ) -> None:
        """Wait for page to reach specified load state (Page context only)"""
        if not self.page:
            self.logger.warning("wait_for_load_state called on FrameLocator context - skipping")
            return
        self.logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    # static wait method
    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a specific amount of time"""
        if not self.page:
            self.logger.warning("wait_for_timeout called on FrameLocator context - skipping")
            return
        self.page.wait_for_timeout(milliseconds)

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        """Click an element with wait and logging - includes auto-healing"""
        self.logger.info("Clicking element")
        try:
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"Click failed with original locator: {e}")
            self.logger.info("🔧 Auto-healing: Trying alternative strategies...")

            # Extract the name/text from original get_by_role locator
            selector_str = str(locator)

            # Strategy 1: Try get_by_text with extracted name (works for both Page and FrameLocator)
            if "name=" in selector_str:
                import re

                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    self.logger.info(f"Trying text-based healing with: '{text}'")
                    healed = self.context.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Auto-healing SUCCESS - Found by text '{text}'")
                        healed.click()
                        return

            # Strategy 2: Use AutoHealingEngine (Page context only)
            if self.page and self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Auto-healing SUCCESS using healing engine!")
                    healed_locator.wait_for(state="visible", timeout=timeout)
                    healed_locator.click()
                    return

            self.logger.error("Auto-healing FAILED - element not found")
            raise

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        """Fill a text field with wait and logging - includes auto-healing"""
        self.logger.info("Filling field with text")
        try:
            locator.wait_for(state="visible", timeout=timeout)
            locator.fill(text)
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"Fill failed with original locator: {e}")
            self.logger.info("Attempting auto-healing...")

            selector_str = str(locator)
            # Use AutoHealingEngine (Page context only)
            if self.page and self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )

                if healed_locator:
                    self.logger.info("Auto-healing successful! Filling healed element...")
                    healed_locator.wait_for(state="visible", timeout=timeout)
                    healed_locator.fill(text)
                    return

            self.logger.error("Auto-healing failed - element not found")
            raise

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        """Get text content from an element with auto-healing"""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return locator.text_content() or ""
        except (PlaywrightError, PlaywrightTimeoutError, Exception) as e:
            self.logger.warning(f"get_text failed with original locator: {e}")
            self.logger.info("🔧 Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Try text-based healing (works for both Page and FrameLocator)
            if "name=" in selector_str:
                import re

                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    healed = self.context.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Auto-healing SUCCESS - Found by text '{text}'")
                        return healed.text_content() or ""

            # Use AutoHealingEngine (Page context only)
            if self.page and self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Auto-healing SUCCESS using healing engine!")
                    return healed_locator.text_content() or ""

            self.logger.error("Auto-healing FAILED - element not found")
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
            self.logger.warning(f"wait_for_element failed with original locator: {e}")
            self.logger.info("Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Try text-based healing
            if "name=" in selector_str:
                import re

                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Auto-healing SUCCESS - Found by text '{text}'")
                        healed.wait_for(state=state, timeout=timeout)
                        return

            # Use AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, was_healed = self._healing_engine.find_element(
                    self.page, selector_str
                )
                if healed_locator:
                    self.logger.info("Auto-healing SUCCESS using healing engine!")
                    healed_locator.wait_for(state=state, timeout=timeout)
                    return

            self.logger.error("Auto-healing FAILED - element not found")
            raise

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

    def empty_field(self, locator: Locator, timeout: int = 30000) -> None:
        """
        Clear a field by clicking and filling with empty string.
        Useful for input fields that need explicit clearing.

        Args:
            locator: Playwright locator for the field to clear
            timeout: Timeout in milliseconds for the click action (default 30000ms)
        """
        self.logger.info("Clearing field")
        locator.click(timeout=timeout)
        locator.fill("")
