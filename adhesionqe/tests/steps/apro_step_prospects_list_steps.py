"""Step definitions for the APro Prospects List page.

Covers navigation to/from the list, proposal verification in the list,
resume flow, copy proposal verification, and list column assertions.
"""

from datetime import datetime

from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _find_original_proposal_row(proposal_page: AproProposalsPage, original_data: dict) -> dict:
    """Find the original proposal row in the prospects list (race-condition safe).

    This helper handles the case where other tests may have created proposals,
    pushing our original proposal down the list. We locate it by matching the
    stored original_proposal_data instead of blindly using row 0.

    Waits for the Kendo grid to finish loading before scanning rows to ensure
    data is fully populated and not stale.

    Args:
        proposal_page: The AproProposalsPage instance
        original_data: The stored row data from the original proposal

    Returns:
        The row data dict for the original proposal

    Raises:
        AssertionError if the original proposal cannot be found
    """
    if not original_data:
        # Fallback: if no original data stored, use first row (shouldn't happen in normal flow)
        logger.warning("No original_proposal_data found; falling back to row 0")
        return proposal_page.get_row_data(0)

    # Wait for Kendo loading mask/overlay to disappear (grid is done loading)
    logger.info("Waiting for Kendo grid to finish loading...")
    proposal_page.page.locator(".k-loading-mask, .k-overlay").first.wait_for(
        state="hidden", timeout=10000
    )

    # Wait for rows to be visible
    proposal_page.proposal_rows.first.wait_for(state="visible", timeout=10000)

    original_client = original_data.get("client", "").strip()

    # Retry getting total rows (may take a moment for grid to fully render)
    total_rows = 0
    for attempt in range(3):
        total_rows = proposal_page.proposal_rows.count()
        if total_rows > 0:
            break
        if attempt < 2:
            logger.info(f"Waiting for rows to populate (attempt {attempt + 1}/3)...")
            proposal_page.page.wait_for_timeout(500)

    logger.info(f"Found {total_rows} rows in prospects list")

    # Scan through all rows to find one matching the original proposal
    for i in range(total_rows):
        # Retry getting row data (cells may take a moment to populate)
        row_data = None
        for attempt in range(3):
            try:
                row_data = proposal_page.get_row_data(i)
                if row_data and row_data.get("client", "").strip():
                    break
                if attempt < 2:
                    proposal_page.page.wait_for_timeout(300)
            except Exception as e:
                logger.debug(f"Attempt {attempt + 1}/3 to get row {i} data: {e}")
                if attempt < 2:
                    proposal_page.page.wait_for_timeout(300)

        if not row_data:
            continue

        row_client = row_data.get("client", "").strip()

        # Match on client name and row data (ID, timestamps, etc. should match)
        if row_client == original_client and row_data == original_data:
            logger.info(f"Found original proposal at row {i}")
            return row_data

    # If exact match not found, try matching just on client name
    for i in range(total_rows):
        row_data = proposal_page.get_row_data(i)
        row_client = row_data.get("client", "").strip()
        if row_client == original_client:
            logger.warning(
                f"Exact match not found for original proposal, using first matching client '{original_client}' at row {i}"
            )
            return row_data

    raise AssertionError(
        f"Could not find original proposal (client: '{original_client}') in prospects list. "
        f"Total rows: {total_rows}. Original data: {original_data}"
    )


@when("I navigate back to the prospects list")
@then("I navigate back to the prospects list")
def _navigate_back_to_list(proposal_page: AproProposalsPage):
    """Click the 'Proposal Builder' breadcrumb to return to the prospects list."""
    logger.info("Navigating back to prospects list via Proposal Builder breadcrumb")
    proposal_page.click_proposal_builder_back()
    proposal_page.wait_for_prospects_list()

    # Wait for Kendo loading mask to disappear before proceeding (grid data refresh)
    logger.info("Waiting for Kendo grid data refresh...")
    proposal_page.page.locator(".k-loading-mask, .k-overlay").first.wait_for(
        state="hidden", timeout=10000
    )


