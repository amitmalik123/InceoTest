"""Step definitions for the APro proposal Tax Management wizard step (step 4)."""

from pytest_bdd import then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I complete the Tax Management step")
@then("I complete the Tax Management step")
def _tax_management(proposal_page: AproProposalsPage):
    """Confirm we reached Tax Management (step 4) and click Next — placeholder step."""
    proposal_page.wait_for_tax_management_step()
    # validate GetHoldings API call on transition to Holdings step
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/GetHoldings" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"GetHoldings returned {resp_info.value.status}, expected 200"

    # Wait for network to idle before Holdings step renders
    proposal_page.page.wait_for_load_state("networkidle", timeout=5000)


@when("I check if TMS is eligible")
@then("I check if TMS is eligible")
def _check_tms_eligibility(proposal_page: AproProposalsPage):
    """Check if the proposal qualifies for Tax Management Services.

    This step verifies the TMS eligibility status without making a selection.
    Used to determine if the proposal flow includes TMS options.
    """
    logger.info("Checking TMS eligibility status")
    proposal_page.wait_for_tax_management_step()
    is_eligible = proposal_page.is_tms_eligible()
    logger.info(f"TMS eligibility: {is_eligible}")


@when("I include Tax Management Services")
@when("I select to include TMS")
def _include_tms(proposal_page: AproProposalsPage):
    """Select the 'Yes — Include TMS' option for Tax Management Services.

    This enables Tax Management Services for the proposal if eligible.
    May trigger additional form fields or page state changes in future versions.
    """
    logger.info("Including Tax Management Services")
    proposal_page.wait_for_tax_management_step()
    proposal_page.select_include_tms()
    logger.info("TMS inclusion selected; proceeding with next step")


@when("I exclude Tax Management Services")
@when("I select to exclude TMS")
def _exclude_tms(proposal_page: AproProposalsPage):
    """Select the 'No — Don't Include TMS' option for standard investment management.

    This excludes Tax Management Services and applies standard investment management.
    """
    logger.info("Excluding Tax Management Services")
    proposal_page.wait_for_tax_management_step()
    proposal_page.select_exclude_tms()
    logger.info("TMS exclusion selected; proceeding with next step")


@then("TMS should be eligible")
def _verify_tms_eligible(proposal_page: AproProposalsPage):
    """Verify that the proposal qualifies for Tax Management Services."""
    logger.info("Verifying TMS eligibility")
    proposal_page.wait_for_tax_management_step()
    is_eligible = proposal_page.is_tms_eligible()
    assert is_eligible, "Expected TMS to be eligible but it is not"
    logger.info("TMS eligibility verified")


@then("TMS should not be eligible")
def _verify_tms_ineligible(proposal_page: AproProposalsPage):
    """Verify that the proposal does not qualify for Tax Management Services."""
    logger.info("Verifying TMS ineligibility")
    proposal_page.wait_for_tax_management_step()
    is_eligible = proposal_page.is_tms_eligible()
    assert not is_eligible, "Expected TMS to be ineligible but it is eligible"
    logger.info("TMS ineligibility verified")
