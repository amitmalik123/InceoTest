"""
API Client utility for making HTTP requests with contract validation support
"""

import logging
from typing import Dict, Optional

import requests
from config.api_endpoints import APIEndpoints

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

    def retriving_value_object_from_response(self, response: requests.Response, key: str):
        """Retrieve a value from JSON response using a simple dotted/key[index] path.

        Examples:
          - "responseHeader.status"
          - "responseHeader.messages[0].description"
        """
        try:
            data = response.json()
        except Exception:
            logger.error("Failed to parse response JSON")
            return None

        current = data
        import re

        pattern = re.compile(r"([^\[\]]+)(?:\[(\d+)\])?")
        for part in key.split('.'):
            m = pattern.fullmatch(part)
            if not m:
                return None
            name, idx = m.group(1), m.group(2)

            if isinstance(current, dict):
                current = current.get(name)
            else:
                return None

            if idx is not None:
                try:
                    current = current[int(idx)]
                except Exception:
                    return None

        logger.info(f"the value is :{current}")
        return current

    def get_bearer_token_cancel_swp(self) -> str:
       
        url = "https://assetmark.oktapreview.com/oauth2/default/v1/token"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Authorization": "Basic MG9hdWx6bnZhZ0VITmJJZk0waDc6RU1BZWNfUmdrdHpobGw3Vk5EWkJ1ZGNUSEJUNGNDZU5YQ2VsMDJEYQ==",
            "Cookie": "JSESSIONID=320178982A98C6F361D7AE1642754152",
        }

        payload = {"grant_type": "client_credentials"}

        client_id = "0oaulznvagEHNbIfM0h7"
        client_secret = "EMAec_Rgktzhll7VNDZBudcTHBT4cCeNXCel02Da"

        resp = self.session.post(
            url,
            data=payload,
            headers=headers,
            auth=(client_id, client_secret),
            verify=True,
            timeout=30,
        )

        self._last_response = resp
        logger.info(f"response code : {resp.status_code}")

        try:
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to parse token response JSON: {e}")
            raise RuntimeError("Failed to parse token response JSON")

        token = data.get("access_token")
        if not token:
            logger.error(f"Access token not found in response: {data}")
            raise RuntimeError("Failed to retrieve access token")

        logger.info(f"Access Token : {token}")
        return token

    def adding_header_parameters_for_cancel_swp(self) -> Dict[str, str]:
        """
        Headers for APIs using SSO token authentication (not Bearer token).
        Used by: GetPeriodicWithdrawalInstruction, GetSWPTradeRequestHistory, GetCheckPINS,
                 GetACHBank, GetACHBankForContributions, ClientHousehold, InstructionOnFile, restrictedCash
        """
        headers = {
            "accept": "text/plain",
            "Authorization": "SSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&UserId=AMADMN:1:81000:::1:,&loginPreference=False&IsAdminLogin=True&LoggedInUserSSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&Group=AMK&UserName=SSOGuidToken&IssuedAt=1/6/2025 11:31:04 AM&ExpiresOn=1/6/2025 12:31:04 PM&ANONYMIZE=NO&KeyVersion=31111&HMACSHA256=ZzhI%2blNCj0SqGiLug4wLiTn%2bFGPzyyEFkjKK4hxMJHg%3d"
        }
        logger.info(f"Headers for Cancel SWP: {headers}")
        return headers

    def adding_header_parameters_for_add_ach_instructions(self) -> Dict[str, str]:
        """
        Headers for Add ACH Instructions APIs using SSO token.
        Used by: AddACHBankInstructions, GetCustomersByAccount, ACHInstructionSubmissionRequest,
                 GetAccountsBySSNAndAgentId, GetCustomerDetails, CreatePeriodicAIP
        """
        headers = {
            "accept": "text/plain",
            "Authorization": "SSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&UserId=AMADMN:1:81000:::1:,&loginPreference=False&IsAdminLogin=True&LoggedInUserSSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&Group=AMK&UserName=SSOGuidToken&IssuedAt=1/6/2025 11:31:04 AM&ExpiresOn=1/6/2025 12:31:04 PM&ANONYMIZE=NO&KeyVersion=31111&HMACSHA256=ZzhI%2blNCj0SqGiLug4wLiTn%2bFGPzyyEFkjKK4hxMJHg%3d",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for Add ACH Instructions: {headers}")
        return headers

    def adding_header_parameters_for_cancel_swp_trade_request_history(self) -> Dict[str, str]:
        """
        Minimal headers for GetSWPTradeRequestHistory and BankRoutingNumber.
        """
        headers = {
            "accept": "text/plain"
        }
        logger.info(f"Headers for Trade Request History: {headers}")
        return headers

    def adding_header_parameters_cancel_swp_create_instruction(self, access_token: str, api_version: str = "v1") -> Dict[str, str]:
        """
        Headers with Bearer token and API management subscription key.
        Used by: GetAccountCustomAttributes, UpdateAccountCustomAttributes, GetACHInstructionsByAccount,
                 GetPayeeInstructions, GetDocumentsListByAccount, DeleteDocumentForAccount, UpdateCustomer
        """
        headers = {
            "Ocp-Apim-Subscription-Key": "db28dc8a774f4e25a9d553067a7ac977",
            "Api-Version": api_version,
            "Ocp-Apim-Trace": "true",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for CancelSWP create instruction: {headers}")
        return headers

    def adding_header_parameters_dm2_beta_access(self, access_token: str) -> Dict[str, str]:
        """
        Headers for DM2 Beta Access APIs.
        Used by: GetAccountDetail, updateAccountForBeta
        """
        headers = {
            "Ocp-Apim-Subscription-Key": "db28dc8a774f4e25a9d553067a7ac977",
            "Api-Version": "v3",
            "Ocp-Apim-Trace": "true",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for DM2 Beta Access: {headers}")
        return headers

    def adding_header_parameters_for_dmt_manage_instructions(self) -> Dict[str, str]:
        """
        Headers for DMT Manage Instructions.
        Used by: DMT_ManageInstructions_SLOA
        """
        headers = {
            "accept": "text/plain",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for DMT Manage Instructions: {headers}")
        return headers

    def adding_header_parameters_for_validate_conflicting_oas(self) -> Dict[str, str]:
        """
        Headers for ValidateConflictingOAs API.
        """
        headers = {
            "accept": "text/plain",
            "Authorization": "SSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&UserId=AMADMN:1:81000:::1:,&loginPreference=False&IsAdminLogin=True&LoggedInUserSSOGUID=7308781A-66BD-DDC6-EAA6-454C2404F367&Group=AMK&UserName=SSOGuidToken&IssuedAt=8/6/2024 2:54:00 PM&ExpiresOn=8/6/2024 3:54:00 PM&ANONYMIZE=NO&KeyVersion=29042&HMACSHA256=fmqtg86B7klwkhkQb4w%2f115AP9njq5dGyxeh6Xa%2bMDI%3d",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for ValidateConflictingOAs: {headers}")
        return headers

    def adding_header_parameters_for_ewm30(self, access_token: str) -> Dict[str, str]:
        """
        Headers for EWM30 APIs.
        Used by: TradeInfoSearch
        """
        headers = {
            "accept": "text/plain",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        logger.info(f"Headers for EWM30: {headers}")
        return headers

    def design_request_body_cancel_swp(self, method: str, acc_type: str, account_number: str, tomorrow_date: str) -> str:
        
        import json

        account_number_int = int(account_number) if account_number and str(account_number).isdigit() else account_number

        request_header = {
            "externalReferenceId": "9daabc98-c969-43ad-94c1-0169d9370134",
            "applicationId": "amk-svc-02",
            "custodialId": "WWS",
            "requestor": {
                "identity": "2426862",
                "identityType": "SubId"
            },
            "requestAction": "Submit"
        }

        base_body = {
            "requestHeader": request_header,
            "createPeriodicWithdrawalInstructionsRequest": {
                "processingInstruction": "Submit",
                "accountNumber": account_number_int,
                "trailerDescription": "string",
                "recipientInformation": {},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "beginningDate": tomorrow_date
                }
            }
        }

        method_bodies = {
            "Journal": {
                "recipientInformation": {"socialSecurityNumber": "000005557"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 125,
                    "beginningDate": tomorrow_date,
                    "assetMovementInstruction": {
                        "sourceCode": "JNL",
                        "destinationAccountNumber": account_number_int,
                        "destinationAccountType": "Cash",
                        "typeOfBeneficiary": "SameNameAndAddress"
                    }
                }
            },
            "Check": {
                "recipientInformation": {"socialSecurityNumber": "000000001"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 123,
                    "beginningDate": tomorrow_date
                }
            },
            "ACH": {
                "recipientInformation": {"socialSecurityNumber": "000000001"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 45,
                    "beginningDate": tomorrow_date,
                    "ACHInstructionNumber": 1
                }
            },
            "Journal_RMD": {
                "recipientInformation": {"socialSecurityNumber": "000005555"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 125,
                    "beginningDate": tomorrow_date,
                    "assetMovementInstruction": {
                        "sourceCode": "JNL",
                        "destinationAccountNumber": account_number_int,
                        "destinationAccountType": "Cash",
                        "typeOfBeneficiary": "SameNameAndAddress"
                    }
                }
            },
            "ACH_RMD": {
                "recipientInformation": {"socialSecurityNumber": "000005555"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 45,
                    "beginningDate": tomorrow_date,
                    "ACHInstructionNumber": 1
                }
            },
            "Check_RMD": {
                "recipientInformation": {"socialSecurityNumber": "000005555"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 129,
                    "beginningDate": tomorrow_date
                }
            },
            "Journal_DivInt": {
                "recipientInformation": {"socialSecurityNumber": "000001001"},
                "periodicWithdrawalInformation": {
                    "frequency": "Annually",
                    "withdrawalAmount": 30,
                    "beginningDate": tomorrow_date,
                    "assetMovementInstruction": {
                        "sourceCode": "JNL",
                        "destinationAccountNumber": account_number_int,
                        "destinationAccountType": "Cash",
                        "typeOfBeneficiary": "SameNameAndAddress"
                    },
                    "checkWithdrawalInstruction": {
                        "dividendIncome": "BatchProcessing",
                        "interest": "BatchProcessing"
                    }
                }
            },
            "Check_DivInt": {
                "recipientInformation": {"socialSecurityNumber": "000001001"},
                "periodicWithdrawalInformation": {
                    "frequency": "Annually",
                    "withdrawalAmount": 30,
                    "beginningDate": tomorrow_date,
                    "checkWithdrawalInstruction": {
                        "dividendIncome": "BatchProcessing",
                        "interest": "BatchProcessing"
                    }
                }
            },
            "ACH_DivInt": {
                "recipientInformation": {"socialSecurityNumber": "000001001"},
                "periodicWithdrawalInformation": {
                    "frequency": "Monthly",
                    "withdrawalAmount": 111,
                    "beginningDate": tomorrow_date,
                    "ACHInstructionNumber": 2,
                    "checkWithdrawalInstruction": {
                        "dividendIncome": "BatchProcessing",
                        "interest": "BatchProcessing"
                    }
                }
            }
        }

        if method not in method_bodies:
            logger.warning(f"Method '{method}' not found; using base body")
            body = base_body
        else:
            # Merge method-specific config with base body
            body = base_body.copy()
            method_config = method_bodies[method]
            if "recipientInformation" in method_config:
                body["createPeriodicWithdrawalInstructionsRequest"]["recipientInformation"] = method_config["recipientInformation"]
            if "periodicWithdrawalInformation" in method_config:
                body["createPeriodicWithdrawalInstructionsRequest"]["periodicWithdrawalInformation"] = method_config["periodicWithdrawalInformation"]

        json_string = json.dumps(body, separators=(",", ":"))
        logger.info(f"Designed request body for method '{method}': {json_string[:100]}...")
        return json_string

    def post_response_for_endpoint(self, endpoint_name: str, account_number: str = None, body: str = None, household_id: str = None, filter_value: str = "false", headers: Dict[str, str] = None) -> requests.Response:
        """
        Post a request to the specified endpoint and return the response.
        Handles POST and GET requests with dynamic URL construction.
        Uses endpoint URLs from api_constants.APIEndpoints.
        
        Args:
            headers: Request headers to use. If None, will use default headers.
        """
        # Map endpoint names to their URLs from APIEndpoints class
        endpoint_mapping = {
            "createACHInstructions": ("POST", APIEndpoints.CreateACHInstructions),
            "CreateACHInstructions": ("POST", APIEndpoints.CreateACHInstructions),
            "deactivateACHInstructions": ("POST", APIEndpoints.DeactivateACHInstructions),
            "DeactivateACHInstructions": ("POST", APIEndpoints.DeactivateACHInstructions),
            "getACHInstructions": ("POST", APIEndpoints.GetACHInstructions),
            "GetACHInstructions": ("POST", APIEndpoints.GetACHInstructions),
            "createPayeeInstructions": ("POST", APIEndpoints.CreatePayeeInstructions),
            "CreatePayeeInstructions": ("POST", APIEndpoints.CreatePayeeInstructions),
            "CreatePeriodicWithdrawalInstructions": ("POST", APIEndpoints.CreatePeriodicWithdrawalInstructions),
            "GetPeriodicWithdrawalInstructionsByAccount": ("POST", APIEndpoints.GetPeriodicWithdrawalInstructionsByAccount),
            "GetPeriodicWithdrawalInstruction": ("GET", APIEndpoints.GetPeriodicWithdrawalInstruction),
            "GetCheckPINS": ("GET", APIEndpoints.GetCheckPINS),
            "GetACHBank": ("GET", APIEndpoints.GetACHBank),
            "AddACHInstructions": ("POST", APIEndpoints.AddACHInstructions),
            "GetACHBankForContribution": ("GET", APIEndpoints.GetACHBankForContribution),
            "GetAccountDetail": ("POST", APIEndpoints.GetAccountDetail),
            "UpdateAccountForBeta": ("POST", APIEndpoints.UpdateAccountForBeta),
            "GetAccountCustomAttributes": ("POST", APIEndpoints.GetAccountCustomAttributes),
            "UpdateAccountCustomAttributes": ("POST", APIEndpoints.UpdateAccountCustomAttributes),
            "DMT_ManageInstructions_SLOA": ("POST", APIEndpoints.DMT_ManageInstructions_SLOA),
            "GetCustomersByAccount": ("POST", APIEndpoints.GetCustomersByAccount),
            "BankRoutingNumber": ("GET", APIEndpoints.BankRoutingNumber),
            "GetACHInstructionsByAccount": ("POST", APIEndpoints.GetACHInstructionsByAccount),
            "GetPayeeInstructions": ("POST", APIEndpoints.GetPayeeInstructions),
            "ACHInstructionSubmissionRequest": ("POST", APIEndpoints.ACHInstructionSubmissionRequest),
            "GetAccountsBySSNAndAgentId": ("POST", APIEndpoints.GetAccountsBySSNAndAgentId),
            "InstructionOnFile": ("GET", APIEndpoints.InstructionsOnFile),
            "GetCustomersByAccountForRoth": ("POST", APIEndpoints.GetCustomersByAccountForRoth),
            "validateConflictingOAs": ("POST", APIEndpoints.ValidateConflictingOAs),
            "GetCustomerDetails": ("POST", APIEndpoints.GetCustomerDetails),
            "GetDocumentsListByAccount": ("GET", APIEndpoints.GetDocumentsListByAccount),
            "DeleteDocumentForAccount": ("POST", APIEndpoints.DeleteDocumentForAccount),
            "CreatePeriodicAIP": ("POST", APIEndpoints.CreatePeriodicAIP),
            "UpdateCustomer": ("POST", APIEndpoints.UpdateCustomer),
            "TradeInfoSearch": ("POST", APIEndpoints.TradeInfoSearch),
            "GetSWPTradeRequestHistory": ("POST", APIEndpoints.GetSWPTradeRequestHistory),
            "restrictedCash": ("GET", APIEndpoints.RestrictedCash),
            "ClientHousehold": ("GET", None),
        }

        if endpoint_name not in endpoint_mapping:
            raise RuntimeError(f"Endpoint '{endpoint_name}' not found in mapping")

        method, base_url = endpoint_mapping[endpoint_name]
        url = base_url

        if endpoint_name == "ClientHousehold":
            if not household_id:
                raise RuntimeError("household_id is required for ClientHousehold endpoint")
            url = APIEndpoints.GetClientHousehold(household_id, filter_value)
            logger.info(f"ClientHousehold URL constructed: {url}")
        elif account_number and method == "GET" and endpoint_name in [
            "GetPeriodicWithdrawalInstruction", "GetCheckPINS", "GetACHBank",
            "GetACHBankForContribution", "BankRoutingNumber", "InstructionOnFile",
            "restrictedCash"
        ]:
            url = base_url + str(account_number)
            if endpoint_name == "GetPeriodicWithdrawalInstruction":
                url += "/GetPeriodicWithdrawalInstruction"
            elif endpoint_name in ["GetCheckPINS", "GetACHBank", "GetACHBankForContribution"]:
                url += "/1/AI0WQ8/true"
            elif endpoint_name == "InstructionOnFile":
                url += "/1/InstructionsOnFile"
            elif endpoint_name == "restrictedCash":
                url += "/restrictedCash"
        elif endpoint_name == "CreatePeriodicAIP" and account_number:
            # CreatePeriodicAIP appends account_number to the path
            url = base_url + str(account_number)

        if headers:
            for key, value in headers.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  (No headers provided)")
        logger.info(f"\nREQUEST BODY:")
        if body:
            logger.info(f"{body}")
        else:
            logger.info(f"  (No body)")
        logger.info(f"{'='*100}\n")
        
        try:
            if method == "POST":
                if body:
                    # Use json= parameter for dict and list bodies to ensure proper JSON encoding
                    if isinstance(body, (dict, list)):
                        response = self.session.post(url, json=body, headers=headers, verify=False, timeout=120)
                    else:
                        # For string bodies, use data= with proper headers
                        response = self.session.post(url, data=body, headers=headers, verify=False, timeout=120)
                else:
                    response = self.session.post(url, headers=headers, verify=False, timeout=120)
            else:
                # For GET requests, remove Content-Type if present
                get_headers = headers.copy() if headers else {}
                get_headers.pop('Content-Type', None)
                response = self.session.get(url, headers=get_headers, verify=False, timeout=120)

            self._last_response = response
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response body: {response.json() if response.content else 'No Content'}")
            return response
        except Exception as e:
            logger.error(f"Error posting to {endpoint_name}: {str(e)}")
            raise RuntimeError(f"Failed to post to {endpoint_name}: {str(e)}")
