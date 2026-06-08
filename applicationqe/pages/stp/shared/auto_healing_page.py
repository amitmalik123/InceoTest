"""
Auto-Healing Base Page - Enhanced page object with self-healing capabilities
"""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class AutoHealingPage:
    """
    Enhanced base page with auto-healing capabilities.

    This page automatically attempts to heal broken locators using multiple strategies.
    """

    def __init__(self, page: Page, enable_healing: bool = True):
        """
        Initialize auto-healing page.

        Args:
            page: Playwright page object
            enable_healing: Enable auto-healing features
        """
        self.page = page
        self.enable_healing = enable_healing
        self.healing_engine = AutoHealingEngine() if enable_healing else None

    def navigate(self, url: str):
        """Navigate to URL"""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)

    def find_element(
        self, selector: str, heal: bool = True, timeout: int = 5000
    ) -> Optional[Locator]:
        """
        Find element with optional auto-healing.

        Args:
            selector: Element selector
            heal: Enable healing if element not found
            timeout: Timeout in milliseconds

        Returns:
            Locator if found, None otherwise
        """
        try:
            locator = self.page.locator(selector)
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except Exception:
            logger.debug(f"Element not found with original selector: {selector}")

            if heal and self.enable_healing:
                healed_locator, was_healed = self.healing_engine.find_element(self.page, selector)
                if healed_locator:
                    logger.info(f"Element healed successfully")
                    return healed_locator

            logger.error(f"Failed to find element: {selector}")
            return None

    def click(self, selector: str, timeout: Optional[int] = None, heal: bool = True):
        """
        Click element with auto-healing.

        Args:
            selector: Element selector
            timeout: Optional timeout
            heal: Enable healing
        """
        logger.info(f"Clicking: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            if timeout:
                locator.click(timeout=timeout)
            else:
                locator.click()
        else:
            raise Exception(f"Cannot click element: {selector}")

    def fill(self, selector: str, value: str, heal: bool = True):
        """
        Fill input field with auto-healing.

        Args:
            selector: Element selector
            value: Value to fill
            heal: Enable healing
        """
        logger.info(f"Filling {selector} with: {value}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.fill(value)
        else:
            raise Exception(f"Cannot fill element: {selector}")

    def get_text(self, selector: str, heal: bool = True) -> str:
        """
        Get text content with auto-healing.

        Args:
            selector: Element selector
            heal: Enable healing

        Returns:
            Text content or empty string
        """
        locator = self.find_element(selector, heal=heal)

        if locator:
            return locator.text_content() or ""
        return ""

    def is_visible(self, selector: str, timeout: int = 5000, heal: bool = True) -> bool:
        """
        Check if element is visible with auto-healing.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            heal: Enable healing

        Returns:
            True if visible, False otherwise
        """
        locator = self.find_element(selector, heal=heal, timeout=timeout)
        return locator is not None

    def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None,
        heal: bool = True,
    ):
        """
        Wait for element with auto-healing.

        Args:
            selector: Element selector
            state: Element state to wait for
            timeout: Optional timeout
            heal: Enable healing
        """
        logger.info(f"Waiting for {selector} to be {state}")
        locator = self.find_element(selector, heal=heal, timeout=timeout or 30000)

        if locator:
            locator.wait_for(state=state, timeout=timeout)
        else:
            raise Exception(f"Element not found: {selector}")

    def select_dropdown_option(self, selector: str, value: str, heal: bool = True):
        """
        Select dropdown option with auto-healing.

        Args:
            selector: Dropdown selector
            value: Option value
            heal: Enable healing
        """
        logger.info(f"Selecting {value} from dropdown {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.select_option(value)
        else:
            raise Exception(f"Cannot select from dropdown: {selector}")

    def check_checkbox(self, selector: str, heal: bool = True):
        """Check checkbox with auto-healing"""
        logger.info(f"Checking checkbox: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.check()
        else:
            raise Exception(f"Cannot check checkbox: {selector}")

    def uncheck_checkbox(self, selector: str, heal: bool = True):
        """Uncheck checkbox with auto-healing"""
        logger.info(f"Unchecking checkbox: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.uncheck()
        else:
            raise Exception(f"Cannot uncheck checkbox: {selector}")

    def hover(self, selector: str, heal: bool = True):
        """Hover over element with auto-healing"""
        logger.info(f"Hovering over: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.hover()
        else:
            raise Exception(f"Cannot hover over element: {selector}")

    def get_attribute(self, selector: str, attribute: str, heal: bool = True) -> Optional[str]:
        """
        Get element attribute with auto-healing.

        Args:
            selector: Element selector
            attribute: Attribute name
            heal: Enable healing

        Returns:
            Attribute value or None
        """
        locator = self.find_element(selector, heal=heal)

        if locator:
            return locator.get_attribute(attribute)
        return None

    def press_key(self, selector: str, key: str, heal: bool = True):
        """
        Press key on element with auto-healing.

        Args:
            selector: Element selector
            key: Key to press
            heal: Enable healing
        """
        logger.info(f"Pressing {key} on {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.press(key)
        else:
            raise Exception(f"Cannot press key on element: {selector}")

    def get_healing_stats(self) -> dict:
        """
        Get auto-healing statistics.

        Returns:
            Dictionary with healing stats
        """
        if self.healing_engine:
            return self.healing_engine.get_stats()
        return {}

    def reset_healing_stats(self):
        """Reset healing statistics"""
        if self.healing_engine:
            self.healing_engine.reset_stats()

    def disable_healing(self):
        """Temporarily disable auto-healing"""
        self.enable_healing = False
        logger.info("Auto-healing disabled")

    def enable_healing_feature(self):
        """Re-enable auto-healing"""
        self.enable_healing = True
        if not self.healing_engine:
            self.healing_engine = AutoHealingEngine()
        logger.info("Auto-healing enabled")
