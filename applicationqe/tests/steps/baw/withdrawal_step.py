"""Withdrawal Step Definitions for BAW Withdrawal BDD tests"""

from pathlib import Path

from pytest_bdd import parsers, then, when

from locators.baw.baw_dashboard_locators import BawDashboardLocators
from pages.baw.shell_process_page import ShellProcessPage
from pages.baw.withdrawal_page import WithdrawalPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


def _ctx(test_context):
    """Return (shell_process_page, test_data) from test_context."""
    page = test_context.get("shell_process_page")
    data = test_context.get("test_data", {})
    return page, data


@when("User creates withdrawal work item and adds withdrawal document")
def step_create_withdrawal_and_add_document(test_context):
    """Create withdrawal work item: select type, enter account, add document, select owner, submit."""
    page, data = _ctx(test_context)
    account_number = str(data.get("AccountNumber", "")).strip()
    indi_user = str(data.get("IndiUser", "")).strip()

    # Resolve PDF path from 'upload/BAW' folder
    app_root = Path(__file__).resolve().parents[3]  # applicationqe/
    pdf_path = str(app_root / "upload" / "BAW" / "test document.pdf")

    shell_page = page
    parent_page = shell_page.page

    with logger.step("Create Withdrawal work item and add document", page=parent_page):
        # Select work item type
        shell_page.select_work_item_type("Withdrawal Request")

        # Enter custodial account and wait for search results to load
        shell_page.enter_custodial_account_value(account_number)
        shell_page.wait_for_loading_data()

        # Select the account row in results to enable Individual Owner
        shell_page.select_account_row_in_results(account_number)
        shell_page.wait_for_loading_data()

        # Add document via popup
        add_doc_btn = parent_page.get_by_role("button", name="Add Document")
        add_doc_btn.wait_for(state="visible", timeout=30000)

        upload_popup = None
        try:
            with parent_page.expect_popup(timeout=30000) as popup_info:
                add_doc_btn.click()
            upload_popup = popup_info.value
        except Exception as popup_exc:
            logger.warning(f"expect_popup failed: {popup_exc}, using context page diff")
            existing = set(parent_page.context.pages)
            add_doc_btn.click()
            for _ in range(30):
                added = [p for p in parent_page.context.pages if p not in existing]
                if added:
                    upload_popup = added[-1]
                    break
                parent_page.wait_for_timeout(500)

        if upload_popup is None:
            raise AssertionError("Upload popup did not open after clicking Add Document")

        upload_popup.wait_for_load_state("domcontentloaded", timeout=30000)

        choose_file = upload_popup.get_by_role("button", name="Choose File")
        choose_file.wait_for(state="visible", timeout=20000)
        try:
            choose_file.set_input_files(pdf_path)
        except Exception:
            with upload_popup.expect_file_chooser(timeout=20000) as fc_info:
                choose_file.click()
            fc_info.value.set_files(pdf_path)
        logger.info(f"Selected file for upload: {pdf_path}")

        commit_btn = upload_popup.get_by_role("button", name="Commit Documents")
        commit_btn.wait_for(state="visible", timeout=20000)
        commit_btn.click()
        logger.info("Clicked Commit Documents")

        # Wait for popup to close after commit
        try:
            upload_popup.wait_for_event("close", timeout=10000)
        except Exception:
            if not upload_popup.is_closed():
                upload_popup.close()

        # After Commit Documents the upload popup closes; the parent work item
        # page may also close or navigate away in some BAW environments.
        # Use shell_page.page (the underlying BAW session page) for all waits.
        active_page = shell_page.page
        try:
            parent_page.bring_to_front()
        except Exception:
            pass
        try:
            active_page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        shell_page.wait_for_loading_data()
        # Extra wait for data prefill from uploaded document
        try:
            active_page.wait_for_timeout(5000)
        except Exception:
            pass
        shell_page.wait_for_loading_data()
        logger.info("Document uploaded, waiting for data prefill")

        # Wait for Individual Owner dropdown to be enabled (data prefill enables it)
        shell_page.individual_owner.wait_for(state="visible", timeout=30000)
        for attempt in range(60):
            if shell_page.individual_owner.is_enabled():
                logger.info(f"Individual Owner dropdown enabled after {attempt + 1}s")
                break
            try:
                active_page.wait_for_timeout(1000)
            except Exception:
                import time; time.sleep(1)
        else:
            logger.warning("Individual Owner dropdown still disabled after 60s, attempting selection anyway")

        shell_page.individual_owner.select_option(indi_user)
        logger.info(f"Individual owner selected: {indi_user}")

        # Set up dialog handler to capture instance ID from alert
        # Alert format: "Work item created successfully:10017714"
        dialog_message = {}

        def handle_submit_dialog(dlg):
            dialog_message["text"] = dlg.message
            logger.info(f"Dialog captured: {dlg.message}")
            dlg.accept()

        parent_page.once("dialog", handle_submit_dialog)
        submit_btn = parent_page.get_by_role("button", name="Submit")
        submit_btn.wait_for(state="visible", timeout=30000)
        submit_btn.click(no_wait_after=True)
        logger.info("Clicked Submit on work item page")

        # Wait for dialog to fire — page may auto-close after accept
        try:
            parent_page.wait_for_timeout(3000)
        except Exception:
            pass  # Page closed after dialog accept, that's expected

        # Extract instance ID from dialog message
        instance_id = ""
        msg = dialog_message.get("text", "")
        if ":" in msg:
            instance_id = msg.split(":")[-1].strip()
        if instance_id:
            test_context["instance_id"] = instance_id
            logger.info(f"Captured work item instance ID: {instance_id}", attach_to_allure=True)
        else:
            logger.warning(f"Could not extract instance ID from dialog: '{msg}'")

        # Wait for parent page to close after submit
        try:
            parent_page.wait_for_event("close", timeout=10000)
        except Exception:
            if not parent_page.is_closed():
                parent_page.close()

        logger.info("Withdrawal work item created and document uploaded")


