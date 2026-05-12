from typing import Dict, Optional

import requests

from config.oam.api_endpoints import APIEndpoints
from config.oam.settings import settings
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class APIUtilityPage:
    def __init__(self):
        self.session = requests.Session()
        self.last_response: Optional[requests.Response] = None

    def get_headers_for_api(
        self, api_name: str, access_token: Optional[str] = None
    ) -> Dict[str, str]:
        headers = {"accept": "text/plain", "Authorization": settings.api_auth_token}

        if api_name in [
            "ClientHousehold",
            "GetPeriodicWithdrawalInstruction",
            "GetCheckPINS",
            "GetACHBank",
            "GetACHBankForContributions",
            "InstructionOnFile",
            "restrictedCash",
        ]:
            pass
        elif api_name in [
            "AddACHBankInstructions",
            "GetCustomersByAccount",
            "BankRoutingNumber",
            "ACHInstructionSubmissionRequest",
            "GetAccountsBySSNAndAgentId",
            "GetCustomerDetails",
            "CreatePeriodicAIP",
        ]:
            headers["Content-Type"] = "application/json"
        elif api_name in ["GetAccountDetail", "updateAccountForBeta"] and access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        elif (
            api_name
            in [
                "GetAccountCustomAttributes",
                "UpdateAccountCustomAttributes",
                "GetACHInstructionsByAccount",
                "GetPayeeInstructions",
                "GetDocumentsListByAccount",
                "DeleteDocumentForAccount",
            ]
            and access_token
        ):
            headers["Authorization"] = f"Bearer {access_token}"
            headers["api-version"] = "v1"
        elif api_name == "UpdateCustomer" and access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            headers["api-version"] = "v2"
        elif api_name == "TradeInfoSearch" and access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        logger.info(f"Headers for {api_name}: {headers}")
        return headers

    def make_api_request(
        self,
        api_name: str,
        household_id: Optional[str] = None,
        filter_value: str = "false",
        body: Optional[Dict] = None,
        scenario_name: str = "",
    ) -> requests.Response:
        headers = self.get_headers_for_api(api_name)

        if api_name == "ClientHousehold":
            if not household_id:
                raise ValueError("household_id is required for ClientHousehold API")

            if "Address Change" in scenario_name:
                filter_value = "true"

            url = APIEndpoints.GetClientHousehold(household_id, filter_value)
            logger.info(f"Making GET request to: {url}")
            response = self.session.get(url, headers=headers, verify=False)
        else:
            raise ValueError(f"API name '{api_name}' not yet implemented")

        self.last_response = response
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text[:500]}...")

        return response

    def validate_status_code(self, expected_status_code: int) -> bool:
        if not self.last_response:
            logger.error("No response available to validate")
            return False

        actual_status = self.last_response.status_code
        is_valid = actual_status == expected_status_code

        if is_valid:
            logger.info(
                f"✓ Status code validation passed: {actual_status} == {expected_status_code}"
            )
        else:
            logger.error(
                f"✗ Status code validation failed: {actual_status} != {expected_status_code}"
            )

        return is_valid

    def validate_api(
        self,
        api_name: str,
        expected_status_code: int,
        household_id: Optional[str] = None,
        filter_value: str = "false",
        scenario_name: str = "",
    ) -> bool:
        logger.info(f"Validating {api_name} API with expected status code {expected_status_code}")

        try:
            self.make_api_request(api_name, household_id, filter_value, scenario_name=scenario_name)

            return self.validate_status_code(expected_status_code)
        except Exception as e:
            logger.error(f"API validation failed with exception: {str(e)}")
            return False

    def get_response_json(self) -> Dict:
        if not self.last_response:
            raise ValueError("No response available")
        return self.last_response.json()
