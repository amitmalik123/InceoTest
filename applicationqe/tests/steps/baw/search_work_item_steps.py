"""Search Work Item Step Definitions for BDD tests"""

from pytest_bdd import when

from pages.baw.search_work_item_page import SearchWorkItemPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when("Enter external id and click on search button")
def step_enter_external_id_and_click_search(search_work_item_page: SearchWorkItemPage, test_context):
    """Enter external ID (B number) in search field and click search."""
    b_number = test_context.get("b_number", "").strip()

    logger.info("Attempting to search for work item with external ID")

    if not b_number:
        logger.error("B number not found in test context")
        raise ValueError(
            "B number not found in test context. Ensure 'Fetch b number from shell process page' step executed successfully."
        )

    logger.info(f"Using B number for search: {b_number}")
    search_work_item_page.enter_external_id_and_click_search(b_number)
    logger.info(f"Successfully searched for work item with B number: {b_number}")


@when("Fetch parent b number")
def step_fetch_parent_b_number(search_work_item_page: SearchWorkItemPage, test_context):
    """Fetch parent B number from search results and store as data in test_context."""
    logger.info("Attempting to fetch parent B number from search results")
 
    parent_b_number = search_work_item_page.fetch_parent_b_number()
 
    test_context["parent_b_number"] = parent_b_number
    test_context["b_tracking_id"] = parent_b_number
    Assertions.assert_is_not_none(parent_b_number, "Parent B number fetched from search results")
    logger.info(f"Parent B Number: {parent_b_number}")
    b_number = test_context.get("b_number", "")
    logger.attach_summary_table({
        "Username": test_context.get("test_data", {}).get("UserName") or test_context.get("test_data", {}).get("username", ""),
        "Client Full Name": test_context.get("client_full_name", ""),
        "Child B Number": b_number,
        "Parent B Number": parent_b_number,
    }, name="B Number Summary")
 


