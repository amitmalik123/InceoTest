"""
Cancel Automatic Investment Plan (AIP) Page Object
"""

from playwright.sync_api import Locator, Page
from pages.stp.shared.base_page import BasePage
from pages.stp.stp_aip.stp_cancelAip.locators.cancel_aip_locators import CancelAIPLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CancelAIPPage(BasePage):
    """Page object for Cancel AIP Landing Page and all AIP-related pages"""
    
    PAGE_NAME = "Cancel AIP Page"
    
    def __init__(self, page: Page):
        super().__init__(page)
        loc = CancelAIPLocators
        
        # Landing Page elements
        self.landing_page_title = page.locator(loc.LANDING_PAGE_TITLE)
        self.select_aip = page.locator(loc.SELECT_AIP)
        self.delete_button = page.locator(loc.DELETE_BUTTON)
        self.next_button = page.locator(loc.NEXT_BUTTON)
        self.cancel_button = page.locator(loc.CANCEL_BUTTON)
        
        # Selection Page elements
        self.selection_page_title = page.locator(loc.SELECTION_PAGE_TITLE)
        self.end_date_selection = page.locator(loc.END_DATE_SELECTION)
        self.future_end_selection = page.locator(loc.FUTURE_END_SELECTION)
        self.calendar_field = page.locator(loc.CALENDAR_FIELD)
        
        # Signature Options
        self.not_obtain_signature_radio = page.locator(loc.NOT_OBTAIN_SIGNATURE_RADIO)
        self.select_esign = page.locator(loc.SELECT_ESIGN)
        self.select_print = page.locator(loc.SELECT_PRINT)
        
        # Summary Page elements
        self.submit_button = page.locator(loc.SUBMIT_BUTTON)
        self.summary_submit_button = page.locator(loc.SUMMARY_SUBMIT_BUTTON)
        self.print_button = page.locator(loc.PRINT_BUTTON)
        self.esign_button = page.locator(loc.ESIGN_BUTTON)
        self.submit_review_button = page.locator(loc.SUBMIT_REVIEW_BUTTON)
        self.submit_to_advisor = page.locator(loc.SUBMIT_TO_ADVISOR)
        
        # Confirmation Page elements
        self.item_number_link = page.locator(loc.ITEM_NUMBER_LINK)
        self.item_number_text = page.locator(loc.ITEM_NUMBER_TEXT)
        
        # Loading indicators
        self.spinner_loading = page.locator(loc.SPINNER_LOADING)
    
    def wait_for_page_load(self) -> None:
        """Wait for Cancel AIP page to load"""
        logger.info("Waiting for Cancel AIP page to load")
        
        # Wait for spinner to disappear if present
        try:
            if self.spinner_loading.count() > 0:
                self.spinner_loading.wait_for(state='hidden', timeout=30000)
                logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.warning(f"Spinner wait failed: {e}")
        
        # Wait for landing page title or selection page title
        try:
            self.landing_page_title.or_(self.selection_page_title).first.wait_for(state='visible', timeout=10000)
            logger.info("Cancel AIP page loaded")
        except Exception as e:
            logger.warning(f"Page title wait failed: {e}")
        
        self.page.wait_for_timeout(500)
    
    def refresh_landing_page(self) -> None:
        """Refresh the landing page to view API created AIP"""
        logger.info("Refreshing landing page")
        self.page.reload(wait_until='networkidle', timeout=30000)
        self.wait_for_page_load()
        logger.info("Landing page refreshed")
    
    def validate_aip_displayed(self) -> bool:
        """Validate that AIP is displayed on landing page"""
        logger.info("Validating AIP is displayed")
        self.select_aip.wait_for(state='visible', timeout=10000)
        is_visible = self.select_aip.is_visible()
        logger.info(f"AIP is visible: {is_visible}")
        return is_visible
    
    def click_on_aip_to_be_deleted(self) -> str:
        """Click on the AIP to be deleted and return its details"""
        logger.info("Clicking on AIP to be deleted")
        self.select_aip.wait_for(state='visible', timeout=10000)
        aip_text = self.select_aip.inner_text()
        self.select_aip.click()
        self.page.wait_for_timeout(2000)
        logger.info(f"Clicked on AIP: {aip_text}")
        return aip_text
    
    def click_delete_button(self) -> None:
        """Click the Delete button"""
        logger.info("Clicking Delete button")
        self.delete_button.wait_for(state='visible', timeout=10000)
        self.delete_button.click()
        self.page.wait_for_timeout(1000)
        logger.info("Delete button clicked")
    
    def validate_aip_to_be_deleted(self) -> bool:
        """Validate AIP to be deleted is displayed on selection page"""
        logger.info("Validating AIP to be deleted on selection page")
        is_visible = self.selection_page_title.is_visible(timeout=10000)
        logger.info(f"Selection page title visible: {is_visible}")
        return is_visible
    
    def validate_end_date_radio_button(self) -> bool:
        """Validate and select end date radio button"""
        logger.info("Validating end date radio button")
        is_visible = self.end_date_selection.is_visible(timeout=10000)
        if is_visible:
            self.end_date_selection.click()
            logger.info("End date radio button selected")
        return is_visible

    def select_future_end_date(self) -> None:
        """Validate Future End Date radio is present, select it, then pick the first
        clickable date from the calendar picker."""
        logger.info("Validating Future End Date radio button is visible")
        self.future_end_selection.wait_for(state='visible', timeout=10000)
        assert self.future_end_selection.is_visible(), "Future End Date radio button not found"

        self.future_end_selection.click()
        logger.info("Future End Date radio button selected")

        logger.info("Validating calendar field button is visible")
        self.calendar_field.wait_for(state='visible', timeout=10000)
        assert self.calendar_field.is_visible(), "Calendar field button not found"

        self.calendar_field.click()
        logger.info("Calendar opened")
        self.page.wait_for_timeout(500)

        # Find and click the first enabled/clickable date button
        for day in range(1, 32):
            date_str = f"{day:02d}"
            date_btn = self.page.locator(
                f"//div[@role='rowgroup']//button[text()='{date_str}']"
            )
            if date_btn.count() > 0 and date_btn.first.is_enabled():
                self.page.evaluate("el => el.click()", date_btn.first.element_handle())
                logger.info(f"Selected date: {date_str}")
                break
        else:
            raise RuntimeError("No clickable date found in calendar")

        self.page.wait_for_timeout(500)
        logger.info("Future End Date selected from calendar")

    def select_signature_option(self, signature_type: str) -> None:
        """Select signature option
        
        Args:
            signature_type: 'notobtain', 'obtain', or 'print'
        """
        logger.info(f"Selecting signature option: {signature_type}")
        
        self.page.evaluate("window.scrollBy(0, 900)")
        self.page.wait_for_timeout(1000)
        
        if signature_type.lower() == "notobtain":
            self.not_obtain_signature_radio.click()
            logger.info("Selected 'Do Not Obtain Client Signature' option")
        elif signature_type.lower() == "obtain":
            self.select_esign.click()
            logger.info("Selected 'Obtain Electronic Client Signature' option")
        elif signature_type.lower() == "print":
            self.select_print.click()
            logger.info("Selected 'Print to Obtain Physical Client Signature' option")
        else:
            raise ValueError(f"Invalid signature type: {signature_type}")
        
        self.page.wait_for_timeout(1000)
    
    def click_next_button(self) -> None:
        """Click the Next button"""
        logger.info("Clicking Next button")
        self.next_button.wait_for(state='visible', timeout=10000)
        self.page.evaluate("window.scrollBy(0, 950)")
        self.next_button.click()
        self.page.wait_for_timeout(2000)
        logger.info("Next button clicked")
    
    def click_summary_submit_button(self) -> None:
        """Click the Submit button on the Cancel AIP Summary page (Immediate flow)"""
        logger.info("Clicking Submit button on Cancel AIP Summary page")
        self.page.evaluate("window.scrollBy(0, 950)")
        self.page.wait_for_timeout(1000)
        self.summary_submit_button.wait_for(state='visible', timeout=20000)
        self.summary_submit_button.click()

        # Wait for spinner to disappear
        try:
            self.spinner_loading.wait_for(state='hidden', timeout=30000)
            logger.info("Submit processing complete")
        except Exception as e:
            logger.warning(f"Spinner wait after submit failed: {e}")

        logger.info("Cancel AIP Summary submit button clicked")

    def click_submit_button(self) -> None:
        """Click the Submit button on summary page"""
        logger.info("Clicking Submit button")
        self.page.evaluate("window.scrollBy(0, 950)")
        self.submit_button.wait_for(state='visible', timeout=10000)
        self.submit_button.click()
        
        # Wait for spinner to disappear
        try:
            self.spinner_loading.wait_for(state='hidden', timeout=30000)
            logger.info("Submit processing complete")
        except Exception as e:
            logger.warning(f"Spinner wait after submit failed: {e}")
        
        # Click submit again if still clickable (for confirmation)
        self.page.wait_for_timeout(2000)
        if self.submit_button.is_visible(timeout=2000):
            try:
                self.submit_button.click(timeout=2000)
                self.spinner_loading.wait_for(state='hidden', timeout=30000)
            except Exception:
                pass
        
        logger.info("Submit button clicked")
    
    def get_item_number(self) -> str:
        """Get item number from confirmation page"""
        logger.info("Getting item number from confirmation page")
        self.item_number_text.wait_for(state='visible', timeout=15000)
        item_number = self.item_number_text.inner_text()
        logger.info(f"Item number: {item_number}")
        return item_number
    
    def click_item_number(self) -> None:
        """Click on item number link to open item details"""
        logger.info("Clicking item number link")
        self.item_number_link.wait_for(state='visible', timeout=10000)
        
        # Store parent window handle
        parent_window = self.page.context.pages[0]
        
        # Click item number link (will open in new tab)
        self.item_number_link.click()
        self.page.wait_for_timeout(2000)
        
        # Switch to new tab
        pages = self.page.context.pages
        if len(pages) > 1:
            new_page = pages[-1]
            new_page.bring_to_front()
            
            # Refresh the new page a few times
            for i in range(5):
                new_page.reload(wait_until='networkidle', timeout=30000)
                new_page.wait_for_timeout(5000)
            
            logger.info("Switched to item details page")
        else:
            logger.warning("New tab not opened")
    
    def get_household_id(self) -> str:
        """Get household ID from URL"""
        current_url = self.page.url
        household_id = current_url.split("=")[-1]
        logger.info(f"Household ID: {household_id}")
        return household_id
