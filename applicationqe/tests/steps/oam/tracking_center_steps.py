from playwright.sync_api import Page
from pytest_bdd import parsers, then, when
import allure

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I navigate to Tracking Center")
def navigate_to_tracking_center(authenticated_page: Page, tracking_center_page):
    """Navigate to Tracking Center"""
    logger.info("Navigating to Tracking Center")
    tracking_center_page.navigate()

@when("User navigate to Tracking Center")
def navigate_to_tracking_center(authenticated_page: Page, tracking_center_page):
    """Navigate to Tracking Center"""
    logger.info("Navigating to Tracking Center")
    tracking_center_page.navigate()


@then("I should see the Roth Conversion entry for the client")
def verify_roth_conversion_entry_exists(
    authenticated_page: Page, tracking_center_page, test_context
):
    """Verify the Roth Conversion entry exists in Tracking Center"""
    logger.info("Verifying Roth Conversion entry in Tracking Center")
    tracking_center_page.verify_account_src(test_context["test_data"]["client_id"])


@then(parsers.parse('I should see "{text}" in the tracking details'))
def verify_text_in_tracking_details(authenticated_page: Page, tracking_center_page, text):
    """Verify specific text in tracking details"""
    logger.info(f"Verifying tracking details contain: {text}")
    tracking_center_page.verify_roth_str(text)


@when("Search the DNumber and open the item details page")
def search_d_number_and_open_item_details(authenticated_page: Page, tracking_center_page, test_context):
    """
    Search for D-number in Tracking Center and open the item details page.
    
    This step:
    1. Retrieves the D-number from test_context (stored during DocuSign process)
    2. Enters D-number in search input field (id: client_search_input)
    3. Clicks search button (id: searchbutton)
    4. Waits for the table row with D-number to load
    5. Clicks on the table row to open item details page
    
    Prerequisite:
    - test_context['d_number'] must exist (populated by DocuSign step: "User Finish the DocuSign process")
    """
    with allure.step("Search DNumber and open item details page"):
        logger.info(">>> STEP: Search DNumber and open item details page")
        
        try:
            # STEP 1: Get D-number from test_context
            logger.info("Step 1: Retrieving D-number from test_context...")
            d_number = test_context.get('d_number')
            
            if not d_number:
                error_msg = "D-number not found in test_context. Ensure 'User Finish the DocuSign process' step is executed first to populate test_context['d_number']."
                logger.error(f"✗ {error_msg}")
                raise KeyError(error_msg)
            
            logger.info(f"D-number retrieved from test_context: {d_number}")
            
            # STEP 2: Call page object method to search and open D-number
            logger.info(f"Step 2: Searching for D-number '{d_number}' and opening item details...")
            try:
                tracking_center_page.search_and_open_d_number(d_number, timeout=30000)
                logger.info(f"[PASS] D-number search and item details page opening completed: {d_number}")
            except AssertionError as e:
                logger.error(f"✗ D-number search failed: {e}")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="D-Number Search Failed", attachment_type=allure.attachment_type.PNG)
                raise
            
            # STEP 3: Take screenshot for verification
            logger.info("Step 3: Capturing screenshot for verification...")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="Item Details Page Opened - DNumber", attachment_type=allure.attachment_type.PNG)
            
            logger.info(f"[PASS] DNumber search step completed successfully for {d_number}.")
            
        except KeyError as e:
            logger.error(f"✗ Missing required data: {e}")
            raise AssertionError(f"[FAIL] Tracking Center: D-Number Retrieval — {e}") from e
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error during D-number search step: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="D-Number Search - Unexpected Error", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"D-number search step failed: {e}") from e
