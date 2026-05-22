"""SGM-specific fixture extensions built on top of Revenue Dashboard shared common steps."""

import pytest
from playwright.sync_api import Page

from tests.steps.billing.platformrevenuedashboard.revenue_dashboard_common_steps import *  # noqa: F401,F403

from approve_reject_family_page import ApproveRejectFamilyPage
from create_family_page import CreateFamilyPage
from edit_family_page import EditFamilyPage
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
