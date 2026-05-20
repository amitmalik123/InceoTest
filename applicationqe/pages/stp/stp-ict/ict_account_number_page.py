from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.ict_account_number_locators import ICTAccountNumberLocators
from validations.ict_account_number_validations import AccountNumberValidations

logger = setup_logger(__name__)

class AccountNumberPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/AcctNumber'

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ICTAccountNumberLocators()
        self.retain_account_number_radio: Locator = self.resolve_locator(self.locators.RETAIN_RADIO)
        self.new_account_number_radio: Locator = self.resolve_locator(self.locators.NEW_RADIO)
        self.next_button: Locator = self.resolve_locator(self.locators.NEXT)
        self._validations = AccountNumberValidations(self.page)

    def navigate(self) -> None:
        logger.info(f"Navigating to Account Number page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Account Number page loaded")

    def select_account_number_option(self, option: str) -> None:
        # Wait for this page to be ready before interacting
        self.page.wait_for_url('**/AcctNumber**', timeout=30000)
        self.page.wait_for_load_state('domcontentloaded', timeout=15000)
        if option.lower() == 'retain':
            logger.info("Retain Account Number selected by default — verifying and clicking Next")
            self._validations.validate_retain_selected()
            self.click_next()
        elif option.lower() == 'new':
            logger.info("Selecting New Account Number radio and clicking Next")
            self.new_account_number_radio.click()
            self._validations.validate_new_account_selected()
            self.click_next()
        else:
            logger.info(f"Unknown account_number_option '{option}' — clicking Next directly")
            self.click_next()

    def click_next(self) -> None:
        logger.info("Clicking Next button on Account Number page")
        self.next_button.click()
        logger.info("Next button clicked")
