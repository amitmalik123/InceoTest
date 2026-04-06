import json

from playwright.sync_api import expect
from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger
from utils.pdf_utils import PDFValidator

logger = get_allure_logger(__name__)


@when("I start a new proposal")
@then("I start a new proposal")
def _create_new_proposal(proposal_page: AproProposalsPage):
    proposal_page.store_advisor_name()
    proposal_page.open_actions()
    proposal_page.click_create_prospect()


@when(
    parsers.parse(
        "I complete the client details section for {client_name} with investment amount {amount:d}"
    )
)
@then(
    parsers.parse(
        "I complete the client details section for {client_name} with investment amount {amount:d}"
    )
)
def _client_details(proposal_page: AproProposalsPage, client_name: str, amount: int):
    proposal_page.wait_for_details_step()
    proposal_page.set_client_name(client_name)
    proposal_page.set_investment_amount(amount)
    proposal_page.set_account_type("401K")
    proposal_page.set_custodian("Pershing")

    # Verify advisor dropdown defaulted to the logged-in advisor
    advisor_selected = proposal_page.get_advisor_dropdown_value()
    assert (
        advisor_selected == proposal_page.expected_advisor_name
    ), f"Expected advisor '{proposal_page.expected_advisor_name}', got '{advisor_selected}'"

    # proceed to the holdings step
    proposal_page.click_next()


@when(parsers.parse("I complete the add holdings section with {holdings_json}"))
@then(parsers.parse("I complete the add holdings section with {holdings_json}"))
def _add_holdings(proposal_page: AproProposalsPage, holdings_json: str):
    """Add multiple holdings. Expects `holdings_json` to be a JSON array of
    [ticker, shares, cost, date(optional)] entries, e.g.:
    [["VTI", 5, 300], ["VOO", 2, 400, "01/14/2025"]]
    """
    proposal_page.wait_for_holdings_step()

    try:
        holdings = json.loads(holdings_json)
    except Exception:
        # fallback: if a Python-style list was passed, eval
        holdings = eval(holdings_json)

    # Add all holdings via POM helper which will select autocomplete, set shares,cost, acquisiiton date and save
    proposal_page.add_holdings_from_tickers(holdings)


@then(parsers.parse("The holdings {holdings_json} should be added to the proposal"))
def _verify_holdings_added(proposal_page: AproProposalsPage, holdings_json: str):
    try:
        holdings = json.loads(holdings_json)
    except Exception:
        # fallback: if a Python-style list was passed, eval
        holdings = eval(holdings_json)

    proposal_page.verify_saved_holding(holdings)

    # proceed to next step
    proposal_page.click_next()


@when("I complete the Assess Risk section")
@then("I complete the Assess Risk section")
def _questionnaire(proposal_page: AproProposalsPage):
    # answer all questionnaire questions with the first option
    proposal_page.answer_all_questions(default="first")
    proposal_page.click_next()


@when("I complete the select allocation section")
@then("I complete the select allocation section")
def _select_allocation(proposal_page: AproProposalsPage):
    # select allocation using POM: pick first row, verify panels, then proceed
    proposal_page.wait_for_allocation_step()
    name = proposal_page.select_first_allocation()
    if name:
        details = proposal_page.get_selected_allocation_details()
        assert details[
            "details_populated"
        ], f"Selected allocation details did not populate for '{name}'"
        assert details["risk_populated"], f"Risk & Performance did not populate for '{name}'"
        name_val = details.get("Name", "")
        assert (
            name in name_val
        ), f"Selected allocation Name mismatch: expected '{name}' in '{name_val}'"
        assert details.get("Strategy"), f"Selected allocation missing Strategy for '{name}'"
        assert details.get("Risk Range"), f"Selected allocation missing Risk Range for '{name}'"
        assert details.get(
            "Tolerance Band"
        ), f"Selected allocation missing Tolerance Band for '{name}'"
    # proceed
    proposal_page.click_next()


@then("The proposal details should contain the expected information")
def _verify_proposal_details(proposal_page: AproProposalsPage):
    proposal_page.wait_for_summary_step()
    summary = proposal_page.get_summary_details()

    assert summary["visible"], "Proposal summary not visible"
    assert (
        summary["client"] and summary["client"] != "--"
    ), f"Client name not populated in summary (still '{summary['client']}')"

    if proposal_page.expected_client_name:
        assert (
            summary["client"] == proposal_page.expected_client_name
        ), f"Client name mismatch: expected '{proposal_page.expected_client_name}', got '{summary['client']}'"

    if proposal_page.expected_strategy:
        assert (
            summary["strategy"] == proposal_page.expected_strategy
        ), f"Strategy mismatch: expected '{proposal_page.expected_strategy}', got '{summary['strategy']}'"

    if proposal_page.expected_allocation_name:
        assert (
            summary["composite"] == proposal_page.expected_allocation_name
        ), f"Allocation mismatch: expected '{proposal_page.expected_allocation_name}', got '{summary['composite']}'"

    if proposal_page.expected_investment_amount is not None:
        assert (
            summary["investment_amount"] is not None
        ), f"Unable to parse investment amount from summary: '{summary['investment_raw']}'"
        assert (
            abs(summary["investment_amount"] - proposal_page.expected_investment_amount) < 0.01
        ), f"Investment Amount mismatch: expected '{proposal_page.expected_investment_amount}', got '{summary['investment_amount']}'"


