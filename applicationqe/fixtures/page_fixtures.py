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
from pages.ewm.manage_instruction_1_page import ManageInstruction1Page
from pages.ewm.manage_instruction_2_page import ManageInstruction2Page
from pages.ewm.navbar_login_page import NavbarLoginPage
from pages.ewm.new_nav_wrapper_page import NewNavWrapperPage
from pages.ewm.portfolio_details_page import PortfolioDetailsPage
from pages.ewm.privacy_and_security_policy_page import PrivacyAndSecurityPolicyPage
from pages.ewm.review_all_accounts_page import ReviewAllAccountsPage
from pages.ewm.supported_browsers_page import SupportedBrowsersPage
from pages.ewm.terms_of_use_page import TermsOfUsePage
from pages.ewm.tracking_center_page import TrackingCenterPage
from pages.ewm.view_documents_page import ViewDocumentsPage
from tests.api.stp.services.stp_api_service import STPApiService
from pages.ewm.esign_signer_information_page import ESignSignerInformationPage
from pages.ewm.item_details_page import ItemDetailsPage

# ---------------------------------------------------------------------------
# Imports: STP pages
# ---------------------------------------------------------------------------
# stp_updateAddress
from pages.stp.stp_updateAddress.dm_tool_address_edit_modal import DMToolAddressEditModal
from pages.stp.stp_updateAddress.dm_tool_usps_modal import DMToolUSPSModal
from pages.stp.stp_updateAddress.dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage
from pages.stp.stp_updateAddress.dmtool_page import DMToolPage
# stp_addACHIntrcutions
from pages.stp.stp_addACHIntrcutions.add_ach_confirmation_page import AddACHConfirmationPage
from pages.stp.stp_addACHIntrcutions.add_ach_instruction import AddACHInstructionPage
from pages.stp.stp_addACHIntrcutions.add_ach_summary_page import AddACHSummaryPage
# stp_mimotransactionpage
from pages.stp.stp_mimotransactionpage.mimo_confirmation_page import MIMOConfirmationPage
from pages.stp.stp_mimotransactionpage.mimo_transaction_request_page import MIMOTransactionRequestPage
from pages.stp.stp_mimotransactionpage.mimo_transaction_request_page2 import MIMOTransactionRequestPage2
from pages.stp.stp_mimotransactionpage.mimo_transaction_summary_page import MIMOTransactionSummaryPage
# stp_swp
from pages.stp.stp_swp.withdrawal_method_modal_page import WithdrawalMethodModalPage
from pages.stp.stp_swp.withdrawal_signature_not_required_modal_page import WithdrawalSignatureNotRequiredModalPage
from pages.stp.stp_swp.swp_establish_landing_page import SWPEstablishLandingPage
from pages.stp.stp_swp.swp_establish_transaction_page_one import SWPEstablishTransactionPageOne
from pages.stp.stp_swp.swp_establish_transaction_page_two import SWPEstablishTransactionPageTwo
from pages.stp.stp_swp.swp_establish_confirmation_page import SWPEstablishConfirmationPage
# stp_oaTradingTool
from pages.stp.stp_oaTradingTool.oa_tool_landing_page import OAToolLandingPage
from pages.stp.stp_oaTradingTool.oa_tool_transaction_page import OAToolTransactionPage
# stp_manageBene
from pages.stp.stp_manageBene.update_beneficiary_page import UpdateBeneficiaryPage
from pages.stp.stp_manageBene.manage_bene_detail_page import ManageBeneDetailPage
from pages.stp.stp_manageBene.add_beneficiary_page import AddBeneficiaryPage
from pages.stp.stp_manageBene.manage_bene_page import ManageBenePage
from pages.stp.stp_manageBene.edit_beneficiary_page import EditBeneficiaryPage
from pages.stp.stp_manageBene.manage_bene_esignature_page import ManageBeneESignaturePage
from pages.stp.stp_manageBene.manage_bene_review_page import ManageBeneReviewPage
from pages.stp.stp_manageBene.deceased_bene_page import DeceasedBenePage
# stp_aip
from pages.stp.stp_aip.stp_cancelAip.cancel_aip_page import CancelAIPPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_landing_page import EstablishAIPLandingPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_origination_selection_page import EstablishAIPOriginationSelectionPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_add_aip_page import EstablishAIPAddAIPPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_summary_page import EstablishAIPSummaryPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_confirmation_page import EstablishAIPConfirmationPage
from pages.stp.stp_aip.stp_establishAip.establish_aip_common_page import EstablishAIPCommonPage

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