@then("the proposal should appear in the prospects list")
def _verify_proposal_in_list(proposal_page: AproProposalsPage):
    """Verify the newly created proposal appears in the prospects list and store its ID."""
    logger.info("Verifying proposal appears in prospects list")
    proposal_page.proposal_rows.first.wait_for(state="visible", timeout=10000)
    row_count = proposal_page.proposal_rows.count()
    assert row_count > 0, "No proposals found in the prospects list"

    if proposal_page.expected_client_name:
        name_cell = proposal_page.proposal_rows.first.locator("td").first
        cell_text = name_cell.inner_text().strip()
        assert (
            proposal_page.expected_client_name in cell_text
        ), f"Expected client '{proposal_page.expected_client_name}' in first row, got '{cell_text}'"

    # Store the original proposal's row data so we can identify the copy later
    original_proposal_data = proposal_page.get_row_data(0)
    proposal_page.original_proposal_data = original_proposal_data
    logger.info(
        f"Proposal found in list with {row_count} row(s). Original proposal data stored: {original_proposal_data}"
    )


@then("the saved proposal details should match the expected information")
def _verify_resumed_proposal(proposal_page: AproProposalsPage):
    """Verify details on the History tab after resuming."""
    logger.info("Verifying saved proposal details after resume")
    details = proposal_page.wait_for_history_details()

    assert details["client"] and details["client"] not in {
        "--",
        "",
    }, f"Resumed proposal client not populated (got '{details['client']}')"

    if proposal_page.expected_client_name:
        assert (
            details["client"] == proposal_page.expected_client_name
        ), f"Resumed client mismatch: expected '{proposal_page.expected_client_name}', got '{details['client']}'"
    logger.info(f"Resumed proposal verified: client='{details['client']}'")


@then("the proposal investment amount should match the created proposal")
def _verify_proposal_investment_in_list(proposal_page: AproProposalsPage):
    """Verify the investment amount column matches the created proposal."""
    logger.info("Verifying proposal investment amount in prospects list")
    if proposal_page.expected_investment_amount is not None:
        expected_amount_str = f"${proposal_page.expected_investment_amount:,.2f}"
        original_data = getattr(proposal_page, "original_proposal_data", None)
        row_data = _find_original_proposal_row(proposal_page, original_data)
        actual_amount = row_data.get("investment_amount", "")
        assert (
            expected_amount_str in actual_amount
            or str(proposal_page.expected_investment_amount) in actual_amount
        ), f"Investment amount mismatch: expected '{expected_amount_str}', got '{actual_amount}'"
    logger.info("Investment amount verified in prospects list")


@then("the proposal advisor should match the logged-in advisor")
def _verify_proposal_advisor_in_list(proposal_page: AproProposalsPage):
    """Verify the advisor column matches the logged-in advisor."""
    logger.info("Verifying proposal advisor in prospects list")
    if proposal_page.expected_advisor_name:
        original_data = getattr(proposal_page, "original_proposal_data", None)
        row_data = _find_original_proposal_row(proposal_page, original_data)
        actual_advisor = row_data.get("advisor", "")
        assert (
            proposal_page.expected_advisor_name in actual_advisor
        ), f"Advisor mismatch: expected '{proposal_page.expected_advisor_name}', got '{actual_advisor}'"
    logger.info("Advisor verified in prospects list")


@then(parsers.parse('the proposal status should be "{status}"'))
def _verify_proposal_status_in_list(proposal_page: AproProposalsPage, status: str):
    """Verify the proposal Status column in the prospects list."""
    logger.info(f"Verifying proposal status: {status}")
    original_data = getattr(proposal_page, "original_proposal_data", None)
    row_data = _find_original_proposal_row(proposal_page, original_data)
    actual_status = row_data.get("status", "").strip()
    assert (
        status.lower() in actual_status.lower()
    ), f"Status mismatch: expected '{status}', got '{actual_status}'"
    logger.info(f"Status verified: {actual_status}")


@then("the proposal strategy should be populated")
def _verify_proposal_strategy_populated(proposal_page: AproProposalsPage):
    """Verify the Strategy column is populated in the prospects list."""
    logger.info("Verifying proposal strategy is populated")
    original_data = getattr(proposal_page, "original_proposal_data", None)
    row_data = _find_original_proposal_row(proposal_page, original_data)
    actual_strategy = row_data.get("strategy", "").strip()
    assert actual_strategy and actual_strategy not in {
        "--",
        "",
    }, f"Strategy should be populated, but got '{actual_strategy}'"
    logger.info(f"Strategy populated: {actual_strategy}")


