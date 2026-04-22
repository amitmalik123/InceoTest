from playwright.sync_api import Locator, Page, expect

from locators import tracking_center_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.wait_utils import WaitContext, wait_for_url_to_match, wait_for_loading_spinner_to_disappear
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class TrackingCenterPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = tracking_center_locators.initialize_locators(page)
        self.account_src_label: Locator = None  # Will be set dynamically
        self.roth_str_label: Locator = locators["roth_str_label"]
        self.logout_link: Locator = locators["logout_link"]
        self.bodycontent_div: Locator = locators["bodycontent_div"]

    def navigate(self) -> None:
        """
        Navigate to Tracking Center by clicking the Tracking Center link.
        
        This method:
        1. Retrieves the Tracking Center link locator
        2. Clicks on the link to navigate
        3. Waits for the page to load with 'domcontentloaded' state
        4. Waits for the loading spinner to disappear
        
        The Tracking Center link is located using the href attribute '/AccountsAnalysis/TrackingCenter'
        """
        logger.info("Navigating to tracking center page via Tracking Center link click")
        
        try:
            # Retrieve locators
            locators = tracking_center_locators.initialize_locators(self.page)
            tracking_center_link = locators["tracking_center_link"]
            
            # Click on the Tracking Center link
            logger.info("Clicking on Tracking Center link...")
            tracking_center_link.click(timeout=10000)
            logger.info("Tracking Center link clicked successfully")
            
            # Wait for page to load
            logger.info("Waiting for Tracking Center page to load...")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info("Tracking center page loaded")
            
            # Wait for loading spinner to disappear
            logger.info("Waiting for loading spinner to disappear...")
            wait_for_loading_spinner_to_disappear(self.page, timeout=15.0)
            logger.info("Loading spinner disappeared - page ready")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Tracking Center page: {e}")
            raise AssertionError(f"Navigation to Tracking Center page failed. Details: {e}") from e

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Verifying account source: {expected}")
        self.account_src_label = self.page.get_by_text(expected)
        expect(self.account_src_label).to_have_text(expected)
        logger.info(f"Account source {expected} verified")

    def verify_roth_str(self, expected: str) -> None:
        logger.info(f"Verifying Roth STR: {expected}")
        expect(self.roth_str_label).to_have_text(expected)
        logger.info(f"Roth STR {expected} verified")

    def click_logout(self) -> None:
        logger.info("Clicking logout")
        self.click(self.logout_link)
        logger.info("Logout clicked")

    def click_bodycontent(self) -> None:
        logger.info("Clicking body content")
        self.click(self.bodycontent_div)

    def search_and_open_d_number(self, d_number: str, timeout: int = 30000) -> None:
        """
        Search for D-number and open the item details page.
        
        This method:
        1. Enters D-number in the search input field (id: client_search_input)
        2. Clicks the search button (id: searchbutton)
        3. Waits for the table row with matching D-number to load
        4. Clicks on the table row to open item details
        
        Args:
            d_number: The D-number to search for (e.g., "D003525811")
            timeout: Timeout in milliseconds for wait operations (default: 30000)
            
        Raises:
            AssertionError: If D-number not found or row not clickable
        """
        logger.info(f">>> STEP: Searching for D-number: {d_number}")
        
        try:
            # Retrieve locators
            locators = tracking_center_locators.initialize_locators(self.page)
            search_input = locators["client_search_input"]
            search_button = locators["search_button"]
            d_number_row = tracking_center_locators.get_d_number_table_row_locator(self.page, d_number)
            
            # STEP 1: Enter D-number in search input
            logger.info(f"Step 1: Entering D-number '{d_number}' in search input...")
            try:
                # Convert timeout from milliseconds to seconds for WaitContext
                timeout_sec = timeout / 1000.0 if timeout else 30.0
                with WaitContext(timeout=timeout_sec) as wait_ctx:
                    search_input.fill(d_number)
                logger.info(f"[PASS] D-number entered in search input: {d_number}")
            except Exception as e:
                logger.error(f"✗ Failed to enter D-number in search input: {e}")
                raise AssertionError(f"Failed to enter D-number '{d_number}' in search input. Details: {e}") from e
            
            # STEP 2: Click search button
            logger.info(f"Step 2: Clicking search button...")
            try:
                search_button.click(timeout=timeout)
                logger.info(f"[PASS] Search button clicked")
            except Exception as e:
                logger.error(f"✗ Failed to click search button: {e}")
                raise AssertionError(f"Failed to click search button. Details: {e}") from e
            
            # STEP 3: Wait for table row with D-number to be visible
            logger.info(f"Step 3: Waiting for D-number table row to load (timeout: {timeout}ms)...")
            try:
                # Convert timeout from milliseconds to seconds for WaitContext
                timeout_sec = timeout / 1000.0 if timeout else 30.0
                with WaitContext(timeout=timeout_sec) as wait_ctx:
                    d_number_row_element = d_number_row
                    assert d_number_row_element.is_visible(), f"Table row with id '{d_number}' is not visible after search"
                logger.info(f"[PASS] D-number table row loaded and visible: {d_number}")
            except Exception as e:
                logger.error(f"✗ Failed to load D-number table row: {e}")
                raise AssertionError(f"Failed to load table row for D-number '{d_number}'. Details: {e}") from e
            
            # STEP 4: Click on the D-number table row
            logger.info(f"Step 4: Clicking D-number table row to open item details...")
            try:
                d_number_row.click(timeout=timeout)
                logger.info(f"[PASS] D-number table row clicked: {d_number}")
            except Exception as e:
                logger.error(f"✗ Failed to click D-number table row: {e}")
                raise AssertionError(f"Failed to click table row for D-number '{d_number}'. Details: {e}") from e
            
            # STEP 5: Wait for page navigation
            logger.info(f"Step 5: Waiting for page navigation to item details...")
            try:
                self.page.wait_for_load_state("networkidle", timeout=timeout)
                logger.info(f"[PASS] Page loaded after clicking D-number row")
            except Exception as e:
                logger.error(f"⚠ Page load timeout (may still be navigating): {e}")
                # Non-critical timeout, log but don't fail
                logger.warning(f"Page load state reached 'networkidle' timeout, but proceeding anyway")
            
            logger.info(f"[PASS] D-Number search and item details page opening completed: {d_number}")
            
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error during D-number search: {e}")
            raise AssertionError(f"Failed to search and open D-number '{d_number}'. Details: {e}") from e
