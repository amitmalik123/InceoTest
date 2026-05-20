"""
Base Page class with common functionality for all page objects.
"""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page


logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects."""

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = base_url or ""
        self.logger = logging.getLogger(self.__class__.__name__)

    def navigate_to(self, url: str, wait_until: str = "load") -> None:
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)

    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000) -> None:
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
        locator.wait_for(state=state, timeout=timeout)

    def screenshot(self, name: str) -> bytes:
        return self.page.screenshot()

    def get_current_url(self) -> str:
        return self.page.url

    def go_back(self) -> None:
        self.page.go_back()

    def refresh(self) -> None:
        self.page.reload()

    def resolve_locator(self, locator_def: dict) -> Locator:
        """Resolve a locator definition (dict) into a Playwright Locator.

        Supported keys:
        - 'role' + optional 'name' or 'label'
        - 'css'    : CSS selector string
        - 'text'   : text to search with get_by_text
        - 'testid' : data-testid attribute
        """
        if not isinstance(locator_def, dict):
            raise ValueError("locator_def must be a dict")

        if 'role' in locator_def:
            role = locator_def['role']
            name = locator_def.get('name') or locator_def.get('label')
            if name:
                return self.page.get_by_role(role, name=name)
            return self.page.get_by_role(role)

        if 'text' in locator_def:
            return self.page.get_by_text(locator_def['text'])

        if 'testid' in locator_def:
            return self.page.locator(f"[data-testid=\"{locator_def['testid']}\"]")

        if 'css' in locator_def:
            return self.page.locator(locator_def['css'])

        raise ValueError(f"Unsupported locator definition: {locator_def}")
