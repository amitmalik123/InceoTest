from playwright.sync_api import Page, expect
from pytest_bdd import parsers, then, when

from pages import AproProposalsPage, GlobalNavigationPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

# Mapping of step names to their 0-indexed positions in the proposal wizard
WIZARD_STEP_MAP = {
    "Details": 0,
    "Assess Risk": 1,
    "Allocation": 2,
    "Tax Management": 3,
    "Holdings": 4,
    "Fees": 5,
    "Generate Proposal": 6,
    "History": 7,
    "History / Actions": 7,
}


@when("I navigate to the APro prospects page")
def navigate_to_apro_prospects(authenticated_page: Page):
    """Navigate to the APro prospects page via global navigation (constructs page object locally)."""
    gnav = GlobalNavigationPage(authenticated_page)
    gnav.click_menu_trigger()
    gnav.click_proposals_apro()


@then("I should see the APro prospects page")
def verify_apro_prospects_page(authenticated_page: Page):
    """Verify that the APro prospects page is displayed"""
    expect(authenticated_page.get_by_text("Prospects List")).to_be_visible()


@when('I search for client "{client_id}"')
def search_for_client(authenticated_page: Page, client_id: str):
    """Search for a client by client ID using the global search."""
    gnav = GlobalNavigationPage(authenticated_page)
    gnav.search(client_id)


@when(parsers.parse("I navigate to the {step_name} step"))
@then(parsers.parse("I navigate to the {step_name} step"))
def navigate_to_wizard_step(proposal_page: AproProposalsPage, step_name: str):
    """Navigate to any proposal wizard step by name.

    Supported step names:
    - Details
    - Assess Risk
    - Allocation
    - Tax Management
    - Holdings
    - Fees
    - Generate Proposal
    - History / Actions

    Args:
        step_name: Name of the step to navigate to
    """
    step_index = WIZARD_STEP_MAP.get(step_name)
    if step_index is None:
        raise ValueError(
            f"Unknown step name: '{step_name}'. "
            f"Supported steps: {', '.join(WIZARD_STEP_MAP.keys())}"
        )

    logger.info(f"Navigating to {step_name} step (index {step_index})")
    proposal_page.click_step(step_index)

    # Wait for the step to load based on the step type
    step_wait_methods = {
        0: lambda: proposal_page.wait_for_details_step(),
        1: lambda: proposal_page.wait_for_risk_step(),
        2: lambda: proposal_page.wait_for_allocation_step(),
        4: lambda: proposal_page.wait_for_holdings_step(),
        7: lambda: proposal_page.wait_for_history_step(),
    }

    if step_index in step_wait_methods:
        step_wait_methods[step_index]()
    else:
        proposal_page.page.wait_for_load_state("networkidle", timeout=10000)

    logger.info(f"Reached {step_name} step")


@when("I refresh the page")
def refresh_page(authenticated_page: Page):
    """Refresh the current page."""
    logger.info("Refreshing the page")
    authenticated_page.reload()
    authenticated_page.wait_for_load_state("networkidle", timeout=10000)


@when(parsers.parse("I resume the {proposal_identifier} proposal from the prospects list"))
def resume_proposal_from_list(proposal_page: AproProposalsPage, proposal_identifier: str):
    """Resume any proposal from the prospects list by identifier.

    Supports finding by:
    - Proposal name: 'original proposal', 'copied proposal'
    - Row index: 'first', 'second', or numeric

    Args:
        proposal_page: The AproProposalsPage instance
        proposal_identifier: Which proposal to resume ('original proposal', 'copied proposal', etc.)
    """
    logger.info(f"Resuming proposal: {proposal_identifier}")
    original_data = getattr(proposal_page, "original_proposal_data", None)
    row_index = proposal_page.find_proposal_row(
        proposal_identifier, original_proposal_data=original_data
    )
    proposal_page.resume_proposal_from_row(row_index)
    logger.info(f"Resumed proposal from row {row_index}")
