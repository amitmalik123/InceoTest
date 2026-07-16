from typing import Union

from playwright.sync_api import FrameLocator, Locator, Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from pages.ewm.locators.account_list_locators import AccountListLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AccountListPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountList"

    def __init__(self, context: Union[Page, FrameLocator]):
        if isinstance(context, Page):
            super().__init__(context)
            self.context = context
            self.page = context
        else:
            # Minimal init for FrameLocator compatibility (STP manage-bene flow).
            self.context = context
            self.page = None
            self.base_url = ""
            self.home_url = ""
            self.logger = logger

        loc = AccountListLocators
        self.client_search_input: Locator = context.locator(loc.SEARCH_INPUT)
        self.client_search_button: Locator = context.locator(loc.SEARCH_BUTTON)
        # Backward-compatible aliases used in some step definitions.
        self.search_input: Locator = self.client_search_input
        self.search_button: Locator = self.client_search_button

    def _get_client_row(self, client_id: str) -> Locator:
        return self.context.locator(f"tr:has-text('{client_id}')")

    def _get_gridcell_by_name(self, name: str) -> Locator:
        return self.context.get_by_role("gridcell", name=name).first

    def _get_element_by_text(self, text: str) -> Locator:
        return self.context.get_by_text(text).first

    def navigate(self) -> None:
        logger.info(f"Navigating to account list page: {self.PAGE_PATH}")
        if self.page:
            logger.info(f"Current URL before navigation: {self.page.url}")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"Current URL after wait: {self.page.url}")
        logger.info("Account list page loaded")

    def search_client(self, client_id: str, click_header: str = None) -> None:
        logger.info(f"Searching for client: {client_id}")

        if self.page:
            before_path = f"reports/account_list_before_search_{client_id}.png"
            self.page.screenshot(path=before_path)
            logger.info(f"Screenshot saved: {before_path}")

        search_successful = False

        try:
            self.client_search_input.wait_for(state="visible", timeout=30000)
            self.fill(self.client_search_input, client_id)
            logger.info(f"Filled client ID: {client_id}")

            self.client_search_button.wait_for(state="visible", timeout=30000)
            self.click(self.client_search_button)
            logger.info("Clicked search button")

            search_successful = True
        except Exception as e:
            logger.warning(f"Primary locator strategy failed: {str(e).splitlines()[0]}")

        if not search_successful:
            search_successful = self._fallback_search(client_id)

        if not search_successful:
            if self.page:
                self.page.screenshot(path=f"reports/account_list_failed_{client_id}.png")
            raise Exception(f"Unable to search for client {client_id} - all strategies failed")

        if self.page:
            after_path = f"reports/account_list_after_search_{client_id}.png"
            self.page.screenshot(path=after_path)
            logger.info(f"Screenshot saved: {after_path}")
        logger.info(f"Search completed for client: {client_id}")

    def search_account(self, account_number: str, click_header: str = None) -> None:
        """Search for an account by account number (delegates to search_client)."""
        logger.info(f"Searching for account: {account_number}")
        self.search_client(account_number, click_header=click_header)
        logger.info(f"Search completed for account: {account_number}")

    def _fallback_search(self, client_id: str) -> bool:
        """Fallback EWM strategies for environments where canonical locators fail."""
        try:
            logger.info("Fallback strategy 1: trying visible text inputs")
            inputs = self.page.locator(
                "input[type='text']:visible, input:not([type]):visible"
            ).all()
            for input_field in inputs:
                try:
                    placeholder = input_field.get_attribute("placeholder", timeout=1000) or ""
                    if "cookie" in placeholder.lower():
                        continue
                    if input_field.is_visible():
                        input_field.fill(client_id)
                        try:
                            search_btn = self.page.locator(
                                "button:has-text('Search'), button#searchbutton, button[type='submit']"
                            ).first
                            search_btn.wait_for(state="visible", timeout=3000)
                            search_btn.click()
                        except Exception:
                            input_field.press("Enter")
                        self.page.wait_for_load_state("networkidle", timeout=15000)
                        return True
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Fallback strategy 1 failed: {e}")

        try:
            logger.info("Fallback strategy 2: using URL query parameter")
            base = self.page.url.split(self.PAGE_PATH)[0] if self.PAGE_PATH in self.page.url else self.page.url.rsplit("/", 1)[0] + "/"
            search_url = f"{base}{self.PAGE_PATH}?search={client_id}"
            self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            return True
        except Exception as e:
            logger.warning(f"Fallback strategy 2 failed: {e}")

        try:
            logger.info("Fallback strategy 3: keyboard search")
            self.page.keyboard.press("Control+F")
            self.page.wait_for_timeout(1000)
            self.page.keyboard.type(client_id)
            self.page.keyboard.press("Enter")
            return True
        except Exception as e:
            logger.warning(f"Fallback strategy 3 failed: {e}")

        return False

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

