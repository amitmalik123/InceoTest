from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishTransactionPageOne(BasePage):
    """SWP Establish Transaction Page One - Page Object Model"""

    PAGE_NAME = "SWP Establish Transaction Page One"

    def __init__(self, page: Page):
        super().__init__(page)
        
        # Account Information section
        self.account_info_header: Locator = page.locator("//span[text()='Account Information']")
        self.account_info_values: Locator = page.locator("//span[@class='MuiTypography-root MuiTypography-body1 MuiCardHeader-subheader css-1cnfykm']")
        self.market_value: Locator = page.locator("//span[text()='Market Value:']")
        self.cash_available: Locator = page.locator("//span[text()='Cash Available:']")
        self.tooltip_btn: Locator = page.locator("//div[@aria-label='tooltip-icon-button']")
        self.tooltip_header: Locator = page.locator("//p[text()='The actual cash balance includes any restricted cash and could vary due to additional intraday activities such as:']")
        self.market_value_field_value: Locator = page.locator("(//span[contains(@class, 'sc-kCMKrZ')])[1]")
        self.cash_available_field_value: Locator = page.locator("(//span[contains(@class, 'sc-kCMKrZ')])[2]")
        
        # Add SWP header section
        self.add_swp_header: Locator = page.locator("//span[text()='Add Systematic Withdrawal Plan (SWP)']")
        self.add_swp_subheader: Locator = page.locator("//div[text()='Select distribution type, delivery method and destination for the new Systematic withdrawal plan.']")
        self.required_field: Locator = page.locator("//div[contains(@class, 'MuiCardHeader-action')]//div[contains(@class, 'sc-ijDOKB') and contains(., 'Required field')]")
        
        # Distribution Type section
        self.distribution_type_field: Locator = page.locator("//div[contains(@class, 'sc-eBwKMn') and contains(., 'Distribution Type')]")
        self.fixed_radio_button: Locator = page.locator("//input[@type='radio' and @value='Fixed Dollar Amount']")
        self.rmd_radio_button: Locator = page.locator("//input[@type='radio' and @value='Required Minimum Distribution']")
        self.fixed_radio_button_text: Locator = page.locator("//span[contains(text(), 'Fixed Dollar Amount')]")
        self.rmd_radio_button_text: Locator = page.locator("//span[contains(text(), 'Required Minimum Distribution')]")
        self.distribution_type_fixed: Locator = page.locator("//input[@value='Fixed Dollar Amount']")
        
        # Delivery Method section
        self.delivery_header: Locator = page.locator("//div[@class='sc-dBFDNq bJvgqJ']")
        self.delivery_subheader: Locator = page.locator("//div[@class='sc-dISpDn bCsUib']")
        self.delivery_options_ach: Locator = page.locator("//div[contains(@class, 'css-u3i1xq')]//label[contains(@class, 'MuiFormControlLabel-root')]//span[contains(@class, 'MuiTypography-body1') and text()='ACH']")
        self.delivery_options_check: Locator = page.locator("//div[contains(@class, 'css-u3i1xq')]//label[contains(@class, 'MuiFormControlLabel-root')]//span[contains(@class, 'MuiTypography-body1') and text()='Check']")
        self.delivery_options_journal: Locator = page.locator("//div[contains(@class, 'css-u3i1xq')]//label[contains(@class, 'MuiFormControlLabel-root')]//span[contains(@class, 'MuiTypography-body1') and text()='Journal']")
        
        self.ach_radio_button: Locator = page.locator("//input[@type='radio' and @value='ACH']")
        self.check_radio_button: Locator = page.locator("//input[@type='radio' and @value='Check']")
        self.journal_radio_button: Locator = page.locator("//input[@type='radio' and @value='Journal']")
        self.ach_delivery: Locator = page.locator("//span[starts-with(@class,'MuiButtonBase-root')]/input[@value='ACH']")
        
        self.no_delivery_method: Locator = page.locator("//div[@class='sc-bOhtcR dOwMgM MuiBox-root css-0']")
        self.delivery_method_opt_enabled: Locator = page.locator("//div[@class='sc-gvPdwL foHFvP MuiBox-root css-0']")
        
        # ACH Instructions section
        self.active_eligible_bank_radio_button: Locator = page.locator("//input[@type='radio' and @value='0']")
        self.active_instructions_ach_account_name: Locator = page.locator("(//p[@class='MuiTypography-root MuiTypography-body1 sc-fEiIrt kSmWKr css-9l3uo3'])[1]")
        self.active_instructions_ach_account_number: Locator = page.locator("(//p[@class='MuiTypography-root MuiTypography-body1 sc-ciQpPG hJMlpb css-9l3uo3'])[1]")
        self.instructions_ach_bottom_description: Locator = page.locator('//div[text()=\'In order to proceed with Establishing a SWP with new bank instructions, please use the "Add ACH Instructions" in Account Wizard to add the bank before proceeding.\']')
        self.add_swp_button: Locator = page.locator("//button[text()='+ Add SWP With New Instructions']")
        self.bank_name: Locator = page.locator("//p[@class='MuiTypography-root MuiTypography-body1 sc-fEiIrt kSmWKr css-9l3uo3']")
        self.account_name: Locator = page.locator("//p[@class='MuiTypography-root MuiTypography-body1 sc-ciQpPG hJMlpb css-9l3uo3']")
        
        # No Instructions on File
        self.no_file_on_instr: Locator = page.locator("//p[text()='No ACH Instructions on File']")
        self.no_inst_subheading: Locator = page.locator("//p[text()='The account selected does not currently have any active ACH instructions on file.']")
        self.bottom_message: Locator = page.locator("//div[@class='sc-ggqIjW hpgIDO']")
        self.no_bank_selected: Locator = page.locator(".PrivateSwitchBase-input")
        self.only_one_bank_selected: Locator = page.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @name='radio-button'][1]")
        self.add_swp_instruction: Locator = page.locator("//button[text()='+ Add SWP With New Instructions']")
        
        # Check Instructions section
        self.link_back_to_instructions_check: Locator = page.locator("//span[(text()='Back to Check Instructions on File')]")
        self.link_back_to_instructions_ach: Locator = page.locator("//span[(text()='Back to ACH Instructions on File')]")
        self.title_add_swp: Locator = page.locator("//div[(text()='Add SWP With New Check Instructions')]")
        self.check_payee_name: Locator = page.locator("(//p[@class='MuiTypography-root MuiTypography-body1 sc-inyXkq hiusSi css-9l3uo3'])[1]")
        self.check_payee_address: Locator = page.locator("(//p[@class='MuiTypography-root MuiTypography-body1 sc-fremEr gieMVE css-9l3uo3'])[1]")
        self.payee_check_radio_button: Locator = page.locator("//input[@name='radio-button']")
        self.payee_info_details: Locator = page.locator("//div[@class='sc-fatcLD fgIMTh MuiBox-root css-0']")
        
        # Party Type section
        self.heading_party_type: Locator = page.locator("//div[contains(text(),'Party Type')]")
        self.text_beneath_heading: Locator = page.locator("//div[(text()='Select the party type for new check instructions. You will be redirected to Docusign to complete the request.')]")
        self.radio_button_1st_party: Locator = page.locator("//h4[(text()='1st Party')]")
        self.sub_text_1st_party: Locator = page.locator("//p[(text()='Payee Name and Address same as the Investment account.')]")
        self.radio_button_3rd_party_same_address: Locator = page.locator("//h4[(text()='3rd Party (Same Address)')]")
        self.sub_text_3rd_party_same_address: Locator = page.locator("//p[(text()='Payee Name same but different address as the Investment account.')]")
        self.radio_button_3rd_party_different_address: Locator = page.locator("//h4[(text()='3rd Party (Different Address)')]")
        self.sub_text_3rd_party_different_address: Locator = page.locator("//p[(text()='Payee Name and Address are not the same as the Investment account.')]")
        self.party_type_details: Locator = page.locator("//div[@class='sc-DWsrX eyPoIq MuiBox-root css-0']")
        
        # Journal Instructions section
        self.journal_instructions: Locator = page.locator("//div[@class='css-1fqf0yk' and text()='Journal Instructions']")
        self.party_type_field_title: Locator = page.locator("//div[@class='css-140i4jo' and contains(text(),'Party Type')]")
        self.party_type_description: Locator = page.locator("//div[@class='css-k3m5h4' and contains(text(),'Select the party type of the receiving account')]")
        self.first_party_title: Locator = page.locator("//h4[@class='MuiTypography-root MuiTypography-h4 css-18c53be' and text()='1st Party']")
        self.first_party_description: Locator = page.locator("//p[@class='MuiTypography-root MuiTypography-body2 css-1t0x7co' and text()='Journal to investment account with the same beneficial owner.']")
        self.third_party_title: Locator = page.locator("//h4[@class='MuiTypography-root MuiTypography-h4 css-18c53be' and text()='3rd Party']")
        self.third_party_description: Locator = page.locator("//p[@class='MuiTypography-root MuiTypography-body2 css-1t0x7co' and text()='Journal to investment account with different account owner.']")
        self.radio_button_1st_party_journal: Locator = page.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @value='1st Party']")
        self.radio_button_3rd_party_journal: Locator = page.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @value='3rd Party']")
        
        # Buttons
        self.back_button: Locator = page.locator("//button[text()='Back']")
        self.cancel_button: Locator = page.locator("//button[text()='Cancel' and @type='button']")
        self.next_button: Locator = page.locator("//button[text()='NEXT']")
        self.establish_landing_add_button: Locator = page.locator("//button[text()='ADD +']")
        self.instruction_radio_button: Locator = page.locator("//input[@class='PrivateSwitchBase-input css-1m9pwf3' and @name='radio-button' and @type='radio' and @value='0']")
        
        # Cancel popup
        self.cancel_popup_header: Locator = page.locator("//h3[text()='Discard changes and exit?']")
        self.cancel_popup_subheader: Locator = page.locator("//h5[text()='Your changes will be lost. Are you sure you want to exit?']")
        self.yes_button_popup: Locator = page.locator("//button[text()='YES, EXIT']")
        self.no_button_popup: Locator = page.locator("//button[text()='NO, STAY']")
        
        # View Details
        self.view_details_link: Locator = page.locator("[data-testid='view-details-link']")
        self.view_details_link_text: Locator = page.locator("//div[text()='View Details']")
        self.instruction_details_header: Locator = page.locator("//h3[text()='Instruction Details']")
        self.bank_information: Locator = page.locator("//div[@class='sc-etVdmn fqLHul']")
        self.close_btn: Locator = page.locator("//button[text()='Close']")
        
        # Instruction Details fields
        self.bank_name_details: Locator = page.locator("//p[text()='Bank Name']/following-sibling::p")
        self.routing_number: Locator = page.locator("//p[text()='ABA/Routing Number']/following-sibling::p")
        self.bank_account_number: Locator = page.locator("//p[text()='Bank Account Number']/following-sibling::p")
        self.bank_account_type: Locator = page.locator("//p[text()='Bank Account Type']/following-sibling::p")
        self.owner_name: Locator = page.locator("//p[text()='Authorized Bank Account Owner/Agent Name']/following-sibling::p")
        self.payee_type: Locator = page.locator("//p[text()='Payee Type']/following-sibling::p")
        self.sloa: Locator = page.locator("//p[text()='Standing Letter of Authorization (SLOA)']/following-sibling::p")
        
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
