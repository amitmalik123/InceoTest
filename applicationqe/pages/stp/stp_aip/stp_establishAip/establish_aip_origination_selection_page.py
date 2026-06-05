from playwright.sync_api import Locator, Page
from pages.stp.shared.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.establish_aip_add_aip_page import EstablishAIPAddAIPPage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_origination_selection_locators import EstablishAIPOriginationSelectionLocators
from utils.settings import settings
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPOriginationSelectionPage(BasePage):
    """Page object for Establish AIP Origination Selection Page"""
    
    PAGE_NAME = "originationSelectionPage"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        loc = EstablishAIPOriginationSelectionLocators

        self.header = page.locator(loc.HEADER)
        self.title_section = page.locator(loc.TITLE_SECTION)

        self.next_button = page.locator(loc.NEXT_BUTTON)

        self.sub_header = page.locator(loc.SUB_HEADER)
        self.origination_label = page.locator(loc.ORIGINATION_LABEL)
        self.origination_help_text = page.locator(loc.ORIGINATION_HELP_TEXT)
        self.info_note_text = page.locator(loc.INFO_NOTE_TEXT)

        self.account_info_label = page.locator(loc.ACCOUNT_INFO_LABEL)
        self.account_info_text = page.locator(loc.ACCOUNT_INFO_TEXT)

        self.selected_origination_text = page.locator(loc.SELECTED_ORIGINATION_TEXT)
        self.selected_origination_text_checked = page.locator(
            loc.SELECTED_ORIGINATION_TEXT_CHECKED
        )

        self.view_details_link = page.locator(loc.VIEW_DETAILS_LINK)
        self.instruction_details_modal_header = page.locator(loc.INSTRUCTION_DETAILS_MODAL_HEADER)
        self.modal_close_icon_button = page.locator(loc.MODAL_CLOSE_ICON_BUTTON)
        self.modal_close_button = page.locator(loc.MODAL_CLOSE_BUTTON)
        self.mui_dialog_overlay = page.locator(loc.MUI_DIALOG_OVERLAY)

        self.spinner_loading = page.locator(loc.SPINNER_LOADING)
        self.loading_overlay = page.locator(loc.LOADING_OVERLAY)

        self.first_radio_button = page.locator(loc.FIRST_RADIO_BUTTON)
        self.first_radio_button_fallback = page.locator(loc.FIRST_RADIO_BUTTON_FALLBACK)
        self.checked_radio_selected = page.locator(loc.CHECKED_RADIO_SELECTED)

        self.wait_for_page_load(page_verification)
    
    def wait_for_page_load(self, page_verification: bool = True) -> None:
        """Wait for Origination Selection Page to load"""
        logger.info("Waiting for Establish AIP Origination Selection Page to load")

        try:
            if self.spinner_loading.count() > 0:
                self.spinner_loading.wait_for(state='hidden', timeout=30000)
                logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.warning(f"Spinner wait failed: {e}")

        try:
            if self.loading_overlay.count() > 0:
                self.loading_overlay.wait_for(state='hidden', timeout=30000)
                logger.info("Loading overlay disappeared")
        except Exception as e:
            logger.warning(f"Loading overlay wait failed: {e}")

        if page_verification:
            header_visible = self.is_visible(self.header, timeout=5000)
            title_visible = self.is_visible(self.title_section, timeout=5000)

            if header_visible and title_visible:
                logger.info(f"{self.PAGE_NAME} verification PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification FAILED")
    
    def select_instruction(self) -> None:
        """Select the first ACH instruction"""
        if self.is_instruction_already_selected():
            logger.info("ACH Instruction is already selected. Skipping selection.")
            return

        radio_container = self.first_radio_button
        radio_container.wait_for(state='visible', timeout=5000)

        if radio_container.count() == 0:
            radio_container = self.first_radio_button_fallback
            if radio_container.count() > 0:
                logger.info("Successfully located radio button using fallback label locator")
        else:
            logger.info("Successfully located radio button container")

        if radio_container.count() == 0:
            raise RuntimeError("ACH Instruction radio button not found on the page")

        try:
            logger.info("Attempting to click radio button container")
            radio_container.scroll_into_view_if_needed()
            radio_container.click()
            logger.info("Successfully selected radio button by clicking on the container")
        except Exception as e:
            raise RuntimeError(f"Failed to select ACH instruction: {e}")
    
    def is_instruction_already_selected(self) -> bool:
        """Check if an instruction is already selected"""
        return self.checked_radio_selected.count() > 0
    
    def is_header_visible(self) -> bool:
        """Check if header is visible"""
        return self.is_visible(self.title_section, timeout=5000)
    
    def is_sub_header_visible(self) -> bool:
        """Check if sub header is visible"""
        return self.is_visible(self.sub_header, timeout=5000)
    
    def is_origination_label_visible(self) -> bool:
        """Check if origination label is visible"""
        return self.is_visible(self.origination_label, timeout=5000)
    
    def is_origination_help_text_visible(self) -> bool:
        """Check if origination help text is visible"""
        return self.is_visible(self.origination_help_text, timeout=5000)
    
    def is_info_note_visible(self) -> bool:
        """Check if info note is visible"""
        return self.is_visible(self.info_note_text, timeout=5000)
    
    def is_expected_text_visible(self, text: str) -> bool:
        """Verify a visible text by exact normalized match"""
        if not text or not text.strip():
            return False

        trimmed = text.strip()

        if trimmed.lower() == "origination *":
            return self.is_visible(self.origination_label, timeout=5000)

        exact_locator = self.page.locator(f"//*[normalize-space()='{trimmed}']")
        if exact_locator.count() > 0:
            return True

        contains_locator = self.page.locator(f"//*[contains(normalize-space(), '{trimmed}')]")
        return contains_locator.count() > 0
    
    def click_next_button(self):
        """Click Next button and navigate to Add AIP Page"""
        logger.info("Clicking Next Button")
        self.next_button.wait_for(state='visible', timeout=5000)
        self.next_button.scroll_into_view_if_needed()
        self.click(self.next_button)
        logger.info("Clicking Next Button--> Clicked")
        
        return EstablishAIPAddAIPPage(self.page)
    
    def get_account_information_text(self) -> str:
        """Get account information text"""
        self.account_info_label.wait_for(state='visible', timeout=20000)
        return self.get_text(self.account_info_text)
    
    def get_selected_origination_text(self) -> str:
        """Get the selected origination text"""
        self.selected_origination_text_checked.wait_for(state='visible', timeout=5000)
        origination_text = self.get_text(self.selected_origination_text_checked)
        logger.info(f"Retrieved selected origination text: {origination_text}")
        return origination_text
    
    def click_view_details_and_verify_modal(self) -> None:
        """Click View Details and verify modal functionality"""
        self.view_details_link.wait_for(state='visible', timeout=10000)
        self.click(self.view_details_link)
        logger.info("Clicking View Details link--> Clicked")

        self.instruction_details_modal_header.wait_for(state='visible', timeout=10000)
        logger.info("Instruction Details modal is displayed")

        self.modal_close_icon_button.wait_for(state='visible', timeout=5000)
        self.click(self.modal_close_icon_button)
        logger.info("Clicking cross button on modal--> Clicked")

        if self.mui_dialog_overlay.count() > 0:
            self.mui_dialog_overlay.wait_for(state='hidden', timeout=10000)
        logger.info("Modal overlay has disappeared")

        self.title_section.wait_for(state='visible', timeout=10000)
        logger.info("User is back on Origination Selection page after clicking cross button")

        self.view_details_link.wait_for(state='visible', timeout=10000)
        self.click(self.view_details_link)
        logger.info("Clicking View Details link again--> Clicked")

        self.instruction_details_modal_header.wait_for(state='visible', timeout=10000)
        logger.info("Instruction Details modal is displayed again")

        self.modal_close_button.wait_for(state='visible', timeout=5000)
        self.click(self.modal_close_button)
        logger.info("Clicking CLOSE button on modal--> Clicked")

        if self.mui_dialog_overlay.count() > 0:
            self.mui_dialog_overlay.wait_for(state='hidden', timeout=10000)
        logger.info("Modal overlay has disappeared")

        self.title_section.wait_for(state='visible', timeout=10000)
        logger.info("User is back on Origination Selection page after clicking CLOSE button")