# ---------------------------------------------------------------------------
# Appended fixtures: migrated from STP shared to EWM
# Kept at end to reduce merge conflicts in frequently edited sections.
# ---------------------------------------------------------------------------

@pytest.fixture
def api_utility_page() -> STPApiService:
    """STP API service fixture."""
    return STPApiService()


@pytest.fixture
def item_details_page(page: Page) -> ItemDetailsPage:
    """Item details page object fixture."""
    return ItemDetailsPage(page, page_verification=False)


@pytest.fixture
def manage_instruction_1_page(page: Page) -> ManageInstruction1Page:
    """Manage instruction 1 page object fixture."""
    return ManageInstruction1Page(page)


@pytest.fixture
def manage_instruction_2_page(page: Page) -> ManageInstruction2Page:
    """Manage instruction 2 page object fixture."""
    return ManageInstruction2Page(page)


@pytest.fixture
def supported_browsers_page(page: Page) -> SupportedBrowsersPage:
    """Supported Browsers page object fixture."""
    return SupportedBrowsersPage(page)


@pytest.fixture
def privacy_and_security_policy_page(page: Page) -> PrivacyAndSecurityPolicyPage:
    """Privacy and Security Policy page object fixture."""
    return PrivacyAndSecurityPolicyPage(page)


@pytest.fixture
def terms_of_use_page(page: Page) -> TermsOfUsePage:
    """Terms of Use page object fixture."""
    return TermsOfUsePage(page)


@pytest.fixture
def new_nav_wrapper_page(page: Page) -> NewNavWrapperPage:
    """New Nav Wrapper page object fixture for iframe handling."""
    return NewNavWrapperPage(page)


@pytest.fixture
def esign_signer_information_page(page: Page) -> ESignSignerInformationPage:
    """eSign Signer Information page object fixture."""
    return ESignSignerInformationPage(page)


# ---------------------------------------------------------------------------
# STP fixtures (migrated from fixtures/stp/page_fixtures.py)
# ---------------------------------------------------------------------------

@pytest.fixture
def roth_conversion_page(page: Page):
    """Roth conversion page object fixture"""
    return RothConversionPage(page)


@pytest.fixture
def dm_tool_page(page: Page):
    """DMTool page object fixture"""
    return DMToolPage(page)


@pytest.fixture
def dm_tool_address_edit_modal(page: Page):
    """DMTool Address Edit Modal page object fixture"""
    return DMToolAddressEditModal(page)


@pytest.fixture
def dm_tool_usps_modal(page: Page):
    """DMTool USPS Modal page object fixture"""
    return DMToolUSPSModal(page)


@pytest.fixture
def dmt_address_change_confirmation_page(page: Page):
    """DMT Address Change Confirmation page object fixture"""
    return DMTAddressChangeConfirmationPage(page)


@pytest.fixture
def add_ach_instruction_page(page: Page):
    """Add ACH instruction page object fixture"""
    return AddACHInstructionPage(page)


@pytest.fixture
def add_ach_summary_page(page: Page):
    """Add ACH summary page object fixture"""
    return AddACHSummaryPage(page)


@pytest.fixture
def add_ach_confirmation_page(page: Page):
    """Add ACH confirmation page object fixture"""
    return AddACHConfirmationPage(page)


@pytest.fixture
def mimo_transaction_page(page: Page):
    """MIMO transaction request page object fixture"""
    return MIMOTransactionRequestPage(page)


@pytest.fixture
def mimo_transaction_page2(page: Page):
    """MIMO transaction request page 2 object fixture"""
    return MIMOTransactionRequestPage2(page)


@pytest.fixture
def mimo_summary_page(page: Page):
    """MIMO transaction summary page object fixture"""
    return MIMOTransactionSummaryPage(page)


