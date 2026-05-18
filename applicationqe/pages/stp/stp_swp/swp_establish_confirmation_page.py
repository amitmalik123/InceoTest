from datetime import datetime

from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishConfirmationPage(BasePage):
    """SWP Establish Confirmation Page - Page Object Model"""

    PAGE_NAME = "SWP Establish Confirmation Page"

    def __init__(self, page: Page):
        super().__init__(page)
        
        # Header/Navigation
        self.confirmation_heading: Locator = page.locator("//span[text()='Request Confirmation']")
        self.confirmation_header_details: Locator = page.locator("//span[text()='Account Information']/parent::div/parent::div/parent::div")
        self.confirmation_screen_status: Locator = page.locator("//div[@aria-label='confirmation-screen-status']")
        
        # Transaction Summary section elements
        self.status: Locator = page.locator("//h3[text()='Status:']/parent::div/span")
        self.date: Locator = page.locator("//h3[text()='Submission date and time:']/parent::div/span")
        self.submitted_by: Locator = page.locator("//h3[text()='Submitted by:']/parent::div/span")
        self.item_number: Locator = page.locator("//h3[text()='Item number:']/parent::div/a")
        
        # Section titles (h3 elements)
        self.status_title: Locator = page.locator("//h3[text()='Status:']")
        self.date_title: Locator = page.locator("//h3[text()='Submission date and time:']")
        self.submitted_by_title: Locator = page.locator("//h3[text()='Submitted by:']")
        self.item_number_title: Locator = page.locator("//h3[text()='Item number:']")
        
        # Request Details
        self.confirmation_request_details: Locator = page.locator("//h3[text()='Request Details']/parent::div")
        self.item_number_link: Locator = page.locator("//h3[text()='Item number:']/parent::div/child::a")
        
        # Spinner
        self.loading_spinner: Locator = page.locator("//div[@data-testid='loading-spinner']")

    def get_header_section_text(self) -> str:
        """Get header section text from confirmation page"""
        logger.info("Getting header section text")
        
        # Wait for page to load
        self.page.wait_for_load_state('domcontentloaded')
        
        # Wait for confirmation heading to be visible
        self.confirmation_heading.wait_for(state='visible', timeout=30000)
        
        # Wait a bit for content to settle
        self.page.wait_for_timeout(1000)
        
        # Get header details text
        header_text = self.confirmation_header_details.inner_text()
        logger.info(f"Header section text: {header_text}")
        
        return header_text

    def get_item_number(self) -> str:
        """Get item number from confirmation page"""
        logger.info("Getting item number")
        self.item_number.wait_for(state='visible', timeout=10000)
        item_num = self.item_number.inner_text()
        logger.info(f"Item number: {item_num}")
        return item_num

    def get_confirmation_screen_status(self) -> str:
        """Get confirmation screen status"""
        return self.confirmation_screen_status.inner_text()

    def get_status_text(self) -> str:
        """Get status value text"""
        return self.status.inner_text()

    def get_status_title(self) -> str:
        """Get status section title"""
        return self.status_title.inner_text()

    def get_date_text(self) -> str:
        """Get date value text"""
        return self.date.inner_text()

    def get_date_title(self) -> str:
        """Get date section title"""
        return self.date_title.inner_text()

    def get_submitted_by_text(self) -> str:
        """Get submitted by value text"""
        return self.submitted_by.inner_text()

    def get_submitted_by_title(self) -> str:
        """Get submitted by section title"""
        return self.submitted_by_title.inner_text()

    def get_item_number_text(self) -> str:
        """Get item number value text"""
        return self.item_number.inner_text()

    def get_item_number_title(self) -> str:
        """Get item number section title"""
        return self.item_number_title.inner_text()

    def click_item_number_link(self):
        """Click on item number link. Handles same-page navigation and new-tab cases."""
        logger.info("Clicking item number link")

        # Check whether the link has a target that opens a new tab
        target = self.item_number_link.get_attribute("target")
        opens_new_tab = target in ("_blank", "_new")

        if opens_new_tab:
            with self.page.context.expect_page(timeout=30000) as new_page_info:
                self.item_number_link.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=30000)
        else:
            self.item_number_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            new_page = self.page

        logger.info(f"Navigated to: {new_page.url}")

        for i in range(5):
            logger.info(f"Refreshing page {i + 1}/5")
            new_page.reload()
            new_page.wait_for_timeout(5000)

        logger.info("Item number link clicked and page refreshed")
        return new_page

    def get_request_details_text(self) -> str:
        """Get request details section text - matches Java validateRequestDetailsForSWPConfirmation"""
        logger.info("Getting request details text")
        self.confirmation_request_details.wait_for(state='visible', timeout=10000)
        request_details = self.confirmation_request_details.inner_text()
        logger.info(f"Request details: {request_details}")
        return request_details

    def validate_header_section(self, advisor_id: str = '') -> None:
        """Validate header section contains Account Information and Advisor ID"""
        self.page.wait_for_timeout(20000)
        header_details = self.get_header_section_text()
        logger.info(f"Header details: {header_details}")

        assert "Account Information" in header_details, \
            f"Validation of the Headers failed. Expected 'Account Information' in: {header_details}"
        logger.info("'Account Information' header validated")

        assert "Advisor ID" in header_details, \
            f"Validation of the Headers failed. Expected 'Advisor ID' in: {header_details}"
        logger.info("'Advisor ID' header validated")

        if advisor_id:
            assert advisor_id in header_details, \
                f"Validation of the Value failed. Expected advisor ID '{advisor_id}' in: {header_details}"
            logger.info(f"Advisor ID value '{advisor_id}' validated")
        else:
            logger.warning("Advisor ID not provided, skipping value validation")

        logger.info("Header Section validation completed")

    def validate_transaction_summary(
        self,
        section_name: str,
        status_header: str,
        status_value: str,
        date_header: str,
        submitted_by_header: str,
        item_number_header: str,
        login_user_role: str = '',
        login_user_name: str = '',
        admin_name: str = ''
    ) -> str:
        """Validate Transaction Summary section details. Returns the actual status value."""
        current_date = datetime.now().strftime("%m/%d/%Y")

        # Status header
        actual_status_title = self.get_status_title()
        assert status_header in actual_status_title, \
            f"Validation of {section_name} section Label failed. Expected: '{status_header}', Got: '{actual_status_title}'"
        logger.info(f"Status header validated: {actual_status_title}")

        # Status value
        actual_status_value = self.get_status_text()
        expected_statuses = {
            "complete": "Complete",
            "in process - pending settlement": "In Process - Pending Settlement",
            "awaiting advisor submission": "Awaiting Advisor Submission",
        }
        expected = expected_statuses.get(status_value.lower())
        if expected:
            assert actual_status_value == expected, \
                f"Validation of {section_name} section Value failed. Expected: '{expected}', Got: '{actual_status_value}'"
        else:
            assert status_value in actual_status_value, \
                f"Validation of {section_name} section Value failed. Expected: '{status_value}', Got: '{actual_status_value}'"
        logger.info(f"Status value validated: {actual_status_value}")

        # Date header
        actual_date_title = self.get_date_title()
        assert date_header in actual_date_title, \
            f"Validation of {section_name} section Label failed. Expected: '{date_header}', Got: '{actual_date_title}'"
        logger.info(f"Date header validated: {actual_date_title}")

        # Date value
        actual_date_value = self.get_date_text()
        assert current_date in actual_date_value, \
            f"Validation of {section_name} section Value failed. Expected date '{current_date}' in: '{actual_date_value}'"
        logger.info(f"Date value validated: {actual_date_value}")

        # Submitted By header
        actual_submitted_by_title = self.get_submitted_by_title()
        assert submitted_by_header in actual_submitted_by_title, \
            f"Validation of {section_name} section Label failed. Expected: '{submitted_by_header}', Got: '{actual_submitted_by_title}'"
        logger.info(f"Submitted By header validated: {actual_submitted_by_title}")

        # Submitted By value
        actual_submitted_by_value = self.get_submitted_by_text()
        logger.info(f"Submitted By value: {actual_submitted_by_value}")
        if "Office" in login_user_role and admin_name:
            assert actual_submitted_by_value == admin_name, \
                f"Validation of {section_name} section Value failed. Expected: '{admin_name}', Got: '{actual_submitted_by_value}'"
            logger.info(f"Submitted By value validated (Office user): {actual_submitted_by_value}")
        elif login_user_name:
            assert actual_submitted_by_value == login_user_name, \
                f"Validation of {section_name} section Value failed. Expected: '{login_user_name}', Got: '{actual_submitted_by_value}'"
            logger.info(f"Submitted By value validated: {actual_submitted_by_value}")
        else:
            logger.warning("Login user name not found, skipping Submitted By value validation")

        # Item Number header
        actual_item_number_title = self.get_item_number_title()
        assert item_number_header in actual_item_number_title, \
            f"Validation of {section_name} section Label failed. Expected: '{item_number_header}', Got: '{actual_item_number_title}'"
        logger.info(f"Item Number header validated: {actual_item_number_title}")

        logger.info(f"{section_name} section validation completed")
        return actual_status_value

    def verify_success_message(self, status_message: str) -> None:
        """Verify confirmation screen success message"""
        actual_status = self.get_confirmation_screen_status()
        assert actual_status == status_message, \
            f"Validation of Confirmation Screen Status failed. Expected: '{status_message}', Got: '{actual_status}'"
        logger.info(f"Confirmation screen status validated: {actual_status}")

    def validate_all_header_details(
        self,
        request_type: str,
        method: str,
        additional_details: list = None
    ) -> None:
        """Validate all header details and values on the confirmation page"""
        request_details = self.get_request_details_text()
        logger.info(f"Request details: {request_details}")

        if additional_details:
            for detail in additional_details:
                if detail:
                    assert detail in request_details, \
                        f"Confirmation page details validation failed. Expected '{detail}' in: {request_details}"
                    logger.info(f"Confirmation page details includes \u2192 {detail}")

        assert request_type in request_details, \
            f"Request Type value validation failed. Expected '{request_type}' in: {request_details}"
        logger.info(f"Request Type validated: {request_type}")

        assert method in request_details, \
            f"Method Type value validation failed. Expected '{method}' in: {request_details}"
        logger.info(f"Method Type validated: {method}")

        logger.info("Validated Confirmation page details for the SWP Establish request")

    def verify_page_loaded(self) -> bool:
        """Verify SWP Establish Confirmation Page is loaded"""
        try:
            self.confirmation_heading.wait_for(state='visible', timeout=30000)
            logger.info(f"{self.PAGE_NAME} verification PASSED")
            return True
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification FAILED: {e}")
            return False
