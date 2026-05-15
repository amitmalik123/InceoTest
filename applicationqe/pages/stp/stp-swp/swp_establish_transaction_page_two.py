from typing import List

from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishTransactionPageTwo(BasePage):
    """SWP Establish Transaction Page Two - Page Object Model"""

    PAGE_NAME = "SWP Establish Transaction Page Two"

    def __init__(self, page: Page):
        super().__init__(page)
        
        # Header section
        self.enter_swp_details: Locator = page.locator("//span[text()='Enter Systematic Withdrawal Plan (SWP) Details']")
        self.enter_swp_details_desc: Locator = page.locator("//div[@class='css-imtm4j']")
        
        # Sections
        self.freq_section: Locator = page.locator("//div[@class='sc-eiQriw diGbcn']")
        self.amount_section: Locator = page.locator("//div[@class='MuiGrid-root MuiGrid-container css-1d3bbye']")
        self.start_date_section: Locator = page.locator("//div[@class='sc-gMZepy coySKu']")
        self.end_date_section: Locator = page.locator("//div[@class='sc-cnVHiu bjYQfZ']")
        self.tax_withholding_section: Locator = page.locator("//div[@class='sc-WsMwQ fLPnYy']")
        self.add_new_swp_details: Locator = page.locator("//div[@class='MuiPaper-root MuiPaper-outlined MuiPaper-rounded MuiCard-root css-9x29ji']")
        self.signature_options: Locator = page.locator("//div[@class='css-172aq5v']")
        self.important_notes: Locator = page.locator("//div[@class='css-fu4pbp']")
        
        # Frequency radio buttons
        self.radio_buttons_tp2: Locator = page.locator("div.MuiFormGroup-root.MuiRadioGroup-root label")
        
        # Amount field
        self.amount_field: Locator = page.locator("//input[@id='outlined-adornment-amount']")
        self.amount_field_clear: Locator = page.locator("//input[@id='outlined-adornment-amount']")
        self.amount_error_field: Locator = page.locator("//span[@aria-label='error-message']")
        
        # NET checkbox
        self.net_checkbox: Locator = page.locator("//input[@type='checkbox']/ancestor::label")
        self.net_checkbox_locator: Locator = page.locator("input[type='checkbox'][data-indeterminate='false']")
        
        # Calendar/Date pickers
        self.calendar_picker_arrow: Locator = page.locator("//button[@title='Previous month']")
        self.calendar_picker_btn: Locator = page.locator("//button[@aria-label='Choose date']").first
        self.select_date: Locator = page.locator("//button[@data-timestamp='1743750000000']")
        self.type_date: Locator = page.locator("//input[@id=':r8:']")
        self.date_error_msg: Locator = page.locator("//span[@aria-label='error-message']")
        self.clear_date: Locator = page.locator("//*[local-name()='svg' and @class='MuiSvgIcon-root MuiSvgIcon-fontSizeSmall css-1k33q06']")
        self.calendar_picker_end_date: Locator = page.locator("//button[@aria-label='Choose date']")
        self.type_end_date: Locator = page.locator("//input[@id=':ra:']")
        
        # Date input fields
        self.start_date_input: Locator = page.locator("input[placeholder='MM/DD/YYYY']")
        self.end_date_input: Locator = page.locator("//input[@id=':ra:']")
        
        # Distribution Reason
        self.distribution_reason: Locator = page.locator("//*[local-name()='svg' and @data-testid='KeyboardArrowDownIcon']")
        self.distribution_reason_dropdown: Locator = page.locator("//p[contains(text(),'Select Distribution Reason')]")
        self.distribution_reason_dropdown_titles: Locator = page.locator("ul.MuiList-root li")
        self.distribution_reason_view_rules_link: Locator = page.locator("//div[contains(text(),'View Rules')]")
        self.distribution_reason_popup_titles: Locator = page.locator("div.css-yp9swi p.MuiTypography-root.css-ggyxjz")
        self.distribution_reason_popup_subtext: Locator = page.locator("div.css-yp9swi p.MuiTypography-root.css-1xmhjxn")
        self.distribution_reason_popup_close_btn: Locator = page.locator("//button[text()='CLOSE']")
        self.distribution_error: Locator = page.locator("//span[text()='Please select a distribution reason.']")
        self.distribution_reason_simple_ira: Locator = page.locator("//ul[@class='MuiList-root MuiList-padding MuiMenu-list css-r8u8y9']")
        
        self.view_rules: Locator = page.locator("//div[text()='View Rules']")
        self.view_rules_popup: Locator = page.locator("//div[@class='MuiDialogContent-root css-r2d22i']")
        self.close_view_rules: Locator = page.locator("//button[text()='CLOSE']")
        
        # Tax Withholding
        self.tax_withholding_title: Locator = page.locator("//p[text()='Tax Withholding']")
        self.tax_withholding_subtitle: Locator = page.locator("(//div[@class='css-c6p3v9']//text())[1]")
        self.tax_withholding_link_text_one: Locator = page.locator("//span[text()='Federal and State Tax Withholding Elections']")
        self.tax_withholding_link_text_two: Locator = page.locator("//span[text()='IRS Marginal Tax Tables']")
        
        # Federal Tax Withholding
        FEDERAL_SECTION = "//span[text()='Federal Tax Withholding ']/parent::div"
        self.federal_tax_title: Locator = page.locator("//span[text()='Federal Tax Withholding ']")
        self.federal_tax_subtitle: Locator = page.locator("//p[contains(text(),'The default for non-periodic payments is 10%')]")
        self.federal_tax_do_not_withhold_button: Locator = page.locator("(//span[contains(text(),'Do Not Withhold')])[1]")
        self.federal_tax_withhold_button: Locator = page.locator("(//span[contains(text(),'Withhold at a Rate of (1% to 99%):')])[1]")
        self.federal_tax_withhold_percentage_button: Locator = page.locator("//input[@id=':re:']")
        self.federal_do_not_withhold_radio: Locator = page.locator(f"{FEDERAL_SECTION}//child::span/input[@value='do_not_withhold']")
        self.federal_withhold_rate_radio: Locator = page.locator(f"{FEDERAL_SECTION}//input[@value='withhold']")
        self.federal_withhold_rate_input: Locator = page.locator(f"{FEDERAL_SECTION}//child::div/input[@type='text']")
        self.federal_do_not_withhold_text: Locator = page.locator("//div[contains(text(),'No federal income tax withheld')]")
        self.federal_withhold_text: Locator = page.locator("//div[contains(text(),'The default federal withholding rate is 10%')]")
        self.federal_dnw_button_message: Locator = page.locator("//div[contains(text(), 'No federal income tax withheld')]")
        
        # State Tax Withholding
        STATE_SECTION = "//span[text()='State Tax Withholding ']/parent::div"
        self.state_tax_title: Locator = page.locator("//span[text()='State Tax Withholding ']")
        self.state_tax_subtitle: Locator = page.locator("//p[contains(text(),'Not all states currently support withholding – consult each state's tax department for specific requirements. State withholding amounts will be rounded up to the next dollar.')]")
        self.state_tax_do_not_withhold_button: Locator = page.locator("(//span[contains(text(),'Do Not Withhold')])[2]")
        self.state_tax_withhold_button: Locator = page.locator("(//span[contains(text(),'Withhold at a Rate of (1% to 99%):')])[2]")
        self.state_tax_withhold_percentage_button: Locator = page.locator("//input[@id=':rg:']")
        self.state_tax_do_not_withhold_radio: Locator = page.locator(f"{STATE_SECTION}//child::span/input[@value='do_not_withhold']")
        self.state_tax_withhold_rate_radio: Locator = page.locator(f"{STATE_SECTION}//input[@value='withhold']")
        self.state_tax_text_input: Locator = page.locator(f"{STATE_SECTION}//child::div/input[@type='text']")
        self.state_dnw_button_message: Locator = page.locator("//div[contains(text(), 'No state income tax withheld')]")
        self.state_tax_withholding_disabled_message: Locator = page.locator("//div[@class='css-x43nyp']")
        
        # Federal and State containers
        self.federal_container: Locator = page.locator("div.MuiFormGroup-root.MuiRadioGroup-root.css-1sb3g1l")
        self.state_container: Locator = page.locator("div.MuiFormControl-root.css-1i5x313")
        
        # Rate input fields
        self.federal_rate_input: Locator = page.locator("input[id^=':re:']")
        self.state_rate_input: Locator = page.locator("input[id^=':rg:']")
        
        # Radio buttons
        self.radio_button_locator: Locator = page.locator("input[name='radio-buttons-group']")
        
        # Error messages
        self.error_message: Locator = page.locator("//span[contains(text(),'The state withholding you are requesting is below') or contains(text(),'You are attempting to withhold state without withholding federal or vice versa')]")
        self.please_review_msg: Locator = page.locator("//p[text()='Please review and fix the error(s).']")
        self.state_withholding_error_message: Locator = page.locator("//span[contains(@aria-label, 'error-message')]")
        self.please_review_error_message: Locator = page.locator("//p[text()='Please review and fix the error(s).']")
        
        # Banner and messages
        self.banner_message_ineligible: Locator = page.locator("//div[contains(text(),'You have selected a')]")
        self.state_minimum_message: Locator = page.locator("//div[contains(text(),'This registration type requires withholding the state minimum.')]")
        self.w4p_message: Locator = page.locator("//div[contains(text(),'Account owner must have a W4P exemption on file.')]")
        
        # Disabled withhold options
        self.do_not_withhold_radio_disabled: Locator = page.locator("//input[@type='radio' and @value='do_not_withhold' and @disabled]")
        self.withhold_radio: Locator = page.locator("(//input[@type='radio' and @value='withhold'])[2]")
        
        # Signature Options
        SIGNATURE_SECTION = "//div[@class='css-fzlq37']"
        self.signature_options_locator: Locator = page.locator("div.MuiRadioGroup-root label")
        self.signature_options_radio: Locator = page.locator("//div[text()='Select from the signature options below.']/following-sibling::div/child::div/child::label/child::span/input")
        self.not_obtain_signature_radio: Locator = page.locator(f"{SIGNATURE_SECTION}//span[contains(text(),'Do Not Obtain Client ')]")
        self.obtain_signature_radio: Locator = page.locator(f"{SIGNATURE_SECTION}//span[contains(text(),'Obtain Electronic')]")
        self.print_signature_radio: Locator = page.locator(f"{SIGNATURE_SECTION}//span[contains(text(),'Print to Obtain ')]")
        
        # Destination
        self.destination_section: Locator = page.locator("//div[text()='Destination Investment Account']/parent::div")
        
        # First Party (Journal)
        self.first_party: Locator = page.locator("input[name='journal-party-type'][value='1st Party']")
        
        # Buttons
        self.back_btn: Locator = page.locator("//button[text()='Back']")
        self.next_btn_tp2: Locator = page.locator("//button[text()='NEXT']")
        self.next_button_locator_tp2: Locator = page.locator("button.MuiButtonBase-root.MuiButton-root.MuiButton-contained")
        self.submit_button: Locator = page.locator("//button[@type='button' and (text()='Submit' or text()='SUBMIT TO ADVISOR' or contains(text(),'E-Sign and Submit') or contains(text(),'Complete and Print'))]")
        self.add_signer_btn: Locator = page.locator("//button[text()='+ Add Signer']")
        
        # Loader
        self.loader_with_header: Locator = page.locator("//span[contains(text(),'Your submission')]")
        self.loader_with_subheader: Locator = page.locator("//span[contains(text(),'Do not refresh this page')]")
        
        # Acknowledgements
        self.acknowledgement_title_locator: Locator = page.locator("//*[contains(text(),'Acknowledgements and Agreements')]")
        self.acknowledgement_contents_locator_ira: Locator = page.locator("ul.css-1mu4qj8 li")
        
        # Instruction radio button
        self.instruction_radio_button: Locator = page.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @name='radio-button' and @type='radio' and @value='0']")
    
    def get_date_button(self, day: str) -> Locator:
        """Get date button locator by day (used in swp_transaction_steps.py)"""
        return self.page.locator(f"//button[text()='{day}']")

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
