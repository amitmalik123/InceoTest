"""Step definitions for the APro proposal History/Actions wizard step (step 8).

Also covers copy proposal actions initiated from the History tab.
"""

from pytest_bdd import then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("the History/Actions step should contain the expected information")
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
        details["status"].lower() == "risk assessment completed"
    ), f"History current status mismatch: expected 'Risk Assessment Completed', got '{details['status']}'"


@when("I navigate to the History step via the top step navigator")
def _navigate_to_history_step(proposal_page: AproProposalsPage):
    """Click the History step in the top step navigator."""
    logger.info("Navigating to History step via top navigator")
    proposal_page.click_step(7)  # Step 7 is History/Actions (0-indexed)
    proposal_page.wait_for_history_step(timeout=10000)


@when("I click the Copy Proposal action")
def _click_copy_proposal(proposal_page: AproProposalsPage):
    """Click the Copy Proposal action in the History step."""
    logger.info("Clicking Copy Proposal action")
    # Validate CopyProposal API call on confirmation
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/CopyProposal" in r.url
    ) as resp_info:
        proposal_page.click_copy_proposal()
        proposal_page.accept_copy_proposal_confirmation()
    assert (
        resp_info.value.status == 200
    ), f"CopyProposal returned {resp_info.value.status}, expected 200"
    proposal_page.page.wait_for_load_state("networkidle", timeout=5000)


@then("I delete the proposal")
def _delete_proposal(proposal_page: AproProposalsPage):
    # validate DeleteProposal API call on confirmation
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/DeleteProposal" in r.url
    ) as resp_info:
        proposal_page.delete_selected_proposal()
    assert (
        resp_info.value.status == 200
    ), f"DeleteProposal returned {resp_info.value.status}, expected 200"
