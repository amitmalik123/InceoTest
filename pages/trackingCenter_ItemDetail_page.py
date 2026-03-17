from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class TrackingCenterItemDetailPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"
    
    # ========================================================================================
    # LOCATORS - All page element locators defined at class level for easy maintenance
    # ========================================================================================
    
    # Status field locator
    STATUS_LABEL = "span:has-text('Status:') + label"
    
    # Advisor Alert Required field locator
    ADVISOR_ALERT_REQUIRED_LABEL = "span:has-text('Advisor Alert Required:') + label"
    
    # Item Number (D-number) field locator
    ITEM_NUMBER_LABEL = "span:has-text('Item Number:') + label"
    
    # Agent Name field locator
    AGENT_NAME_LABEL = "//span[text()='Agent Name']/following-sibling::label"
    
    # Column flow container (buttons area)
    COLUMN_FLOW_CONTAINER = "div#column-flow-container"
    
    # Buttons within the column flow container
    BUTTONS_SELECTOR = "button, a.btn, .item-detail-button"
    
    # Notes grid table
    NOTES_GRID_TABLE = "table#TrackingCenterItemDetailNotesGrid"
    
    # Description cells in notes grid
    NOTES_DESCRIPTION_CELLS = "td[aria-describedby='TrackingCenterItemDetailNotesGrid_description']"
    
    # Data rows in notes grid (excluding header)
    NOTES_GRID_DATA_ROWS = "tbody tr:not(:first-child)"

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
        status_label = self.page.locator(self.STATUS_LABEL)
        
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
        advisor_alert_label = self.page.locator(self.ADVISOR_ALERT_REQUIRED_LABEL)
        
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
        item_number_label = self.page.locator(self.ITEM_NUMBER_LABEL)
        
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
        agent_name_label = self.page.locator(self.AGENT_NAME_LABEL)
        
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
        container = self.page.locator(self.COLUMN_FLOW_CONTAINER)
        
        # Wait for container to be visible
        container.wait_for(state="visible", timeout=10000)
        logger.info("Column-flow-container is visible")
        
        # Find all buttons/links within the container
        # This includes <button>, <a> elements with class "btn", and elements with class "item-detail-button"
        all_buttons = container.locator(self.BUTTONS_SELECTOR)
        
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
        notes_grid = self.page.locator(self.NOTES_GRID_TABLE)
        
        # Wait for the grid to be visible
        notes_grid.wait_for(state="visible", timeout=10000)
        logger.info("Notes grid is visible")
        
        # Find all description cells (td elements with the description aria-describedby)
        description_cells = notes_grid.locator(self.NOTES_DESCRIPTION_CELLS)
        
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
            notes_grid = self.page.locator(self.NOTES_GRID_TABLE)
            
            # Wait for grid to be visible
            notes_grid.wait_for(state="visible", timeout=5000)
            logger.debug("Notes grid is visible")
            
            # Find all data rows in the grid (exclude header row)
            # tbody tr:not(:first-child) selects all <tr> except the first one (header)
            grid_rows = notes_grid.locator(self.NOTES_GRID_DATA_ROWS)
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
