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
        self.page = page
        self.enable_healing = enable_healing
        self.healing_engine = AutoHealingEngine() if enable_healing else None

    def navigate(self, url: str):
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)

    def find_element(
        self, selector: str, heal: bool = True, timeout: int = 5000
    ) -> Optional[Locator]:
        try:
            locator = self.page.locator(selector)
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except Exception:
            logger.debug(f"Element not found with original selector: {selector}")

            if heal and self.enable_healing and self.healing_engine is not None:
                healed_locator, was_healed = self.healing_engine.find_element(self.page, selector)
                if healed_locator:
                    logger.info("Element healed successfully")
                    return healed_locator

            logger.error(f"Failed to find element: {selector}")
            return None

    def click(self, selector: str, timeout: Optional[int] = None, heal: bool = True):
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
        logger.info(f"Filling {selector} with: {value}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.fill(value)
        else:
            raise Exception(f"Cannot fill element: {selector}")

    def get_text(self, selector: str, heal: bool = True) -> str:
        locator = self.find_element(selector, heal=heal)

        if locator:
            return locator.text_content() or ""
        return ""

    def is_visible(self, selector: str, timeout: int = 5000, heal: bool = True) -> bool:
        locator = self.find_element(selector, heal=heal, timeout=timeout)
        return locator is not None

    def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None,
        heal: bool = True,
    ):
        logger.info(f"Waiting for {selector} to be {state}")
        locator = self.find_element(selector, heal=heal, timeout=timeout or 30000)

        if locator:
            locator.wait_for(state=state, timeout=timeout)
        else:
            raise Exception(f"Element not found: {selector}")

    def select_dropdown_option(self, selector: str, value: str, heal: bool = True):
        logger.info(f"Selecting {value} from dropdown {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.select_option(value)
        else:
            raise Exception(f"Cannot select from dropdown: {selector}")  # nosec B608

    def check_checkbox(self, selector: str, heal: bool = True):
        logger.info(f"Checking checkbox: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.check()
        else:
            raise Exception(f"Cannot check checkbox: {selector}")

    def uncheck_checkbox(self, selector: str, heal: bool = True):
        logger.info(f"Unchecking checkbox: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.uncheck()
        else:
            raise Exception(f"Cannot uncheck checkbox: {selector}")

    def hover(self, selector: str, heal: bool = True):
        logger.info(f"Hovering over: {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.hover()
        else:
            raise Exception(f"Cannot hover over element: {selector}")

    def get_attribute(self, selector: str, attribute: str, heal: bool = True) -> Optional[str]:
        locator = self.find_element(selector, heal=heal)

        if locator:
            return locator.get_attribute(attribute)
        return None

    def press_key(self, selector: str, key: str, heal: bool = True):
        logger.info(f"Pressing {key} on {selector}")
        locator = self.find_element(selector, heal=heal)

        if locator:
            locator.press(key)
        else:
            raise Exception(f"Cannot press key on element: {selector}")

    def get_healing_stats(self) -> dict:
        if self.healing_engine:
            return self.healing_engine.get_stats()
        return {}

    def reset_healing_stats(self):
        if self.healing_engine:
            self.healing_engine.reset_stats()

    def disable_healing(self):
        self.enable_healing = False
        logger.info("Auto-healing disabled")

    def enable_healing_feature(self):
        self.enable_healing = True
        if not self.healing_engine:
            self.healing_engine = AutoHealingEngine()
        logger.info("Auto-healing enabled")