@when("User searches work item by instance ID and copies B number")
def step_search_work_item_and_copy_b_number(baw_dashboard_page, test_context):
    """Go to Search Work Item, search by instance ID, copy B number."""
    page = baw_dashboard_page.page

    instance_id = str(test_context.get("instance_id", "")).strip()
    if not instance_id:
        raise ValueError("instance_id not found in test_context. Submit dialog may not have been captured.")

    with logger.step(f"Search Work Item by Instance ID: {instance_id}", page=page):
        # Click Search Work Item tab
        page.get_by_role("link", name="Search Work Item BAW").click()
        page.wait_for_timeout(3000)

        coach_frame = page.locator("iframe[title=\"Coach\"]").content_frame

        # Enter instance ID in Work Item ID field and search
        work_item_id_input = coach_frame.get_by_role("textbox", name="Work Item ID")
        work_item_id_input.wait_for(state="visible", timeout=30000)
        work_item_id_input.fill(instance_id)

        # B number result locator (td cell with id containing 'BNumber')
        b_cell = coach_frame.locator("td[id*='BNumber']").first
        search_btn = coach_frame.get_by_role("button", name="Search")

        # Retry search every 5 seconds until B number appears in results (max 12 attempts = 60s)
        for attempt in range(12):
            search_btn.click()
            page.wait_for_timeout(5000)
            try:
                b_cell.wait_for(state="visible", timeout=5000)
                logger.info(f"B number visible in search results after {attempt + 1} attempt(s)")
                break
            except Exception:
                logger.info(f"Search result not ready, retrying... (attempt {attempt + 1})")
                work_item_id_input.fill(instance_id)
        else:
            raise AssertionError(f"B number not found in search results after 12 attempts for instance: {instance_id}")

        b_number = b_cell.inner_text().strip()
        test_context["parent_b_number"] = b_number
        test_context["b_tracking_id"] = b_number
        logger.info(f"Found B number from search: {b_number} (instance: {instance_id})", attach_to_allure=True)


