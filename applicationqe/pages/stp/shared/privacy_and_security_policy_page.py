"""
Privacy and Security Policy Page Object
"""

from playwright.sync_api import Locator, Page
from pages.stp.shared.base_page import BasePage
from pages.stp.shared.locators.privacy_and_security_policy_locators import PrivacyAndSecurityPolicyLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class PrivacyAndSecurityPolicyPage(BasePage):
    """Page object for Privacy and Security Policy Page"""
    
    PAGE_NAME = "Privacy and Security Policy Page"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        loc = PrivacyAndSecurityPolicyLocators
        # Page elements
        self.page_header = page.locator(loc.PAGE_HEADER)
        self.close_button = page.locator(loc.CLOSE_BUTTON)
        
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
