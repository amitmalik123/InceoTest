from pytest_bdd import parsers, then, when

from pages import AproProposalsPage, GlobalNavigationPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('I search for client "{search_query}"'))
def search_for_client(global_navigation_page: GlobalNavigationPage, search_query: str):
    """Search for a client using the global search bar."""
    logger.info(f"Searching for client: {search_query}")
    global_navigation_page.click_menu_trigger()
    global_navigation_page.search(search_query)
    global_navigation_page.global_search_results.wait_for(state="visible", timeout=10000)
    global_navigation_page.global_search_accounts_results.first.hover()


@then("the Actions list loads")
def verify_actions_list_loads(global_navigation_page: GlobalNavigationPage):
    """Verify that the Actions list appears after search."""
    logger.info("Verifying Actions list loads")
    try:
        global_navigation_page.action_menu_items.wait_for(state="visible", timeout=10000)
        logger.info("Actions list is visible")
    except Exception as exc:
        raise AssertionError(f"Actions list did not load: {exc}")


@when("I select the Create/Edit Proposal action")
def select_create_proposal_action(global_navigation_page: GlobalNavigationPage):
    """Click the Create/Edit Proposal action."""
    logger.info("Selecting Create/Edit Proposal action")
    global_navigation_page.action_menu_items.wait_for(state="visible", timeout=5000)
    global_navigation_page.click_create_proposal()


@then("I should be taken to the Proposal page")
def verify_proposal_page(proposal_page: AproProposalsPage):
    """Verify that the Proposal page is displayed."""
    logger.info("Verifying Proposal page is displayed")
    try:
        # TODO move selectors to POM
        # Click the Proposals(new) tab
        proposal_page.page.locator("div#proposals-new-tab").click()
        logger.info("Clicked Proposals(new) tab")

        # Wait for a row in the kgrid (prospectGrid) within accounts-page-contents
        kgrid_row = proposal_page.page.locator(
            "div#accounts-page-contents tbody.k-table-tbody tr.k-table-row"
        )
        kgrid_row.first.wait_for(state="visible", timeout=15000)

        # # Get and log the inner text of the row
        # row_text = kgrid_row.first.inner_text()
        # logger.info(f"Proposal row found with content: {row_text}")

        logger.info("Proposal page loaded successfully - Proposals(new) tab verified")
    except Exception as exc:
        raise AssertionError(f"Proposal page did not load: {exc}")
