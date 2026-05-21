"""BAW Login Page - Business Automation Workflow"""

from playwright.sync_api import Locator, Page

from config.settings import get_settings
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)



class BawLoginPage(BasePage):
    """BAW Login Page class with login functionality"""
    
    PAGE_NAME = "BAW Login Page"

    def __init__(self, page: Page):
        super().__init__(page)
        self.baw_url = self._get_baw_login_url()
        # Locators for BAW login form (from Java: By.id("username"), By.id("password"), etc.)
        self.username_field: Locator = page.locator("#username")
        self.password_field: Locator = page.locator("#password")
        self.signin_button: Locator = page.locator("//form[@id='signInForm']/a[@href='javascript:submitForm();']")

    def _get_baw_login_url(self) -> str:
        """Resolve BAW login URL from environment YAML."""
        baw_config = get_settings().get_app_config("baw")
        baw_url = (baw_config.get("login_url") or "").strip()
        if not baw_url:
            raise ValueError("BAW login_url is not configured in environment YAML (config/naw/env.*.yaml)")
        return baw_url

    @staticmethod
    def _normalize_login_method(login_method: str) -> str:
        """Normalize login method variants for direct BAW."""
        normalized = (login_method or "").strip().lower().replace(" ", "")
        if normalized in {"directbaw", "direct-baw", "direct_baw"}:
            return "directbaw"
        return normalized

    def navigate_to_baw(self) -> Page:
        """
        Navigate to BAW URL using direct navigation.

        Returns:
            Page object for the BAW application
        """
        with logger.step("Navigate to BAW", page=self.page):
            logger.info(f"Navigating to BAW URL: {self.baw_url}")
            self.page.goto(self.baw_url, wait_until="networkidle", timeout=30000)
            logger.info(f"Navigated to BAW: {self.page.url}")
            return self.page

    def enter_username(self, username: str) -> None:
        """
        Enter username in BAW login form

        Args:
            username: BAW username
        """
        with logger.step(f"Enter BAW username", page=self.page):
            logger.info("Waiting for username field to be visible")
            self.username_field.wait_for(state="visible", timeout=20000)
            
            logger.info(f"Entering username: {username}")
            self.fill(self.username_field, username)
            logger.info("Username entered successfully")

    def enter_password(self, password: str) -> None:
        """
        Enter password in BAW login form

        Args:
            password: BAW password
        """
        with logger.step("Enter BAW password", page=self.page):
            logger.info("Waiting for password field to be visible")
            self.password_field.wait_for(state="visible", timeout=20000)
            
            logger.info("Entering password")
            self.fill(self.password_field, password)
            logger.info("Password entered successfully")

    def click_signin(self) -> None:
        """Click the Sign In button"""
        with logger.step("Click Sign In button", page=self.page):
            logger.info("Waiting for Sign In button to be visible")
            self.signin_button.wait_for(state="visible", timeout=20000)
            
            logger.info("Clicking Sign In button")
            with self.page.expect_navigation(wait_until="load", timeout=30000):
                self.click(self.signin_button)
            logger.info(f"Sign In successful. Current URL: {self.page.url}")

    def login(self, username: str, password: str, baw_page: Page = None) -> None:
        """
        Complete BAW login process.

        Args:
            username: BAW username
            password: BAW password
            baw_page: Optional existing BAW page (from navigate_to_baw call)
        """
        with logger.step("BAW Login Process", page=self.page):
            # If baw_page not provided, navigate to BAW
            if baw_page is None:
                baw_page = self.navigate_to_baw()
            
            # Update self.page to the BAW page
            self.page = baw_page
            
            # Perform login
            self.enter_username(username)
            self.enter_password(password)
            self.click_signin()
            
            logger.info("BAW login completed successfully")

    def perform_login(self, test_data: dict) -> bool:
        """
        Complete BAW login flow: navigate -> enter creds -> sign in.

        Reads 'BawUserName' and 'BawUserPassword' columns from test_data.

        Args:
            test_data: dict from Excel row containing 'BawUserName' and 'BawUserPassword'

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            username = str(test_data.get("BawUserName", "")).strip()
            password = str(test_data.get("BawUserPassword", "")).strip()
            if not username or not password:
                logger.error("BAW credentials (BawUserName/BawUserPassword) not found in test data")
                return False
            self.navigate_to_baw()
            self.enter_username(username)
            self.enter_password(password)
            self.click_signin()
            return "login" not in self.page.url.lower()
        except Exception as e:
            logger.error(f"BAW login failed: {e}")
            return False
