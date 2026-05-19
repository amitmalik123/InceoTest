"""APro Prospects List page."""

from typing import Any

from playwright.sync_api import Locator, Page

from pages.Adhesion.base_smart_filter_page import BaseSmartFilterPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProspectsListPage(BaseSmartFilterPage):
    """Page object for the APro prospects list page.

    Locators:
      - actions_button: the button that opens the actions dropdown (id `btnMainActionButton`)
      - items_container: the dropdown container (id `items`)
      - create_prospect_item: the menu item text 'Create Prospect'
      - advisor_name_element: the advisor name display in the page header
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        self.actions_button: Locator = page.locator("#btnMainActionButton")
        self.items_container: Locator = page.locator("#items")
        self.create_prospect_item: Locator = page.get_by_text("Create Prospect", exact=True)
        self.advisor_name_element: Locator = page.locator("div.user div.name")

        # --- Proposals List (non-modal) selectors ---
        # Proposals table (Kendo Grid Data Table) - main proposals list
        # Use :not([data-role="selectable"]) to exclude secondary grids that may exist after proposal creation
        self.proposals_table: Locator = page.locator(
            "table.k-grid-table:not([data-role='selectable'])"
        )
        # Proposal data rows in the table
        self.proposal_rows: Locator = page.locator(
            "table.k-grid-table:not([data-role='selectable']) tbody tr"
        )
        # Individual proposal cells within a row
        self.proposal_row_name: Locator = page.locator(
            "table.k-grid-table:not([data-role='selectable']) tbody tr td:nth-of-type(1)"
        )
        self.proposal_row_status: Locator = page.locator(
            "table.k-grid-table:not([data-role='selectable']) tbody tr td:nth-of-type(3)"
        )
        # Column headers in the Kendo grid header container
        self.column_headers: Locator = page.locator("div.k-grid-header th")
        # Breadcrumb back link to return from proposal wizard
        self.proposal_builder_back: Locator = page.locator("#divGlobalBack")

    def open_actions(self) -> None:
        """Open the actions dropdown."""
        logger.info("Opening APro actions dropdown")
        self.click(self.actions_button)

    def wait_for_items(self, timeout: int = 10000) -> None:
        """Wait for the actions items container to be visible."""
        logger.info("Waiting for actions items to be visible")
        self.wait_for_element(self.items_container, state="visible", timeout=timeout)

    def click_create_prospect(self) -> None:
        """Click the 'Create Prospect' item inside the actions dropdown."""
        logger.info("Clicking 'Create Prospect' in APro actions")
        # Ensure dropdown is open and items visible
        try:
            self.wait_for_items()
        except Exception:
            # Attempt to open then wait again
            self.open_actions()
            self.wait_for_items()

        self.click(self.create_prospect_item)

    def get_advisor_name(self) -> str:
        """Get the logged-in advisor name from the page header.

        Returns:
            str: The advisor name displayed in the page header
        """
        logger.info("Retrieving advisor name from page header")
        self.advisor_name_element.wait_for(state="visible", timeout=5000)
        advisor_name = self.advisor_name_element.inner_text().strip()
        logger.info(f"Retrieved advisor name: {advisor_name}")
        return advisor_name

    # --- Row Data Access Methods ---
    # Column mapping for the proposals grid (1-indexed for CSS nth-of-type)
    _COLUMN_INDEX_MAP = {
        "name": 1,
        "date_created": 2,
        "status": 3,
        "advisor": 4,
        "id": 5,
        "strategy": 6,
        "composite": 7,
        "investment_amount": 8,
        "risk_assessment_completed": 9,
        "finished": 10,
    }

    def wait_for_prospects_list(self, timeout: int = 10000) -> None:
        """Wait for the prospects list table to be visible and ready.

        Waits for overlay to disappear (modal closed), brief DOM settle,
        then waits for main table to be visible.
        """
        logger.info("Waiting for prospects list to be visible")
        overlay = self.page.locator("div.k-overlay")
        from contextlib import suppress

        with suppress(Exception):
            self.wait_for_element(
                overlay, state="hidden", timeout=timeout
            )  # Overlay may not always be present

        # Brief DOM settle delay
        self.page.wait_for_timeout(200)

        # Wait for main table visibility
        self.wait_for_element(self.proposals_table, state="visible", timeout=timeout)
        logger.info("Modal overlay closed successfully")
        self.wait_for_element(self.proposals_table, state="visible", timeout=timeout)

    def click_proposal_builder_back(self) -> None:
        """Click the Proposal Builder breadcrumb to return to the prospects list."""
        logger.info("Clicking Proposal Builder breadcrumb to return to prospects list")
        self.click(self.proposal_builder_back)

    def get_row_cell(self, row_index: int, column_index: int) -> Locator:
        """Get a cell locator from the proposals grid by row and column indices.

        Args:
            row_index: 0-based row index
            column_index: 1-based column index (use column names from _COLUMN_INDEX_MAP)

        Returns:
            Locator for the cell
        """
        selector = f"table.k-grid-table:not([data-role='selectable']) tbody tr:nth-child({row_index + 1}) td:nth-child({column_index})"
        return self.page.locator(selector)

    def get_row_cell_by_column_name(self, row_index: int, column_name: str) -> Locator:
        """Get a cell locator by row index and column name.

        Args:
            row_index: 0-based row index
            column_name: Column name from _COLUMN_INDEX_MAP

        Returns:
            Locator for the cell
        """
        if column_name not in self._COLUMN_INDEX_MAP:
            raise ValueError(
                f"Unknown column: {column_name}. Valid columns: {list(self._COLUMN_INDEX_MAP.keys())}"
            )
        column_index = self._COLUMN_INDEX_MAP[column_name]
        return self.get_row_cell(row_index, column_index)

    def get_row_cell_text(self, row_index: int, column_index: int, timeout: int = 5000) -> str:
        """Get the text content of a cell by row and column indices.

        Args:
            row_index: 0-based row index
            column_index: 1-based column index
            timeout: Wait timeout in ms

        Returns:
            Trimmed cell text
        """
        cell = self.get_row_cell(row_index, column_index)
        self.wait_for_element(cell, state="visible", timeout=timeout)
        return cell.inner_text().strip()

    def get_row_cell_text_by_column_name(
        self, row_index: int, column_name: str, timeout: int = 5000
    ) -> str:
        """Get the text content of a cell by row index and column name.

        Args:
            row_index: 0-based row index
            column_name: Column name from _COLUMN_INDEX_MAP
            timeout: Wait timeout in ms

        Returns:
            Trimmed cell text
        """
        cell = self.get_row_cell_by_column_name(row_index, column_name)
        self.wait_for_element(cell, state="visible", timeout=timeout)
        return cell.inner_text().strip()

    def get_row_data(self, row_index: int, timeout: int = 5000) -> dict:
        """Get all column data for a row as a dictionary.

        Args:
            row_index: 0-based row index
            timeout: Wait timeout in ms

        Returns:
            Dict mapping column_name -> cell_text for all columns
        """
        row_data = {}
        for column_name, column_index in self._COLUMN_INDEX_MAP.items():
            try:
                text = self.get_row_cell_text(row_index, column_index, timeout=timeout)
                row_data[column_name] = text
            except Exception as exc:
                logger.warning(f"Could not read column {column_name}: {exc}")
                row_data[column_name] = ""

        return row_data

    def get_row_count(self) -> int:
        """Get the count of visible data rows in the prospects grid (per spec §3.5).

        Returns the count of <tbody> rows in the main proposals table, excluding
        the header row. Useful for verifying filter behavior and grid state.

        Returns:
            int: Count of data rows in the grid
        """
        count = self.proposal_rows.count()
        logger.info(f"Prospects list row count: {count}")
        return count

    def are_column_headers_visible(self) -> bool:
        """Check if column headers are visible in the prospects grid (per spec §3.6).

        Verifies that the grid header row exists and is visible, which indicates
        the grid has properly rendered after an export operation.

        Kendo grids store headers in a separate div.k-grid-header element.

        Returns:
            bool: True if at least one column header is visible, False otherwise
        """
        try:
            # Wait briefly for headers to be present
            self.column_headers.first.wait_for(state="visible", timeout=2000)

            # Check if at least one header cell is visible
            cell_count = self.column_headers.count()
            is_visible = cell_count > 0
            logger.info(f"Column headers visible: {is_visible} ({cell_count} headers found)")
            return is_visible
        except Exception as exc:
            logger.warning(f"Could not verify column headers visibility: {exc}")
            return False

    def find_proposal_row(
        self, proposal_identifier: str, original_proposal_data: dict[Any, Any] | None = None
    ) -> int:
        """Find and return the row index of a proposal by identifier.

        Supports:
        - "original" or "original proposal": First row (or uses original_proposal_data if provided)
        - "copied" or "copied proposal": Finds the copy by matching client name and excluding original by ID
        - Numeric string: Uses as direct row index

        Args:
            proposal_identifier: Identifier for the proposal to find
            original_proposal_data: Dict of stored original proposal row data (for finding copies)

        Returns:
            The row index (0-based) of the proposal

        Raises:
            AssertionError if the proposal cannot be found
        """
        logger.info(f"Finding proposal: {proposal_identifier}")

        # Wait for Kendo grid to load
        self.page.locator(".k-loading-mask, .k-overlay").first.wait_for(
            state="hidden", timeout=10000
        )
        self.proposal_rows.first.wait_for(state="visible", timeout=10000)

        total_rows = self.proposal_rows.count()
        logger.info(f"Total proposals in list: {total_rows}")

        # Handle numeric row index
        if proposal_identifier.isdigit():
            row_index = int(proposal_identifier)
            if row_index < total_rows:
                logger.info(f"Using proposal at row {row_index}")
                return row_index
            raise AssertionError(f"Row index {row_index} out of range (total: {total_rows})")

        # Handle "original" identifier
        if proposal_identifier.lower() in ("original", "original proposal"):
            # Try to use provided original_proposal_data first
            if original_proposal_data:
                # Use the stored original data to find it (handles race conditions)
                for i in range(total_rows):
                    row_data = self.get_row_data(i)
                    if row_data == original_proposal_data:
                        logger.info(f"Found original proposal at row {i}")
                        return i
            # Fallback: first row
            logger.info("Using first row as original proposal (fallback)")
            return 0

        # Handle "copied" identifier
        if proposal_identifier.lower() in ("copied", "copied proposal"):
            # Get provided original_proposal_data
            if not original_proposal_data:
                raise AssertionError(
                    "Original proposal data not found. Cannot identify copied proposal."
                )

            original_client = original_proposal_data.get("client", "").strip()
            original_id = original_proposal_data.get("id", "").strip()
            logger.info(
                f"Looking for copied proposal (client: {original_client}, excluding ID: {original_id})"
            )

            # Find proposal with same client but different ID (excludes the original)
            for i in range(total_rows):
                row_data = self.get_row_data(i)
                row_client = row_data.get("client", "").strip()
                row_id = row_data.get("id", "").strip()

                if row_client == original_client and row_id != original_id:
                    logger.info(f"Found copied proposal at row {i} (ID: {row_id})")
                    return i

            raise AssertionError(
                f"Could not find copied proposal for client '{original_client}' in prospects list"
            )

        raise ValueError(
            f"Unknown proposal identifier: '{proposal_identifier}'. "
            f"Supported: 'original', 'copied', or numeric row index"
        )

    def resume_proposal_from_row(self, row_index: int, timeout: int = 15000) -> None:
        """Click a proposal row to resume/reopen the proposal wizard.

        Clicks the first link in the specified row, which opens the proposal
        wizard at the last completed step.

        Args:
            row_index: 0-based row index to click
            timeout: Wait timeout for wizard to load (ms)
        """
        logger.info(f"Resuming proposal from row {row_index}")

        # Get the row and click the first link (proposal name)
        row = self.proposal_rows.nth(row_index)
        proposal_link = row.locator("td a").first
        proposal_link.wait_for(state="visible", timeout=5000)
        proposal_link.click()

        logger.info(f"Clicked proposal link in row {row_index}, waiting for proposal to load...")

        # Wait for the wizard to load (will be on History step since we're resuming)
        # Use wait_for_history_step from self.history POM
        from pages.Adhesion.apro_step_history import ProposalHistoryPage

        history_page = ProposalHistoryPage(self.page)
        history_page.wait_for_history_step(timeout=timeout)
