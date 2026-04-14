from playwright.sync_api import expect
from pytest_bdd import parsers, then, when

from pages.base_smart_filter_page import BaseSmartFilterPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


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
    """Select a smart filter option on any page with smart filters"""
    logger.info(f"Selecting filter option: {filter_option}")
    smart_filter_page.wait_for_filter_panel()
    smart_filter_page.select_filter_by_text(filter_option)

    # Verify the filter was selected
    assert smart_filter_page.is_filter_selected(
        filter_option
    ), f"Filter '{filter_option}' was not selected"


@when("I remove the filter")
def remove_filter(smart_filter_page: BaseSmartFilterPage):
    """Remove all applied filters on any page with smart filters"""
    logger.info("Removing all filters")
    smart_filter_page.clear_all_filters()
