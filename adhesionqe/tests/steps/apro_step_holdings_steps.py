"""Step definitions for the APro proposal Holdings wizard step (step 5).

Covers both manual holdings entry and the import modal workflow.
Also covers holding editing (symbol, cost, tax lot save) and the incomplete
tax lot acknowledgement modal.
"""

import csv
import json
import os

from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger
from utils.playwright_api_validator import PlaywrightResponseTracker

logger = get_allure_logger(__name__)


# ============ Manual Holdings Entry ============


@when(parsers.parse("I complete the Holdings step with {holdings_json}"))
@then(parsers.parse("I complete the Holdings step with {holdings_json}"))
def _add_holdings(proposal_page: AproProposalsPage, holdings_json: str):
    """Add multiple holdings. Expects `holdings_json` to be a JSON array of
    [ticker, shares, cost, date(optional)] entries, e.g.:
    [["VTI", 5, 300], ["VOO", 2, 400, "01/14/2025"]]
    """
    proposal_page.wait_for_holdings_step(timeout=15000)

    try:
        holdings = json.loads(holdings_json)
    except Exception:
        # fallback: if a Python-style list was passed, eval
        holdings = eval(holdings_json)

    # Track ALL SearchSymbols and GetSymbolDetails responses across all holdings
    search_tracker = PlaywrightResponseTracker(proposal_page.page)
    details_tracker = PlaywrightResponseTracker(proposal_page.page)

    search_tracker.start_tracking("/Proposals/Editor/SearchSymbols")
    details_tracker.start_tracking("/Proposals/Editor/GetSymbolDetails")

    # Add all holdings via POM helper
    if holdings:
        for holding in holdings:
            proposal_page.add_holding(holding)

    search_tracker.stop_tracking()
    details_tracker.stop_tracking()

    # Validate all calls succeeded
    search_tracker.validate_count(len(holdings), api_name="SearchSymbols")
    details_tracker.validate_count(len(holdings), api_name="GetSymbolDetails")

    logger.info("Holdings added successfully")


@then(parsers.parse("The holdings {holdings_json} should be added to the proposal"))
def _verify_holdings_added(proposal_page: AproProposalsPage, holdings_json: str):
    try:
        holdings = json.loads(holdings_json)
    except Exception:
        # fallback: if a Python-style list was passed, eval
        holdings = eval(holdings_json)

    missing = proposal_page.verify_saved_holding(holdings)
    assert not missing, f"Holdings verification failed; missing entries: {missing}"

    logger.info("Holdings verified successfully")


@when("I click Next from the Holdings step")
def _click_next_from_holdings(proposal_page: AproProposalsPage):
    """Click Next to move from Holdings to the next step."""
    logger.info("Clicking Next from Holdings step to proceed")
    proposal_page.click_next()
    proposal_page.page.wait_for_load_state("networkidle", timeout=5000)


# ============ Holding Editing ============


@when("I select the first imported holding row")
def _select_first_holding(proposal_page: AproProposalsPage):
    """Click the first imported holding row in the grid to load it for editing."""
    logger.info("Selecting first imported holding row")
    proposal_page.select_holding_row(0)


@when("I select the first holding row")
def _select_first_holding_row(proposal_page: AproProposalsPage):
    """Click the first holding row in the grid to load its data into edit fields."""
    logger.info("Selecting first holding row")
    proposal_page.select_holding_row(0)
    logger.info("First holding row selected; edit fields populated")


@when(parsers.parse("I update the holding cost to {cost}"))
def _update_holding_cost(proposal_page: AproProposalsPage, cost: str):
    """Update the holding cost field."""
    logger.info(f"Updating holding cost to: {cost}")
    proposal_page.edit_holding_field("cost", cost)


@when(parsers.parse("I update the holding symbol to {symbol}"))
def _edit_holding_symbol(proposal_page: AproProposalsPage, symbol: str):
    """Update the holding symbol in the edit fields below the grid."""
    # Strip quotes if present
    symbol = symbol.strip('"')
    logger.info(f"Updating holding symbol to {symbol}")

    # Track GetSymbolDetails API call during symbol update
    details_tracker = PlaywrightResponseTracker(proposal_page.page)
    details_tracker.start_tracking("/Proposals/Editor/GetSymbolDetails")

    proposal_page.edit_holding_field("symbol", symbol)

    details_tracker.stop_tracking()
    details_tracker.validate_count(1, api_name="GetSymbolDetails")

    logger.info(f"Holding symbol updated to {symbol} with API validation")


