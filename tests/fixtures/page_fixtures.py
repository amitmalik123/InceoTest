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
from pages.api_utility_page import APIUtilityPage
from pages.change_investments_page import ChangeInvestmentsPage
from pages.clients_page import ClientsPage
from pages.dmtool_page import DMToolPage
from pages.login_page import LoginPage
from pages.manage_instruction_1_page import ManageInstruction1Page
from pages.navbar_login_page import NavbarLoginPage
from pages.manage_instruction_2_page import ManageInstruction2Page
from pages.roth_conversion_page import RothConversionPage
from pages.tracking_center_page import TrackingCenterPage

# Resolve base_url once from the active environment config
_base_url = get_settings().base_url


@pytest.fixture
def login_page(authenticated_page: Page) -> LoginPage:
    """Login page object fixture"""
    return LoginPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def navbar_login_page(authenticated_page: Page) -> NavbarLoginPage:
    """Navbar login page object fixture"""
    return NavbarLoginPage(authenticated_page)


@pytest.fixture
def clients_page(authenticated_page: Page) -> ClientsPage:
    """Clients page object fixture"""
    return ClientsPage(authenticated_page, base_url=_base_url)


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
