"""
Request Summary Page Object - Request summary display and navigation actions
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from typing import Dict, Any, Optional, List

class RequestSummaryPage(BasePage):
    """Page object for request summary display and navigation actions"""

    def __init__(self, page: Page):
        super().__init__(page)

    def wait_for_summary_page_load(self, expected_headings: List[str] = None) -> None:
        """
        Wait for request summary page to load with expected headings
        Args:
            expected_headings: List of headings to wait for (optional)
        """
        self.logger.info("Waiting for request summary page to load")
        self.wait_for_load_state("domcontentloaded")
        
        # Default headings to look for
        if not expected_headings:
            expected_headings = [
                "Request Summary",
                "Transaction Summary", 
                "Summary",
                "Request Details"
            ]
        
        # Wait for at least one summary heading to appear
        for heading in expected_headings:
            try:
                if self.page.get_by_text(heading).first.is_visible(timeout=5000):
                    self.logger.info(f"Summary page loaded with heading: '{heading}'")
                    return
            except:
                continue
                
        self.logger.warning("No standard summary headings found, but page may have loaded")

    def click_edit_button(self, section: str = None) -> None:
        """
        Click edit button for a specific section or general edit
        Args:
            section: Specific section to edit (optional)
        """
        try:
            if section:
                # Look for section-specific edit button
                edit_button = self.page.locator(f"button:has-text('Edit'):near(text='{section}')")
            else:
                # Look for any edit button
                edit_button = self.page.get_by_role("button", name="Edit").first
                
            if edit_button.is_visible(timeout=5000):
                self.logger.info(f"Clicking edit button{' for ' + section if section else ''}")
                edit_button.click()
                self.wait_for_load_state("networkidle")
            else:
                self.logger.warning(f"Edit button not found{' for ' + section if section else ''}")
                
        except Exception as e:
            self.logger.error(f"Failed to click edit button: {e}")

    def click_continue_button(self) -> None:
        """Click continue/proceed button from summary page"""
        try:
            continue_selectors = [
                "button:has-text('Continue')",
                "button:has-text('Proceed')",
                "button:has-text('Next')",
                "button:has-text('Submit')"
            ]
            
            for selector in continue_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        self.logger.info(f"Clicking continue button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
            self.logger.warning("No continue/proceed button found")
            
        except Exception as e:
            self.logger.error(f"Failed to click continue button: {e}")

    def click_submit_button(self) -> None:
        """Click final submit button to process the request"""
        try:
            submit_selectors = [
                "button:has-text('Submit')",
                "button:has-text('Submit Request')", 
                "button:has-text('Process Request')",
                "input[type='submit']"
            ]
            
            for selector in submit_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000) and button.is_enabled():
                        self.logger.info(f"Clicking submit button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
            self.logger.warning("No submit button found or enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to click submit button: {e}")

    def click_back_button(self) -> None:
        """Click back button to return to previous page"""
        try:
            back_selectors = [
                "button:has-text('Back')",
                "button:has-text('Previous')",
                "a:has-text('Back')"
            ]
            
            for selector in back_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        self.logger.info(f"Clicking back button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Back button not found: {e}")

    def get_displayed_account_info(self) -> Dict[str, Any]:
        """
        Extract account information displayed on summary page
        Returns:
            Dictionary with source and destination account details
        """
        account_info = {
            "source_account": {},
            "destination_account": {}
        }
        
        try:
            # Look for account number patterns
            account_elements = self.page.locator("text=/\\d{4}-\\d{4}-\\d{4}/")
            
            for i in range(min(2, account_elements.count())):  # Get up to 2 accounts
                account_text = account_elements.nth(i).text_content()
                account_key = "source_account" if i == 0 else "destination_account"
                account_info[account_key]["number"] = account_text
                
                # Try to find associated account name
                try:
                    parent = account_elements.nth(i).locator("..")
                    account_info[account_key]["name"] = parent.text_content().strip()
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Could not extract account information: {e}")
            
        return account_info

    def get_displayed_amount(self) -> Optional[str]:
        """
        Extract transfer amount displayed on summary page
        Returns:
            Transfer amount string or None if not found
        """
        try:
            # Look for dollar amount patterns
            amount_selectors = [
                "text=/\\$[\\d,]+\\.\\d{2}/",  # $1,000.00 format
                "text=/\\$[\\d,]+/",          # $1,000 format  
                "*:has-text('Amount') + *",   # Element after "Amount" label
                "*:has-text('$')"             # Any element containing $
            ]
            
            for selector in amount_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        amount_text = element.text_content().strip()
                        if '$' in amount_text:
                            self.logger.info(f"Found amount: {amount_text}")
                            return amount_text
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Could not extract amount: {e}")
            
        return None

    def scroll_to_section(self, section_name: str) -> None:
        """
        Scroll to a specific section on the summary page
        Args:
            section_name: Name of section to scroll to
        """
        try:
            section_element = self.page.get_by_text(section_name).first
            if section_element.is_visible():
                section_element.scroll_into_view_if_needed()
                self.logger.info(f"Scrolled to section: {section_name}")
        except Exception as e:
            self.logger.warning(f"Could not scroll to section '{section_name}': {e}")

    def expand_details_section(self, section_name: str) -> None:
        """
        Expand a collapsible details section if present
        Args:
            section_name: Name of section to expand
        """
        try:
            # Look for expand buttons or collapsible sections
            expand_selectors = [
                f"button:near(text='{section_name}'):has-text('Details')",
                f"button:near(text='{section_name}'):has-text('Show')",
                f"button:near(text='{section_name}'):has-text('Expand')",
                f"*:has-text('{section_name}') >> button"
            ]
            
            for selector in expand_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        self.logger.info(f"Expanded section: {section_name}")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"No expandable section found for '{section_name}': {e}")
