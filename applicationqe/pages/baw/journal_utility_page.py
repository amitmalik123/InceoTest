from playwright.sync_api import FrameLocator, Locator, Page

from config.settings import get_settings
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.helpers import random_number

logger = get_allure_logger(__name__)


class JournalUtilityPage(BasePage):
    """Journal Utility page object for interactions on the Journal Utility page."""
    

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        self._frame: FrameLocator = page.frame_locator("iframe[title='Coach']")
        f = self._frame
        self.destination_account: Locator = f.locator("[id=\"singleselect-JournalCV1\\:DestinationManageAccountNumber\"]").first
        self.destination_model_name: Locator = f.locator("[id=\"textarea-textarea-JournalCV1\\:DestinationModelName\"]").first
        self.unit: Locator = f.get_by_label("Unit").first
        self.amount: Locator = f.get_by_label("Amount", exact=True).first
        self.add_journal_button: Locator = f.get_by_role("button", name="Add Journal")
        self.save_and_close_button: Locator = f.get_by_role("button", name="Save & Close")
        self.pending_journal_cells: Locator = f.locator("table:has(th[aria-label='Dest Acct Name']) tbody td")

        # Wait for page + iframe content to fully load
        page.wait_for_load_state("load", timeout=60000)
        self.destination_account.wait_for(state="visible", timeout=30000)
        logger.info("JournalUtilityPage loaded - iframe content ready")

    def _select_different_destination_account(self, current_account: str) -> None:
        """Select a different destination account from the dropdown."""
        options = self.destination_account.locator("option").all()
        for option in options:
            text = (option.text_content() or "").strip()
            if text and text != current_account and text != "Select":
                self.select_option(self.destination_account, label=text)
                from playwright.sync_api import expect
                expect(self.destination_model_name).to_be_disabled(timeout=20000)
                break

    def selectUnit(self) -> None:
        self.select_option(self.unit, index=3)
        self.fill(self.amount, random_number(1))        
        logger.info("selecting unit percentage and enter amount")

    def clickAddJournalButton(self) -> None:
        self.click(self.add_journal_button)        
        logger.info("clicked on add journal button ")

    def validateAddedJournal(self) -> None:
        pending_journal = self.pending_journal_cells.all()
        if not pending_journal:
            raise ValueError("added journal is not present")
        logger.info("added journal has been validated ")

    def clickSaveCloseButton(self) -> None:
        self.click(self.save_and_close_button, timeout=30000)
        logger.info("clicked on save and close button on journal utility page")
        self.page.wait_for_timeout(2000)
        self.page.close()    
	
