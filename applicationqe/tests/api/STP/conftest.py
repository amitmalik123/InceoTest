

import os
from typing import Dict

import pytest
import requests

from utils.logger import setup_logger
from utils.settings import Settings

logger = setup_logger(__name__)

# Get environment from environment variable or use default (test11)
env = os.getenv("TEST_ENV", "test11")
settings = Settings(env=env)


@pytest.fixture(scope="session")
def api_client():

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    logger.info("Created API client session")

    yield session

    session.close()
    logger.info("Closed API client session")


@pytest.fixture(scope="session")
def api_base_url():
   
    base_url = settings.base_url
    logger.info(f"Using API base URL: {base_url}")
    return base_url

@pytest.fixture(scope="session")
def api_token():
    
    # Option 1: From environment variable
    token = os.getenv("API_TOKEN")

    # Option 2: From settings file (if stored there)
    # token = settings.api_token

    # Option 3: Generate from API auth endpoint
    # if not token:
    #     auth_response = requests.post(
    #         f"{settings.base_url}/api/auth/token",
    #         json={"username": settings.username, "password": settings.password}
    #     )
    #     token = auth_response.json().get("access_token")

    if token:
        logger.info("API token loaded successfully")
    else:
        logger.warning("No API token found - some tests may fail")

    return token


@pytest.fixture
def api_headers(api_token) -> Dict[str, str]:
    """
    Common API headers with authentication.
    Function scope - creates fresh headers for each test.

    Usage:
        def test_with_headers(api_client, api_base_url, api_headers):
            response = api_client.get(f"{api_base_url}/api/users", headers=api_headers)
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"

    return headers


@pytest.fixture
def api_headers_no_auth() -> Dict[str, str]:
    """
    Headers without authentication (for public endpoints or negative tests).

    Usage:
        def test_public_endpoint(api_client, api_base_url, api_headers_no_auth):
            response = api_client.get(f"{api_base_url}/api/public", headers=api_headers_no_auth)
    """
    return {"Content-Type": "application/json", "Accept": "application/json"}


# ============================================================================
# Response Validation Fixtures
# ============================================================================


@pytest.fixture
def validate_response():
    """
    Helper fixture for common response validations.

    Usage:
        def test_api_response(api_client, api_base_url, validate_response):
            response = api_client.get(f"{api_base_url}/api/users")
            validate_response(response, expected_status=200, expected_keys=["id", "name"])
    """

    def _validate(
        response: requests.Response,
        expected_status: int = 200,
        expected_keys: list = None,
        expected_schema: dict = None,
    ):
        """
        Validate API response.

        Args:
            response: Response object from requests
            expected_status: Expected HTTP status code
            expected_keys: List of keys that must exist in response JSON
            expected_schema: JSON schema for validation (if using jsonschema)
        """
        # Validate status code
        assert (
            response.status_code == expected_status
        ), f"Expected {expected_status}, got {response.status_code}. Response: {response.text}"

        # Validate response is JSON
        try:
            data = response.json()
        except ValueError:
            pytest.fail(f"Response is not valid JSON: {response.text}")

        # Validate required keys
        if expected_keys:
            missing_keys = set(expected_keys) - set(data.keys())
            assert not missing_keys, f"Missing required keys: {missing_keys}. Response: {data}"

        # Validate schema (if jsonschema is installed)
        if expected_schema:
            try:
                from jsonschema import validate as schema_validate

                schema_validate(instance=data, schema=expected_schema)
            except ImportError:
                logger.warning("jsonschema not installed - skipping schema validation")

        logger.info(f"Response validation passed: {expected_status} status code")
        return data

    return _validate


@pytest.fixture
def validate_error_response():
    """
    Helper fixture for validating error responses.

    Usage:
        def test_invalid_request(api_client, api_base_url, validate_error_response):
            response = api_client.get(f"{api_base_url}/api/invalid")
            validate_error_response(response, expected_status=404)
    """

    def _validate_error(
        response: requests.Response, expected_status: int = 400, error_message: str = None
    ):
        """
        Validate error response.

        Args:
            response: Response object from requests
            expected_status: Expected error status code (4xx or 5xx)
            error_message: Expected error message substring
        """
        assert (
            response.status_code == expected_status
        ), f"Expected {expected_status}, got {response.status_code}"

        try:
            data = response.json()
        except ValueError:
            pytest.fail(f"Error response is not valid JSON: {response.text}")

        # Check if error message is present
        if error_message:
            response_text = response.text.lower()
            assert (
                error_message.lower() in response_text
            ), f"Expected error message '{error_message}' not found in response: {response.text}"

        logger.info(f"Error response validation passed: {expected_status} status code")
        return data

    return _validate_error


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def api_test_data():
    """
    Common test data for API tests.
    Can be loaded from CSV/JSON files or generated dynamically.

    Usage:
        def test_create_user(api_client, api_base_url, api_test_data):
            response = api_client.post(
                f"{api_base_url}/api/users",
                json=api_test_data["new_user"]
            )
    """
    return {
        "new_user": {
            "username": "testuser",
            "email": "testuser@example.com",
            "firstName": "Test",
            "lastName": "User",
        },
        "update_user": {"email": "updated@example.com", "firstName": "Updated"},
        "invalid_user": {
            "username": "",  # Invalid: empty username
            "email": "invalid-email",  # Invalid: bad email format
        },
    }


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture
def cleanup_api_resources():
    """
    Track and cleanup API resources created during tests.

    Usage:
        def test_create_account(api_client, api_base_url, cleanup_api_resources):
            # Create account
            response = api_client.post(f"{api_base_url}/api/accounts", json={...})
            account_id = response.json()["id"]

            # Register for cleanup
            cleanup_api_resources.add(f"/api/accounts/{account_id}")

            # Test logic...
            # Account will be automatically deleted after test
    """
    resources_to_delete = []

    class ResourceCleaner:
        def add(self, resource_path: str):
            """Add resource path for cleanup"""
            resources_to_delete.append(resource_path)

    yield ResourceCleaner()

    # Cleanup after test
    if resources_to_delete:
        logger.info(f"Cleaning up {len(resources_to_delete)} API resources")
        session = requests.Session()
        for resource_path in resources_to_delete:
            try:
                full_url = f"{settings.base_url}{resource_path}"
                response = session.delete(full_url)
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Cleaned up resource: {resource_path}")
                else:
                    logger.warning(f"Failed to cleanup {resource_path}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error cleaning up {resource_path}: {e}")
        session.close()
