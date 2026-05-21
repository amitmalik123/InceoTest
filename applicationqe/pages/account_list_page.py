from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountListPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountList"

    def __init__(self, page: Page):
        super().__init__(page)
        self.client_search_input: Locator = page.locator("#client_search_input")
        self.client_search_button: Locator = page.locator("form.client_search button#searchbutton")

    def _get_client_row(self, client_id: str) -> Locator:
        """Get table row locator for specific client ID"""
        return self.page.locator(f"tr:has-text('{client_id}')")
    
    def _get_gridcell_by_name(self, name: str) -> Locator:
        """Get gridcell locator by name"""
        return self.page.get_by_role("gridcell", name=name).first
    
    def _get_element_by_text(self, text: str) -> Locator:
        """Get element locator by text content"""
        return self.page.get_by_text(text).first

    def navigate(self) -> None:
        logger.info(f"Navigating to account list page: {self.PAGE_PATH}")
        logger.info(f"Current URL before navigation: {self.page.url}")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Current URL after wait: {self.page.url}")
        logger.info("Account list page loaded")

    def search_client(self, client_id: str, click_header: str = None) -> None:
        logger.info(f"Searching for client: {client_id}")

        before_path = f"reports/account_list_before_search_{client_id}.png"
        self.page.screenshot(path=before_path)
        logger.info(f"Screenshot saved: {before_path}")

        try:
            self.client_search_input.wait_for(state="visible", timeout=30000)
            self.fill(self.client_search_input, client_id)
            logger.info(f"Filled client ID: {client_id}")
        except Exception as e:
            logger.error(f"Search input not found: {str(e).splitlines()[0]}")
            self.page.screenshot(
                path=f"reports/account_list_search_input_not_found_{client_id}.png"
            )
            raise Exception(f"Search input not found for client {client_id}")

        try:
            self.client_search_button.wait_for(state="visible", timeout=30000)
            self.click(self.client_search_button)
            logger.info("Clicked search button")
        except Exception as e:
            logger.error(f"Search button not found or not clickable: {str(e).splitlines()[0]}")
            self.page.screenshot(
                path=f"reports/account_list_search_button_not_found_{client_id}.png"
            )
            raise Exception(f"Search button not found or not clickable for client {client_id}")

        after_path = f"reports/account_list_after_search_{client_id}.png"
        self.page.screenshot(path=after_path)
        logger.info(f"Screenshot saved: {after_path}")

        logger.info(f"Search completed for client: {client_id}")

    def select_account(self, account_name: str, client_id: str = None) -> None:
        logger.info(f"Selecting account: {account_name} (Client ID: {client_id})")

        if client_id:
            try:
                row = self._get_client_row(client_id)
                logger.info(f"Found row with client ID: {client_id}")
                account_cell = row.locator(f"td:has-text('{account_name}')").first
                self.click(account_cell)
                logger.info(f"{account_name} account selected from client {client_id} row")
                return
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {str(e).splitlines()[0]}. Trying alternative approach.")

        try:
            logger.info("Strategy 2: Using role gridcell selector")
            account_cell = self._get_gridcell_by_name(account_name)
            self.click(account_cell)
            logger.info(f"{account_name} account selected using gridcell role")
            return
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {str(e).splitlines()[0]}. Trying final approach.")

        logger.info("Strategy 3: Using first occurrence of account name")
        account_cell = self._get_element_by_text(account_name)
        self.click(account_cell)
        logger.info(f"{account_name} account selected (first occurrence)")
