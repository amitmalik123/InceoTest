"""Step definitions for the APro proposal Allocation wizard step (step 3)."""

from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger
from utils.playwright_api_validator import PlaywrightResponseTracker

logger = get_allure_logger(__name__)


@when(parsers.parse("I complete the Allocation step with {allocation_name}"))
@then(parsers.parse("I complete the Allocation step with {allocation_name}"))
def _select_allocation(proposal_page: AproProposalsPage, allocation_name: str):
    """Complete the Allocation step by selecting an allocation.

    Args:
        allocation_name: Allocation name or partial name (e.g., "Brandes International ADR")
    """
    proposal_page.wait_for_allocation_step()

    # Track allocation-related API calls BEFORE selecting
    validate_tracker = PlaywrightResponseTracker(proposal_page.page)
    validate_tracker.start_tracking("/Proposals/Editor/ValidateCompositeSelection")

    save_tracker = PlaywrightResponseTracker(proposal_page.page)
    save_tracker.start_tracking("/Proposals/Editor/SaveAllocationSelection")

    pie_tracker = PlaywrightResponseTracker(proposal_page.page)
    pie_tracker.start_tracking("/Allocations/Summary/AllocationPieChartData")

    risk_tracker = PlaywrightResponseTracker(proposal_page.page)
    risk_tracker.start_tracking("/ProposalReports/RiskRewardChart_Read")

    perf_tracker = PlaywrightResponseTracker(proposal_page.page)
    perf_tracker.start_tracking("/ProposalReports/PerformanceGrid_Read")

    # Select allocation by name (triggers all the above API calls)
    name = proposal_page.select_allocation_by_partial_name(allocation_name)
    logger.info(f"Selected allocation: {name}")

    # Wait for all API responses including lazy-loaded chart data
    proposal_page.page.wait_for_load_state("networkidle", timeout=10000)
    proposal_page.page.wait_for_timeout(
        5000
    )  # Brief wait for lazy-loaded chart APIs after networkidle

    # Stop tracking and validate all API calls
    validate_tracker.stop_tracking()
    assert validate_tracker.responses, "ValidateCompositeSelection API call was not triggered"
    validate_tracker.validate_all_successful(api_name="ValidateCompositeSelection")

    save_tracker.stop_tracking()
    assert save_tracker.responses, "SaveAllocationSelection API call was not triggered"
    save_tracker.validate_all_successful(api_name="SaveAllocationSelection")

    pie_tracker.stop_tracking()
    assert pie_tracker.responses, "AllocationPieChartData API call was not triggered"
    pie_tracker.validate_all_successful(api_name="AllocationPieChartData")

    risk_tracker.stop_tracking()
    assert risk_tracker.responses, "RiskRewardChart_Read API call was not triggered"
    risk_tracker.validate_all_successful(api_name="RiskRewardChart_Read")
    # Proceed to next step
    proposal_page.click_next()


@when(parsers.parse("I select the allocation {allocation_name}"))
@when(parsers.parse("I select {allocation_name} allocation"))
def _select_allocation_by_name(proposal_page: AproProposalsPage, allocation_name: str):
    """Select a specific allocation by name (supports partial matching).

    Args:
        allocation_name: Allocation name or partial name (e.g., "Blackrock 10-90 Target")
    """
    logger.info(f"Selecting allocation by name: {allocation_name}")
    proposal_page.wait_for_allocation_step()

    validate_tracker = PlaywrightResponseTracker(proposal_page.page)
    validate_tracker.start_tracking("/Proposals/Editor/ValidateCompositeSelection")

    save_tracker = PlaywrightResponseTracker(proposal_page.page)
    save_tracker.start_tracking("/Proposals/Editor/SaveAllocationSelection")

    pie_tracker = PlaywrightResponseTracker(proposal_page.page)
    pie_tracker.start_tracking("/Allocations/Summary/AllocationPieChartData")

    risk_tracker = PlaywrightResponseTracker(proposal_page.page)
    risk_tracker.start_tracking("/ProposalReports/RiskRewardChart_Read")

    perf_tracker = PlaywrightResponseTracker(proposal_page.page)
    perf_tracker.start_tracking("/ProposalReports/PerformanceGrid_Read")

    # Select allocation by partial name match
    selected_name = proposal_page.select_allocation_by_partial_name(allocation_name)
    logger.info(f"Selected allocation: {selected_name}")

    # Wait for all API responses including lazy-loaded chart data
    proposal_page.page.wait_for_load_state("networkidle", timeout=10000)
    proposal_page.page.wait_for_timeout(
        5000
    )  # Brief wait for lazy-loaded chart APIs after networkidle

    # Stop tracking and validate all API calls
    validate_tracker.stop_tracking()
    assert validate_tracker.responses, "ValidateCompositeSelection API call was not triggered"
    validate_tracker.validate_all_successful(api_name="ValidateCompositeSelection")

    save_tracker.stop_tracking()
    assert save_tracker.responses, "SaveAllocationSelection API call was not triggered"
    save_tracker.validate_all_successful(api_name="SaveAllocationSelection")

    pie_tracker.stop_tracking()
    assert pie_tracker.responses, "AllocationPieChartData API call was not triggered"
    pie_tracker.validate_all_successful(api_name="AllocationPieChartData")

    risk_tracker.stop_tracking()
    assert risk_tracker.responses, "RiskRewardChart_Read API call was not triggered"
    risk_tracker.validate_all_successful(api_name="RiskRewardChart_Read")

    perf_tracker.stop_tracking()
    assert perf_tracker.responses, "PerformanceGrid_Read API call was not triggered"
    perf_tracker.validate_all_successful(api_name="PerformanceGrid_Read")

    # Proceed to next step
    proposal_page.click_next()


