from playwright.sync_api import Locator, Page, expect

from locators import tracking_center_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class TrackingCenterPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.account_src_label: Locator = None  # Will be set dynamically
        locators = tracking_center_locators.initialize_locators(page)
        self.roth_str_label: Locator = locators["roth_str_label"]
        self.logout_link: Locator = locators["logout_link"]
        self.bodycontent_div: Locator = locators["bodycontent_div"]

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to tracking center page: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
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
        self.click(self.logout_link)
        logger.info("Logout clicked")

    def click_bodycontent(self) -> None:
        logger.info("Clicking body content")
        self.click(self.bodycontent_div)