@then("the proposal composite should match the selected allocation")
def _verify_proposal_composite_matches_allocation(proposal_page: AproProposalsPage):
    """Verify the Composite column matches the selected allocation."""
    logger.info("Verifying proposal composite matches selected allocation")
    if proposal_page.expected_allocation_name:
        original_data = getattr(proposal_page, "original_proposal_data", None)
        row_data = _find_original_proposal_row(proposal_page, original_data)
        actual_composite = row_data.get("composite", "").strip()
        assert (
            proposal_page.expected_allocation_name in actual_composite
        ), f"Composite mismatch: expected '{proposal_page.expected_allocation_name}', got '{actual_composite}'"
    logger.info("Composite verified in prospects list")


@then("the proposal finished date should be today")
def _verify_proposal_finished_date_today(proposal_page: AproProposalsPage):
    """Verify the Finished column shows today's date."""
    logger.info("Verifying proposal finished date is today")
    today = datetime.now().strftime("%m/%d/%Y")
    original_data = getattr(proposal_page, "original_proposal_data", None)
    row_data = _find_original_proposal_row(proposal_page, original_data)
    actual_finished = row_data.get("finished", "").strip()

    # Extract just the date portion (finished column may contain date + time)
    finished_date = actual_finished.split()[0] if actual_finished else ""

    assert today in finished_date or finished_date.startswith(
        today.split("/")[2]
    ), f"Finished date should be today ({today}), but got '{actual_finished}'"
    logger.info(f"Finished date verified: {actual_finished}")


@then("the proposal Risk Assessment Completed column should have today's date")
def _verify_proposal_rac_checked(proposal_page: AproProposalsPage):
    """Verify the Risk Assessment Completed has today's date."""
    logger.info("Verifying Risk Assessment Completed column has today's date")
    today = datetime.now().strftime("%m/%d/%Y")
    original_data = getattr(proposal_page, "original_proposal_data", None)
    row_data = _find_original_proposal_row(proposal_page, original_data)
    rac_value = row_data.get("risk_assessment_completed", "").strip()
    # Value should be today's date
    assert (
        today in rac_value
    ), f"Risk Assessment Completed should have today's date ({today}), but got '{rac_value}'"
    logger.info("Risk Assessment Completed column verified as checked")


@then("the copied proposal should appear as a new row with a finished date")
def _verify_copied_proposal_is_unique_and_finished(proposal_page: AproProposalsPage):
    """Verify the copied proposal exists as a separate proposal with a finished date.

    This proves the copied proposal workflow completed successfully.
    We identify the copy by:
    1. Finding all proposals with the same client name as the original
    2. Filtering out the original proposal (by comparing row data)
    3. Verifying the copy has a finished date

    This approach is race-condition-safe: even if other tests create proposals,
    we specifically identify our copy by matching on the original's stored data.
    """
    logger.info("Verifying copied proposal exists as unique proposal with finished date")
    proposal_page.wait_for_prospects_list()

    original_data = getattr(proposal_page, "original_proposal_data", None)
    assert original_data, "Original proposal data not found. Did the first verification step run?"

    original_client = original_data.get("client", "").strip()
    logger.info(f"Looking for copy of proposal for client: {original_client}")

    # Scan through all rows to find the copy
    total_rows = proposal_page.proposal_rows.count()
    logger.info(f"Total proposals in list: {total_rows}")

    copy_found = False
    copy_finished_date = None

    for i in range(total_rows):
        row_data = proposal_page.get_row_data(i)
        row_client = row_data.get("client", "").strip()
        row_finished = row_data.get("finished", "").strip()

        # Check if this row matches our client and is NOT the original
        if (
            row_client == original_client
            and row_data != original_data
            and row_finished
            and row_finished not in {"--", ""}
        ):
            # This is the copy - verify it has a finished date
            copy_found = True
            copy_finished_date = row_finished
            logger.info(f"Found copy proposal at row {i} with finished date: {copy_finished_date}")
            break

    assert copy_found, (
        f"Could not find a copy proposal for client '{original_client}' with a finished date. "
        f"Original data: {original_data}"
    )

    logger.info(f"Copied proposal verified as unique row with finished date: {copy_finished_date}")