@when("I save the tax lot")
@then("I save the tax lot")
def _save_holding_tax_lot(proposal_page: AproProposalsPage):
    """Click save/update tax lot button."""
    logger.info("Saving tax lot")
    proposal_page.save_holding_tax_lot()
    logger.info("Tax lot saved; grid row updated")


@then(parsers.parse("the holding cost should display {cost} in the grid"))
def _verify_holding_cost_updated(proposal_page: AproProposalsPage, cost: str):
    """Verify the holding cost is updated in the grid."""
    logger.info(f"Verifying holding cost updated to: {cost}")
    actual_cost = proposal_page.get_holding_field_value(0, "cost")
    assert cost in actual_cost, f"Cost mismatch: expected '{cost}', got '{actual_cost}'"
    logger.info("Holding cost verified")


@then(parsers.parse("the holding symbol should display {symbol} in the grid"))
def _verify_holding_symbol_updated(proposal_page: AproProposalsPage, symbol: str):
    """Verify the updated holding symbol is reflected in the grid."""
    # Strip quotes if present
    symbol = symbol.strip('"')
    logger.info(f"Verifying holding symbol {symbol} displays in grid")

    # Wait briefly for grid to update
    proposal_page.page.wait_for_timeout(500)

    # Use same validation as verify_saved_holding - check if symbol appears in grid text
    holdings_text = proposal_page.step_holdings_panel.inner_text()
    assert (
        symbol.upper() in holdings_text.upper()
    ), f"Expected holding symbol {symbol} not found in grid"
    logger.info(f"Holding symbol verified: {symbol}")


@when("I acknowledge the incomplete tax lot data modal")
def _acknowledge_incomplete_tax_lot_modal(proposal_page: AproProposalsPage):
    """Check the 'Proceed with incomplete data' checkbox and close the modal."""
    logger.info("Acknowledging incomplete tax lot data modal")

    # Find and check the checkbox using its ID
    checkbox = proposal_page.page.locator("#chkProceedIncompleteData")
    checkbox.wait_for(state="visible", timeout=5000)
    logger.info("Checkbox is visible")

    # Use Playwright's check() method which properly sets the checkbox state
    checkbox.check()
    logger.info("Checkbox checked")

    # Wait a moment for validation to register
    proposal_page.page.wait_for_timeout(500)

    # Click the Close button (the one in the modal footer, not the header)
    close_btn = proposal_page.page.locator('button:has-text("Close")').last()
    close_btn.wait_for(state="visible", timeout=3000)
    close_btn.click()
    logger.info("Close button clicked")

    # Wait for modal to disappear
    proposal_page.page.wait_for_timeout(1000)
    logger.info("Incomplete tax lot data modal closed successfully")
    proposal_page.click_next()  # Proceed to next step after acknowledging


# ============ Holdings Import Modal ============


@when("I open the holdings import modal")
@then("I open the holdings import modal")
def _open_holdings_import_modal(proposal_page: AproProposalsPage):
    """Open the holdings import modal."""
    proposal_page.open_import_modal()


@when("I download the holdings template")
@then("I download the holdings template")
def _download_holdings_template(proposal_page: AproProposalsPage):
    """Download the holdings template and store the path for later verification."""
    template_path = proposal_page.download_template()

    # Store the path for verification steps
    proposal_page.downloaded_template_path = template_path
    logger.info(f"Template downloaded to: {template_path}")


@then(parsers.parse("the template file should be named {filename_pattern}"))
def _verify_template_filename(proposal_page: AproProposalsPage, filename_pattern: str):
    """Verify the downloaded template has the expected filename.

    Constructs the exact filename with today's date in YYYYMMDD format.

    Args:
        filename_pattern: Not used (kept for compatibility), filename is constructed from today's date
    """
    from datetime import datetime

    template_path = getattr(proposal_page, "downloaded_template_path", None)
    assert template_path, "No template path found - download step may not have run"

    filename = os.path.basename(template_path)

    # Construct expected filename with today's date
    today = datetime.now().strftime("%Y%m%d")
    expected_filename = f"Holdings_Template_{today}.csv"

    assert (
        filename == expected_filename
    ), f"Template filename '{filename}' does not match expected '{expected_filename}'"
    logger.info(f"Template filename verified: {filename}")


