from playwright.sync_api import Locator, Page
from pages.stp.shared.base_page import BasePage
from establish_aip_add_aip_page import EstablishAIPAddAIPPage
from utils.settings import settings
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPOriginationSelectionPage(BasePage):
    """Page object for Establish AIP Origination Selection Page"""
    
    PAGE_NAME = "originationSelectionPage"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)

        self.header = page.locator("//p[text()='Manage Automatic Investment Plans']")
        self.title_section = page.locator("//span[normalize-space()='Add Automatic Investment Plan (AIP)']")

        self.next_button = page.locator("//button[@type='button' and normalize-space(.)='NEXT']")

        self.sub_header = page.locator("//*[normalize-space()='Select the origination for the new automatic investment plan.']")
        self.origination_label = page.locator("//span[normalize-space()='Origination *'] | //span[normalize-space()='Origination']/span[normalize-space()='*']")
        self.origination_help_text = page.locator("//*[normalize-space()='Select which ACH Instructions on file to be used for the new automatic investment plan.']")
        self.info_note_text = page.locator("//div[text()=' In order to proceed with adding an AIP with new bank instructions, please Add ACH Instructions in the Account Wizard to add the bank before proceeding.']")

        self.account_info_label = page.locator("//span[text()='Account Information']")
        self.account_info_text = page.locator("//span[text()='Account Information']/ancestor::div[contains(@class,'MuiCardHeader-root')]//span[contains(@class,'MuiCardHeader-subheader')]")

        self.selected_origination_text = page.locator("(//div[@role='radiogroup']/child::ul/child::li[1]/descendant::p[contains(@class,'MuiTypography-root MuiTypography-body1')])[1]")
        self.selected_origination_text_checked = page.locator(
            "(//div[@role='radiogroup']//span[contains(@class,'Mui-checked')]"
            "/ancestor::li[1]//p[contains(@class,'MuiTypography-body1')])[1]"
        )

        self.view_details_link = page.locator("(//div[@data-testid='view-details-link'])[1]")
        self.instruction_details_modal_header = page.locator("//h2[text()='Instruction Details']")
        self.modal_close_icon_button = page.locator("//h2[text()='Instruction Details']/following-sibling::button")
        self.modal_close_button = page.locator("//button[normalize-space()='Close']")
        self.mui_dialog_overlay = page.locator("//div[contains(@class,'MuiDialog-container')]")

        self.spinner_loading = page.locator("div[class='App']>div>div>div>span")
        self.loading_overlay = page.locator("//div[contains(@class,'loading')]")

        self.first_radio_button = page.locator("(//span[contains(@class, 'MuiRadio-root')])[2]")
        self.first_radio_button_fallback = page.locator("(//label[.//input[@type='radio']])[1]")
        self.checked_radio_selected = page.locator("//input[@type='radio' and @checked]")

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
        if settings.env == 'prod':
            self.selected_origination_text_checked.wait_for(state='visible', timeout=5000)
            origination_text = self.get_text(self.selected_origination_text_checked)
        else:
            self.selected_origination_text.wait_for(state='visible', timeout=5000)
            origination_text = self.get_text(self.selected_origination_text)
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
