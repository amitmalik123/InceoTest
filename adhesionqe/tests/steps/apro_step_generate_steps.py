"""Step definitions for the APro proposal Generate Report / Summary wizard step (step 7)."""

from playwright.sync_api import expect
from pytest_bdd import then, when

from pages import AproProposalsPage
from utils.proposal_pdf_validator import ProposalPDFValidator as PDFValidator
from utils.allure_logger import get_allure_logger
from utils.playwright_api_validator import PlaywrightResponseTracker

logger = get_allure_logger(__name__)


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
    # validate GetReportGeneratorModel API call when the PREVIEW modal opens
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/GetReportGeneratorModel" in r.url
    ) as resp_info:
        proposal_page.click_preview()
    assert (
        resp_info.value.status == 200
    ), f"GetReportGeneratorModel returned {resp_info.value.status}, expected 200"


@when("I complete the Generate Report step with all reports")
@then("I complete the Generate Report step with all reports")
def _generate_report(proposal_page: AproProposalsPage):
    """Generate report for both original and copied proposals.

    Both proposal types follow the same workflow:
    1. Select "All Reports" template
    2. Transfer all reports to selected list
    3. Click GENERATE PREVIEW
    4. Wait for the Preview/View Proposal button to appear
    """
    # Both proposal types select template and reports the same way
    proposal_page.select_template_name_by_text("All Reports")
    report_results = proposal_page.select_all_reports()
    proposal_page.last_selected_reports = report_results

    # Track GenerateReport API response before clicking
    generate_tracker = PlaywrightResponseTracker(proposal_page.page)
    generate_tracker.start_tracking("/Proposals/Editor/GenerateReport")

    # Click to trigger the API
    proposal_page.click_generate_preview()

    # Wait for the button to appear (signals GenerateReport completed)
    # The button appears after report generation completes (~120 seconds for full reports)
    logger.info("Waiting for report generation to complete (takes a few minutes)...")

    # Timeout: 5 min (300s) for generation + buffer for modal to render
    proposal_page.generate.preview_proposal_button.wait_for(state="visible", timeout=300000)
    logger.info("Report generation complete")

    # Now stop tracking and validate
    generate_tracker.stop_tracking()
    generate_tracker.validate_all_successful(api_name="GenerateReport")


@then("the proposal should be generated with all reports")
@when("the proposal should be generated with all reports")
def _verify_report_generated(proposal_page: AproProposalsPage):
    logger.info("Clicking preview button to download PDF...")
    pdf_path = proposal_page.click_preview_proposal_and_verify_tab()
    assert pdf_path is not None, "PDF was not saved from the preview tab"

    # Validate PDF content
    pdf = PDFValidator(pdf_path)

    # Validate page count by reading the last entry in the TOC.
    last_toc_page = pdf.get_last_toc_page_number()
    page_count = pdf.get_page_count()
    if last_toc_page is not None:
        assert (
            page_count >= last_toc_page
        ), f"PDF has {page_count} pages but TOC shows last section starting on page {last_toc_page}"
    else:
        # Fallback: at least 1 page per successfully selected report
        selected = getattr(proposal_page, "last_selected_reports", {})
        min_pages = max(sum(1 for v in selected.values() if v), 1)
        assert page_count >= min_pages, (
            f"Expected at least {min_pages} pages "
            f"({sum(1 for v in selected.values() if v)} reports selected), "
            f"got {page_count}"
        )

    full_text = pdf.extract_text()

    # Report titles that should appear at least twice (once in TOC, once as section header).
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

    # Composite Fact Sheet: TOC lists "Composite Fact Sheet"
    composite_toc_count = full_text.lower().count("composite fact sheet")
    assert composite_toc_count >= 1, "Expected 'Composite Fact Sheet' in TOC but not found in PDF"

    proposal_page.click_preview_proposal_close()
    proposal_page.click_preview_report_close()
    proposal_page.click_finish()


@then("the report proposal should be complete")
def step_report_complete(proposal_page: AproProposalsPage) -> None:
    # basic assertion that proposal pieces exist on the page
    expect(proposal_page.page.get_by_text("Proposal Summary")).to_be_visible()
