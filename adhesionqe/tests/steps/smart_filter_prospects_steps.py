"""Smart filter steps specific to the Prospects List page."""

from playwright.sync_api import expect
from pytest_bdd import then

from pages.prospects_list_page import ProspectsListPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("The prospects list should be filtered accordingly")
def verify_prospects_filtered(prospects_list_page: ProspectsListPage):
    """Verify that the prospects list has been filtered"""
    logger.info("Verifying prospects list is filtered")

    # Verify at least one filter is active
    active_count = prospects_list_page.get_active_filter_count()
    assert active_count > 0, "Expected at least one active filter but found none"
    logger.info(f"Verified {active_count} active filter(s)")

    # Verify the prospects grid is visible (assumes it will update after filtering)
    prospects_grid = prospects_list_page.page.locator("#prospectGrid")
    expect(prospects_grid).to_be_visible()


@then("The prospects list should be unfiltered")
def verify_prospects_unfiltered(prospects_list_page: ProspectsListPage):
    """Verify that the prospects list is unfiltered"""
    logger.info("Verifying prospects list is unfiltered")

    # Verify no filters are active
    active_count = prospects_list_page.get_active_filter_count()
    assert active_count == 0, f"Expected 0 active filters but found {active_count}"
    logger.info("Verified all filters cleared")

    # Verify the prospects grid is still visible
    prospects_grid = prospects_list_page.page.locator("#prospectGrid")
    expect(prospects_grid).to_be_visible()
