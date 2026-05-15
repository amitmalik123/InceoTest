from playwright.sync_api import Page

from pages.oam.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class DMToolPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    def get_household_id(self) -> str:
        """Fetch the ClientHouseholdID from the current URL"""
        current_url = self.page.url
        logger.info(f"Current URL: {current_url}")

        # Split by '=' and get the 3rd element (index 2)
        household_id = current_url.split("=")[2]
        logger.info(f"ClientHouseholdID: {household_id}")

        return household_id
