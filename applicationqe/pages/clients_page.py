from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ClientsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Test01 add client button
        self.add_client_button: Locator = page.get_by_role("button", name="Add a Client")

    def click_add_client(self) -> None:
        """Click the add a client button on test01 clients page."""
        logger.info("Clicking add a client button")
        try:
            self.add_client_button.wait_for(state="visible", timeout=30000)
            self._click_element_with_strategies(self.add_client_button, "Add a Client button")
        except PlaywrightTimeoutError:
            logger.warning(
                "Add a Client button did not become visible in 30s; using JS fallback on attached element"
            )
            self.add_client_button.first.wait_for(state="attached", timeout=10000)
            self.add_client_button.first.evaluate("el => el.click()")
        self.wait_for_spinner_to_disappear(timeout_seconds=30)
        logger.info("Add a client button clicked")