@then("the template should contain the expected column headers")
def _verify_template_headers(proposal_page: AproProposalsPage):
    """Verify the downloaded template CSV contains the expected headers."""
    template_path = getattr(proposal_page, "downloaded_template_path", None)
    assert template_path, "No template path found"

    expected_headers = ["Symbol", "Description", "Acquisition Date", "Shares", "Cost", "Price"]

    with open(template_path, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)

    assert (
        headers == expected_headers
    ), f"Template headers {headers} do not match expected {expected_headers}"
    logger.info(f"Template headers verified: {headers}")


@when("I upload a holdings import file with sample data")
def _upload_holdings_import_file(proposal_page: AproProposalsPage):
    """Upload a sample holdings CSV file for import."""
    # Use the happy path holdings import file (6 holdings with preview cutoff behavior)
    test_file = "data/holdings/happy_path_import.csv"

    assert os.path.exists(test_file), f"Test data file not found: {test_file}"

    proposal_page.upload_import_file(test_file)
    proposal_page.uploaded_file_path = test_file
    logger.info(f"Holdings import file uploaded: {test_file}")


@then("the import preview should display the holdings accurately")
def _verify_preview_content(proposal_page: AproProposalsPage):
    """Verify the import preview displays holdings with correct data."""
    preview_data = proposal_page.get_preview_data()

    assert len(preview_data) > 0, "No rows found in import preview"

    # Verify each row has expected number of columns (6: Symbol, Description, Date, Shares, Cost, Price)
    for i, row in enumerate(preview_data):
        assert len(row) == 6, f"Row {i} has {len(row)} columns, expected 6. Data: {row}"

        # Verify Symbol (first column) is not empty
        assert row[0].strip(), f"Row {i} has empty Symbol"

    logger.info(f"Preview content verified: {len(preview_data)} rows with valid data")


@then("the preview should show correct row count")
def _verify_preview_row_count(proposal_page: AproProposalsPage):
    """Verify the preview row count matches expected behavior.

    The preview shows up to 4 rows, while the holdings indicator shows the total count.
    """
    preview_count = proposal_page.get_preview_row_count()
    total_count = proposal_page.get_total_holdings_count()

    # Preview should show <= 4 rows
    assert preview_count <= 4, f"Preview shows {preview_count} rows, expected max 4"

    # Total count should be >= preview count
    assert (
        total_count >= preview_count
    ), f"Total count {total_count} should be >= preview count {preview_count}"

    logger.info(f"Row count verified: preview={preview_count}, total={total_count}")


@when("I submit the import")
@then("I submit the import")
def _submit_holdings_import(proposal_page: AproProposalsPage):
    """Submit the holdings import."""
    proposal_page.submit_import()


@then("the imported holdings should appear in the holdings grid")
def _verify_imported_holdings_in_grid(proposal_page: AproProposalsPage):
    """Verify the imported holdings now appear in the main holdings grid.

    Note: Grid may be paginated, so we check if at least some holdings are present.
    """
    # Get the grid text
    grid_text = proposal_page.step_holdings_panel.inner_text()
    logger.info(f"Grid content (first 500 chars): {grid_text[:500]}")

    # Should contain at least some of the symbols from our happy_path_import.csv file
    expected_symbols = ["MSFT", "TSLA", "META", "AMZN", "IBM", "GE"]

    found_symbols = []
    for symbol in expected_symbols:
        if symbol.upper() in grid_text.upper():
            found_symbols.append(symbol)

    # Just verify at least ONE symbol is found (grid might be paginated)
    assert (
        len(found_symbols) >= 1
    ), f"Expected at least 1 of {expected_symbols} found in holdings grid, but found none. Grid text: {grid_text[:1000]}"

    logger.info(f"Imported holdings verified in grid: {found_symbols}")
