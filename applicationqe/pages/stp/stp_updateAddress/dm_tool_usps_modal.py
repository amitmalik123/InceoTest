"""
DM Tool USPS Address Validation Modal Page Object
"""

from typing import List, TYPE_CHECKING
from playwright.sync_api import Page

from pages.ewm.base_page import BasePage
from utils.logger import setup_logger
from utils.address_comparison import check_if_there_is_address_match

if TYPE_CHECKING:
    from pages.stp.stp_updateAddress.dmtool_page import DMToolPage

logger = setup_logger(__name__)


class DMToolUSPSModal(BasePage):
    """Page object for USPS Address Validation Modal"""
    
    PAGE_NAME = "USPS Address Validation Modal"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Modal elements
        self.modal_title = "//h2[contains(text(),'Address Validation')]"
        self.modal_container = "//div[@role='dialog' and contains(@aria-label,'usps')]"
        
        # Address display sections
        self.original_address_section = "//div[@aria-label='original-address-section']"
        self.suggested_address_section = "//div[@aria-label='suggested-address-section']"
        
        # Original address elements
        self.original_address_line1 = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-1']"
        self.original_address_line2 = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-2']"
        self.original_address_city_state_zip = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-city-state-zip']"
        
        # Suggested address elements
        self.suggested_address_line1 = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-1']"
        self.suggested_address_line2 = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-2']"
        self.suggested_address_city_state_zip = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-city-state-zip']"
        
        # Radio buttons for address selection
        self.use_original_radio = "//input[@type='radio' and @value='original']"
        self.use_suggested_radio = "//input[@type='radio' and @value='suggested']"
        
        # Error message
        self.error_message = "//div[@aria-label='usps-error-message']"
        
        # Action buttons
        self.save_button = "//button[text()='Save']"
        self.back_button = "//button[text()='Back']"
        self.cancel_button = "//button[text()='Cancel']"
    
    def wait_for_modal_to_load(self) -> None:
        """Wait for USPS Address Validation Modal to be visible"""
        logger.info("Waiting for USPS Address Validation Modal to load")
        try:
            self.page.wait_for_selector(self.modal_title, timeout=10000)
            logger.info("USPS Address Validation Modal loaded")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            logger.error(f"Error waiting for USPS modal: {e}")
            raise
    
    def click_save(self) -> 'DMToolPage':
        """Click the Save button to confirm address selection
        
        Returns:
            DMToolPage instance
        """
        from pages.stp.stp_updateAddress.dmtool_page import DMToolPage  # deferred: circular dependency

        logger.info(f"{self.PAGE_NAME}: Clicking save")
        try:
            save_btn = self.page.locator(self.save_button)
            save_btn.wait_for(state='visible', timeout=10000)
            save_btn.click()
            logger.info(f"{self.PAGE_NAME}: Save button clicked")
            
            self.page.wait_for_timeout(3000)
            
            return DMToolPage(self.page)
            
        except Exception as e:
            logger.error(f"Error clicking Save button: {e}")
            raise
    
    def click_back(self) -> None:
        """Click the Back button to return to edit modal"""
        logger.info("Clicking Back button on USPS modal")
        try:
            back_btn = self.page.locator(self.back_button)
            back_btn.wait_for(state='visible', timeout=5000)
            back_btn.click()
            logger.info("Back button clicked")
            
            # Wait for transition back to edit modal
            self.page.wait_for_timeout(1500)
            
        except Exception as e:
            logger.error(f"Error clicking Back button: {e}")
            raise
    
    def check_original_address_matches(self, address_items: List[str]) -> bool:
        """Verify the original address displayed matches expected values
        
        Args:
            address_items: List of expected address components [street1, street2 (optional), city_state_zip]
        
        Returns:
            True if addresses match, False otherwise
        """
        logger.info("Checking if original address matches expected")
        logger.info(f"Expected address: {address_items}")
        
        try:
            # Wait for original address section to be visible
            self.page.wait_for_selector(self.original_address_section, timeout=5000)
            
            # Get displayed original address
            original_address = self.get_original_address()
            logger.info(f"Displayed original address: {original_address}")
            
            # Use address comparison utility
            address_match = check_if_there_is_address_match(address_items, original_address)
            
            if address_match:
                logger.info("[OK] Original address matches expected")
            else:
                logger.error("[FAIL] Original address does not match expected")
            
            return address_match
            
        except Exception as e:
            logger.error(f"Error checking original address: {e}")
            return False
    
    def get_original_address(self) -> List[str]:
        """Get the original address displayed in the modal
        
        Returns:
            List of address components [street1, street2 (optional), city_state_zip]
        """
        logger.info("Retrieving original address from USPS modal")
        
        try:
            address_lines = []
            
            # Get line 1
            line1_locator = self.page.locator(self.original_address_line1)
            if line1_locator.count() > 0:
                line1 = line1_locator.inner_text().strip()
                if line1:
                    address_lines.append(line1)
            
            # Get line 2 (optional)
            line2_locator = self.page.locator(self.original_address_line2)
            if line2_locator.count() > 0:
                line2 = line2_locator.inner_text().strip()
                if line2:
                    address_lines.append(line2)
            
            # Get city/state/zip
            city_state_zip_locator = self.page.locator(self.original_address_city_state_zip)
            if city_state_zip_locator.count() > 0:
                city_state_zip = city_state_zip_locator.inner_text().strip()
                if city_state_zip:
                    address_lines.append(city_state_zip)
            
            logger.info(f"Original address: {address_lines}")
            return address_lines
            
        except Exception as e:
            logger.error(f"Error retrieving original address: {e}")
            return []
    
    def grab_suggested_address(self) -> List[str]:
        """Get the suggested address from USPS validation
        
        Returns:
            List of address components [street1, street2 (optional), city_state_zip]
        """
        logger.info("Retrieving suggested address from USPS modal")
        
        try:
            address_lines = []
            
            # Wait for suggested address section
            self.page.wait_for_selector(self.suggested_address_section, timeout=5000)
            
            # Get line 1
            line1_locator = self.page.locator(self.suggested_address_line1)
            if line1_locator.count() > 0:
                line1 = line1_locator.inner_text().strip()
                if line1:
                    address_lines.append(line1)
            
            # Get line 2 (optional)
            line2_locator = self.page.locator(self.suggested_address_line2)
            if line2_locator.count() > 0:
                line2 = line2_locator.inner_text().strip()
                if line2:
                    address_lines.append(line2)
            
            # Get city/state/zip
            city_state_zip_locator = self.page.locator(self.suggested_address_city_state_zip)
            if city_state_zip_locator.count() > 0:
                city_state_zip = city_state_zip_locator.inner_text().strip()
                if city_state_zip:
                    address_lines.append(city_state_zip)
            
            logger.info(f"Suggested address: {address_lines}")
            return address_lines
            
        except Exception as e:
            logger.error(f"Error retrieving suggested address: {e}")
            return []
    
    def select_original_address(self) -> None:
        """Select the original address radio button"""
        logger.info("Selecting original address")
        try:
            original_radio = self.page.locator(self.use_original_radio)
            original_radio.wait_for(state='visible', timeout=5000)
            
            if not original_radio.is_checked():
                original_radio.click()
                logger.info("Original address radio button selected")
            else:
                logger.info("Original address already selected")
            
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            logger.error(f"Error selecting original address: {e}")
            raise
    
    def select_suggested_address(self) -> None:
        """Select the suggested address radio button"""
        logger.info("Selecting suggested address")
        try:
            suggested_radio = self.page.locator(self.use_suggested_radio)
            suggested_radio.wait_for(state='visible', timeout=5000)
            
            if not suggested_radio.is_checked():
                suggested_radio.click()
                logger.info("Suggested address radio button selected")
            else:
                logger.info("Suggested address already selected")
            
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            logger.error(f"Error selecting suggested address: {e}")
            raise
    
    def error_message_exists(self) -> bool:
        """Check if an error message is displayed in the modal
        
        Returns:
            True if error message is visible, False otherwise
        """
        logger.info("Checking for error message in USPS modal")
        
        try:
            error_locator = self.page.locator(self.error_message)
            is_visible = error_locator.is_visible()
            
            if is_visible:
                error_text = error_locator.inner_text()
                logger.warning(f"Error message displayed: {error_text}")
            else:
                logger.info("No error message displayed")
            
            return is_visible
            
        except Exception as e:
            logger.error(f"Error checking for error message: {e}")
            return False
    
    def is_suggested_address_available(self) -> bool:
        """Check if a suggested address is available from USPS
        
        Returns:
            True if suggested address section is visible, False otherwise
        """
        logger.info("Checking if suggested address is available")
        
        try:
            suggested_section = self.page.locator(self.suggested_address_section)
            is_visible = suggested_section.is_visible()
            
            logger.info(f"Suggested address available: {is_visible}")
            return is_visible
            
        except Exception as e:
            logger.error(f"Error checking suggested address availability: {e}")
            return False
    
    def compare_addresses(self) -> bool:
        """Compare original and suggested addresses
        
        Returns:
            True if addresses are different, False if they are the same
        """
        logger.info("Comparing original and suggested addresses")
        
        try:
            original = self.get_original_address()
            suggested = self.grab_suggested_address()
            
            logger.info(f"Original: {original}")
            logger.info(f"Suggested: {suggested}")
            
            # Simple comparison - check if any line is different
            are_different = original != suggested
            
            if are_different:
                logger.info("Addresses are different")
            else:
                logger.info("Addresses are the same")
            
            return are_different
            
        except Exception as e:
            logger.error(f"Error comparing addresses: {e}")
            return False
