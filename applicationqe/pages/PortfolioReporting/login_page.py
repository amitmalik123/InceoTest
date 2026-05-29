import os

from playwright.sync_api import Locator, Page

from locators.PortfolioReporting import login_locators
from pages.PortfolioReporting.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class LoginPage(BasePage):
    PAGE_PATH = "ewmLogin/account/login"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = login_locators.initialize_locators(page)
        self.allow_all_button: Locator = locators["allow_all_button"]
        self.username_input_field: Locator = locators["username_input_field"]
        self.password_input_field: Locator = locators["password_input_field"]
        self.sign_in_button: Locator = locators["sign_in_button"]
        self.login_form: Locator = locators["login_form"]

    def navigate(self) -> None:
        base_url = (self.base_url or "").strip()
        page_path = self.PAGE_PATH.lstrip("/")

        if base_url.startswith("http"):
            url = f"{base_url.rstrip('/')}/{page_path}"
        else:
            # Fallback keeps login flow usable when base_url is not supplied.
            env = os.getenv("TEST_ENV", "test11")
            url = f"https://{env}.ewealthmanager.com/{page_path}"

        logger.info(f"Navigating to login page: {url}")
        self.page.goto(url)
        # Allow All button is optional - only appears first time (no session/cookies)
        try:
            self.allow_all_button.wait_for(state="visible", timeout=3000)
            logger.info("Allow All button found")
        except Exception:
            logger.info("Allow All button not present (session may already exist)")
        logger.info("Login page loaded successfully")

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
