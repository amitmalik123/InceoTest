"""
Fixtures Module

This module consolidates all test fixtures and makes them discoverable by pytest.
All fixtures are re-exported from their specialized modules for easy importing.
"""

# Assertion fixtures
from fixtures.assertion_fixtures import reset_step_screenshot_counter, soft_assert

# Authentication fixtures
from fixtures.auth_fixtures import authenticated_page, fresh_page

# Browser fixtures
from fixtures.browser_fixtures import (
    browser_context_args,
    browser_type_launch_args,
    multi_user_contexts,
    new_context,
    new_page,
)

# Data fixtures
from fixtures.data_fixtures import excel_data_manager, test_data_manager

# Database fixtures
from fixtures.db_fixtures import db_manager

# Hooks (pytest-bdd lifecycle — no __all__ entry needed, just imported for side-effects)
from fixtures.hooks_fixtures import (  # noqa: F401
    pytest_bdd_after_scenario,
    pytest_bdd_after_step,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
)

# Page-object fixtures
from fixtures.page_fixtures import (
    account_detail_page,
    account_list_page,
    account_wizard_page,
    account_approval_page,
    account_setup_page,
    baw_dashboard_page,
    baw_login_page,
    client_accounts_page,
    client_profile_page,
    clients_page,
    construct_portfolio_page,
    create_documents_page,
    dashboard_page,
    docusign_page,
    ewm_page,
    fees_page,
    login_page,
    lookup_page,
    naa_coach_page,
    navbar_login_page,
    new_account_wizard_page,
    oam_docusign_page,
    outlook_page,
    portfolio_details_page,
    portfolio_engine_page,
    proposal_login_page,
    review_all_accounts_page,
    search_work_item_page,
    shell_process_page,
    switch_id_page,
    tax_management_services_page,
    tracking_center_page,
    trackingCenter_ItemDetail_page,
    view_documents_page,
)

__all__ = [
    # assertion
    "soft_assert",
    "reset_step_screenshot_counter",
    # auth
    "authenticated_page",
    "fresh_page",
    # browser
    "browser_context_args",
    "browser_type_launch_args",
    "new_context",
    "new_page",
    "multi_user_contexts",
    # data
    "test_data_manager",
    "excel_data_manager",
    # database
    "db_manager",
    # hooks
    "pytest_bdd_before_step",
    "pytest_bdd_after_step",
    "pytest_bdd_after_scenario",
    "pytest_bdd_step_error",
    # pages - OAM/EWM/BAW/PROPOSAL
    "account_approval_page",
    "account_detail_page",
    "account_list_page",
    "account_setup_page",
    "account_wizard_page",
    "baw_dashboard_page",
    "baw_login_page",
    "client_accounts_page",
    "client_profile_page",
    "clients_page",
    "construct_portfolio_page",
    "create_documents_page",
    "dashboard_page",
    "docusign_page",
    "ewm_page",
    "fees_page",
    "login_page",
    "lookup_page",
    "naa_coach_page",
    "navbar_login_page",
    "new_account_wizard_page",
    "oam_docusign_page",
    "outlook_page",
    "portfolio_details_page",
    "portfolio_engine_page",
    "proposal_login_page",
    "review_all_accounts_page",
    "search_work_item_page",
    "shell_process_page",
    "switch_id_page",
    "tax_management_services_page",
    "tracking_center_page",
    "trackingCenter_ItemDetail_page",
    "view_documents_page",
    # data
    "test_data_manager",
    "excel_data_manager",
    # database
    "db_manager",
    # hooks
    "pytest_bdd_before_step",
    "pytest_bdd_after_step",
    "pytest_bdd_after_scenario",
    "pytest_bdd_step_error",
    # pages - OAM/EWM/BAW/PROPOSAL
    "account_approval_page",
    "account_detail_page",
    "account_list_page",
    "account_setup_page",
    "account_wizard_page",
    "baw_dashboard_page",
    "baw_login_page",
    "client_accounts_page",
    "client_profile_page",
    "clients_page",
    "construct_portfolio_page",
    "create_documents_page",
    "dashboard_page",
    "docusign_page",
    "ewm_page",
    "fees_page",
    "login_page",
    "lookup_page",
    "naa_coach_page",
    "navbar_login_page",
    "new_account_wizard_page",
    "oam_docusign_page",
    "outlook_page",
    "portfolio_details_page",
    "portfolio_engine_page",
    "proposal_login_page",
    "review_all_accounts_page",
    "search_work_item_page",
    "shell_process_page",
    "switch_id_page",
    "tax_management_services_page",
    "tracking_center_page",
    "trackingCenter_ItemDetail_page",
    "view_documents_page",
]
