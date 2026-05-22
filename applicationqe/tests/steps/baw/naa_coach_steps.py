"""NAA Coach Step Definitions for BDD tests"""

from pytest_bdd import parsers, then, when

from pages.baw.naa_coach_page import NAACoachPage
from pages.baw.shell_process_page import ShellProcessPage
from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when(parsers.parse('User clicks on "{work_type}" b number open button'))
def step_user_clicks_on_b_number_open_button(
    naa_coach_page: NAACoachPage,
    shell_process_page: ShellProcessPage,
    work_type: str,
):
    """Click on the open button for a specific work type in NAA Coach page."""
    naa_coach_page.click_open_button(work_type)
    shell_process_page.switch_to_shell_process_page(source_page=naa_coach_page.page)
    logger.info(f"Successfully clicked open button for work type: {work_type}")


@when(parsers.parse('User switch to "{page_title}" page'))
def step_user_switch_to_target_page(naa_coach_page: NAACoachPage, page_title: str):
    """Switch to target page from the NAA Coach page object layer."""
    if page_title.strip().lower() == "naa coach":
        naa_coach_page.switch_to_naa_coach_page()
    else:
        naa_coach_page.switch_to_page_by_title(page_title, timeout=30)
    logger.info(f"Switched to page: {page_title}")


@when(parsers.parse('User select CIP status "{cip_status}" and save client'))
def step_user_select_cip_status_and_save_client(
    naa_coach_page: NAACoachPage, test_context, cip_status: str
):
    """Select CIP status and save client data (GNW only)."""
    test_data = test_context.get("test_data", {})
    custodian_selection = test_data.get("CustodianSelection", "").strip()

    if custodian_selection.upper() == "GNW":
        logger.info(f"Custodian is GNW, proceeding with CIP status selection: {cip_status}")
        naa_coach_page.select_cip_and_save_client(cip_status)
        logger.info(f"CIP status '{cip_status}' selected and client data saved successfully")
    else:
        logger.info(f"Step inapplicable for partner custodian: {custodian_selection}")


@when(parsers.parse('User clicks on "{work_type}" b number open button for tms'))
def step_user_clicks_on_b_number_open_button_for_tms(
    naa_coach_page: NAACoachPage,
    shell_process_page: ShellProcessPage,
    work_type: str,
):
    """For TMS-eligible clients, add and open the requested work item from NAA Coach."""
    if ConstructPortfolioStep.is_tms_eligible:
        naa_coach_page.click_save_and_refresh()
        naa_coach_page.add_work_item(work_type)
        naa_coach_page.click_save_and_refresh()
        naa_coach_page.click_open_button(work_type)
        shell_process_page.switch_to_shell_process_page(source_page=naa_coach_page.page)
    else:
        logger.info(
            "Step inapplicable for non TMS eligible client: "
            "New Account Tax Management is not applicable for this client"
        )


@when("expand the account and click on vieweditappdata button")
def step_expand_account_and_open_view_edit_app_data(
    naa_coach_page: NAACoachPage,
    test_context,
    _pytest_bdd_example,
):
    """Expand the account, open View/Edit App Data, verify plan document, and fill IDs."""
    irs_plan_docu_type = (_pytest_bdd_example.get("IRSPlanDocuType", "") or "").strip()
    plan_document_option = irs_plan_docu_type or (test_context.get("test_data", {}).get("PlanDocumentOption", "") or "").strip()

    naa_coach_page.prepare_view_edit_app_data_for_activation(
        plan_document_option=plan_document_option,
        epic_plan_id="876",
        penchecks_plan_id="765776767686",
    )
    test_context["view_edit_app_data_prepared"] = True
    logger.info("Expanded account, updated View/Edit App Data, and saved changes")


@when("User does the activate account")
def step_user_does_the_activate_account(naa_coach_page: NAACoachPage, test_context):
    """Run account activation workflow in NAA Coach using account type from test data."""
    test_data = test_context.get("test_data", {})
    account_activation = (test_data.get("AccountActivation", "") or "").strip().lower()
    if account_activation == "no":
        logger.info("AccountActivation is 'no', skipping account activation", attach_to_allure=True)
        return

    account_type = (
        test_data.get("ClientAccountType")
        or test_data.get("CLIENT_ACCOUNT_TYPE")
        or test_data.get("AccountType")
        or ""
    )
    _ = account_type

    naa_coach_page.expand_activation_section()
    logger.info("Account activation button clicked", attach_to_allure=True)

    plan_document_option = (test_data.get("PlanDocumentOption", "") or "").strip()
    custodian_selection = (test_data.get("CustodianSelection", "") or "").strip()
    if (
        custodian_selection.upper() == "GNW"
        and plan_document_option
        and not test_context.get("view_edit_app_data_prepared")
    ):
        naa_coach_page.validate_plan_document_epic_plan_id_and_penchecks_plan_id(
            plan_document_option=plan_document_option,
        )

    naa_coach_page.activate_accounts()
    logger.info("Account activated", attach_to_allure=True)


@then("User validate the activated account and switch to eWM")
def step_user_validate_the_activated_account_and_switch_to_ewm(
    naa_coach_page: NAACoachPage,
    test_context,
):
    """Validate activated account section and switch to eWM tab."""
    test_data = test_context.get("test_data", {})
    account_activation = (test_data.get("AccountActivation", "") or "").strip().lower()
    if account_activation == "no":
        logger.info("AccountActivation is 'no', skipping validation and eWM switch", attach_to_allure=True)
        return
    custodian_code = (test_data.get("CustodianSelection", "") or "").strip()
        
    ewm_page = naa_coach_page.expand_action_section_for_validation(
            ConstructPortfolioStep.is_tms_eligible,
            custodian_code,
        )
    Assertions.assert_is_not_none(NAACoachPage.activated_account_number, "Activated account number fetched after activation")
    logger.info(f"Activated Account Number: {NAACoachPage.activated_account_number}")
    logger.attach_summary_table({
        "Username": test_data.get("UserName") or test_data.get("username", ""),
        "Client Full Name": test_context.get("client_full_name", ""),
        "Activated Account Number": NAACoachPage.activated_account_number,
        "HRC Number": test_context.get("hrc_number", ""),
        "Child B Number": test_context.get("b_number", ""),
        "Parent B Number": test_context.get("parent_b_number", ""),
    }, name="Account Activation Summary")


@when("Switch to Naa Coach page and click open button")
def step_switch_to_naa_coach_and_click_open_button(
    naa_coach_page: NAACoachPage,
    shell_process_page: ShellProcessPage,
):
    """Switch back to NAA Coach page and open New Account Application work item."""
    naa_coach_page.click_open_button("New Account Application")
    shell_process_page.switch_to_shell_process_page(source_page=naa_coach_page.page)
    logger.info("Switched to NAA Coach and opened New Account Application work item")
