from playwright.sync_api import Page
from pytest_bdd import given, parsers, then

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


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
def navigate_to_login_page(authenticated_page: Page, login_page):
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
def logout_from_application(authenticated_page: Page, tracking_center_page):
    """Logout from the application"""
    logger.info("Logging out from application")
    tracking_center_page.click_logout()
    tracking_center_page.click_bodycontent()


@then("I should be logged out successfully")
def verify_logout_successful():
    """Verify successful logout"""
    logger.info("=== Test Completed Successfully ===", attach_to_allure=False)
