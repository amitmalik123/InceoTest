from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_mimotransactionpage.locators.mimo_transaction_request_locators import MIMOTransactionRequestLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOTransactionRequestPage(BasePage):
    PAGE_NAME = "MIMO Landing Page"
    
    def __init__(self, page: Page):
        super().__init__(page)
        loc = MIMOTransactionRequestLocators
        self.header_item: Locator = page.locator(loc.HEADER_ITEM)
        self.next_button: Locator = page.locator(loc.NEXT_BUTTON)
        self.cancel_button: Locator = page.locator(loc.CANCEL_BUTTON)
        self.instructions_on_file_heading: Locator = page.locator(loc.INSTRUCTIONS_ON_FILE_HEADING)
        self.instructions_message: Locator = page.locator(loc.INSTRUCTIONS_MESSAGE)
    
    def wait_for_page_load(self):
        """Wait for MIMO Transaction Request Page to load"""
        logger.info("Waiting for MIMO Transaction Request Page to load")
        
        # Wait for spinner to disappear (primary indicator of page readiness)
        spinner = self.page.locator("//div[@data-testid='loading-spinner']")
        if spinner.count() > 0:
            try:
                spinner.wait_for(state='hidden', timeout=30000)
                logger.info("Loading spinner disappeared")
            except Exception as e:
                logger.warning(f"Spinner wait failed: {e}")
        
        # Try to wait for instructions heading (soft wait - may not exist on all flows like Contribution)
        try:
            if self.instructions_on_file_heading.count() > 0:
                self.instructions_on_file_heading.wait_for(state='visible', timeout=5000)
                logger.info("Instructions on file heading found and visible")
        except Exception as e:
            logger.info(f"Instructions heading not visible (expected for some flows): {e}")
        
        # Wait a brief moment for page stabilization
        self.page.wait_for_timeout(500)
        logger.info("MIMO Transaction Request Page loaded")

    def get_instructions_on_file_heading(self) -> str:
        """Return the 'Instructions on file' heading text."""
        try:
            self.instructions_on_file_heading.wait_for(state='visible', timeout=10000)
            return self.instructions_on_file_heading.inner_text().strip()
        except Exception:
            return ""

    def get_instructions_message(self) -> str:
        """Return the message displayed under the 'Instructions on file' heading."""
        try:
            self.instructions_message.wait_for(state='visible', timeout=10000)
            return self.instructions_message.inner_text().strip()
        except Exception:
            return ""

    def is_hardstop_visible(self) -> bool:
        """Return True if a hard-stop error message is visible on the page."""
        try:
            error_locator = self.page.locator("//p[@aria-label='error-message']")
            if error_locator.count() > 0:
                return error_locator.first.is_visible()
            return False
        except Exception:
            return False

    def validate_account_details_information(self, account_details: list, partial_match: bool = False):
        
        logger.info("Validating account details on MIMO Transaction Request Page")

        # Wait for spinner to disappear and page to fully load before asserting
        self.wait_for_page_load()

        account_items = self.page.locator("//section[@aria-label='account-info-section']//ul//li")
        try:
            account_items.first.wait_for(state='visible', timeout=30000)
        except Exception:
            raise AssertionError("Account info elements not found on MIMO Transaction Request Page")

        texts = []
        count = account_items.count()
        for i in range(min(count, 3)):
            try:
                texts.append(account_items.nth(i).inner_text().strip())
            except Exception:
                texts.append("")

        if partial_match:
            if len(account_details) >= 1 and account_details[0]:
                account_name_parts = account_details[0].strip().split(',')
                primary_name = account_name_parts[0].strip()
                assert primary_name in texts[0], f"Account name mismatch: expected '{primary_name}' in '{texts[0]}'"
            if len(account_details) >= 2 and account_details[1]:
                account_number_match = account_details[1].split(',')[0].strip().replace('Account # ', '').replace('(', '').replace(')', '')
                account_number_digits = ''.join(filter(str.isdigit, account_number_match))
                assert account_number_digits in texts[1], f"Account number mismatch: expected '{account_number_digits}' in '{texts[1]}'"
        else:
            if len(account_details) >= 1:
                assert account_details[0].strip() in texts[0], f"Account name mismatch: expected contains '{account_details[0]}', got '{texts[0]}'"
            if len(account_details) >= 2:
                assert account_details[1].strip() in texts[1], f"Account number mismatch: expected contains '{account_details[1]}', got '{texts[1]}'"
            if len(account_details) >= 3:
                assert account_details[0].strip() in texts[2], f"Account strategy/name mismatch: expected contains '{account_details[0]}', got '{texts[2]}'"

        logger.info("Account details validated successfully")
    
    def select_bank_for_contributions(self, sloa_option: str = "Any"):
        """Select bank for contributions request"""
        logger.info(f"Selecting bank with SLOA option: {sloa_option}")
        
        if sloa_option != "Any":
            locator = f"//p[@aria-label='authorization-status table-cell-text' and text()='{sloa_option}']//parent::div//preceding-sibling::div/div/div/input"
        else:
            locator = "//p[@aria-label='authorization-status table-cell-text']//parent::div//preceding-sibling::div/div/div/input"
        
        bank_radio = self.page.locator(locator).first
        bank_radio.wait_for(state='visible', timeout=60000)
        bank_radio.click()
        logger.info("Bank selected for contribution request")
    
    def click_next(self):
        """Click Next button and navigate to MIMO Transaction Request Page 2"""
        logger.info("Clicking Next button")
        
        try:
            self.page.wait_for_load_state('networkidle', timeout=90000)
            logger.info("Page load state: networkidle")
        except Exception as e:
            logger.warning(f"Network idle wait failed: {e}")
        
        # Now wait for Next button to be visible
        self.next_button.wait_for(state='visible', timeout=90000)
        self.next_button.scroll_into_view_if_needed()
        self.next_button.click()
        logger.info("Navigated to MIMO Transaction Request Page 2")
        logger.info("Next button clicked")

    def verify_pagination(self):
        continue_pagination = True
        iterations = 0
        while continue_pagination:
            iterations += 1
            if iterations > 50:
                raise AssertionError("Pagination loop exceeded safe iteration limit")

            radio_locator = self.page.locator("//div[@aria-label='swp-cancel-table-row-item-radio']")
            size = radio_locator.count()

            if size == 10:
                next_btn = self.page.locator("//button[@aria-label='Go to next page']")
                try:
                    if next_btn.count() > 0 and next_btn.first.is_enabled() and next_btn.first.is_visible():
                        logger.info("Number of records present are 10 - clicking next page")
                        next_btn.first.click()
                        # brief wait for UI to update
                        self.page.wait_for_timeout(500)
                        continue
                    else:
                        logger.info("Total Records are over or next button not clickable")
                        continue_pagination = False
                except Exception:
                    logger.info("Next page button not clickable or not present")
                    continue_pagination = False
            elif size > 10:
                raise AssertionError(f"Size should not be greater than 10: {size}")
            else:
                logger.info("The records present are less than 10 - pagination complete")
                continue_pagination = False

    def select_first_instruction_by_method(self, method: str):
        """Select the first instruction matching the provided method (e.g., 'ACH', 'Check', 'Journal').

        If no matching method is found, selects the first available instruction radio.
        """
        method_text = method.strip()
        # XPath similar to Java returnInstructionByMethod
        xpath = f"//p[text()='{method_text}']//parent::div/preceding-sibling::div[@aria-label='Radio-table-cell']//input"
        locator = self.page.locator(xpath)
        if locator.count() > 0:
            locator.first.scroll_into_view_if_needed()
            locator.first.click()
            logger.info(f"Selected instruction by method: {method_text}")
            return

        # fallback: click the first instruction radio
        first_radio = self.page.locator("//div[@aria-label='swp-cancel-table-row-item-radio']//input").first
        if first_radio.count() > 0:
            first_radio.scroll_into_view_if_needed()
            first_radio.click()
            logger.info("Selected first available instruction (fallback)")
        else:
            raise AssertionError("No instruction radio buttons found to select")

    def get_ui_values_from_instructions_for_first(self) -> list:
        """Return a list of UI text values from the selected instruction's visible cells.

        Returns up to 6 values (matches Java behavior).
        """
        values = []
        locator = self.page.locator("//div[contains(@class,'selected')]//div[@aria-label='Radio-table-cell']/following-sibling::div//p")
        count = locator.count()
        for i in range(min(count, 6)):
            try:
                values.append(locator.nth(i).inner_text().strip())
            except Exception:
                values.append("")
        return values

    def click_expand_icon_for_selected_instruction(self):
        """Click the expand icon for the currently selected instruction."""
        expand_locator = self.page.locator("//div[contains(@class,'selected')]//div[@aria-label='Radio-table-cell']/following-sibling::*[contains(@class,'MuiSvgIcon-root') or contains(@data-testid,'ArrowForwardIosIcon')]")
        if expand_locator.count() > 0:
            expand_locator.first.scroll_into_view_if_needed()
            expand_locator.first.click()
            self.page.wait_for_timeout(300)
            logger.info("Clicked expand icon for selected instruction")
        else:
            raise AssertionError("Expand icon for selected instruction not found")

    def get_address_value_from_expanded_view(self) -> str:
        """Return the address/destination value visible in the expanded view for the selected instruction."""
        locator = self.page.locator("//div[contains(@class,'selected')]//following-sibling::div[@aria-label='table-cell']//p[@aria-label='destination table-cell-text'][2]")
        if locator.count() > 0:
            try:
                return locator.first.inner_text().strip()
            except Exception:
                return ""
        return ""
