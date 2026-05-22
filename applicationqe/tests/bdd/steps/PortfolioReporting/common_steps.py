from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from config.PortfolioReporting.settings import get_settings
from pages.PortfolioReporting.clients_page import ClientsPage
from pages.PortfolioReporting.lookup_page import LookupPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _excel_row(excel_data_manager, sheet_name: str, row_number: int) -> dict:
    if row_number < 2:
        raise ValueError(
            f"Invalid RowNumber '{row_number}' for sheet '{sheet_name}'. "
            "Use Excel row numbers starting at 2 (first data row)."
        )
    return excel_data_manager.get_row(sheet_name, row_number - 2)


def _first_non_empty(row_data: dict, keys: list[str]) -> str | None:
    for key in keys:
        value = row_data.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return None


# ============================================================================
# Scalable Multi-User Data Access Steps
# ============================================================================


@given(parsers.parse('I am using test data for scenario "{scenario_name}"'))
def use_test_data_for_scenario(test_context, test_data_manager, scenario_name):
    """
    Load test data by scenario name - NO NEED TO KNOW ROW INDEX!

    Example:
        Given I am using test data for scenario "add_ach"
        Given I am using test data for scenario "roth_conversion"
    """
    user_data = test_data_manager.get_by(test_scenario=scenario_name)

    if not user_data:
        raise ValueError(
            f"No test data found for scenario '{scenario_name}'. "
            f"Available scenarios: {test_data_manager.get_scenarios()}"
        )

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for scenario: {scenario_name}")
    logger.attach_json(user_data, f"Test Data - {scenario_name}")


@given(parsers.parse('I am using test data for user type "{user_type}"'))
def use_test_data_for_user_type(test_context, test_data_manager, user_type):
    """
    Load test data by user type - NO NEED TO KNOW ROW INDEX!

    Example:
        Given I am using test data for user type "advisor"
        Given I am using test data for user type "client"
    """
    user_data = test_data_manager.get_by(user_type=user_type)

    if not user_data:
        raise ValueError(
            f"No test data found for user type '{user_type}'. "
            f"Available user types: {test_data_manager.get_user_types()}"
        )

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for user type: {user_type}")
    logger.attach_json(user_data, f"Test Data - {user_type}")


@given(parsers.parse('I am using test data for username "{username}"'))
def use_test_data_for_username(test_context, test_data_manager, username):
    """
    Load test data by username.

    Example:
        Given I am using test data for username "T11_User2_Test"
    """
    user_data = test_data_manager.get_by(username=username)

    if not user_data:
        raise ValueError(f"Username '{username}' not found in test data CSV")

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for username: {username}")
    logger.attach_json(user_data, f"Test Data - {username}")


# ============================================================================
# Standard Steps
# ============================================================================


@given("I am on the login page")
def navigate_to_login_page(page: Page, login_page):
    """
    Verification step - Does NOT navigate to login page

    This step ONLY verifies that the page is ready.
    The page fixture already handles authentication, so we should NOT be on login page.

    This step is kept for backward compatibility but does nothing in practice.
    """
    logger.info("Verifying page is ready (authentication already handled by fixture)")
    # No action needed - page fixture already authenticated
    # If we're still on login page, the page fixture will handle it


@given("I logout from the application")
def logout_from_application(page: Page, tracking_center_page):
    """Logout from the application"""
    logger.info("Logging out from application")
    tracking_center_page.click_logout()
    tracking_center_page.click_bodycontent()


@then("I should be logged out successfully")
def verify_logout_successful():
    """Verify successful logout"""
    logger.info("=== Test Completed Successfully ===", attach_to_allure=False)


@given(parsers.parse('User should login to the application and impersonate into an agent "{agent_id}"'))
def login_and_impersonate_agent(authenticated_page, agent_id: str):
    """
    Ensure login as admin, then impersonate into an agent using the Switch ID lookup.

    Example:
        Given User should login to the application and impersonate into an agent "AG1634"
    """
    logger.info(f"Logging in as admin and impersonating agent: {agent_id}")

    # Ensure we are logged in as admin (authenticated_page fixture should use admin credentials)
    current_url = authenticated_page.url or ""
    if "login" in current_url.lower():
        raise AssertionError("Admin user is not authenticated. Current page is login page.")

    lookup_page = LookupPage(authenticated_page)
    lookup_page.impersonate_agent(agent_id)

    # Some environments intermittently land on about:blank after Switch ID.
    # Recover by navigating back to app home URL before downstream page actions.
    current_url = authenticated_page.url or ""
    if current_url.startswith("about:blank"):
        settings = get_settings()
        home_url = settings.get_app_config("ewm").get("home_url", settings.base_url)
        logger.info(f"Recovered from about:blank after impersonation, navigating to {home_url}")
        authenticated_page.goto(home_url, timeout=30000)
        authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)

    logger.info(f"Impersonation completed for agent: {agent_id}")


@given(
    parsers.parse(
        'User should login to the application and impersonate into an agent "{sheet_name}" , {row_number:d}'
    )
)
def login_and_impersonate_agent_from_excel(
    authenticated_page, excel_data_manager, test_context, sheet_name: str, row_number: int
):
    row_data = _excel_row(excel_data_manager, sheet_name, row_number)
    test_context["excel_row_data"] = row_data

    agent_id = _first_non_empty(row_data, ["UserName", "Username", "Agentid", "AgentId"])
    if not agent_id:
        raise ValueError(
            f"Could not resolve agent id from Excel sheet '{sheet_name}' row {row_number}. "
            "Expected one of columns: UserName, Username, Agentid, AgentId"
        )

    logger.info(
        f"Using Excel row for login - Sheet: {sheet_name}, Row: {row_number}, Agent: {agent_id}"
    )
    login_and_impersonate_agent(authenticated_page, agent_id)


# ============================================================================
# New NavBar Steps
# ============================================================================


@when("Login application")
def login_application(authenticated_page: Page, test_context: dict):
    """
    Login to the new navbar application using credentials from test data.
    The authenticated_page fixture yields a fresh unauthenticated page for
    @newNavBar scenarios - NavbarLoginPage handles the actual login.
    """
    from pages.PortfolioReporting.navbar_login_page import NavbarLoginPage

    test_data = test_context.get("test_data", {})
    username = test_data.get("username") or test_data.get("UserName")
    password = test_data.get("password") or test_data.get("Password")

    if not username or not password:
        raise ValueError(
            "Missing credentials in test data. "
            "Expected 'username'/'password' or 'UserName'/'Password' columns."
        )

    logger.info(f"Logging in to navbar application as: {username}")
    navbar_login_page = NavbarLoginPage(authenticated_page)
    navbar_login_page.login_application(username, password)


@when("User clicks on the clients tab")
def click_clients_tab(authenticated_page: Page):
    """
    Click on the Clients tab in the new navbar flow.
    Used in new navbar scenario flows.
    """
    logger.info("Clicking on the Clients tab")
    # Keep the stabilization short so the click happens as soon as the tab is visible.
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=5000)
    authenticated_page.wait_for_timeout(250)
    settings = get_settings()
    base_url = settings.base_url
    clients_page = ClientsPage(authenticated_page, base_url=base_url)
    clients_page.click_clients()
    logger.info("Clients tab clicked successfully")
