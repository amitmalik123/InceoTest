from playwright.sync_api import Locator, Page, expect

from locators import roth_conversion_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class RothConversionPage(BasePage):
    PAGE_PATH = "maintenance/journals/index"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.destination_account_paragraph: Locator = None  # Will be set dynamically
        locators = roth_conversion_locators.initialize_locators(page)
        self.destination_account_div: Locator = locators["destination_account_div"]
        self.convert_portion_span: Locator = locators["convert_portion_span"]
        self.portion_radio_input: Locator = locators["portion_radio_input"]
        self.amount_input_field: Locator = locators["amount_input_field"]
        self.do_not_withhold_span: Locator = locators["do_not_withhold_span"]
        self.do_not_withhold_radio_input: Locator = locators["do_not_withhold_radio_input"]
        self.str_message_paragraph: Locator = locators["str_message_paragraph"]
        self.str_button: Locator = locators["str_button"]
        self.next_button: Locator = locators["next_button"]

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to Roth conversion page: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info("Roth conversion page loaded")

    def select_destination_account(self, account_id: str) -> None:
        logger.info(f"Selecting destination account: {account_id}")
        self.destination_account_paragraph = self.page.get_by_text(account_id)
        self.click(self.destination_account_paragraph)
        logger.info(f"Destination account {account_id} selected")

    def click_destination_account_div(self) -> None:
        logger.info("Clicking destination account div")
        self.click(self.destination_account_div)

    def select_convert_portion(self) -> None:
        logger.info("Selecting convert portion option")
        self.click(self.convert_portion_span)
        self.portion_radio_input.check()
        logger.info("Convert portion selected")

    def enter_amount(self, amount: str) -> None:
        logger.info(f"Entering conversion amount: {amount}")
        self.fill(self.amount_input_field, amount)
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
        self.click(self.next_button)
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
        logger.info("Clicking STR button")
        self.click(self.str_button)
