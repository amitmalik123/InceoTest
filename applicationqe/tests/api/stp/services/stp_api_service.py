from typing import Dict, Optional

import requests

from config.stp.stp_moneyin_moneyout.api_endpoints import APIEndpoints
from utils.allure_logger import get_allure_logger
from utils.settings import settings

logger = get_allure_logger(__name__)


class STPApiService:
    def __init__(self):
        self.session = requests.Session()
        self.last_response: Optional[requests.Response] = None

    def get_headers_for_api(
        self, api_name: str, access_token: Optional[str] = None
    ) -> Dict[str, str]:
        headers = {"accept": "text/plain", "Authorization": settings.api_auth_token}

        if api_name in [
            "ClientHousehold",
            "BeneficiaryHousehold",
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

        masked = {k: ("*****" if k == "Authorization" else v) for k, v in headers.items()}
        logger.info(f"Headers for {api_name}: {masked}")
        return headers

    def make_api_request(
        self,
        api_name: str,
        household_id: Optional[str] = None,
        filter_value: str = "false",
        body: Optional[Dict] = None,
        scenario_name: str = "",
        depth: int = 1,
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
        elif api_name == "BeneficiaryHousehold":
            if not household_id:
                raise ValueError("household_id is required for BeneficiaryHousehold API")

            url = APIEndpoints.GetBeneficiaryHousehold(household_id, depth)
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
                f"âœ“ Status code validation passed: {actual_status} == {expected_status_code}"
            )
        else:
            logger.error(
                f"âœ— Status code validation failed: {actual_status} != {expected_status_code}"
            )

        return is_valid

    def validate_api(
        self,
        api_name: str,
        expected_status_code: int,
        household_id: Optional[str] = None,
        filter_value: str = "false",
        scenario_name: str = "",
        depth: int = 1,
    ) -> bool:
        logger.info(f"Validating {api_name} API with expected status code {expected_status_code}")

        try:
            self.make_api_request(
                api_name, household_id, filter_value, scenario_name=scenario_name, depth=depth
            )

            return self.validate_status_code(expected_status_code)
        except Exception as e:
            logger.error(f"API validation failed with exception: {str(e)}")
            return False

    def get_response_json(self) -> Dict:
        if not self.last_response:
            raise ValueError("No response available")
        return self.last_response.json()

    def getBeneficiaryHouseholdData(
        self, household_id: str, depth: int = 1
    ) -> requests.Response:
        """
        Get beneficiary household data by household ID.

        Args:
            household_id: Household identifier
            depth: Depth level for nested data (default: 1)

        Returns:
            Response object with status code 200 and JSON data
        """
        logger.info(f"Getting beneficiary household data for ID: {household_id} with depth: {depth}")
        
        headers = self.get_headers_for_api("BeneficiaryHousehold")
        url = APIEndpoints.GetBeneficiaryHousehold(household_id, depth)
        
        response = self.session.get(url, headers=headers, verify=False)
        self.last_response = response
        
        logger.info(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info("[OK] Beneficiary household data retrieved successfully")
        else:
            logger.error(f"[FAIL] Failed to retrieve beneficiary household data. Status: {response.status_code}")
        
        return response

