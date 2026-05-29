"""BDD bindings for features/Lead_Page_Validation.feature."""
import pytest
from pytest_bdd import scenarios, when, then

# Re-use the common Background steps
from steps.salesforce.common_steps import *  # noqa: F401,F403

from utils.logger import get_allure_logger
logger = get_allure_logger(__name__)
pytestmark = pytest.mark.smoke

# Bind every scenario in the feature file
scenarios("../../features/salesforce/Lead_Page_Validation.feature")


# ---------------------------------------------------------------------------
# Scenario: Verify standard fields on the Lead creation page
# ---------------------------------------------------------------------------
@when("I open the new Lead form")
def step_open_new_lead_form():
    """Open the new Lead form."""
    # The page object's verify_Standard_Fields() also clicks the New button,
    # so we leave this as a documentation-only step (no-op) to keep the
    # Gherkin readable.
    pass
    logger.info("New Lead form is opened.")


@then("the standard Lead fields should be displayed on the new Lead form")
def step_verify_standard_fields(lead_fields):
    """Verify that the standard Lead fields are displayed on the new Lead form."""
    lead_fields.verify_Standard_Fields()
    logger.info("Standard fields on the new Lead form are verified.")

# ---------------------------------------------------------------------------
# Scenario: Verify dependent picklist values
# ---------------------------------------------------------------------------
@then("the dependent Lead Channel picklist values should be correct")
def step_verify_dependent_picklists(lead_picklists):
    """Verify that the dependent Lead Channel picklist values are correct."""
    lead_picklists.verify_Lead_Channel_Dependent_Picklist_Values()
    logger.info("Dependent Lead Channel picklist values are verified.")


# ---------------------------------------------------------------------------
# Scenario: Verify picklist values
# ---------------------------------------------------------------------------
@then("the Lead Source picklist values should be correct")
def step_verify_lead_source_picklist(lead_picklists):
    """Verify that the Lead Source picklist values are correct."""
    lead_picklists.verify_Lead_Source_Picklist_Values()
    logger.info("Lead Source picklist values are verified.")


# @then("the Lead Status picklist values should be correct")
# def step_verify_lead_status_picklist(lead_picklists):
#     """Verify that the Lead Status picklist values are correct."""
#     lead_picklists.verify_Lead_Status_Picklist_Values()
#     logger.info("Lead Status picklist values are verified.")


# @then("the Lead Type picklist values should be correct")
# def step_verify_lead_type_picklist(lead_picklists):
#     """Verify that the Lead Type picklist values are correct."""
#     lead_picklists.verify_Lead_Type_Picklist_Values()
#     logger.info("Lead Type picklist values are verified.")


@then("the Marketing Funnel picklist values should be correct")
def step_verify_marketing_funnel_picklist(lead_picklists):
    """Verify that the Marketing Funnel picklist values are correct."""
    lead_picklists.verify_Marketing_Funnel_Picklist_Values()
    logger.info("Marketing Funnel picklist values are verified.")


@then("the Registered Rep Type picklist values should be correct")
def step_verify_registered_rep_type_picklist(lead_picklists):
    """Verify that the Registered Rep Type picklist values are correct."""
    lead_picklists.verify_Registered_Rep_Type_Picklist_Values()
    logger.info("Registered Rep Type picklist values are verified.")

# ---------------------------------------------------------------------------
# Scenario: Verify error messages for mandatory fields
# ---------------------------------------------------------------------------
@when("I try to save the Lead without filling mandatory fields")
def step_try_save_empty_lead():
    """Try to save the Lead without filling mandatory fields."""
    # The validation page object performs the click + assertions in one method.
    # Acts as a documentation-only step.
    pass
    logger.info("Attempting to save the Lead without filling mandatory fields.")

@then("validation errors should be displayed for mandatory fields")
def step_verify_mandatory_field_errors(lead_validation, test_data):
    """Verify that validation errors are displayed for mandatory fields."""
    lead_validation.validation_Errors_with_Different_Account_Types(
        test_data["firstName"], test_data["lastName"], test_data["email"]
    )
    logger.info("Validation errors are displayed for mandatory fields.")

# ---------------------------------------------------------------------------
# Scenario: Verify lookup fields
# ---------------------------------------------------------------------------
@then("the Lead lookup fields should be displayed")
def step_verify_lookup_fields(lead_fields):
    """Verify that the Lead lookup fields are displayed."""
    lead_fields.verify_Lookup_Fields()
    logger.info("Lead lookup fields are displayed.")


# ---------------------------------------------------------------------------
# Scenario: Verify CRD fields
# ---------------------------------------------------------------------------
@then("the CRD fields should be displayed")
def step_verify_crd_fields(lead_fields):
    """Verify that the CRD fields are displayed."""
    lead_fields.verify_CRD_Fields()
    logger.info("CRD fields are displayed.")


# ---------------------------------------------------------------------------
# Scenario: Verify opportunity related fields
# ---------------------------------------------------------------------------
# @then("the opportunity related fields should be displayed")
# def step_verify_opportunity_fields(lead_fields):
#     """Verify that the opportunity related fields are displayed."""
#     lead_fields.verify_Opportunity_Related_Fields()
#     logger.info("Opportunity related fields are displayed.")


# ---------------------------------------------------------------------------
# Scenario: Create a Lead with valid data
# ---------------------------------------------------------------------------
@when("I create a Lead with valid data")
def step_create_lead(lead_happy_path, test_data, session_state):
    """Create a Lead with valid data."""
    lead_happy_path.create_Lead_with_Valid_Data(
        test_data["firstName"], test_data["lastName"], test_data["email"]
    )
    session_state["lead_created"] = True
    logger.info("Lead created with valid data.")

@then("the Lead detail page should display the new Lead's name")
def step_verify_lead_detail():
    """Verify that the Lead detail page displays the new Lead's name."""
    # create_Lead_with_Valid_Data already asserts the primaryField text.
    pass
    logger.info("Lead detail page displays the new Lead's name.")


# ---------------------------------------------------------------------------
# Scenario: Verify the Lead path on the Leads page
# ---------------------------------------------------------------------------
@then("the Lead path stages should display the correct descriptions")
def step_verify_lead_path(lead_happy_path, test_data):
    """Verify that the Lead path stages display the correct descriptions."""
    lead_happy_path.verify_Path_On_Leads_Page(
        test_data["firstName"], test_data["lastName"]
    )
    logger.info("Lead path stages display the correct descriptions.")