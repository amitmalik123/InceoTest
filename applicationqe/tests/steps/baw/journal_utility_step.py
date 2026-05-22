"""JournalUtilityPage Step Definitions for BDD tests"""

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.baw.create_oa_page import JournalUtilityPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _ctx(test_context) -> tuple["JournalUtilityPage", dict]:
    """Return (JournalUtilityPage, test_data) from test_context."""
    page_obj = test_context.get("journal_utility_page")
    if not page_obj:
        raise ValueError("JournalUtilityPage not initialized. ")
    return page_obj, test_context.get("test_data", {})


def _require(data: dict, key: str) -> str:
    """Get a required non-empty string value from test data."""
    value = str(data.get(key, "") or "").strip()
    if not value:
        raise ValueError(f"{key} not found in test data")
    return value

@when("User add a journal")
def user_add_a_journal(test_context):
    page, _ = _ctx(test_context)
    page._select_different_destination_account(test_context["shell_custodian_acc"])
    page.selectUnit()
    page.clickAddJournalButton()

@then("Validate Added Journal")
def validate_added_journal(test_context):
    page, _ = _ctx(test_context)
    page.validateAddedJournal()

@when("Click on save and close button on journalUtilityPage page")
def click_on_save_and_close_button(test_context):
    page, _ = _ctx(test_context)
    page.clickSaveCloseButton()
    # Switch back to Create OA page after Journal tab closes
    create_oa_page = test_context.get("create_oa_page")
    if create_oa_page:
        create_oa_page.page.bring_to_front()
        create_oa_page.page.wait_for_load_state("load", timeout=30000)