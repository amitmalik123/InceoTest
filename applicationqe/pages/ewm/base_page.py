# pages/base_page.py

"""
Base Page class with common functionality for all page objects
"""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page, expect

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common functionality like navigation, waits, and assertions.
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = base_url or ""
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate_to(self, url: str, wait_until: str = "load") -> None:
        """Navigate to a specific URL"""
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000) -> None:
        """Wait for page to reach specified load state"""
        self.logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a specific amount of time"""
        self.page.wait_for_timeout(milliseconds)

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        """Click an element with wait and logging"""
        self.logger.info(f"Clicking element")
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        """Fill a text field with wait and logging"""
        self.logger.info(f"Filling field with text")
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(text)

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        """Get text content from an element"""
        locator.wait_for(state="visible", timeout=timeout)
        return locator.text_content() or ""

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        """Check if element is visible"""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator: Locator, state: str = "visible", timeout: int = 10000) -> None:
        """Wait for element to reach specified state"""
        self.logger.info(f"Waiting for element to be {state}")
        locator.wait_for(state=state, timeout=timeout)

    def screenshot(self, name: str) -> bytes:
        """Take a screenshot and return bytes"""
        self.logger.info(f"Taking screenshot: {name}")
        return self.page.screenshot()

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

