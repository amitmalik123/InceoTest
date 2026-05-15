"""
Page Object Fixtures

Provides fixtures for all page objects used in UI tests.
Each fixture creates a page object instance with the current Playwright page.
The base_url is injected from Settings so pages are environment-agnostic.
"""

import pytest
from playwright.sync_api import Page

from config.oam.settings import get_settings
from pages.oam.account_detail_page import AccountDetailPage
from pages.oam.account_list_page import AccountListPage
from pages.oam.account_management_page import AccountManagementPage
from pages.oam.account_wizard_page import AccountWizardPage
from pages.oam.add_ach_instruction import AddACHInstructionPage
from pages.oam.api_utility_page import APIUtilityPage
from pages.oam.change_investments_page import ChangeInvestmentsPage
from pages.oam.client_accounts_page import ClientAccountsPage
from pages.oam.clients_page import ClientsPage
from pages.oam.docusign_page import DocuSignPage
from pages.oam.dmtool_page import DMToolPage
from pages.oam.login_page import LoginPage
from pages.oam.outlook_page import OutlookPage
from pages.oam.manage_instruction_1_page import ManageInstruction1Page
from pages.oam.manage_instruction_2_page import ManageInstruction2Page
from pages.oam.roth_conversion_page import RothConversionPage
from pages.oam.tracking_center_page import TrackingCenterPage
from pages.oam.item_detail_page import ItemDetailPage

# Resolve base_url once from the active environment config
_base_url = get_settings().base_url


@pytest.fixture
def login_page(authenticated_page: Page) -> LoginPage:
    """Login page object fixture"""
    return LoginPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def clients_page(authenticated_page: Page) -> ClientsPage:
    """Clients page object fixture"""
    return ClientsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def client_accounts_page(authenticated_page: Page) -> ClientAccountsPage:
    """Client accounts page object fixture"""
    return ClientAccountsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def dmtool_page(authenticated_page: Page) -> DMToolPage:
    """DMTool page object fixture"""
    return DMToolPage(authenticated_page)


@pytest.fixture
def docusign_page(authenticated_page: Page) -> DocuSignPage:
    """DocuSign page object fixture"""
    return DocuSignPage(authenticated_page, base_url=_base_url)


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


@pytest.fixture
def tracking_center_item_detail_page(authenticated_page: Page) -> ItemDetailPage:
    """Tracking center item detail page object fixture"""
    return ItemDetailPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def trackingCenter_ItemDetail_page(authenticated_page: Page) -> ItemDetailPage:
    """Tracking center item detail page object fixture (camelCase alias)"""
    return ItemDetailPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def outlook_page(authenticated_page: Page) -> OutlookPage:
    """Outlook page object fixture for email-based workflows.
    
    This fixture creates an OutlookPage instance initialized from configuration,
    used for OTP retrieval and email-based signing workflows.
    """
    return OutlookPage.from_config(authenticated_page)
