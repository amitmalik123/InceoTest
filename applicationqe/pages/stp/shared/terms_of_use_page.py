"""
Terms of Use Page Object
"""

from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class TermsOfUsePage(BasePage):
    """Page object for Terms of Use Page"""
    
    PAGE_NAME = "Terms of Use Page"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        
        # Page elements
        self.page_header = page.locator("//h1[text()='Terms of Use'] | //h1[contains(text(),'Terms')]")
        self.close_button = page.locator("//button[@aria-label='close-button']")
        
        # Page verification
        if page_verification:
            is_visible = self.is_element_visible(self.page_header, timeout=45000)
            
            if is_visible:
                logger.info(f"{self.PAGE_NAME} verification : {self.PAGE_NAME} verification is PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification is FAILED")
    
    def click_close_button(self):
        """Click close button and return to previous page
        
        Returns:
            Page instance (caller should handle appropriate page)
        """
        logger.info("Clicking Close Button")
        self.close_button.wait_for(state='visible', timeout=10000)
        self.close_button.click()
        logger.info("Clicking Close Button--> Clicked")
        
        # Return the page object for method chaining
        return self.page
