"""
Page Object Fixtures

Provides fixtures for all page objects used in UI tests.
Each fixture creates a page object instance with the current Playwright page.
The base_url is injected from Settings so pages are environment-agnostic.
"""

import pytest
from playwright.sync_api import Page

from config.settings import get_settings

# ---------------------------------------------------------------------------
# Imports: OAM pages (not yet consolidated to EWM)
# ---------------------------------------------------------------------------
from pages.oam.client_accounts_page import ClientAccountsPage
from pages.oam.docusign_page import OAM_DocuSignPage
from pages.oam.item_detail_page import ItemDetailPage
from pages.outlook_page import OutlookPage

# ---------------------------------------------------------------------------
# Imports: EWM pages
# ---------------------------------------------------------------------------
from pages.ewm.account_approval_page import AccountApprovalPage
from pages.ewm.account_detail_page import AccountDetailPage
from pages.ewm.account_list_page import AccountListPage
from pages.ewm.account_setup_page import AccountSetupPage
from pages.ewm.account_wizard_page import AccountWizardPage
from pages.ewm.client_profile_page import ClientProfilePage
from pages.ewm.clients_page import ClientsPage
from pages.ewm.construct_portfolio_page import ConstructPortfolioPage
from pages.ewm.create_documents_page import CreateDocumentsPage
from pages.ewm.dashboard_page import DashboardPage
from pages.ewm.docusign_page import DocuSignPage
from pages.ewm.fees_page import FeesPage
from pages.ewm.login_page import LoginPage
from pages.ewm.lookup_page import LookupPage
from pages.ewm.navbar_login_page import NavbarLoginPage
from pages.ewm.portfolio_details_page import PortfolioDetailsPage
from pages.ewm.review_all_accounts_page import ReviewAllAccountsPage
from pages.ewm.tracking_center_page import TrackingCenterPage
from pages.ewm.view_documents_page import ViewDocumentsPage

# ---------------------------------------------------------------------------
# Imports: BAW pages
# ---------------------------------------------------------------------------
from pages.baw.baw_dashboard_page import BawDashboardPage
from pages.baw.baw_login_page import BawLoginPage
from pages.baw.naa_coach_page import NAACoachPage
from pages.baw.search_work_item_page import SearchWorkItemPage
from pages.baw.shell_process_page import ShellProcessPage

# ---------------------------------------------------------------------------
# Imports: PROPOSAL pages
# ---------------------------------------------------------------------------
from pages.proposal.ewm_page import EwmPage
from pages.proposal.login_page import LoginPage as ProposalLoginPage
from pages.proposal.new_account_wizard_page import NewAccountWizardPage
from pages.proposal.portfolio_engine_page import PortfolioEnginePage
from pages.proposal.switch_id_page import SwitchIDPage
from pages.proposal.tax_management_services_page import TaxManagementServicesPage

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_base_url = get_settings().base_url


# ---------------------------------------------------------------------------
# OAM fixtures (require base_url)
# ---------------------------------------------------------------------------

@pytest.fixture
def client_accounts_page(authenticated_page: Page) -> ClientAccountsPage:
    """Client accounts page object fixture"""
    return ClientAccountsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def trackingCenter_ItemDetail_page(authenticated_page: Page) -> ItemDetailPage:
    """Tracking center item detail page object fixture"""
    return ItemDetailPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def outlook_page(authenticated_page: Page) -> OutlookPage:
    """Outlook page object fixture for email-based OTP and signing workflows."""
    return OutlookPage.from_config(authenticated_page)


@pytest.fixture
def oam_docusign_page(authenticated_page: Page) -> OAM_DocuSignPage:
    """OAM DocuSign page object fixture (inherits all EWM methods)"""
    return OAM_DocuSignPage(authenticated_page, base_url=_base_url)


# ---------------------------------------------------------------------------
# EWM fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def login_page(authenticated_page: Page) -> LoginPage:
    """Login page object fixture"""
    return LoginPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def clients_page(authenticated_page: Page) -> ClientsPage:
    """Clients page object fixture"""
    return ClientsPage(authenticated_page)


