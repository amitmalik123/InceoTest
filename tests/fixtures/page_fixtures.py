"""
Page Object Fixtures

Provides fixtures for all page objects used in UI tests.
Each fixture creates a page object instance with the current Playwright page.
The base_url is injected from Settings so pages are environment-agnostic.
"""

import pytest
from playwright.sync_api import Page

from config.settings import get_settings
from pages.account_detail_page import AccountDetailPage
from pages.account_list_page import AccountListPage
from pages.account_management_page import AccountManagementPage
from pages.account_wizard_page import AccountWizardPage
from pages.add_ach_instruction import AddACHInstructionPage
from pages.Adhesion.apro_proposals_page import AproProposalsPage
from pages.Adhesion.base_smart_filter_page import BaseSmartFilterPage
from pages.Adhesion.global_navigation_page import GlobalNavigationPage
from pages.Adhesion.prospects_list_page import ProspectsListPage
from pages.api_utility_page import APIUtilityPage
from pages.change_investments_page import ChangeInvestmentsPage
from pages.clients_page import ClientsPage
from pages.dmtool_page import DMToolPage
from pages.login_page import LoginPage
from pages.manage_instruction_1_page import ManageInstruction1Page
from pages.manage_instruction_2_page import ManageInstruction2Page
from pages.roth_conversion_page import RothConversionPage
from pages.tracking_center_page import TrackingCenterPage
from tests.fixtures.auth_fixtures import APP_CONFIGS

# Resolve base_url once from the active environment config
_base_url = get_settings().base_url


@pytest.fixture
def login_page(authenticated_page: Page, request) -> LoginPage:
    """Login page object fixture - returns correct login page based on app marker"""
    # Get app name from pytest marker (default to "ewm")
    marker = request.node.get_closest_marker("app")
    app_name = marker.args[0] if marker else "ewm"

    # Get the appropriate login page class from app config
    app_config = APP_CONFIGS.get(app_name)
    if app_config:
        return app_config.login_page_class(authenticated_page, base_url=_base_url)

    # Fallback to LoginPage if app config not found
    return LoginPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def clients_page(authenticated_page: Page) -> ClientsPage:
    """Clients page object fixture"""
    return ClientsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def global_navigation_page(authenticated_page: Page) -> GlobalNavigationPage:
    """Global navigation page object fixture"""
    return GlobalNavigationPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def prospects_list_page(authenticated_page: Page) -> ProspectsListPage:
    """APro prospects list page object fixture"""
    return ProspectsListPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def smart_filter_page(authenticated_page: Page) -> BaseSmartFilterPage:
    """Generic smart filter page fixture for reusable filter steps.

    Returns a BaseSmartFilterPage instance that can be used by generic smart filter
    step definitions across different pages (Prospects, Accounts, etc).
    """
    return BaseSmartFilterPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def proposal_page(authenticated_page: Page) -> AproProposalsPage:
    """APro proposal modal/page fixture"""
    return AproProposalsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def dmtool_page(authenticated_page: Page) -> DMToolPage:
    """DMTool page object fixture"""
    return DMToolPage(authenticated_page)


@pytest.fixture
def account_list_page(authenticated_page: Page) -> AccountListPage:
    """Account list page object fixture"""
    return AccountListPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def api_utility_page() -> APIUtilityPage:
    """
    API utility page object fixture.

    Note: This doesn't require a browser page as it's for API operations.
    """
    return APIUtilityPage()


@pytest.fixture
def account_detail_page(authenticated_page: Page) -> AccountDetailPage:
    """Account detail page object fixture"""
    return AccountDetailPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def account_wizard_page(authenticated_page: Page) -> AccountWizardPage:
    """Account wizard page object fixture"""
    return AccountWizardPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def manage_instruction_1_page(authenticated_page: Page) -> ManageInstruction1Page:
    """Manage instruction 1 page object fixture"""
    return ManageInstruction1Page(authenticated_page)


@pytest.fixture
def manage_instruction_2_page(authenticated_page: Page) -> ManageInstruction2Page:
    """Manage instruction 2 page object fixture"""
    return ManageInstruction2Page(authenticated_page)


@pytest.fixture
def add_ach_instruction_page(authenticated_page: Page) -> AddACHInstructionPage:
    """Add ACH instruction page object fixture"""
    return AddACHInstructionPage(authenticated_page)


@pytest.fixture
def roth_conversion_page(authenticated_page: Page) -> RothConversionPage:
    """Roth conversion page object fixture"""
    return RothConversionPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def change_investments_page(authenticated_page: Page) -> ChangeInvestmentsPage:
    """Change investments page object fixture"""
    return ChangeInvestmentsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def account_management_page(authenticated_page: Page) -> AccountManagementPage:
    """Account management page object fixture"""
    return AccountManagementPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def tracking_center_page(authenticated_page: Page) -> TrackingCenterPage:
    """Tracking center page object fixture"""
    return TrackingCenterPage(authenticated_page, base_url=_base_url)
