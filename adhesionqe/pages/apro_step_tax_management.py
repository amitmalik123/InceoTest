"""APro Proposal Tax Management step (wizard-3)."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalTaxManagementPage(BasePage):
    """Page object for APro proposal Tax Management step (wizard-3).

    Minimal step for tax management configuration.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 4 (Tax Management) container
        self.step_tax_management_panel: Locator = page.locator("#proposal-wizard-3")

        # TMS eligibility options
        self.tms_eligible_message: Locator = page.locator("text=Tax Management Services (TMS)")
        self.tms_ineligible_message: Locator = page.locator(
            "text=does not qualify for Tax Management Services"
        )

        # TMS selection cards
        self.tms_yes_option: Locator = page.locator("h3:has-text('Yes — Include TMS')").locator(
            ".."
        )
        self.tms_no_option: Locator = page.locator(
            "h3:has-text('No — Don\\'t Include TMS')"
        ).locator("..")

    def wait_for_tax_management_step(self, timeout: int = 10000) -> None:
        """Wait for the Tax Management (wizard step 4, proposal-wizard-3) to be visible."""
        logger.info("Waiting for Tax Management (proposal-wizard-3) step to be visible")
        self.wait_for_element(self.step_tax_management_panel, state="visible", timeout=timeout)

    def click_next(self) -> None:
        """Click Next button to proceed to Holdings step."""
        logger.info("Clicking Next from Tax Management step")
        next_button = self.step_tax_management_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-3 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button to go back to Allocation step."""
        logger.info("Clicking Previous from Tax Management step")
        prev_button = self.step_tax_management_panel.locator("button[data-wizard-previous]")
        prev_button.click()

    def is_tms_eligible(self, timeout: int = 5000) -> bool:
        """Check if the proposal qualifies for Tax Management Services.

        Returns True if the TMS eligibility message is visible, False if ineligible message is visible.
        Raises if neither message is found.

        Args:
            timeout: Wait timeout in ms

        Returns:
            True if TMS eligible, False if ineligible
        """
        logger.info("Checking TMS eligibility")

        try:
            self.tms_eligible_message.wait_for(state="visible", timeout=timeout)
            logger.info("Proposal qualifies for TMS")
            return True
        except Exception:
            try:
                self.tms_ineligible_message.wait_for(state="visible", timeout=timeout)
                logger.info("Proposal does not qualify for TMS")
                return False
            except Exception:
                raise RuntimeError(
                    "Could not determine TMS eligibility - neither eligible nor ineligible message found"
                )

    def select_include_tms(self) -> None:
        """Click the 'Yes — Include TMS' option card.

        Selects to include Tax Management Services with the proposal.
        In the future, this may trigger additional form fields or page state changes.
        """
        logger.info("Selecting 'Yes — Include TMS' option")
        self.click(self.tms_yes_option)
        self.page.wait_for_timeout(500)
        logger.info("TMS inclusion selected")

    def select_exclude_tms(self) -> None:
        """Click the 'No — Don't Include TMS' option card.

        Selects standard investment management without Tax Management Services.
        """
        logger.info("Selecting 'No — Don't Include TMS' option")
        self.click(self.tms_no_option)
        self.page.wait_for_timeout(500)
        logger.info("TMS exclusion selected")
