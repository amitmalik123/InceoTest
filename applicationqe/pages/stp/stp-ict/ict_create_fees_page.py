from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.ict_create_fees_locators import ICTCreateFeesLocators

logger = setup_logger(__name__)


class CreateFeesPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/Fees/CreateFees'

    def enter_fee(self, fee_type: str, fee_value: str) -> None:
        """Enter fee based on type: 'flat' fills the flat fee input, 'tiered' selects from dropdown."""
        logger.info(f"Entering fee — type: {fee_type}, value: {fee_value}")
        logger.info(f"Current URL before wait: {self.page.url}")
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info(f"Current URL after networkidle: {self.page.url}")
        # Save HTML for diagnostics on first use
        try:
            with open('reports/create_fees_page.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        if fee_type == 'flat':
            self.page.locator(ICTCreateFeesLocators.FLAT_FEE_INPUT).fill(fee_value)
            logger.info(f"Flat fee entered: {fee_value}")
        elif fee_type == 'tiered':
            self.page.locator(ICTCreateFeesLocators.TIERED_DROPDOWN).select_option(fee_value)
            logger.info(f"Tiered fee selected: {fee_value}")
        else:
            raise ValueError(f"Unknown fee_type '{fee_type}'. Expected 'flat' or 'tiered'.")

    def click_next(self) -> None:
        logger.info("Clicking Next button on Create Fees page")
        self.page.locator(ICTCreateFeesLocators.NEXT_BUTTON).click()
        logger.info("Next button clicked")
        