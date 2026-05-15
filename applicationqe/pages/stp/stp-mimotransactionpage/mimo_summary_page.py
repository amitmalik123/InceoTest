"""
Page Object Model for MIMO Transaction Summary Page.
This page appears after clicking Next on MIMO Transaction Request Page 2.
Contains summary sections like Request Details, QUALIFIED INFORMATION, etc.
"""
from typing import Dict, List
from playwright.sync_api import Page
from pages.stp.shared.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOSummaryPage(BasePage):
    """MIMO Transaction Summary Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        
        # Main page identifier
        self.transaction_summary_title = page.locator("//h3[@class='section-title' and text()='Transaction summary']")
        
        # Submit buttons
        self.submit_button = page.locator("//button[@data-testid='submit-button']")
        self.submit_review_button = page.locator("//button[@data-testid='submit-to-review-button']")
        self.back_button = page.locator("//button[@data-testid='back-button']")
        
        # Qualified Information section locators
        self.qualified_info_values = page.locator(
            "//h3[text()='QUALIFIED INFORMATION']//parent::div//div[@aria-label='category-group-item']//h4[@aria-label='category-group-item-value']"
        )
        
        logger.info("MIMO Summary Page initialized")

    def get_summary_page_details(self, category_name: str) -> Dict[str, str]:
        """
        Get all field name-value pairs from a category section.
        
        Args:
            category_name: The category section name (e.g., "QUALIFIED INFORMATION", "Request Details")
            
        Returns:
            Dictionary mapping field names to their values
            
        Example:
            {"Distribution Reason": "First Distribution", 
             "Federal Tax Withholding": "Waived",
             "State Tax Withholding": "Waived",
             "State": "CA",
             "Net Distribution Amount": "$1,000"}
        """
        logger.info(f"Getting summary page details for category: {category_name}")
        
        xpath = f"//h3[text()='{category_name}']//following-sibling::div//h4"
        category_elements = self.page.locator(xpath)
        
        # Scroll to make visible
        if category_elements.count() > 0:
            category_elements.first.scroll_into_view_if_needed()
        
        # Wait for elements to be visible
        category_elements.first.wait_for(state="visible", timeout=10000)
        
        # Get all text values
        all_texts = category_elements.all_text_contents()
        
        # Convert list to dictionary (field name, field value pairs)
        details = {}
        for i in range(0, len(all_texts), 2):
            if i + 1 < len(all_texts):
                field_name = all_texts[i]
                field_value = all_texts[i + 1]
                details[field_name] = field_value
                logger.info(f"  {field_name}: {field_value}")
        
        return details

    def summary_page_qualified_values(self) -> List:
        """
        Get the WebElement list of qualified information values.
        
        Returns:
            List of Playwright Locator objects for each value field
        """
        logger.info("Getting qualified information value elements")
        
        self.qualified_info_values.first.wait_for(state="visible", timeout=10000)
        
        # Return all locators as a list
        count = self.qualified_info_values.count()
        elements = [self.qualified_info_values.nth(i) for i in range(count)]
        
        logger.info(f"Found {count} qualified information value elements")
        return elements

    def list_string_summary_page_qualified_values(self) -> List[str]:
        """
        Get the text content of all qualified information values as a string list.
        
        Returns:
            List of strings containing the text of each value field
            [Distribution Reason text, Federal Tax text, State Tax text, State text, Net Amount text]
        """
        logger.info("Getting qualified information values as string list")
        
        self.qualified_info_values.first.wait_for(state="visible", timeout=10000)
        
        # Get all text contents
        values = self.qualified_info_values.all_text_contents()
        
        logger.info(f"Qualified information values: {values}")
        return values

    def click_submit_button(self) -> None:
        """Click the Submit button to submit the transaction"""
        logger.info("Clicking Submit button in MIMO Summary Page")
        
        self.submit_button.wait_for(state="visible", timeout=10000)
        self.submit_button.click()
        
        logger.info("Submit button clicked")

    def click_submit_for_review_button(self) -> None:
        """Click the Submit for Review button"""
        logger.info("Clicking Submit for Review button in MIMO Summary Page")
        
        self.submit_review_button.wait_for(state="visible", timeout=10000)
        self.submit_review_button.click()
        
        logger.info("Submit for Review button clicked")

    def click_back_button(self) -> None:
        """Click the Back button to return to previous page"""
        logger.info("Clicking Back button in MIMO Summary Page")
        
        self.back_button.wait_for(state="visible", timeout=10000)
        self.back_button.click()
        
        logger.info("Back button clicked")
