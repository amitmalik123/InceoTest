"""Transfer Attributes Step Definitions for BDD tests"""

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.baw.transfer_attributes_page import TransferAttributesPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _ctx(test_context) -> tuple[TransferAttributesPage, dict]:
    """Return (TransferAttributesPage, test_data) from test_context."""
    page_obj = test_context.get("transferAttributes")
    if not page_obj:
        raise ValueError("TransferAttributes page not initialized. Click 'Update Transfer Details' first.")
    return page_obj, test_context.get("test_data", {})


def _require(data: dict, key: str) -> str:
    """Get a required non-empty string value from test data."""
    value = str(data.get(key, "") or "").strip()
    if not value:
        raise ValueError(f"{key} not found in test data")
    return value


@then(parsers.parse('enter transfer details for work item "{work_item_type}" with "{allocation_unit}" allocation in destination'))
def enter_transfer_details(test_context, work_item_type: str, allocation_unit: str):
    page, data = _ctx(test_context)
    transfer_amount = str(data.get("TransferAmount", "123") or "123")
    page.enter_transfer_request(_require(data, "TransferRequest"), work_item_type, transfer_amount)
    if work_item_type in ("Transfer In Request", "Custodian Change Request"):
        page.enter_destination_accounts(work_item_type, allocation_unit)
        logger.info(f"Entering destination accounts with {allocation_unit} allocation")
    if work_item_type == "Full Transfer Out In Kind":
        page.enter_details_for_full_transfer_out_in_kind(_require(data, "TransferRequest"), work_item_type)
        logger.info(f"Executing {work_item_type} workflow")
    if work_item_type == "Partial Transfer Out In Kind":
        page.enter_details_for_partial_transfer_out_in_kind(_require(data, "TransferRequest"), work_item_type)
        logger.info(f"Executing {work_item_type} workflow")


@then(parsers.parse(
    'enter transfer details for work item "{work_item_type}" with "{allocation_unit}" '
    'allocation in destination without creating TOAR record'
))
def enter_transfer_details_no_toar(test_context, work_item_type: str, allocation_unit: str):
    """Same as the main transfer-details step, but skips the
    'Create TOAR Record' button and goes straight to Save & Close.
    Used by C95661 where TOAR creation is not desired."""
    page, data = _ctx(test_context)
    transfer_amount = str(data.get("TransferAmount", "123") or "123")
    page.enter_transfer_request(
        _require(data, "TransferRequest"),
        work_item_type,
        transfer_amount,
        transfer_type_override="Cash",
        contribution_code_label="DEP - Non Qualified",
        delivery_method="Mail",
    )
    if work_item_type in ("Transfer In Request", "Custodian Change Request"):
        page.enter_destination_accounts(
            work_item_type,
            allocation_unit,
            create_toar=False,
            skip_funding_account=True,
        )
        logger.info(
            f"Entering destination accounts with {allocation_unit} allocation "
            f"(TOAR creation skipped)"
        )
        # Refresh the shell page so it reflects the just-saved transfer state.
        shell_page = test_context.get("shell_process_page")
        if shell_page is not None:
            shell_page.click_save_refresh()
        else:
            logger.info("shell_process_page not in test_context; skipping Save & Refresh")
    else:
        raise ValueError(
            f"'without creating TOAR record' variant only supported for "
            f"Custodian Change Request / Transfer In Request, got: {work_item_type}"
        )
