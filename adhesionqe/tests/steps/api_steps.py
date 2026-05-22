"""
API validation step definitions for BDD tests
"""

from pytest_bdd import parsers, then

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then(parsers.parse('User should validate "{api_name}" API with status code "{status_code}"'))
def validate_api_with_status_code(api_name, status_code, test_context, api_utility_page):
    """Aggregated step: add headers, make request, validate status code"""
    logger.info(f"Validating {api_name} API with expected status code {status_code}")

    expected_status = int(status_code)
    household_id = test_context.get("household_id")

    if api_name == "ClientHousehold" and not household_id:
        logger.error("household_id not found in test context for ClientHousehold API")
        raise ValueError(
            "household_id is required for ClientHousehold API but not found in test context"
        )

    is_valid = api_utility_page.validate_api(
        api_name=api_name, expected_status_code=expected_status, household_id=household_id
    )

    if api_utility_page.last_response:
        logger.attach_json(api_utility_page.last_response.json(), f"{api_name} Response")

    assert (
        is_valid
    ), f"{api_name} API validation failed. Expected status code {expected_status}, got {api_utility_page.last_response.status_code if api_utility_page.last_response else 'No response'}"

    logger.info(f"✓ {api_name} API validation completed successfully")
