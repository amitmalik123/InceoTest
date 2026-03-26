from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class NavbarLoginPage(BasePage):
    """Login page object for new navbar validation flow."""

    PAGE_URL = "https://app.test01.assetmark.com/"

    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    def _init_locators(self) -> None:
        """Initialize locators for the current page object reference."""
        self.username_input: Locator = self.page.locator(
            "input#okta-signin-username[name='username'][type='text'][aria-required='true']"
        )
        self.password_input: Locator = self.page.locator(
            "input#okta-signin-password[name='password'][type='password'][aria-required='true']"
        )
        self.sign_in_button: Locator = self.page.locator(
            "input#okta-signin-submit[type='submit'][value='Sign In']"
        )
        self.login_form: Locator = self.page.locator(
            "form#form32.primary-auth-form.o-form.o-form-edit-mode"
        )

    def _switch_to_latest_open_page(self) -> bool:
        """Switch to latest open page in context if current page gets closed."""
        try:
            if not self.page.is_closed():
                return True
            open_pages = [p for p in self.page.context.pages if not p.is_closed()]
            if not open_pages:
                return False
            self.page = open_pages[-1]
            self._init_locators()
            logger.info(f"Switched to latest open page: {self.page.url}")
            return True
        except Exception:
            return False

    def navigate(self) -> None:
        logger.info(f"Navigating to navbar login page: {self.PAGE_URL}")
        try:
            self.page.goto(self.PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            if "Target page, context or browser has been closed" not in str(e):
                raise
            if not self._switch_to_latest_open_page():
                raise

        # If SSO already authenticated, app may skip login form and redirect immediately.
        current_url = self.page.url
        if "signinCallback" in current_url or "dashboard" in current_url:
            logger.info(f"Navbar app redirected without login form: {current_url}")
            return

        self.username_input.wait_for(state="visible", timeout=20000)
        logger.info("Navbar login page loaded successfully")

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering navbar username: {username}")
        self.fill(self.username_input, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering navbar password")
        self.fill(self.password_input, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking navbar sign in button")
        self.click(self.sign_in_button)

    def login_application(self, username: str, password: str) -> None:
        self.navigate()
        if (
            not self.page.is_closed()
            and self.username_input.count() > 0
            and self.username_input.first.is_visible(timeout=3000)
        ):
            self.enter_username(username)
            self.enter_password(password)
            self.click_sign_in()
            # Wait for the full OAuth redirect chain to complete (callback → signinCallback → app)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_url(
                lambda url: "callback" not in url.lower() and "signinCallback" not in url,
                timeout=30000
            )
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"Navbar login submitted. Current URL: {self.page.url}")
            return

        logger.info(
            f"Navbar login form not visible; continuing with current URL: {self.page.url}"
        )
