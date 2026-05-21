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
    pytest_bdd_after_step,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
)

# Page-object fixtures
from fixtures.page_fixtures import (
    account_detail_page,
    account_list_page,
    account_management_page,
    account_wizard_page,
    api_utility_page,
    global_navigation_page,
    login_page,
    proposal_page,
    prospects_list_page,
    smart_filter_page,
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
    "pytest_bdd_step_error",
    # pages
    "login_page",
    "global_navigation_page",
    "proposal_page",
    "prospects_list_page",
    "smart_filter_page",
    "account_list_page",
    "api_utility_page",
    "account_detail_page",
    "account_management_page",
    "account_wizard_page",
]
