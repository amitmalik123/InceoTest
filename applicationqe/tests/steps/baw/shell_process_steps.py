"""Shell Process Step Definitions for BDD tests"""

from pytest_bdd import parsers, then, when

from applicationqe.pages.baw.baw_dashboard_page import BawDashboardPage
from applicationqe.pages.baw.naa_coach_page import NAACoachPage
from applicationqe.pages.baw.shell_process_page import ShellProcessPage
from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when(parsers.parse('Select work item type "{value}"'))
def step_select_work_item_type(shell_process_page: ShellProcessPage, value: str):
    shell_process_page.select_work_item_type(value)


@then("Select custodian type for activation")
def step_select_custodian_type_for_activation(shell_process_page: ShellProcessPage, test_context):
    data = test_context.get("test_data", {})
    custodian_value = (data.get("CustodianSelection", "") or "").strip()
    if not custodian_value:
        raise ValueError("CustodianSelection not found in test data")
    shell_process_page.select_custodian_type(custodian_value)


@when("Select individual owner and click run now")
def step_select_individual_owner_and_click_run_now(shell_process_page: ShellProcessPage, test_context):
    data = test_context.get("test_data", {})
    individual_user = (data.get("IndiUser", "") or "").strip()
    if not individual_user:
        raise ValueError("IndiUser not found in test data")
    shell_process_page.select_individual_owner_and_click_run_now(individual_user)


@when("Fetch b number from shell process page")
def step_fetch_b_number_from_shell_process_page(shell_process_page: ShellProcessPage, test_context):
    b_number = shell_process_page.fetch_b_number()
    test_context["b_number"] = b_number
    Assertions.assert_is_not_none(b_number, "B number fetched from shell process page")
    logger.info(f"Child B Number: {b_number}")
    logger.attach_summary_table({
        "Username": test_context.get("test_data", {}).get("UserName") or test_context.get("test_data", {}).get("username", ""),
        "Client Full Name": test_context.get("client_full_name", ""),
        "Child B Number": b_number,
    }, name="Shell Process - B Number")


@when("User enter hrc number and click on submit")
def step_user_enter_hrc_number_and_click_on_submit(
    shell_process_page: ShellProcessPage,
    baw_dashboard_page: BawDashboardPage,
    test_context,
):
    """Enter HRC number in Shell Process page and submit."""
    hrc_number = test_context.get("hrc_number", "").strip()

    with logger.step("User enter hrc number and click on submit", page=shell_process_page.page):
        logger.info("Attempting to enter HRC number from test context")
        logger.info(f"Available context keys: {list(test_context.keys())}")
        logger.info(f"HRC number value: '{hrc_number}'")

        if not hrc_number:
            logger.error("HRC number is empty or not found in test context")
            raise ValueError(
                "HRC number not found in test context. Ensure View Documents step extracted it from PDF. "
                "Check if 'Separate Documents' step executed successfully."
            )

        logger.attach_summary_table({"HRC Number": hrc_number}, name="Shell Process - HRC Submit")

        shell_process_page.enter_hrc(hrc_number)
        shell_process_page.submit_hrc()
        logger.info("HRC number submitted successfully")

    try:
        shell_process_page.spinner_loader()
    except Exception as spinner_error:
        logger.warning(
            f"Spinner loader check failed after HRC submit (spinner may have already disappeared): {spinner_error}"
        )
        logger.info("Continuing with next step despite spinner check failure")
    
    # Restore focus to parent dashboard page after HRC submit completes
    try:
        baw_dashboard_page.page.bring_to_front()
        logger.info("Brought parent dashboard page back to front after HRC submit")
    except Exception as e:
        logger.warning(f"Failed to restore parent dashboard page focus: {e}")
        logger.info("Continuing with next step despite parent page restore failure")


@when(parsers.parse('Click on "{button_type}" button under account number association'))
def step_click_on_button_under_account_number_association(shell_process_page: ShellProcessPage, button_type: str):
    shell_process_page.click_select_button(button_type)
    try:
        shell_process_page.spinner_loader()
    except Exception as spinner_error:
        logger.warning(
            f"Spinner loader check failed after '{button_type}' click (spinner may have already disappeared): {spinner_error}"
        )
        logger.info("Continuing with next step despite spinner check failure")


@when("Click on save shell process button")
def step_click_on_save_shell_process_button(shell_process_page: ShellProcessPage):
    shell_process_page.click_save_shell_process_button()


@then("Validate added account number and account name")
def step_validate_added_account_number_and_account_name(shell_process_page: ShellProcessPage, test_context):
    add_account_info = shell_process_page.validate_added_account_in_account_number_association()
    test_context["add_account_info"] = add_account_info


@when("Click on save exit button")
def step_click_on_save_exit_button(shell_process_page: ShellProcessPage, naa_coach_page: NAACoachPage):
    shell_process_page.click_save_exit_button()
    try:
        naa_coach_page.page.bring_to_front()
        logger.info("Brought NAA Coach page to front after Save & Exit")
    except Exception as e:
        logger.warning(f"bring_to_front failed after Save & Exit, falling back to switch logic: {e}")
        try:
            naa_coach_page.switch_to_naa_coach_page()
            logger.info("Switched to NAA Coach page after Save & Exit (fallback)")
        except Exception as switch_error:
            logger.warning(f"Failed to switch to NAA Coach page after Save & Exit: {switch_error}")
            logger.info("Continuing with next step despite NAA Coach page switch failure")



@when(parsers.parse('Click on "{button_type}" button under account number association for tms'))
def step_click_on_select_button_for_tms(shell_process_page: ShellProcessPage, button_type: str):
    with logger.step(f'Click on "{button_type}" button under account number association for tms'):
        if button_type.strip().lower() == "add" and ConstructPortfolioStep.is_tms_eligible:
            shell_process_page.click_select_button(button_type)
            shell_process_page.validate_added_account_in_account_number_association()
            shell_process_page.click_save_exit_button()
        else:
            logger.info("Skipped TMS Add step because TMS not eligible")


@when("Close the workitem")
def step_close_the_workitem(shell_process_page: ShellProcessPage):
    """On Shell Process page, set Internal Status to Close-Other and close the work item."""
    shell_process_page.select_internal_status_and_close_work_item("Close-Other")
    logger.info("Work item closed with Internal Status: Close-Other")
