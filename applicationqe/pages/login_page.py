from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from locators import login_locators
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
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to login page: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("Login page loaded successfully")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies / dismissing OneTrust overlay")
        # First try the BasePage OneTrust dismissal (handles Reject All, close button, JS removal)
        self._dismiss_onetrust_overlay()
        
        # Also try the Allow All button (legacy/alternative cookie consent)
        try:
            self.allow_all_button.click(timeout=2000)
        except Exception:
            logger.info("Allow All button not available (already accepted or dismissed)")

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.fill(self.username_input_field, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.fill(self.password_input_field, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        # Click sign in - triggers SSO redirect chain
        self.click(self.sign_in_button)
        
        # Wait for SSO redirect to complete - URL should no longer contain login paths
        # The SSO flow may land on different domains (ewealthmanager.com or ewm3.assetmark.net)
        try:
            self.page.wait_for_url(
                lambda url: "login" not in url.lower().split("?")[0].split("/")[-1]
                and "account/login" not in url.lower()
                and "test-login.assetmark.com" not in url.lower(),
                timeout=60000,
                wait_until="domcontentloaded"
            )
        except Exception:
            logger.warning(f"SSO redirect wait timed out. Current URL: {self.page.url}")
            self.page.wait_for_load_state("networkidle", timeout=120000)
        
        logger.info(f"Navigation after sign in completed. Current URL: {self.page.url}")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        # Additional wait to ensure any post-login redirects complete
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")
