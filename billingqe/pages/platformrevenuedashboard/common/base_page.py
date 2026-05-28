"""Shared base page object utilities for Billing Platform Revenue Dashboard."""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page


logger = logging.getLogger(__name__)


class BasePage:
    """Base class for page objects with common browser helpers."""

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = base_url or ""
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate_to(self, url: str, wait_until: str = "load") -> None:
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000) -> None:
        self.logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    def wait_for_timeout(self, milliseconds: int) -> None:
        self.page.wait_for_timeout(milliseconds)

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(text)

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        locator.wait_for(state="visible", timeout=timeout)
        return locator.text_content() or ""

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator: Locator, state: str = "visible", timeout: int = 10000) -> None:
        self.logger.info(f"Waiting for element to be {state}")
        locator.wait_for(state=state, timeout=timeout)

    def screenshot(self, name: str) -> bytes:
        self.logger.info(f"Taking screenshot: {name}")
        return self.page.screenshot()

    def get_current_url(self) -> str:
        return self.page.url

    def go_back(self) -> None:
        self.logger.info("Navigating back")
        self.page.go_back()

    def refresh(self) -> None:
        self.logger.info("Refreshing page")
        self.page.reload()
