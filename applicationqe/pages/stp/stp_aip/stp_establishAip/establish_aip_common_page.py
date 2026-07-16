"""
Establish AIP Common Page Object - Shared functionality across Establish AIP pages
"""

from typing import List
from playwright.sync_api import Locator, Page
from pages.ewm.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_common_locators import EstablishAIPCommonLocators
from pages.ewm.privacy_and_security_policy_page import PrivacyAndSecurityPolicyPage
from pages.ewm.terms_of_use_page import TermsOfUsePage
from pages.ewm.supported_browsers_page import SupportedBrowsersPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPCommonPage(BasePage):
    """Common page object for shared Establish AIP functionality"""
    
    PAGE_NAME = "establishAIPCommonPage"
    
    def __init__(self, page: Page):
        super().__init__(page)
        ctx = self.active_root()
        loc = EstablishAIPCommonLocators
        
        # Bottom hyperlinks
        self.privacy_security_link = ctx.locator(loc.PRIVACY_SECURITY_LINK)
        self.terms_of_use_link = ctx.locator(loc.TERMS_OF_USE_LINK)
        self.supported_browsers_link = ctx.locator(loc.SUPPORTED_BROWSERS_LINK)
        self.bottom_hyperlinks_container = ctx.locator(loc.BOTTOM_HYPERLINKS_CONTAINER)
    
    def get_bottom_hyperlinks(self) -> List:
        """Get all bottom hyperlinks"""
        self.bottom_hyperlinks_container.first.wait_for(state='visible', timeout=10000)
        links = self.bottom_hyperlinks_container.all()
        logger.info(f"Found {len(links)} bottom hyperlinks")
        return links
    
    def click_privacy_and_security_policy_link(self):
        """Click Privacy and Security Policy link
        
        Returns:
            PrivacyAndSecurityPolicyPage instance
        """
        logger.info("Clicking Privacy And Security Policy Link")
        self.get_bottom_hyperlinks()[0].click()
        logger.info("Privacy And Security Policy Link --> Clicked")
        
        return PrivacyAndSecurityPolicyPage(self.page)
    
    def click_terms_of_use(self):
        """Click Terms of Use link
        
        Returns:
            TermsOfUsePage instance
        """
        logger.info("Clicking Terms Of Use Link")
        self.get_bottom_hyperlinks()[1].click()
        logger.info("Terms Of Use Link --> Clicked")
        
        return TermsOfUsePage(self.page)
    
    def click_supported_browsers(self):
        """Click Supported Browsers link
        
        Returns:
            SupportedBrowsersPage instance
        """
        logger.info("Clicking Supported Browsers Link")
        self.get_bottom_hyperlinks()[2].click()
        logger.info("Supported Browsers Link --> Clicked")
        
        return SupportedBrowsersPage(self.page)
