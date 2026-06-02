"""
API Client utility for making HTTP requests with contract validation support
"""

import logging
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """API Client for making HTTP requests with optional contract validation"""

    def __init__(self, session: requests.Session, base_url: str, contract_validator=None):
        """
        Initialize API Client.

        Args:
            session: Requests session
            base_url: Base API URL
            contract_validator: Optional ContractTester instance for validation
        """
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.contract_validator = contract_validator
        self._last_response = None

    def get(
        self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, headers=headers)
        logger.info(f"GET {url} - Status: {response.status_code}")
        return response

    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Make POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json, headers=headers)
        logger.info(f"POST {url} - Status: {response.status_code}")
        return response

    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Make PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, data=data, json=json, headers=headers)
        logger.info(f"PUT {url} - Status: {response.status_code}")
        return response

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Make PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.patch(url, data=data, json=json, headers=headers)
        logger.info(f"PATCH {url} - Status: {response.status_code}")
        return response

    def delete(
        self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make DELETE request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url, params=params, headers=headers)
        logger.info(f"DELETE {url} - Status: {response.status_code}")
        return response

    def set_auth_token(self, token: str):
        """
        Set authentication token in session headers.

        Args:
            token: Authentication token
        """
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        logger.info("Authentication token set")

    def remove_auth_token(self):
        """Remove authentication token from session headers."""
        self.session.headers.pop("Authorization", None)
        logger.info("Authentication token removed")

    def validate_response_schema(self, response: requests.Response, schema: Dict) -> bool:
        """
        Validate response against JSON schema.

        Args:
            response: Response to validate
            schema: JSON schema

        Returns:
            True if valid, False otherwise
        """
        if not self.contract_validator:
            from utils.api_response_utils import JSONSchemaValidator

            validator = JSONSchemaValidator()
            result = validator.validate_response(response, schema)
        else:
            result = self.contract_validator.schema_validator.validate_response(response, schema)

        if not result.is_valid:
            logger.error(f"Schema validation failed: {result.errors}")

        return result.is_valid

    def validate_contract(
        self, endpoint: str, method: str, response: Optional[requests.Response] = None
    ) -> bool:
        """
        Validate response against contract.

        Args:
            endpoint: API endpoint
            method: HTTP method
            response: Response to validate (uses last response if not provided)

        Returns:
            True if valid, False otherwise
        """
        if not self.contract_validator:
            logger.warning("No contract validator configured")
            return True

        if response is None:
            response = self._last_response

        if response is None:
            logger.error("No response to validate")
            return False

        result = self.contract_validator.test_openapi_contract(endpoint, method, response)

        if not result.is_valid:
            logger.error(f"Contract validation failed:\n{result}")

        return result.is_valid
