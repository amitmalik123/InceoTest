"""
Page Object Fixtures

Provides fixtures for all page objects used in UI tests.
Each fixture creates a page object instance with the current Playwright page.
"""

import pytest
from playwright.sync_api import Page

from pages.account_detail_page import AccountDetailPage
from pages.account_list_page import AccountListPage
from pages.account_wizard_page import AccountWizardPage
from pages.add_ach_confirmation_page import AddACHConfirmationPage
from pages.add_ach_instruction import AddACHInstructionPage
from pages.add_ach_summary_page import AddACHSummaryPage
from pages.api_utility_page import APIUtilityPage
from pages.clients_page import ClientsPage
from pages.dm_tool_address_edit_modal import DMToolAddressEditModal
from pages.dm_tool_usps_modal import DMToolUSPSModal
from pages.dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage
from pages.dmtool_page import DMToolPage
from pages.item_details_page import ItemDetailsPage
from pages.login_page import LoginPage
from pages.manage_instruction_1_page import ManageInstruction1Page
from pages.manage_instruction_2_page import ManageInstruction2Page
from pages.mimo_confirmation_page import MIMOConfirmationPage
from pages.mimo_transaction_request_page import MIMOTransactionRequestPage
from pages.mimo_transaction_request_page2 import MIMOTransactionRequestPage2
from pages.mimo_transaction_summary_page import MIMOTransactionSummaryPage
from pages.roth_conversion_page import RothConversionPage
from pages.tracking_center_page import TrackingCenterPage
from pages.withdrawal_signature_not_required_modal_page import WithdrawalSignatureNotRequiredModalPage
from pages.swp_establish_landing_page import SWPEstablishLandingPage
from pages.swp_establish_transaction_page_one import SWPEstablishTransactionPageOne
from pages.swp_establish_transaction_page_two import SWPEstablishTransactionPageTwo
from pages.swp_establish_confirmation_page import SWPEstablishConfirmationPage
from pages.oa_tool_landing_page import OAToolLandingPage
from pages.oa_tool_transaction_page import OAToolTransactionPage
from pages.new_nav_wrapper_page import NewNavWrapperPage
from pages.update_beneficiary_page import UpdateBeneficiaryPage
from pages.manage_bene_detail_page import ManageBeneDetailPage
from pages.add_beneficiary_page import AddBeneficiaryPage
from pages.manage_bene_page import ManageBenePage
from pages.edit_beneficiary_page import EditBeneficiaryPage
from pages.manage_bene_esignature_page import ManageBeneESignaturePage
from pages.manage_bene_review_page import ManageBeneReviewPage
from pages.deceased_bene_page import DeceasedBenePage
from pages.docusign_page import DocuSignPage
from pages.esign_signer_information_page import ESignSignerInformationPage


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
    from pages.withdrawal_method_modal_page import WithdrawalMethodModalPage
    return WithdrawalMethodModalPage(page)


@pytest.fixture
def cancel_aip_page(page: Page):
    """Cancel AIP page object fixture"""
    from pages.cancel_aip_page import CancelAIPPage
    return CancelAIPPage(page)


@pytest.fixture
def establish_aip_landing_page(page: Page):
    """Establish AIP Landing Page object fixture"""
    from pages.establish_aip_landing_page import EstablishAIPLandingPage
    return EstablishAIPLandingPage(page)


@pytest.fixture
def establish_aip_origination_selection_page(page: Page):
    """Establish AIP Origination Selection Page object fixture"""
    from pages.establish_aip_origination_selection_page import EstablishAIPOriginationSelectionPage
    return EstablishAIPOriginationSelectionPage(page)


@pytest.fixture
def establish_aip_add_aip_page(page: Page):
    """Establish AIP Add AIP Page object fixture"""
    from pages.establish_aip_add_aip_page import EstablishAIPAddAIPPage
    return EstablishAIPAddAIPPage(page)


@pytest.fixture
def establish_aip_summary_page(page: Page):
    """Establish AIP Summary Page object fixture"""
    from pages.establish_aip_summary_page import EstablishAIPSummaryPage
    return EstablishAIPSummaryPage(page)


@pytest.fixture
def establish_aip_confirmation_page(page: Page):
    """Establish AIP Confirmation Page object fixture"""
    from pages.establish_aip_confirmation_page import EstablishAIPConfirmationPage
    return EstablishAIPConfirmationPage(page)


@pytest.fixture
def establish_aip_common_page(page: Page):
    """Establish AIP Common Page object fixture"""
    from pages.establish_aip_common_page import EstablishAIPCommonPage
    return EstablishAIPCommonPage(page)


@pytest.fixture
def supported_browsers_page(page: Page):
    """Supported Browsers Page object fixture"""
    from pages.supported_browsers_page import SupportedBrowsersPage
    return SupportedBrowsersPage(page)


@pytest.fixture
def privacy_and_security_policy_page(page: Page):
    """Privacy and Security Policy Page object fixture"""
    from pages.privacy_and_security_policy_page import PrivacyAndSecurityPolicyPage
    return PrivacyAndSecurityPolicyPage(page)


@pytest.fixture
def terms_of_use_page(page: Page):
    """Terms of Use Page object fixture"""
    from pages.terms_of_use_page import TermsOfUsePage
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
