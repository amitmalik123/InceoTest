from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AccountListPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/AccountsAnalysis/Clients/AccountList'

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate(self) -> None:
        logger.info(f"Navigating to account list page: {self.PAGE_URL}")
        logger.info(f"Current URL before navigation: {self.page.url}")
        # Wait for account list navigation to complete
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        logger.info(f"Current URL after wait: {self.page.url}")
        logger.info("Account list page loaded")

    def search_client(self, client_id: str) -> None:
        logger.info(f"Searching for client: {client_id}")
        
        # Take screenshot for debugging
        screenshot_path = f"reports/account_list_debug_{client_id}.png"
        self.page.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Try multiple search strategies
        search_successful = False
        
        # Strategy 1: Look for any visible text input that might be the search
        try:
            logger.info("Strategy 1: Trying visible text inputs")
            inputs = self.page.locator('input[type="text"]:visible, input:not([type]):visible').all()
            logger.info(f"Found {len(inputs)} visible input fields")
            
            for idx, input_field in enumerate(inputs):
                try:
                    placeholder = input_field.get_attribute('placeholder', timeout=1000)
                    input_id = input_field.get_attribute('id', timeout=1000)
                    logger.info(f"Input {idx}: id='{input_id}', placeholder='{placeholder}'")
                    
                    # Skip cookie search
                    if placeholder and 'cookie' in placeholder.lower():
                        continue
                    
                    # Try to use this input
                    if input_field.is_visible():
                        logger.info(f"Attempting to use input {idx}")
                        input_field.fill(client_id)
                        logger.info(f"Filled input with: {client_id}")
                        
                        # Try to find and click search button nearby
                        try:
                            search_btn = self.page.locator('button:has-text("Search"), button#searchbutton, button[type="submit"]').first
                            search_btn.wait_for(state='visible', timeout=3000)
                            search_btn.click()
                            logger.info("Clicked search button")
                        except Exception as e:
                            logger.info(f"No search button found, pressing Enter: {e}")
                            input_field.press('Enter')
                        
                        search_successful = True
                        break
                except Exception as e:
                    logger.debug(f"Input {idx} check failed: {e}")
                    continue
        except Exception as e:
            logger.error(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Try direct URL navigation with query parameter
        if not search_successful:
            try:
                logger.info("Strategy 2: Using URL with search parameter")
                search_url = f"{self.PAGE_URL}?search={client_id}"
                self.page.goto(search_url, wait_until='networkidle', timeout=30000)
                logger.info(f"Navigated to: {search_url}")
                search_successful = True
            except Exception as e:
                logger.error(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Use keyboard shortcut (Ctrl+F or /) to open search
        if not search_successful:
            try:
                logger.info("Strategy 3: Trying keyboard shortcuts")
                self.page.keyboard.press('Control+F')
                self.page.wait_for_timeout(1000)
                self.page.keyboard.type(client_id)
                self.page.keyboard.press('Enter')
                logger.info("Used keyboard shortcut to search")
                search_successful = True
            except Exception as e:
                logger.error(f"Strategy 3 failed: {e}")
        
        if search_successful:
            # Wait for results
            self.page.wait_for_load_state('networkidle', timeout=15000)
            logger.info(f"Search completed for client: {client_id}")
        else:
            logger.error("All search strategies failed!")
            # Take another screenshot after attempts
            self.page.screenshot(path=f"reports/account_list_failed_{client_id}.png")
            raise Exception(f"Unable to search for client {client_id} - all strategies failed")

    def select_account(self, account_name: str, client_id: str = None) -> None:
        logger.info(f"Selecting account: {account_name} (Client ID: {client_id})")
        
        # Strategy 1: Try to find by both account name and client ID in the same row
        if client_id:
            try:
                # Find the row that contains the client ID
                row = self.page.locator(f"tr:has-text('{client_id}')")
                logger.info(f"Found row with client ID: {client_id}")
                
                # Within that row, click the cell with the account name
                account_cell = row.locator(f"td:has-text('{account_name}')").first
                account_cell.click()
                logger.info(f"{account_name} account selected from client {client_id} row")
                return
            except Exception as e:
                logger.warning(f"Strategy 1 failed: {e}. Trying alternative approach.")
        
        # Strategy 2: Fallback - use role gridcell with account name
        try:
            logger.info("Strategy 2: Using role gridcell selector")
            account_cell = self.page.get_by_role("gridcell", name=account_name).first
            account_cell.click()
            logger.info(f"{account_name} account selected using gridcell role")
            return
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}. Trying final approach.")
        
        # Strategy 3: Final fallback - get first occurrence
        logger.info("Strategy 3: Using first occurrence of account name")
        account_cell = self.page.get_by_text(account_name).first
        account_cell.click()
        logger.info(f"{account_name} account selected (first occurrence)")

