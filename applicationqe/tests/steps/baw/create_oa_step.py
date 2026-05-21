"""createOA Step Definitions for BDD tests"""

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.baw.create_oa_page import CreateOAPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _ctx(test_context) -> tuple[CreateOAPage, dict]:
    """Return (CreateOAPage, test_data) from test_context."""
    page_obj = test_context.get("create_oa_page")
    if not page_obj:
        raise ValueError("CreateOAPage not initialized. Run 'click on Update OA button' step first.")
    return page_obj, test_context.get("test_data", {})


@when("cancel already created journal")
def cancel_added_journal(test_context):
    page, _ = _ctx(test_context)
    page.clickCancelLink()

@when(parsers.parse('Select action type "{Journal}"'))
def select_action_type(test_context, Journal: str):
    page, _ = _ctx(test_context)
    journalUtilityPage = page.selectActionType(Journal)
    test_context["journal_utility_page"] = journalUtilityPage

@when("Click on save and close button on createOAPage page")
def click_on_save_and_close_button(test_context):
    page, _ = _ctx(test_context)
    page.clickSaveCloseButton()