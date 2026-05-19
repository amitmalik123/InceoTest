"""Document Visibility Step Definitions for BDD tests G현 PRODENG-2057

AC Scenarios (from Jira customfield_10207):
  AC 3: FID & TDA G현 AM-branded docs NOT visible, custodial-branded SHOULD be visible
  AC 4: IRS forms for Simple/SEP IRA (5304-SIMPLE, 5305-SA, 5305-SEP)

Smart approach: navigate once, open Separate Documents dialog, validate all rules in one pass.
"""

from pytest_bdd import then
from pages.ewm.view_documents_page import ViewDocumentsPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)

# AC 3: AM-branded form keywords G현 should NOT appear for FID/TDA custodians
AM_BRANDED_KEYWORDS = [
    "Cash Restriction",
    "Suspend Trading",
]

# AC 3: Custodial-branded form keywords G현 SHOULD appear for FID/TDA custodians
CUSTODIAL_KEYWORDS = [
    "Standing Instructions",
    "Systematic Withdrawal",
    "SWP",
]

# AC 4: IRS forms expected for specific registration types
IRS_FORMS = {
    "simple": ["5304-SIMPLE"],
    "sep": ["5305-SA", "5305-SEP"],
}


def _get_custodian_code(custodian_name: str) -> str:
    """Map test data custodian name to custodian code."""
    mapping = {
        "fidelity": "FID",
        "fidelity direct": "FDD",
        "schwab": "TDA",
        "schwab direct": "SWB",
        "pershing advisor solutions": "PAS",
        "assetmark trust": "GNW",
    }
    return mapping.get(custodian_name.strip().lower(), custodian_name.strip().upper())


def _is_fid_or_tda(custodian: str) -> bool:
    """Return True if custodian is FID, FDD, TDA, or SWB (Fidelity/Schwab family)."""
    code = _get_custodian_code(custodian)
    return code in ("FID", "FDD", "TDA", "SWB")


def _check_am_branded_not_visible(doc_names: list[str]) -> list[str]:
    """AC 3: Assert AM-branded documents are NOT in the list.

    Returns list of failure messages (empty = all passed).
    """
    failures: list[str] = []
    doc_text_lower = " ".join(doc_names).lower()

    for keyword in AM_BRANDED_KEYWORDS:
        if keyword.lower() in doc_text_lower:
            failures.append(
                f"AM-branded form '{keyword}' found in documents but should be HIDDEN for FID/TDA"
            )
            logger.error(f"  Gｙ FAIL G현 AM-branded '{keyword}' is visible (should be hidden)")
        else:
            logger.info(f"  Gｔ PASS G현 AM-branded '{keyword}' correctly hidden")

    return failures


def _check_custodial_visible(doc_names: list[str]) -> list[str]:
    """AC 3: Assert at least one custodial-branded document IS in the list.

    Returns list of failure messages (empty = all passed).
    """
    failures: list[str] = []
    doc_text_lower = " ".join(doc_names).lower()

    found_any = False
    for keyword in CUSTODIAL_KEYWORDS:
        if keyword.lower() in doc_text_lower:
            found_any = True
            logger.info(f"  Gｔ PASS G현 Custodial form '{keyword}' is visible")
        else:
            logger.info(f"  G현 Custodial form '{keyword}' not found (may not apply to this registration)")

    if not found_any:
        failures.append(
            f"No custodial-branded forms found. Expected at least one of: {CUSTODIAL_KEYWORDS}"
        )
        logger.error("  Gｙ FAIL G현 No custodial-branded forms found at all")

    return failures


def _check_irs_forms(doc_names: list[str], reg_type: str) -> list[str]:
    """AC 4: If registration is Simple or SEP IRA, IRS forms must be present.

    Returns list of failure messages (empty = all passed or not applicable).
    """
    failures: list[str] = []
    reg_lower = reg_type.lower()
    doc_text_lower = " ".join(doc_names).lower()

    for irs_key, form_list in IRS_FORMS.items():
        if irs_key in reg_lower:
            for form_name in form_list:
                if form_name.lower() in doc_text_lower:
                    logger.info(f"  Gｔ PASS G현 IRS form '{form_name}' present for {irs_key.upper()} IRA")
                else:
                    failures.append(
                        f"IRS form '{form_name}' NOT found for {irs_key.upper()} IRA registration"
                    )
                    logger.error(f"  Gｙ FAIL G현 IRS form '{form_name}' missing for {irs_key.upper()} IRA")

    return failures


@then("User validates document visibility for form bundle master")
def user_validates_document_visibility(test_context, view_documents_page: ViewDocumentsPage):
    """Single step covering AC 3 + AC 4 document visibility rules.

    1. Open Separate Documents dialog via ViewDocumentsPage
    2. Collect all visible document/form names
    3. For FID/TDA: assert AM-branded NOT visible + custodial-branded ARE visible
    4. For Simple/SEP IRA: assert IRS forms present
    5. Log every assertion result
    """
    with logger.step("Validate document visibility for form bundle master", page=view_documents_page.page):
        test_data = test_context.get("test_data", {})
        custodian = test_data.get("Custodian", "")
        reg_type = test_data.get("RegistrationType", "")

        logger.info(f"Validating document visibility - Custodian: {custodian}, Registration: {reg_type}")

        # Collect all document names from Separate Documents dialog
        doc_names = view_documents_page.get_all_separate_document_names()
        Assertions.assert_true(len(doc_names) > 0, "Separate Documents dialog returned no documents")

        all_failures: list[str] = []

        # AC 3: FID/TDA visibility rules
        if _is_fid_or_tda(custodian):
            logger.info("=== AC 3: FID/TDA Document Visibility ===")
            all_failures.extend(_check_am_branded_not_visible(doc_names))
            all_failures.extend(_check_custodial_visible(doc_names))
        else:
            logger.info(f"Custodian '{custodian}' is not FID/TDA - skipping AC 3 visibility checks")

        # AC 4: IRS forms for Simple/SEP
        logger.info("=== AC 4: IRS Forms Check ===")
        all_failures.extend(_check_irs_forms(doc_names, reg_type))

        # Final verdict
        if all_failures:
            failure_report = "\n".join(f"  - {f}" for f in all_failures)
            Assertions.fail(f"Document visibility validation failed:\n{failure_report}")

        logger.info("All document visibility assertions passed")
