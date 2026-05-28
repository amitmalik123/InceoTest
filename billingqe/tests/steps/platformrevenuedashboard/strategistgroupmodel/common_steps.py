"""SGM-specific fixture extensions built on top of Revenue Dashboard shared common steps."""

import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

_COMMON_STEP_DIR = Path(__file__).resolve().parents[1]
if str(_COMMON_STEP_DIR) not in sys.path:
    sys.path.insert(0, str(_COMMON_STEP_DIR))

from revenue_dashboard_common_steps import *  # noqa: F401,F403

from approve_reject_family_page import ApproveRejectFamilyPage
from create_family_page import CreateFamilyPage
from edit_family_page import EditFamilyPage
from edit_model_page import EditModelPage
from search_model_page import SearchModelPage


@pytest.fixture
def revenue_dashboard_subfolder() -> str:
    return "strategistgroupmodel"


@pytest.fixture
def create_family_page(page: Page) -> CreateFamilyPage:
    return CreateFamilyPage(page)


@pytest.fixture
def edit_family_page(page: Page) -> EditFamilyPage:
    return EditFamilyPage(page)


@pytest.fixture
def approve_reject_family_page(page: Page) -> ApproveRejectFamilyPage:
    return ApproveRejectFamilyPage(page)


@pytest.fixture
def search_model_page(page: Page) -> SearchModelPage:
    return SearchModelPage(page)


@pytest.fixture
def edit_model_page(page: Page) -> EditModelPage:
    return EditModelPage(page)