@pytest.fixture
def account_list_page(authenticated_page: Page) -> AccountListPage:
    """Account list page object fixture"""
    return AccountListPage(authenticated_page)


@pytest.fixture
def account_detail_page(authenticated_page: Page) -> AccountDetailPage:
    """Account detail page object fixture"""
    return AccountDetailPage(authenticated_page)


@pytest.fixture
def account_wizard_page(page: Page):
    """Account wizard page object fixture"""
    return AccountWizardPage(page)


@pytest.fixture
def tracking_center_page(authenticated_page: Page) -> TrackingCenterPage:
    """Tracking center page object fixture (EWM version)"""
    return TrackingCenterPage(authenticated_page)


@pytest.fixture
def docusign_page(authenticated_page: Page) -> DocuSignPage:
    """DocuSign page object fixture (EWM)"""
    return DocuSignPage(authenticated_page)

@pytest.fixture
def navbar_login_page(page: Page):
    """Navbar login page object fixture"""
    return NavbarLoginPage(page)


@pytest.fixture
def dashboard_page(page: Page):
    """Dashboard page object fixture"""
    return DashboardPage(page)


@pytest.fixture
def client_profile_page(page: Page):
    """Client profile page object fixture"""
    return ClientProfilePage(page)


@pytest.fixture
def construct_portfolio_page(page: Page):
    """Construct portfolio page object fixture"""
    return ConstructPortfolioPage(page)


@pytest.fixture
def fees_page(page: Page):
    """Fees page object fixture"""
    return FeesPage(page)


@pytest.fixture
def portfolio_details_page(page: Page):
    """Portfolio details page object fixture"""
    return PortfolioDetailsPage(page)


@pytest.fixture
def account_setup_page(page: Page):
    """Account setup page object fixture"""
    return AccountSetupPage(page)


@pytest.fixture
def review_all_accounts_page(page: Page):
    """Review all accounts page object fixture"""
    return ReviewAllAccountsPage(page)


@pytest.fixture
def create_documents_page(page: Page):
    """Create documents page object fixture"""
    return CreateDocumentsPage(page)


@pytest.fixture
def view_documents_page(page: Page):
    """View documents page object fixture"""
    return ViewDocumentsPage(page)


@pytest.fixture
def lookup_page(page: Page):
    """Lookup page object fixture"""
    return LookupPage(page)


@pytest.fixture
def account_approval_page(page: Page):
    """Account Approval page object fixture"""
    return AccountApprovalPage(page)


# ---------------------------------------------------------------------------
# BAW fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def baw_login_page(page: Page):
    """BAW login page object fixture"""
    return BawLoginPage(page)


@pytest.fixture
def baw_dashboard_page(page: Page):
    """BAW dashboard page object fixture"""
    return BawDashboardPage(page)


@pytest.fixture
def shell_process_page(page: Page):
    """Shell process page object fixture"""
    return ShellProcessPage(page)


@pytest.fixture
def search_work_item_page(page: Page):
    """Search work item page object fixture"""
    return SearchWorkItemPage(page)


@pytest.fixture
def naa_coach_page(page: Page):
    """NAA coach page object fixture"""
    return NAACoachPage(page)


# ---------------------------------------------------------------------------
# PROPOSAL fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ewm_page(page: Page):
    """EWM main page object fixture (PROPOSAL)"""
    return EwmPage(page)


@pytest.fixture
def proposal_login_page(page: Page):
    """Login page object fixture (PROPOSAL)"""
    return ProposalLoginPage(page)


@pytest.fixture
def new_account_wizard_page(page: Page):
    """New Account Wizard page object fixture (PROPOSAL)"""
    return NewAccountWizardPage(page)


@pytest.fixture
def portfolio_engine_page(page: Page):
    """Portfolio Engine page object fixture (PROPOSAL)"""
    return PortfolioEnginePage(page)


@pytest.fixture
def switch_id_page(page: Page):
    """Switch ID page object fixture (PROPOSAL)"""
    return SwitchIDPage(page)


@pytest.fixture
def tax_management_services_page(page: Page):
    """Tax Management Services page object fixture (PROPOSAL)"""
    return TaxManagementServicesPage(page)
