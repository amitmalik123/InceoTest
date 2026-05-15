"""
DM Tool Page Object for Address Change functionality
"""

from typing import List, Optional, TYPE_CHECKING
from playwright.sync_api import Page

from pages.stp.shared.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)
from utils.address_comparison import check_if_there_is_address_match

if TYPE_CHECKING:
    from dm_tool_address_edit_modal import DMToolAddressEditModal
    from dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage



class DMToolPage(BasePage):
    """Page object for DM Tool Address Change functionality"""
    
    PAGE_NAME = "DM Tool Address Change"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Section XPath patterns (matching Java implementation)
        self.footer_section_xpath = "//footer"
        self.header_section_xpath = "//header[@data-testid='header']"
        self.notes_section_xpath = "//li[@aria-label='list-item']"
        self.bottom_buttons_section_xpath = "//div[@data-testid='action-buttons']"
        self.account_info_section_xpath = "//section[@aria-label='account-info-section']"
        self.addresses_section_xpath = "//section[@aria-label='address-change-section']"
        self.legal_address_section = self.addresses_section_xpath + "//div[@data-testid='legal-address-card']"
        self.mailing_address_section = self.addresses_section_xpath + "//div[@data-testid='mailing-address-card']"
        
        # Page Locators for Address Change UI elements
        self.table_row = self.account_info_section_xpath + "//tr[@aria-label='table-row']"
        self.important_notes_section = self.notes_section_xpath + "[1]"
        self.important_notes_bulletins_first = self.notes_section_xpath + "[1]"
        self.important_notes_bulletins_second = self.notes_section_xpath + "[2]"
        self.important_notes_bulletins_third = self.notes_section_xpath + "[3]"
        self.important_notes_bulletins_fourth = self.notes_section_xpath + "[4]"
        
        # Header elements
        self.update_addresses_text = self.header_section_xpath + "//h1[@data-testid='header-tool-name']"
        self.advisor_id = self.header_section_xpath + "//span[@data-testid='header-advisor-id']"
        
        # Legal Address elements
        self.legal_address_label = self.legal_address_section + "//h3[@data-testid='address-card-name']"
        self.legal_address_contents = self.legal_address_section + "//ul/li"
        self.legal_edit_button = self.legal_address_section + "//button[@aria-label='icon-button']//*[local-name() = 'svg']"
        
        # Mailing Address elements
        self.mailing_address_label = self.mailing_address_section + "//h3[@data-testid='address-card-name']"
        self.mailing_address_contents = self.mailing_address_section + "//ul/li"
        self.mailing_edit_button = self.mailing_address_section + "//button[@aria-label='icon-button']//*[local-name() = 'svg']"
        
        # Action buttons
        self.submit_button = self.bottom_buttons_section_xpath + "//button[@data-testid='submit-button']"
        self.cancel_button = self.bottom_buttons_section_xpath + "//button[@data-testid='cancel-button']"
        
        # Footer elements
        self.assetmark_text = self.footer_section_xpath + "//p[@aria-label='company-name']"
        self.privacy_link = self.footer_section_xpath + "//button[.='Privacy and Security Policy']"
        self.terms_link = self.footer_section_xpath + "//button[.='Terms of Use']"
        self.supported_browsers_link = self.footer_section_xpath + "//button[.='Supported Browsers']"
        self.copyright_text = self.footer_section_xpath + "//p[@aria-label='copyright']"
        
        # Account Information elements
        self.household_name = self.account_info_section_xpath + "//h3[@aria-label='household-name']"
        self.account_information_label = self.account_info_section_xpath + "//h3[@class='section-title']"
        self.account_name_column_label = self.account_info_section_xpath + "//th[contains(text(),'Account Name')]"
        self.account_number_column_label = self.account_info_section_xpath + "//th[contains(text(),'Account Number')]"
        self.strategy_column_label = self.account_info_section_xpath + "//th[contains(text(),'Strategy')]"
        self.status_column_label = self.account_info_section_xpath + "//th[contains(text(),'Status')]"
        
        # Address section title
        self.address_section_title = self.addresses_section_xpath + "//h3[@aria-label='address-change-section-title']"
        
        # Error messages
        self.no_changes_error = "//div[@data-testid='no-changes-note']"
        self.fraud_message = "//div[@aria-label='no-changes-note']"
        
        # Loading indicators
        self.loading_spinner = "//div[@class='spinner-border']"

    def get_household_id(self) -> str:
        """Fetch the ClientHouseholdID from the current URL"""
        current_url = self.page.url
        logger.info(f"Current URL: {current_url}")

        # Split by '=' and get the 3rd element (index 2)
        household_id = current_url.split("=")[2]
        logger.info(f"ClientHouseholdID: {household_id}")
        
        return household_id
    
    def get_advisor_id(self) -> str:
        """Get the advisor ID from the page header"""
        advisor_element = self.page.locator(self.advisor_id)
        advisor_text = advisor_element.inner_text().strip()
        return advisor_text
    
    def wait_for_data_to_load(self) -> None:
        """Wait for Address Change data to load on the page"""
        logger.info("Waiting for Address Change data to load")
        
        try:
            # Wait for table rows to appear (address data)
            self.page.wait_for_selector(self.table_row, timeout=120000)
            logger.info("Address table rows loaded")
            
            # Wait for loading spinner to disappear if present
            if self.page.locator(self.loading_spinner).count() > 0:
                self.page.locator(self.loading_spinner).wait_for(state='hidden', timeout=30000)
                logger.info("Loading spinner disappeared")
            
            # Additional wait for data stabilization
            self.page.wait_for_timeout(2000)
            logger.info("Address Change page data fully loaded")
            
        except Exception as e:
            logger.error(f"Error waiting for data to load: {e}")
            raise
    
    def test_address_change_ui(self, display_only_mailing_address: bool, advisor_name: str) -> None:
        """Test the Address Change UI elements based on custodian configuration
        
        Args:
            display_only_mailing_address: If True, only mailing address should be displayed
            advisor_name: Name of the advisor to verify
        """
        logger.info(f"Testing Address Change UI - Display only mailing: {display_only_mailing_address}")
        
        # Check Important Notes section
        important_notes_exists = self.important_notes_section_exists()
        assert important_notes_exists, "Important Notes section not found"
        logger.info("[OK] Important Notes section verified")
        
        # Verify notes content
        self.check_notes()
        logger.info("[OK] Important Notes content verified")
        
        # Verify Legal Address existence
        if not display_only_mailing_address:
            legal_exists = self.check_legal_address_existence()
            assert legal_exists, "Legal Address should be displayed but is not found"
            logger.info("[OK] Legal Address section verified")
        else:
            logger.info("Skipping Legal Address check (display_only_mailing_address=True)")
        
        # Verify Mailing Address existence
        mailing_exists = self.check_mailing_address_existence()
        assert mailing_exists, "Mailing Address not found"
        logger.info("[OK] Mailing Address section verified")
        
        logger.info("Address Change UI validation completed successfully")
    
    def important_notes_section_exists(self) -> bool:
        """Check if Important Notes section exists"""
        logger.info("Checking for Important Notes section")
        try:
            is_visible = self.page.locator(self.important_notes_section).is_visible(timeout=15000)
            logger.info(f"Important Notes section visible: {is_visible}")
            return is_visible
        except Exception as e:
            logger.error(f"Error checking Important Notes section: {e}")
            return False
    
    def check_notes(self) -> None:
        """Verify the content of Important Notes"""
        logger.info("Checking Important Notes content")
        try:
            # Check first bulletin (always present)
            first_bulletin = self.page.locator(self.important_notes_bulletins_first)
            first_bulletin.wait_for(state='visible', timeout=10000)
            
            first_content = first_bulletin.inner_text()
            logger.info(f"First bulletin content: {first_content}")
            
            # Verify expected content is present
            assert len(first_content) > 0, "Important Notes content is empty"
            logger.info("[OK] Important Notes first bulletin verified")
            
            # Check if additional bulletins exist
            second_bulletin_count = self.page.locator(self.important_notes_bulletins_second).count()
            if second_bulletin_count > 0:
                logger.info(f"[OK] Found {second_bulletin_count + 1} important notes bulletins")
            
        except Exception as e:
            logger.error(f"Error checking notes content: {e}")
            raise
    
    def check_legal_address_existence(self) -> bool:
        """Check if Legal Address section exists"""
        logger.info("Checking for Legal Address section")
        try:
            is_visible = self.page.locator(self.legal_address_label).is_visible(timeout=5000)
            logger.info(f"Legal Address section visible: {is_visible}")
            return is_visible
        except Exception as e:
            logger.error(f"Error checking Legal Address section: {e}")
            return False
    
    def check_mailing_address_existence(self) -> bool:
        """Check if Mailing Address section exists"""
        logger.info("Checking for Mailing Address section")
        try:
            is_visible = self.page.locator(self.mailing_address_label).is_visible(timeout=5000)
            logger.info(f"Mailing Address section visible: {is_visible}")
            return is_visible
        except Exception as e:
            logger.error(f"Error checking Mailing Address section: {e}")
            return False
    
    def return_address(self, selector: str) -> List[str]:
       
        logger.info(f"Retrieving {selector} address")
        
        try:
            if selector.lower() == 'legal':
                address_contents = self.legal_address_contents
            elif selector.lower() == 'mailing':
                address_contents = self.mailing_address_contents
            else:
                raise ValueError(f"Invalid selector: {selector}. Must be 'legal' or 'mailing'")
            
            address_lines = self.page.locator(address_contents).all()
            size = len(address_lines)
            array = []
            
            if size > 0:
                for line in address_lines:
                    array.append(line.inner_text())
            
            logger.info(f"{selector.capitalize()} address retrieved: {array}")
            return array
            
        except Exception as e:
            logger.error(f"Error retrieving {selector} address: {e}")
            raise
    
    def wait_for_all_spinners_to_disappear(self) -> None:
        """Wait for all loading spinners to disappear"""
        logger.info("Waiting for all spinners to disappear")
        try:
            spinner_selector = "//div[contains(@class, 'spinner')]"
            spinners = self.page.locator(spinner_selector)
            
            if spinners.count() > 0:
                spinners.first.wait_for(state='hidden', timeout=30000)
                logger.info("All spinners disappeared")
            else:
                logger.info("No spinners found")
                
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            logger.warning(f"Error waiting for spinners: {e}")
    
    def click_submit(self) -> 'DMTAddressChangeConfirmationPage':
        """Click the Submit button
        
        Returns:
            DMTAddressChangeConfirmationPage instance
        """
        from dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage
        
        logger.info("DMT: Clicking submit button")
        try:
            submit_locator = self.page.locator(self.submit_button)
            submit_locator.wait_for(state='visible', timeout=10000)
            
            self.page.evaluate("(element) => element.click()", submit_locator.element_handle())
            logger.info("DMT: Submit button clicked")
            
            self.wait_for_all_spinners_to_disappear()
            
            return DMTAddressChangeConfirmationPage(self.page)
            
        except Exception as e:
            logger.error(f"Error clicking Submit button: {e}")
            raise
    
    def navigate_to_address_change_edit_modal(self, step_name: str, log_message: str) -> 'DMToolAddressEditModal':
       
        from dm_tool_address_edit_modal import DMToolAddressEditModal
        
        logger.info(f"{step_name}: {log_message}")
        try:
            edit_button = self.page.locator(self.legal_edit_button)
            
            edit_button.wait_for(state='visible', timeout=10000)
            edit_button.wait_for(state='attached', timeout=10000)
            
            edit_button.click()
            logger.info(f"Legal Edit button clicked")
            
            modal_input = self.page.locator("//div[@aria-label='form-input-item']//input[@name='addressLine1']")
            try:
                modal_input.wait_for(state='visible', timeout=10000)
                logger.info(f"{self.PAGE_NAME}: Successfully navigated to Address edit modal")
            except:
                logger.error(f"{self.PAGE_NAME}: FAILED to navigate to Address edit modal")
                raise
            
            return DMToolAddressEditModal(self.page)
            
        except Exception as e:
            logger.error(f"Error navigating to Address Change Edit Modal: {e}")
            raise
    
    def navigate_to_mailing_address_change_edit_modal(self, step_name: str, log_message: str) -> 'DMToolAddressEditModal':
        """Click Edit button to open Mailing Address Change Edit Modal
        
        Args:
            step_name: Name of the step for logging
            log_message: Custom log message
            
        Returns:
            DMToolAddressEditModal instance
        """
        from dm_tool_address_edit_modal import DMToolAddressEditModal
        
        logger.info(f"{step_name}: {log_message}")
        try:
            edit_button = self.page.locator(self.mailing_edit_button)
            
            edit_button.wait_for(state='visible', timeout=10000)
            edit_button.wait_for(state='attached', timeout=10000)
            
            edit_button.click()
            logger.info(f"Mailing Edit button clicked")
            
            modal_input = self.page.locator("//div[@aria-label='form-input-item']//input[@name='addressLine1']")
            try:
                modal_input.wait_for(state='visible', timeout=10000)
                logger.info(f"{self.PAGE_NAME}: Successfully navigated to Mailing edit modal")
            except:
                logger.error(f"{self.PAGE_NAME}: FAILED to navigate to Mailing edit modal")
                raise
            
            return DMToolAddressEditModal(self.page)
            
        except Exception as e:
            logger.error(f"Error navigating to Mailing Address Change Edit Modal: {e}")
            raise
    
    def click_cancel_button(self) -> None:
        """Click the Cancel button"""
        logger.info("Clicking Cancel button")
        try:
            cancel_locator = self.page.locator(self.cancel_button)
            cancel_locator.wait_for(state='visible', timeout=10000)
            cancel_locator.click()
            logger.info("Cancel button clicked")
            
            # Wait for cancel button to disappear (navigated away from DM Tool)
            cancel_locator.wait_for(state='hidden', timeout=10000)
            logger.info("Navigated away from DM Tool page")
            
            # Wait for spinner to disappear
            self.wait_for_all_spinners_to_disappear()
            
            # Additional wait for page stabilization
            self.page.wait_for_timeout(2000)
            logger.info("Returned to Account Wizard page")
            
        except Exception as e:
            logger.error(f"Error clicking Cancel button: {e}")
            raise
    
    def check_new_address_has_been_saved(self, 
                                          address_type: str,
                                          expected_address: List[str]) -> bool:
        """Verify that new address has been saved correctly
        
        Args:
            address_type: 'legal' or 'mailing'
            expected_address: List of expected address components [street1, street2 (optional), city_state_zip]
        
        Returns:
            True if address matches, False otherwise
        """
        logger.info(f"Verifying new {address_type} address has been saved")
        
        try:
            # Wait for page to refresh after save
            self.page.wait_for_timeout(2000)
            self.wait_for_data_to_load()
            
            # Get current address from page
            current_address = self.return_address(address_type)
            logger.info(f"Current {address_type} address: {current_address}")
            logger.info(f"Expected {address_type} address: {expected_address}")
            
            # Use address comparison utility to verify match
            address_match = check_if_there_is_address_match(expected_address, current_address)
            
            if address_match:
                logger.info(f"[OK] New {address_type} address verified successfully")
            else:
                logger.error(f"[FAIL] New {address_type} address does not match expected")
            
            return address_match
            
        except Exception as e:
            logger.error(f"Error verifying new {address_type} address: {e}")
            return False
