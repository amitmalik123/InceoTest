"""BAW Dashboard Step Definitions for BDD tests"""

from pytest_bdd import given, parsers, when

from pages.baw.baw_dashboard_page import BawDashboardPage
from pages.baw.shell_process_page import ShellProcessPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@given("User should login to BAW application and click on the dashboard")
def step_login_to_baw_dashboard(baw_dashboard_page: BawDashboardPage):
    """User is logged into BAW and on the dashboard.
    
    Note: Actual authentication is handled by the authenticated_page fixture.
    This step serves as a BDD precondition statement."""
    logger.info("User is authenticated and on BAW dashboard")
    # The baw_dashboard_page fixture ensures we're already logged in and on the dashboard
    # No additional action needed here


@when("User click on Open New Work Item button")
def step_click_open_new_workitem(baw_dashboard_page: BawDashboardPage, test_context):
    """Click Open New Work Item and store Shell Process page in test_context."""
    logger.info("Starting Open New WorkItem process")

    page = baw_dashboard_page.page
    pages_before = len(page.context.pages)

    baw_dashboard_page.click_open_new_workitem_button()
    logger.info("Open New Work Item button clicked successfully")

    # Wait for the new tab to open and load
    page.wait_for_timeout(3000)
    shell_page = page.context.pages[-1] if len(page.context.pages) > pages_before else page
    shell_page.wait_for_load_state("domcontentloaded", timeout=60000)

    test_context["shell_process_page"] = ShellProcessPage(shell_page)
    logger.info("Shell Process page stored in test context")


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


# ============================================================================
# IWR Extraction - dashboard navigation steps
# ============================================================================

@when("Click search button and fetch the B number from results")
def step_click_search_and_fetch_iwr_b_number(baw_dashboard_page: BawDashboardPage, test_context):
    b_number = baw_dashboard_page.fetch_b_number_from_search_results()
    test_context["iwr_b_number"] = b_number
    logger.info(f"Stored IWR B number: {b_number}", attach_to_allure=True)


@when("Click dashboard and enter the fetched B number in search bar")
def step_navigate_dashboard_and_search_iwr_b_number(baw_dashboard_page: BawDashboardPage, test_context):
    b_number = test_context.get("iwr_b_number", "")
    if not b_number:
        raise ValueError(
            "IWR B number not found in test context. "
            "Ensure 'Click search button and fetch the B number from results' ran first."
        )
    baw_dashboard_page.navigate_to_dashboard_and_search_b_number(b_number)


@when("Click the run icon")
def step_click_run_icon_for_iwr(baw_dashboard_page: BawDashboardPage, test_context):
    b_number = test_context.get("iwr_b_number", "")
    page = baw_dashboard_page.page

    # Snapshot existing pages BEFORE click so we can detect the new popup.
    pages_before = set(id(p) for p in page.context.pages)

    # Click the run icon (internally waits for BAW loading).
    baw_dashboard_page.click_run_icon(b_number)

    # Poll up to 30s for a new non-dashboard popup page to appear.
    shell_page = None
    for _ in range(30):
        for p in page.context.pages:
            if id(p) not in pages_before and p.url and "dashboards" not in p.url:
                shell_page = p
                break
        if shell_page:
            break
        page.wait_for_timeout(1000)

    if shell_page:
        try:
            shell_page.wait_for_load_state("domcontentloaded", timeout=60000)
        except Exception:
            pass
        logger.info(f"Shell popup detected: {shell_page.url}")
    else:
        # No popup opened — task loaded inline inside dashboard iframe.
        shell_page = page
        logger.info(f"No new tab opened, task is inline: {shell_page.url}")

    test_context["shell_process_page"] = ShellProcessPage(shell_page)
    logger.info(f"Clicked run icon for B# {b_number}, shell process page stored")

