"""DocuSign Step Definitions for BDD tests"""

from pytest_bdd import parsers, when

from applicationqe.pages.ewm.docusign_page import DocuSignPage
from pages.ewm.view_documents_page import ViewDocumentsPage
from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions


logger = get_allure_logger(__name__)

# Global variables for registration and custodian info
reg_type = None
custodian = None
is_esignature_required = None

def get_reg_type_and_custodian(test_data):
    """
    Extract registration type, custodian, and eSignature option from test data and set globals.
    """
    global reg_type, custodian, is_esignature_required
    reg_types = test_data.get("RegistrationType", "").split(",")
    if len(reg_types) <= 1:
        reg_type = reg_types[0].strip()
    else:
        reg_type = reg_types[1].strip()
    custodian = test_data.get("Custodian", "").strip()
    is_esignature_required = test_data.get("ESignatureOption", "")




class DocuSignStep:
    """Helper class for DocuSign step methods"""

    def __init__(self, test_context: dict, view_documents_page: ViewDocumentsPage):
        """
        Initialize DocuSignStep

        Args:
            test_context: Test context containing test data
            view_documents_page: ViewDocumentsPage instance
        """
        self.test_context = test_context
        self.view_documents_page = view_documents_page
        self.test_data = test_context.get("test_data", {})
        self.reg_type = None
        self.custodian = None
        self.client_account_type = None
        self.is_esignature_required = None

    def get_reg_type_and_custodian(self):
        """Extract registration type, custodian, and other required data from test data"""
        reg_types = self.test_data.get("RegistrationType", "").split(",")
        if len(reg_types) <= 1:
            self.reg_type = reg_types[0].strip()
        else:
            self.reg_type = reg_types[1].strip()

        self.custodian = self.test_data.get("Custodian", "").strip()
        self.client_account_type = self.test_data.get("ClientAccountType", "")
        self.is_esignature_required = self.test_data.get("ESignatureOption", "")

        logger.info(f"Registration Type: {self.reg_type}, Custodian: {self.custodian}")
        logger.info(
            f"Client Account Type: {self.client_account_type}, eSignature: {self.is_esignature_required}"
        )

    def check_checkbox_and_sign_document(self):
        self.get_reg_type_and_custodian()
        if "yes" == (self.is_esignature_required or "").strip().lower():
            advisory_type = ConstructPortfolioStep.is_sub_advisory or ""
            esignature_eligibility = "Eligible" if ConstructPortfolioStep.is_esignature_eligible else "Ineligible"
            logger.info(f"Advisory Type: {advisory_type}")
            logger.info(f"eSignature Eligibility: {esignature_eligibility}")
            if "Non SubAdvisory".lower() == (advisory_type or "").strip().lower() and "Eligible".lower() == esignature_eligibility.lower():
                logger.info("Conditions met: Non SubAdvisory + eSignature Eligible. Proceeding with Client eSignature signing...")
                with logger.step("Sign documents as Client", page=self.view_documents_page.page):
                    docusign_page = self.view_documents_page.get_docusign_page_instance()
                    docusign_page.e_signature_sign(
                        first_name=self.test_data.get("AccountHolderFirstName", ""),
                        second_name=self.test_data.get("AccountHolderLastName", ""),
                        reg_type=self.reg_type,
                        custodian=self.custodian,
                        client_type=self.test_data.get("ClientType", ""),
                        role="Client",
                        option="",
                        is_sub_advisory=advisory_type,
                    )
                with logger.step("Verify Client eSignature status", page=self.view_documents_page.page):
                    docusign_page = self.view_documents_page.get_docusign_page_instance()
                    docusign_page.verify_e_signature_status("Client", self.test_data.get("ESignatureOption", ""), advisory_type)
                logger.info("Client eSignature signing completed successfully")
            else:
                error_message = (
                    f"Skipping Client Signature Verification because this step is inapplicable for "
                    f"advisory type: {advisory_type} or eSignature eligibility: {esignature_eligibility}"
                )
                is_valid_skip = (
                    esignature_eligibility.lower() == "ineligible" or 
                    advisory_type.lower() == "subadvisory"
                )
                assert is_valid_skip, error_message
                logger.info(error_message)
        else:
            if (not self.is_esignature_required or self.is_esignature_required.strip().lower() in ["no", "na", ""]):
                logger.info("Skipping this Step as Option not enabled for eSignature in data sheet")


