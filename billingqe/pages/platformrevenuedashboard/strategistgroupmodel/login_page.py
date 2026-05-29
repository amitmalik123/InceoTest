"""Login page object for Billing Platform Revenue Dashboard > Strategist Group Model."""

import logging
import re
from typing import Optional

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Azure login helper page object."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def goto_login(self):
        self.navigate_to(self.base_url, wait_until="domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    def _first_visible_selector(self, selectors, timeout_ms: int):
        for selector in selectors:
            locator = self.page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=timeout_ms)
                return locator
            except PlaywrightTimeoutError:
                continue
        return None

    def _is_app_shell_visible(self, timeout_ms: int = 1500) -> bool:
        try:
            self.page.get_by_role("link", name=re.compile(r"log out", re.I)).first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True
        except Exception:
            pass

        try:
            self.page.get_by_role("button", name="Navigation menu").first.wait_for(
                state="visible", timeout=timeout_ms
            )
            self.page.get_by_role("link", name="Strategist Group Model").first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True
        except Exception:
            return False

    def _is_password_prompt_visible(self, timeout_ms: int = 2000) -> bool:
        password_locator = self._first_visible_selector(
            [
                "input#i0118",
                "input[name='passwd']:visible:not([aria-hidden='true']):not(.moveOffScreen)",
                "input[type='password']:visible:not([aria-hidden='true']):not(.moveOffScreen)",
            ],
            timeout_ms=timeout_ms,
        )
        return password_locator is not None

    def _click_use_another_account_if_present(self):
        candidates = [
            self.page.get_by_text(re.compile(r"use\s+another\s+account", re.I)).first,
            self.page.get_by_role("button", name=re.compile(r"use\s+another\s+account", re.I)).first,
        ]
        for locator in candidates:
            try:
                locator.wait_for(state="visible", timeout=2000)
                locator.click()
                logger.info("Clicked 'Use another account'")
                return
            except Exception:
                continue

    def _choose_password_signin_option_if_present(self):
        try:
            sign_in_options = self.page.get_by_text(re.compile(r"sign-?in\s+options", re.I)).first
            sign_in_options.wait_for(state="visible", timeout=1500)
            sign_in_options.click()
        except Exception:
            return

        candidates = [
            self.page.get_by_text(re.compile(r"password", re.I)).first,
            self.page.get_by_role("button", name=re.compile(r"password", re.I)).first,
        ]
        for locator in candidates:
            try:
                locator.wait_for(state="visible", timeout=1500)
                locator.click()
                logger.info("Selected password sign-in option")
                return
            except Exception:
                continue

    def _advance_to_password_prompt(self, username: str, attempts: int = 5) -> bool:
        username_selectors = [
            "input#i0116:visible",
            "input[name='loginfmt']:visible",
            "input[type='email']:visible",
            "input[name='loginfmt']",
            "input#i0116",
        ]

        for _ in range(attempts):
            if self._is_password_prompt_visible(timeout_ms=2500):
                return True

            if self._is_app_shell_visible(timeout_ms=1200):
                return True

            self._choose_password_signin_option_if_present()
            if self._is_password_prompt_visible(timeout_ms=2500):
                return True

            username_locator = self._first_visible_selector(username_selectors, timeout_ms=2000)
            if username_locator is not None:
                username_locator.fill(username)
                self.click_next()
                self.page.wait_for_timeout(1200)
                continue

            self.page.wait_for_timeout(800)

        return self._is_password_prompt_visible(timeout_ms=2500)

    def click_login_button(self):
        login_link = self.page.get_by_role("link", name=re.compile(r"log in", re.I)).first
        try:
            login_link.wait_for(state="visible", timeout=10000)
            login_link.click()
        except PlaywrightTimeoutError:
            pass

    def enter_username(self, username: str):
        if not username:
            raise ValueError("Username is empty.")

        selectors = [
            "input#i0116:visible",
            "input[name='loginfmt']:visible",
            "input[type='email']:visible",
            "input[name='loginfmt']",
            "input#i0116",
        ]

        locator = self._first_visible_selector(selectors, timeout_ms=2500)
        if locator:
            locator.fill(username)
            return

        if self._is_password_prompt_visible(timeout_ms=1200):
            return

        locator = self._first_visible_selector(selectors, timeout_ms=45000)
        if locator:
            locator.fill(username)
            return

        raise TimeoutError("Could not find username input field on login page.")

    def click_next(self):
        candidates = [
            self.page.get_by_role("button", name=re.compile(r"next|sign in", re.I)).first,
            self.page.locator("#idSIButton9").first,
        ]
        for button in candidates:
            try:
                button.wait_for(state="visible", timeout=10000)
                button.click()
                return
            except PlaywrightTimeoutError:
                continue

        if self._is_password_prompt_visible(timeout_ms=1200):
            return

        raise TimeoutError("Could not find Next/Sign in button after entering username.")

    def enter_password(self, password: Optional[str] = None):
        if not password:
            raise ValueError("Password is empty.")

        selectors = [
            "input#i0118",
            "input[name='passwd']:visible:not([aria-hidden='true']):not(.moveOffScreen)",
            "input[type='password']:visible:not([aria-hidden='true']):not(.moveOffScreen)",
            "input[name='passwd']:not([aria-hidden='true']):not(.moveOffScreen)",
            "input[type='password']:not([aria-hidden='true']):not(.moveOffScreen)",
        ]
        locator = self._first_visible_selector(selectors, timeout_ms=30000)
        if locator:
            locator.fill(password)
            return
        raise TimeoutError("Could not find password input field on login page.")

    def click_sign_in(self):
        before_url = self.page.url
        password_field = self.page.locator("input[type='password'], input[name='passwd']").first
        candidates = [
            self.page.get_by_role("button", name=re.compile(r"sign in", re.I)).first,
            self.page.locator("#idSIButton9").first,
        ]

        for _ in range(2):
            clicked = False
            for button in candidates:
                try:
                    button.wait_for(state="visible", timeout=10000)
                    button.scroll_into_view_if_needed()
                    button.click(force=True)
                    clicked = True
                    break
                except PlaywrightTimeoutError:
                    continue

            if not clicked:
                try:
                    password_field.press("Enter")
                except Exception:
                    self.page.keyboard.press("Enter")

            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass

            self.page.wait_for_timeout(1500)

            if self.page.url != before_url:
                return

            try:
                if not password_field.is_visible():
                    return
            except Exception:
                return

        raise TimeoutError("Could not submit sign in after entering password.")

    def handle_stay_signed_in(self):
        try:
            yes_button = self.page.get_by_role("button", name=re.compile(r"yes", re.I)).first
            yes_button.wait_for(state="visible", timeout=8000)
            yes_button.click()
        except Exception:
            pass

    def login(self, username: str, password: str):
        self.goto_login()

        if self._is_app_shell_visible(timeout_ms=2500):
            return

        self.click_login_button()
        if self._is_app_shell_visible(timeout_ms=2500):
            return

        self._click_use_another_account_if_present()
        self.enter_username(username)
        self.click_next()

        if not self._advance_to_password_prompt(username):
            if self._is_app_shell_visible(timeout_ms=2500):
                return
            raise TimeoutError("Could not reach password prompt from username step.")

        self.enter_password(password)
        self.click_sign_in()
        self.handle_stay_signed_in()

        if not self._is_app_shell_visible(timeout_ms=15000):
            raise TimeoutError("Login did not reach application shell after sign-in.")

    def logout(self):
        modal = self.page.get_by_role("dialog").first
        if modal.count() > 0:
            try:
                if modal.is_visible(timeout=1000):
                    ok_button = modal.get_by_role("button", name=re.compile(r"ok", re.I)).first
                    if ok_button.count() > 0:
                        try:
                            ok_button.click(timeout=1500)
                        except Exception:
                            pass
            except Exception:
                pass

        self.page.get_by_role("link", name="Log out").click(timeout=30000)
        self.page.wait_for_load_state("domcontentloaded")
