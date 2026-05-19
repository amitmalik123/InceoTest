"""APro Proposal Holdings step (wizard-4)."""

import os
from typing import Any

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalHoldingsPage(BasePage):
    """Page object for APro proposal Holdings step (wizard-4).

    Handles tax lot entry: symbol search/autocomplete, acquisition date,
    shares, cost, and holding verification.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 5 (Holdings) container
        self.step_holdings_panel: Locator = page.locator("#proposal-wizard-4")

        # Symbol/ticker search and entry
        self.symbol_search_input: Locator = page.locator("#SymbolSearch")
        self.symbol_input: Locator = page.locator("#Symbol")

        # Holding details inputs
        self.acquisition_input: Locator = page.locator("#Acquisition")
        self.price_input: Locator = page.locator("#Price")

        # Prefer visible Kendo wrapper inputs over hidden backing fields
        self.shares_input: Locator = page.locator(
            '.form-input-group:has-text("Shares") input.k-input-inner'
        ).first
        self.cost_input: Locator = page.locator(
            '.form-input-group:has-text("Cost") input.k-input-inner:visible'
        ).first
        self.value_input: Locator = page.locator("#Value")

        # Action buttons
        self.holdings_import_button: Locator = page.locator("#btn-holdings-import")
        self.save_holding_button: Locator = page.get_by_text("SAVE TAX LOT", exact=True)
        self.clear_holding_button: Locator = page.get_by_text("CLEAR", exact=True)
        self.delete_holding_button: Locator = page.get_by_text("DELETE", exact=True)

        # Import modal selectors
        self.import_modal: Locator = page.locator("#HoldingsImportModal")
        self.download_template_button: Locator = page.get_by_text("DOWNLOAD TEMPLATE", exact=True)
        self.upload_data_button: Locator = page.get_by_text("UPLOAD DATA", exact=True)
        self.file_input: Locator = page.locator("#holdings-import-file-input-hidden")
        self.import_submit_button: Locator = page.locator("#holdings-import-submit-btn")
        self.import_cancel_button: Locator = page.locator(
            "button[onclick*='HoldingsImport.cancel']"
        )
        self.import_preview_table: Locator = page.locator("#holdings-inline-preview-table")
        self.import_preview_rows: Locator = page.locator("#holdings-inline-preview-tbody tr")
        self.holdings_count_display: Locator = page.locator("#holdings-uploaded-file-details-count")

    def wait_for_holdings_step(self, timeout: int = 10000) -> None:
        """Wait for holdings step (step 5, proposal-wizard-4) to be visible."""
        logger.info("Waiting for holdings step to be visible")
        self.wait_for_element(self.step_holdings_panel, state="visible", timeout=timeout)

    def set_symbol(self, symbol: str) -> None:
        """Set the stock symbol/ticker via autocomplete.

        Types the symbol into the search field, waits for dropdown,
        and selects the matching option.

        Args:
            symbol: Stock ticker (e.g., "GOOG", "AAPL")
        """
        logger.info(f"Setting Symbol: {symbol}")

        # Type into search field
        self.fill(self.symbol_search_input, symbol)
        self.page.wait_for_timeout(500)  # Wait for autocomplete dropdown

        # Click the first matching option in the dropdown
        try:
            dropdown_item = self.page.locator(f".k-list-item:has-text('{symbol}')").first
            dropdown_item.click()
            logger.info(f"Selected {symbol} from autocomplete dropdown")
        except Exception as exc:
            logger.warning(f"Could not select from dropdown, filling directly: {exc}")
            self.fill(self.symbol_input, symbol)

    def set_acquisition(self, date_str: str) -> None:
        """Set the acquisition date in mm/dd/yyyy format.

        Args:
            date_str: Date string in format mm/dd/yyyy
        """
        logger.info(f"Setting Acquisition date: {date_str}")
        self.empty_field(self.acquisition_input)
        self.fill(self.acquisition_input, date_str)

    def set_price(self, value: str) -> None:
        """Set the price field."""
        logger.info(f"Setting Price: {value}")
        self.fill(self.price_input, value)

    def set_shares(self, value: str) -> None:
        """Set the shares field using Kendo NumericTextBox API.

        Args:
            value: Number of shares as string
        """
        logger.info(f"Setting Shares: {value}")

        # Use Kendo NumericTextBox API to set value
        self.page.evaluate(
            f"""
        (function() {{
            // Find by ID first
            var widget = $('#Shares').data('kendoNumericTextBox');

            if (widget) {{
                widget.value('{value}');
                widget.trigger('change');
                return {{ success: true, value: widget.value() }};
            }} else {{
                // Fallback: find by looking through all numeric inputs
                var inputs = document.querySelectorAll('input.k-input-inner[type="text"][role="spinbutton"]');
                if (inputs.length > 0) {{
                    var input = inputs[0];  // First spinbutton is Shares
                    input.value = '{value}';
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return {{ success: true, value: '{value}' }};
                }} else {{
                    throw new Error('Shares input not found');
                }}
            }}
        }})()
        """
        )

    def set_cost(self, value: str) -> None:
        """Set the cost field using Kendo NumericTextBox API.

        Args:
            value: Cost per share as string
        """
        logger.info(f"Setting Cost: {value}")

        # Use Kendo NumericTextBox API to set value
        self.page.evaluate(
            f"""
        (function() {{
            // Find by ID first
            var widget = $('#Cost').data('kendoNumericTextBox');

            if (widget) {{
                widget.value('{value}');
                widget.trigger('change');
                return {{ success: true, value: widget.value() }};
            }} else {{
                // Fallback: find by looking through all numeric inputs
                var inputs = document.querySelectorAll('input.k-input-inner[type="text"][role="spinbutton"]');
                if (inputs.length > 1) {{
                    var input = inputs[1];  // Second spinbutton is Cost
                    input.value = '{value}';
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return {{ success: true, value: '{value}' }};
                }} else {{
                    throw new Error('Cost input not found');
                }}
            }}
        }})()
        """
        )

    def add_holding(self, holding: list) -> None:
        """Add a complete holding: [ticker, shares, cost, date(optional)].

        Args:
            holding: List of [symbol, shares, cost] or [symbol, shares, cost, acquisition_date]
        """
        logger.info(f"Adding holding: {holding}")

        if len(holding) < 3:
            raise ValueError(f"Holding must have at least 3 elements: {holding}")

        symbol, shares, cost = holding[:3]
        acq_date = holding[3] if len(holding) > 3 else None

        # Set fields
        self.set_symbol(symbol)
        self.page.wait_for_timeout(1000)  # Brief pause for UI to update
        self.set_acquisition(acq_date or "05/01/2026")  # Default to today if not provided
        self.page.wait_for_timeout(1000)  # Brief pause for UI to update
        self.set_shares(str(shares))
        self.page.wait_for_timeout(1000)  # Brief pause for UI to update
        self.set_cost(str(cost))
        self.page.wait_for_timeout(1000)  # Brief pause for UI to update

        # Save the holding
        logger.info(f"Clicked SAVE TAX LOT button for {symbol}")
        self.click(self.save_holding_button)
        self.page.wait_for_timeout(1000)  # Brief pause for UI to update

    def get_value(self) -> str:
        """Read the computed Value field."""
        logger.info("Getting Value field")
        return self.get_text(self.value_input)

    def clear_holding_form(self) -> None:
        """Clear the holding entry form."""
        logger.info("Clearing holding form")
        self.click(self.clear_holding_button)

    def delete_holding(self) -> None:
        """Delete a holding via the UI."""
        logger.info("Deleting holding")
        self.click(self.delete_holding_button)

    def verify_saved_holding(self, holdings: list, timeout: int = 10000) -> list:
        """Verify that all holdings appear in the UI after being added.

        Args:
            holdings: List of [ticker, shares, cost, date] lists
            timeout: Wait timeout in ms

        Returns:
            List of missing holdings (empty if all found)
        """
        logger.info(f"Checking saved holdings list of {len(holdings)} entries")

        self.wait_for_element(self.step_holdings_panel, state="visible", timeout=timeout)

        # Wait for Kendo grid to display at least one row (skip header row)
        holdings_grid_rows = self.page.locator("#proposal-wizard-4 [role='grid'] [role='row']").nth(
            1
        )  # Skip header row
        holdings_grid_rows.wait_for(state="visible", timeout=timeout)

        holdings_text = ""
        from contextlib import suppress

        with suppress(Exception):
            holdings_text = self.step_holdings_panel.inner_text()

        missing = []
        for holding in holdings:
            symbol = holding[0]
            if symbol.upper() not in holdings_text.upper():
                missing.append(holding)
                logger.warning(f"Holding {symbol} not found in UI")
            else:
                logger.info(f"Holding {symbol} verified in list")

        return missing

    def select_holding_row(self, row_index: int) -> None:
        """Click a holding row in the grid to load it for editing.

        Args:
            row_index: 0-based index of the row to select (0 = first data row)
        """
        logger.info(f"Selecting holding row at index {row_index}")

        # Get all rows from the holdings grid
        # Holdings are displayed in a Kendo grid within the step panel
        rows = self.step_holdings_panel.locator("table tbody tr")

        if rows.count() <= row_index:
            raise ValueError(f"Row index {row_index} out of range (only {rows.count()} rows)")

        target_row = rows.nth(row_index)
        target_row.click()
        self.page.wait_for_timeout(1000)  # Wait for form to populate (matching add_holding pattern)
        logger.info(f"Holding row {row_index} selected")

    def edit_holding_field(self, field: str, value: str) -> None:
        """Edit a holding field after selecting a row.

        Args:
            field: Field name ('symbol', 'shares', 'cost', 'acquisition')
            value: New value for the field
        """
        logger.info(f"Editing holding field {field} to: {value}")

        if field.lower() == "symbol":
            self.page.wait_for_timeout(2000)  # Wait for UI to be ready
            # Clear and re-enter symbol (similar to add_holding flow)
            logger.info("Clearing symbol field")
            # Use Ctrl+A to select all, then Delete to clear
            self.symbol_search_input.focus()
            self.symbol_search_input.press("Control+A")
            self.page.wait_for_timeout(300)
            self.symbol_search_input.press("Delete")
            self.page.wait_for_timeout(500)  # Wait for field to clear
            logger.info(f"Symbol field cleared, now entering {value}")
            self.set_symbol(value)
            self.page.wait_for_timeout(1000)  # Wait after setting symbol
        elif field.lower() == "shares":
            self.set_shares(value)
            self.page.wait_for_timeout(1000)  # Wait after setting shares
        elif field.lower() == "cost":
            self.set_cost(value)
            self.page.wait_for_timeout(1000)  # Wait after setting cost
        elif field.lower() == "acquisition":
            self.set_acquisition(value)
            self.page.wait_for_timeout(1000)  # Wait after setting acquisition
        else:
            raise ValueError(f"Unknown field: {field}")

    def save_holding_tax_lot(self) -> None:
        """Click the SAVE TAX LOT button to save edited holding."""
        logger.info("Saving tax lot after edit")
        self.click(self.save_holding_button)
        self.page.wait_for_timeout(1500)  # Wait for grid to update after save
        logger.info("Tax lot saved")

    def get_holding_field_value(self, row_index: int, field: str) -> str:
        """Get the value of a field from a specific holding row in the grid.

        Args:
            row_index: 0-based index of the row
            field: Field name to retrieve ('symbol', 'shares', 'cost', 'acquisition')

        Returns:
            The cell value as a string
        """
        logger.info(f"Getting holding field {field} from row {row_index}")

        # Get all rows from the holdings grid
        rows = self.step_holdings_panel.locator("table tbody tr")

        if rows.count() <= row_index:
            raise ValueError(f"Row index {row_index} out of range (only {rows.count()} rows)")

        target_row = rows.nth(row_index)

        # Map field names to column positions (0-based, counting all td elements)
        # Grid structure: [checkbox, hidden-id, symbol, description, type, class, benchmark, acquisition, shares, cost, price, value]
        field_map = {
            "symbol": 2,  # 3rd td (after checkbox and hidden ID)
            "description": 3,
            "type": 4,
            "class": 5,
            "benchmark": 6,
            "acquisition": 7,  # 8th td
            "shares": 8,  # 9th td
            "cost": 9,  # 10th td
            "price": 10,
            "value": 11,
        }

        if field.lower() not in field_map:
            raise ValueError(f"Unknown field: {field}. Available fields: {list(field_map.keys())}")

        col_index = field_map[field.lower()]
        cell = target_row.locator("td").nth(col_index)
        value = cell.inner_text().strip()

        logger.info(f"Retrieved holding {field}: {value}")
        return value

    def click_next(self) -> None:
        """Click Next button to proceed to Fees step."""
        logger.info("Clicking Next from Holdings step")
        next_button = self.step_holdings_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-4 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button to go back to Tax Management step."""
        logger.info("Clicking Previous from Holdings step")
        prev_button = self.step_holdings_panel.locator("button[data-wizard-previous]")
        prev_button.click()

    def open_import_modal(self, timeout: int = 10000) -> None:
        """Open the holdings import modal by clicking the import button.

        Note: We don't explicitly wait for the modal here. Subsequent operations
        that interact with elements inside the modal (file upload, buttons, etc.)
        will automatically wait for those elements to be visible/actionable.
        """
        logger.info("Opening holdings import modal")
        self.click(self.holdings_import_button)
        # Give the modal a brief moment to animate in
        self.page.wait_for_timeout(300)

    def download_template(self, download_path: str | None = None) -> str:
        """Download the holdings template CSV file.

        Args:
            download_path: Optional directory to save the file. If None, uses system temp directory.

        Returns:
            Path to the downloaded file.
        """
        import tempfile

        logger.info("Downloading holdings template")

        # Wait for download
        with self.page.expect_download() as download_info:
            self.click(self.download_template_button)

        download = download_info.value

        # If no directory specified, use system temp directory
        if download_path is None:
            temp_dir = tempfile.gettempdir()
            download_path = temp_dir

        # Use the file's default suggested filename
        filename = download.suggested_filename
        full_path = os.path.join(download_path, filename)
        download.save_as(full_path)

        logger.info(f"Template downloaded to {full_path}")
        return full_path

    def upload_import_file(self, file_path: str) -> None:
        """Upload a CSV file via the import file chooser.

        Args:
            file_path: Path to the CSV file to upload
        """
        logger.info(f"Uploading holdings import file: {file_path}")

        # Playwright automatically waits for the element
        self.file_input.set_input_files(file_path)
        logger.info("File uploaded")

    def get_preview_row_count(self) -> int:
        """Get the number of rows shown in the import preview.

        Returns:
            Number of data rows in preview (excludes header)
        """
        logger.info("Getting preview row count")
        count = self.import_preview_rows.count()
        logger.info(f"Preview shows {count} rows")
        return count

    def get_total_holdings_count(self) -> int:
        """Get the total holdings count from the upload info display.

        Returns:
            Total number of holdings in the file
        """
        logger.info("Getting total holdings count")
        count_text = self.holdings_count_display.inner_text()
        try:
            count = int(count_text.strip())
            logger.info(f"Total holdings count: {count}")
            return count
        except ValueError:
            logger.warning(f"Could not parse holdings count from '{count_text}'")
            return 0

    def verify_preview_headers(self, expected_headers: list[Any] | None = None) -> bool:
        """Verify the import preview contains expected column headers.

        Args:
            expected_headers: List of expected header names. If None, uses default headers.

        Returns:
            True if all headers found, False otherwise
        """
        if expected_headers is None:
            expected_headers = [
                "Symbol",
                "Description",
                "Acquisition Date",
                "Shares",
                "Cost",
                "Price",
            ]

        logger.info(f"Verifying preview headers: {expected_headers}")

        header_row = self.import_preview_table.locator("thead tr")
        header_text = header_row.inner_text()

        all_found = True
        for header in expected_headers:
            if header.lower() in header_text.lower():
                logger.info(f"Header '{header}' found")
            else:
                logger.warning(f"Header '{header}' NOT found")
                all_found = False

        return all_found

    def get_preview_data(self) -> list:
        """Extract all visible rows from the import preview.

        Returns:
            List of dictionaries with row data
        """
        logger.info("Extracting preview data")

        rows = []
        for i in range(self.import_preview_rows.count()):
            row = self.import_preview_rows.nth(i)
            cells = row.locator("td")
            row_data = [cells.nth(j).inner_text() for j in range(cells.count())]
            rows.append(row_data)

        logger.info(f"Extracted {len(rows)} preview rows")
        return rows

    def submit_import(self, timeout: int = 10000) -> None:
        """Submit the holdings import and wait for holdings to be added to the grid.

        Args:
            timeout: Wait timeout in ms
        """
        logger.info("Submitting holdings import")

        self.click(self.import_submit_button)

        # Wait for modal to close and grid to update
        self.wait_for_element(self.import_modal, state="hidden", timeout=timeout)

        # Wait for grid to display the imported holdings
        self.wait_for_element(
            self.step_holdings_panel.locator("[role='grid']"), state="visible", timeout=timeout
        )
        logger.info("Holdings imported and grid updated")

    def cancel_import(self) -> None:
        """Cancel the holdings import modal."""
        logger.info("Canceling holdings import")
        self.click(self.import_cancel_button)
        self.wait_for_element(self.import_modal, state="hidden")
