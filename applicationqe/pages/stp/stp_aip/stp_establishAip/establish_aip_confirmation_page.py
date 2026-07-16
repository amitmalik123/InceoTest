"""
Establish AIP Confirmation Page Object
"""

from playwright.sync_api import Locator, Page
from pages.ewm.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_confirmation_locators import EstablishAIPConfirmationLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPConfirmationPage(BasePage):
    """Page object for Establish AIP Confirmation Page"""
    
    PAGE_NAME = "establishAIPConfirmationPage"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        ctx = self.active_root()
        loc = EstablishAIPConfirmationLocators
        
        # Submission modal
        self.submission_modal = ctx.locator(loc.SUBMISSION_MODAL)
        
        # Success banner
        self.success_banner = ctx.locator(loc.SUCCESS_BANNER)
        
        # Request Summary section
        self.request_summary_header = ctx.locator(loc.REQUEST_SUMMARY_HEADER)
        self.status_label = ctx.locator(loc.STATUS_LABEL)
        self.status_value = ctx.locator(loc.STATUS_VALUE)
        self.submission_datetime_label = ctx.locator(loc.SUBMISSION_DATETIME_LABEL)
        self.submission_datetime_value = ctx.locator(loc.SUBMISSION_DATETIME_VALUE)
        self.submitted_by_label = ctx.locator(loc.SUBMITTED_BY_LABEL)
        self.submitted_by_value = ctx.locator(loc.SUBMITTED_BY_VALUE)
        self.item_number_label = ctx.locator(loc.ITEM_NUMBER_LABEL)
        self.item_number_value = ctx.locator(loc.ITEM_NUMBER_VALUE)
        
        # Request Details section
        self.request_details_header = ctx.locator(loc.REQUEST_DETAILS_HEADER)
        self.request_type_value = ctx.locator(loc.REQUEST_TYPE_VALUE)
        self.delivery_method_value = ctx.locator(loc.DELIVERY_METHOD_VALUE)
        self.origination_value = ctx.locator(loc.ORIGINATION_VALUE)
        self.frequency_value = ctx.locator(loc.FREQUENCY_VALUE)
        self.amount_value = ctx.locator(loc.AMOUNT_VALUE)
        self.start_date_value = ctx.locator(loc.START_DATE_VALUE)
        self.end_date_value = ctx.locator(loc.END_DATE_VALUE)
        
        # Account Information
        self.account_info_label = ctx.locator(loc.ACCOUNT_INFO_LABEL)
        self.account_info_text = ctx.locator(loc.ACCOUNT_INFO_TEXT)
        
        # Close button
        self.close_button = ctx.locator(loc.CLOSE_BUTTON)
        
        # Loading indicators
        self.spinner_loading = ctx.locator(loc.SPINNER_LOADING)
        self.loading_overlay = ctx.locator(loc.LOADING_OVERLAY)
        
        # Wait for submission modal to disappear first
        self.wait_for_submission_modal_to_disappear()
        
        # Then wait for page load
        self.wait_for_page_load(page_verification)
    
    def wait_for_submission_modal_to_disappear(self) -> None:
        """Waits for the 'Your submission is in progress' modal to disappear"""
        logger.info("Waiting for submission modal to disappear...")
        try:
            if self.submission_modal.count() > 0:
                logger.info("Submission modal detected, waiting for it to disappear...")
                self.submission_modal.wait_for(state='hidden', timeout=60000)
                logger.info("Submission modal has disappeared")
            else:
                logger.info("Submission modal not detected, proceeding...")
        except Exception as e:
            logger.warning(f"Error while waiting for submission modal: {e}")
    
    def wait_for_page_load(self, page_verification: bool = True) -> None:
        """Wait for Confirmation Page to load"""
        logger.info("Waiting for Establish AIP Confirmation Page to load")
        
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
            success_banner_visible = self.is_visible(self.success_banner, timeout=10000)
            
            if success_banner_visible:
                logger.info(f"{self.PAGE_NAME} verification PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification FAILED")
    
    # ========== MODAL HANDLING ==========
    def verify_submission_modal_displayed(self) -> None:
        """Verifies the submission modal is displayed with correct text"""
        modal_visible = self.is_visible(self.submission_modal, timeout=10000)
        assert modal_visible, "Submission modal not visible"
        
        modal_text = self.get_text(self.submission_modal)
        assert modal_text == "Your submission is in progress.", f"Modal text mismatch: {modal_text}"
        logger.info(f"Submission modal verified: {modal_text}")
    
    # ========== SUCCESS BANNER ==========
    def verify_success_banner_displayed(self) -> None:
        """Verifies the success banner 'Request submitted successfully' is displayed"""
        self.success_banner.wait_for(state='visible', timeout=30000)
        
        banner_text = self.get_text(self.success_banner)
        assert banner_text == "Request submitted successfully", f"Success banner text mismatch: {banner_text}"
        logger.info(f"Success banner verified: {banner_text}")
    
    # ========== REQUEST SUMMARY SECTION ==========
    def verify_request_summary_section_visible(self) -> None:
        """Verify Request Summary section is visible"""
        assert self.is_visible(self.request_summary_header, timeout=10000), "Request Summary header not visible"
        logger.info("Request Summary section is visible")
    
    def get_status(self) -> str:
        """Get status value"""
        return self.get_text(self.status_value)
    
    def assert_status_complete(self) -> None:
        """Assert status is Complete"""
        actual_status = self.get_status()
        assert actual_status == "Complete", f"Status mismatch. Expected: Complete, Actual: {actual_status}"
        logger.info(f"Status verified: {actual_status}")
    
    def get_submission_datetime(self) -> str:
        """Get submission date/time"""
        return self.get_text(self.submission_datetime_value)
    
    def get_submitted_by(self) -> str:
        """Get submitted by (agent name)"""
        return self.get_text(self.submitted_by_value)
    
    def get_item_number(self) -> str:
        """Get item number"""
        return self.get_text(self.item_number_value)
    
    def assert_item_number_format(self) -> None:
        """Verifies Item Number starts with 'A' followed by digits"""
        item_number = self.get_item_number()
        assert item_number, "Item Number is empty"
        assert item_number[0] == 'A' and item_number[1:].isdigit(), \
            f"Item Number should start with 'A' followed by digits. Actual: {item_number}"
        logger.info(f"Item Number format verified: {item_number}")
    
    def assert_submitted_by(self, expected_agent_name: str) -> None:
        """Verifies Submitted By (Agent Name) matches expected value"""
        actual_submitted_by = self.get_submitted_by()
        assert actual_submitted_by == expected_agent_name, \
            f"Submitted By mismatch. Expected: {expected_agent_name}, Actual: {actual_submitted_by}"
        logger.info(f"Submitted By verified: {actual_submitted_by}")
    
    # ========== REQUEST DETAILS SECTION ==========
    def verify_request_details_section_visible(self) -> None:
        """Verify Request Details section is visible"""
        assert self.is_visible(self.request_details_header, timeout=10000), "Request Details header not visible"
        logger.info("Request Details section is visible")
    
    def get_request_type(self) -> str:
        """Get request type"""
        return self.get_text(self.request_type_value)
    
    def get_delivery_method(self) -> str:
        """Get delivery method"""
        return self.get_text(self.delivery_method_value)
    
    def get_origination(self) -> str:
        """Get origination"""
        return self.get_text(self.origination_value)
    
    def get_frequency(self) -> str:
        """Get frequency"""
        return self.get_text(self.frequency_value)
    
    def get_amount(self) -> str:
        """Get amount"""
        return self.get_text(self.amount_value)
    
    def get_start_date(self) -> str:
        """Get start date"""
        return self.get_text(self.start_date_value)
    
    def get_end_date(self) -> str:
        """Get end date"""
        return self.get_text(self.end_date_value)
    
    # ========== ASSERTION METHODS ==========
    def assert_request_type(self, expected_request_type: str) -> None:
        """Assert Request Type matches expected"""
        actual = self.get_request_type()
        assert actual == expected_request_type, f"Request Type mismatch. Expected: {expected_request_type}, Actual: {actual}"
        logger.info(f"Request Type verified: {actual}")
    
    def assert_delivery_method(self, expected_delivery_method: str) -> None:
        """Assert Delivery Method matches expected"""
        actual = self.get_delivery_method()
        assert actual == expected_delivery_method, f"Delivery Method mismatch. Expected: {expected_delivery_method}, Actual: {actual}"
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
        """Normalizes origination text"""
        if not text:
            return ""
        return text.replace(" - ", " ").strip()
    
    def assert_frequency(self, expected_frequency: str) -> None:
        """Assert Frequency matches expected"""
        actual = self.get_frequency()
        assert actual == expected_frequency, f"Frequency mismatch. Expected: {expected_frequency}, Actual: {actual}"
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
        assert actual == expected_start_date, f"Start Date mismatch. Expected: {expected_start_date}, Actual: {actual}"
        logger.info(f"Start Date verified: {actual}")
    
    def assert_end_date(self, expected_end_date: str) -> None:
        """Assert End Date matches expected"""
        actual = self.get_end_date()
        if (not expected_end_date or expected_end_date == "") and actual.upper() == "N/A":
            logger.info("End Date verified as N/A (no end date selected)")
            return
        assert actual == expected_end_date, f"End Date mismatch. Expected: {expected_end_date}, Actual: {actual}"
        logger.info(f"End Date verified: {actual}")
    
    # ========== ACCOUNT INFORMATION ==========
    def get_account_information_text(self) -> str:
        """Get account information text"""
        self.account_info_label.wait_for(state='visible', timeout=5000)
        return self.get_text(self.account_info_text)
    
    def verify_account_information(self, expected_account_info: str) -> None:
        """Verify account information matches expected"""
        actual = self.get_account_information_text()
        assert actual == expected_account_info, \
            f"Account Information mismatch. Expected: {expected_account_info}, Actual: {actual}"
        logger.info(f"Account Information verified: {actual}")
    
    # ========== COMPLETE VERIFICATION ==========
    def verify_confirmation_page_complete(self, expected_origination: str, expected_frequency: str,
                                         expected_amount: str, expected_start_date: str,
                                         expected_end_date: str) -> None:
        """Verifies all elements on the Confirmation Page"""
        self.verify_success_banner_displayed()
        self.verify_request_summary_section_visible()
        self.assert_status_complete()
        self.assert_item_number_format()
        
        self.verify_request_details_section_visible()
        self.assert_request_type("Automatic Investment Plan - Establish")
        self.assert_delivery_method("ACH")
        self.assert_origination(expected_origination)
        self.assert_frequency(expected_frequency)
        self.assert_amount(expected_amount)
        self.assert_start_date(expected_start_date)
        self.assert_end_date(expected_end_date)
        
        logger.info("Confirmation page verification completed successfully")
    
    # ========== CLOSE BUTTON ==========
    def click_close_button(self) -> None:
        """Clicks the Close button"""
        logger.info("Clicking Close button")
        self.close_button.wait_for(state='visible', timeout=5000)
        self.close_button.scroll_into_view_if_needed()
        self.close_button.click()
        logger.info("Close button clicked successfully")
