"""Wrappermodel-local BasePage shim.

This file exists so wrappermodel page objects can resolve `pages.base_page`
without importing the shared STP-oriented base page module.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Callable, Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class BasePage:
    """Minimal page-object base class for wrappermodel tests."""

    _healing_engine: Optional[AutoHealingEngine] = None

    def __init__(self, page: Page, base_url: Optional[str] = None, home_url: Optional[str] = None):
        self.page = page
        self.context = page
        self.base_url = base_url or home_url or ""
        self.home_url = self.base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.promo_chat_close_icon: Locator = page.locator("#promoChatCloseIcon > g > path")
        self.chat_close_icon: Locator = page.locator("button#xBtnSvg path[fill='black']")

        if BasePage._healing_engine is None:
            BasePage._healing_engine = AutoHealingEngine("locator_mappings.json")
            self.logger.info("Auto-healing engine initialized")

        try:
            page.add_init_script(
                """
                (function setupKetchObserver() {
                    function tryAccept() {
                        const root = document.querySelector('#lanyard_root');
                        if (!root) return false;
                        const shadow = root.shadowRoot;
                        const buttons = shadow
                            ? shadow.querySelectorAll('button')
                            : root.querySelectorAll('button');
                        for (const btn of buttons) {
                            if ((btn.textContent || '').trim().includes('Accept All')) {
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
                """
            )
        except Exception:
            logger.debug("Unable to install wrappermodel init script")

    def _heal_and_retry(self, locator: Locator, action_fn: Callable[[Locator], Any]) -> Any:
        try:
            return action_fn(locator)
        except (PlaywrightError, PlaywrightTimeoutError, Exception):
            selector_str = str(locator)
            if self._healing_engine is not None:
                healed_locator, _ = self._healing_engine.find_element(self.page, selector_str)
                if healed_locator:
                    return action_fn(healed_locator)
            raise

    def click(self, locator: Locator, timeout: int = 10000, force: bool = False) -> None:
        self._heal_and_retry(locator, lambda loc: loc.click(timeout=timeout, force=force))

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.fill(text, timeout=timeout))

    def type(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.type(text, timeout=timeout))

    def press(self, locator: Locator, key: str, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.press(key, timeout=timeout))

    def hover(self, locator: Locator, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.hover(timeout=timeout))

    def check(self, locator: Locator, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.check(timeout=timeout))

    def uncheck(self, locator: Locator, timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.uncheck(timeout=timeout))

    def select_option(self, locator: Locator, value: str | None = None, label: str | None = None) -> None:
        options: dict[str, str] = {}
        if value is not None:
            options["value"] = value
        if label is not None:
            options["label"] = label
        self._heal_and_retry(locator, lambda loc: loc.select_option(**options))

    def wait_for(self, locator: Locator, state: str = "visible", timeout: int = 10000) -> None:
        self._heal_and_retry(locator, lambda loc: loc.wait_for(state=state, timeout=timeout))

    def wait_for_timeout(self, timeout: int) -> None:
        self.page.wait_for_timeout(timeout)

    def wait_for_load_state(self, state: str = "load", timeout: int = 10000) -> None:
        self.page.wait_for_load_state(state=state, timeout=timeout)

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        return self.page.wait_for_selector(selector, timeout=timeout)

    def goto(self, url: str, wait_until: str = "load", timeout: int = 10000) -> None:
        self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def text_content(self, locator: Locator, timeout: int = 10000) -> str:
        value = self._heal_and_retry(locator, lambda loc: loc.text_content(timeout=timeout))
        return value or ""

    def get_attribute(self, locator: Locator, name: str, timeout: int = 10000) -> str | None:
        return self._heal_and_retry(locator, lambda loc: loc.get_attribute(name, timeout=timeout))

    def is_visible(self, locator: Locator, timeout: int = 10000) -> bool:
        return bool(self._heal_and_retry(locator, lambda loc: loc.is_visible(timeout=timeout)))

    def count(self, locator: Locator) -> int:
        return int(locator.count())

    def first(self, locator: Locator) -> Locator:
        return locator.first

    def last(self, locator: Locator) -> Locator:
        return locator.last

    def nth(self, locator: Locator, index: int) -> Locator:
        return locator.nth(index)

    def get_by_text(self, text: str, exact: bool = False):
        return self.page.get_by_text(text, exact=exact)

    def get_by_role(self, role: str, name: str | re.Pattern[str] | None = None, exact: bool = False):
        return self.page.get_by_role(role, name=name, exact=exact)
