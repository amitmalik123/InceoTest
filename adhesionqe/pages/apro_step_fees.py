"""APro Proposal Fees step (wizard-5)."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalFeesPage(BasePage):
    """Page object for APro proposal Fees step (wizard-5).

    Minimal step for fee configuration.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 6 (Fees) container
        self.step_fees_panel: Locator = page.locator("#proposal-wizard-5")

    def wait_for_fees_step(self, timeout: int = 10000) -> None:
        """Wait for the Fees (wizard step 6, proposal-wizard-5) to be visible."""
        logger.info("Waiting for Fees (proposal-wizard-5) step to be visible")
        self.wait_for_element(self.step_fees_panel, state="visible", timeout=timeout)

    def click_next(self) -> None:
        """Click Next button to proceed to Generate step."""
        logger.info("Clicking Next from Fees step")
        next_button = self.step_fees_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-5 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button to go back to Holdings step."""
        logger.info("Clicking Previous from Fees step")
        prev_button = self.step_fees_panel.locator("button[data-wizard-previous]")
        prev_button.click()
