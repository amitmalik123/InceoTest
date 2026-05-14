from typing import List

from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AddACHInstructionPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Input fields
        self.routing_number = page.locator('input[maxlength="9"][inputmode="numeric"]')
        self.bank_account_number = page.locator('[aria-label="Bank-AccountNumber"] input')
        self.confirm_bank_account_number = page.locator(
            '[aria-label="Confirm-BankAccount-Number"] input'
        )
        self.verify_button = page.locator("span:text('Verify')")
        self.bank_name_display = page.locator("span:text('Bank Name') + span")
        self.name_on_bank_account = page.locator(
            '[aria-label="Bank-Account-OwnerName"] textarea[aria-invalid]'
        )
        self.additional_bank_account_owner_name = page.get_by_placeholder(
            "Additional Bank Account Owner Name"
        )
        
        # Buttons
        self.verify_button = page.locator("span:text('Verify')")
        self.next_button = page.get_by_role("button", name="Next")
        
        # Display elements
        self.bank_name_display = page.locator("span:text('Bank Name') + span")
        self.account_name_list = page.get_by_test_id("account-details").locator("span").first
        
        # Radio buttons - Account Type
        self.checking_radio = page.get_by_role("radio", name="Checking")
        self.savings_radio = page.get_by_role("radio", name="Savings")
        
        # Radio buttons - Party Type
        self.first_party_radio = page.get_by_role("radio", name="1st Party")
        self.third_party_radio = page.get_by_role("radio", name="3rd Party")
        
        # Checkboxes
        self.certify_checkbox = page.locator("input[name='certifyCheckbox']")
        self.investment_account_checkbox = page.get_by_test_id("checkbox").locator(
            "input[type='checkbox']"
        )

    def client_household(self, household_header: str):
        """Helper method to get client household locator by header text"""
        return self.page.locator(f"span:text('{household_header}')")

    def account_heading(self, household_header: str):
        """Helper method to get account heading locator by household header"""
        return self.page.locator(
            f"xpath=//span[text()='{household_header}']/following-sibling::span"
        )
    
    def get_sloa_option_locator(self, sloa_option: str):
        """Helper method to get SLOA option locator"""
        sloa_label = self.page.locator(
            f"span[data-testid^='test-option-label']:has-text('{sloa_option}')"
        )
        return sloa_label.locator("xpath=ancestor::label//input[@type='radio']")
    
    def get_sloa_sub_option_locator(self, display_text: str):
        """Helper method to get SLOA sub-option locator"""
        sub_label = self.page.locator(f"label:has-text('{display_text}')")
        return sub_label.locator("input[type='radio']")

    def get_household_heading_and_account(self, household_header: str) -> List[str]:
        logger.info(f"Getting household heading and account name for: {household_header}")

        result_list = []

        heading_text = self.client_household(household_header).inner_text()
        result_list.append(heading_text)

        account_text = self.account_heading(household_header).inner_text()
        result_list.append(account_text)

        logger.info(f"Heading: {heading_text}, Account: {account_text}")
        return result_list

    def click_sloa_option(self, sloa_option: str) -> None:
        logger.info(f"Clicking SLOA option: {sloa_option}")
        sloa_radio = self.get_sloa_option_locator(sloa_option)
        self.click(sloa_radio)
        logger.info(f"SLOA option '{sloa_option}' clicked")

    def click_sloa_sub_option(self, sloa_sub_option: str) -> None:
        logger.info(f"Clicking SLOA sub-option: {sloa_sub_option}")

        sub_option_map = {
            "NoEsign": "Do Not Obtain Signature(s)",
            "Esign": "Obtain Electronic Signature(s)",
            "Print": "Print to Obtain Physical Signature(s)",
        }

        display_text = sub_option_map.get(sloa_sub_option, sloa_sub_option)
        sub_radio = self.get_sloa_sub_option_locator(display_text)
        self.click(sub_radio)
        logger.info(f"SLOA sub-option '{display_text}' clicked")

    def enter_details_for_vanishing_errors(
        self,
        rout_num: str,
        account_num: str,
        confirm_account_num: str,
        sloa_option: str,
        sloa_sub_option: str,
        additional_bao: str,
    ) -> List[str]:
        logger.info("Entering AINS page details")

        summary_details = []

        self.empty_field(self.routing_number, timeout=120000)
        self.routing_number.type(rout_num)
        number = self.routing_number.input_value()
        logger.info(f"Routing Number Entered: {number}")
        summary_details.append(number)

        self.click_verify()
        
        # Wait for bank name to load after verification
        self.page.wait_for_timeout(3000)
        
        ui_bank_name = self.get_bank_name_ui()
        logger.info(f"Bank Account Name Displayed: {ui_bank_name}")
        summary_details.append(ui_bank_name)

        self.empty_field(self.bank_account_number)
        self.bank_account_number.type(account_num)
        number1 = self.bank_account_number.input_value()
        logger.info(f"Bank Account Number Entered: {number1}")

        self.empty_field(self.confirm_bank_account_number)
        self.confirm_bank_account_number.type(confirm_account_num)
        number2 = self.confirm_bank_account_number.input_value()
        logger.info(f"Confirm Bank Account Number Entered: {number2}")
        summary_details.append(number1)

        self.click(self.checking_radio)
        summary_details.append("Checking")

        self.empty_field(self.name_on_bank_account)
        self.name_on_bank_account.type("HENRY SSASSAFRAS")
        name2 = self.name_on_bank_account.input_value()
        logger.info(f"Name/Title on Bank Account is: {name2}")
        summary_details.append(name2)

        self.click_sloa_option(sloa_option)
        summary_details.append(sloa_option)

        self.click_sloa_sub_option(sloa_sub_option)

        return summary_details

    def click_verify(self) -> None:
        logger.info("Clicking Verify button")
        self.verify_button.click(timeout=5000)
        logger.info("Verify button clicked")

    def get_bank_name_ui(self) -> str:
        logger.info("Getting bank name from UI")
        bank_name = self.bank_name_display.inner_text()
        logger.info(f"Bank name retrieved: {bank_name}")
        return bank_name

    def select_one_account(self, account_index: int) -> str:
        logger.info(f"Selecting account at index: {account_index}")
        account_locator = self.investment_account_checkbox.nth(account_index)
        self.click(account_locator)

        all_accounts = self.page.get_by_test_id("account-details")
        selected_account = all_accounts.nth(account_index).locator("span").first.inner_text()
        logger.info(f"Selected account: {selected_account}")
        return selected_account

    def select_multiple_accounts(self) -> str:
        logger.info("Selecting multiple investment accounts")
        count = self.investment_account_checkbox.count()

        selected_accounts = []
        for i in range(count):
            account_checkbox = self.investment_account_checkbox.nth(i)
            self.click(account_checkbox)
            account_name = self.account_name_list.nth(i).inner_text()
            selected_accounts.append(account_name)

        selected_accounts_str = ", ".join(selected_accounts)
        logger.info(f"Selected accounts: {selected_accounts_str}")
        return selected_accounts_str

    def select_party_type(self, party_type: str) -> None:
        """Select party type: '1st' or '3rd'"""
        logger.info(f"Selecting party type: {party_type}")
        
        if party_type == "1st":
            count = self.first_party_radio.count()
            
            for i in range(count):
                if self.first_party_radio.nth(i).is_enabled():
                    self.first_party_radio.nth(i).click(timeout=10000)
                    logger.info(f"1st Party selected (radio button {i})")
                    return
            
            raise Exception("No enabled 1st Party radio button found")
            
        elif party_type == "3rd":
            count = self.third_party_radio.count()
            
            for i in range(count):
                if self.third_party_radio.nth(i).is_enabled():
                    self.third_party_radio.nth(i).click(timeout=10000)
                    logger.info(f"3rd Party selected (radio button {i})")
                    return
            
            raise Exception("No enabled 3rd Party radio button found")
        else:
            raise ValueError(f"Invalid party type: {party_type}. Must be '1st' or '3rd'")

    def click_certify_checkbox(self) -> None:
        """Click the certify checkbox"""
        logger.info("Clicking certify checkbox")
        self.certify_checkbox.click(timeout=10000)
        logger.info("Certify checkbox clicked")

    def click_next(self) -> None:
        logger.info("Clicking Next button on Add ACH instruction page")
        self.next_button.click()
        self.page.wait_for_timeout(10000)
        logger.info("Next button clicked - navigating to summary page")
