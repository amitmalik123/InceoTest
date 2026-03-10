"""
TMS verification steps for navigation and page element validation
"""

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.tms_page import TMSPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('user navigates to the TMS page "{account_number}"'))
def navigate_to_tms_page(page: Page, account_number: str):
    logger.info(f"Navigating to TMS page for account number: {account_number}")
    tms_page = TMSPage(page)
    tms_page.navigate_to_tms_page(account_number)


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
