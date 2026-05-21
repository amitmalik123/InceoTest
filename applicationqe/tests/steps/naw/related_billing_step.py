"""Related Billing Step Definitions for BDD tests GÇö PRODENG-22459

Acceptance Criteria (from Jira):
  When Fee Payment Method = "Debit from another AssetMark account",
  the Investment Account(s) dropdown must show ONLY billing-eligible models
  (ModelAllowsDirectBilling = 1). Applies to both sleeve and non-sleeve models.

Smart approach: navigate once, validate all model types from DB in single pass.
"""

from pytest_bdd import when, then, parsers
from pages.ewm.account_setup_page import AccountSetupPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.database import execute_query_from_yaml

logger = get_allure_logger(__name__)


def _fetch_model_name(db_manager, query_name: str) -> str:
    """Fetch a single model name from the Platform DB via a YAML query."""
    rows = execute_query_from_yaml("platform", query_name, db_manager=db_manager)
    if not rows:
        raise ValueError(f"No results from platform.{query_name} GÇö check [Platform].[dbo].[Model] data")
    return rows[0]["ModelName"]


@when(parsers.parse('User selects "{method}" as FAA payment method'))
def user_selects_faa_payment_method(test_context, account_setup_page: AccountSetupPage, method: str):
    with logger.step(f"Select FAA payment method: {method}", page=account_setup_page.page):
        account_setup_page.select_faa_payment_method(method)


@then("User validates all billing model filter scenarios from database")
def user_validates_all_billing_scenarios(test_context, account_setup_page: AccountSetupPage, db_manager):
    """Single step covering both Jira AC scenarios (sleeve + non-sleeve).

    Validates on the already-open dropdown after selecting 'Debit from another AssetMark account':
      1. Dropdown has at least one option
      2. Non-billable models (DirectBilling=0) are absent
      3. Non-billable sleeve models (DirectBilling=0, SleeveAPLID NOT NULL) are absent
      4. Billable models (DirectBilling=1) are present
      5. Billable sleeve models (supportscustommodel=1, DirectBilling=1) are present
      6. A billable model can be selected without error
    """
    with logger.step("Validate billing model filter scenarios from database", page=account_setup_page.page):
        options = account_setup_page.get_billing_model_options()

        # Verify dropdown is populated
        Assertions.assert_true(len(options) > 0, "No billing model options found — expected at least one billing-eligible model")
        logger.info(f"Billing dropdown contains {len(options)} model(s): {options}")

        # Jira Scenario: Non-Sleeve Model
        non_billable = _fetch_model_name(db_manager, "non_billable_models")
        logger.info(f"Non-billable model from DB (DirectBilling=0): {non_billable}")
        found = account_setup_page.is_model_in_billing_dropdown(non_billable)
        Assertions.assert_false(
            found,
            f"Non-billable model '{non_billable}' (ModelAllowsDirectBilling=0) "
            f"should NOT appear in dropdown"
        )
        logger.info(f"Non-billable model '{non_billable}' is filtered out")

        billable = _fetch_model_name(db_manager, "billable_models")
        logger.info(f"Billable model from DB (DirectBilling=1): {billable}")
        found = account_setup_page.is_model_in_billing_dropdown(billable)
        Assertions.assert_true(
            found,
            f"Billable model '{billable}' (ModelAllowsDirectBilling=1) "
            f"should appear in dropdown but was not found"
        )
        logger.info(f"Billable model '{billable}' is present")

        # Jira Scenario: Sleeve Model
        non_billable_sleeve = _fetch_model_name(db_manager, "non_billable_sleeve_models")
        logger.info(f"Non-billable sleeve model from DB (DirectBilling=0, SleeveAPLID NOT NULL): {non_billable_sleeve}")
        found = account_setup_page.is_model_in_billing_dropdown(non_billable_sleeve)
        Assertions.assert_false(
            found,
            f"Non-billable sleeve model '{non_billable_sleeve}' "
            f"should NOT appear in dropdown"
        )
        logger.info(f"Non-billable sleeve model '{non_billable_sleeve}' is filtered out")

        billable_sleeve = _fetch_model_name(db_manager, "billable_sleeve_models")
        logger.info(f"Billable sleeve model from DB (supportscustommodel=1, DirectBilling=1): {billable_sleeve}")
        found = account_setup_page.is_model_in_billing_dropdown(billable_sleeve)
        Assertions.assert_true(
            found,
            f"Billable sleeve model '{billable_sleeve}' (ModelAllowsDirectBilling=1) "
            f"should appear in dropdown but was not found"
        )
        logger.info(f"Billable sleeve model '{billable_sleeve}' is present")

        # Select a billable model and verify no error
        account_setup_page.select_billing_model(options[0])
        logger.info(f"Selected first available billable model: {options[0]}")
        Assertions.assert_false(account_setup_page.is_billing_error_visible(), "Billing error visible after selecting billable model")
        logger.info("No billing error — billable model accepted")

        logger.info("All billing model filter scenarios validated in single pass")
