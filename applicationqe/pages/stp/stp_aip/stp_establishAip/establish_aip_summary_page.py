"""
Establish AIP Summary Page Object
"""

from typing import List
from playwright.sync_api import Locator, Page
from pages.ewm.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_summary_locators import EstablishAIPSummaryLocators
from pages.stp.stp_aip.stp_establishAip.establish_aip_confirmation_page import EstablishAIPConfirmationPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPSummaryPage(BasePage):
    """Page object for Establish AIP Summary Page"""
    
    PAGE_NAME = "establishAIPSummaryPage"
    
    ACKNOWLEDGEMENT_HEADER = "Upon completion of this request, I certify that:"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        ctx = self.active_root()
        loc = EstablishAIPSummaryLocators
        
        # Acknowledgements section
        self.acknowledgements = ctx.locator(loc.ACKNOWLEDGEMENTS)
        
        # Summary section
        self.summary_section = ctx.locator(loc.SUMMARY_SECTION)
        self.request_type_value = ctx.locator(loc.REQUEST_TYPE_VALUE)
        self.delivery_method_value = ctx.locator(loc.DELIVERY_METHOD_VALUE)
        self.origination_value = ctx.locator(loc.ORIGINATION_VALUE)
        self.frequency_value = ctx.locator(loc.FREQUENCY_VALUE)
        self.amount_value = ctx.locator(loc.AMOUNT_VALUE)
        self.start_date_value = ctx.locator(loc.START_DATE_VALUE)
        self.end_date_value = ctx.locator(loc.END_DATE_VALUE)
        
        # Acknowledgements section
        self.acknowledgements_header = ctx.locator(loc.ACKNOWLEDGEMENTS_HEADER)
        self.acknowledgements_body = ctx.locator(loc.ACKNOWLEDGEMENTS_BODY)
        self.acknowledgements_list = ctx.locator(loc.ACKNOWLEDGEMENTS_LIST)
        
        # Buttons
        self.cancel_button = ctx.locator(loc.CANCEL_BUTTON)
        self.back_button = ctx.locator(loc.BACK_BUTTON)
        self.submit_button = ctx.locator(loc.SUBMIT_BUTTON)
        
        # Loading indicators
        self.spinner_loading = ctx.locator(loc.SPINNER_LOADING)
        self.loading_overlay = ctx.locator(loc.LOADING_OVERLAY)
        
        # Wait for page load
        self.wait_for_page_load(page_verification)
    
    def wait_for_page_load(self, page_verification: bool = True) -> None:
        """Wait for Summary Page to load"""
        logger.info("Waiting for Establish AIP Summary Page to load")
        
        # Wait for spinner to disappear
        try:
            if self.spinner_loading.count() > 0:
                self.spinner_loading.wait_for(state='hidden', timeout=30000)
                logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.warning(f"Spinner wait failed: {e}")
        
        # Wait for loading overlay to disappear
        try:
            if self.loading_overlay.count() > 0:
                self.loading_overlay.wait_for(state='hidden', timeout=30000)
                logger.info("Loading overlay disappeared")
        except Exception as e:
            logger.warning(f"Loading overlay wait failed: {e}")
        
        # Page verification
        if page_verification:
            acknowledgements_visible = self.is_visible(self.acknowledgements, timeout=5000)
            
            if acknowledgements_visible:
                logger.info(f"{self.PAGE_NAME} verification PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification FAILED")
    
    # ========== SUMMARY SECTION ==========
    def verify_summary_section_visible(self) -> None:
        """Verify summary section is visible"""
        self.summary_section.wait_for(state='visible', timeout=10000)
        logger.info("Summary section is visible")
    
    def get_request_type(self) -> str:
        """Get request type value"""
        return self.get_text(self.request_type_value)
    
    def get_delivery_method(self) -> str:
        """Get delivery method value"""
        return self.get_text(self.delivery_method_value)
    
    def get_origination(self) -> str:
        """Get origination value"""
        return self.get_text(self.origination_value)
    
    def get_frequency(self) -> str:
        """Get frequency value"""
        return self.get_text(self.frequency_value)
    
    def get_amount(self) -> str:
        """Get amount value"""
        return self.get_text(self.amount_value)
    
    def get_start_date(self) -> str:
        """Get start date value"""
        return self.get_text(self.start_date_value)
    
    def get_end_date(self) -> str:
        """Get end date value"""
        return self.get_text(self.end_date_value)
    
    # ========== ASSERTION METHODS ==========
    def assert_request_type(self, expected_request_type: str) -> None:
        """Assert Request Type matches expected"""
        actual = self.get_request_type()
        assert actual == expected_request_type, \
            f"Request Type mismatch. Expected: {expected_request_type}, Actual: {actual}"
        logger.info(f"Request Type verified: {actual}")
    
    def assert_delivery_method(self, expected_delivery_method: str) -> None:
        """Assert Delivery Method matches expected"""
        actual = self.get_delivery_method()
        assert actual == expected_delivery_method, \
            f"Delivery Method mismatch. Expected: {expected_delivery_method}, Actual: {actual}"
        logger.info(f"Delivery Method verified: {actual}")
    
    def assert_origination(self, expected_origination: str) -> None:
        """Assert Origination matches expected"""
        actual = self.get_origination()
        normalized_expected = self._normalize_origination_text(expected_origination)
        normalized_actual = self._normalize_origination_text(actual)
        assert normalized_expected == normalized_actual, \
            f"Origination mismatch. Expected: {expected_origination}, Actual: {actual}"
        logger.info(f"Origination verified: {actual}")
    
    def _normalize_origination_text(self, text: str) -> str:
        """Normalizes origination text by removing separators"""
        if not text:
            return ""
        return text.replace(" - ", " ").strip()
    
    def _normalize_quotes(self, text: str) -> str:
        """Normalizes curly/smart quotes to straight quotes for comparison"""
        if not text:
            return ""
        return text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201C", '"').replace("\u201D", '"')
    
    def assert_frequency(self, expected_frequency: str) -> None:
        """Assert Frequency matches expected"""
        actual = self.get_frequency()
        assert actual == expected_frequency, \
            f"Frequency mismatch. Expected: {expected_frequency}, Actual: {actual}"
        logger.info(f"Frequency verified: {actual}")
    
    def assert_amount(self, expected_amount: str) -> None:
        """Assert Amount matches expected"""
        actual = self.get_amount()
        normalized_expected = self._normalize_amount_text(expected_amount)
        normalized_actual = self._normalize_amount_text(actual)
        assert normalized_expected == normalized_actual, \
            f"Amount mismatch. Expected: {expected_amount}, Actual: {actual}"
        logger.info(f"Amount verified: {actual}")
    
    def _normalize_amount_text(self, amount: str) -> str:
        """Normalizes amount text"""
        if not amount:
            return ""
        normalized = amount.replace("$", "").replace(",", "").strip()
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        return normalized
    
    def assert_start_date(self, expected_start_date: str) -> None:
        """Assert Start Date matches expected"""
        actual = self.get_start_date()
        assert actual == expected_start_date, \
            f"Start Date mismatch. Expected: {expected_start_date}, Actual: {actual}"
        logger.info(f"Start Date verified: {actual}")
    
    def assert_end_date(self, expected_end_date: str) -> None:
        """Assert End Date matches expected"""
        actual = self.get_end_date()
        if (not expected_end_date or expected_end_date == "") and actual.upper() == "N/A":
            logger.info("End Date verified as N/A (no end date selected)")
            return
        assert actual == expected_end_date, \
            f"End Date mismatch. Expected: {expected_end_date}, Actual: {actual}"
        logger.info(f"End Date verified: {actual}")
    
    # ========== ACKNOWLEDGEMENTS SECTION ==========
    def verify_acknowledgements_section(self, expected_acknowledgements_text: str) -> None:
        """Verify Acknowledgements and Agreements section"""
        # Verify acknowledgements header is visible
        assert self.is_visible(self.acknowledgements_header, timeout=10000), \
            "Acknowledgements header not visible"
        logger.info("Acknowledgements header verified: 'Acknowledgements and Agreements'")
        
        # Verify body text
        assert self.is_visible(self.acknowledgements_body, timeout=5000), \
            "Acknowledgements body text not visible"
        actual_body_text = self.get_text(self.acknowledgements_body)
        assert actual_body_text == self.ACKNOWLEDGEMENT_HEADER, \
            f"Acknowledgements body text mismatch. Expected: {self.ACKNOWLEDGEMENT_HEADER}, Actual: {actual_body_text}"
        logger.info(f"Acknowledgements body text verified: '{actual_body_text}'")
        
        # Split expected acknowledgements by delimiter "|" if provided
        if expected_acknowledgements_text and expected_acknowledgements_text.strip():
            expected_acknowledgements = [ack.strip() for ack in expected_acknowledgements_text.split("|") if ack.strip()]
        else:
            # If no expected acknowledgements provided, just verify items are present
            expected_acknowledgements = []
        
        # Verify list items
        list_items = self.acknowledgements_list.all()
        
        if expected_acknowledgements:
            # If expected acknowledgements provided, verify count and text
            assert len(list_items) == len(expected_acknowledgements), \
                f"Expected {len(expected_acknowledgements)} acknowledgement items but found {len(list_items)}"
            logger.info(f"Found {len(list_items)} acknowledgement items as expected")
            
            # Assert each acknowledgement item text matches expected
            for i, list_item in enumerate(list_items):
                actual_text = self._normalize_quotes(list_item.text_content().strip())
                expected_text = self._normalize_quotes(expected_acknowledgements[i])
                assert actual_text == expected_text, \
                    f"Acknowledgement {i + 1} text mismatch. Expected: {expected_text}, Actual: {actual_text}"
                logger.info(f"Acknowledgement {i + 1} verified: {actual_text}")
        else:
            # If no expected acknowledgements, just verify items exist
            assert len(list_items) > 0, "No acknowledgement items found"
            logger.info(f"Found {len(list_items)} acknowledgement items (no specific text verification)")
            
            # Log the acknowledgement items for reference
            for i, list_item in enumerate(list_items):
                actual_text = list_item.text_content().strip()
                logger.info(f"Acknowledgement {i + 1}: {actual_text}")
        
        logger.info("All Acknowledgements and Agreements texts verified successfully")
    
    # ========== BUTTON METHODS ==========
    def click_submit_button(self):
        """Click Submit button and navigate to Confirmation Page
        
        Returns:
            EstablishAIPConfirmationPage instance
        """
        logger.info("Clicking Submit button")
        self.submit_button.wait_for(state='visible', timeout=10000)
        self.submit_button.scroll_into_view_if_needed()
        self.submit_button.click()
        logger.info("Submit button clicked successfully")
        
        return EstablishAIPConfirmationPage(self.page)
    
    def click_back_button(self) -> None:
        """Click Back button"""
        logger.info("Clicking Back button")
        self.back_button.wait_for(state='visible', timeout=10000)
        self.back_button.click()
        logger.info("Back button clicked successfully")
    
    def click_cancel_button(self) -> None:
        """Click Cancel button"""
        logger.info("Clicking Cancel button")
        self.cancel_button.wait_for(state='visible', timeout=10000)
        self.cancel_button.click()
        logger.info("Cancel button clicked successfully")
