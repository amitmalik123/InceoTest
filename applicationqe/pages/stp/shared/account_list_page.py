from typing import Union
from playwright.sync_api import Locator, Page, FrameLocator

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountListPage(BasePage):
    PAGE_URL = "https://test11.ewealthmanager.com/AccountsAnalysis/Clients/AccountList"

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        # Search locators - work with both Page and FrameLocator
        self.search_input: Locator = context.locator("#client_search_input")
        self.search_button: Locator = context.locator("form.client_search button#searchbutton")
    
    def get_row_by_client_id(self, client_id: str) -> Locator:
        """Get row locator by client ID"""
        return self.context.locator(f"tr:has-text('{client_id}')")
    
    def get_account_cell_by_name(self, account_name: str) -> Locator:
        """Get account cell locator by account name using gridcell role"""
        return self.context.get_by_role("gridcell", name=account_name).first
    
    def get_account_by_text(self, account_name: str) -> Locator:
        """Get account locator by text"""
        return self.context.get_by_text(account_name).first

    def navigate(self) -> None:
        logger.info(f"Navigating to account list page: {self.PAGE_URL}")
        logger.info(f"Current URL before navigation: {self.page.url}")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Current URL after wait: {self.page.url}")
        logger.info("Account list page loaded")

    def search_client(self, client_id: str, click_header: str = None) -> None:
        logger.info(f"Searching for client: {client_id}")

        # Screenshots only work with Page context
        if self.page:
            before_path = f"reports/account_list_before_search_{client_id}.png"
            self.page.screenshot(path=before_path)
            logger.info(f"Screenshot saved: {before_path}")

        try:
            self.search_input.wait_for(state="visible", timeout=30000)
            self.fill(self.search_input, client_id)
            logger.info(f"Filled client ID: {client_id}")
        except Exception as e:
            logger.error(f"Search input not found: {e}")
            if self.page:
                self.page.screenshot(
                    path=f"reports/account_list_search_input_not_found_{client_id}.png"
                )
            raise Exception(f"Search input not found for client {client_id}")

        try:
            self.search_button.wait_for(state="visible", timeout=30000)
            self.click(self.search_button)
            logger.info("Clicked search button")
        except Exception as e:
            logger.error(f"Search button not found or not clickable: {e}")
            if self.page:
                self.page.screenshot(
                    path=f"reports/account_list_search_button_not_found_{client_id}.png"
                )
            raise Exception(f"Search button not found or not clickable for client {client_id}")

        if self.page:
            after_path = f"reports/account_list_after_search_{client_id}.png"
            self.page.screenshot(path=after_path)
            logger.info(f"Screenshot saved: {after_path}")

        logger.info(f"Search completed for client: {client_id}")

    def select_account(self, account_name: str, client_id: str = None) -> None:
        logger.info(f"Selecting account: {account_name} (Client ID: {client_id})")

        if client_id:
            try:
                row = self.get_row_by_client_id(client_id)
                logger.info(f"Found row with client ID: {client_id}")
                account_cell = row.locator(f"td:has-text('{account_name}')").first
                self.click(account_cell)
                logger.info(f"{account_name} account selected from client {client_id} row")
                return
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {e}. Trying alternative approach.")

        try:
            logger.info("Strategy 2: Using role gridcell selector")
            account_cell = self.get_account_cell_by_name(account_name)
            self.click(account_cell)
            logger.info(f"{account_name} account selected using gridcell role")
            return
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}. Trying final approach.")

        logger.info("Strategy 3: Using first occurrence of account name")
        account_cell = self.get_account_by_text(account_name)
        self.click(account_cell)
        logger.info(f"{account_name} account selected (first occurrence)")
