# tests/bdd/steps/__init__.py

"""
Step definitions package for BDD tests.
Imports all step definition modules to make them discoverable by pytest-bdd.
"""

# API steps
from tests.bdd.steps.api_steps import validate_api_with_status_code

# Common steps
from tests.bdd.steps.common_steps import (
    logout_from_application,
    navigate_to_login_page,
    use_test_data_for_scenario,
    use_test_data_for_user_type,
    use_test_data_for_username,
    verify_logout_successful,
)

# Data steps
from tests.bdd.steps.data_steps import load_data_from_excel

# Database steps
from tests.bdd.steps.database_steps import (
    verify_account_distribution_in_database,
    verify_account_in_database,
    verify_am_billing_accounts_data_from_database,
    verify_database_contains_minimum_records,
    verify_database_contains_records,
    verify_database_with_query,
    verify_retirement_billing_client_in_database,
    verify_transfer_status_exists,
    verify_transfer_status_in_database,
)

# Login steps
from tests.bdd.steps.login_steps import login_with_valid_credentials, verify_redirect_to_home_page

# Navigation steps
from tests.bdd.steps.navigation_steps import (
    click_on_account_list,
    click_searched_account_and_navigate_to_wizard,
    navigate_to_clients_menu,
    verify_account_list_page_loaded,
    verify_account_list_page_loaded_and_search,
    verify_account_wizard_page_is_loaded,
)

__all__ = [
    # api
    "validate_api_with_status_code",
    # common
    "use_test_data_for_scenario",
    "use_test_data_for_user_type",
    "use_test_data_for_username",
    "navigate_to_login_page",
    "logout_from_application",
    "verify_logout_successful",
    # data
    "load_data_from_excel",
    # database
    "verify_database_with_query",
    "verify_retirement_billing_client_in_database",
    "verify_am_billing_accounts_data_from_database",
    "verify_transfer_status_in_database",
    "verify_account_distribution_in_database",
    "verify_account_in_database",
    "verify_database_contains_records",
    "verify_transfer_status_exists",
    "verify_database_contains_minimum_records",
    # login
    "login_with_valid_credentials",
    "verify_redirect_to_home_page",
    # navigation
    "navigate_to_clients_menu",
    "click_on_account_list",
    "verify_account_list_page_loaded",
    "verify_account_list_page_loaded_and_search",
    "click_searched_account_and_navigate_to_wizard",
    "verify_account_wizard_page_is_loaded",
]
