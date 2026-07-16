"""
Establish AIP Add AIP Page Object
"""

import allure
from typing import List
from playwright.sync_api import Locator, Page
from pages.ewm.base_page import BasePage
from pages.stp.stp_aip.stp_establishAip.locators.establish_aip_add_aip_locators import EstablishAIPAddAIPLocators
from pages.stp.stp_aip.stp_establishAip.establish_aip_summary_page import EstablishAIPSummaryPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EstablishAIPAddAIPPage(BasePage):
    """Page object for Establish AIP Add AIP Page"""
    
    PAGE_NAME = "addAIPPage"
    
    # All available frequency options in order
    ALL_FREQUENCIES = ["Weekly", "Bi-Weekly", "Monthly", "Bi-Monthly", "Quarterly", "Annually"]
    
    # Maximum number of months to navigate forward
    MAX_MONTHS_TO_NAVIGATE = 12
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        ctx = self.active_root()
        loc = EstablishAIPAddAIPLocators
        
        # Header elements
        self.header = ctx.locator(loc.HEADER)
        self.add_aip_title = ctx.locator(loc.ADD_AIP_TITLE)
        
        # Contribution
        self.contribution_amount_input = ctx.locator(loc.CONTRIBUTION_AMOUNT_INPUT)
        
        # Calendar icon buttons
        self.start_date_calendar_btn = ctx.locator(loc.START_DATE_CALENDAR_BTN)
        self.end_date_calendar_btn = ctx.locator(loc.END_DATE_CALENDAR_BTN)
        
        # Date picker days
        self.enabled_days = ctx.locator(loc.ENABLED_DAYS)
        self.disabled_days = ctx.locator(loc.DISABLED_DAYS)
        
        # Date picker controls
        self.next_month_arrow = ctx.locator(loc.NEXT_MONTH_ARROW)
        self.date_picker_popup = ctx.locator(loc.DATE_PICKER_POPUP)
        
        # Signature options
        self.signature_header = ctx.locator(loc.SIGNATURE_HEADER)
        self.signature_option_labels = ctx.locator(loc.SIGNATURE_OPTION_LABELS)
        self.next_button = ctx.locator(loc.NEXT_BUTTON)
        
        # Account Information section
        self.account_info_label = ctx.locator(loc.ACCOUNT_INFO_LABEL)
        self.account_info_text = ctx.locator(loc.ACCOUNT_INFO_TEXT)
        
        # Loading indicators
        self.spinner_loading = ctx.locator(loc.SPINNER_LOADING)
        self.loading_overlay = ctx.locator(loc.LOADING_OVERLAY)
        
        # Wait for page load
        self.wait_for_page_load(page_verification)
    
    def wait_for_page_load(self, page_verification: bool = True) -> None:
        """Wait for Add AIP Page to load"""
        logger.info("Waiting for Add AIP Page to load")
        
        # Wait for spinner to disappear
        try:
            if self.spinner_loading.count() > 0:
                self.spinner_loading.wait_for(state='hidden', timeout=120000)
                logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.warning(f"Spinner wait failed: {e}")
        
        # Wait for loading overlay to disappear
        try:
            if self.loading_overlay.count() > 0:
                self.loading_overlay.wait_for(state='hidden', timeout=120000)
                logger.info("Loading overlay disappeared")
        except Exception as e:
            logger.warning(f"Loading overlay wait failed: {e}")
        
        # Page verification
        if page_verification:
            header_visible = self.is_visible(self.header, timeout=5000)
            title_visible = self.is_visible(self.add_aip_title, timeout=5000)
            
            if header_visible and title_visible:
                logger.info(f"{self.PAGE_NAME} verification PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification FAILED")
    
    # ========== CONTRIBUTION ==========
    def enter_contribution_amount(self, amount: str) -> None:
        """Enter contribution amount"""
        logger.info(f"Entering contribution amount: {amount}")
        
        self.contribution_amount_input.wait_for(state='visible', timeout=5000)
        self.contribution_amount_input.clear()
        self.contribution_amount_input.fill(amount)
        
        logger.info(f"Contribution amount entered: {amount}")
    
    def get_contribution_amount(self) -> str:
        """Get the contribution amount"""
        amount = self.contribution_amount_input.input_value()
        logger.info(f"Retrieved contribution amount: {amount}")
        return amount
    
    # ========== FREQUENCY ==========
    def select_frequency(self, frequency: str) -> None:
        """Validate all frequency radio buttons and select the specified frequency"""
        logger.info(f"Starting frequency validation - will test all options and end with: {frequency}")
        
        # Wait for first frequency option
        first_radio = self.page.locator("//input[@name='frequency' and @value='Weekly']")
        first_radio.wait_for(state='visible', timeout=5000)
        
        # Loop through all frequency options to verify each is selectable
        for freq in self.ALL_FREQUENCIES:
            self._click_frequency_option_fast(freq)
        
        # Finally select the desired frequency
        final_frequency = self._normalize_frequency_value(frequency)
        self._click_frequency_option_fast(final_frequency)
        logger.info(f"All frequency options verified. Final selection: {final_frequency}")
    
    def _normalize_frequency_value(self, frequency: str) -> str:
        """Normalizes user input to proper case for xpath matching"""
        freq_map = {
            "weekly": "Weekly",
            "bi-weekly": "Bi-Weekly",
            "monthly": "Monthly",
            "bi-monthly": "Bi-Monthly",
            "quarterly": "Quarterly",
            "annually": "Annually"
        }
        return freq_map.get(frequency.lower(), frequency)
    
    def _click_frequency_option_fast(self, frequency_value: str) -> None:
        """Quickly clicks a frequency radio button"""
        radio_input = self.page.locator(f"//input[@name='frequency' and @value='{frequency_value}']")
        
        # Click the radio button using JavaScript
        self.page.evaluate("el => el.click()", radio_input.element_handle())
        
        # Verify selection
        if not radio_input.is_checked():
            # Fallback: click the label
            label = radio_input.locator("xpath=ancestor::label")
            self.page.evaluate("el => el.click()", label.element_handle())
        
        logger.info(f"Selected frequency: {frequency_value}")
    
    def get_selected_frequency_text(self) -> str:
        """Get the selected frequency label text"""
        all_radio_buttons = self.page.locator("//input[@name='frequency']")
        
        for i in range(all_radio_buttons.count()):
            radio = all_radio_buttons.nth(i)
            if radio.is_checked():
                label = radio.locator("xpath=ancestor::label//span[contains(@class, 'MuiFormControlLabel-label')]")
                frequency_text = label.text_content()
                logger.info(f"Retrieved selected frequency text: {frequency_text}")
                return frequency_text
        
        raise RuntimeError("No frequency option is currently selected")
    
    # ========== DATE SELECTION ==========
    def dismiss_date_picker_if_open(self) -> None:
        """Dismisses any open date picker popup by pressing Escape key"""
        try:
            if self.is_visible(self.date_picker_popup, timeout=2000):
                logger.info("Date picker is open, dismissing it...")
                self.page.keyboard.press("Escape")
                self.date_picker_popup.wait_for(state='hidden', timeout=5000)
                logger.info("Date picker dismissed")
        except Exception as e:
            logger.warning(f"Error while dismissing date picker: {e}")
    
    def select_start_and_end_dates(self) -> None:
        """Select start and end dates from calendar"""
        try:
            # Start Date
              # Debug pause to inspect the state before date selection
            logger.info("Selecting start date...")
            self.start_date_calendar_btn.wait_for(state='visible', timeout=10000)
            allure.attach(self.page.screenshot(), name="Start Date - Before Calendar Open", attachment_type=allure.attachment_type.PNG)
            self.start_date_calendar_btn.click()
            allure.attach(self.page.screenshot(), name="Start Date - Calendar Opened", attachment_type=allure.attachment_type.PNG)

            self.enabled_days.first.wait_for(state='visible', timeout=5000)

            # Navigate to find enabled days for start date
            start_enabled_days = self._find_enabled_days_navigating_months()

            if not start_enabled_days:
                raise RuntimeError("No enabled start dates found after navigating months")

            # Click the first enabled day
            allure.attach(self.page.screenshot(), name="Start Date - Before Day Click", attachment_type=allure.attachment_type.PNG)
            self._click_date_with_retry(0)
            allure.attach(self.page.screenshot(), name="Start Date - Selected", attachment_type=allure.attachment_type.PNG)
            logger.info("Start date selected")

            # End Date
            logger.info("Selecting end date...")
            self.end_date_calendar_btn.wait_for(state='visible', timeout=10000)
            allure.attach(self.page.screenshot(), name="End Date - Before Calendar Open", attachment_type=allure.attachment_type.PNG)
            self.end_date_calendar_btn.click()
            allure.attach(self.page.screenshot(), name="End Date - Calendar Opened", attachment_type=allure.attachment_type.PNG)

            # Wait for end date to be ready (wait for calendar update)
            self.page.wait_for_timeout(1000)

            # Navigate to find enabled days for end date
            end_enabled_days = self._find_enabled_days_navigating_months()

            if not end_enabled_days:
                raise RuntimeError("No enabled end dates found after navigating months")

            # Click the first enabled day
            allure.attach(self.page.screenshot(), name="End Date - Before Day Click", attachment_type=allure.attachment_type.PNG)
            self._click_date_with_retry(0)
            allure.attach(self.page.screenshot(), name="End Date - Selected", attachment_type=allure.attachment_type.PNG)
            logger.info("End date selected")

        except Exception as e:
            allure.attach(self.page.screenshot(), name="Date Selection - Failure State", attachment_type=allure.attachment_type.PNG)
            raise RuntimeError(f"Failed to select Start/End dates: {e}")
    
    def _find_enabled_days_navigating_months(self) -> List:
        """Finds enabled days in the date picker, navigating to next months if needed"""
        enabled_days_count = self.enabled_days.count()
        months_navigated = 0
        
        while enabled_days_count == 0 and months_navigated < self.MAX_MONTHS_TO_NAVIGATE:
            # Check if next month arrow is available and click it
            if self.next_month_arrow.count() > 0:
                self.next_month_arrow.first.click()
                logger.info("Clicked next month arrow to find enabled dates")
                
                # Wait for calendar to update
                self.page.wait_for_timeout(1000)
                
                # Re-check for enabled days
                enabled_days_count = self.enabled_days.count()
                months_navigated += 1
            else:
                logger.warning("Next month arrow not available")
                break
        
        if enabled_days_count == 0:
            logger.error(f"No enabled days found after navigating {months_navigated} months")
        else:
            logger.info(f"Found {enabled_days_count} enabled days after navigating {months_navigated} month(s)")
        
        return enabled_days_count > 0
    
    def _click_date_with_retry(self, index: int, max_retries: int = 3) -> None:
        """Clicks a date element with retry logic to handle stale element references"""
        for attempt in range(max_retries):
            try:
                # Get the date element
                date_element = self.enabled_days.nth(index)
                date_element.click()
                return
                
            except Exception as e:
                logger.warning(f"Stale element on attempt {attempt + 1}, retrying...")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to click date after {max_retries} attempts: {e}")
                self.page.wait_for_timeout(500)
    
    def get_start_date(self) -> str:
        """Get the start date"""
        start_date_input = self.page.locator("(//input[@type='text'])[2]")
        start_date = start_date_input.input_value()
        logger.info(f"Retrieved start date: {start_date}")
        return start_date
    
    def get_end_date(self) -> str:
        """Get the end date"""
        end_date_input = self.page.locator("(//input[@type='text'])[3]")
        end_date = end_date_input.input_value()
        logger.info(f"Retrieved end date: {end_date}")
        return end_date
    
    # ========== SIGNATURE OPTIONS ==========
    def select_and_verify_signature_option_and_click_next(self, option: str):
        """Select signature option, verify, and click Next
        
        Returns:
            EstablishAIPSummaryPage instance
        """
        # Header verification
        self.signature_header.wait_for(state='visible', timeout=10000)
        
        stable_text = option.split("–")[0].strip()
        
        labels = self.signature_option_labels.all()
        found = False
        
        for label in labels:
            label_text = label.text_content()
            
            if stable_text in label_text:
                label.click()
                logger.info(f"Selecting signature option: {label_text}")
                
                # Wait for selection to register
                self.page.wait_for_timeout(500)
                
                # Verify selection - find radio input within the parent container
                parent_container = label.locator("xpath=ancestor::div[@class='sc-cDvQBt EZYBk']")
                radio_input = parent_container.locator("input[type='radio']").first
                
                try:
                    if not radio_input.is_checked(timeout=5000):
                        raise AssertionError("Signature option not selected")
                except Exception as e:
                    logger.warning(f"Could not verify radio selection: {e}")
                    # Continue anyway since we clicked the label
                
                found = True
                break
        
        if not found:
            raise RuntimeError(f"Signature option not found: {option}")
        
        # Dismiss any open date picker
        self.dismiss_date_picker_if_open()
        
        # Click NEXT button
        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.scroll_into_view_if_needed()
        self.next_button.click()
        logger.info("Clicked NEXT button after signature selection")
        
        return EstablishAIPSummaryPage(self.page)
    
    # ========== ACCOUNT INFORMATION ==========
    def get_account_information_text(self) -> str:
        """Get account information text"""
        self.account_info_label.wait_for(state='visible', timeout=10000)
        account_info = self.get_text(self.account_info_text)
        logger.info(f"Account Information: {account_info}")
        return account_info
