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
def navigate_to_tracking_center_user(authenticated_page: Page, tracking_center_page):
    """Navigate to Tracking Center"""
    logger.info("Navigating to Tracking Center")
    tracking_center_page.navigate()


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
            raise AssertionError(f"[FAIL] TrackingCenterPage: D-Number Search — Expected: D-number found and item details opened, Actual: search failed. Details: {e}") from e


@then("Verify No search result message should be displayed")
def verify_no_search_result_message_displayed_uppercase(authenticated_page: Page, tracking_center_page, test_context):
    """
    Verify that the "No search results" message is displayed after deleting a document.
    
    This step:
    1. Retrieves the no search results message from the Tracking Center grid
    2. Validates the message text matches the expected values
    3. Captures screenshot for reporting
    
    Uses framework utilities:
    - tracking_center_page.get_no_search_results_message(): Retrieves the message text
    - Assertions: Hard assertions to validate the message content
    - allure: Attach screenshots for reporting
    
    Expected message:
    "No search results were found.  Please clear the search field and try again or click Restore Default."
    
    Pre-condition:
    - Tracking Center page must be displayed
    - Search must have been performed but yielded no results (e.g., after document deletion)
    
    Post-condition:
    - No search results message is confirmed visible and contains expected text
    
    Raises:
        AssertionError: If message not found, not visible, or text doesn't match expected value
    """
    logger.info("[STEP] Verify No search result message should be displayed")
    
    expected_message = "No search results were found.  Please clear the search field and try again or click Restore Default."
    
    with allure.step("Verify No search result message should be displayed"):
        try:
            # STEP 1: Retrieve the no search results message
            logger.info("[STEP_DETAIL] Retrieving no search results message from Tracking Center...")
            try:
                actual_message = tracking_center_page.get_no_search_results_message(timeout=30000)
                logger.info(f"[PASS] No search results message retrieved")
            except AssertionError as e:
                logger.error(f"✗ Failed to retrieve no search results message: {e}")
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="No_Search_Results_Message_Not_Found",
                    attachment_type=allure.attachment_type.PNG
                )
                raise
            
            # STEP 2: Validate the message text matches expected value
            logger.info("[STEP_DETAIL] Validating message text matches expected value...")
            logger.info(f"Expected message: '{expected_message}'")
            logger.info(f"Actual message: '{actual_message}'")
            
            if actual_message != expected_message:
                error_msg = f"No search results message text mismatch. Expected: '{expected_message}', Actual: '{actual_message}'"
                logger.error(f"✗ {error_msg}")
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Message_Text_Mismatch",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError(error_msg)
            
            logger.info(f"[PASS] Message text matches expected value")
            
            # STEP 3: Capture screenshot for verification
            logger.info("[STEP_DETAIL] Capturing screenshot for verification...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="No_Search_Results_Message_Verified",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] No search result message verification completed successfully")
            
        except AssertionError:
            # Re-raise assertion errors without additional wrapping
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error during verification: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="No_Search_Results_Verification_Error",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"[FAIL] TrackingCenterPage: No Results Message Verification — Expected: message='{expected_message}', Actual: message='{actual_message}'. Details: {e}") from e


