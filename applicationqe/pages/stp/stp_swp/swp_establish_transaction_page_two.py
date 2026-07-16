from typing import List

from playwright.sync_api import Locator, Page

from pages.ewm.base_page import BasePage
from pages.stp.stp_swp.locators.swp_establish_transaction_page_2_locators import SWPEstablishTransactionPage2Locators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishTransactionPageTwo(BasePage):
    """SWP Establish Transaction Page Two - Page Object Model"""

    PAGE_NAME = "SWP Establish Transaction Page Two"

    def __init__(self, page: Page):
        super().__init__(page)
        ctx = self.active_root()
        loc = SWPEstablishTransactionPage2Locators
        
        # Header section
        self.enter_swp_details: Locator = ctx.locator(loc.ENTER_SWP_DETAILS)
        self.enter_swp_details_desc: Locator = ctx.locator(loc.ENTER_SWP_DETAILS_DESC)
        
        # Sections
        self.freq_section: Locator = ctx.locator(loc.FREQ_SECTION)
        self.amount_section: Locator = ctx.locator(loc.AMOUNT_SECTION)
        self.start_date_section: Locator = ctx.locator(loc.START_DATE_SECTION)
        self.end_date_section: Locator = ctx.locator(loc.END_DATE_SECTION)
        self.tax_withholding_section: Locator = ctx.locator(loc.TAX_WITHHOLDING_SECTION)
        self.add_new_swp_details: Locator = ctx.locator(loc.ADD_NEW_SWP_DETAILS)
        self.signature_options: Locator = ctx.locator(loc.SIGNATURE_OPTIONS)
        self.important_notes: Locator = ctx.locator(loc.IMPORTANT_NOTES)
        
        # Frequency radio buttons
        self.radio_buttons_tp2: Locator = ctx.locator(loc.RADIO_BUTTONS_TP2)
        
        # Amount field
        self.amount_field: Locator = ctx.locator(loc.AMOUNT_FIELD)
        self.amount_field_clear: Locator = ctx.locator(loc.AMOUNT_FIELD)
        self.amount_error_field: Locator = ctx.locator(loc.AMOUNT_ERROR_FIELD)
        
        # NET checkbox
        self.net_checkbox: Locator = ctx.locator(loc.NET_CHECKBOX)
        self.net_checkbox_locator: Locator = ctx.locator(loc.NET_CHECKBOX_LOCATOR)
        
        # Calendar/Date pickers
        self.calendar_picker_arrow: Locator = ctx.locator(loc.CALENDAR_PICKER_ARROW)
        self.calendar_picker_btn: Locator = ctx.locator(loc.CALENDAR_PICKER_BTN).first
        self.select_date: Locator = ctx.locator(loc.SELECT_DATE)
        self.type_date: Locator = ctx.locator(loc.TYPE_DATE)
        self.date_error_msg: Locator = ctx.locator(loc.DATE_ERROR_MSG)
        self.clear_date: Locator = ctx.locator(loc.CLEAR_DATE)
        self.calendar_picker_end_date: Locator = ctx.locator(loc.CALENDAR_PICKER_END_DATE)
        self.type_end_date: Locator = ctx.locator(loc.TYPE_END_DATE)
        
        # Date input fields
        self.start_date_input: Locator = ctx.locator(loc.START_DATE_INPUT)
        self.end_date_input: Locator = ctx.locator(loc.END_DATE_INPUT)
        
        # Distribution Reason
        self.distribution_reason: Locator = ctx.locator(loc.DISTRIBUTION_REASON)
        self.distribution_reason_dropdown: Locator = ctx.locator(loc.DISTRIBUTION_REASON_DROPDOWN)
        self.distribution_reason_dropdown_titles: Locator = ctx.locator(loc.DISTRIBUTION_REASON_DROPDOWN_TITLES)
        self.distribution_reason_view_rules_link: Locator = ctx.locator(loc.DISTRIBUTION_REASON_VIEW_RULES_LINK)
        self.distribution_reason_popup_titles: Locator = ctx.locator(loc.DISTRIBUTION_REASON_POPUP_TITLES)
        self.distribution_reason_popup_subtext: Locator = ctx.locator(loc.DISTRIBUTION_REASON_POPUP_SUBTEXT)
        self.distribution_reason_popup_close_btn: Locator = ctx.locator(loc.DISTRIBUTION_REASON_POPUP_CLOSE_BTN)
        self.distribution_error: Locator = ctx.locator(loc.DISTRIBUTION_ERROR)
        self.distribution_reason_simple_ira: Locator = ctx.locator(loc.DISTRIBUTION_REASON_SIMPLE_IRA)
        
        self.view_rules: Locator = ctx.locator(loc.VIEW_RULES)
        self.view_rules_popup: Locator = ctx.locator("//div[@class='MuiDialogContent-root css-r2d22i']")
        self.close_view_rules: Locator = ctx.locator(loc.DISTRIBUTION_REASON_POPUP_CLOSE_BTN)
        
        # Tax Withholding
        self.tax_withholding_title: Locator = ctx.locator("//p[text()='Tax Withholding']")
        self.tax_withholding_subtitle: Locator = ctx.locator("(//div[@class='css-c6p3v9']//text())[1]")
        self.tax_withholding_link_text_one: Locator = ctx.locator("//span[text()='Federal and State Tax Withholding Elections']")
        self.tax_withholding_link_text_two: Locator = ctx.locator("//span[text()='IRS Marginal Tax Tables']")
        
        # Federal Tax Withholding
        self.federal_tax_title: Locator = ctx.locator(loc.FEDERAL_TAX_TITLE)
        self.federal_tax_subtitle: Locator = ctx.locator(loc.FEDERAL_TAX_SUBTITLE)
        self.federal_tax_do_not_withhold_button: Locator = ctx.locator(loc.FEDERAL_TAX_DO_NOT_WITHHOLD_BUTTON)
        self.federal_tax_withhold_button: Locator = ctx.locator(loc.FEDERAL_TAX_WITHHOLD_BUTTON)
        self.federal_tax_withhold_percentage_button: Locator = ctx.locator(loc.FEDERAL_TAX_WITHHOLD_PERCENTAGE_BUTTON)
        self.federal_do_not_withhold_radio: Locator = ctx.locator(loc.FEDERAL_DO_NOT_WITHHOLD_RADIO)
        self.federal_withhold_rate_radio: Locator = ctx.locator(loc.FEDERAL_WITHHOLD_RATE_RADIO)
        self.federal_withhold_rate_input: Locator = ctx.locator(loc.FEDERAL_WITHHOLD_RATE_INPUT)
        self.federal_do_not_withhold_text: Locator = ctx.locator(loc.FEDERAL_DO_NOT_WITHHOLD_TEXT)
        self.federal_withhold_text: Locator = ctx.locator(loc.FEDERAL_WITHHOLD_TEXT)
        self.federal_dnw_button_message: Locator = ctx.locator(loc.FEDERAL_DNW_BUTTON_MESSAGE)
        
        # State Tax Withholding
        self.state_tax_title: Locator = ctx.locator(loc.STATE_TAX_TITLE)
        self.state_tax_subtitle: Locator = ctx.locator(loc.STATE_TAX_SUBTITLE)
        self.state_tax_do_not_withhold_button: Locator = ctx.locator(loc.STATE_TAX_DO_NOT_WITHHOLD_BUTTON)
        self.state_tax_withhold_button: Locator = ctx.locator(loc.STATE_TAX_WITHHOLD_BUTTON)
        self.state_tax_withhold_percentage_button: Locator = ctx.locator(loc.STATE_TAX_WITHHOLD_PERCENTAGE_BUTTON)
        self.state_tax_do_not_withhold_radio: Locator = ctx.locator(loc.STATE_TAX_DO_NOT_WITHHOLD_RADIO)
        self.state_tax_withhold_rate_radio: Locator = ctx.locator(loc.STATE_TAX_WITHHOLD_RATE_RADIO)
        self.state_tax_text_input: Locator = ctx.locator(loc.STATE_TAX_TEXT_INPUT)
        self.state_dnw_button_message: Locator = ctx.locator(loc.STATE_DNW_BUTTON_MESSAGE)
        self.state_tax_withholding_disabled_message: Locator = ctx.locator(loc.STATE_TAX_WITHHOLDING_DISABLED_MESSAGE)
        
        # Federal and State containers
        self.federal_container: Locator = ctx.locator(loc.FEDERAL_CONTAINER)
        self.state_container: Locator = ctx.locator(loc.STATE_CONTAINER)
        
        # Rate input fields
        self.federal_rate_input: Locator = ctx.locator(loc.FEDERAL_RATE_INPUT)
        self.state_rate_input: Locator = ctx.locator(loc.STATE_RATE_INPUT)
        
        # Radio buttons
        self.radio_button_locator: Locator = ctx.locator(loc.RADIO_BUTTON_LOCATOR)
        
        # Error messages
        self.error_message: Locator = ctx.locator(loc.ERROR_MESSAGE)
        self.please_review_msg: Locator = ctx.locator(loc.PLEASE_REVIEW_MSG)
        self.state_withholding_error_message: Locator = ctx.locator(loc.STATE_WITHHOLDING_ERROR_MESSAGE)
        self.please_review_error_message: Locator = ctx.locator(loc.PLEASE_REVIEW_MSG)
        
        # Banner and messages
        self.banner_message_ineligible: Locator = ctx.locator(loc.BANNER_MESSAGE_INELIGIBLE)
        self.state_minimum_message: Locator = ctx.locator(loc.STATE_MINIMUM_MESSAGE)
        self.w4p_message: Locator = ctx.locator(loc.W4P_MESSAGE)
        
        # Disabled withhold options
        self.do_not_withhold_radio_disabled: Locator = ctx.locator(loc.DO_NOT_WITHHOLD_RADIO_DISABLED)
        self.withhold_radio: Locator = ctx.locator(loc.WITHHOLD_RADIO)
        
        # Signature Options
        self.signature_options_locator: Locator = ctx.locator(loc.SIGNATURE_OPTIONS_LOCATOR)
        self.signature_options_radio: Locator = ctx.locator(loc.SIGNATURE_OPTIONS_RADIO)
        self.not_obtain_signature_radio: Locator = ctx.locator(loc.NOT_OBTAIN_SIGNATURE_RADIO)
        self.obtain_signature_radio: Locator = ctx.locator(loc.OBTAIN_SIGNATURE_RADIO)
        self.print_signature_radio: Locator = ctx.locator(loc.PRINT_SIGNATURE_RADIO)
        
        # Destination
        self.destination_section: Locator = ctx.locator(loc.DESTINATION_SECTION)
        
        # First Party (Journal)
        self.first_party: Locator = ctx.locator(loc.FIRST_PARTY)
        
        # Buttons
        self.back_btn: Locator = ctx.locator(loc.BACK_BTN)
        self.next_btn_tp2: Locator = ctx.locator(loc.NEXT_BTN_TP2)
        self.next_button_locator_tp2: Locator = ctx.locator(loc.NEXT_BUTTON_LOCATOR_TP2)
        self.submit_button: Locator = ctx.locator(loc.SUBMIT_BUTTON)
        self.add_signer_btn: Locator = ctx.locator(loc.ADD_SIGNER_BTN)
        
        # Loader
        self.loader_with_header: Locator = ctx.locator(loc.LOADER_WITH_HEADER)
        self.loader_with_subheader: Locator = ctx.locator(loc.LOADER_WITH_SUBHEADER)
        
        # Acknowledgements
        self.acknowledgement_title_locator: Locator = ctx.locator(loc.ACKNOWLEDGEMENT_TITLE)
        self.acknowledgement_contents_locator_ira: Locator = ctx.locator(loc.ACKNOWLEDGEMENT_CONTENTS_IRA)
        
        # Instruction radio button
        self.instruction_radio_button: Locator = ctx.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @name='radio-button' and @type='radio' and @value='0']")
    
    def get_date_button(self, day: str) -> Locator:
        """Get date button locator by day (used in swp_transaction_steps.py)"""
        return self.active_root().locator(f"//button[text()='{day}']")

    def select_frequency(self, frequency: str) -> bool:
        """Select frequency radio button on transaction page two"""
        logger.info(f"Selecting frequency: {frequency}")
        
        # Wait for spinners and UI to load
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(5000)
        
        # Get all radio button labels
        radio_buttons = self.radio_buttons_tp2.all()
        
        for button in radio_buttons:
            button_text = button.text_content().strip()
            if button_text == frequency:
                button.click()
                logger.info(f"Selected Frequency: {frequency}")
                return True
        
        logger.error(f"Frequency '{frequency}' not found")
        return False

    def enter_amount(self, amount: str) -> None:
        """Enter amount in the amount field"""
        logger.info(f"Entering amount: {amount}")
        self.amount_field.wait_for(state='visible', timeout=10000)
        self.amount_field.fill(amount)
        logger.info(f"Amount entered: {amount}")

    def select_net_checkbox(self, selection: str) -> None:
        """Select or deselect NET checkbox"""
        logger.info(f"NET checkbox selection: {selection}")
        if selection.lower() == "select":
            if not self.net_checkbox.is_checked():
                self.net_checkbox.click()
                logger.info("NET checkbox selected")
        elif selection.lower() == "deselect":
            if self.net_checkbox.is_checked():
                self.net_checkbox.click()
                logger.info("NET checkbox deselected")

    def click_distribution_reason_dropdown(self) -> None:
        """Click distribution reason dropdown"""
        logger.info("Clicking distribution reason dropdown")
        self.distribution_reason_dropdown.wait_for(state='visible', timeout=10000)
        self.distribution_reason_dropdown.click()
        logger.info("Distribution reason dropdown clicked")

    def select_distribution_reason(self, reason: str) -> None:
        """Select distribution reason from dropdown"""
        logger.info(f"Selecting distribution reason: {reason}")
        
        # Get all dropdown options
        options = self.distribution_reason_dropdown_titles.all()
        
        for option in options:
            if reason in option.text_content():
                option.click()
                logger.info(f"Distribution reason selected: {reason}")
                return
        
        logger.error(f"Distribution reason '{reason}' not found")

    def select_federal_withholding_option(self, option: str) -> None:
        """Select federal withholding option"""
        logger.info(f"Selecting federal withholding option: {option}")
        
        if option.lower() == "do_not_withhold":
            self.federal_do_not_withhold_radio.click()
            logger.info("Federal 'Do Not Withhold' selected")
        elif option.lower() == "withhold":
            self.federal_withhold_rate_radio.click()
            logger.info("Federal 'Withhold' selected")

    def enter_federal_withholding_rate(self, rate: str) -> None:
        """Enter federal withholding rate"""
        if rate and rate.strip():
            logger.info(f"Entering federal withholding rate: {rate}")
            self.federal_withhold_rate_input.wait_for(state='visible', timeout=10000)
            self.federal_withhold_rate_input.fill(rate)
            logger.info(f"Federal rate entered: {rate}")

    def select_state_withholding_option(self, option: str) -> None:
        """Select state withholding option"""
        logger.info(f"Selecting state withholding option: {option}")
        
        if option.lower() == "do_not_withhold":
            self.state_tax_do_not_withhold_radio.click()
            logger.info("State 'Do Not Withhold' selected")
        elif option.lower() == "withhold":
            self.state_tax_withhold_rate_radio.click()
            logger.info("State 'Withhold' selected")

    def enter_state_withholding_rate(self, rate: str) -> None:
        """Enter state withholding rate"""
        if rate and rate.strip():
            logger.info(f"Entering state withholding rate: {rate}")
            self.state_tax_text_input.wait_for(state='visible', timeout=10000)
            self.state_tax_text_input.fill(rate)
            logger.info(f"State rate entered: {rate}")

    def select_signature_option(self, option: str) -> None:
        """Select signature option"""
        logger.info(f"Selecting signature option: {option}")
        
        # Get all signature option labels
        signature_options = self.signature_options_locator.all()
        
        for sig_option in signature_options:
            if option in sig_option.text_content():
                sig_option.click()
                logger.info(f"Signature option selected: {option}")
                return
        
        logger.error(f"Signature option '{option}' not found")

    def click_next_button(self) -> None:
        """Click Next button on Transaction Page Two"""
        logger.info("Clicking Next button on Transaction Page Two")
        self.next_btn_tp2.wait_for(state='visible', timeout=10000)
        self.next_btn_tp2.click()
        logger.info("Next button clicked")

    def click_submit_button(self) -> None:
        """Click Submit button"""
        logger.info("Clicking Submit button")
        self.submit_button.wait_for(state='visible', timeout=10000)
        self.submit_button.click()
        logger.info("Submit button clicked")

    def verify_page_loaded(self) -> bool:
        """Verify SWP Establish Transaction Page Two is loaded"""
        try:
            self.enter_swp_details.wait_for(state='visible', timeout=10000)
            logger.info(f"{self.PAGE_NAME} verification PASSED")
            return True
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification FAILED: {e}")
            return False
