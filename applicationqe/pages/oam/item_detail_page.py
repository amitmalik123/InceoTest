"""
Locators for Item Detail Page (Tracking Center Item Detail)

This module contains all locator definitions for the Item Detail page.
Locators are organized by functional area for easy maintenance.
"""

from playwright.sync_api import Locator, Page, expect
from pages.oam.base_page import BasePage
from locators.oam import item_detail_locators
from utils.allure_logger import get_allure_logger
from utils.retry_utils import retry_until_true, RetryError
from utils.dialog_utils import DialogHandler

logger = get_allure_logger(__name__)


class ItemDetailPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

    def get_status(self) -> str:
        """
        Get the status value from the Tracking Center detail page.
        
        This method:
        1. Locates the Status label in the tracking center snapshot container
        2. Extracts and returns the status text
        
        Returns:
            Status text (e.g., "Document Submitted")
            
        Raises:
            PlaywrightTimeoutError: If status element not found
            
        Example:
            status = tracking_center_item_detail_page.get_status()
            assert status == "Document Submitted"
        """
        logger.info("Getting Status from Tracking Center page...")
        
        # Locate the label that follows the "Status:" span
        # Using adjacent sibling combinator: span:has-text("Status:") + label
        status_label = self.page.locator(item_detail_locators.STATUS_LABEL)
        
        # Wait for the status label to be visible
        status_label.wait_for(state="visible", timeout=10000)
        logger.info("Status label is visible")
        
        # Get the status text
        status_text = status_label.text_content()
        logger.info(f"Status retrieved: {status_text}")
        
        return status_text or ""

    def get_advisor_alert_required(self) -> str:
        """
        Get the Advisor Alert Required value from the Tracking Center detail page.
        
        This method:
        1. Locates the Advisor Alert Required label in the tracking center snapshot container
        2. Extracts and returns the value
        
        Returns:
            Advisor Alert Required value (e.g., "Yes" or "No")
            
        Raises:
            PlaywrightTimeoutError: If element not found
            
        Example:
            advisor_alert = tracking_center_item_detail_page.get_advisor_alert_required()
            assert advisor_alert == "No"
        """
        logger.info("Getting Advisor Alert Required from Tracking Center page...")
        
        # Locate the label that follows the "Advisor Alert Required:" span
        # Using adjacent sibling combinator: span:has-text("Advisor Alert Required:") + label
        advisor_alert_label = self.page.locator(item_detail_locators.ADVISOR_ALERT_REQUIRED_LABEL)
        
        # Wait for the advisor alert label to be visible
        advisor_alert_label.wait_for(state="visible", timeout=10000)
        logger.info("Advisor Alert Required label is visible")
        
        # Get the advisor alert value
        advisor_alert_text = advisor_alert_label.text_content()
        logger.info(f"Advisor Alert Required retrieved: {advisor_alert_text}")
        
        return advisor_alert_text or ""

    def get_d_number(self) -> str:
        """
        Get the D-number (Item Number) from the Tracking Center detail page.
        
        This method:
        1. Locates the Item Number label in the tracking center snapshot container
        2. Extracts and returns the D-number value
        
        Returns:
            D-number (e.g., "D003518970")
            
        Raises:
            PlaywrightTimeoutError: If Item Number element not found
            
        Example:
            d_number = tracking_center_item_detail_page.get_d_number()
            assert d_number == "D003518970"
        """
        logger.info("Getting D-number (Item Number) from Tracking Center page...")
        
        # Locate the label that follows the "Item Number:" span
        # Using adjacent sibling combinator: span:has-text("Item Number:") + label
        item_number_label = self.page.locator(item_detail_locators.ITEM_NUMBER_LABEL)
        
        # Wait for the item number label to be visible
        item_number_label.wait_for(state="visible", timeout=10000)
        logger.info("Item Number label is visible")
        
        # Get the D-number text
        d_number_text = item_number_label.text_content()
        d_number = d_number_text.strip() if d_number_text else ""
        logger.info(f"D-number retrieved from Tracking Center: {d_number}")
        
        return d_number

    def get_agent_name(self) -> str:
        """
        Get the Agent Name value from the Tracking Center detail page.
        
        This method:
        1. Locates the Agent Name label using XPath
        2. Extracts and returns the agent name text
        
        Returns:
            Agent name text (e.g., "John Doe")
            
        Raises:
            PlaywrightTimeoutError: If Agent Name element not found
            
        Example:
            agent_name = tracking_center_item_detail_page.get_agent_name()
            assert agent_name == "John Doe"
        """
        logger.info("Getting Agent Name from Tracking Center page...")
        
        # Locate the label that follows the "Agent Name:" span using XPath
        # XPath: //span[text()='Agent Name']/following-sibling::label
        agent_name_label = self.page.locator(item_detail_locators.AGENT_NAME_LABEL)
        
        # Wait for the agent name label to be visible
        agent_name_label.wait_for(state="visible", timeout=10000)
        logger.info("Agent Name label is visible")
        
        # Get the agent name text
        agent_name_text = agent_name_label.text_content()
        agent_name = agent_name_text.strip() if agent_name_text else ""
        logger.info(f"Agent Name retrieved from Tracking Center: {agent_name}")
        
        return agent_name

    def get_buttons_info(self) -> dict:
        """
        Get information about all VISIBLE and INTERACTIVE buttons in the column-flow-container.
        
        This method:
        1. Locates the column-flow-container div
        2. Finds all buttons/links (both <button> and <a> elements with class "btn")
        3. Filters only VISIBLE buttons (excludes hidden/modal buttons)
        4. Returns button count and text of each button
        
        Returns:
            Dictionary containing:
            - 'count': Total number of VISIBLE buttons found
            - 'button_texts': List of text for each VISIBLE button
            - 'buttons': Locator to all buttons
            
        Raises:
            PlaywrightTimeoutError: If container not found
            
        Example:
            buttons_info = tracking_center_item_detail_page.get_buttons_info()
            assert buttons_info['count'] == 1
            assert "View" in buttons_info['button_texts']
        """
        logger.info("Getting VISIBLE button information from column-flow-container...")
        
        # Locate the column-flow-container div
        container = self.page.locator(item_detail_locators.COLUMN_FLOW_CONTAINER)
        
        # Wait for container to be visible
        container.wait_for(state="visible", timeout=10000)
        logger.info("Column-flow-container is visible")
        
        # Find all buttons/links within the container
        # This includes <button>, <a> elements with class "btn", and elements with class "item-detail-button"
        all_buttons = container.locator(item_detail_locators.BUTTONS_SELECTOR)
        
        # Get the count of ALL buttons (for logging)
        all_button_count = all_buttons.count()
        logger.info(f"Total number of buttons in DOM: {all_button_count}")
        
        # Filter and get only VISIBLE buttons
        button_texts = []
        visible_buttons_locator_list = []
        
        for i in range(all_button_count):
            button = all_buttons.nth(i)
            
            # Check if button is visible
            if button.is_visible():
                button_text = button.text_content()
                if button_text:
                    button_text = button_text.strip()
                    button_texts.append(button_text)
                    visible_buttons_locator_list.append(button)
                    logger.info(f"Visible Button {len(visible_buttons_locator_list)} text: {button_text}")
            else:
                button_text = button.text_content()
                logger.info(f"Skipping hidden button with text: {button_text.strip() if button_text else 'N/A'}")
        
        visible_button_count = len(button_texts)
        logger.info(f"Total number of VISIBLE and INTERACTIVE buttons: {visible_button_count}")
        
        return {
            'count': visible_button_count,
            'button_texts': button_texts,
            'buttons': all_buttons
        }

    def get_notes_descriptions(self) -> list:
        """
        Get all description texts from the Notes grid.
        
        This method:
        1. Locates the TrackingCenterItemDetailNotesGrid table
        2. Finds all description cells
        3. Extracts and returns the text from each description
        
        Returns:
            List of description texts from the grid rows
            
        Raises:
            PlaywrightTimeoutError: If grid not found
            
        Example:
            descriptions = tracking_center_item_detail_page.get_notes_descriptions()
            assert len(descriptions) > 0
            assert "Your document has been submitted" in descriptions[0]
        """
        logger.info("Getting all description texts from Notes grid...")
        
        # Locate the Notes grid table
        notes_grid = self.page.locator(item_detail_locators.NOTES_GRID_TABLE)
        
        # Wait for the grid to be visible
        notes_grid.wait_for(state="visible", timeout=10000)
        logger.info("Notes grid is visible")
        
        # Find all description cells (td elements with the description aria-describedby)
        description_cells = notes_grid.locator(item_detail_locators.NOTES_DESCRIPTION_CELLS)
        
        # Get count of description cells
        cell_count = description_cells.count()
        logger.info(f"Found {cell_count} description cells in notes grid")
        
        # Extract text from each description cell
        descriptions = []
        for i in range(cell_count):
            cell = description_cells.nth(i)
            cell_text = cell.text_content()
            if cell_text:
                cell_text = cell_text.strip()
                descriptions.append(cell_text)
                logger.info(f"Description {i + 1}: {cell_text[:100]}...")  # Log first 100 chars
        
        logger.info(f"Total descriptions extracted: {len(descriptions)}")
        return descriptions

    def _get_grid_row_count(self) -> int:
        """
        Get the count of data rows in the Notes grid (excluding header row).
        
        This method:
        1. Locates the Notes grid table
        2. Counts data rows (skips header row using CSS :not(:first-child))
        3. Returns the count
        
        Returns:
            Count of data rows (0 if grid not found)
            
        Example:
            row_count = tracking_center_item_detail_page._get_grid_row_count()
            assert row_count > 0
        """
        try:
            # Locate the Notes grid table
            notes_grid = self.page.locator(item_detail_locators.NOTES_GRID_TABLE)
            
            # Wait for grid to be visible
            notes_grid.wait_for(state="visible", timeout=5000)
            logger.debug("Notes grid is visible")
            
            # Find all data rows in the grid (exclude header row)
            # tbody tr:not(:first-child) selects all <tr> except the first one (header)
            grid_rows = notes_grid.locator(item_detail_locators.NOTES_GRID_DATA_ROWS)
            row_count = grid_rows.count()
            
            logger.info(f"Grid row count: {row_count}")
            return row_count
                
        except Exception as e:
            logger.warning(f"Error getting grid row count: {e}")
            return 0

    def refresh_page(self) -> None:
        """
        Refresh the page once to ensure content is updated.
        
        This method:
        1. Reloads the page
        2. Waits for networkidle (all network requests completed)
        
        Raises:
            PlaywrightTimeoutError: If page fails to load within default timeout
            
        Example:
            tracking_center_item_detail_page.refresh_page()
        """
        logger.info("Refreshing page...")
        
        try:
            self.page.reload(wait_until="networkidle")
            logger.info("✓ Page refreshed successfully")
        except Exception as e:
            logger.error(f"✗ Error refreshing page: {e}")
            raise

    def click_upload_button_and_upload_document(self, file_path: str = "") -> None:
        """
        Click the Upload button and upload a document on the Tracking Center Item Detail page.
        
        This method:
        1. Locates the Upload button using stable selector (get_by_text)
        2. Waits for the associated file input to be attached
        3. Creates a minimal test PDF if no file provided
        4. Sets the file via set_input_files() for secure upload
        5. Clicks the Upload button to trigger submission
        6. Waits for page load after upload
        
        Args:
            file_path: Optional path to document file. If empty, creates a minimal test PDF.
                      Default: "" (generates test PDF)
        
        Returns:
            None
            
        Raises:
            PlaywrightTimeoutError: If Upload button or file input not found
            Exception: If file upload fails
            
        Example:
            item_detail_page.click_upload_button_and_upload_document()
            item_detail_page.click_upload_button_and_upload_document("/path/to/document.pdf")
        """
        import os
        import tempfile

        logger.info("Starting document upload process...")
        
        # Step 1: Create test PDF if no file provided
        if not file_path or not os.path.exists(file_path):
            file_path = os.path.join(tempfile.gettempdir(), "item_detail_upload.pdf")
            if not os.path.exists(file_path):
                _create_min_pdf_for_upload(file_path)
            logger.info(f"Using generated test PDF: {file_path}")
        else:
            logger.info(f"Using provided file: {file_path}")

        # Step 2: Find file input associated with Upload button
        logger.info("Locating file input for upload...")
        try:
            # Try to find file input in the page
            file_input = self.page.locator(item_detail_locators.FILE_INPUT_SELECTOR).first
            file_input.wait_for(state="attached", timeout=10000)
            logger.info("✓ File input located")
        except Exception as e:
            logger.error(f"✗ File input not found: {e}")
            raise

        # Step 3: Set the file for upload
        logger.info(f"Setting file for upload: {file_path}")
        try:
            file_input.set_input_files(file_path)
            logger.info("✓ File set successfully on input element")
        except Exception as e:
            logger.error(f"✗ Failed to set file on input: {e}")
            raise

        # Step 4: Wait for page stabilization before clicking
        self.page.wait_for_timeout(1000)

        # Step 5: Click Upload button
        logger.info("Clicking Upload button...")
        try:
            # Use get_by_text to find the Upload button (stable selector)
            upload_button = self.page.get_by_text(item_detail_locators.UPLOAD_BUTTON_TEXT)
            upload_button.wait_for(state="visible", timeout=10000)
            upload_button.click()
            logger.info("✓ Upload button clicked")
        except Exception as e:
            logger.warning(f"⚠ Upload button click warning: {e} - File may auto-upload")

        # Step 6: Wait for page load and stabilization
        logger.info("Waiting for page load after upload...")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info("✓ Page loaded after upload")
        except Exception as e:
            logger.warning(f"⚠ Page load warning: {e}")

        logger.info("✓ Document upload process completed successfully")

    def click_close_button(self) -> None:
        """
        Click the Close button on the Tracking Center Item Detail page.
        
        This method:
        1. Locates the Close button using stable selector (get_by_role)
        2. Waits for the button to be visible and enabled
        3. Clicks the Close button
        4. Waits for page stabilization
        
        The Close button HTML:
            <span class="right-padding">
                <button type="button" class="btn btn-default">Close</button>
            </span>
        
        Selector Strategy: Uses get_by_role("button", name="Close") - stable & accessible
        
        Returns:
            None
            
        Raises:
            PlaywrightTimeoutError: If Close button not found or not clickable
            Exception: If button click fails
            
        Example:
            item_detail_page.click_close_button()
        """
        logger.info("Clicking Close button on Tracking Center Item Detail page...")
        
        try:
            # Locate the Close button using role-based selector (most stable)
            # This uses the button role and matches the text "Close"
            close_button = self.page.get_by_role("button", name=item_detail_locators.CLOSE_BUTTON_TEXT)
            
            # Wait for button to be visible and enabled
            close_button.wait_for(state="visible", timeout=10000)
            logger.info("✓ Close button is visible")
            
            # Click the Close button
            close_button.click()
            logger.info("✓ Close button clicked successfully")
            
            # Wait for page stabilization after close
            self.page.wait_for_timeout(2000)
            logger.info("✓ Page stabilized after Close button click")
            
        except Exception as e:
            logger.error(f"✗ Failed to click Close button: {e}")
            raise AssertionError(
                f"Failed to click Close button. "
                f"Locator: button[role='button'][name='Close']. "
                f"HTML: <button type='button' class='btn btn-default'>Close</button>. "
                f"Error: {e}"
            ) from e

    def click_cancel_button(self) -> None:
        """
        Click the Cancel button on the Tracking Center Item Detail page.
        
        This method:
        1. Locates the Cancel button using CSS selector (id-based for stability)
        2. Waits for the button to be visible
        3. Scrolls into view if needed for interactivity
        4. Clicks the button with retry logic using retry_until_true utility
        5. Waits for page stabilization after click
        
        The Cancel button HTML:
            <a href="#" class="btn btn-default" id="cancelRequest" 
               onclick="setOmniture('Tracking Center:::Tracking Center_Details page Cancel button')">
                Cancel
            </a>
        
        Selector Strategy: Uses CSS selector "a#cancelRequest" - stable & unique ID-based
        
        Returns:
            None
            
        Raises:
            AssertionError: If Cancel button not found or all click attempts fail
            
        Example:
            item_detail_page.click_cancel_button()
        """
        logger.info("Clicking Cancel button on Tracking Center Item Detail page...")
        
        try:
            # Step 1: Locate the Cancel button using CSS selector with ID
            # Selector: a#cancelRequest (most stable - uses unique ID)
            cancel_button = self.page.locator(item_detail_locators.CANCEL_BUTTON_SELECTOR)
            
            # Step 2: Wait for button to be visible in the DOM
            logger.info("Waiting for Cancel button to be visible...")
            cancel_button.wait_for(state="visible", timeout=10000)
            logger.info("✓ Cancel button is visible")
            
            # Step 3: Scroll into view to ensure it's in viewport (important for clicking)
            logger.info("Scrolling Cancel button into view...")
            cancel_button.scroll_into_view_if_needed()
            logger.info("✓ Cancel button scrolled into view")
            
            # Step 4: Click the button with retry logic using retry_until_true utility
            # This provides resilience for timing issues in headless/headed modes
            logger.info("Attempting to click Cancel button with retry logic...")
            
            def attempt_click() -> bool:
                """Attempt to click the cancel button and return True on success"""
                try:
                    cancel_button.click(timeout=5000)
                    logger.debug("Cancel button click successful")
                    return True
                except Exception as click_error:
                    logger.debug(f"Cancel button click attempt failed: {click_error}")
                    return False
            
            try:
                # Use retry_until_true from utils.retry_utils for robust retry logic
                # Max 3 attempts with 1 second delay between attempts
                retry_until_true(
                    condition=attempt_click,
                    max_attempts=3,
                    delay=1.0,
                    error_message="Failed to click Cancel button after retries"
                )
                logger.info("✓ Cancel button clicked successfully after retries")
            except RetryError as retry_error:
                logger.error(f"✗ All click retry attempts failed: {retry_error}")
                raise AssertionError(
                    f"Failed to click Cancel button after 3 retry attempts. "
                    f"Locator: {item_detail_locators.CANCEL_BUTTON_SELECTOR}. "
                    f"Error: {retry_error}"
                ) from retry_error
            
            # Step 5: Wait for page stabilization after click
            logger.info("Waiting for page stabilization after Cancel button click...")
            self.page.wait_for_timeout(2000)
            logger.info("✓ Page stabilized after Cancel button click")
            
        except AssertionError:
            # Re-raise assertion errors as-is
            raise
        except Exception as e:
            logger.error(f"✗ Failed to interaction with Cancel button: {e}")
            raise AssertionError(
                f"Failed to click Cancel button. "
                f"Locator: {item_detail_locators.CANCEL_BUTTON_SELECTOR}. "
                f"HTML: <a href='#' class='btn btn-default' id='cancelRequest'>Cancel</a>. "
                f"Error: {e}"
            ) from e

    def click_finish_now_button(self, timeout: int = 30000) -> None:
        """
        Click the Finish Now button on the Tracking Center Item Detail page.
        
        This method:
        1. Locates the Finish Now button using XPath
        2. Waits for the button to be visible
        3. Scrolls into view if needed for interactivity
        4. Clicks the button and waits for page navigation
        5. Waits for page stabilization after navigation
        
        The Finish Now button HTML:
            <a href="#"><span>Finish Now</span></a>
        
        Selector Strategy: Uses XPath "//a[contains(text(),'Finish Now')]" to locate the button link
        
        Args:
            timeout: Maximum time to wait for button visibility in milliseconds (default: 30000ms)
        
        Returns:
            None
            
        Raises:
            AssertionError: If Finish Now button not found or click fails
            PlaywrightTimeoutError: If button visibility times out or page doesn't navigate
            
        Example:
            item_detail_page.click_finish_now_button()
        """
        logger.info("Clicking Finish Now button on Tracking Center Item Detail page...")
        
        try:
            # Step 1: Locate the Finish Now button using XPath
            # Selector: //a[contains(text(),'Finish Now')]
            finish_now_button = self.page.locator(item_detail_locators.FINISH_NOW_BUTTON)
            
            # Step 2: Wait for button to be visible in the DOM
            logger.info(f"Waiting for Finish Now button to be visible (timeout: {timeout}ms)...")
            finish_now_button.wait_for(state="visible", timeout=timeout)
            logger.info("✓ Finish Now button is visible")
            
            # Step 3: Scroll into view to ensure it's in viewport (important for clicking)
            logger.info("Scrolling Finish Now button into view...")
            finish_now_button.scroll_into_view_if_needed()
            logger.info("✓ Finish Now button scrolled into view")
            
            # Step 4: Click the button with page navigation wait
            # Using click() directly without retry to avoid stale locator issues during navigation
            # Increased timeout to 120s to allow for page navigation to complete
            logger.info("Clicking Finish Now button...")
            finish_now_button.click(timeout=120000)
            logger.info("✓ Finish Now button clicked")
            
            # Step 5: Wait for page navigation after click
            logger.info("Waiting for page navigation/load after Finish Now button click...")
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("✓ Page loaded after Finish Now button click")
            
            logger.info("✓ Finish Now button click completed successfully")
            
        except AssertionError:
            # Re-raise assertion errors as-is
            raise
        except Exception as e:
            logger.error(f"✗ Failed to interact with Finish Now button: {e}")
            raise AssertionError(
                f"Failed to click Finish Now button. "
                f"Locator: {item_detail_locators.FINISH_NOW_BUTTON}. "
                f"HTML: <a href='#'><span>Finish Now</span></a>. "
                f"Error: {e}"
            ) from e

    def confirm_cancel_dialog(self) -> None:
        """
        Confirm the cancel request by clicking 'Yes' in the confirmation dialog.
        
        This method:
        1. Uses existing DialogHandler.wait_for_dialog() to detect jQuery UI dialog
        2. Locates the 'Yes' button using Playwright get_by_text() locator
        3. Clicks 'Yes' with retry logic for resilience
        4. Waits for dialog to close
        5. Waits for page stabilization
        
        The Confirmation Dialog HTML:
            <div tabindex="-1" role="dialog" class="ui-dialog ui-corner-all ui-widget 
                 ui-widget-content ui-front ui-dialog-buttons" aria-describedby="dialog-confirm">
                <div class="ui-dialog-titlebar ...">
                    <span class="ui-dialog-title">You are about to cancel this request.</span>
                </div>
                <div id="dialog-confirm" class="ui-dialog-content ...">
                    <p>Cancelling this request will close the item...</p>
                </div>
                <div class="ui-dialog-buttonset">
                    <div class="button_container">
                        <button type="button" class="formButton">Yes</button>
                    </div>
                    <div class="button_container">
                        <button type="button" class="formButton">No</button>
                    </div>
                </div>
            </div>
        
        Dialog Selector: `.ui-dialog` (jQuery UI dialog class)
        Yes Button Selector: Playwright `get_by_text("Yes")` locator (simplest & most stable)
        
        Returns:
            None
            
        Raises:
            AssertionError: If dialog doesn't appear or Yes button click fails
            PlaywrightTimeoutError: If dialog detection times out
            
        Example:
            item_detail_page.click_cancel_button()          # Click Cancel to trigger dialog
            item_detail_page.confirm_cancel_dialog()        # Confirm cancellation in dialog
        """
        logger.info("Confirming cancel request via dialog...")
        
        try:
            # Step 1: Detect dialog using existing DialogHandler.wait_for_dialog() utility
            logger.info("Step 1: Waiting for cancel confirmation dialog to appear...")
            dialog_handler = DialogHandler(self.page)
            
            try:
                dialog = dialog_handler.wait_for_dialog(timeout=10000)
                logger.info("✓ Cancel confirmation dialog detected")
            except Exception as dialog_error:
                logger.error(f"✗ Failed to detect cancel confirmation dialog: {dialog_error}")
                raise AssertionError(
                    f"Cancel confirmation dialog did not appear. "
                    f"Dialog Selector: {item_detail_locators.CANCEL_CONFIRMATION_DIALOG_SELECTOR}. "
                    f"This dialog should appear after clicking the Cancel button. "
                    f"Error: {dialog_error}"
                ) from dialog_error
            
            # Step 2: Locate the 'Yes' button using Playwright get_by_role locator
            # get_by_role is more reliable for jQuery UI buttons than get_by_text
            logger.info("Step 2: Locating 'Yes' button in confirmation dialog...")
            
            # Try multiple locator strategies in order of preference
            yes_button = None
            locator_strategies = [
                ("get_by_role button + filter text(Yes)", lambda: self.page.get_by_role("button").filter(has_text="Yes").first),
                ("get_by_text in dialog", lambda: self.page.locator(".ui-dialog").first.get_by_text("Yes").first),
            ]
            
            for strategy_name, strategy_locator in locator_strategies:
                try:
                    test_button = strategy_locator()
                    test_button.wait_for(state="visible", timeout=3000)
                    yes_button = test_button
                    logger.info(f"✓ 'Yes' button located using strategy: {strategy_name}")
                    break
                except Exception as e:
                    logger.debug(f"Strategy '{strategy_name}' failed: {e}")
                    continue
            
            if yes_button is None:
                raise AssertionError(
                    f"'Yes' button not found in cancel confirmation dialog using any locator strategy. "
                    f"Tried: get_by_role('button'), get_by_text in dialog scope. "
                    f"Button Text: '{item_detail_locators.CANCEL_CONFIRM_YES_BUTTON_TEXT}'."
                )
            
            logger.info("✓ 'Yes' button is visible and clickable")
            
            # Step 3: Click 'Yes' button with retry logic for resilience
            logger.info("Step 3: Clicking 'Yes' button with retry logic...")
            
            def attempt_click_yes() -> bool:
                """Attempt to click Yes button and verify it actually worked"""
                try:
                    # jQuery UI dialogs can have animation delays - add wait before clicking
                    self.page.wait_for_timeout(500)
                    
                    # Scroll button into view to ensure it's fully accessible
                    yes_button.scroll_into_view_if_needed()
                    logger.debug("Button scrolled into view")
                    
                    # Log button details for debugging
                    button_html = yes_button.evaluate("el => el.outerHTML")
                    logger.debug(f"Button HTML: {button_html[:100]}...")
                    
                    # Click with force=True to bypass any UI overlay issues
                    # force=True ignores any covering elements
                    yes_button.click(timeout=5000, force=True)
                    logger.debug("'Yes' button click command executed")
                    
                    # Add delay for dialog to start closing
                    self.page.wait_for_timeout(500)
                    
                    # Verify click actually worked by checking if dialog is still visible
                    dialog_still_visible = False
                    try:
                        dialog_locator = self.page.locator(item_detail_locators.CANCEL_CONFIRMATION_DIALOG_SELECTOR).first
                        dialog_locator.wait_for(state="visible", timeout=1000)
                        dialog_still_visible = True
                        logger.debug("✗ Dialog still visible after click - click may have failed")
                        return False
                    except:
                        # Dialog not visible = click worked!
                        logger.debug("✓ Dialog is no longer visible after click - click succeeded")
                        return True
                    
                except Exception as click_error:
                    logger.debug(f"'Yes' button click attempt failed: {click_error}")
                    return False
            
            try:
                # Use retry_until_true for robust retry logic
                # Max 3 attempts with 2 second delay between attempts (for jQuery animation settling)
                retry_until_true(
                    condition=attempt_click_yes,
                    max_attempts=3,
                    delay=2.0,
                    error_message="Failed to click 'Yes' button in cancel confirmation dialog"
                )
                logger.info("✓ 'Yes' button clicked successfully and dialog closed")
            except RetryError as retry_error:
                logger.error(f"✗ All click retry attempts failed: {retry_error}")
                raise AssertionError(
                    f"Failed to click 'Yes' button after 3 retry attempts. "
                    f"Button Text: '{item_detail_locators.CANCEL_CONFIRM_YES_BUTTON_TEXT}'. "
                    f"Error: {retry_error}"
                ) from retry_error
            
            # Step 4: Confirm dialog has closed
            logger.info("Step 4: Verifying confirmation dialog is closed...")
            try:
                # Verify dialog is no longer visible
                dialog_check = self.page.locator(item_detail_locators.CANCEL_CONFIRMATION_DIALOG_SELECTOR).first
                dialog_check.wait_for(state="hidden", timeout=5000)
                logger.info("✓ Confirmation dialog has closed")
            except Exception as close_error:
                logger.warning(f"⚠ Dialog may still be closing: {close_error}")
                # Add extra delay for dialog animations
                self.page.wait_for_timeout(1000)
            
            # Step 5: Wait for page stabilization
            logger.info("Step 5: Waiting for page stabilization after dialog close...")
            self.page.wait_for_timeout(2000)
            logger.info("✓ Page stabilized after dialog confirmation")
            
            logger.info("[SUCCESS] Cancel confirmation completed via dialog")
            
        except AssertionError:
            # Re-raise assertion errors as-is
            raise
        except Exception as e:
            logger.error(f"✗ Unexpected error during cancel dialog confirmation: {e}")
            raise AssertionError(
                f"Failed to confirm cancel request via dialog. "
                f"Dialog Selector: {item_detail_locators.CANCEL_CONFIRMATION_DIALOG_SELECTOR}. "
                f"Yes Button Text: '{item_detail_locators.CANCEL_CONFIRM_YES_BUTTON_TEXT}'. "
                f"Error: {e}"
            ) from e


def _create_min_pdf_for_upload(path: str) -> None:
    """
    Create a minimal valid PDF file for testing document uploads on Item Detail page.
    
    This helper function generates a compact, valid PDF file with proper structure:
    - PDF header (%PDF-1.0)
    - Object definitions (Catalog, Pages, Page)
    - Cross-reference table (xref)
    - Trailer
    
    Args:
        path: File path where the PDF should be created
        
    Returns:
        None - Creates file at specified path
        
    Example:
        _create_min_pdf_for_upload("/tmp/test_upload.pdf")
    """
    pdf_content = (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n190\n%%EOF"
    )
    with open(path, "wb") as f:
        f.write(pdf_content)