@when("User runs withdrawal B number in Dashboard")
def step_run_withdrawal_b_number_in_dashboard(baw_dashboard_page, test_context):
    """Go to Dashboard, search B number, and click run icon."""
    page = baw_dashboard_page.page
    b_number = test_context.get("parent_b_number", "").strip()

    with logger.step(f"Run B# {b_number} in Dashboard", page=page):
        page.get_by_role("link", name="Dashboard").click()
        page.wait_for_timeout(3000)

        # Use dashboard page to search B#
        baw_dashboard_page.enter_b_number_to_search(b_number)
        page.wait_for_timeout(5000)

        # Find the run icon: img[src*='run.gif'] with onclick containing B number
        # Element: <img src="/portal/jsp/images/run.gif" onclick="return doPopup(...,'B100177415',...)">
        frame_locator = page.frame_locator("xpath=//iframe[@title='Dashboard']")

        def find_run_icon():
            """Locate run icon specific to our B number using multiple strategies."""
            # Strategy 1: onclick contains B number
            s1 = frame_locator.locator(
                BawDashboardLocators.RUN_ICON_BY_ONCLICK_TPL.format(b_tracking_id=b_number)
            ).first
            if s1.count() > 0:
                return s1
            # Strategy 2: row containing B# text, first-column img
            s2 = frame_locator.locator(
                BawDashboardLocators.RUN_ICON_ROW_XPATH_TPL.format(b_tracking_id=b_number)
            ).first
            if s2.count() > 0:
                return s2
            # Strategy 3: broad row search (img/button/icon in first td)
            s3 = frame_locator.locator(
                BawDashboardLocators.RUN_ICON_BROAD_ROW_XPATH_TPL.format(b_tracking_id=b_number)
            ).first
            if s3.count() > 0:
                return s3
            # No B#-specific run icon found
            logger.warning(f"No run icon found for B# {b_number} using B#-specific locators")
            return None

        run_icon = None

        # Step 1: Search B# to confirm it appears in the dashboard
        baw_dashboard_page.enter_b_number_to_search(b_number)
        page.wait_for_timeout(5000)
        logger.info(f"Searched for B# {b_number} in dashboard")

        # Step 2: Double-click Unassigned button to assign the work item
        logger.info("Double-clicking Unassigned button to assign the work item")
        try:
            frame_locator.locator("button#REFRESH").dblclick(timeout=10000)
            logger.info("Unassigned button double-clicked successfully")
        except Exception:
            logger.warning("dblclick failed, trying force click on Unassigned")
            frame_locator.locator("button#REFRESH").click(force=True, timeout=10000)

        # Step 3: Wait for page to load fully after Unassigned click
        page.wait_for_timeout(5000)
        page.wait_for_selector("xpath=//iframe[@title='Dashboard']", state="attached", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        frame_locator = page.frame_locator("xpath=//iframe[@title='Dashboard']")
        logger.info("Dashboard reloaded after Unassigned click")

        # Step 4: Search B# again after Unassigned
        logger.info("Searching B# again after Unassigned click")
        baw_dashboard_page.enter_b_number_to_search(b_number)
        page.wait_for_timeout(5000)

        # Step 5: Find run icon for our specific B# (only exists after assignment)
        run_icon = find_run_icon()
        if run_icon is None:
            raise AssertionError(f"Run icon not found for B# {b_number} after Unassigned + search")
        try:
            run_icon.wait_for(state="visible", timeout=15000)
            logger.info("Run icon visible after Unassigned + search")
        except Exception:
            raise AssertionError(f"Run icon not visible after Unassigned refresh for B# {b_number}")

        # Step 6: Click run icon to open work item popup
        logger.info(f"Run icon confirmed visible, clicking for B# {b_number}")

        # Click run icon to open work item popup
        context = page.context
        existing_pages = set(context.pages)
        new_page = None

        # Wait before clicking run icon to ensure page is ready
        page.wait_for_timeout(3000)

        try:
            with page.expect_popup(timeout=60000) as popup_info:
                run_icon.click()
            new_page = popup_info.value
            logger.info("Popup opened after clicking run icon")
        except Exception:
            logger.warning("expect_popup failed for run icon, checking context pages")
            page.wait_for_timeout(5000)
            added = [p for p in context.pages if p not in existing_pages and not p.is_closed()]
            if added:
                new_page = added[-1]
                logger.info("Found popup page from context pages")

        if new_page is None:
            raise AssertionError(f"Run icon click did not open a new page for B# {b_number}")

        new_page.wait_for_load_state("domcontentloaded", timeout=60000)
        for _state in ("load", "networkidle"):
            try:
                new_page.wait_for_load_state(_state, timeout=30000)
            except Exception:
                pass
        new_page.bring_to_front()

        test_context["withdrawal_page"] = WithdrawalPage(new_page)
        logger.info(f"Opened withdrawal page from Dashboard: {b_number}")


@when("User completes the OCR Screen")
def step_complete_ocr_screen(test_context):
    """Complete the OCR screen for withdrawal."""
    wd_page = test_context.get("withdrawal_page")
    data = test_context.get("test_data", {})
    account_number = str(data.get("AccountNumber", "")).strip()
    client_name = str(data.get("ClientName", "")).strip()

    wd_page.complete_ocr_screen(account_number, client_name)


@then(parsers.parse('User completes the IWR process with delivery method "{method}"'))
def step_complete_iwr_process(test_context, method: str):
    """Complete the IWR process with specified delivery method."""
    wd_page = test_context.get("withdrawal_page")
    data = test_context.get("test_data", {})
    amount = str(data.get("Amount", "10")).strip()
    delivery_data = str(data.get("DeliveryData", "")).strip()

    wd_page.complete_iwr_process(amount, delivery_data)


@when("User clicks on Place Withdrawal OA button")
def step_click_place_withdrawal_oa(test_context):
    """Click Place Withdrawal Advisor OA button in Initiate OA page."""
    wd_page = test_context.get("withdrawal_page")
    wd_page.click_place_withdrawal_oa()


@then("User clicks on Submit to BETA button")
def step_click_submit_to_beta(test_context):
    """Click Submit To BETA button in Initiate Distribution page."""
    wd_page = test_context.get("withdrawal_page")
    wd_page.click_submit_to_beta()

    # Close the withdrawal page after submission
    try:
        wd_page.page.close()
    except Exception:
        pass
    logger.info("Withdrawal submitted to BETA and page closed")


@then(parsers.parse('Validate withdrawal note "{expected_text}"'))
def step_validate_withdrawal_note(baw_dashboard_page, test_context, expected_text: str):
    """Validate the withdrawal submission note in Notes section."""
    page = baw_dashboard_page.page
    b_number = test_context.get("parent_b_number", "").strip()

    with logger.step(f"Validate withdrawal note for {b_number}", page=page):
        dashboard_frame = page.locator("iframe[title='Dashboard']").content_frame

        # Search for the B number in the dashboard before clicking the link
        b_search = dashboard_frame.get_by_role("textbox", name="B#:")
        b_search.wait_for(state="visible", timeout=20000)
        b_search.fill(b_number)
        dashboard_frame.get_by_role("button", name="Search").click()
        page.wait_for_timeout(3000)

        # Click on the B number link to open shell page
        b_link = dashboard_frame.get_by_role("link", name=b_number)
        b_link.wait_for(state="visible", timeout=20000)

        context = page.context
        existing_pages = set(context.pages)

        try:
            with page.expect_popup(timeout=60000) as popup_info:
                b_link.click()
            shell_popup = popup_info.value
            logger.info("Shell popup opened via expect_popup")
        except Exception:
            logger.warning("expect_popup timed out for B# link, checking context pages")
            page.wait_for_timeout(5000)
            added = [p for p in context.pages if p not in existing_pages and not p.is_closed()]
            if added:
                shell_popup = added[-1]
                logger.info("Found shell popup from context pages")
            else:
                raise AssertionError(f"B# link click did not open a new page for {b_number}")

        shell_popup.wait_for_load_state("domcontentloaded", timeout=60000)
        for _state in ("load", "networkidle"):
            try:
                shell_popup.wait_for_load_state(_state, timeout=30000)
            except Exception:
                pass
        page.wait_for_timeout(3000)

        # Get notes text with explicit wait
        notes_loc = shell_popup.get_by_text(expected_text)
        notes_loc.wait_for(state="visible", timeout=30000)
        notes_text = notes_loc.inner_text()
        Assertions.assert_true(
            expected_text.lower() in notes_text.lower(),
            f"Expected note '{expected_text}' not found. Actual: '{notes_text}'"
        )
        logger.info(f"Validated withdrawal note: '{expected_text}'")
        shell_popup.close()
