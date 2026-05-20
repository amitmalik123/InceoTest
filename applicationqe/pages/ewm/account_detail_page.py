from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AccountDetailPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/AccountsAnalysis/Clients/AccountDetail/Holdings/Summary/AM4K56/W108DM'

    def __init__(self, page: Page):
        super().__init__(page)
        # Use specific ID to avoid ambiguity with the main menu Account Wizard link
        self.account_wizard_link: Locator = page.locator('#clientDetailAccountDetailAnchor')
        self.funded_radio_input: Locator = page.locator("input#ctl00_cphContentArea_rdlAccountList_1[type='radio']")
        self.move_assets_between_accounts_list_item: Locator = page.get_by_text('Move Assets Between Accounts')
        # Use specific ID to avoid ambiguity with the header
        self.roth_ira_conversion_list_item: Locator = page.locator('#lstSubCategory5')
        self.next_button: Locator = page.get_by_role('button', name='Next')
        self.change_investment_link: Locator = page.get_by_text('Change Investments')

    def navigate(self) -> None:
        logger.info(f"Navigating to account detail page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.account_wizard_link.wait_for(state='visible', timeout=15000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    def wait_for_account_detail_loaded(self) -> None:
        logger.info("Waiting for Account Detail page to load")
        self.page.wait_for_load_state('networkidle', timeout=30000)
        if 'AccountsAnalysis/Clients/AccountDetail' not in self.page.url:
            raise Exception(f"Expected Account Detail page URL, but got: {self.page.url}")
        self.account_wizard_link.wait_for(state='visible', timeout=15000)
        logger.info("Account Detail page verified")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard button on account detail page")
        self.account_wizard_link.click()
        try:
            self.change_investment_link.wait_for(state='visible', timeout=15000)
        except Exception:
            self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Account Wizard button clicked and next screen is ready")

    def select_funded_radio(self) -> None:
        logger.info("Selecting Funded radio button")
        self.funded_radio_input.check()
        logger.info("Funded radio selected")

    def select_move_assets_between_accounts(self) -> None:
        logger.info("Selecting Move Assets Between Accounts")
        self.move_assets_between_accounts_list_item.click()
        logger.info("Move Assets Between Accounts selected")

    def select_roth_ira_conversion(self) -> None:
        logger.info("Selecting Roth IRA Conversion")
        self.roth_ira_conversion_list_item.click()
        logger.info("Roth IRA Conversion selected")

    def click_next(self) -> None:
        logger.info("Clicking Next button")
        self.next_button.click()
        logger.info("Next button clicked")

    def click_change_investment(self) -> None:
        logger.info("Clicking Change Investments link")
        self.change_investment_link.click()
        logger.info("Change Investments clicked")

