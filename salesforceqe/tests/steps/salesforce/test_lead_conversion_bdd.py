"""BDD bindings for features/Lead_Conversion.feature."""
import pytest
from pytest_bdd import scenarios, given, when, then
from steps.salesforce.common_steps import *  # noqa: F401,F403
from utils.logger import get_allure_logger
logger = get_allure_logger(__name__)

pytestmark = pytest.mark.smoke

scenarios("../../features/salesforce/Lead_Conversion.feature")

@given("I have created a Lead with valid data")
def step_ensure_lead_exists(lead_happy_path, test_data, session_state):
    """Ensure a Lead with valid data exists"""
    if session_state["lead_created"]:
        return
    lead_happy_path.create_Lead_with_Valid_Data(
        test_data["firstName"], test_data["lastName"], test_data["email"]
    )
    session_state["lead_created"] = True
    logger.info(f"Lead: {test_data['firstName']} {test_data['lastName']} is created and ready for conversion tests.")


@when("I attempt to convert the Lead with missing Broker Dealer Account and CRD Advisor")
def step_attempt_lead_conversion(lead_validation, test_data):
    """Attempt to convert the Lead with missing Broker Dealer Account and CRD Advisor"""
    logger.info(f"Attempting to convert Lead with missing Broker Dealer Account and CRD Advisor: {test_data['CRD_Firm']}, {test_data['CRD_Advisor']}")  
    lead_validation.validation_On_Lead_Conversion(
        test_data["CRD_Firm"], test_data["CRD_Advisor"]
    )


@then("a Lead Conversion validation error should be displayed")
def step_verify_lead_conversion_validation():
    """Verify that a Lead Conversion validation error is displayed"""
    # Assertions live inside validation_On_Lead_Conversion().
    pass
    logger.info("Lead Conversion validation errors are verified.")