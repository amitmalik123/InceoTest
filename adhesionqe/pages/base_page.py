# pages/base_page.py

"""
Base Page class with common functionality for all page objects
"""

import logging
import re
from typing import Any, Callable, Literal, Optional

import allure
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common functionality like navigation, waits, and assertions.
    """

    _healing_engine: Optional[AutoHealingEngine] = None  # Shared across all page objects

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
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
        """Navigate to a specific URL"""
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    # dynamic wait method(condition based)
    def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: int = 30000,
    ) -> None:
        """Wait for page to reach specified load state"""
        self.logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    # static wait method
    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a specific amount of time"""
        self.page.wait_for_timeout(milliseconds)

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
            self.logger.info("🔧 Auto-healing: Trying alternative strategies...")

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

    # ------------------------------------------------------------------
    # Element interaction methods (all delegate to _heal_and_retry)
    # ------------------------------------------------------------------

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        """Click an element with wait and logging - includes auto-healing."""
        self.logger.info("Clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()

        self._heal_and_retry(locator, _action)

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        """Fill a text field with wait and logging - includes auto-healing."""
        self.logger.info("Filling field with text")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.fill(text)

        self._heal_and_retry(locator, _action)

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        """Get text content from an element with auto-healing."""

        def _action(loc: Locator) -> str:
            loc.wait_for(state="visible", timeout=timeout)
            return loc.text_content() or ""

        return self._heal_and_retry(locator, _action)

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
        """Wait for element to reach specified state with auto-healing."""
        self.logger.info(f"Waiting for element to be {state}")

        def _action(loc: Locator) -> None:
            loc.wait_for(state=state, timeout=timeout)

        self._heal_and_retry(locator, _action)

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
