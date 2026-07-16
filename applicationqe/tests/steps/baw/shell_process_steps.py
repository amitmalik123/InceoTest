"""Shell Process Step Definitions for BDD tests"""

import allure
from pytest_bdd import parsers, then, when

from pages.baw.create_oa_page import CreateOAPage
from locators.baw.shell_process_locators import ShellProcessLocators
from pages.baw.shell_process_page import ShellProcessPage
from tests.conftest import test_context  # noqa: F401
from tests.steps.baw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


def _safe_screenshot(page: ShellProcessPage, name: str) -> None:
    """Take screenshot and attach to Allure report, silently handling failures."""
    try:
        logger.attach_screenshot(page.page, name)
    except Exception:
        logger.warning(f"Could not take screenshot: {name}")


def _ctx(test_context) -> tuple[ShellProcessPage, dict]:
    """Return (ShellProcessPage, test_data) from test_context."""
    page_obj = test_context.get("shell_process_page")
    if not page_obj:
        raise ValueError("Shell Process page not initialized. Open or switch to Shell Process first.")
    return page_obj, test_context.get("test_data", {})


def _require(data: dict, key: str) -> str:
    """Get a required non-empty string value from test data."""
    value = str(data.get(key, "") or "").strip()
    if not value:
        raise ValueError(f"{key} not found in test data")
    return value


@when('Select work item type "Digital Check"')
@when(parsers.parse('Select work item type "{value}"'))
def step_select_work_item_type(test_context, value: str):
    page, _ = _ctx(test_context)
    page.select_work_item_type(value)
    # Track the work item type so subsequent Fetch step can stash the B# under
    # a type-specific key (e.g. ``digital_check_b_number``).
    test_context["work_item_type"] = value


@then("Select custodian type for activation")
def step_select_custodian_type_for_activation(test_context):
    page, data = _ctx(test_context)
    page.select_custodian_type(_require(data, "CustodianSelection"))


@when("Select individual owner and click run now")
def step_select_individual_owner_and_click_run_now(test_context):
    page, data = _ctx(test_context)
    page.select_individual_owner_and_click_run_now(_require(data, "IndiUser"))


# ----------------------------------------------------------------------
# C95666 - Check Document Extraction steps
# ----------------------------------------------------------------------
@when("Select Individual Owner")
def step_select_individual_owner_only(test_context):
    """Select the individual owner WITHOUT clicking Run Now.

    Used by the C95666 Check Document Extraction scenario where the
    upload-check-document + Submit flow replaces the Run Now navigation.
    """
    page, data = _ctx(test_context)
    page.select_individual_owner(_require(data, "IndiUser"))


@when("Upload the check document and click on Submit button")
def step_upload_check_document_and_submit(test_context):
    """Upload the check document via Add Document/Choose File/Commit Documents,
    then dismiss any dialog and click Submit on the parent work item page.

    The document filename is taken from ``CheckDocument`` in test data when
    provided; otherwise the default sample
    (``PDF to Upload/<default file>``) is used.
    """
    page, data = _ctx(test_context)
    file_path = str(data.get("CheckDocument", "") or "").strip() or ShellProcessLocators.DEFAULT_CHECK_DOCUMENT_FILENAME
    page.upload_check_document_and_submit(file_path)


@when("Go to search page and copy the Check B number and Run the Check B number in Dashboard")
def step_search_and_run_check_b_number_in_dashboard(test_context):
    """Open Search Work Item BAW, filter by the current work item type
    (captured earlier by ``Select work item type``), copy the B# of the
    first matching result, then navigate to the Dashboard and open the
    shell process page for that B#."""
    page, _ = _ctx(test_context)
    work_item_name = str(
        test_context.get("work_item_type", "") or "Digital Check"
    ).strip() or "Digital Check"
    # Use the first word (lowercased) as the multiselect filter, mirroring
    # the codegen recording (".default".fill("digital") for "Digital Check").
    work_item_filter = work_item_name.split()[0].lower() if work_item_name else "digital"
    copied = page.search_and_run_check_b_number_in_dashboard(
        work_item_name=work_item_name,
        work_item_filter=work_item_filter,
    )
    if copied:
        test_context["check_b_number_copied"] = copied
        logger.info(
            f"Copied Check B# stored in test_context['check_b_number_copied']: {copied}",
            attach_to_allure=True,
        )


