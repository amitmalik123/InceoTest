"""
Review Summary Page Object - Review and approval actions
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.ewm.locators.review_summary_locators import ReviewSummaryLocators
from typing import Dict, Any, Optional

class ReviewSummaryPage(BasePage):
    """Page object for review summary and approval actions"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ReviewSummaryLocators()

    def wait_for_review_page_load(self, timeout: int = 30000) -> None:
        """Wait for review summary page to load completely"""
        self.logger.info("Waiting for review summary page to load")
        self.wait_for_load_state("domcontentloaded", timeout=timeout)
        
        # Wait for review-specific elements
        review_indicators = [
            "Review",
            "Summary", 
            "Confirmation",
            "Please review"
        ]
        
        for indicator in review_indicators:
            try:
                if self.page.get_by_text(indicator).first.is_visible(timeout=5000):
                    self.logger.info(f"Review page loaded with indicator: '{indicator}'")
                    return
            except:
                continue
                
        self.logger.info("Review page loaded (no specific indicators found)")

    def click_approve_button(self) -> None:
        """Click approve button to approve the request"""
        try:
            approve_selectors = [
                "button:has-text('Approve')",
                "button:has-text('Accept')",
                "button:has-text('Confirm')",
                "input[value='Approve']"
            ]
            
            for selector in approve_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000) and button.is_enabled():
                        self.logger.info(f"Clicking approve button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
            self.logger.warning("No approve button found or enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to click approve button: {e}")

    def click_reject_button(self) -> None:
        """Click reject button to reject the request"""
        try:
            reject_selectors = [
                "button:has-text('Reject')",
                "button:has-text('Decline')",
                "button:has-text('Cancel')",
                "input[value='Reject']"
            ]
            
            for selector in reject_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000) and button.is_enabled():
                        self.logger.info(f"Clicking reject button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to click reject button: {e}")

    def add_review_comment(self, comment: str) -> None:
        """
        Add a comment during the review process
        Args:
            comment: Comment text to add
        """
        try:
            comment_selectors = [
                "textarea[placeholder*='comment']",
                "textarea[name*='comment']",
                "textarea[id*='comment']",
                "input[placeholder*='comment']",
                "*:has-text('Comment') + textarea",
                "*:has-text('Notes') + textarea"
            ]
            
            for selector in comment_selectors:
                try:
                    comment_field = self.page.locator(selector).first
                    if comment_field.is_visible(timeout=3000):
                        self.logger.info("Adding review comment")
                        comment_field.clear()
                        comment_field.fill(comment)
                        return
                except:
                    continue
                    
            self.logger.warning("No comment field found")
            
        except Exception as e:
            self.logger.error(f"Failed to add review comment: {e}")

    def click_submit_review_button(self) -> None:
        """Click submit button to finalize the review"""
        try:
            submit_selectors = [
                "button:has-text('Submit Review')",
                "button:has-text('Submit')",
                "button:has-text('Complete Review')",
                "button:has-text('Finalize')"
            ]
            
            for selector in submit_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000) and button.is_enabled():
                        self.logger.info(f"Clicking submit review button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to click submit review button: {e}")

    def select_review_option(self, option: str) -> None:
        """
        Select a review option from radio buttons or dropdown
        Args:
            option: Review option to select (e.g., "Approve", "Require Changes")
        """
        try:
            # Try radio buttons first
            radio_button = self.page.get_by_role("radio", name=option)
            if radio_button.is_visible(timeout=3000):
                self.logger.info(f"Selecting review option (radio): {option}")
                radio_button.check()
                return
                
            # Try dropdown/select
            select_element = self.page.locator("select").first
            if select_element.is_visible(timeout=3000):
                self.logger.info(f"Selecting review option (dropdown): {option}")
                select_element.select_option(label=option)
                return
                
            # Try clickable option buttons
            option_button = self.page.get_by_role("button", name=option)
            if option_button.is_visible(timeout=3000):
                self.logger.info(f"Selecting review option (button): {option}")
                option_button.click()
                return
                
            self.logger.warning(f"Review option '{option}' not found")
            
        except Exception as e:
            self.logger.error(f"Failed to select review option '{option}': {e}")

    def get_review_summary_details(self) -> Dict[str, Any]:
        """
        Extract review summary details displayed on page
        Returns:
            Dictionary with review details
        """
        details = {
            "timestamp": self.page.evaluate("() => new Date().toISOString()"),
            "url": self.page.url,
            "request_type": None,
            "amount": None,
            "accounts": {}
        }
        
        try:
            # Extract request type
            type_patterns = [
                "Journal Transfer",
                "Account Transfer", 
                "Securities Transfer"
            ]
            
            for pattern in type_patterns:
                if self.page.get_by_text(pattern).first.is_visible(timeout=1000):
                    details["request_type"] = pattern
                    break
                    
            # Extract amount if visible
            amount_element = self.page.locator("text=/\\$[\\d,]+\\.?\\d*/").first
            if amount_element.is_visible(timeout=1000):
                details["amount"] = amount_element.text_content()
                
            # Extract account information
            account_elements = self.page.locator("text=/\\d{4}-\\d{4}/")
            for i in range(min(2, account_elements.count())):
                account_key = "source" if i == 0 else "destination"
                details["accounts"][account_key] = account_elements.nth(i).text_content()
                
        except Exception as e:
            self.logger.warning(f"Could not extract all review details: {e}")
            
        return details

    def verify_signatures_section(self) -> bool:
        """
        Verify if e-signature or signature section is visible
        Returns:
            True if signatures section found, False otherwise
        """
        try:
            signature_indicators = [
                "Signature",
                "E-Signature", 
                "Digital Signature",
                "DocuSign",
                "Electronic Signature"
            ]
            
            for indicator in signature_indicators:
                if self.page.get_by_text(indicator).first.is_visible(timeout=2000):
                    self.logger.info(f"Signatures section found: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not verify signatures section: {e}")
            return False

    def scroll_to_review_buttons(self) -> None:
        """Scroll to the review action buttons at bottom of page"""
        try:
            # Look for review buttons and scroll to them
            button_selectors = [
                "button:has-text('Approve')",
                "button:has-text('Submit')",
                "button:has-text('Confirm')"
            ]
            
            for selector in button_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible():
                        button.scroll_into_view_if_needed()
                        self.logger.info("Scrolled to review buttons")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Could not scroll to review buttons: {e}")
