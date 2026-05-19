# tests/steps/__init__.py

"""
Step definitions package for BDD tests.
Imports all step definition modules to make them discoverable by pytest-bdd.
"""

# Account steps
from tests.steps.account_steps import (
    search_for_client,
    select_client_account,
    verify_account_detail_page_loaded,
)

# Account wizard steps
from tests.steps.account_wizard_steps import (
    check_and_click_add_ach_instruction_link,
    click_next_on_account_wizard,
    click_on_account_wizard,
    pick_account_information_from_selected_account,
    select_funded_account_option,
    select_move_assets_between_accounts,
    select_roth_ira_conversion,
    verify_roth_conversion_page_loaded,
)

# API steps
from tests.steps.api_steps import validate_api_with_status_code

# Common steps
from tests.steps.common_steps import (
    logout_from_application,
    navigate_to_login_page,
    use_test_data_for_scenario,
    use_test_data_for_user_type,
    use_test_data_for_username,
    verify_logout_successful,
)

# Data steps
from tests.steps.data_steps import load_data_from_excel

# Database steps
from tests.steps.database_steps import (
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
from tests.steps.login_steps import login_with_valid_credentials, verify_redirect_to_home_page

# Navigation steps
from tests.steps.navigation_steps import (
    click_searched_account_and_navigate_to_wizard,
    verify_account_list_page_loaded,
    verify_account_list_page_loaded_and_search,
    verify_account_wizard_page_is_loaded,
)

# Account wizard steps (removed references to deleted ACH/Roth modules)

__all__ = [
    # account
    "search_for_client",
    "select_client_account",
    "verify_account_detail_page_loaded",
    # account wizard
    "click_on_account_wizard",
    "select_funded_account_option",
    "select_move_assets_between_accounts",
    "select_roth_ira_conversion",
    "click_next_on_account_wizard",
    "verify_roth_conversion_page_loaded",
    "pick_account_information_from_selected_account",
    "check_and_click_add_ach_instruction_link",
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
    "verify_account_list_page_loaded",
    "verify_account_list_page_loaded_and_search",
    "click_searched_account_and_navigate_to_wizard",
    "verify_account_wizard_page_is_loaded",
]
