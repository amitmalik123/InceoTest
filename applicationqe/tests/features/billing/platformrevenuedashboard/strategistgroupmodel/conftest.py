"""
Strategist Group Model (SGM) — conftest.py

All tests under tests/features/billing/platformrevenuedashboard/strategistgroupmodel/
inherit:
  - All Revenue Dashboard common fixtures + steps (via parent conftest)
  - SGM-specific page-object fixtures
  - SGM-specific step definitions

Adding a new Revenue Dashboard sub-module in the future?
  1. Create tests/features/billing/platformrevenuedashboard/<subfolder>/conftest.py
  2. Override `revenue_dashboard_subfolder` to return the subfolder name.
  3. Import the sub-module page objects and step files.
  4. Done — all shared login / navigation / hooks are inherited automatically.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]  # applicationqe/
_SGM_STEP_DIR = (
    _REPO_ROOT
    / "tests"
    / "steps"
    / "billing"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
)
_SGM_PAGE_DIR = (
    _REPO_ROOT
    / "pages"
    / "billing"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
)

for _p in [str(_REPO_ROOT), str(_SGM_STEP_DIR), str(_SGM_PAGE_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import Page

# ── Import fixtures from consolidated billing_fixture.py ────
from fixtures.billing_fixture import (  # noqa: F401
    browser_context_args,
    browser_type_launch_args,
    TestDataManager,
    csv_data_manager,
    soft_assert,
)

# ── Override the subfolder name so credentials/config load from the correct path ─
@pytest.fixture
def revenue_dashboard_subfolder() -> str:
    return "strategistgroupmodel"


# ── SGM page-object fixtures ──────────────────────────────────────────────────
from approve_reject_family_page import ApproveRejectFamilyPage
from create_family_page import CreateFamilyPage
from edit_family_page import EditFamilyPage
from search_model_page import SearchModelPage


@pytest.fixture
def approve_reject_family_page(page: Page) -> ApproveRejectFamilyPage:
    return ApproveRejectFamilyPage(page)


@pytest.fixture
def create_family_page(page: Page) -> CreateFamilyPage:
    return CreateFamilyPage(page)


@pytest.fixture
def edit_family_page(page: Page) -> EditFamilyPage:
    return EditFamilyPage(page)


@pytest.fixture
def search_model_page(page: Page) -> SearchModelPage:
    return SearchModelPage(page)


# ── SGM step definitions (re-exported so pytest-bdd picks them up) ───────────
# common_steps re-exports revenue_dashboard_common_steps (shared login/nav steps)
from common_steps import *  # noqa: F401,F403
from approve_reject_family_steps import *  # noqa: F401,F403
from create_family_steps import *  # noqa: F401,F403
from edit_family_steps import *  # noqa: F401,F403
from search_family_steps import *  # noqa: F401,F403
from search_model_steps import *  # noqa: F401,F403