@then("the TMS column should be visible in the allocation grid")
@when("the TMS column should be visible in the allocation grid")
def _verify_tms_column_visible(proposal_page: AproProposalsPage):
    """Verify that the TMS column is visible in the allocation grid.

    If TMS column is visible, it means the account is TMS-eligible.
    """
    logger.info("Verifying TMS column is visible in allocation grid")
    proposal_page.wait_for_allocation_step()

    is_visible = proposal_page.is_tms_column_visible()
    assert is_visible, "TMS column is not visible - account is TMS-ineligible"
    logger.info("✓ TMS column is visible - account is TMS-eligible")


@then("the TMS column should not be visible in the allocation grid")
@when("the TMS column should not be visible in the allocation grid")
def _verify_tms_column_not_visible(proposal_page: AproProposalsPage):
    """Verify that the TMS column is NOT visible in the allocation grid.

    If TMS column is not visible, the account is TMS-ineligible and
    will skip the Tax Management step.
    """
    logger.info("Verifying TMS column is NOT visible in allocation grid")
    proposal_page.wait_for_allocation_step()

    is_visible = proposal_page.is_tms_column_visible()
    assert not is_visible, "TMS column is visible - account should be TMS-ineligible"
    logger.info("✓ TMS column is not visible - account is TMS-ineligible")


@then(parsers.parse("the selected allocation should be TMS-eligible"))
@when(parsers.parse("the selected allocation should be TMS-eligible"))
def _verify_allocation_tms_eligible(proposal_page: AproProposalsPage):
    """Verify that the currently selected allocation is TMS-eligible.

    Only meaningful if the TMS column is visible.
    """
    logger.info("Verifying selected allocation is TMS-eligible")
    proposal_page.wait_for_allocation_step()

    is_eligible = proposal_page.is_allocation_tms_eligible()
    assert is_eligible, "Selected allocation is not TMS-eligible (no TMS icon found)"
    logger.info("✓ Selected allocation is TMS-eligible")


@then(parsers.parse("the allocation '{allocation_name}' should be TMS-eligible"))
@when(parsers.parse("the allocation '{allocation_name}' should be TMS-eligible"))
def _verify_named_allocation_tms_eligible(proposal_page: AproProposalsPage, allocation_name: str):
    """Verify that a named allocation is TMS-eligible.

    Args:
        allocation_name: Allocation name or partial name to check (e.g., "Blackrock 10-90")
    """
    logger.info(f"Verifying allocation '{allocation_name}' is TMS-eligible")
    proposal_page.wait_for_allocation_step()

    is_eligible = proposal_page.is_allocation_tms_eligible(allocation_name=allocation_name)
    assert is_eligible, f"Allocation '{allocation_name}' is not TMS-eligible (no TMS icon found)"
    logger.info(f"✓ Allocation '{allocation_name}' is TMS-eligible")


@then(parsers.parse("the selected allocation should be TMS-ineligible"))
@when(parsers.parse("the selected allocation should be TMS-ineligible"))
def _verify_allocation_tms_ineligible(proposal_page: AproProposalsPage):
    """Verify that the currently selected allocation is TMS-ineligible.

    Only meaningful if the TMS column is visible.
    """
    logger.info("Verifying selected allocation is TMS-ineligible")
    proposal_page.wait_for_allocation_step()

    is_eligible = proposal_page.is_allocation_tms_eligible()
    assert not is_eligible, "Selected allocation is TMS-eligible (TMS icon found)"
    logger.info("✓ Selected allocation is TMS-ineligible")


@then(parsers.parse("the allocation '{allocation_name}' should be TMS-ineligible"))
@when(parsers.parse("the allocation '{allocation_name}' should be TMS-ineligible"))
def _verify_named_allocation_tms_ineligible(proposal_page: AproProposalsPage, allocation_name: str):
    """Verify that a named allocation is TMS-ineligible.

    Args:
        allocation_name: Allocation name or partial name to check (e.g., "Blackrock 10-90")
    """
    logger.info(f"Verifying allocation '{allocation_name}' is TMS-ineligible")
    proposal_page.wait_for_allocation_step()

    is_eligible = proposal_page.is_allocation_tms_eligible(allocation_name=allocation_name)
    assert not is_eligible, f"Allocation '{allocation_name}' is TMS-eligible (TMS icon found)"
    logger.info(f"✓ Allocation '{allocation_name}' is TMS-ineligible")
