from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.select_source_account_locators import SelectSourceAccountLocators

logger = setup_logger(__name__)

class SelectSourceAccountPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/AcctSelection/SelectAccount'

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = SelectSourceAccountLocators()
        self.next_button: Locator = self.resolve_locator(self.locators.NEXT)

   # def navigate(self, bng_client_id: str | None = None) -> None:
    #    logger.info(f"Navigating to Select Source Account page for BngClientID={bng_client_id}")
    #    url = f"{self.PAGE_URL}?BngClientID={bng_client_id}" if bng_client_id else self.PAGE_URL
    #    self.navigate_to(url)
    #    self.wait_for_load_state('networkidle')
    #    logger.info("Select Source Account page loaded")

    def select_account_checkbox(self, account_number: str) -> None:
        """Find the row for 'Account #: {account_number}' and check the hidden input via force."""
        logger.info(f"Selecting source account checkbox for account {account_number}")
        if not account_number:
            raise ValueError("No account number provided to select_account_checkbox")

        label_selector = self.locators.ACCOUNT_LABEL_TEMPLATE.format(account_number=account_number)
        label = self.page.locator(label_selector)
        label.wait_for(state='visible', timeout=15000)
        logger.info(f"Found label for account {account_number}")

        # Step 1: Try clicking the Uniform.js span (what Uniform binds events to)
        checker_span = label.locator("xpath=../..//div[contains(@class,'checker')]//span")
        try:
            checker_span.click(timeout=3000, force=True)
            logger.info(f"Clicked checker span for account {account_number}")
        except Exception:
            # Fallback: click outer checker div
            checker = label.locator("xpath=../..//div[contains(@class,'checker')]")
            checker.click(force=True)
            logger.info(f"Clicked checker div for account {account_number}")

        # Step 2: Also force-check the hidden checkbox to trigger JS change events
        try:
            checkbox = label.locator("xpath=../..//input[@type='checkbox']")
            checkbox.check(force=True)
            logger.info(f"Force-checked hidden input for account {account_number}")
        except Exception as e:
            logger.warning(f"Could not force-check hidden input: {e}")

        # Step 3: Wait for Next button to become enabled (JS processes the selection)
        try:
            self.page.wait_for_function(
                "!document.getElementById('nextButton') || !document.getElementById('nextButton').disabled",
                timeout=5000,
            )
            logger.info("Next button enabled after checkbox selection")
        except Exception:
            logger.warning("Next button still appears disabled after selection attempt")

    def click_next(self) -> None:
        logger.info("Clicking Next button on Select Source Account page")
        # Wait up to 10s for Next to be enabled (Uniform.js may have a delay)
        try:
            self.page.wait_for_function(
                "document.getElementById('nextButton') && !document.getElementById('nextButton').disabled",
                timeout=10000,
            )
        except Exception:
            logger.warning("Next button still disabled before click — attempting anyway")
        self.next_button.click()
        logger.info("Next button clicked")



