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

    def search_account(self, account_number: str) -> None:
        """Fill the search input with account_number and click GO. Used by ICT steps."""
        logger.info(f"Searching for account number: {account_number}")
        self.page.wait_for_load_state('networkidle', timeout=30000)
        search_input = self.page.locator(
            "input#client_search_input, input[id*='client_search_input'], "
            "input[name*='search'], input[placeholder*='Search']"
        ).first
        search_input.fill(account_number)
        go_button = self.page.locator("#searchbutton").first
        go_button.click()
        logger.info(f"GO clicked — searching for: {account_number}")
        # Wait for any Kendo grid loading mask to appear then disappear
        try:
            self.page.wait_for_selector('.k-loading-mask', state='visible', timeout=5000)
            logger.info("Grid loading mask appeared")
            self.page.wait_for_selector('.k-loading-mask', state='hidden', timeout=30000)
            logger.info("Grid loading mask disappeared — results ready")
        except Exception:
            # No loading mask (fast response or different indicator), fall back to networkidle
            self.page.wait_for_load_state('networkidle', timeout=30000)
            logger.info("Search results loaded (networkidle)")
        # Diagnostic: log iframes present and save screenshot
        try:
            frames = self.page.frames
            logger.info(f"Frames on page after search: {[f.url for f in frames]}")
            self.page.screenshot(path="reports/account_list_after_search.png")
            logger.info("Screenshot saved: reports/account_list_after_search.png")
        except Exception as diag_e:
            logger.warning(f"Diagnostic info failed: {diag_e}")

    def select_account(self, account_name: str, client_id: str = None) -> None:
        logger.info(f"Selecting account: {account_name} (Client ID: {client_id})")

        # Try on each frame (main page + any iframes)
        frames_to_try = [self.page] + list(self.page.frames)
        logger.info(f"Will search across {len(frames_to_try)} frame(s)")

        for frame_idx, frame in enumerate(frames_to_try):
            frame_url = getattr(frame, 'url', 'main')
            logger.info(f"Trying frame {frame_idx}: {frame_url}")

            # Strategy A: link with account name
            try:
                el = frame.locator(f"a:has-text('{account_name}')").first
                el.wait_for(state='visible', timeout=5000)
                el.click()
                logger.info(f"Account selected via link in frame {frame_idx}")
                return
            except Exception:
                pass

            # Strategy B: td cell with account name
            try:
                el = frame.locator(f"td:has-text('{account_name}')").first
                el.wait_for(state='visible', timeout=5000)
                el.click()
                logger.info(f"Account selected via td in frame {frame_idx}")
                return
            except Exception:
                pass

            # Strategy C: any element with the text
            try:
                el = frame.get_by_text(account_name, exact=False).first
                el.wait_for(state='visible', timeout=5000)
                el.click()
                logger.info(f"Account selected via text match in frame {frame_idx}")
                return
            except Exception:
                pass

        # Last resort: log page content snippet for debugging
        try:
            content_snippet = self.page.content()[:3000]
            logger.error(f"Could not find account. Page content snippet:\n{content_snippet}")
        except Exception:
            pass

        raise Exception(f"Could not find and click account '{account_name}' in any frame")

