# tests/bdd/steps/__init__.py

"""
Step definitions package for BDD tests.
Imports all step definition modules to make them discoverable by pytest-bdd.
"""

# Account steps
from tests.bdd.steps.account_steps import (
    search_for_client,
    select_client_account,
    verify_account_detail_page_loaded,
)

# Account wizard steps
from tests.bdd.steps.account_wizard_steps import (
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

# Manage instruction steps
from tests.bdd.steps.manage_instruction_steps import (
    click_next_button_on_add_ach_page,
    click_on_add_button,
    enter_valid_ains_page_details,
    fetch_client_household_api_values,
    fetch_household_id,
    select_radio_and_click_on_next,
    validate_household_heading,
)

# Navigation steps
from tests.bdd.steps.navigation_steps import (
    click_on_account_list,
    click_searched_account_and_navigate_to_wizard,
    navigate_to_clients_menu,
    verify_account_list_page_loaded,
    verify_account_list_page_loaded_and_search,
    verify_account_wizard_page_is_loaded,
)

# Roth conversion steps
from tests.bdd.steps.roth_conversion_steps import (
    click_next_on_conversion_details,
    click_next_on_destination_selection,
    enter_conversion_amount,
    handle_str_review_or_proceed,
    select_convert_portion_option,
    select_destination_account,
    select_do_not_withhold_taxes,
    verify_destination_account_correct,
)

# Tracking center steps
from tests.bdd.steps.tracking_center_steps import (
    navigate_to_tracking_center,
    verify_roth_conversion_entry_exists,
    verify_text_in_tracking_details,
)

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
    # manage instruction
    "select_radio_and_click_on_next",
    "click_on_add_button",
    "fetch_household_id",
    "fetch_client_household_api_values",
    "enter_valid_ains_page_details",
    "validate_household_heading",
    "click_next_button_on_add_ach_page",
    # navigation
    "navigate_to_clients_menu",
    "click_on_account_list",
    "verify_account_list_page_loaded",
    "verify_account_list_page_loaded_and_search",
    "click_searched_account_and_navigate_to_wizard",
    "verify_account_wizard_page_is_loaded",
    # roth conversion
    "select_destination_account",
    "verify_destination_account_correct",
    "click_next_on_destination_selection",
    "select_convert_portion_option",
    "enter_conversion_amount",
    "select_do_not_withhold_taxes",
    "click_next_on_conversion_details",
    "handle_str_review_or_proceed",
    # tracking center
    "navigate_to_tracking_center",
    "verify_roth_conversion_entry_exists",
    "verify_text_in_tracking_details",
]
