from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class RothConversionPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/maintenance/journals/index?Method=roth&Toggle=DM_RothConversionsToggle&Advisor=AG8959&Household=CB54R2&AccountId=AM4K56'

    def __init__(self, page: Page):
        super().__init__(page)
        self.destination_account_paragraph: Locator = None  # Will be set dynamically
        self.destination_account_div: Locator = page.locator('div.css-1z0509q')
        self.convert_portion_span: Locator = page.get_by_text('Convert a Portion of the Account')
        self.portion_radio_input: Locator = page.locator("input.PrivateSwitchBase-input.css-1m9pwf3[name='radio-buttons-group'][value='portion']")
        # Use more reliable selector for amount input - by type and class instead of dynamic ID
        self.amount_input_field: Locator = page.locator('input[type="text"].MuiInputBase-input.MuiOutlinedInput-input.MuiInputBase-inputAdornedStart')
        # Federal withholding
        self.do_not_withhold_span: Locator = page.get_by_text('Do not withhold')
        self.do_not_withhold_radio_input: Locator = page.locator("input.PrivateSwitchBase-input.css-1m9pwf3[name='radio-buttons-group'][value='do_not_withhold']")
        # State withholding - will use same locators but access with .nth(1)
        self.str_message_paragraph: Locator = page.get_by_text('Your request will require additional review to ensure the existing source and/or destination account is still eligible due to recent actions on the account(s). Please refer to the Tracking Center for any additional requirements and an updated status.')
        self.str_button: Locator = page.get_by_role('button', name='SUBMIT TO REVIEW')
        self.next_button: Locator = page.get_by_role('button', name='Next')

    def navigate(self) -> None:
        logger.info(f"Navigating to Roth conversion page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Roth conversion page loaded")

    def select_destination_account(self, account_id: str) -> None:
        logger.info(f"Selecting destination account: {account_id}")
        self.destination_account_paragraph = self.page.get_by_text(account_id)
        self.destination_account_paragraph.click()
        logger.info(f"Destination account {account_id} selected")

    def click_destination_account_div(self) -> None:
        logger.info("Clicking destination account div")
        self.destination_account_div.click()

    def select_convert_portion(self) -> None:
        logger.info("Selecting convert portion option")
        self.convert_portion_span.click()
        self.portion_radio_input.check()
        logger.info("Convert portion selected")

    def enter_amount(self, amount: str) -> None:
        logger.info(f"Entering conversion amount: {amount}")
        self.amount_input_field.fill(amount)
        logger.info(f"Amount {amount} entered")

    def select_do_not_withhold(self) -> None:
        logger.info("Selecting do not withhold option for federal tax")
        # Federal withholding (first occurrence)
        self.do_not_withhold_span.first.click()
        self.do_not_withhold_radio_input.first.check()
        logger.info("Federal do not withhold selected")
        
        # State withholding (second occurrence)
        logger.info("Selecting do not withhold option for state tax")
        self.do_not_withhold_span.nth(1).click()
        self.do_not_withhold_radio_input.nth(1).check()
        logger.info("State do not withhold selected")

    def click_next(self) -> None:
        logger.info("Clicking Next button")
        self.next_button.click()
        logger.info("Next button clicked")

    def verify_destination_account(self, expected: str) -> None:
        logger.info(f"Verifying destination account contains: {expected}")
        # Use the paragraph that was dynamically set in select_destination_account
        if self.destination_account_paragraph:
            # Use to_contain_text instead of to_have_text to handle partial matches
            expect(self.destination_account_paragraph.first).to_contain_text(expected)
            logger.info("Destination account verified successfully")
        else:
            logger.warning("Destination account paragraph not set, skipping verification")

    def verify_next_button_visible(self) -> None:
        expect(self.next_button).to_be_visible()

    def verify_str_message(self, expected: str) -> None:
        expect(self.str_message_paragraph).to_have_text(expected)

    def verify_str_button_visible(self) -> None:
        expect(self.str_button).to_be_visible()

    def click_str_button(self) -> None:
        self.str_button.click()

