"""
DM Tool Address Change Confirmation Page Object
"""

from typing import Dict, List, Optional
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from utils.address_comparison import compare_address_arrays, get_current_date

logger = setup_logger(__name__)


class DMTAddressChangeConfirmationPage(BasePage):
    """Page object for Address Change Confirmation Page"""
    
    PAGE_NAME = "Address Change Confirmation"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        HEADER_SECTION = "//div[@aria-label='confirmation-screen-header']"
        FOOTER_SECTION = "//div[@aria-label='confirmation-screen-buttons']"
        HOUSEHOLD_SECTION = "//div[@aria-label='confirmation-screen-account-information']"
        IMPORTANT_SECTION = "//div[@role='presentation']/div[3]/div/div[2]/div[3]"
        SUMMARY_SECTION = "//div[@aria-label='confirmation-screen-summary']"
        
        self.header_text = f"{HEADER_SECTION}//h2"
        self.close_button = f"{FOOTER_SECTION}//button"
        self.household_label = f"({HOUSEHOLD_SECTION}//h3)[1]"
        self.household_data = f"({HOUSEHOLD_SECTION}//p)[1]"
        self.household_advisor_label = f"({HOUSEHOLD_SECTION}//h3)[2]"
        self.household_advisor_data = f"({HOUSEHOLD_SECTION}//p)[2]"
        self.custodian_label = f"({HOUSEHOLD_SECTION}//h3)[3]"
        self.custodian_data = f"({HOUSEHOLD_SECTION}//p)[3]"
        self.updated_successfully_text = "//div[3]//h3[.='Address updated successfully']"
        self.important_notes_label = f"{IMPORTANT_SECTION}//h3"
        self.important_notes_data = f"{IMPORTANT_SECTION}//p"
        self.status_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-status-completed']//h3[.='Status']"
        self.status_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-status-completed']//p"
        self.submitted_by_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-submitted-by']//h3[.='Submitted by']"
        self.submitted_by_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-submitted-by']//p"
        self.submission_date_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-submitted-date']//h3[.='Submission date and time']"
        self.submission_date_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-submitted-date']//p"
        self.item_number_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-item-number']//h3[.='Item number']"
        self.item_number_link = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-item-number']//a"
        self.updated_information_label = f"{SUMMARY_SECTION}//h3[.='Updated Information']"
        self.previous_information_label = f"{SUMMARY_SECTION}//h3[.='Previous Information']"
        self.legal_address_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-updated-legal']//h3[.='Legal Address']"
        self.legal_address_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-updated-legal']//p"
        self.mailing_address_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-updated-mailing']//h3[.='Mailing Address']"
        self.mailing_address_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-updated-mailing']//p"
        self.previous_legal_address_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-previous-legal']//h3[.='Legal Address']"
        self.previous_legal_address_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-previous-legal']//p"
        self.previous_mailing_address_label = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-previous-mailing']//h3[.='Mailing Address']"
        self.previous_mailing_address_data = f"{SUMMARY_SECTION}//div[@aria-label='confirmation-screen-previous-mailing']//p"
        self.print_button = f"{HEADER_SECTION}//button"
        
    def wait_for_page_load(self) -> None:
        logger.info("Waiting for Address Change Confirmation page to load")
        self.page.wait_for_selector(self.header_text, timeout=15000)
        logger.info("Confirmation page loaded")
        self.page.wait_for_timeout(1500)
    
    def check_ui_elements_exist(self, display_only_mailing_address: bool) -> bool:
        value = (self.page.locator(self.header_text).is_visible() and
                self.page.locator(self.close_button).is_visible() and
                self.page.locator(self.household_label).is_visible() and
                self.page.locator(self.household_data).is_visible() and
                self.page.locator(self.household_advisor_label).is_visible() and
                self.page.locator(self.household_advisor_data).is_visible() and
                self.page.locator(self.updated_successfully_text).is_visible() and
                self.page.locator(self.important_notes_label).is_visible() and
                self.page.locator(self.important_notes_data).is_visible() and
                self.page.locator(self.status_label).is_visible() and
                self.page.locator(self.status_data).is_visible() and
                self.page.locator(self.submitted_by_label).is_visible() and
                self.page.locator(self.submitted_by_data).is_visible() and
                self.page.locator(self.submission_date_label).is_visible() and
                self.page.locator(self.submission_date_data).is_visible() and
                self.page.locator(self.item_number_label).is_visible() and
                self.page.locator(self.item_number_link).is_visible() and
                self.page.locator(self.updated_information_label).is_visible() and
                self.page.locator(self.mailing_address_label).is_visible() and
                self.page.locator(self.mailing_address_data).is_visible() and
                self.page.locator(self.previous_information_label).is_visible() and
                self.page.locator(self.previous_mailing_address_label).is_visible() and
                self.page.locator(self.previous_mailing_address_data).is_visible())
        
        value1 = (self.page.locator(self.legal_address_label).is_visible() and
                 self.page.locator(self.legal_address_data).is_visible() and
                 self.page.locator(self.previous_legal_address_label).is_visible() and
                 self.page.locator(self.previous_legal_address_data).is_visible())
        
        value2 = True
        if display_only_mailing_address:
            value2 = (self.page.locator(self.custodian_label).is_visible() and
                     self.page.locator(self.custodian_data).is_visible())
            value1 = not value1
        
        return value and value1 and value2
    
    def check_data_is_correct(self,
                              mailing_before: List[str],
                              legal_before: Optional[List[str]],
                              mailing_after: List[str],
                              legal_after: Optional[List[str]],
                              household: str,
                              advisor: str,
                              display_only_mailing_address: bool) -> None:
        """Verify all data displayed on confirmation page is correct
        
        Args:
            mailing_before: Expected mailing address before change
            legal_before: Expected legal address before change (optional)
            mailing_after: Expected mailing address after change
            legal_after: Expected legal address after change (optional)
            household: Expected household ID
            advisor: Expected advisor name
            display_only_mailing_address: If True, only verify mailing address
        """
        logger.info("Verifying data on confirmation page")
        
        try:
            # Verify household ID
            displayed_household = self.get_household_id()
            if household:
                assert displayed_household == household, f"Household ID mismatch: {displayed_household} != {household}"
                logger.info(f"[OK] Household ID verified: {household}")
            
            # Verify advisor name
            displayed_advisor = self.get_advisor_name()
            if advisor:
                assert advisor.lower() in displayed_advisor.lower(), f"Advisor name mismatch: {displayed_advisor} != {advisor}"
                logger.info(f"[OK] Advisor name verified: {advisor}")
            
            # Verify mailing address BEFORE
            logger.info("Verifying mailing address BEFORE")
            displayed_mailing_before = self.get_address_from_section('mailing', 'before')
            mailing_before_match = not compare_address_arrays(mailing_before, displayed_mailing_before)
            assert mailing_before_match, f"Mailing BEFORE mismatch: {displayed_mailing_before} != {mailing_before}"
            logger.info("[OK] Mailing address BEFORE verified")
            
            # Verify mailing address AFTER
            logger.info("Verifying mailing address AFTER")
            displayed_mailing_after = self.get_address_from_section('mailing', 'after')
            mailing_after_match = not compare_address_arrays(mailing_after, displayed_mailing_after)
            assert mailing_after_match, f"Mailing AFTER mismatch: {displayed_mailing_after} != {mailing_after}"
            logger.info("[OK] Mailing address AFTER verified")
            
            # Verify legal address if applicable
            if not display_only_mailing_address and legal_before and legal_after:
                # Verify legal address BEFORE
                logger.info("Verifying legal address BEFORE")
                displayed_legal_before = self.get_address_from_section('legal', 'before')
                legal_before_match = not compare_address_arrays(legal_before, displayed_legal_before)
                assert legal_before_match, f"Legal BEFORE mismatch: {displayed_legal_before} != {legal_before}"
                logger.info("[OK] Legal address BEFORE verified")
                
                # Verify legal address AFTER
                logger.info("Verifying legal address AFTER")
                displayed_legal_after = self.get_address_from_section('legal', 'after')
                legal_after_match = not compare_address_arrays(legal_after, displayed_legal_after)
                assert legal_after_match, f"Legal AFTER mismatch: {displayed_legal_after} != {legal_after}"
                logger.info("[OK] Legal address AFTER verified")
            else:
                logger.info("Skipping legal address verification")
            
            logger.info("[OK] All data verification completed successfully")
            
        except Exception as e:
            logger.error(f"Error verifying data on confirmation page: {e}")
            raise
    
    def get_item_number(self) -> str:
        """Get the item number from the confirmation page
        
        Returns:
            The item number as a string
        """
        logger.info("Retrieving item number from confirmation page")
        
        try:
            item_number_locator = self.page.locator(self.item_number_link)
            item_number_locator.wait_for(state='visible', timeout=10000)
            
            item_number = item_number_locator.inner_text().strip()
            logger.info(f"Item number: {item_number}")
            
            return item_number
            
        except Exception as e:
            logger.error(f"Error retrieving item number: {e}")
            raise
    
    def click_item_number(self) -> None:
        """Click on the item number link to view details"""
        logger.info("Clicking item number link")
        
        try:
            item_number_locator = self.page.locator(self.item_number_link)
            item_number_locator.wait_for(state='visible', timeout=10000)
            item_number_locator.click()
            logger.info("Item number link clicked")
            
            # Wait for navigation to item details page
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            logger.error(f"Error clicking item number: {e}")
            raise
    
    def click_close(self) -> None:
        """Click the Close button"""
        logger.info("Clicking Close button")
        
        try:
            close_btn = self.page.locator(self.close_button)
            close_btn.wait_for(state='visible', timeout=10000)
            close_btn.click()
            logger.info("Close button clicked")
            
            # Wait for page transition
            self.page.wait_for_timeout(1500)
            
        except Exception as e:
            logger.error(f"Error clicking Close button: {e}")
            raise
    
    def get_household_id(self) -> str:
        """Get the household ID displayed on the page
        
        Returns:
            Household ID as string
        """
        logger.info("Retrieving household ID from confirmation page")
        
        try:
            household_locator = self.page.locator(self.household_id_value)
            if household_locator.count() > 0:
                household_id = household_locator.inner_text().strip()
                logger.info(f"Household ID: {household_id}")
                return household_id
            else:
                logger.warning("Household ID element not found")
                return ""
            
        except Exception as e:
            logger.error(f"Error retrieving household ID: {e}")
            return ""

    def get_household_id_prod(self) -> str:
        """PROD: Get the household ID from the confirmation page UI element.

        Returns:
            Household ID as string
        """
        logger.info("[PROD] Retrieving household ID from confirmation page")

        try:
            household_locator = self.page.locator(self.household_data)
            if household_locator.count() > 0:
                household_id = household_locator.inner_text().strip()
                logger.info(f"[PROD] Household ID: {household_id}")
                return household_id
            else:
                logger.warning("[PROD] Household ID element not found")
                return ""

        except Exception as e:
            logger.error(f"[PROD] Error retrieving household ID: {e}")
            return ""
    
    def get_advisor_name(self) -> str:
        """Get the advisor name displayed on the page
        
        Returns:
            Advisor name as string
        """
        logger.info("Retrieving advisor name from confirmation page")
        
        try:
            advisor_locator = self.page.locator(self.advisor_name_value)
            if advisor_locator.count() > 0:
                advisor_name = advisor_locator.inner_text().strip()
                logger.info(f"Advisor name: {advisor_name}")
                return advisor_name
            else:
                logger.warning("Advisor name element not found")
                return ""
            
        except Exception as e:
            logger.error(f"Error retrieving advisor name: {e}")
            return ""

    def get_advisor_name_prod(self) -> str:
        """PROD: Get the advisor name from the confirmation page UI element.

        Returns:
            Advisor name as string
        """
        logger.info("[PROD] Retrieving advisor name from confirmation page")

        try:
            advisor_locator = self.page.locator(self.household_advisor_data)
            if advisor_locator.count() > 0:
                advisor_name = advisor_locator.inner_text().strip()
                logger.info(f"[PROD] Advisor name: {advisor_name}")
                return advisor_name
            else:
                logger.warning("[PROD] Advisor name element not found")
                return ""

        except Exception as e:
            logger.error(f"[PROD] Error retrieving advisor name: {e}")
            return ""
    
    def get_address_from_section(self, address_type: str, timing: str) -> List[str]:
        """Get address from specific section
        
        Args:
            address_type: 'legal' or 'mailing'
            timing: 'before' or 'after'
        
        Returns:
            List of address components
        """
        logger.info(f"Retrieving {address_type} address {timing}")
        
        try:
            # Build section selector
            section_selector = f"//div[@aria-label='{address_type}-address-{timing}']"
            
            # Wait for section to be visible
            self.page.wait_for_selector(section_selector, timeout=10000)
            
            # Get address lines from section
            address_lines = []
            
            # Line 1
            line1_selector = f"{section_selector}//p[@aria-label='address-line-1']"
            line1_locator = self.page.locator(line1_selector)
            if line1_locator.count() > 0:
                line1 = line1_locator.inner_text().strip()
                if line1:
                    address_lines.append(line1)
            
            # Line 2 (optional)
            line2_selector = f"{section_selector}//p[@aria-label='address-line-2']"
            line2_locator = self.page.locator(line2_selector)
            if line2_locator.count() > 0:
                line2 = line2_locator.inner_text().strip()
                if line2:
                    address_lines.append(line2)
            
            # City/State/ZIP
            city_state_zip_selector = f"{section_selector}//p[@aria-label='address-line-city-state-zip']"
            city_state_zip_locator = self.page.locator(city_state_zip_selector)
            if city_state_zip_locator.count() > 0:
                city_state_zip = city_state_zip_locator.inner_text().strip()
                if city_state_zip:
                    address_lines.append(city_state_zip)
            
            logger.info(f"{address_type.capitalize()} address {timing}: {address_lines}")
            return address_lines
            
        except Exception as e:
            logger.error(f"Error retrieving {address_type} address {timing}: {e}")
            return []
    
    def get_submission_date(self) -> str:
        """Get the submission date from the page
        
        Returns:
            Submission date as string
        """
        logger.info("Retrieving submission date")
        
        try:
            date_locator = self.page.locator(self.submission_date)
            if date_locator.count() > 0:
                date_text = date_locator.inner_text().strip()
                logger.info(f"Submission date: {date_text}")
                return date_text
            else:
                logger.warning("Submission date not found")
                return ""
            
        except Exception as e:
            logger.error(f"Error retrieving submission date: {e}")
            return ""
    
    def verify_submission_date_is_today(self) -> bool:
        """Verify the submission date is today's date
        
        Returns:
            True if submission date is today, False otherwise
        """
        logger.info("Verifying submission date is today")
        
        try:
            displayed_date = self.get_submission_date()
            today_date = get_current_date("%m/%d/%Y")
            
            is_today = today_date in displayed_date or displayed_date in today_date
            
            if is_today:
                logger.info(f"[OK] Submission date is today: {displayed_date}")
            else:
                logger.warning(f"[FAIL] Submission date mismatch: {displayed_date} != {today_date}")
            
            return is_today
            
        except Exception as e:
            logger.error(f"Error verifying submission date: {e}")
            return False
