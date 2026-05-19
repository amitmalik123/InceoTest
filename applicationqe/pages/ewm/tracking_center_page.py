from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TrackingCenterPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail/A034607033'

    def __init__(self, page: Page):
        super().__init__(page)
        self.account_src_label: Locator = None  # Will be set dynamically
        self.roth_str_label: Locator = page.get_by_text('Roth Conversion')
        self.logout_link: Locator = page.get_by_role('link', name='Logout')
        self.bodycontent_div: Locator = page.locator('div#BodyContent')

    def navigate(self) -> None:
        logger.info(f"Navigating to tracking center page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Tracking center page loaded")

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Verifying account source: {expected}")
        self.account_src_label = self.page.get_by_text(expected)
        expect(self.account_src_label).to_have_text(expected)
        logger.info(f"Account source {expected} verified")

    def verify_roth_str(self, expected: str) -> None:
        logger.info(f"Verifying Roth STR: {expected}")
        expect(self.roth_str_label).to_have_text(expected)
        logger.info(f"Roth STR {expected} verified")

    def click_logout(self) -> None:
        logger.info("Clicking logout")
        self.logout_link.click()
        logger.info("Logout clicked")

    def click_bodycontent(self) -> None:
        logger.info("Clicking body content")
        self.bodycontent_div.click()

