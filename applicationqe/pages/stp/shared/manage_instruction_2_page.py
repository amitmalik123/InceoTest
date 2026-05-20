from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageInstruction2Page(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.add_button: Locator = page.get_by_role("button", name="Add")

    def click_add_button(self) -> None:
        """Click the Add button"""
        logger.info("Clicking Add button")
        self.click(self.add_button)
        logger.info("Add button clicked")
