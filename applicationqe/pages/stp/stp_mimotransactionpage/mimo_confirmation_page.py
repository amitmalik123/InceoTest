from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_mimotransactionpage.locators.mimo_confirmation_locators import MIMOConfirmationLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOConfirmationPage(BasePage):
    PAGE_NAME = "MIMO Confirmation Page"
    
    def __init__(self, page: Page):
        super().__init__(page)
        loc = MIMOConfirmationLocators
        
        # Page elements
        self.page_title: Locator = page.locator(loc.PAGE_TITLE)
        self.status_completed: Locator = page.locator(loc.STATUS_COMPLETED)
        self.confirmation_screen_status: Locator = page.locator(loc.CONFIRMATION_SCREEN_STATUS)
        
        # Account Information
        self.account_info_section: Locator = page.locator(loc.ACCOUNT_INFO_SECTION)
        self.account_name: Locator = page.locator(loc.ACCOUNT_NAME)
        self.account_number: Locator = page.locator(loc.ACCOUNT_NUMBER)
        self.account_strategy: Locator = page.locator(loc.ACCOUNT_STRATEGY)
        self.advisor_id: Locator = page.locator(loc.ADVISOR_ID)
        
        # Transaction Summary section
        self.status_section: Locator = page.locator(loc.STATUS_SECTION)
        self.status_section_label: Locator = self.status_section.locator(loc.STATUS_SECTION_LABEL)
        self.status_section_text: Locator = self.status_section.locator(loc.STATUS_SECTION_TEXT)

        self.date_section: Locator = page.locator(loc.DATE_SECTION)
        self.date_section_label: Locator = self.date_section.locator(loc.DATE_SECTION_LABEL)
        self.date_section_text: Locator = self.date_section.locator(loc.DATE_SECTION_TEXT)

        self.submitted_by_section: Locator = page.locator(loc.SUBMITTED_BY_SECTION)
        self.submitted_by_section_label: Locator = self.submitted_by_section.locator(loc.SUBMITTED_BY_SECTION_LABEL)
        self.submitted_by_section_text: Locator = self.submitted_by_section.locator(loc.SUBMITTED_BY_SECTION_TEXT)

        self.item_number_section: Locator = page.locator(loc.ITEM_NUMBER_SECTION)

        # Request Details
        self.request_details_section: Locator = page.locator(loc.REQUEST_DETAILS_SECTION)
        self.request_type_container: Locator = page.locator(loc.REQUEST_TYPE_CONTAINER)
        self.request_type_title: Locator = self.request_type_container.locator(loc.REQUEST_TYPE_TITLE)
        self.request_type_value: Locator = self.request_type_container.locator(loc.REQUEST_TYPE_VALUE)

        self.delivery_method: Locator = page.locator(loc.DELIVERY_METHOD)
        self.frequency: Locator = page.locator(loc.FREQUENCY)
        self.amount: Locator = page.locator(loc.AMOUNT)
        
        # Contribution specific
        self.contribution_amount: Locator = page.locator(loc.CONTRIBUTION_AMOUNT)
        self.contribution_date: Locator = page.locator(loc.CONTRIBUTION_DATE)
        self.contribution_reason: Locator = page.locator(loc.CONTRIBUTION_REASON)
        
        # Destination section
        self.destination_section: Locator = page.locator(loc.DESTINATION_SECTION)
        
        # Buttons
        self.print_button: Locator = page.locator("//button[@aria-label='print-link-button']")
        self.close_button: Locator = page.locator("//div[@aria-label='confirmation-screen-buttons']//button")
        
        # Spinner
        self.loading_spinner: Locator = page.locator("//div[@data-testid='loading-spinner']")
    
    def wait_for_page_load(self):
        """Wait for MIMO Confirmation Page to load"""
        logger.info("Waiting for MIMO Confirmation Page to load")
        
        # Wait for spinner to disappear
        spinner = self.page.locator("//div[@data-testid='loading-spinner']")
        if spinner.count() > 0:
            spinner.wait_for(state='hidden', timeout=30000)
        
        # Wait for status completed
        self.status_completed.wait_for(state='visible', timeout=120000)
        logger.info("MIMO Confirmation Page loaded")
    
    def get_page_title(self) -> str:
        """Get confirmation page title"""
        return self.page_title.inner_text()
    
    def get_confirmation_screen_status(self) -> str:
        """Get confirmation screen status text"""
        return self.confirmation_screen_status.inner_text()
    
    def get_account_name(self) -> str:
        """Get account name"""
        return self.account_name.inner_text()
    
    def get_account_number(self) -> str:
        """Get account number"""
        return self.account_number.inner_text()
    
    def get_account_strategy(self) -> str:
        """Get account strategy"""
        return self.account_strategy.inner_text()
    
    def get_advisor_id(self) -> str:
        """Get advisor ID"""
        return self.advisor_id.inner_text()
    
    def get_status_section_title(self) -> str:
       return self.status_section_label.inner_text()
    
    def get_status_section_text(self) -> str:
        return self.status_section_text.inner_text()
    
    def get_date_section_title(self) -> str:
        """Get date section title"""
        return self.date_section_label.inner_text()
    
    def get_date_section_text(self) -> str:
        """Get date section text (actual date)"""
        return self.date_section_text.inner_text()
    
    def get_submitted_by_section_title(self) -> str:
        """Get submitted by section title"""
        return self.submitted_by_section_label.inner_text()
    
    def get_submitted_by_section_text(self) -> str:
        """Get submitted by section text"""
        return self.submitted_by_section_text.inner_text()
    
    def _get_confirmation_field_value(self, label: str) -> str:
        locator = self.page.locator(
            f"//div[@aria-label='confirmation-screen-summary']"
            f"//div[h3[normalize-space(text())='{label}']]/*[self::p or self::a]"
        )
        return locator.inner_text()

    def _get_confirmation_field_label(self, label: str) -> str:
        locator = self.page.locator(
            f"//div[@aria-label='confirmation-screen-summary']"
            f"//div[h3[normalize-space(text())='{label}']]/h3"
        )
        return locator.inner_text()

    def get_item_number_section_title(self) -> str:
        return self._get_confirmation_field_label("Item number")

    def get_item_number_section_text(self) -> str:
        return self._get_confirmation_field_value("Item number")

    def get_request_type_title(self) -> str:
        return self._get_confirmation_field_label("Request Type")

    def get_request_type_text(self) -> str:
        return self._get_confirmation_field_value("Request Type")

    def get_delivery_method_title(self) -> str:
        return self._get_confirmation_field_label("Delivery Method")

    def get_delivery_method_text(self) -> str:
        return self._get_confirmation_field_value("Delivery Method")

    def get_frequency_title(self) -> str:
        return self._get_confirmation_field_label("Frequency")

    def get_frequency_text(self) -> str:
        return self._get_confirmation_field_value("Frequency")

    def get_amount_title(self) -> str:
        return self._get_confirmation_field_label("Amount")

    def get_amount_text(self) -> str:
        return self._get_confirmation_field_value("Amount")
    
    def get_contribution_amount_title(self) -> str:
        """Get contribution amount title"""
        text = self.contribution_amount.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_contribution_amount_text(self) -> str:
        """Get contribution amount text"""
        text = self.contribution_amount.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_contribution_date_title(self) -> str:
        """Get contribution date title"""
        text = self.contribution_date.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_contribution_date_text(self) -> str:
        """Get contribution date text"""
        text = self.contribution_date.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_contribution_reason_title(self) -> str:
        """Get contribution reason title"""
        text = self.contribution_reason.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_contribution_reason_text(self) -> str:
        """Get contribution reason text"""
        text = self.contribution_reason.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_bank_name_value(self) -> str:
        """Get bank name value"""
        return self.bank_name.inner_text()
    
    def get_bank_account_no_value(self) -> str:
        """Get bank account number value"""
        return self.bank_account_number.inner_text()
    
    def print_button_enabled(self) -> bool:
        """Check if print button is enabled"""
        return self.print_button.is_enabled(timeout=5000)
    
    def click_print_button(self) -> int:
        """Click print button and return number of tabs"""
        logger.info("Clicking Print button")
        parent_window = self.page.context.pages[0]
        self.print_button.click()
        
        self.page.wait_for_timeout(2000)
        tabs = self.page.context.pages
        logger.info(f"Total opened windows: {len(tabs)}")
        
        # Close the new tab if opened
        if len(tabs) > 1:
            tabs[-1].close()
        
        return len(tabs)
    
    def click_item_number(self):
        """Click item number link"""
        logger.info("Clicking Item Number link")
        item_number_link = self.item_number_section.locator("//a")
        item_number_link.click()
        
        # Switch to the new tab
        self.page.wait_for_timeout(2000)
        new_page = self.page.context.pages[-1]
        return new_page
    
    def click_close_button(self):
        """Click close button"""
        logger.info("Clicking Close button")
        self.close_button.click()
    
    def get_distribution_reason_title(self) -> str:
        """Get distribution reason section title"""
        text = self.distribution_reason.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_distribution_reason_text(self) -> str:
        """Get distribution reason section text/value"""
        text = self.distribution_reason.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_federal_tax_withholding_title(self) -> str:
        """Get federal tax withholding section title"""
        text = self.federal_tax_withholding.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_federal_tax_withholding_text(self) -> str:
        """Get federal tax withholding section text/value"""
        text = self.federal_tax_withholding.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_state_tax_withholding_title(self) -> str:
        """Get state tax withholding section title"""
        text = self.state_tax_withholding.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_state_tax_withholding_text(self) -> str:
        """Get state tax withholding section text/value"""
        text = self.state_tax_withholding.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_state_of_residence_title(self) -> str:
        """Get state of residence section title"""
        text = self.state_of_residence.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_state_of_residence_text(self) -> str:
        """Get state of residence section text/value"""
        text = self.state_of_residence.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_net_distribution_amount_title(self) -> str:
        """Get net distribution amount section title"""
        text = self.net_distribution_amount.inner_text()
        return text.split('\n')[0] if '\n' in text else ""
    
    def get_net_distribution_amount_text(self) -> str:
        """Get net distribution amount section text/value"""
        text = self.net_distribution_amount.inner_text()
        return text.split('\n')[-1] if '\n' in text else text
    
    def get_request_details_header(self) -> str:
        """Get REQUEST DETAILS section header text for Cancel SWP"""
        header = self.page.locator("//div[@aria-label='request-details-section']//h3[text()='Request Details']")
        return header.inner_text()
    
    def get_request_details_values(self) -> str:
        """Get all REQUEST DETAILS section values as text for Cancel SWP"""
        request_details_section = self.page.locator("//div[@aria-label='request-details-section']")
        return request_details_section.inner_text()
    
    def get_cancelled_date(self) -> str:
        """Get cancellation date from REQUEST DETAILS section"""
        # Assuming cancellation date is in a specific locator, adjust as needed
        cancellation_date = self.page.locator("//div[@aria-label='confirmation-screen-cancellation-date']")
        if cancellation_date.count() > 0:
            text = cancellation_date.inner_text()
            return text.split('\n')[-1] if '\n' in text else text
        return ""
