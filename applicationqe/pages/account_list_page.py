from typing import Optional

from playwright.sync_api import Page

from locators import account_list_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountListPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountList"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

    def navigate(self) -> None:
        logger.info(f"Navigating to account list page: {self.base_url}{self.PAGE_PATH}")
        logger.info(f"Current URL before navigation: {self.page.url}")
        self.page.wait_for_load_state("domcontentloaded", timeout=120000)
        logger.info(f"Current URL after wait: {self.page.url}")
        logger.info("Account list page loaded")

    def search_client(self, client_id: str, click_header: Optional[str] = None) -> None:
        logger.info(f"Searching for client: {client_id}")

        try:
            search_input = self.page.locator(account_list_locators.ACCOUNT_SEARCH_INPUT)
            search_input.wait_for(state="visible", timeout=120000)
            self.fill(search_input, client_id)
            logger.info(f"Filled client ID: {client_id}")
        except Exception as e:
            logger.error(f"Search input not found: {e}")
            self.page.screenshot(
                path=f"reports/account_list_search_input_not_found_{client_id}.png"
            )
            raise Exception(f"Search input not found for client {client_id}")

        try:
            search_button = self.page.locator(account_list_locators.ACCOUNT_SEARCH_BUTTON)
            search_button.wait_for(state="visible", timeout=120000)
            self.click(search_button)
            logger.info("Clicked search button")
        except Exception as e:
            logger.error(f"Search button not found or not clickable: {e}")
            self.page.screenshot(
                path=f"reports/account_list_search_button_not_found_{client_id}.png"
            )
            raise Exception(f"Search button not found or not clickable for client {client_id}")

        after_path = f"reports/account_list_after_search_{client_id}.png"
        self.page.screenshot(path=after_path)
        logger.info(f"Screenshot saved: {after_path}")

        logger.info(f"Search completed for client: {client_id}")

    def search_account(self, account_number: str, click_header: Optional[str] = None) -> None:
        logger.info(f"Searching for account: {account_number}")

        try:
            search_input = self.page.locator(account_list_locators.ACCOUNT_SEARCH_INPUT)
            search_input.wait_for(state="visible", timeout=120000)
            self.fill(search_input, account_number)
            logger.info(f"Filled account number: {account_number}")
        except Exception as e:
            logger.error(f"Search input not found: {e}")
            self.page.screenshot(
                path=f"reports/account_list_search_input_not_found_{account_number}.png"
            )
            raise Exception(f"Search input not found for account {account_number}")

        try:
            search_button = self.page.locator(account_list_locators.ACCOUNT_SEARCH_BUTTON)
            search_button.wait_for(state="visible", timeout=120000)
            self.click(search_button)
            logger.info("Clicked search button")
        except Exception as e:
            logger.error(f"Search button not found or not clickable: {e}")
            self.page.screenshot(
                path=f"reports/account_list_search_button_not_found_{account_number}.png"
            )
            raise Exception(f"Search button not found or not clickable for account {account_number}")

        after_path = f"reports/account_list_after_search_{account_number}.png"
        self.page.screenshot(path=after_path)
        logger.info(f"Screenshot saved: {after_path}")

        logger.info(f"Search completed for account: {account_number}")

    def select_account(self, account_name: str, client_id: Optional[str] = None) -> None:
        logger.info(f"Selecting account: {account_name} (Client ID: {client_id})")

        if client_id:
            try:
                row = self.page.locator(f"tr:has-text('{client_id}')")
                logger.info(f"Found row with client ID: {client_id}")
                account_cell = row.locator(f"td:has-text('{account_name}')").first
                self.click(account_cell)
                logger.info(f"{account_name} account selected from client {client_id} row")
                return
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {e}. Trying alternative approach.")

        try:
            logger.info("Strategy 2: Using role gridcell selector")
            account_cell = self.page.get_by_role("gridcell", name=account_name).first
            self.click(account_cell)
            logger.info(f"{account_name} account selected using gridcell role")
            return
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}. Trying final approach.")

        logger.info("Strategy 3: Using first occurrence of account name")
        account_cell = self.page.get_by_text(account_name).first
        self.click(account_cell)
        logger.info(f"{account_name} account selected (first occurrence)")