@when("Fetch b number from shell process page")
def step_fetch_b_number_from_shell_process_page(test_context):
    """
    Fetch B number from Shell Process page.
    Stores the B number in test_context for later use.
    Also appends to ``b_numbers_history`` and, if a previous ``b_number`` was
    captured for an earlier work item in the same scenario, preserves it under
    a work-item-specific key (e.g. ``digital_check_b_number``) so it isn't
    lost when the next Fetch step overwrites ``b_number``.
    """
    shell_process_page, _ = _ctx(test_context)

    # Preserve any previously-fetched B# under a type-specific key before we
    # overwrite ``b_number``. Use the work item type captured *at the time the
    # previous B# was fetched* (stored in ``b_number_work_item_type``) — not
    # the current ``work_item_type`` which already reflects the new selection.
    previous_b = str(test_context.get("b_number", "") or "").strip()
    if previous_b:
        previous_type = str(
            test_context.get("b_number_work_item_type", "")
            or test_context.get("work_item_type", "")
            or ""
        ).strip()
        if previous_type:
            slug = previous_type.lower().replace(" ", "_")
            key = f"{slug}_b_number"
            test_context.setdefault(key, previous_b)
            logger.info(f"Preserved previous B# {previous_b} under '{key}'")

    b_number = shell_process_page.fetch_b_number()
    test_context["b_number"] = b_number
    # Record which work item type this B# belongs to for the *next* fetch.
    test_context["b_number_work_item_type"] = str(
        test_context.get("work_item_type", "") or ""
    )
    history = test_context.setdefault("b_numbers_history", [])
    history.append(b_number)
    logger.info(f"Child B Number: {b_number}", attach_to_allure=True)


@when("Enter Custodial Account value")
def step_enter_custodial_account_value(test_context):
    page, data = _ctx(test_context)
    page.enter_custodial_account_value(_require(data, "AccountNumber"))
	
@when("User enter hrc number and click on submit")
def step_user_enter_hrc_number_and_click_on_submit(test_context):
    """
    Enter HRC number in Shell Process page and submit.
    The HRC number should have been extracted from View Documents step.
    Allows taking screenshots before and after HRC submission.
    """
    page, _ = _ctx(test_context)

    # Retrieve HRC number from test context (should be extracted from PDF in View Documents step)
    hrc_number = test_context.get("hrc_number", "").strip()
    
    logger.info(f"Attempting to enter HRC number from test context")
    logger.info(f"Available context keys: {list(test_context.keys())}")
    logger.info(f"HRC number value: '{hrc_number}'")
        
    _safe_screenshot(page, "HRC Before Action")
        
    if not hrc_number:
        logger.error("HRC number is empty or not found in test context")
        logger.error(f"Full test context: {test_context}")
        _safe_screenshot(page, "HRC Error State")
        raise ValueError(
            "HRC number not found in test context. Ensure View Documents step extracted it from PDF. "
            "Check if 'Separate Documents' step executed successfully."
        )

    logger.info(f"HRC Number: {hrc_number}", attach_to_allure=True)
        
    try:
        # Step 1: Enter HRC number
        page.enter_hrc(hrc_number)

        _safe_screenshot(page, "HRC Entered Before Submit")

        # Step 2: Submit HRC (includes wait before clicking)
        page.submit_hrc()
        
        # Update test_context in case page was recovered
        test_context["baw_page"] = page.page
        
        # Take screenshot after submission (wrapped in try-except to handle closed pages)
        try:
            page.page.screenshot(path="/tmp/hrc_after.png")
            allure.attach.file("/tmp/hrc_after.png", name="HRC After Submission", attachment_type=allure.attachment_type.PNG)
        except Exception as screenshot_error:
            logger.warning(f"Could not take after submission screenshot: {screenshot_error}")

        logger.info("HRC number submitted successfully")
    except Exception as e:
        logger.error(f"Error entering HRC: {str(e)}")
        _safe_screenshot(page, "HRC Exception")
        raise

    try:
        page.baw_spinner_loader()
    except Exception as spinner_error:
        logger.warning(f"Spinner loader check failed after HRC submit (spinner may have already disappeared): {spinner_error}")
        logger.info("Continuing with next step despite spinner check failure")
        


@when(parsers.parse('Click on "{button_type}" button under account number association'))
def step_click_on_button_under_account_number_association(
    test_context, button_type: str
):
    """
    Click button under account number association section in Shell Process page.

    Args:
        test_context: Test context containing page objects
        button_type: Button name (select/remove/add)
    """
    page, _ = _ctx(test_context)
    page.click_select_button(button_type)
    try:
        page.baw_spinner_loader()
    except Exception as spinner_error:
        logger.warning(f"Spinner loader check failed after '{button_type}' click (spinner may have already disappeared): {spinner_error}")
        logger.info("Continuing with next step despite spinner check failure")

