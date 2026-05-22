from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.ict_summary_locators import ICTSummaryLocators

logger = setup_logger(__name__)


class ICTSummaryPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/Summary'

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ICTSummaryLocators()
        # use BasePage.resolve_locator to keep locator definitions centralized
        self.next_button: Locator = self.resolve_locator(self.locators.NEXT)

    def navigate(self) -> None:
        logger.info(f"Navigating to ICT Summary page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("ICT Summary page loaded")

    def click_next(self) -> None:
        logger.info("Clicking Next button on ICT Summary page")
        self.next_button.click()
        logger.info("Next button clicked")
