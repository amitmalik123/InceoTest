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
    user_navigate_to_clients_menu,
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

# Client accounts steps
from tests.bdd.steps.client_accounts_steps import (
    select_authorized_signer_approval_option,
    verify_signer_information_dialog_exists_with_correct_information,
    verify_authorized_signer_approval_section,
    verify_fields_for_esign_method,
    verify_authorized_signer_esign_method_section,
    user_select_signer_esign_method,
    provide_authorized_signers_information,
    verify_authorized_signer_dropdown,
    click_continue_button,
    verify_account_number_displayed_and_radio_selected,
    user_select_oam_request_and_type,
    verify_form_heading_matches_oam_type,
    user_select_submission_type,
    user_select_client_signature_method,
    verify_client_signature_not_required_dialog,
    verify_request_dialog,
    user_click_on_d_number,
    verify_client_in_person_signing_dialog_displayed,
    user_click_on_form_button_dynamic,
    user_provide_client_signature_details,
)

# DocuSign steps
from tests.bdd.steps.docusign_steps import (
    user_confirm_and_continue,
    user_finish_the_docusign_process,
    user_should_be_redirected_to_docusign_page,
    verify_as_authorized_by_stamp_presence,
    verify_docusign_review_and_continue_dialog_text,
    user_add_signature,
    verify_signature_and_date_added_on_document,
    user_click_on_send_now_and_fetch_otp_from_mail,
)

# Outlook steps
from tests.bdd.steps.outlook_steps import (
    fetch_otp_from_outlook,
    user_login_to_the_email_and_search_the_authorized_signer_email,
    fetch_authorized_signer_email_subject_and_body_step,
    user_login_to_the_email_and_complete_the_workflow_approver_signature,
    user_login_to_the_email_and_fetch_the_latest_otp,
    user_verifies_carbon_copy_received_in_email,
    user_click_on_review_document_link_in_authorized_signer_email,
)

# Tracking center steps
from tests.bdd.steps.tracking_center_steps import (
    navigate_to_tracking_center,
    verify_roth_conversion_entry_exists,
    verify_text_in_tracking_details,
)

# Item detail steps
from tests.bdd.steps.item_detail_steps import (
    verify_item_detail_d_number_matches_request_submitted_pop_up_d_number,
    verify_tracking_center_item_detail_status,
    verify_buttons_displayed,
    verify_notes_description,
    verify_advisor_alert_required_value,
    verify_redirected_to_tracking_center_item_detail_page,
    verify_agent_name,
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
    # client accounts
    "select_authorized_signer_approval_option",
    "verify_signer_information_dialog_exists_with_correct_information",
    "verify_authorized_signer_approval_section",
    "verify_fields_for_esign_method",
    "verify_authorized_signer_esign_method_section",
    "user_select_signer_esign_method",
    "provide_authorized_signers_information",
    "verify_authorized_signer_dropdown",
    "click_continue_button",
    "verify_account_number_displayed_and_radio_selected",
    "user_select_oam_request_and_type",
    "verify_form_heading_matches_oam_type",
    "user_select_submission_type",
    "user_select_client_signature_method",
    "verify_client_signature_not_required_dialog",
    "verify_request_dialog",
    "user_click_on_d_number",
    "verify_client_in_person_signing_dialog_displayed",
    "user_click_on_form_button_dynamic",
    "user_provide_client_signature_details",
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
    # docusign
    "user_confirm_and_continue",
    "user_finish_the_docusign_process",
    "user_should_be_redirected_to_docusign_page",
    "verify_as_authorized_by_stamp_presence",
    "verify_docusign_review_and_continue_dialog_text",
    "user_add_signature",
    "verify_signature_and_date_added_on_document",
    "user_click_on_send_now_and_fetch_otp_from_mail",
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
    "user_navigate_to_clients_menu",
    "click_on_account_list",
    "verify_account_list_page_loaded",
    "verify_account_list_page_loaded_and_search",
    "click_searched_account_and_navigate_to_wizard",
    "verify_account_wizard_page_is_loaded",
    # outlook
    "fetch_otp_from_outlook",
    "user_login_to_the_email_and_search_the_authorized_signer_email",
    "fetch_authorized_signer_email_subject_and_body_step",
    "user_login_to_the_email_and_complete_the_workflow_approver_signature",
    "user_login_to_the_email_and_fetch_the_latest_otp",
    "user_verifies_carbon_copy_received_in_email",
    "user_click_on_review_document_link_in_authorized_signer_email",
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
    # tracking center item detail
    "verify_item_detail_d_number_matches_request_submitted_pop_up_d_number",
    "verify_tracking_center_item_detail_status",
    "verify_buttons_displayed",
    "verify_notes_description",
    "verify_advisor_alert_required_value",
    "verify_redirected_to_tracking_center_item_detail_page",
    "verify_agent_name",
]