@when("Click on save shell process button")
def step_click_on_save_shell_process_button(test_context):
    page, _ = _ctx(test_context)
    page.click_save_shell_process_button()


@then("Validate added account number and account name")
def step_validate_added_account_number_and_account_name(test_context):
    page, _ = _ctx(test_context)
    test_context["add_account_info"] = page.validate_added_account_in_account_number_association()


@when("Click on save exit button")
def step_click_on_save_exit_button(test_context):
    page, _ = _ctx(test_context)
    naa_coach_page = page.click_save_exit_button()
    if naa_coach_page:
        test_context["naa_coach_page"] = naa_coach_page
        test_context.pop("shell_process_page", None)


@when(parsers.parse('Click on "{button_type}" button under account number association for tms'))
def step_click_on_select_button_for_tms(test_context, button_type: str):
    if button_type.strip().lower() == "add" and ConstructPortfolioStep.is_tms_eligible:
        page, _ = _ctx(test_context)
        page.click_select_button(button_type)
        page.validate_added_account_in_account_number_association()
        naa_coach_page = page.click_save_exit_button()

        if naa_coach_page:
            test_context["naa_coach_page"] = naa_coach_page
            test_context.pop("shell_process_page", None)
    else:
        logger.info("Skipped TMS Add step because TMS not eligible")

@then("Click on update transfer button")
def click_on_update_transfer_button(test_context):
    page, _ = _ctx(test_context)
    transfer_page = page.click_update_transfer_details_button()
    test_context["transferAttributes"] = transfer_page

@then(parsers.parse('Validate notes history section "{msg}"'))
def validate_notes_history_section(test_context, msg: str):
    page, _ = _ctx(test_context)
    text = page.validate_notes_history(expected_text=msg)
    Assertions.assert_true(
        msg.lower() in text.lower(),
        f"Expected text '{msg}' not found in notes history. Actual text: '{text}'"
    )
    logger.info(f"Validated notes history step contains '{msg}'")

@when(parsers.parse('Update internal status "{status}"'))
def update_internal_status(test_context, status: str):
    page, _ = _ctx(test_context)
    page.update_internal_status(status)

@when("User fetches custodian account")
def fetch_custodian_account(test_context):
    page, _ = _ctx(test_context)
    shell_custodian_acc = page.fetch_custodian_account()
    test_context["shell_custodian_acc"] = shell_custodian_acc

@when("click on Update OA button")
def click_Update_OA_button(test_context):
    page, _ = _ctx(test_context)
    page.clickAddUpdateButton()
    page.page.wait_for_load_state("load", timeout=30000)
    test_context["create_oa_page"] = CreateOAPage(page.page)


# ============================================================================
# C95661: Check work item association steps
# ============================================================================

@when("Select account row from search results")
def step_select_account_row_from_search_results(test_context):
    page, data = _ctx(test_context)
    page.select_account_row_in_results(_require(data, "AccountNumber"))


@when("User clicks on Create New Digital Record and Add Update Check details")
def step_click_create_digital_record_and_add_check_details(test_context):
    """Click 'Create New Digital Record' then 'Add/Update Check details'
    and store the Check Details popup in test_context for the next step.
    """
    page, _ = _ctx(test_context)
    popup = page.click_create_digital_record_and_add_check_details()
    test_context["check_details_popup"] = popup


@when("Validate the Account Funding Validation section")
def step_validate_account_funding_validation_section(test_context):
    """C95666: Verify the AFV section expand/collapse and the category
    results cell on the shell process page."""
    page, _ = _ctx(test_context)
    page.validate_account_funding_validation_section()


@then("User updates check details and clicks save and close")
def step_update_check_details_and_save_close(test_context):
    """Fill all check detail fields in the Coach iframe and click Save & Close."""
    page, data = _ctx(test_context)
    popup = test_context.get("check_details_popup")
    if popup is None:
        raise ValueError(
            "Check Details popup not found in test_context. "
            "Ensure 'User clicks on Create New Digital Record and Add Update Check details' ran first."
        )
    page.fill_check_details_and_save_close(
        popup,
        check_type=str(data.get("CheckType", "A_PersonalCheck")),
        alpha_amount=str(data.get("AlphaAmount", "123")),
        numerical_amount=str(data.get("NumericalAmount", "123")),
        check_date_day=str(data.get("CheckDateDay", "20")),
        check_number=str(data.get("CheckNumber", "4535634634")),
        aba_routing=str(data.get("ABARouting", "011001755")),
        duplicate_option=str(data.get("DuplicateOption", "Original")),
        bank_account_number=str(data.get("BankAccountNumber", "") or ""),
    )
    test_context.pop("check_details_popup", None)


