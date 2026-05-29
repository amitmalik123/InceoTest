from playwright.sync_api import Page
from pytest_bdd import when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("User navigates to fee page and enter require data")
def user_navigates_to_fee_page_and_enter_require_data(page: Page, fees_page, test_context):
    """Enter required data on fee page and proceed."""
    test_data = test_context.get("test_data", {})
    reg_type = (test_context.get("reg_type") or "").strip()
    custodian = (test_context.get("custodian") or "").strip()

    if not reg_type:
        reg_type_data = test_data.get("RegistrationType") or test_data.get("registration_type", "")
        reg_types = reg_type_data.split(",")
        if len(reg_types) <= 1:
            reg_type = reg_types[0].strip()
        else:
            reg_type = reg_types[1].strip()

    if not custodian:
        custodian = (test_data.get("Custodian") or test_data.get("custodian", "")).strip()

    client_fee = test_data.get("ClientFee") or test_data.get("client_fee") or ""

    skip_fee_entry = custodian.lower() == "schwab" and "self-directed brokerage account" in reg_type.lower()

    if skip_fee_entry:
        logger.info(
            "Skipping flat fee entry for Schwab Self-Directed Brokerage Account flow"
        )
    else:
        if not client_fee:
            raise ValueError("ClientFee is missing from test data")

        fees_page.enter_client_fee(client_fee, "Enter flat fee: ", "entering the flat fee ")

    fees_page.confirm_client_fee("Click on next button ", "navigate to portfolio details page ")
    logger.info("Fee page data entered and Next button clicked")
