from playwright.sync_api import Locator, Page
from typing import TYPE_CHECKING

from config.settings import get_settings
from pages.base_page import BasePage
from pages.baw.journal_utility_page import JournalUtilityPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

if TYPE_CHECKING:
    from pages.baw.journal_utility_page import JournalUtilityPage


class CreateOAPage(BasePage):
    """Create OA page object for interactions on the Create OA page."""

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        # Create OA page content is in the main frame (fauxRedirect.lsw)
        self.cancel_button: Locator = page.get_by_role("link", name="Cancel", exact=True)
        self.action_type_combobox: Locator = page.locator("#OAType").last
        self.save_and_close_button: Locator = page.get_by_role("button", name="Save & Close")

    def clickCancelLink(self) -> None:
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        # Wait for the Coach iframe content to render before checking for cancel links
        try:
            self.cancel_button.first.wait_for(state="visible", timeout=30000)
        except Exception:
            logger.info("No Cancel links found on the page — nothing to cancel")
            return
        cancel_buttons = self.cancel_button.all()
        if cancel_buttons:
            for button in cancel_buttons:
                try:
                    self.accept_alert()
                    self.click(button)
                    logger.info("Clicked on Cancel button and accepted alert")
                except Exception as e:
                    logger.warning(f"Failed to click Cancel button or accept alert: {str(e)}")            

    def selectActionType(self, value: str) -> JournalUtilityPage:
        logger.info("select action type to " + value)

        with self.page.context.expect_page(timeout=60000) as page_info:
            self.select_option(self.action_type_combobox, label=value)

        journal_utility_page = page_info.value
        journal_utility_page.wait_for_load_state("domcontentloaded", timeout=30000)
        journal_utility_page.bring_to_front()
        logger.info(f"Switched to JournalUtility tab: {journal_utility_page.url}")
        return JournalUtilityPage(journal_utility_page)
    
    def clickSaveCloseButton(self) -> None:
        self.click(self.save_and_close_button)
        logger.info("clicked on save and close button on create OA page")  