@then("User selects shell B number and clicks Save and Exit")
def step_select_b_number_and_save_exit(test_context):
    """Double-click the shell B# cell, dismiss dialog, click Save & Exit."""
    page, _ = _ctx(test_context)
    b_number = str(test_context.get("b_number", "") or "").strip()
    if not b_number:
        raise ValueError(
            "B number not found in test_context. "
            "Ensure 'Fetch b number from shell process page' ran before this step."
        )
    page.select_b_number_and_save_exit(b_number)


@then("Associate Check work item with transfer")
def step_associate_check_with_transfer(test_context):
    """Click 'Associate Check' in the transfer section of the shell page,
    enter the previously fetched Digital Check work item B#, select the
    'All funds expected were received' radio, and click Submit.

    Reads the check B# from test_context['digital_check_b_number'] which
    is preserved by `step_fetch_b_number_from_shell_process_page` whenever
    a new Fetch step runs after a 'Digital Check' work item was created.
    """
    page, _ = _ctx(test_context)
    check_b_number = str(
        test_context.get("digital_check_b_number", "") or ""
    ).strip()
    if not check_b_number:
        raise ValueError(
            "Digital Check B# not found in test_context['digital_check_b_number']. "
            "Ensure the Digital Check work item was created and a subsequent "
            "Fetch step preserved its B# before this step."
        )
    page.associate_check_with_transfer(check_b_number)
    logger.info(
        f"Associated Check work item {check_b_number} with transfer",
        attach_to_allure=True,
    )


@then("Verify the added note for Associate Check")
def step_verify_associate_check_note(test_context):
    """Click Save & Refresh on the shell page and assert the newly added
    Associate Check note is rendered in //*[@id='CustomHTML11_0']/pre."""
    page, _ = _ctx(test_context)
    note_text = page.verify_associate_check_note(
        expected_text="A check to fund this transfer has been received"
    )
    logger.info(
        f"Verified Associate Check note: '{note_text}'",
        attach_to_allure=True,
    )


@then("Verify the added note in check work item for Associate Check")
def step_verify_associate_check_note_in_check_work_item(
    test_context, baw_dashboard_page
):
    """Re-open the Digital Check work item via the dashboard (Run icon) and
    assert the same 'Associate Check' note is present in its notes section.

    Uses ``test_context['digital_check_b_number']`` (preserved by the Fetch
    step after the Digital Check work item was created) and reuses the
    existing ``_navigate_to_shell_via_dashboard`` + ``verify_associate_check_note``
    logic so we don't duplicate the search/run/notes flow.
    """
    page_obj = test_context.get("shell_process_page")
    if page_obj is None:
        page_obj = ShellProcessPage(baw_dashboard_page.page)
        test_context["shell_process_page"] = page_obj

    check_b_number = str(
        test_context.get("digital_check_b_number", "") or ""
    ).strip()
    if not check_b_number:
        raise ValueError(
            "Digital Check B# not found in test_context['digital_check_b_number']. "
            "Ensure the Digital Check work item was created earlier in the scenario."
        )

    # Force the dashboard page as the active page so the dashboard-search
    # path is exercised (the previous step left self.page on the transfer
    # shell popup).
    dashboard_page = baw_dashboard_page.page
    page_obj.page = dashboard_page
    page_obj.internal_status = dashboard_page.get_by_role(
        "combobox", name="Internal Status"
    )
    page_obj.save_exit_button = dashboard_page.locator("button#ButtonGroup0_Button2")
    try:
        dashboard_page.bring_to_front()
    except Exception:
        pass

    with logger.step(
        f"Open Digital Check work item {check_b_number} from dashboard", page=dashboard_page
    ):
        page_obj._navigate_to_shell_via_dashboard(check_b_number)

    note_text = page_obj.verify_associate_check_note(
        expected_text="Transfer related to this check"
    )
    logger.info(
        f"Verified Associate Check note in Digital Check work item {check_b_number}: "
        f"'{note_text}'",
        attach_to_allure=True,
    )


# ============================================================================
# C95662: Work item cleanup step
# ============================================================================

