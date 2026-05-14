from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from config.oam.settings import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.allow_all_button: Locator = page.get_by_role('button', name='Allow All')
        self.username_input_field: Locator = page.get_by_label('Username')
        self.password_input_field: Locator = page.get_by_label('Password')
        self.sign_in_button: Locator = page.get_by_role('button', name='SIGN IN')
        self.login_form: Locator = page.locator('form#form19.primary-auth-form.o-form.o-form-edit-mode')

    def navigate(self) -> None:
        login_url = get_settings().login_url
        logger.info(f"Navigating to login page: {login_url}")
        self.page.goto(login_url)
        logger.info("Waiting for Allow All button")
        self.allow_all_button.wait_for(state='visible')
        logger.info("Login page loaded successfully")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies")
        self.allow_all_button.click()

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.username_input_field.fill(username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.password_input_field.fill(password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        # Click and wait for navigation to happen
        with self.page.expect_navigation(wait_until='networkidle', timeout=30000):
            self.sign_in_button.click()
        logger.info(f"Navigation after sign in completed. Current URL: {self.page.url}")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        # Additional wait to ensure any post-login redirects complete
        self.page.wait_for_load_state('domcontentloaded', timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")

