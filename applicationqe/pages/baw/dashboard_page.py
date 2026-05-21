from playwright.sync_api import Locator, Page

from config.settings import get_settings
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class DashboardPage(BasePage):
    """Dashboard page object for post-login navigation and interactions."""

    PAGE_URL = get_settings().get_app_config("navbar")["dashboard_url"]

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        self.clients_tab_btn: Locator = page.get_by_role("link", name="Clients")
        self.action_items_link: Locator = page.get_by_role("link", name="Action Items")

    def click_clients_tab(self) -> None:
        """Click on the Clients navigation link."""
        with logger.step("Click Clients navigation link"):
            self.clients_tab_btn.wait_for(state="visible", timeout=30000)
            self.clients_tab_btn.click()
            self.wait_for_spinner_to_disappear(timeout_seconds=30)
            self.close_chat_popups()

    def click_action_items_tab(self) -> None:
        """Click Action Items from current page, or navigate to dashboard and retry."""
        try:
            # Wait for any in-flight OAuth/OIDC redirects to settle before checking elements
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.action_items_link.wait_for(state="visible", timeout=15000)
            self.click(self.action_items_link)
            logger.info("Action Items tab clicked")
        except Exception:
            logger.warning("Action Items link not visible, navigating to dashboard and retrying")
            self.page.goto(self.PAGE_URL, wait_until="domcontentloaded", timeout=30000)
            self.action_items_link.wait_for(state="visible", timeout=15000)
            self.click(self.action_items_link)
            logger.info("Action Items tab clicked after dashboard navigation")
