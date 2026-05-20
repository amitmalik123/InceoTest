from typing import Union
from playwright.sync_api import Locator, Page, FrameLocator

from pages.stp.shared.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountDetailPage(BasePage):
    PAGE_URL = "https://test11.ewealthmanager.com/AccountsAnalysis/Clients/AccountDetail/Holdings/Summary/AM4K56/W108DM"

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        # Use specific ID to avoid ambiguity with the main menu Account Wizard link
        self.account_wizard_link: Locator = context.locator("#clientDetailAccountDetailAnchor")
        self.funded_radio_input: Locator = context.locator(
            "input#ctl00_cphContentArea_rdlAccountList_1[type='radio']"
        )
        self.move_assets_between_accounts_list_item: Locator = context.get_by_text(
            "Move Assets Between Accounts"
        )
        # Use specific ID to avoid ambiguity with the header
        self.roth_ira_conversion_list_item: Locator = context.locator("#lstSubCategory5")
        self.next_button: Locator = context.get_by_role("button", name="Next")
        self.manage_account_button = context.locator("div.actionButtons").get_by_role("button", name="Manage Account")
        self.manage_beneficiaries_link: Locator = context.locator("#ctl00_cphContentArea_lnkManageBeneficiary")


    def navigate(self) -> None:
        logger.info(f"Navigating to account detail page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.account_wizard_link.wait_for(state="visible", timeout=15000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard button on account detail page")
        self.account_wizard_link.wait_for(state="visible", timeout=60000)
        self.account_wizard_link.click(timeout=60000)
        self.page.wait_for_load_state("networkidle", timeout=120000)
        logger.info("Account Wizard button clicked and page loaded")

    def click_manage_account(self) -> None:
        logger.info("Clicking Manage Account button on account detail page")
        self.click(self.manage_account_button)
        logger.info("Manage Account button clicked")

    def verify_manage_beneficiaries_link_present(self) -> bool:
        """Verify Manage Beneficiaries link is present and return its text"""
        try:
            self.manage_beneficiaries_link.wait_for(state="visible", timeout=10000)
            link_text = self.manage_beneficiaries_link.text_content()
            logger.info(f"Manage Beneficiaries link found with text: {link_text}")
            return True
        except Exception as e:
            logger.error(f"Manage Beneficiaries link not found: {e}")
            return False

    def get_manage_beneficiaries_text(self) -> str:
        """Get text content of Manage Beneficiaries link"""
        return self.get_text(self.manage_beneficiaries_link)

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