@when(parsers.parse('Closing work item after testing for "{b_numbers_csv}"'))
def step_closing_work_item_after_testing(test_context, baw_dashboard_page, b_numbers_csv: str):
    """Close one or more work items listed in the step parameter.

    Used by the C95662 scenario.  After a single BAW login the user is on
    the dashboard; for every B# in the comma-separated parameter this step
    searches the dashboard, clicks the Run icon to open the shell page,
    and closes the work item via the existing
    :meth:`ShellProcessPage.close_work_item` logic.  All B numbers are
    processed sequentially in this single step so no re-login is required
    between them.

    Expected feature-file shape::

        When Closing work item after testing for "B100123615,B100120975"
    """
    b_numbers: list[str] = [
        v.strip() for v in (b_numbers_csv or "").split(",") if v and v.strip()
    ]
    if not b_numbers:
        raise ValueError(
            "'Closing work item after testing' requires at least one B number "
            "in the quoted, comma-separated parameter."
        )
    logger.info(f"Closing {len(b_numbers)} work item(s): {b_numbers}")

    # Reuse an existing ShellProcessPage when available; otherwise build one
    # that wraps the current dashboard page so close_work_item can perform
    # its dashboard-search → Run-icon → close flow.
    page_obj = test_context.get("shell_process_page")
    if page_obj is None:
        page_obj = ShellProcessPage(baw_dashboard_page.page)
        test_context["shell_process_page"] = page_obj

    # User is on the BAW dashboard after login — force the dashboard-search
    # path for every B number (don't rely on the URL heuristic).
    dashboard_page = page_obj.page
    for b_number in b_numbers:
        with logger.step(f"Close work item {b_number}", page=page_obj.page):
            # Restore the dashboard page for each iteration (close flow may
            # have switched self.page to a popup that is now closed).
            page_obj.page = dashboard_page
            page_obj.internal_status = dashboard_page.get_by_role(
                "combobox", name="Internal Status"
            )
            page_obj.save_exit_button = dashboard_page.locator(
                "button#ButtonGroup0_Button2"
            )
            try:
                dashboard_page.bring_to_front()
            except Exception:
                pass
            logger.info(f"Dashboard search for {b_number}")
            page_obj._navigate_to_shell_via_dashboard(b_number)
            page_obj._close_current_work_item()
            logger.info(f"Work item {b_number} closed successfully")


# ============================================================================
# C12345: Agent Notification step
# ============================================================================

@when("Click on View Notification Preferences button and verify the notification preferences for the work item")
def step_click_view_notification_preferences(test_context):
    """Click the View Notification Preferences link on the shell process page
    and verify that the notification preferences popup/page opens successfully."""
    page, _ = _ctx(test_context)
    popup = page.click_view_notification_preferences()
    assert popup is not None, (
        "View Notification Preferences popup did not open. "
        "Check that the link is visible on the shell process page."
    )
    logger.info("Notification Preferences popup verified", attach_to_allure=True)

#====================================================================
# IWR Extraction steps
# ============================================================================

@when("Click add document button and upload the check document")
def step_click_add_document_and_upload_iwr(test_context):
    page, data = _ctx(test_context)
    file_path = (
        str(data.get("IWRDocument", "") or "").strip()
        or ShellProcessLocators.DEFAULT_CHECK_DOCUMENT_FILENAME
    )
    page.upload_check_document(file_path)


@when("Click submit button and store work item number")
def step_click_submit_and_store_work_item_number(test_context):
    page, _ = _ctx(test_context)
    work_item_number = page.submit_iwr_work_item()
    test_context["iwr_work_item_number"] = work_item_number
    test_context["shell_process_page"] = page
    logger.info(f"Stored IWR work item number: {work_item_number}", attach_to_allure=True)


@when("Click Search Work Item BAW and enter the stored work item number")
def step_navigate_search_baw_and_enter_work_item_id(test_context):
    page, _ = _ctx(test_context)
    work_item_id = test_context.get("iwr_work_item_number", "")
    if not work_item_id:
        raise ValueError(
            "IWR work item number not found in test context. "
            "Ensure 'Click submit button and store work item number' ran first."
        )
    page.navigate_to_search_baw_and_enter_work_item_id(work_item_id)


@then(parsers.parse('Validate the view note "{expected_text}"'))
def step_validate_iwr_view_note(test_context, expected_text: str):
    page, _ = _ctx(test_context)
    page.validate_iwr_extraction_note(expected_text)


@when("Click Create New Digital record and Add/Update check details")
def step_iwr_click_create_digital_record_and_add_check_details(test_context):
    page, _ = _ctx(test_context)
    page.create_new_digital_record_and_open_check_details()
    test_context["shell_process_page"] = page
