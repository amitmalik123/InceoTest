"""
Establish Automatic Investment Plan (AIP) Landing Page Object
"""

from playwright.sync_api import Locator, Page
from pages.stp.shared.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_landing_locators import EstablishAIPLandingLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPLandingPage(BasePage):
    """Page object for Establish AIP Landing Page"""
    
    PAGE_NAME = "Establish AIP Landing Page"
    
    def __init__(self, page: Page):
        super().__init__(page)
        loc = EstablishAIPLandingLocators
        
        # Header elements
        self.header = page.locator(loc.HEADER)
        self.title_section = page.locator(loc.TITLE_SECTION)
        
        # Landing Page Action Buttons
        self.add_button = page.locator(loc.ADD_BUTTON)
        self.cancel_button = page.locator(loc.CANCEL_BUTTON)
        self.next_button = page.locator(loc.NEXT_BUTTON)
        
        # Account Information section
        self.account_info_label = page.locator(loc.ACCOUNT_INFO_LABEL)
        self.account_info_text = page.locator(loc.ACCOUNT_INFO_TEXT)
        self.market_value = page.locator(loc.MARKET_VALUE)
        self.cash_available = page.locator(loc.CASH_AVAILABLE)
        
        # AIP Plans section
        self.select_aip = page.locator(loc.SELECT_AIP)
        self.hard_stop_message = page.locator(loc.HARD_STOP_MESSAGE)
        self.active_aip_list = page.locator(loc.ACTIVE_AIP_LIST)
        
        # Loading indicators
        self.spinner_loading = page.locator(loc.SPINNER_LOADING)
        self.loading_overlay = page.locator(loc.LOADING_OVERLAY)
    
    def wait_for_page_load(self, page_verification: bool = True) -> None:
        """Wait for Establish AIP Landing Page to load
        
        Args:
            page_verification: If True, verify page elements after load
        """
        logger.info("Waiting for Establish AIP Landing Page to load")
        
        # Wait for spinner to disappear if present
        try:
            if self.spinner_loading.count() > 0:
                self.spinner_loading.wait_for(state='hidden', timeout=120000)
                logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.warning(f"Spinner wait failed: {e}")
        
        # Wait for loading overlay to disappear if present
        try:
            if self.loading_overlay.count() > 0:
                self.loading_overlay.wait_for(state='hidden', timeout=120000)
                logger.info("Loading overlay disappeared")
        except Exception as e:
            logger.warning(f"Loading overlay wait failed: {e}")
        
        self.page.wait_for_timeout(500)
        
        # Page verification
        if page_verification:
            is_header = self.is_visible(self.header, timeout=5000)
            is_title_section = self.is_visible(self.title_section, timeout=5000)
            
            if is_header and is_title_section:
                logger.info(f"{self.PAGE_NAME} verification --> {self.PAGE_NAME} verification is PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification --> {self.PAGE_NAME} verification is FAILED")
    
    def verify_page_loaded(self) -> bool:
        """Verify Establish AIP Landing Page is loaded"""
        try:
            self.title_section.wait_for(state='visible', timeout=10000)
            logger.info("Establish AIP Landing Page verification PASSED")
            return True
        except Exception as e:
            logger.warning(f"Establish AIP Landing Page verification FAILED: {e}")
            return False
    
    def is_aip_displayed(self) -> bool:
        """Check if AIP is displayed on the page"""
        return self.is_visible(self.select_aip, timeout=10000)
    
    def is_hard_stop_message_displayed(self) -> bool:
        """Check if hard stop message is displayed"""
        return self.is_visible(self.hard_stop_message, timeout=10000)
    
    def no_aip_on_account(self) -> str:
        """Get hard stop message text if no AIP found on account
        
        Returns:
            Hard stop message text if displayed, empty string otherwise
        """
        if self.is_hard_stop_message_displayed():
            return self.get_text(self.hard_stop_message)
        return ""
    
    def get_account_information_text(self) -> str:
        """Get account information text from the landing page"""
        logger.info("Getting account information text")
        
        # Wait for account info label to be visible
        self.account_info_label.wait_for(state='visible', timeout=10000)
        
        # Get the account info text
        account_info = self.get_text(self.account_info_text)
        logger.info(f"Account Information: {account_info}")
        
        return account_info
    
    def verify_account_information(self, expected_info: str) -> bool:
        """Verify account information matches expected value
        
        Args:
            expected_info: Expected account information text
            
        Returns:
            True if account info matches, False otherwise
        """
        logger.info(f"Verifying account information matches: {expected_info}")
        
        actual_info = self.get_account_information_text()
        
        # Compare
        matches = expected_info.strip() in actual_info.strip() or actual_info.strip() in expected_info.strip()
        
        if matches:
            logger.info(f"[OK] Account Information verification PASSED")
        else:
            logger.error(f"[FAIL] Account Information verification FAILED")
            logger.error(f"  Expected: {expected_info}")
            logger.error(f"  Actual: {actual_info}")
        
        return matches
    
    def click_add_button(self):
        """Click on ADD button to add a new AIP and navigate to Origination Selection Page
        
        Returns:
            EstablishAIPOriginationSelectionPage instance
        """
        from establish_aip_origination_selection_page import EstablishAIPOriginationSelectionPage
        
        logger.info("Clicking on ADD button")
        
        # Wait for button to be clickable
        self.add_button.wait_for(state='visible', timeout=5000)
        
        # Scroll into view
        self.add_button.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        
        # Click the button
        self.click(self.add_button)
        logger.info("Clicking Add Button--> Clicked")
        
        # Return next page object
        return EstablishAIPOriginationSelectionPage(self.page)
    
    def click_cancel_button(self) -> None:
        """Click on Cancel button"""
        logger.info("Clicking on Cancel button")
        
        self.cancel_button.wait_for(state='visible', timeout=10000)
        self.cancel_button.click()
        self.page.wait_for_timeout(1000)
        
        logger.info("Cancel button clicked")
    
    def click_next_button(self) -> None:
        """Click on NEXT button"""
        logger.info("Clicking on NEXT button")
        
        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()
        self.page.wait_for_timeout(2000)
        
        logger.info("NEXT button clicked")
    
    def get_account_info_header(self) -> str:
        """Get account information header text"""
        self.account_info_label.wait_for(state='visible')
        account_info_header = self.account_info_label.text_content()
        logger.info(f"Account Information Header: {account_info_header}")
        return account_info_header
    
    def get_market_value(self) -> str:
        """Get market value text"""
        self.market_value.wait_for(state='visible', timeout=10000)
        market_value = self.market_value.text_content()
        logger.info(f"Market Value: {market_value}")
        return market_value
    
    def get_cash_available(self) -> str:
        """Get cash available text"""
        self.cash_available.wait_for(state='visible', timeout=10000)
        cash_available = self.cash_available.text_content()
        logger.info(f"Cash Available: {cash_available}")
        return cash_available
    
    def validate_buttons_present(self) -> bool:
        """Validate ADD and Cancel buttons are present"""
        add_present = self.add_button.is_visible()
        cancel_present = self.cancel_button.is_visible()
        
        logger.info(f"ADD button present: {add_present}")
        logger.info(f"Cancel button present: {cancel_present}")
        
        return add_present and cancel_present
    
    def get_hard_stop_message_text(self) -> str:
        """Get hard stop message text when no AIPs found"""
        self.hard_stop_message.wait_for(state='visible', timeout=5000)
        message = self.hard_stop_message.text_content()
        logger.info(f"Hard Stop Message: {message}")
        return message
    
    def get_header_text(self) -> str:
        """Get page header text"""
        self.header.wait_for(state='visible', timeout=10000)
        header_text = self.header.text_content()
        logger.info(f"Header: {header_text}")
        return header_text
    
    def select_first_aip(self) -> str:
        """Select first AIP from the list"""
        self.select_aip.wait_for(state='visible', timeout=10000)
        aip_text = self.select_aip.text_content()
        self.select_aip.click()
        logger.info(f"Selected AIP: {aip_text}")
        return aip_text
