from playwright.sync_api import Locator, Page

from locators import navbar_login_locators
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
        locators = navbar_login_locators.initialize_locators(self.page)
        self.username_input: Locator = locators["username_input"]
        self.password_input: Locator = locators["password_input"]
        self.sign_in_button: Locator = locators["sign_in_button"]

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

    def _maximize_window(self) -> None:
        """Maximize headed browser window (OS-level)."""
        try:
            cdp = self.page.context.new_cdp_session(self.page)
            window_id = cdp.send("Browser.getWindowForTarget")["windowId"]
            cdp.send("Browser.setWindowBounds", {
                "windowId": window_id,
                "bounds": {"windowState": "maximized"},
            })
        except Exception:
            pass

    def _stabilize_post_login_ui(self) -> None:
        self._maximize_window()
        self.page.wait_for_timeout(600)

        try:
            accept_all = self.page.locator("button:has-text('Accept All')").first
            if self.is_visible(accept_all, timeout=2000):
                accept_all.click(timeout=4000, force=True)
                self.page.wait_for_timeout(1200)
        except Exception:
            pass

        # User-provided exact close locator for "The Sidebar Navigation" popup.
        sidebar_close = self.page.locator(
            "//div[text()=\"The Sidebar Navigation\"]//parent::div//child::button[@type=\"button\"]"
        ).first
        for _ in range(2):
            try:
                if self.is_visible(sidebar_close, timeout=5000):
                    sidebar_close.click(timeout=4000, force=True)
                    self.page.wait_for_timeout(800)
                else:
                    break
            except Exception:
                self.page.wait_for_timeout(700)

    def login_application(self, username: str, password: str) -> None:
        self.navigate()
        if "dashboard" in (self.page.url or "").lower():
            self._stabilize_post_login_ui()
            logger.info(f"Navbar already on dashboard: {self.page.url}")
            return

        can_login = not self.page.is_closed() and self.is_visible(self.username_input.first, timeout=3000)
        if not can_login:
            logger.info(
                f"Navbar login form not visible; continuing with current URL: {self.page.url}"
            )
            return

        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()
        # Complete OAuth chain and ensure we settle on dashboard.
        self.page.wait_for_url(lambda url: "app." in url.lower(), timeout=60000)
        self.page.wait_for_function(
            """() => window.location.href.toLowerCase().includes('/dashboard')""",
            timeout=60000,
        )
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self._stabilize_post_login_ui()
        self.page.wait_for_timeout(5000)
        logger.info(f"Navbar login submitted. Current URL: {self.page.url}")
