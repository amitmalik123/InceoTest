from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageInstruction1Page(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.next_button: Locator = page.get_by_role("button", name="NEXT")

    def select_radio_button(self, radio_type: str) -> None:
        """Select radio button by type (e.g., 'ACH', 'Wire', etc.)"""
        logger.info(f"Selecting radio button: {radio_type}")

        # Wait for DOM to be ready - better for SPAs with continuous updates
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        # Locator with increased timeout - auto-waits for actionability
        radio_button = self.page.locator(f'input[type="radio"][value="{radio_type}"]')

        # Click auto-waits for: attached, visible, stable, enabled
        try:
            radio_button.click(timeout=30000)
        except Exception as e:
            logger.warning(f"Normal click failed, trying force click: {e}")
            radio_button.click(force=True, timeout=10000)

        logger.info(f"Radio button '{radio_type}' selected")

    def click_next_button(self) -> None:
        """Click the Next button"""
        logger.info("Clicking Next button")

        # Click auto-waits for: attached, visible, stable, enabled
        self.next_button.click(timeout=30000)
        logger.info("Next button clicked")

    def get_household_id(self) -> str:
        """Fetch the ClientHouseholdID from the current URL"""
        current_url = self.page.url
        logger.info(f"Current URL: {current_url}")

        household_id = current_url.split("=")[2]
        logger.info(f"ClientHouseholdID: {household_id}")

        return household_id