@when("Search the DNumber")
def search_d_number(authenticated_page: Page, tracking_center_page, test_context):
    """
    Search for a D-number in Tracking Center and wait for search results.
    
    This step:
    1. Retrieves the D-number from test_context (stored during DocuSign process)
    2. Enters D-number in search input field (id: client_search_input)
    3. Clicks search button (id: searchbutton)
    4. Waits for the search results to load
    
    Uses framework utilities:
    - tracking_center_page.search_d_number(): Performs the search
    - allure: Attach screenshots for reporting
    - test_context: Retrieves D-number stored by DocuSign steps
    
    Pre-condition:
    - Tracking Center page must be displayed
    - test_context['d_number'] must exist (populated during DocuSign workflow)
    
    Post-condition:
    - Search results are loaded and ready for verification
    
    Raises:
        KeyError: If D-number not found in test_context
        AssertionError: If search fails
    """
    logger.info("[STEP] Search the DNumber")
    
    with allure.step("Search the DNumber"):
        try:
            # STEP 1: Get D-number from test_context
            logger.info("Step 1: Retrieving D-number from test_context...")
            d_number = test_context.get('d_number')
            
            if not d_number:
                error_msg = "D-number not found in test_context. Ensure 'User Finish the DocuSign process' step is executed first to populate test_context['d_number']."
                logger.error(f"✗ {error_msg}")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="D-Number_Not_In_Context", attachment_type=allure.attachment_type.PNG)
                raise KeyError(error_msg)
            
            logger.info(f"[PASS] D-number retrieved from test_context: {d_number}")
            
            # STEP 2: Call page object method to search D-number
            logger.info(f"Step 2: Searching for D-number '{d_number}'...")
            try:
                tracking_center_page.search_d_number(d_number, timeout=30000)
                logger.info(f"[PASS] D-number search completed")
            except AssertionError as e:
                logger.error(f"✗ D-number search failed: {e}")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="D-Number_Search_Failed", attachment_type=allure.attachment_type.PNG)
                raise
            
            # STEP 3: Capture screenshot after search
            logger.info("Step 3: Capturing screenshot after search...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="D-Number_Search_Results",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info(f"[PASS] D-number search step completed successfully for {d_number}")
            
        except KeyError as e:
            logger.error(f"✗ Missing required data: {e}")
            raise AssertionError(f"[FAIL] Tracking Center: D-Number Retrieval — {e}") from e
        
        except AssertionError:
            raise
        
        except Exception as e:
            logger.error(f"✗ Unexpected error during D-number search: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="D-Number_Search_Unexpected_Error",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"[FAIL] TrackingCenterPage: D-Number Search — Expected: search completed successfully, Actual: search failed. Details: {e}") from e


@then("Verify no search result message should be displayed")
def verify_no_search_result_message_displayed(authenticated_page: Page, tracking_center_page, test_context):
    """
    Verify that the "No search results" message is displayed after searching for a D-number.
    
    This step:
    1. Retrieves the no search results message from the Tracking Center grid
    2. Validates the message text matches the expected values
    3. Captures screenshot for reporting
    
    Uses framework utilities:
    - tracking_center_page.get_no_search_results_message(): Retrieves the message text
    - Assertions: Hard assertions to validate the message content
    - allure: Attach screenshots for reporting
    
    Expected message:
    "No search results were found.  Please clear the search field and try again or click Restore Default."
    
    Pre-condition:
    - Tracking Center page must be displayed
    - D-number search must have been performed (via "Search the DNumber" step)
    - Search must have yielded no results (typically after document deletion)
    
    Post-condition:
    - No search results message is confirmed visible and contains expected text
    
    Raises:
        AssertionError: If message not found, not visible, or text doesn't match expected value
    """
    logger.info("[STEP] Verify no search result message should be displayed")
    
    expected_message = "No search results were found.  Please clear the search field and try again or click Restore Default."
    
    with allure.step("Verify no search result message should be displayed"):
        try:
            # STEP 1: Retrieve the no search results message
            logger.info("[STEP_DETAIL] Retrieving no search results message from Tracking Center...")
            try:
                actual_message = tracking_center_page.get_no_search_results_message(timeout=30000)
                logger.info(f"[PASS] No search results message retrieved")
            except AssertionError as e:
                logger.error(f"✗ Failed to retrieve no search results message: {e}")
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="No_Search_Result_Message_Not_Found",
                    attachment_type=allure.attachment_type.PNG
                )
                raise
            
            # STEP 2: Validate the message text matches expected value
            logger.info("[STEP_DETAIL] Validating message text matches expected value...")
            logger.info(f"Expected message: '{expected_message}'")
            logger.info(f"Actual message: '{actual_message}'")
            
            if actual_message != expected_message:
                error_msg = f"No search results message text mismatch. Expected: '{expected_message}', Actual: '{actual_message}'"
                logger.error(f"✗ {error_msg}")
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="No_Search_Result_Message_Text_Mismatch",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError(error_msg)
            
            logger.info(f"[PASS] Message text matches expected value")
            
            # STEP 3: Capture screenshot for verification
            logger.info("[STEP_DETAIL] Capturing screenshot for verification...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="No_Search_Result_Message_Verified",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] No search result message verification completed successfully")
            
        except AssertionError:
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error during verification: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="No_Search_Result_Message_Verification_Error",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"[FAIL] TrackingCenterPage: No Search Result Message Verification — Expected: message='{expected_message}', Actual: message='{actual_message}'. Details: {e}") from e
