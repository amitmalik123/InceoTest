"""BDD step definitions for the PMT SDT ISC end-to-end flow.

Canonical (and only) home for every step used by
``tests/features/pmt/sdt_isc.feature``:

  - EWM login verification and account-wizard search
  - Client Management / Change Investments selection, allocation, risk
    assessment, time horizon, liquidity needs
  - Complete & Print, DocuSign, tracking record, PDF upload, B-number capture
  - SDT ISC Process Portal login, search, D-number, ICT activation, OK popup,
    Save & Exit, status dropdown, Add/Update QC Reasons

All page interactions for the SDT ISC portal go through
:class:`pages.pmt.sdt_isc_page.SdtIscPage`. EWM-side interactions reuse the
existing shared framework page objects under ``pages/ewm/`` (login, clients,
account list, account detail, change investments, DocuSign, tracking center)
and the fixtures defined in ``tests/conftest.py``. The local pmt fixtures
(``sdt_isc_page``, ``pmt_query``, ``pmt_db_config``, ...) live in
``tests/features/pmt/conftest.py``.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from pages.pmt.sdt_isc_page import (
    AccountDetailPage,
    AccountListPage,
    ChangeInvestmentsPage,
    ClientsPage,
    DocusignPage,
    SdtIscPage,
    TrackingCenterPage,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

DEFAULT_B_NUMBER = "B100152542"

# Runtime B-number generated during test execution. Populated by the
# "User verify the tracking Id starts with B" step and consumed by the
# SDT ISC Process Portal steps below.
generated_b_number = ""


def _get_b_number() -> str:
    """Get B-number from runtime or fall back to hardcoded value."""
    if generated_b_number and str(generated_b_number).startswith("B"):
        return str(generated_b_number)
    logger.warning(f"No runtime B-number found. Using hardcoded: {DEFAULT_B_NUMBER}")
    return DEFAULT_B_NUMBER


# ==================================================================
# Account Management / EWM login and Account Wizard
# ==================================================================


@given("User login into ewm application on test11 environment")
def user_login_into_ewm_application(authenticated_page: Page, test_context: dict):
    """Verify the user is authenticated on the eWealthManager application.

    The ``authenticated_page`` fixture handles session storage / auto-login.
    """
    current_url = authenticated_page.url
    logger.info(f"Verifying login status - Current URL: {current_url}")
    if current_url and "login" not in current_url.lower():
        logger.info("User is already authenticated (session storage)")
        return
    error_msg = "AUTHENTICATION FAILED: User is not logged in on test11."
    logger.error(error_msg)
    raise AssertionError(error_msg)


@when(parsers.parse('User switches user ID with agent "{agent}" for account "{account}"'))
def user_switches_user_id(
    authenticated_page: Page,
    clients_page: ClientsPage,
    test_context: dict,
    agent: str,
    account: str,
):
    """Store the supplied agent/account in test_data and click the Switch ID link."""
    logger.info(f"Switching user ID with agent='{agent}' account='{account}'")
    test_context["test_data"]["advisor_id"] = agent
    test_context["test_data"]["account_number"] = account
    test_context["test_data"]["client_id"] = agent
    clients_page.switch_user()


@when("User enters agent ID from test data")
def user_enters_agent_id(
    authenticated_page: Page,
    clients_page: ClientsPage,
    test_context: dict,
    test_data: dict,
):
    """Enter the agent ID. Prefer the runtime value set from the feature
    Examples table (test_context); fall back to the CSV row only if unset."""
    agent_id = (
        test_context.get("test_data", {}).get("advisor_id")
        or test_data.get("advisor_id", "")
    )
    if not agent_id:
        raise ValueError("advisor_id not found in test data")
    clients_page.enter_agent_id(agent_id)
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    logger.info(f"Agent ID entered and impersonated: {agent_id}")


@when("User is on the account wizard tab and search the client")
def navigate_to_account_wizard_and_search(
    authenticated_page: Page,
    account_detail_page: AccountDetailPage,
    test_context: dict,
):
    """Navigate to Clients > Account List, search the client, select the account,
    then navigate to Account Wizard.

    Page logic is encapsulated in :class:`AccountDetailPage` per migration
    convention; it was originally split across ``ClientsPage`` and
    ``AccountListPage`` on ``team/portfolio-mgmt-trading``.
    """
    account_number = test_context["test_data"]["account_number"]
    selected = account_detail_page.open_account_wizard_and_search_client(account_number)
    test_context["test_data"]["account_name"] = selected


@when(parsers.parse('Select request "{request_name}" and type "{type_name}" in Account Management'))
def select_request_and_type(
    authenticated_page: Page,
    sdt_isc_page: SdtIscPage,
    request_name: str,
    type_name: str,
):
    """Select the specified request and type in the Account Management section."""
    logger.info(f"Selecting request: '{request_name}', type: '{type_name}'")
    sdt_isc_page.select_request_and_type(request_name, type_name)
    logger.info("Request and type selected in Account Management")


# ==================================================================
# Change Investments
# ==================================================================


@when(parsers.parse('Click on client management option "{option_name}"'))
def click_client_management_option(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    option_name: str,
):
    """Open the Client Management dropdown and click the specified option."""
    logger.info(f"Clicking client management option: {option_name}")
    change_investments_page.click_client_management_option(option_name)
    logger.info(f"'{option_name}' selected from Client Management")


@when("Click on account number and navigate to investment selection tab")
def click_account_number_navigate_to_investment_selection(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click the account number link to navigate to the investment selection tab."""
    logger.info("Clicking account number to navigate to investment selection tab")
    change_investments_page.click_account_number_investment_selection()
    logger.info("On investment selection tab")


