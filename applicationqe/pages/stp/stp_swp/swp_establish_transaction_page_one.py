from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_swp.locators.swp_establish_transaction_page_1_locators import SWPEstablishTransactionPage1Locators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishTransactionPageOne(BasePage):
    """SWP Establish Transaction Page One - Page Object Model"""

    PAGE_NAME = "SWP Establish Transaction Page One"

    def __init__(self, page: Page):
        super().__init__(page)
        loc = SWPEstablishTransactionPage1Locators
        
        # Account Information section
        self.account_info_header: Locator = page.locator(loc.ACCOUNT_INFO_HEADER)
        self.account_info_values: Locator = page.locator(loc.ACCOUNT_INFO_VALUES)
        self.market_value: Locator = page.locator(loc.MARKET_VALUE)
        self.cash_available: Locator = page.locator(loc.CASH_AVAILABLE)
        self.tooltip_btn: Locator = page.locator(loc.TOOLTIP_BTN)
        self.tooltip_header: Locator = page.locator(loc.TOOLTIP_HEADER)
        self.market_value_field_value: Locator = page.locator(loc.MARKET_VALUE_FIELD_VALUE)
        self.cash_available_field_value: Locator = page.locator(loc.CASH_AVAILABLE_FIELD_VALUE)
        
        # Add SWP header section
        self.add_swp_header: Locator = page.locator(loc.ADD_SWP_HEADER)
        self.add_swp_subheader: Locator = page.locator(loc.ADD_SWP_SUBHEADER)
        self.required_field: Locator = page.locator(loc.REQUIRED_FIELD)
        
        # Distribution Type section
        self.distribution_type_field: Locator = page.locator(loc.DISTRIBUTION_TYPE_FIELD)
        self.fixed_radio_button: Locator = page.locator(loc.FIXED_RADIO_BUTTON)
        self.rmd_radio_button: Locator = page.locator(loc.RMD_RADIO_BUTTON)
        self.fixed_radio_button_text: Locator = page.locator(loc.FIXED_RADIO_BUTTON_TEXT)
        self.rmd_radio_button_text: Locator = page.locator(loc.RMD_RADIO_BUTTON_TEXT)
        self.distribution_type_fixed: Locator = page.locator(loc.DISTRIBUTION_TYPE_FIXED)
        
        # Delivery Method section
        self.delivery_header: Locator = page.locator(loc.DELIVERY_HEADER)
        self.delivery_subheader: Locator = page.locator(loc.DELIVERY_SUBHEADER)
        self.delivery_options_ach: Locator = page.locator(loc.DELIVERY_OPTIONS_ACH)
        self.delivery_options_check: Locator = page.locator(loc.DELIVERY_OPTIONS_CHECK)
        self.delivery_options_journal: Locator = page.locator(loc.DELIVERY_OPTIONS_JOURNAL)
        
        self.ach_radio_button: Locator = page.locator(loc.ACH_RADIO_BUTTON)
        self.check_radio_button: Locator = page.locator(loc.CHECK_RADIO_BUTTON)
        self.journal_radio_button: Locator = page.locator(loc.JOURNAL_RADIO_BUTTON)
        self.ach_delivery: Locator = page.locator(loc.ACH_DELIVERY)
        
        self.no_delivery_method: Locator = page.locator(loc.NO_DELIVERY_METHOD)
        self.delivery_method_opt_enabled: Locator = page.locator(loc.DELIVERY_METHOD_OPT_ENABLED)
        
        # ACH Instructions section
        self.active_eligible_bank_radio_button: Locator = page.locator(loc.ACTIVE_ELIGIBLE_BANK_RADIO_BUTTON)
        self.active_instructions_ach_account_name: Locator = page.locator(loc.ACTIVE_INSTRUCTIONS_ACH_ACCOUNT_NAME)
        self.active_instructions_ach_account_number: Locator = page.locator(loc.ACTIVE_INSTRUCTIONS_ACH_ACCOUNT_NUMBER)
        self.instructions_ach_bottom_description: Locator = page.locator(loc.INSTRUCTIONS_ACH_BOTTOM_DESCRIPTION)
        self.add_swp_button: Locator = page.locator(loc.ADD_SWP_BUTTON)
        self.bank_name: Locator = page.locator(loc.BANK_NAME)
        self.account_name: Locator = page.locator(loc.ACCOUNT_NAME)
        
        # No Instructions on File
        self.no_file_on_instr: Locator = page.locator(loc.NO_FILE_ON_INSTR)
        self.no_inst_subheading: Locator = page.locator(loc.NO_INST_SUBHEADING)
        self.bottom_message: Locator = page.locator(loc.BOTTOM_MESSAGE)
        self.no_bank_selected: Locator = page.locator(loc.NO_BANK_SELECTED)
        self.only_one_bank_selected: Locator = page.locator(loc.ONLY_ONE_BANK_SELECTED)
        self.add_swp_instruction: Locator = page.locator(loc.ADD_SWP_INSTRUCTION)
        
        # Check Instructions section
        self.link_back_to_instructions_check: Locator = page.locator(loc.LINK_BACK_TO_INSTRUCTIONS_CHECK)
        self.link_back_to_instructions_ach: Locator = page.locator(loc.LINK_BACK_TO_INSTRUCTIONS_ACH)
        self.title_add_swp: Locator = page.locator(loc.TITLE_ADD_SWP)
        self.check_payee_name: Locator = page.locator(loc.CHECK_PAYEE_NAME)
        self.check_payee_address: Locator = page.locator(loc.CHECK_PAYEE_ADDRESS)
        self.payee_check_radio_button: Locator = page.locator(loc.PAYEE_CHECK_RADIO_BUTTON)
        self.payee_info_details: Locator = page.locator(loc.PAYEE_INFO_DETAILS)
        
        # Party Type section
        self.heading_party_type: Locator = page.locator(loc.HEADING_PARTY_TYPE)
        self.text_beneath_heading: Locator = page.locator(loc.TEXT_BENEATH_HEADING)
        self.radio_button_1st_party: Locator = page.locator(loc.RADIO_BUTTON_1ST_PARTY)
        self.sub_text_1st_party: Locator = page.locator(loc.SUB_TEXT_1ST_PARTY)
        self.radio_button_3rd_party_same_address: Locator = page.locator(loc.RADIO_BUTTON_3RD_PARTY_SAME_ADDRESS)
        self.sub_text_3rd_party_same_address: Locator = page.locator(loc.SUB_TEXT_3RD_PARTY_SAME_ADDRESS)
        self.radio_button_3rd_party_different_address: Locator = page.locator(loc.RADIO_BUTTON_3RD_PARTY_DIFFERENT_ADDRESS)
        self.sub_text_3rd_party_different_address: Locator = page.locator(loc.SUB_TEXT_3RD_PARTY_DIFFERENT_ADDRESS)
        self.party_type_details: Locator = page.locator(loc.PARTY_TYPE_DETAILS)
        
        # Journal Instructions section
        self.journal_instructions: Locator = page.locator(loc.JOURNAL_INSTRUCTIONS)
        self.party_type_field_title: Locator = page.locator(loc.PARTY_TYPE_FIELD_TITLE)
        self.party_type_description: Locator = page.locator(loc.PARTY_TYPE_DESCRIPTION)
        self.first_party_title: Locator = page.locator(loc.FIRST_PARTY_TITLE_JOURNAL)
        self.first_party_description: Locator = page.locator(loc.FIRST_PARTY_DESCRIPTION_JOURNAL)
        self.third_party_title: Locator = page.locator(loc.THIRD_PARTY_TITLE_JOURNAL)
        self.third_party_description: Locator = page.locator(loc.THIRD_PARTY_DESCRIPTION_JOURNAL)
        self.radio_button_1st_party_journal: Locator = page.locator(loc.RADIO_BUTTON_1ST_PARTY_JOURNAL)
        self.radio_button_3rd_party_journal: Locator = page.locator(loc.RADIO_BUTTON_3RD_PARTY_JOURNAL)
        
        # Buttons
        self.back_button: Locator = page.locator(loc.BACK_BUTTON)
        self.cancel_button: Locator = page.locator(loc.CANCEL_BUTTON)
        self.next_button: Locator = page.locator(loc.NEXT_BUTTON)
        self.establish_landing_add_button: Locator = page.locator(loc.ESTABLISH_LANDING_ADD_BUTTON)
        self.instruction_radio_button: Locator = page.locator(loc.INSTRUCTION_RADIO_BUTTON)
        
        # Cancel popup
        self.cancel_popup_header: Locator = page.locator(loc.CANCEL_POPUP_HEADER)
        self.cancel_popup_subheader: Locator = page.locator(loc.CANCEL_POPUP_SUBHEADER)
        self.yes_button_popup: Locator = page.locator(loc.YES_BUTTON_POPUP)
        self.no_button_popup: Locator = page.locator(loc.NO_BUTTON_POPUP)
        
        # View Details
        self.view_details_link: Locator = page.locator(loc.VIEW_DETAILS_LINK)
        self.view_details_link_text: Locator = page.locator(loc.VIEW_DETAILS_LINK_TEXT)
        self.instruction_details_header: Locator = page.locator(loc.INSTRUCTION_DETAILS_HEADER)
        self.bank_information: Locator = page.locator(loc.BANK_INFORMATION)
        self.close_btn: Locator = page.locator(loc.CLOSE_BTN)
        
        # Instruction Details fields
        self.bank_name_details: Locator = page.locator(loc.BANK_NAME_DETAILS)
        self.routing_number: Locator = page.locator(loc.ROUTING_NUMBER_DETAIL)
        self.bank_account_number: Locator = page.locator(loc.BANK_ACCOUNT_NUMBER_DETAIL)
        self.bank_account_type: Locator = page.locator(loc.BANK_ACCOUNT_TYPE_DETAIL)
        self.owner_name: Locator = page.locator(loc.OWNER_NAME_DETAIL)
        self.payee_type: Locator = page.locator(loc.PAYEE_TYPE_DETAIL)
        self.sloa: Locator = page.locator(loc.SLOA_DETAIL)
        
        # Error messages
        self.distribution_type_error: Locator = page.locator("//span[text()='Please select a distribution type.']")
        self.delivery_method_error: Locator = page.locator("//span[text()='Please select a delivery type.']")
        self.add_swp_party_error: Locator = page.locator("//span[@class='sc-aXZVg dQXkK red']")
        self.add_ach_error: Locator = page.locator('//span[text()=\'Please select an instruction on file or use the "Add ACH Instructions" link in the Account Wizard to add a new bank.\']')
        self.party_type_error: Locator = page.locator("//span[text()='Please select party type.']")
        self.please_review_error: Locator = page.locator("//p[text()='Please review and fix the error(s).']")
        
        # Tax Withholding
        self.tax_withholding_section: Locator = page.locator("//p[text()='Tax Withholding']//parent::div")

    def select_distribution_type(self, distribution_type: str) -> None:
        """Select distribution type radio button (Fixed or RMD)"""
        logger.info(f"Selecting distribution type: {distribution_type}")
        
        # Wait for any spinners to disappear and page to settle
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(3000)
        
        distribution_type_lower = distribution_type.lower()
        
        if distribution_type_lower == "fixed":
            # Wait for the visible label span, then click it
            self.fixed_radio_button_text.wait_for(state='visible', timeout=60000)
            self.fixed_radio_button_text.click()
            button_text = "Fixed Radio Button Selected"
        elif distribution_type_lower == "rmd":
            self.rmd_radio_button_text.wait_for(state='visible', timeout=60000)
            self.rmd_radio_button_text.click()
            button_text = "RMD Radio Button Selected"
        else:
            logger.error(f"INVALID Distribution Type: {distribution_type}")
            raise ValueError(f"Invalid distribution type: {distribution_type}. Valid options are: 'Fixed' or 'RMD'")

        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(1000)
        logger.info(button_text)

    def select_delivery_method(self, delivery_method: str) -> None:
        """Select delivery method radio button (ACH, Check, or Journal).
        MUI hides the actual <input type='radio'> — click the visible label text span.
        """
        logger.info(f"Selecting delivery method: {delivery_method}")

        delivery_method_lower = delivery_method.lower()

        if delivery_method_lower == "ach":
            self.delivery_options_ach.wait_for(state='visible', timeout=15000)
            self.delivery_options_ach.click()
            button_text = "ACH Radio Button Selected"
        elif delivery_method_lower == "check":
            self.delivery_options_check.wait_for(state='visible', timeout=15000)
            self.delivery_options_check.click()
            button_text = "Check Radio Button Selected"
        elif delivery_method_lower == "journal":
            self.delivery_options_journal.wait_for(state='visible', timeout=15000)
            self.delivery_options_journal.click()
            button_text = "Journal Radio Button Selected"
        else:
            logger.error(f"INVALID Delivery Method: {delivery_method}")
            raise ValueError(f"Invalid delivery method: {delivery_method}. Valid options are: 'ACH', 'Check', or 'Journal'")
        
        # Wait for UI to update
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(1000)
        
        logger.info(button_text)

    def click_next_button(self) -> None:
        """Click Next button on Transaction Page One"""
        logger.info("Clicking Next button on Transaction Page One")
        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()
        logger.info("Next button clicked")

    def click_back_button(self) -> None:
        """Click Back button"""
        logger.info("Clicking Back button")
        self.back_button.wait_for(state='visible', timeout=10000)
        self.back_button.click()
        logger.info("Back button clicked")

    def click_cancel_button(self) -> None:
        """Click Cancel button"""
        logger.info("Clicking Cancel button")
        self.cancel_button.wait_for(state='visible', timeout=10000)
        self.cancel_button.click()
        logger.info("Cancel button clicked")

    def click_active_eligible_bank_radio_button(self) -> None:
        """Click active eligible bank radio button"""
        logger.info("Clicking active eligible bank radio button")
        self.active_eligible_bank_radio_button.wait_for(state='visible', timeout=10000)
        self.active_eligible_bank_radio_button.click()
        logger.info("Active eligible bank radio button clicked")

    def get_account_info_header(self) -> str:
        """Get account information header text"""
        return self.account_info_header.text_content()

    def get_market_value(self) -> str:
        """Get market value"""
        return self.market_value_field_value.text_content()

    def get_cash_available(self) -> str:
        """Get cash available"""
        return self.cash_available_field_value.text_content()

    def verify_page_loaded(self) -> bool:
        """Verify SWP Establish Transaction Page One is loaded"""
        try:
            self.add_swp_header.wait_for(state='visible', timeout=10000)
            self.distribution_type_field.wait_for(state='visible', timeout=10000)
            logger.info(f"{self.PAGE_NAME} verification PASSED")
            return True
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification FAILED: {e}")
            return False
