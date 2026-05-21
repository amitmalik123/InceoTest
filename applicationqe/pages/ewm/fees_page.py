from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class FeesPage(BasePage):
    """Page object for Fees page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.form_root = self.active_root()
        self.flat_fee: Locator = self.form_root.locator("#advFlatFee")
        self.confirm_client_fees: Locator = self.form_root.locator("#nextButton")


    def _ensure_fee_page_ready(self) -> None:
        """Wait for Fees page to fully load and re-resolve form root + locators."""
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.form_root = self.active_root()
        self.flat_fee = self.form_root.locator("#advFlatFee")
        self.confirm_client_fees = self.form_root.locator("#nextButton")
        self.flat_fee.wait_for(state="attached", timeout=30000)

    def enter_client_fee(self, fee_value: str, step_name: str, log_message: str) -> None:
        """Enter client flat fee in the fee input."""
        logger.info(step_name)
        self._ensure_fee_page_ready()
        logger.info(f"Fee page URL: {self.page.url}")

        self.flat_fee.wait_for(state="visible", timeout=30000)
        self.flat_fee.fill(str(fee_value))
        self.tab_out(self.flat_fee)
        logger.info(log_message)

    def confirm_client_fee(self, step_name: str, log_message: str) -> None:
        """
        Confirm client fee and proceed to next page.
        Mirrors old Selenium: confirmClientFee()

        Logic flow:
        1. Wait for fee input to have hasvalue='Yes' attribute indicating value was registered
        2. Click nextButton to confirm
        """
        logger.info(step_name)
        self._ensure_fee_page_ready()

        # Step 2: Click nextButton to confirm
        self.confirm_client_fees.wait_for(state="visible", timeout=30000)
        self.click(self.confirm_client_fees)
