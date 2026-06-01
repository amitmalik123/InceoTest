"""
Page Object Fixtures

Provides fixtures for all page objects used in UI tests.
Each fixture creates a page object instance with the current Playwright page.
"""
from pathlib import Path
import sys

import pytest
from playwright.sync_api import Page

# ---------------------------------------------------------------------------
# Path setup — hyphenated STP page dirs cannot use Python dot-notation imports
# ---------------------------------------------------------------------------
_APP_ROOT = Path(__file__).resolve().parents[2]  # .../applicationqe/
_PAGE_DIRS = [
    "pages/stp/stp_addACHIntrcutions",
    "pages/stp/stp_updateAddress",
    "pages/stp/stp_mimotransactionpage",
    "pages/stp/stp_swp",
    "pages/stp/stp_oaTradingTool",
    "pages/stp/stp_manageBene",
    "pages/stp/stp_aip",
    "pages/stp/stp_aip/stp_cancelAip",
    "pages/stp/stp_aip/stp_establishAip",
]
for _d in _PAGE_DIRS:
    _p = str(_APP_ROOT / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Shared pages (non-hyphenated, standard import)
from pages.stp.shared.account_detail_page import AccountDetailPage
from pages.stp.shared.account_list_page import AccountListPage
from pages.stp.shared.account_wizard_page import AccountWizardPage
from pages.stp.shared.api_utility_page import APIUtilityPage
from pages.stp.shared.clients_page import ClientsPage
from pages.stp.shared.docusign_page import DocuSignPage
from pages.stp.shared.esign_signer_information_page import ESignSignerInformationPage
from pages.stp.shared.item_details_page import ItemDetailsPage
from pages.stp.shared.login_page import LoginPage
from pages.stp.shared.manage_instruction_1_page import ManageInstruction1Page
from pages.stp.shared.manage_instruction_2_page import ManageInstruction2Page
from pages.stp.shared.new_nav_wrapper_page import NewNavWrapperPage
from pages.stp.shared.privacy_and_security_policy_page import PrivacyAndSecurityPolicyPage
from pages.stp.shared.supported_browsers_page import SupportedBrowsersPage
from pages.stp.shared.terms_of_use_page import TermsOfUsePage
from pages.stp.shared.tracking_center_page import TrackingCenterPage
from pages.ewm.roth_conversion_page import RothConversionPage

# Pages from hyphenated dirs (imported via sys.path above)
from add_ach_confirmation_page import AddACHConfirmationPage  # stp_addACHIntrcutions
from add_ach_instruction import AddACHInstructionPage  # stp_addACHIntrcutions
from add_ach_summary_page import AddACHSummaryPage  # stp_addACHIntrcutions
from dm_tool_address_edit_modal import DMToolAddressEditModal  # stp_updateAddress
from dm_tool_usps_modal import DMToolUSPSModal  # stp_updateAddress
from dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage  # stp_updateAddress
from dmtool_page import DMToolPage  # stp_updateAddress
from mimo_confirmation_page import MIMOConfirmationPage  # stp_mimotransactionpage
from mimo_transaction_request_page import MIMOTransactionRequestPage  # stp_mimotransactionpage
from mimo_transaction_request_page2 import MIMOTransactionRequestPage2  # stp_mimotransactionpage
from mimo_transaction_summary_page import MIMOTransactionSummaryPage  # stp_mimotransactionpage
from withdrawal_method_modal_page import WithdrawalMethodModalPage  # stp_swp
from withdrawal_signature_not_required_modal_page import WithdrawalSignatureNotRequiredModalPage  # stp_swp
from swp_establish_landing_page import SWPEstablishLandingPage  # stp_swp
from swp_establish_transaction_page_one import SWPEstablishTransactionPageOne  # stp_swp
from swp_establish_transaction_page_two import SWPEstablishTransactionPageTwo  # stp_swp
from swp_establish_confirmation_page import SWPEstablishConfirmationPage  # stp_swp
from oa_tool_landing_page import OAToolLandingPage  # stp_oaTradingTool
from oa_tool_transaction_page import OAToolTransactionPage  # stp_oaTradingTool
from update_beneficiary_page import UpdateBeneficiaryPage  # stp_manageBene
from manage_bene_detail_page import ManageBeneDetailPage  # stp_manageBene
from add_beneficiary_page import AddBeneficiaryPage  # stp_manageBene
from manage_bene_page import ManageBenePage  # stp_manageBene
from edit_beneficiary_page import EditBeneficiaryPage  # stp_manageBene
from manage_bene_esignature_page import ManageBeneESignaturePage  # stp_manageBene
from manage_bene_review_page import ManageBeneReviewPage  # stp_manageBene
from deceased_bene_page import DeceasedBenePage  # stp_manageBene
from cancel_aip_page import CancelAIPPage  # stp_aip
from establish_aip_landing_page import EstablishAIPLandingPage  # stp_aip
from establish_aip_origination_selection_page import EstablishAIPOriginationSelectionPage  # stp_aip
from establish_aip_add_aip_page import EstablishAIPAddAIPPage  # stp_aip
from establish_aip_summary_page import EstablishAIPSummaryPage  # stp_aip
from establish_aip_confirmation_page import EstablishAIPConfirmationPage  # stp_aip
from establish_aip_common_page import EstablishAIPCommonPage  # stp_aip

@pytest.fixture
def login_page(page: Page):
    """Login page object fixture"""
    return LoginPage(page)


@pytest.fixture
def clients_page(page: Page):
    """Clients page object fixture"""
    return ClientsPage(page)


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
def account_list_page(page: Page):
    """Account list page object fixture"""
    return AccountListPage(page)


@pytest.fixture
def api_utility_page():
    """
    API utility page object fixture.

    Note: This doesn't require a browser page as it's for API operations.
    """
    return APIUtilityPage()


@pytest.fixture
def account_detail_page(page: Page):
    """Account detail page object fixture"""
    return AccountDetailPage(page)


@pytest.fixture
def account_wizard_page(page: Page):
    """Account wizard page object fixture"""
    return AccountWizardPage(page)


@pytest.fixture
def manage_instruction_1_page(page: Page):
    """Manage instruction 1 page object fixture"""
    return ManageInstruction1Page(page)


@pytest.fixture
def manage_instruction_2_page(page: Page):
    """Manage instruction 2 page object fixture"""
    return ManageInstruction2Page(page)


@pytest.fixture
def add_ach_instruction_page(page: Page):
    """Add ACH instruction page object fixture"""
    return AddACHInstructionPage(page)


@pytest.fixture
def roth_conversion_page(page: Page):
    """Roth conversion page object fixture"""
    return RothConversionPage(page)


@pytest.fixture
def tracking_center_page(page: Page):
    """Tracking center page object fixture"""
    return TrackingCenterPage(page)


@pytest.fixture
def add_ach_summary_page(page: Page):
    """Add ACH summary page object fixture"""
    return AddACHSummaryPage(page)


@pytest.fixture
def add_ach_confirmation_page(page: Page):
    """Add ACH confirmation page object fixture"""
    return AddACHConfirmationPage(page)


@pytest.fixture
def item_details_page(page: Page):
    """Item details page object fixture"""
    return ItemDetailsPage(page, page_verification=False)


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


@pytest.fixture
def supported_browsers_page(page: Page):
    """Supported Browsers Page object fixture"""
    return SupportedBrowsersPage(page)


@pytest.fixture
def privacy_and_security_policy_page(page: Page):
    """Privacy and Security Policy Page object fixture"""
    return PrivacyAndSecurityPolicyPage(page)


@pytest.fixture
def terms_of_use_page(page: Page):
    """Terms of Use Page object fixture"""
    return TermsOfUsePage(page)


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
def new_nav_wrapper_page(page: Page):
    """New Nav Wrapper Page object fixture for iframe handling"""
    return NewNavWrapperPage(page)


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
def esign_signer_information_page(page: Page):
    """eSign Signer Information page object fixture (inside #esig_iframe)"""
    return ESignSignerInformationPage(page)


@pytest.fixture
def docusign_page(page: Page):
    """DocuSign page object fixture"""
    return DocuSignPage(page)