@pytest.fixture
def mimo_confirmation_page(page: Page):
    """MIMO confirmation page object fixture"""
    return MIMOConfirmationPage(page)


@pytest.fixture
def withdrawal_signature_modal_page(page: Page):
    """Withdrawal signature not required modal page object fixture"""
    return WithdrawalSignatureNotRequiredModalPage(page)


@pytest.fixture
def withdrawal_method_modal_page(page: Page):
    """Withdrawal method modal page object fixture"""
    return WithdrawalMethodModalPage(page)


@pytest.fixture
def swp_establish_landing_page(page: Page):
    """SWP Establish Landing Page object fixture"""
    return SWPEstablishLandingPage(page)


@pytest.fixture
def swp_establish_transaction_page_one(page: Page):
    """SWP Establish Transaction Page One object fixture"""
    return SWPEstablishTransactionPageOne(page)


@pytest.fixture
def swp_establish_transaction_page_two(page: Page):
    """SWP Establish Transaction Page Two object fixture"""
    return SWPEstablishTransactionPageTwo(page)


@pytest.fixture
def swp_establish_confirmation_page(page: Page):
    """SWP Establish Confirmation Page object fixture"""
    return SWPEstablishConfirmationPage(page)


@pytest.fixture
def oa_tool_landing_page(page: Page):
    """OA Tool Landing Page object fixture"""
    return OAToolLandingPage(page)


@pytest.fixture
def oa_tool_transaction_page(page: Page):
    """OA Tool Transaction Page object fixture"""
    return OAToolTransactionPage(page)


@pytest.fixture
def update_beneficiary_page(page: Page):
    """Update/Manage Beneficiaries page object fixture"""
    return UpdateBeneficiaryPage(page)


@pytest.fixture
def add_beneficiary_page(page: Page):
    """Add Beneficiary modal page object fixture"""
    return AddBeneficiaryPage(page)


@pytest.fixture
def manage_bene_detail_page(page: Page):
    """Manage Beneficiary Detail page object fixture"""
    return ManageBeneDetailPage(page)


@pytest.fixture
def add_beneficiary_buttons_page(page: Page):
    """Add Beneficiary buttons page object fixture (Save/Don't Save)"""
    return AddBeneficiaryPage(page)


@pytest.fixture
def manage_bene_page(page: Page):
    """Manage Beneficiaries page object fixture"""
    return ManageBenePage(page)


@pytest.fixture
def edit_beneficiary_page(page: Page):
    """Edit Beneficiary inline form page object fixture"""
    return EditBeneficiaryPage(page)


@pytest.fixture
def manage_bene_esignature_page(page: Page):
    """Manage Beneficiary e-Signature Details page object fixture"""
    return ManageBeneESignaturePage(page)


@pytest.fixture
def manage_bene_review_page(page: Page):
    """Manage Beneficiary Review page object fixture"""
    return ManageBeneReviewPage(page)


@pytest.fixture
def deceased_bene_page(page: Page):
    """Deceased account Manage Beneficiaries landing page object fixture"""
    return DeceasedBenePage(page)


@pytest.fixture
def cancel_aip_page(page: Page):
    """Cancel AIP page object fixture"""
    return CancelAIPPage(page)


@pytest.fixture
def establish_aip_landing_page(page: Page):
    """Establish AIP Landing Page object fixture"""
    return EstablishAIPLandingPage(page)


@pytest.fixture
def establish_aip_origination_selection_page(page: Page):
    """Establish AIP Origination Selection Page object fixture"""
    return EstablishAIPOriginationSelectionPage(page)


@pytest.fixture
def establish_aip_add_aip_page(page: Page):
    """Establish AIP Add AIP Page object fixture"""
    return EstablishAIPAddAIPPage(page)


@pytest.fixture
def establish_aip_summary_page(page: Page):
    """Establish AIP Summary Page object fixture"""
    return EstablishAIPSummaryPage(page)


@pytest.fixture
def establish_aip_confirmation_page(page: Page):
    """Establish AIP Confirmation Page object fixture"""
    return EstablishAIPConfirmationPage(page)


@pytest.fixture
def establish_aip_common_page(page: Page):
    """Establish AIP Common Page object fixture"""
    return EstablishAIPCommonPage(page)