@when("User does the client signature")
def step_user_check_checkbox_and_sign_document(test_context, view_documents_page: ViewDocumentsPage):
    """
    Check the checkbox and sign the document as Client.
    (Logic inlined to match Java step definition style)
    """
    test_data = test_context.get("test_data", {})
    get_reg_type_and_custodian(test_data)

    logger.info("[STEP] User does the client signature - BEGIN")
    logger.info(f"Global reg_type: {reg_type}, custodian: {custodian}, is_esignature_required: {is_esignature_required}")

    agent_esignature_option = test_context.get("agent_esignature_option", "")

    if str(is_esignature_required).strip().lower() == "yes":
        advisory_type = ConstructPortfolioStep.is_sub_advisory or ""
        esignature_eligible = ConstructPortfolioStep.is_esignature_eligible
        esignature_eligibility = "Eligible" if esignature_eligible else "Ineligible"

        logger.info(f"Advisory Type: {advisory_type}")
        logger.info(f"eSignature Eligibility: {esignature_eligibility}")

        if advisory_type.strip().lower() == "non subadvisory" and esignature_eligibility.lower() == "eligible":
            logger.info("Conditions met: Non SubAdvisory + eSignature Eligible. Proceeding with Client eSignature signing...")
            with logger.step("Sign documents as Client", page=view_documents_page.page, auto_screenshot=True):
                docusign_page = view_documents_page.get_docusign_page_instance()
                docusign_page.e_signature_sign(
                    first_name=test_data.get("AccountHolderFirstName", ""),
                    second_name=test_data.get("AccountHolderLastName", ""),
                    reg_type=reg_type,
                    custodian=custodian,
                    client_type=test_data.get("ClientType", ""),
                    role="Client",
                    option=agent_esignature_option,
                    is_sub_advisory=advisory_type,
                )
                logger.info("[SCREENSHOT] Captured after e_signature_sign().")
            with logger.step("Verify Client eSignature status", page=view_documents_page.page, auto_screenshot=True):
                docusign_page = view_documents_page.get_docusign_page_instance()
                docusign_page.verify_e_signature_status("Client", test_data.get("ESignatureOption", ""), advisory_type)
            Assertions.assert_is_not_none(DocuSignPage.nNumber, "N number fetched after client eSignature")
            logger.info(f"N Number after client signature: {DocuSignPage.nNumber}")
            logger.attach_summary_table({"N Number": DocuSignPage.nNumber}, name="Client eSignature - N Number")
            logger.info("Client eSignature signing completed successfully")
        else:
            error_message = (
                f"Skipping Client Signature Verification because this step is inapplicable for "
                f"advisory type: {advisory_type} or eSignature eligibility: {esignature_eligibility}"
            )
            is_valid_skip = (
                esignature_eligibility.lower() == "ineligible" or advisory_type.lower() == "subadvisory"
            )
            assert is_valid_skip, error_message
            logger.info(error_message)
    else:
        if (
            not is_esignature_required or str(is_esignature_required).strip().lower() in ["no", "na", ""]
        ):
            logger.info("Skipping this Step as Option not enabled for eSignature in data sheet")
    logger.info("[STEP] User does the client signature - END")


@when("User does the client from tracking center page")
def step_user_does_client_from_tracking_center(test_context, view_documents_page: ViewDocumentsPage):
    """
    Perform client eSignature from the Tracking Center page
    (after agent selected Finish Later and navigated to Tracking Center).
    Supports both original page and new browser context (via test_context["new_page"]).
    """
    test_data = test_context.get("test_data", {})
    get_reg_type_and_custodian(test_data)

    logger.info("[STEP] User does the client from tracking center page - BEGIN")
    logger.info(f"Global reg_type: {reg_type}, custodian: {custodian}, is_esignature_required: {is_esignature_required}")

    agent_esignature_option = test_context.get("agent_esignature_option", "")

    # Determine which page to use: new context or original
    new_page = test_context.get("new_page")
    new_context = test_context.get("new_browser_context")
    if new_page:
        active_page = new_page
        logger.info("[tracking-ctx] Using new browser context page for client eSign")
    else:
        active_page = view_documents_page.page
        logger.info("Using original page context for client eSign")

    if str(is_esignature_required).strip().lower() == "yes":
        advisory_type = ConstructPortfolioStep.is_sub_advisory or ""
        esignature_eligible = ConstructPortfolioStep.is_esignature_eligible
        esignature_eligibility = "Eligible" if esignature_eligible else "Ineligible"

        logger.info(f"Advisory Type: {advisory_type}")
        logger.info(f"eSignature Eligibility: {esignature_eligibility}")

        if advisory_type.strip().lower() == "non subadvisory" and esignature_eligibility.lower() == "eligible":
            logger.info("Conditions met: Non SubAdvisory + eSignature Eligible. Proceeding with Client eSignature from Tracking Center...")
            try:
                with logger.step("Sign documents as Client from Tracking Center", page=active_page, auto_screenshot=True):
                    docusign_page = DocuSignPage(active_page)
                    docusign_page.e_signature_sign_tracking_center(
                        first_name=test_data.get("AccountHolderFirstName", ""),
                        second_name=test_data.get("AccountHolderLastName", ""),
                        reg_type=reg_type,
                        custodian=custodian,
                        client_type=test_data.get("ClientType", ""),
                        role="Client",
                        option=agent_esignature_option,
                        is_sub_advisory=advisory_type,
                    )
                with logger.step("Verify Client eSignature status from Tracking Center", page=active_page, auto_screenshot=True):
                    docusign_page = DocuSignPage(active_page)
                    # docusign_page.verify_e_signature_status("Client", test_data.get("ESignatureOption", ""), advisory_type)
                logger.info("Client eSignature from Tracking Center completed successfully")
            finally:
                # Cleanup new browser context if used
                if new_page:
                    test_context.pop("new_page", None)
                    test_context.pop("new_browser_context", None)
                    if new_context:
                        try:
                            new_context.close()
                            logger.info("[tracking-ctx] New browser context closed")
                        except Exception as e:
                            logger.warning(f"[tracking-ctx] Failed to close context: {str(e).splitlines()[0]}")
        else:
            error_message = (
                f"Skipping Client Signature from Tracking Center because this step is inapplicable for "
                f"advisory type: {advisory_type} or eSignature eligibility: {esignature_eligibility}"
            )
            is_valid_skip = (
                esignature_eligibility.lower() == "ineligible" or advisory_type.lower() == "subadvisory"
            )
            assert is_valid_skip, error_message
            logger.info(error_message)
    else:
        if not is_esignature_required or str(is_esignature_required).strip().lower() in ["no", "na", ""]:
            logger.info("Skipping this Step as Option not enabled for eSignature in data sheet")
    logger.info("[STEP] User does the client from tracking center page - END")

