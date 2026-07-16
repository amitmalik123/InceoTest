from playwright.sync_api import Locator, Page, expect

from pages.ewm.base_page import BasePage
from pages.ewm.locators.manage_instruction_1_locators import ManageInstruction1Locators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageInstruction1Page(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        loc = ManageInstruction1Locators
        self.next_button: Locator = page.get_by_role('button', name=loc.NEXT_BUTTON)
        self.closed_on_date: Locator = page.locator(loc.CLOSED_ON_DATE)
        self.status: Locator = page.locator(loc.STATUS)
        self.description: Locator = page.locator(loc.DESCRIPTION)


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
        self.next_button.wait_for(state="visible", timeout=30000)
        # JS click bypasses any Ketch/OneTrust overlay intercepting pointer events
        self.next_button.evaluate("el => el.click()")
        logger.info("Next button clicked")

    def get_household_id(self) -> str:
        """Fetch the ClientHouseholdID from the current URL"""
        current_url = self.page.url
        logger.info(f"Current URL: {current_url}")

        household_id = current_url.split('=')[2].split('&')[0]
        logger.info(f"ClientHouseholdID: {household_id}")

        return household_id

    
    def get_closed_on_date(self) -> str:
        """Get the Closed On date"""
        logger.info("Getting Closed On date")
        self.closed_on_date.wait_for(state="visible", timeout=10000)
        closed_date = self.closed_on_date.inner_text()
        logger.info(f"Closed On Date: {closed_date}")
        return closed_date
    
    def get_status(self) -> str:
        """Get the Status"""
        logger.info("Getting Status")
        self.status.wait_for(state="visible", timeout=10000)
        status_text = self.status.inner_text()
        logger.info(f"Get Status --> : {status_text}")
        return status_text
    
    def get_description(self) -> str:
        """Get the Description"""
        logger.info("Getting Description")
        self.description.wait_for(state="visible", timeout=10000)
        desc_text = self.description.inner_text()
        logger.info(f"Get Description --> : {desc_text}")
        return desc_text

