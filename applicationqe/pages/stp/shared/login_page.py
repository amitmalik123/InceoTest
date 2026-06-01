from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.shared.locators.login_locators import LoginLocators
from utils.allure_logger import get_allure_logger
from utils.settings import settings

logger = get_allure_logger(__name__)


class LoginPage(BasePage):
    PAGE_URL = settings.login_url
    try:
        NEW_NAV_PAGE_URL = settings.get_role_url("manage_bene_test")
    except ValueError:
        NEW_NAV_PAGE_URL = ""

    def __init__(self, page: Page):
        super().__init__(page)
        loc = LoginLocators
        self.allow_all_button: Locator = page.get_by_role("button", name=loc.ALLOW_ALL_BUTTON)
        self.username_input_field: Locator = page.get_by_label(loc.USERNAME)
        self.password_input_field: Locator = page.get_by_label(loc.PASSWORD)
        self.sign_in_button: Locator = page.get_by_role("button", name=loc.SIGN_IN_BUTTON)
        self.login_form: Locator = page.locator(loc.LOGIN_FORM)

    def navigate(self) -> None:
        logger.info(f"Navigating to login page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        # Allow All button is optional - only appears first time (no session/cookies)
        try:
            self.allow_all_button.wait_for(state="visible", timeout=3000)
            logger.info("Allow All button found")
        except Exception:
            logger.info("Allow All button not present (session may already exist)")
        logger.info("Login page loaded successfully")

    def navigate_to_new_nav(self) -> None:
        logger.info(f"Navigating to new nav page: {self.NEW_NAV_PAGE_URL}")
        self.page.goto(self.NEW_NAV_PAGE_URL)
        self.dismiss_cookie_banner()
        logger.info("New nav page loaded successfully")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies")
        try:
            self.allow_all_button.click(timeout=2000)
        except Exception:
            logger.info("Allow All button not available (already accepted or session exists)")

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.fill(self.username_input_field, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.fill(self.password_input_field, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        # Click and wait for navigation to happen
        with self.page.expect_navigation(wait_until="networkidle", timeout=30000):
            self.click(self.sign_in_button)
        logger.info(f"Navigation after sign in completed. Current URL: {self.page.url}")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        # Additional wait to ensure any post-login redirects complete
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")