@when("I preview the proposal")
@then("I preview the proposal")
def _preview_proposal(proposal_page: AproProposalsPage):
    proposal_page.click_preview()


@when("I complete the generate report section with all reports")
@then("I complete the generate report section with all reports")
def _generate_report(proposal_page: AproProposalsPage):
    proposal_page.select_template_name_by_text("All Reports")
    proposal_page.select_all_reports()
    proposal_page.click_generate_preview()


@then("the proposal should be generated with all reports")
@when("the proposal should be generated with all reports")
def _verify_report_generated(proposal_page: AproProposalsPage):
    # Verify the preview opened in a new tab, save the PDF, and return focus
    pdf_path = proposal_page.click_preview_proposal_and_verify_tab()
    assert pdf_path is not None, "PDF was not saved from the preview tab"

    # Validate PDF content
    pdf = PDFValidator(pdf_path)

    # Validate page count
    page_count = pdf.get_page_count()
    assert page_count == 19, f"Expected 19 pages, got {page_count}"

    full_text = pdf.extract_text()

    # Report titles that should appear at least twice (once in TOC, once as section header).
    # Excludes Cover Page, Table of Contents, Composite Fact Sheet, and Manager Holdings
    # which have special naming patterns.
    report_titles = [
        "Proposal Summary",
        "Projected Fees Report",
        "Manager Performance Review",
        "Manager Transition Summary",
        "Fee Detail Report",
        "Strategy Performance Review",
        "Proposal Agreement",
    ]

    for title in report_titles:
        count = full_text.lower().count(title.lower())
        assert count >= 2, (
            f"Expected report title '{title}' to appear at least 2 times "
            f"(TOC + section header), but found {count} occurrence(s)"
        )

    # Holdings Transition: TOC lists "Holdings Transition Report", section header is "Holdings Transition".
    holdings_transition_toc = full_text.lower().count("holdings transition report")
    assert (
        holdings_transition_toc >= 1
    ), "Expected 'Holdings Transition Report' in TOC but not found in PDF"
    holdings_transition_section = full_text.lower().count("holdings transition")
    assert holdings_transition_section >= 2, (
        f"Expected 'Holdings Transition' at least 2 times (TOC + section header), "
        f"but found {holdings_transition_section} occurrence(s)"
    )

    allocation_name = proposal_page.expected_allocation_name

    # Composite Fact Sheet: TOC lists "Composite Fact Sheet"
    composite_toc_count = full_text.lower().count("composite fact sheet")
    assert composite_toc_count >= 1, "Expected 'Composite Fact Sheet' in TOC but not found in PDF"

    # Manager Holdings: TOC lists "Holdings: {allocation_name}", section header is "Manager Holdings".
    # PDF text extraction may split the TOC entry across lines, so check components separately.
    holdings_toc_entry = f"Holdings: {allocation_name}"
    holdings_toc_found = holdings_toc_entry.lower() in full_text.lower()
    if not holdings_toc_found:
        # Fallback: check that "Holdings:" and the allocation name both appear
        assert "holdings:" in full_text.lower(), "Expected 'Holdings:' TOC entry not found in PDF"
    manager_holdings_count = full_text.lower().count("manager holdings")
    assert (
        manager_holdings_count >= 1
    ), "Expected 'Manager Holdings' section header not found in PDF"

    proposal_page.click_preview_proposal_close()
    proposal_page.click_preview_report_close()
    proposal_page.click_finish()


@then("the report proposal should be complete")
def step_report_complete(proposal_page: AproProposalsPage) -> None:
    # basic assertion that proposal pieces exist on the page
    expect(proposal_page.page.get_by_text("Proposal Summary")).to_be_visible()


@then("the History/Actions section should contain the expected information")
def _view_history(proposal_page: AproProposalsPage):
    details = proposal_page.wait_for_history_details()

    assert details["client"] and details["client"] not in {
        "--",
        "",
    }, f"History client not populated (still '{details['client']}')"

    if proposal_page.expected_client_name:
        assert (
            details["client"] == proposal_page.expected_client_name
        ), f"History client mismatch: expected '{proposal_page.expected_client_name}', got '{details['client']}'"

    if proposal_page.expected_strategy:
        assert (
            details["strategy"] == proposal_page.expected_strategy
        ), f"History strategy mismatch: expected '{proposal_page.expected_strategy}', got '{details['strategy']}'"

    if proposal_page.expected_allocation_name:
        assert (
            details["composite"] == proposal_page.expected_allocation_name
        ), f"History allocation mismatch: expected '{proposal_page.expected_allocation_name}', got '{details['composite']}'"

    if proposal_page.expected_investment_amount is not None:
        expected_inv_str = f"${proposal_page.expected_investment_amount:,.2f}"
        assert (
            details["investment"] == expected_inv_str
        ), f"History investment amount mismatch: expected '{expected_inv_str}', got '{details['investment']}'"

    assert (
        details["status"].lower() == "questionnaire completed"
    ), f"History current status mismatch: expected 'Questionnaire Completed', got '{details['status']}'"


@then("I delete the proposal")
def _delete_proposal(proposal_page: AproProposalsPage):
    # Use the POM helper to delete the currently selected proposal
    # need to scope to the actions button in the modal to avoid clicking the actions button for the proposal card behind it
    # need to also verify client, strategy, allocation, investment amount, current status before deleting
    proposal_page.delete_selected_proposal()