@then("Validate Account Number On Destination Investment Tab")
def validate_account_number_on_destination_investment_tab(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    test_context: dict,
):
    """Validate the account number is displayed on the destination investment tab."""
    account_number = test_context["test_data"].get(
        "account_number",
        test_context["test_data"].get("client_id", ""),
    )
    logger.info(f"Validating account number: {account_number}")
    if account_number:
        change_investments_page.validate_account_number_on_destination_tab(account_number)
    else:
        change_investments_page.validate_account_number_visible_on_destination_tab()
    logger.info("Account number validation passed")


@when("Select new investment on destination investment tab")
def select_new_investment(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click 'Select New Investment' button on the destination investment tab."""
    logger.info("Selecting new investment on destination investment tab")
    change_investments_page.select_new_investment()
    logger.info("New investment selected")


@then("Validate New Investment Modal")
def validate_new_investment_modal(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Validate the New Investment modal/dialog is displayed."""
    logger.info("Validating New Investment modal")
    change_investments_page.validate_new_investment_modal()
    logger.info("New Investment modal validated successfully")


@when(parsers.parse('User selects investment strategy "{strategy_name}"'))
def user_selects_investment_strategy(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    strategy_name: str,
):
    """Select the investment strategy type (e.g., Single Strategy Account)."""
    logger.info(f"Selecting investment strategy: {strategy_name}")
    change_investments_page.select_investment_strategy(strategy_name)
    logger.info(f"Investment strategy '{strategy_name}' selected")


@when(parsers.parse('User selects investment profile "{profile_name}"'))
def user_selects_investment_profile(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    profile_name: str,
):
    """Select a specific investment profile from the grid."""
    logger.info(f"Selecting investment profile: {profile_name}")
    change_investments_page.select_investment_profile(profile_name)
    logger.info(f"Investment profile '{profile_name}' selected")


@when("User confirms investment selection")
def user_confirms_investment_selection(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click OK to confirm the investment selection."""
    logger.info("Confirming investment selection")
    change_investments_page.confirm_investment_selection()
    logger.info("Investment selection confirmed")


@when(parsers.parse('User selects allocation option "{allocation_type}"'))
def user_selects_allocation_option(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    allocation_type: str,
):
    """Select allocation option (Full, Partial, etc.)."""
    logger.info(f"Selecting allocation option: {allocation_type}")
    change_investments_page.select_allocation_option(allocation_type)
    logger.info(f"Allocation option '{allocation_type}' selected")


@when("User clicks next to continue")
def user_clicks_next_to_continue(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click Next button to continue to next step."""
    logger.info("Clicking Next to continue")
    change_investments_page.click_next_button()
    logger.info("Navigated to next step")


@when("User clicks next to risk assessment")
def user_clicks_next_to_risk_assessment(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click Next button to continue to risk assessment."""
    logger.info("Clicking Next to risk assessment")
    change_investments_page.click_next_button()
    logger.info("Navigated to risk assessment")


@when("User clicks next to review")
def user_clicks_next_to_review(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click Next button to review."""
    logger.info("Clicking Next to review")
    change_investments_page.click_next_button()
    logger.info("Navigated to review")


@when("User clicks next to complete")
def user_clicks_next_to_complete(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click Next button to complete the process. Skip if already on a final page."""
    logger.info("Clicking Next to complete")
    next_btn = authenticated_page.get_by_role("button", name="Next").first
    try:
        next_btn.wait_for(state="visible", timeout=5000)
    except Exception:
        logger.info(
            f"Next button not visible on {authenticated_page.url} - skipping (final page)"
        )
        return
    change_investments_page.click_next_button()
    logger.info("Process completion step executed")


@when(parsers.parse('User selects risk tolerance "{risk_level}"'))
def user_selects_risk_tolerance(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    risk_level: str,
):
    """Select risk tolerance level."""
    logger.info(f"Selecting risk tolerance: {risk_level}")
    change_investments_page.select_risk_tolerance(risk_level)
    logger.info(f"Risk tolerance '{risk_level}' selected")


@when(parsers.parse('User selects time horizon "{time_period}"'))
def user_selects_time_horizon(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    time_period: str,
):
    """Select time horizon."""
    logger.info(f"Selecting time horizon: {time_period}")
    change_investments_page.select_time_horizon(time_period)
    logger.info(f"Time horizon '{time_period}' selected")


@when(parsers.parse('User selects liquidity needs "{percentage}"'))
def user_selects_liquidity_needs(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    percentage: str,
):
    """Select liquidity needs percentage."""
    logger.info(f"Selecting liquidity needs: {percentage}")
    change_investments_page.select_liquidity_needs(percentage)
    logger.info(f"Liquidity needs '{percentage}' selected")


@then("Investment change should be completed successfully")
def investment_change_completed_successfully(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Validate that the investment change completed successfully."""
    logger.info("Validating investment change completion")
    change_investments_page.validate_investment_change_completed()
    logger.info("Investment change validated as completed successfully")


# ==================================================================
# Complete & Print / DocuSign / Tracking record / PDF / B-number
# ==================================================================


@when("User clicks on complete and print button")
def click_complete_and_print(
    authenticated_page: Page,
    sdt_isc_page: SdtIscPage,
):
    """Click the Complete and Print button."""
    logger.info("Clicking 'Complete and Print' button")
    sdt_isc_page.click_complete_and_print()
    logger.info("'Complete and Print' clicked")


@then("User navigates to docu sign page and clicks on Continue and Finish button")
def handle_docusign(
    authenticated_page: Page,
    docusign_page: DocusignPage,
):
    """Handle the DocuSign redirect - click Continue & Finish.

    Page logic lives in :class:`DocusignPage` (migrated from
    ``team/portfolio-mgmt-trading:pages/account_management_page.py``).
    """
    logger.info("Handling DocuSign page")
    docusign_page.handle_docusign_page()
    logger.info("DocuSign completed")


@then("User opens the tracking record")
def open_tracking_record(
    authenticated_page: Page,
    tracking_center_page: TrackingCenterPage,
    test_context: dict,
):
    """Open the tracking record before uploading the PDF.

    Page logic lives in :class:`TrackingCenterPage` (migrated from
    ``team/portfolio-mgmt-trading:pages/account_management_page.py``).
    """
    logger.info("Opening tracking record")
    tracking_center_page.open_tracking_record()
    test_context["tracking_id"] = ""
    logger.info("Tracking record opened")


@then("User upload the PDF file")
def upload_pdf(
    authenticated_page: Page,
    tracking_center_page: TrackingCenterPage,
):
    """Upload a PDF file on the tracking center page.

    Uses the sample PDF bundled in the repo under ``data/pmt/`` so the test
    is portable across machines (no user-specific paths).
    """
    repo_root = Path(__file__).resolve().parents[3]
    pdf_path = str(repo_root / "data" / "pmt" / "sample_upload.pdf")
    logger.info(f"Uploading PDF file: {pdf_path}")
    tracking_center_page.upload_pdf(pdf_path)
    logger.info("PDF uploaded successfully")


@then("User verify the tracking Id starts with B")
def verify_tracking_id_starts_with_b(
    authenticated_page: Page,
    tracking_center_page: TrackingCenterPage,
    test_context: dict,
):
    """Wait for the generated B-number and verify it starts with 'B'."""
    global generated_b_number
    tracking_id = test_context.get("tracking_id", "")
    if not tracking_id.startswith("B"):
        logger.info(
            "Tracking ID is missing or not a B-number; waiting for it to be generated"
        )
        tracking_id = tracking_center_page.wait_for_tracking_id("B")
        test_context["tracking_id"] = tracking_id
    logger.info(f"Verifying tracking ID: '{tracking_id}' starts with 'B'")
    tracking_center_page.verify_tracking_id_starts_with("B", tracking_id)
    logger.info(f"Tracking ID '{tracking_id}' verified - starts with B")

    generated_b_number = tracking_id


# ==================================================================
# SDT ISC Process Portal
# ==================================================================


@given("User launches SDT ISC process portal login page")
def launch_sdt_isc_process_portal_login_page(sdt_isc_page: SdtIscPage):
    """Launch the SDT ISC Process Portal login page from YAML-backed config."""
    logger.info("Launching SDT ISC Process Portal login page")

    # Wait for the B-number to propagate to the BAW portal before navigating.
    # BAW takes time to reflect newly generated B-numbers.
    logger.info("Waiting 45s for B-number to propagate to BAW portal")
    sdt_isc_page.page.wait_for_timeout(45000)

    try:
        sdt_isc_page.navigate()
    except RuntimeError as error:
        if "Unable to reach SDT ISC Process Portal login page" in str(error):
            pytest.skip(
                "Skipping SDT ISC scenario due to external Process Portal connectivity issue. "
                f"Details: {error}"
            )
        raise


@when(parsers.parse('User logs into SDT ISC process portal as "{user}"'))
def login_to_sdt_isc_process_portal(sdt_isc_page: SdtIscPage, user):
    """Login to the SDT ISC Process Portal and verify login success."""
    logger.info(f"Logging into SDT ISC Process Portal as {user}")
    sdt_isc_page.login_as(str(user))


@when("User searches for the stored B-number")
@when("User searches for the stored B-number in the dashboard")
def search_stored_b_number(sdt_isc_page: SdtIscPage):
    """Search for the B-number that was generated or use hardcoded fallback."""
    b_number = _get_b_number()
    logger.info(f"Searching for stored B-number: '{b_number}'")
    sdt_isc_page.search_b_number(b_number)


@when("User refreshes the dashboard")
def refresh_sdt_isc_dashboard(sdt_isc_page: SdtIscPage):
    """Refresh the SDT ISC Process Portal dashboard page."""
    logger.info("Refreshing SDT ISC Process Portal dashboard")
    sdt_isc_page.refresh_dashboard()


@when(parsers.parse('User verifies internal status is "{expected_status}"'))
def verify_internal_status(sdt_isc_page: SdtIscPage, expected_status: str):
    """Verify the Internal Status cell on the dashboard contains expected text."""
    logger.info(f"Verifying internal status is '{expected_status}'")
    sdt_isc_page.verify_internal_status(expected_status)


@when("User repeats Save and Exit cycle if B-number still visible")
def repeat_save_and_exit_if_visible(sdt_isc_page: SdtIscPage):
    """If the B-number is still in user1's dashboard, click Run + Save & Exit
    + OK popup. Otherwise skip silently and continue to user2."""
    b_number = _get_b_number()
    logger.info(
        f"Checking whether B-number '{b_number}' is still visible to user1 "
        "for a repeat Save & Exit cycle"
    )
    executed = sdt_isc_page.repeat_save_and_exit_if_visible(b_number)
    if executed:
        logger.info("Repeat Save & Exit cycle executed for user1")
    else:
        logger.info("Repeat Save & Exit cycle skipped (B-number not visible to user1)")


@when("User verifies exact B-number match and clicks Run button")
def verify_exact_b_number_and_click_run(sdt_isc_page: SdtIscPage):
    """Verify exact searched B-number match and click the green Run button."""
    b_number = _get_b_number()
    logger.info(f"Verifying exact B-number '{b_number}' and clicking Run button")
    sdt_isc_page.verify_exact_b_number_and_click_run(b_number)


@when(parsers.parse('User selects "{option}" from the status dropdown'))
def select_internal_status_dropdown_option(sdt_isc_page: SdtIscPage, option: str):
    """Select an option from the status dropdown."""
    logger.info(f"Selecting '{option}' from the status dropdown")
    sdt_isc_page.select_status_dropdown(option)


@when("User clicks on D number checkbox")
def click_d_number_checkbox(sdt_isc_page: SdtIscPage):
    logger.info("Clicking D number checkbox")
    sdt_isc_page.click_d_number_checkbox()


@when("User clicks on ICT Activation checkbox")
def click_ict_activation_checkbox(sdt_isc_page: SdtIscPage):
    logger.info("Clicking ICT Activation checkbox")
    sdt_isc_page.click_ict_activation_checkbox()


@when("User clicks on Activate ICT button")
def click_activate_ict_button(sdt_isc_page: SdtIscPage):
    logger.info("Clicking Activate ICT button")
    sdt_isc_page.click_activate_ict_button()


@when("User clicks OK on Activation popup")
def click_ok_on_activation_popup(sdt_isc_page: SdtIscPage):
    logger.info("Clicking OK on Activation popup")
    sdt_isc_page.click_ok_on_activation_popup()


@when("User clicks Save & Exit button")
def click_save_and_exit(sdt_isc_page: SdtIscPage):
    logger.info("Clicking Save & Exit button")
    sdt_isc_page.click_save_and_exit()


@when("User clicks on Add/Update QC Reasons button")
def click_add_update_qc_reasons(sdt_isc_page: SdtIscPage):
    logger.info("Clicking Add/Update QC Reasons button")
    sdt_isc_page.click_add_update_qc_reasons()


@when(parsers.parse('User selects "{option}" from dropdown'))
def select_dropdown_option(sdt_isc_page: SdtIscPage, option: str):
    logger.info(f"Selecting '{option}' from dropdown")
    sdt_isc_page.select_dropdown_option(option)


@when("User clicks on Add button")
def click_add_button(sdt_isc_page: SdtIscPage):
    logger.info("Clicking Add button")
    sdt_isc_page.click_add_button()


@when("User clicks on Save button")
def click_qc_save_button(sdt_isc_page: SdtIscPage):
    logger.info("Clicking Save button on QC Reasons page")
    sdt_isc_page.click_qc_save_button()


@then(parsers.parse('QC Reason is added as "{expected_status}" in QC Reasons section'))
def verify_qc_reason_added(sdt_isc_page: SdtIscPage, expected_status: str):
    logger.info(f"Verifying QC Reason added as '{expected_status}' in QC Reasons section")
    sdt_isc_page.verify_qc_reason_verified(expected_status)


@when("User clicks on Return To Last User button in FollowUp and Ownership")
def click_return_to_last_user(sdt_isc_page: SdtIscPage):
    logger.info("Clicking 'Return To Last User' button in FollowUp and Ownership section")
    sdt_isc_page.click_return_to_last_user()
