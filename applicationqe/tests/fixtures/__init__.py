"""Fixtures Module for the supported feature flows."""

# Assertion fixtures
from tests.fixtures.assertion_fixtures import reset_step_screenshot_counter, soft_assert

# Authentication fixtures
from tests.fixtures.auth_fixtures import authenticated_page, fresh_page, page

# Browser fixtures
from tests.fixtures.browser_fixtures import (
    browser_context_args,
    browser_type_launch_args,
    multi_user_contexts,
    new_context,
    new_page,
)

# Data fixtures
from tests.fixtures.data_fixtures import excel_data_manager, test_data_manager

# Database fixtures
from tests.fixtures.db_fixtures import db_manager

# Hooks (pytest-bdd lifecycle — no __all__ entry needed, just imported for side-effects)
from tests.fixtures.hooks_fixtures import (  # noqa: F401
    pytest_bdd_after_scenario,
    pytest_bdd_after_step,
    pytest_bdd_before_step,
    pytest_bdd_step_error,
)

# Page-object fixtures
from tests.fixtures.page_fixtures import (
    clients_page,
    document_vault_page,
    login_page,
    navbar_login_page,
    tracking_center_page,
)

__all__ = [
    # assertion
    "soft_assert",
    "reset_step_screenshot_counter",
    # auth
    "authenticated_page",
    "page",
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
    # pages
    "login_page",
    "clients_page",
    "navbar_login_page",
    "document_vault_page",
    "tracking_center_page",
]
