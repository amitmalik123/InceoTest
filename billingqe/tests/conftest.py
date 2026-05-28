"""Consolidated conftest.py for all billingqe tests.

Single conftest.py covering:
  - sys.path setup (billingqe root, all step/page dirs)
  - Browser and data fixture imports from modular fixtures/
  - BDD lifecycle hooks
  - Shared Revenue Dashboard step re-exports
  - SGM page-object fixtures
  - Test collection ordering
"""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

# ── sys.path: billingqe root + all step/page dirs ────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent  # billingqe/
_COMMON_STEP_DIR = _REPO_ROOT / "tests" / "steps" / "billing" / "platformrevenuedashboard"
_SGM_STEP_DIR = _COMMON_STEP_DIR / "strategistgroupmodel"
_SGM_PAGE_DIR = (
    _REPO_ROOT / "pages" / "billing" / "platformrevenuedashboard" / "strategistgroupmodel"
)

_REPO_ROOT_STR = str(_REPO_ROOT)
if _REPO_ROOT_STR in sys.path:
    sys.path.remove(_REPO_ROOT_STR)
sys.path.insert(0, _REPO_ROOT_STR)

# Prevent sibling repo from shadowing the tests package in multi-root workspaces
_SIBLING_ROOT = str(_REPO_ROOT.parent / "applicationqe")
if _SIBLING_ROOT in sys.path:
    sys.path.remove(_SIBLING_ROOT)

for _p in [str(_COMMON_STEP_DIR), str(_SGM_STEP_DIR), str(_SGM_PAGE_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── BDD lifecycle hooks ───────────────────────────────────────────────────────
from fixtures.hooks_fixtures import (  # noqa: F401
    pytest_bdd_before_scenario,
    pytest_bdd_after_scenario,
    pytest_bdd_before_step,
    pytest_bdd_after_step,
    pytest_bdd_step_error,
)

# ── Modular fixture imports ───────────────────────────────────────────────────
from fixtures.browser_fixtures import browser_context_args, browser_type_launch_args  # noqa: F401
from fixtures.data_fixtures import TestDataManager, csv_data_manager  # noqa: F401
from fixtures.assertion_fixtures import soft_assert  # noqa: F401
from fixtures.db_fixtures import db_helper, db_manager  # noqa: F401

# ── Revenue Dashboard step re-exports ────────────────────────────────────────
# import * is required so pytest-bdd discovers step fixture names with spaces.
from revenue_dashboard_common_steps import *  # noqa: F401,F403
from common_steps import *  # noqa: F401,F403
from approve_reject_family_steps import *  # noqa: F401,F403
from approve_reject_model_steps import *  # noqa: F401,F403
from create_family_steps import *  # noqa: F401,F403
from edit_family_steps import *  # noqa: F401,F403
from edit_model_steps import *  # noqa: F401,F403
from search_family_steps import *  # noqa: F401,F403
from search_model_steps import *  # noqa: F401,F403

# ── SGM page-object imports ───────────────────────────────────────────────────
from approve_reject_family_page import ApproveRejectFamilyPage
from approve_reject_model_page import ApproveRejectModelPage
from create_family_page import CreateFamilyPage
from edit_family_page import EditFamilyPage
from edit_model_page import EditModelPage
from search_model_page import SearchModelPage


# ── SGM page-object fixtures ──────────────────────────────────────────────────
@pytest.fixture
def revenue_dashboard_subfolder() -> str:
    return "strategistgroupmodel"


@pytest.fixture
def approve_reject_family_page(page: Page) -> ApproveRejectFamilyPage:
    return ApproveRejectFamilyPage(page)


@pytest.fixture
def approve_reject_model_page(page: Page) -> ApproveRejectModelPage:
    return ApproveRejectModelPage(page)


@pytest.fixture
def create_family_page(page: Page) -> CreateFamilyPage:
    return CreateFamilyPage(page)


@pytest.fixture
def edit_family_page(page: Page) -> EditFamilyPage:
    return EditFamilyPage(page)


@pytest.fixture
def search_model_page(page: Page) -> SearchModelPage:
    return SearchModelPage(page)


@pytest.fixture
def edit_model_page(page: Page) -> EditModelPage:
    return EditModelPage(page)


# ── General fixtures ──────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def vcr_config():
    """VCR configuration for recording HTTP interactions."""
    return {"filter_headers": ["authorization"]}


# ── Test collection ordering ──────────────────────────────────────────────────
def pytest_collection_modifyitems(config, items):
    """Order family-tagged SGM tests for deterministic workflow execution."""
    family_file_order = {
        "test_create_family_bdd_runner.py": 0,
        "test_approve_reject_family_bdd_runner.py": 1,
        "test_edit_family_bdd_runner.py": 2,
        "test_search_family_bdd_runner.py": 3,
    }

    family_items = []
    non_family_items = []

    for item in items:
        if item.get_closest_marker("family"):
            family_items.append(item)
        else:
            non_family_items.append(item)

    def _family_sort_key(test_item):
        file_name = Path(str(test_item.fspath)).name.lower()
        return (
            family_file_order.get(file_name, 999),
            str(test_item.fspath).lower(),
            test_item.name.lower(),
        )

    family_items.sort(key=_family_sort_key)
    items[:] = family_items + non_family_items
