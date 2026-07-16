import re

from playwright.sync_api import FrameLocator, Locator, Page

from config.settings import get_settings
from locators.baw.journal_utility_locators import JournalUtilityLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.helpers import random_number

logger = get_allure_logger(__name__)


class JournalUtilityPage(BasePage):
    """Journal Utility page object for interactions on the Journal Utility page."""
    

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        self._frame: FrameLocator = page.frame_locator(JournalUtilityLocators.COACH_IFRAME)
        f = self._frame
        self.destination_account: Locator = f.locator(JournalUtilityLocators.DESTINATION_ACCOUNT).first
        self.destination_model_name: Locator = f.locator(JournalUtilityLocators.DESTINATION_MODEL_NAME).first
        self.unit: Locator = f.get_by_label(JournalUtilityLocators.UNIT_LABEL).first
        self.amount: Locator = f.get_by_role("textbox", name=JournalUtilityLocators.AMOUNT_LABEL, exact=True).first
        self.add_journal_button: Locator = f.get_by_role("button", name=JournalUtilityLocators.ADD_JOURNAL_BUTTON_ROLE)
        self.save_and_close_button: Locator = f.get_by_role("button", name=JournalUtilityLocators.SAVE_AND_CLOSE_BUTTON_ROLE)
        self.pending_journal_cells: Locator = f.locator(JournalUtilityLocators.PENDING_JOURNAL_CELLS)

        # Wait for page + iframe content to fully load
        page.wait_for_load_state("load", timeout=60000)
        self.destination_account.wait_for(state="visible", timeout=30000)
        # Extract source account APL ID from URL (e.g. tw.local.accountAPLID=AI6CZ6)
        apl_match = re.search(r'accountAPLID=([^&]+)', page.url)
        self._source_apl_id: str = apl_match.group(1) if apl_match else ""
        logger.info(f"JournalUtilityPage loaded - source APL ID: '{self._source_apl_id}'")

    def _select_different_destination_account(self, current_account: str) -> None:
        """Select a destination account that is different from the source account."""

        # Step 1: Wait for the dropdown to be visible and click it
        self.destination_account.wait_for(state="visible", timeout=30000)
        self.destination_account.click()

        # Step 2: Get all options from the dropdown
        options = self.destination_account.locator("option").all()

        # Step 3: Loop through each option and pick the first non-source account
        for option in options:
            account_name = (option.text_content() or "").strip()
            apl_id = (option.get_attribute("value") or "").strip()

            # Skip placeholder option
            if not account_name or account_name == "Select":
                continue

            # Skip the source account (identified by APL ID extracted from URL)
            if apl_id == self._source_apl_id:
                logger.info(f"Skipping source account: '{account_name}'")
                continue

            # Step 4: Select the first valid destination account
            logger.info(f"Selecting destination account: '{account_name}'")
            self.select_option(self.destination_account, label=account_name)
            from playwright.sync_api import expect
            expect(self.destination_model_name).to_be_disabled(timeout=20000)
            break

    def selectUnit(self) -> None:
        self.select_option(self.unit, index=3)
        # Wait for BAW coach form recalculation after unit change to settle;
        # without this the amount fill races against BAW resetting the field.
        self.wait_for_timeout(2000)
        self.wait_for_loading_data()
        self.amount.wait_for(state="visible", timeout=10000)
        amount_value = random_number(2)
        self.fill(self.amount, amount_value)
        # Press Tab directly on the locator so the keystroke fires inside the
        # iframe and triggers BAW's onchange handler to commit the value.
        self.amount.press("Tab")
        # Verify BAW didn't reset the field during post-unit recalculation.
        actual = (self.amount.input_value() or "").strip()
        if not actual:
            logger.info("Amount cleared by BAW after unit selection - retrying")
            self.wait_for_timeout(1000)
            self.fill(self.amount, amount_value)
            self.amount.press("Tab")
        logger.info(f"selecting unit percentage and enter amount: {amount_value}")

    def clickAddJournalButton(self) -> None:
        self.scroll_into_view(self.add_journal_button)
        self.add_journal_button.wait_for(state="visible", timeout=10000)
        # Use dispatch_event to bypass BAW coach transparent overlay
        self.add_journal_button.dispatch_event("click")
        logger.info("clicked on add journal button")
        self.wait_for_loading_data()

    def validateAddedJournal(self) -> None:
        try:
            self.pending_journal_cells.first.wait_for(state="visible", timeout=30000)
        except Exception:
            raise ValueError("added journal is not present")
        pending_journal = self.pending_journal_cells.all()
        if not pending_journal:
            raise ValueError("added journal is not present")
        logger.info("added journal has been validated")

    def clickSaveCloseButton(self) -> None:
        self.click(self.save_and_close_button, timeout=30000)
        logger.info("clicked on save and close button on journal utility page")
        try:
            self.page.wait_for_timeout(2000)
        except Exception:
            pass
        try:
            self.page.close()
        except Exception:
            pass    
	


