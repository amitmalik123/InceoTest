"""BAW Dashboard Step Definitions for BDD tests"""

from pytest_bdd import parsers, when

from pages.baw.baw_dashboard_page import BawDashboardPage
from pages.baw.naa_coach_page import NAACoachPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("User click on Open New Work Item button")
def step_click_open_new_workitem(baw_dashboard_page: BawDashboardPage):
    """Click Open New Work Item button on BAW dashboard."""
    logger.info("Starting Open New WorkItem process")
    
    # Capture parent dashboard page reference before opening Shell Process window
    # baw_dashboard_window = baw_dashboard_page.page
    # logger.info(f"Captured parent dashboard page: {baw_dashboard_window.url if baw_dashboard_window else 'None'}")
    
    baw_dashboard_page.click_open_new_workitem_button()
    logger.info("Open New Work Item button clicked successfully")


@when(parsers.parse('Click on "{tab_name}" tab'))
def step_click_on_tab(baw_dashboard_page: BawDashboardPage, tab_name: str):
    """Click on a dashboard menu tab like 'Search Work Item', 'Bulk Reassign', etc."""
    logger.info(f"Attempting to click on tab: {tab_name}")
    baw_dashboard_page.click_tab(tab_name)
    logger.info(f"Successfully clicked on {tab_name} tab")


@when(parsers.parse('User search via B tracking number "{option}"'))
def step_user_search_via_b_tracking_number(
    baw_dashboard_page: BawDashboardPage, test_context, option: str
):
    """Search for B tracking number using provided option."""
    logger.info(f"Starting B tracking number search with option: {option}")

    b_number_to_search = None

    if option == "viaeWM":
        b_number_to_search = test_context.get("b_tracking_id")
        if not b_number_to_search:
            b_number_to_search = test_context.get("parent_b_number")
            if b_number_to_search:
                logger.info(f"Using parent_b_number as fallback: {b_number_to_search}")
        if b_number_to_search:
            logger.info(f"Search for b number: {b_number_to_search}")
    elif option == "directBAW":
        b_number_to_search = test_context.get("b_number")
        if b_number_to_search:
            logger.info(f"Search for b number: {b_number_to_search}")
    else:
        logger.info("user is doing b number search")

    if not b_number_to_search:
        error_msg = f"Required B number not found in test context for option: {option}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    baw_dashboard_page.enter_b_number_to_search(b_number_to_search)
    logger.info(f"B tracking number search completed for: {b_number_to_search}")


@when("User click on run icon")
def step_user_click_run_icon(
    baw_dashboard_page: BawDashboardPage,
    test_context,
):
    """Click run icon for the selected B tracking row without switching tabs."""
    selected_tracking_id = test_context.get("parent_b_number") or test_context.get("b_tracking_id")
    baw_dashboard_page.click_run_icon(selected_tracking_id)
    logger.info("Clicked run icon")


@when(parsers.parse('User click on run icon and switch to "{page_title}" page'))
def step_user_click_run_icon_and_switch_page(
    baw_dashboard_page: BawDashboardPage,
    naa_coach_page: NAACoachPage,
    test_context,
    page_title: str,
):
    """Click the BAW run icon and switch to the requested follow-up page."""
    selected_tracking_id = test_context.get("parent_b_number") or test_context.get("b_tracking_id")
    baw_dashboard_page.click_run_icon(selected_tracking_id)

    if page_title.strip().lower() == "naa coach":
        naa_coach_page.switch_to_naa_coach_page()
    else:
        naa_coach_page.switch_to_page_by_title(page_title, timeout=30)

    logger.info(f"Clicked run icon and switched to {page_title}")
