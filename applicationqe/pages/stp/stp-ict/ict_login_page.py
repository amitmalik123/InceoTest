import re
from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ewmLogin/account/login'

    def __init__(self, page: Page):
        super().__init__(page)
        self.allow_all_button: Locator = page.get_by_role('button', name='Allow All')
        self.username_input_field: Locator = page.get_by_label('Username')
        self.password_input_field: Locator = page.get_by_label('Password')
        self.sign_in_button: Locator = page.get_by_role('button', name='SIGN IN')
        self.login_form: Locator = page.locator('form#form19.primary-auth-form.o-form.o-form-edit-mode')

    def navigate(self) -> None:
        logger.info(f"Navigating to login page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        logger.info("Waiting for Allow All button (optional cookie consent)")
        try:
            self.allow_all_button.wait_for(state='visible', timeout=10000)
            self.allow_all_button.click()
            logger.info("Cookie consent accepted")
        except Exception:
            logger.info("Allow All button not present — skipping cookie consent")
        logger.info("Login page loaded successfully")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies (if present)")
        if self.allow_all_button.is_visible():
            self.allow_all_button.click()

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.username_input_field.fill(username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.password_input_field.fill(password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        start_url = self.page.url
        self.sign_in_button.click()

        try:
            self.page.wait_for_url(re.compile(r"(dashboard|/en\.aspx|AccountsAnalysis)"), timeout=30000)
        except Exception:
            try:
                self.page.wait_for_function(
                    "prev => window.location.href !== prev",
                    arg=start_url,
                    timeout=10000
                )
            except Exception:
                self.page.wait_for_load_state('domcontentloaded', timeout=30000)

        logger.info(f"Navigation after sign in completed. Current URL: {self.page.url}")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        # Additional wait to ensure any post-login redirects complete
        self.page.wait_for_load_state('domcontentloaded', timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")
