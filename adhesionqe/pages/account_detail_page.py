from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountDetailPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountDetail/Holdings/Summary"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        # Use specific ID to avoid ambiguity with the main menu Account Wizard link
        self.account_wizard_link: Locator = page.locator("#clientDetailAccountDetailAnchor")
        self.funded_radio_input: Locator = page.locator(
            "input#ctl00_cphContentArea_rdlAccountList_1[type='radio']"
        )
        self.move_assets_between_accounts_list_item: Locator = page.get_by_text(
            "Move Assets Between Accounts"
        )
        # Use specific ID to avoid ambiguity with the header
        self.roth_ira_conversion_list_item: Locator = page.locator("#lstSubCategory5")
        self.next_button: Locator = page.get_by_role("button", name="Next")

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to account detail page: {url}")
        self.page.goto(url)
        self.account_wizard_link.wait_for(state="visible", timeout=15000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard button on account detail page")
        self.click(self.account_wizard_link)
        logger.info("Account Wizard button clicked")

    def select_funded_radio(self) -> None:
        logger.info("Selecting Funded radio button")
        self.funded_radio_input.check()
        logger.info("Funded radio selected")

    def select_move_assets_between_accounts(self) -> None:
        logger.info("Selecting Move Assets Between Accounts")
        self.click(self.move_assets_between_accounts_list_item)
        logger.info("Move Assets Between Accounts selected")

    def select_roth_ira_conversion(self) -> None:
        logger.info("Selecting Roth IRA Conversion")
        self.click(self.roth_ira_conversion_list_item)
        logger.info("Roth IRA Conversion selected")

    def click_next(self) -> None:
        logger.info("Clicking Next button")
        self.click(self.next_button)
        logger.info("Next button clicked")
