from playwright.sync_api import expect
from pytest_bdd import parsers, then, when

from pages.Adhesion.base_smart_filter_page import BaseSmartFilterPage
from pages.Adhesion.prospects_list_page import ProspectsListPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

# Store baseline row count in scenario context
baseline_row_count = {}


@then("I should see the smart filter options")
def verify_smart_filter_options(smart_filter_page: BaseSmartFilterPage):
    """Verify that smart filter options are visible on any page with smart filters"""
    logger.info("Verifying smart filter options are visible")
    smart_filter_page.wait_for_filter_panel()

    # Verify filter panel is visible
    expect(smart_filter_page.filter_panel).to_be_visible()

    # Verify there are filter checkboxes available
    checkbox_count = smart_filter_page.filter_checkboxes.count()
    assert checkbox_count > 0, "No filter checkboxes found in filter panel"
    logger.info(f"Found {checkbox_count} filter options")


@when(parsers.parse('I select the "{filter_option}" filter'))
def select_filter_option(smart_filter_page: BaseSmartFilterPage, filter_option: str):
    """Select a smart filter option and validate the grid refresh API returns 200"""
    logger.info(f"Selecting filter option: {filter_option}")
    smart_filter_page.wait_for_filter_panel()

    with smart_filter_page.page.expect_response(lambda r: "AJAXRead" in r.url) as response_info:
        smart_filter_page.select_filter_by_text(filter_option)

    ajax_status = response_info.value.status
    logger.info(f"Filter AJAXRead response status: {ajax_status}")
    assert ajax_status == 200, f"Filter AJAXRead returned {ajax_status}, expected 200"

    # Verify the filter was selected
    assert smart_filter_page.is_filter_selected(
        filter_option
    ), f"Filter '{filter_option}' was not selected"


@when("I remove the filter")
def remove_filter(smart_filter_page: BaseSmartFilterPage):
    """Remove all applied filters and validate the grid refresh API returns 200"""
    logger.info("Removing all filters")

    with smart_filter_page.page.expect_response(lambda r: "AJAXRead" in r.url) as response_info:
        smart_filter_page.clear_all_filters()

    ajax_status = response_info.value.status
    logger.info(f"Remove filter AJAXRead response status: {ajax_status}")
    assert ajax_status == 200, f"Remove filter AJAXRead returned {ajax_status}, expected 200"


@then("I capture the baseline row count")
def capture_baseline_row_count(prospects_list_page: ProspectsListPage):
    """Capture the current row count as baseline for later comparison (per spec §3.5).

    This step should be executed before applying any filters to establish a baseline
    count that will be used to verify the grid returns to at least this count after
    filters are removed.
    """
    logger.info("Capturing baseline row count")
    prospects_list_page.wait_for_filter_panel()
    row_count = prospects_list_page.get_row_count()
    baseline_row_count["count"] = row_count
    logger.info(f"Baseline row count: {row_count}")


@then(parsers.parse('the "{filter_option}" filter checkbox should be checked'))
def verify_filter_checkbox_checked(smart_filter_page: BaseSmartFilterPage, filter_option: str):
    """Verify that a specific filter option checkbox is checked (per spec §3.5 gap).

    This assertion ensures the UI correctly reflects that the filter is active.
    """
    logger.info(f"Verifying filter '{filter_option}' checkbox is checked")
    is_checked = smart_filter_page.is_filter_selected(filter_option)
    assert is_checked, f"Filter '{filter_option}' checkbox is not checked after selection"
    logger.info(f"Filter '{filter_option}' is correctly checked")


@then(parsers.parse('the "{filter_option}" filter checkbox should be unchecked'))
def verify_filter_checkbox_unchecked(smart_filter_page: BaseSmartFilterPage, filter_option: str):
    """Verify that a specific filter option checkbox is unchecked (per spec §3.5 gap).

    This assertion ensures the UI correctly reflects that the filter has been removed.
    """
    logger.info(f"Verifying filter '{filter_option}' checkbox is unchecked")
    is_checked = smart_filter_page.is_filter_selected(filter_option)
    assert not is_checked, f"Filter '{filter_option}' checkbox is still checked after removal"
    logger.info(f"Filter '{filter_option}' is correctly unchecked")


@then("the prospects list row count should be at least the baseline count")
def verify_row_count_restored(prospects_list_page: ProspectsListPage):
    """Verify that after filters are cleared, the row count is at least the baseline.

    This assertion validates that the grid has returned to showing the full unfiltered
    dataset (or close to it), confirming that the filter removal worked correctly.
    Per spec §3.5: "Grid returns to baseline after clear"
    """
    logger.info("Verifying prospects list row count is at least the baseline")
    prospects_list_page.wait_for_filter_panel()
    current_row_count = prospects_list_page.get_row_count()
    stored_baseline = baseline_row_count.get("count", 0)

    assert (
        current_row_count >= stored_baseline
    ), f"Row count {current_row_count} is less than baseline {stored_baseline}"
    logger.info(f"Row count verified: current={current_row_count}, baseline={stored_baseline}")
