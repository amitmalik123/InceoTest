from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class LoginPage(BasePage):
    PAGE_PATH = "ewmLogin/account/login"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.allow_all_button: Locator = page.get_by_role("button", name="Allow All")
        self.accept_all_button: Locator = page.locator("#ketch-banner-button-primary")
        self.username_input_field: Locator = page.locator("input#okta-signin-username")
        self.password_input_field: Locator = page.locator("input#okta-signin-password")
        self.sign_in_button: Locator = page.locator("input#okta-signin-submit")
        self.login_form: Locator = page.locator(
            "form#form32.primary-auth-form.o-form.o-form-edit-mode"
        )
        self.onetrust_accept_button: Locator = page.locator("#accept-recommended-btn-handler")
        self.onetrust_overlay: Locator = page.locator("div.onetrust-pc-dark-filter")

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to login page: {url}")
        self.page.goto(url)
        # Cookie consent button is optional - only appears first time (no session/cookies)
        try:
            if self.accept_all_button.is_visible(timeout=2000):
                logger.info("Ketch Accept All button found")
            elif self.allow_all_button.is_visible(timeout=1000):
                logger.info("Allow All button found")
            else:
                logger.info("No cookie consent button present (session may already exist)")
        except Exception:
            logger.info("No cookie consent button present (session may already exist)")
        logger.info("Login page loaded successfully")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies")
        try:
            if self.accept_all_button.is_visible(timeout=2000):
                self.accept_all_button.click(timeout=3000)
                logger.info("Ketch Accept All button clicked")
                return
        except Exception:
            pass
        try:
            self.allow_all_button.click(timeout=2000)
        except Exception:
            logger.info("No cookie consent button available (already accepted or session exists)")

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.fill(self.username_input_field, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.fill(self.password_input_field, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        # Some environments do not trigger a full navigation on sign-in.
        # Try navigation wait first, then fall back to regular click + load-state wait.
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                self.click(self.sign_in_button)
        except PlaywrightTimeoutError:
            logger.warning("Sign-in did not trigger timed navigation; continuing with post-click waits")
            self.click(self.sign_in_button)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
        logger.info(f"Navigation after sign in completed. Current URL: {self.page.url}")

    def dismiss_onetrust(self) -> None:
        """Dismiss OneTrust cookie consent overlay if present (appears after login)."""
        try:
            if self.onetrust_accept_button.is_visible(timeout=5000):
                self.click(self.onetrust_accept_button)
                logger.info("OneTrust 'Allow All' button clicked")
                self.onetrust_overlay.wait_for(state="hidden", timeout=5000)
                return
        except Exception:
            pass
        # Fallback: dismiss via JS if overlay is blocking
        try:
            self.page.evaluate("document.querySelector('#onetrust-accept-btn-handler')?.click()")
            self.onetrust_overlay.wait_for(state="hidden", timeout=3000)
            logger.info("OneTrust consent dismissed via JS fallback")
        except Exception:
            logger.info("No OneTrust consent overlay present")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        # Additional wait to ensure any post-login redirects complete
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")
