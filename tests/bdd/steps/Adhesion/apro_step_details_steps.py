"""Step definitions for the APro proposal Details wizard step (step 1)."""

from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from pages.Adhesion.prospects_list_page import ProspectsListPage
from utils.allure_logger import get_allure_logger
from utils.playwright_api_validator import PlaywrightResponseTracker

logger = get_allure_logger(__name__)


@when("I start a new proposal")
@then("I start a new proposal")
def _create_new_proposal(prospects_list_page: ProspectsListPage, proposal_page: AproProposalsPage):
    # Get advisor name before opening modal
    advisor_name = prospects_list_page.get_advisor_name()

    # Start tracking AccountsAvailableToLink before modal opens
    accounts_tracker = PlaywrightResponseTracker(proposal_page.page)
    accounts_tracker.start_tracking("/Proposals/Editor/AccountsAvailableToLink")

    # Open and click to create proposal
    prospects_list_page.open_actions()
    prospects_list_page.click_create_prospect()

    # Wait for proposal modal to be visible and all network calls to complete
    proposal_page.page.locator("#proposal-wizard-0").wait_for(state="visible", timeout=10000)
    proposal_page.page.wait_for_load_state("networkidle", timeout=5000)

    # Store tracker and advisor name in proposal_page
    proposal_page.expected_advisor_name = advisor_name
    proposal_page.accounts_tracker = accounts_tracker


@when(
    parsers.parse("I complete the Details step for {client_name} with investment amount {amount:d}")
)
@then(
    parsers.parse("I complete the Details step for {client_name} with investment amount {amount:d}")
)
def _client_details(proposal_page: AproProposalsPage, client_name: str, amount: int):
    proposal_page.wait_for_details_step()

    # Stop tracking responses that started when modal opened
    accounts_tracker = proposal_page.accounts_tracker
    accounts_tracker.stop_tracking()

    # Validate AccountsAvailableToLink calls succeeded
    accounts_tracker.validate_all_successful(api_name="AccountsAvailableToLink")

    proposal_page.set_client_name(client_name)
    proposal_page.set_investment_amount(amount)
    proposal_page.set_account_type("401K")
    proposal_page.set_custodian("Pershing")

    # Verify advisor dropdown defaulted to the logged-in advisor
    advisor_selected = proposal_page.get_advisor_dropdown_value()
    assert (
        advisor_selected == proposal_page.expected_advisor_name
    ), f"Expected advisor '{proposal_page.expected_advisor_name}', got '{advisor_selected}'"

    # proceed to the Assess Risk step — validate SaveDetails API call
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/SaveDetails" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"SaveDetails returned {resp_info.value.status}, expected 200"


@then("the proposal Details step should open for the copied proposal")
def _verify_copy_details_step_opened(proposal_page: AproProposalsPage):
    """Verify the copied proposal opens at the Details step."""
    logger.info("Verifying copy proposal Details step opened")
    proposal_page.wait_for_details_step(timeout=10000)
    logger.info("Copy proposal Details step confirmed visible")


@then("the copy proposal modal should show the Details step")
def _verify_copy_modal_step(proposal_page: AproProposalsPage):
    """Verify the copy proposal modal is showing the Details step."""
    logger.info("Verifying copy proposal modal is at Details step")
    proposal_page.wait_for_details_step(timeout=10000)
    logger.info("Copy proposal Details step verified")


@when("I proceed from the populated Details step")
def _proceed_from_copy_details(proposal_page: AproProposalsPage):
    """Click Next to proceed from the copy proposal Details step (which is pre-populated)."""
    logger.info("Proceeding from copy proposal Details step (already populated)")
    proposal_page.wait_for_details_step(timeout=10000)
    # Click Next to move to Assess Risk step
    proposal_page.click_next()
    logger.info("Details step skipped; moving to Assess Risk step")
