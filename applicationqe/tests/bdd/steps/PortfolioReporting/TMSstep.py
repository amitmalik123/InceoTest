"""
TMS verification steps for navigation and page element validation
"""

from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from pages.PortfolioReporting.tms_page import TMSPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@given("user click on clients tab")
def given_user_clicks_clients_tab_for_tms(page: Page):
    """Open Clients tab before TMS navigation in classic flow."""
    locator_candidates = [
        page.get_by_role("link", name="Clients").first,
        page.locator("//a[normalize-space()='Clients']").first,
        page.locator("text=Clients").first,
    ]

    last_error = None
    for clients_tab in locator_candidates:
        try:
            clients_tab.wait_for(state="visible", timeout=3000)
            clients_tab.scroll_into_view_if_needed(timeout=1000)
            clients_tab.click(timeout=3000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            logger.info("Clients tab clicked successfully")
            return
        except Exception as exc:
            last_error = exc
            try:
                clients_tab.click(timeout=3000, force=True)
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                logger.info("Clients tab clicked successfully (force click fallback)")
                return
            except Exception as force_exc:
                last_error = force_exc

    raise AssertionError(f"Unable to click Clients tab before TMS navigation: {last_error}")


@when(parsers.parse('user navigates to the TMS page "{account_number}"'))
def navigate_to_tms_page(page: Page, account_number: str, test_context):
    row_data = test_context.get("excel_row_data") or {}
    excel_account_number = row_data.get("AccountNumber")
    if excel_account_number is not None and str(excel_account_number).strip() != "":
        excel_account_number = str(excel_account_number).strip()
        feature_account_number = account_number.strip()
        is_excel_placeholder = feature_account_number.lower() in {"accountnumber", "account number"}
        if (
            not feature_account_number.lower().startswith("source:")
            and not is_excel_placeholder
            and feature_account_number != excel_account_number
        ):
            raise AssertionError(
                f"Account number mismatch: feature='{account_number}' excel='{excel_account_number}'"
            )
        account_number = excel_account_number

    logger.info(f"Navigating to TMS page for account number: {account_number}")
    tms_page = TMSPage(page)
    tms_page.navigate_to_tms_page(account_number)


@when(parsers.parse('user navigates to the new navbar TMS page using "{sheet_name}" , {row_number:d}'))
def navigate_to_new_navbar_tms_page(
    page: Page, excel_data_manager, test_context, sheet_name: str, row_number: int
):
    if row_number < 2:
        raise ValueError(
            f"Invalid RowNumber '{row_number}' for sheet '{sheet_name}'. "
            "Use Excel row numbers starting at 2 (first data row)."
        )

    row_data = excel_data_manager.get_row(sheet_name, row_number - 2)
    test_context["excel_row_data"] = row_data

    account_number = None
    for key in ["AccountNumber", "Account Number", "accountnumber"]:
        value = row_data.get(key)
        if value is not None and str(value).strip() != "":
            account_number = str(value).strip()
            break

    if not account_number:
        raise ValueError(
            f"AccountNumber is missing in Excel sheet '{sheet_name}' row {row_number}."
        )

    logger.info(f"Navigating to new navbar TMS page for account: {account_number}")
    tms_page = TMSPage(page)
    tms_page.navigate_to_tms_page_from_clients(account_number)


@then("TMS page should be displayed")
def verify_tms_page_displayed(page: Page):
    logger.info("Verifying TMS page is displayed")
    tms_page = TMSPage(page)
    tms_page.assert_tax_management_service_present()
    logger.info("TMS page successfully displayed")


@when("validate the Federal Short Term and Federal Long Term")
def validate_federal_short_and_long_term(page: Page):
    logger.info("Validating Federal Short Term and Federal Long Term values")
    tms_page = TMSPage(page)
    federal_short_term, federal_long_term = tms_page.assert_federal_terms_valid()
    assert federal_short_term is not None and federal_short_term != "", "Federal Short Term is null or empty"
    assert federal_long_term is not None and federal_long_term != "", "Federal Long Term is null or empty"


@when("validate the Short Term Gain Budget and Long Term Gain Budget")
def validate_short_and_long_term_gain_budget(page: Page):
    logger.info("Validating Short Term Gain Budget and Long Term Gain Budget values")
    tms_page = TMSPage(page)
    short_budget, long_budget = tms_page.assert_gain_budgets_valid()
    assert short_budget is not None and short_budget != "", "Short Term Gain Budget is null or empty"
    assert long_budget is not None and long_budget != "", "Long Term Gain Budget is null or empty"


@then("validate the account name and account number are alphanumeric and not editable")
def validate_account_name_and_number_alphanumeric_and_not_editable(page: Page):
    logger.info("Validating account name and account number are alphanumeric and not editable")
    tms_page = TMSPage(page)
    account_name, account_number = tms_page.assert_account_fields_alphanumeric_and_not_editable()
    assert account_name is not None and account_name != "", "Account Name is null or empty"
    assert account_number is not None and account_number != "", "Account Number is null or empty"
