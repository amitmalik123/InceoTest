"""
BDD step definitions for Change Investments E2E flow.

Steps cover:
  - Login and navigation to account list
  - Account search and selection
  - Navigating to holding page
  - Client management ΓåÆ Change Investments
  - Investment selection and destination investment validation
  - New investment modal validation
"""

from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from pages.account_list_page import AccountListPage
from pages.change_investments_page import ChangeInvestmentsPage
from pages.clients_page import ClientsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


# ------------------------------------------------------------------
# Given: Login
# ------------------------------------------------------------------


@given("User login into ewm application on test11 environment")
def user_login_into_ewm_application(authenticated_page: Page, test_context: dict):
    """
    Verify the user is authenticated on the eWealthManager application.
    The `authenticated_page` fixture handles session storage / auto-login.
    """
    current_url = authenticated_page.url
    logger.info(f"Verifying login status - Current URL: {current_url}")
    if current_url and "login" not in current_url.lower():
        logger.info("User is already authenticated (session storage)")
        return
    error_msg = "AUTHENTICATION FAILED: User is not logged in on test11."
    logger.error(error_msg)
    raise AssertionError(error_msg)


# ------------------------------------------------------------------
# When: Navigation to Account List
# ------------------------------------------------------------------


@when("User should click on clients tab and navigate to account list page")
def click_clients_tab_and_navigate_to_account_list(
    authenticated_page: Page,
    clients_page: ClientsPage,
):
    """Click on the Clients tab and then navigate to the Account List."""
    logger.info("Navigating to Clients menu")
    clients_page.navigate()
    clients_page.click_clients()
    logger.info("Clicking Account List")
    clients_page.click_account_list()
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    logger.info("Account List page loaded")


# ------------------------------------------------------------------
# And: Search account
# ------------------------------------------------------------------


@when("User is on the accountlist tab and search with the account")
def search_with_account(
    authenticated_page: Page,
    account_list_page: AccountListPage,
    test_context: dict,
):
    """Search for the client account using the client_id from test data."""
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Searching for client: {client_id}")
    account_list_page.search_client(client_id)
    logger.info(f"Search completed for client: {client_id}")


# ------------------------------------------------------------------
# And: Click on searched account ΓåÆ holding page
# ------------------------------------------------------------------


@when(parsers.parse('User should click on searched account and navigate to account "{tab}" page'))
def click_searched_account_and_navigate_to_tab(
    authenticated_page: Page,
    account_list_page: AccountListPage,
    change_investments_page: ChangeInvestmentsPage,
    test_context: dict,
    tab: str,
):
    """Select the account from search results and navigate to the holding page."""
    account_name = test_context["test_data"]["account_name"]
    client_id = test_context["test_data"]["client_id"]
    logger.info(f"Selecting account: {account_name} (tab: {tab})")
    account_list_page.select_account(account_name, client_id)
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    change_investments_page.verify_on_holding_page()
    logger.info(f"Navigated to account {tab} page")


# ------------------------------------------------------------------
# And: Click on client management option ΓåÆ Change Investments
# ------------------------------------------------------------------


@when(parsers.parse('Click on client management option "{option_name}"'))
def click_client_management_option(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    option_name: str,
):
    """Open Client Management dropdown and click the specified option."""
    logger.info(f"Clicking client management option: {option_name}")
    change_investments_page.click_client_management_option(option_name)
    logger.info(f"'{option_name}' selected from Client Management")


# ------------------------------------------------------------------
# And: Click on account number ΓåÆ investment selection tab
# ------------------------------------------------------------------


@when("Click on account number and navigate to investment selection tab")
def click_account_number_navigate_to_investment_selection(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click the account number link to navigate to the investment selection tab."""
    logger.info("Clicking account number to navigate to investment selection tab")
    change_investments_page.click_account_number_investment_selection()
    logger.info("On investment selection tab")


# ------------------------------------------------------------------
# Then: Validate account number on destination investment tab
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# When: Select new investment
# ------------------------------------------------------------------


@when("Select new investment on destination investment tab")
def select_new_investment(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click 'Select New Investment' button on the destination investment tab."""
    logger.info("Selecting new investment on destination investment tab")
    change_investments_page.select_new_investment()
    logger.info("New investment selected")


# ------------------------------------------------------------------
# Then: Validate New Investment Modal
# ------------------------------------------------------------------


@then("Validate New Investment Modal")
def validate_new_investment_modal(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Validate the New Investment modal/dialog is displayed."""
    logger.info("Validating New Investment modal")
    change_investments_page.validate_new_investment_modal()
    logger.info("New Investment modal validated successfully")


# ------------------------------------------------------------------
# When: Select investment strategy
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# And: Select investment profile
# ------------------------------------------------------------------


@when(parsers.parse('User selects investment profile "{profile_name}"'))
def user_selects_investment_profile(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
    profile_name: str,
):
    """Select specific investment profile from the grid."""
    logger.info(f"Selecting investment profile: {profile_name}")
    change_investments_page.select_investment_profile(profile_name)
    logger.info(f"Investment profile '{profile_name}' selected")


# ------------------------------------------------------------------
# And: Confirm investment selection
# ------------------------------------------------------------------


@when("User confirms investment selection")
def user_confirms_investment_selection(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Click OK to confirm the investment selection."""
    logger.info("Confirming investment selection")
    change_investments_page.confirm_investment_selection()
    logger.info("Investment selection confirmed")


# ------------------------------------------------------------------
# And: Select allocation option
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# And: Click next buttons
# ------------------------------------------------------------------


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
    """Click Next button to complete the process."""
    logger.info("Clicking Next to complete")
    change_investments_page.click_next_button()
    logger.info("Process completion step executed")


# ------------------------------------------------------------------
# And: Risk assessment selections
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# Then: Validate completion
# ------------------------------------------------------------------


@then("Investment change should be completed successfully")
def investment_change_completed_successfully(
    authenticated_page: Page,
    change_investments_page: ChangeInvestmentsPage,
):
    """Validate that the investment change completed successfully."""
    logger.info("Validating investment change completion")
    change_investments_page.validate_investment_change_completed()
    logger.info("Investment change validated as completed successfully")
