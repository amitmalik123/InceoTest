"""
API validation step definitions for BDD tests
"""

import allure
import json
import requests
from datetime import datetime, timedelta
from pytest_bdd import parsers, then, when

from pages.stp.shared.api_utility_page import APIUtilityPage
from tests.api.stp.services.beneficiaryHouseholdService import BeneficiaryHouseholdService
from utils.allure_logger import get_allure_logger
from utils.api_request_utils import APIClient

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
        api_name=api_name,
        expected_status_code=expected_status,
        household_id=household_id
    )
    
    if api_utility_page.last_response:
        allure.attach(
            api_utility_page.last_response.text,
            name=f"{api_name} Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    assert is_valid, f"{api_name} API validation failed. Expected status code {expected_status}, got {api_utility_page.last_response.status_code if api_utility_page.last_response else 'No response'}"
    
    logger.info(f"{api_name} API validation completed successfully")


@when('User should generate bearer token for Cancel_SWP')
def generate_access_token_cancel_swp(test_context):
    """Generate OAuth bearer token for Cancel_SWP and store in test_context."""
    logger.info("Generating bearer token for Cancel_SWP")
    client = APIClient(session=requests.Session(), base_url="")
    token = client.get_bearer_token_cancel_swp()
    test_context["cancel_swp_access_token"] = token
    test_context["cancel_swp_api_client"] = client
    logger.info("Bearer token generated and stored in test_context['cancel_swp_access_token']")


@when('User should generate bearer token for Beta Access')
def generate_access_token_beta_access(test_context):
    """Generate OAuth bearer token for Beta Access and store in test_context."""
    logger.info("Generating bearer token for Beta Access")
    client = APIClient(session=requests.Session(), base_url="")
    token = client.get_bearer_token_cancel_swp()
    test_context["access_token"] = token
    test_context["beta_access_token"] = token
    test_context["api_client"] = client
    logger.info("Bearer token generated and stored in test_context['access_token']")
    logger.info(f"Access Token: {token}")


@when('User should add request header parameters For cancelSWP')
def add_headers_cancel_swp(test_context):
    logger.info("Adding request header parameters for CancelSWP")

    token = test_context.get("cancel_swp_access_token")
    client: APIClient = test_context.get("cancel_swp_api_client")
    
    headers = client.adding_header_parameters_cancel_swp_create_instruction(token, api_version="v1")
    test_context["cancel_swp_request_headers"] = headers
    test_context["cancel_swp_api_client"] = client
    logger.info("Request headers for CancelSWP stored in test_context['cancel_swp_request_headers']")


@when(parsers.parse('User should add request header parameters For "{api_name}"'))
@then(parsers.parse('User should add request header parameters For "{api_name}"'))
def add_request_headers_for_api(api_name: str, test_context: dict):
    logger.info(f"Adding request header parameters for API: {api_name}")

    api_client_key = f"{api_name.lower()}_api_client"
    client: APIClient = test_context.get(api_client_key) or test_context.get("api_client")
    if not client:
        client = APIClient(session=requests.Session(), base_url="")

    api_token_key = f"{api_name.lower()}_access_token"
    token = test_context.get(api_token_key) or test_context.get("access_token")
    
    headers = None
    
    if api_name in ["GetPeriodicWithdrawalInstruction", "GetCheckPINS", "GetACHBank", 
                    "GetACHBankForContributions", "ClientHousehold", "InstructionOnFile", "restrictedCash"]:
        headers = client.adding_header_parameters_for_cancel_swp()
        
    elif api_name in ["GetSWPTradeRequestHistory", "BankRoutingNumber"]:
        headers = client.adding_header_parameters_for_cancel_swp_trade_request_history()
        
    elif api_name in ["AddACHBankInstructions", "GetCustomersByAccount", "ACHInstructionSubmissionRequest",
                      "GetAccountsBySSNAndAgentId", "GetCustomerDetails", "CreatePeriodicAIP"]:
        headers = client.adding_header_parameters_for_add_ach_instructions()
        
    elif api_name in ["GetAccountDetail", "updateAccountForBeta"]:
        if not token:
            logger.warning(f"No access token found for {api_name}, generating new token")
            token = client.get_bearer_token_cancel_swp()
            test_context[api_token_key] = token
            test_context["access_token"] = token
        headers = client.adding_header_parameters_dm2_beta_access(token)
        
    elif api_name in ["GetAccountCustomAttributes", "UpdateAccountCustomAttributes", "GetACHInstructionsByAccount",
                      "GetPayeeInstructions", "GetDocumentsListByAccount", "DeleteDocumentForAccount",
                      "GetPeriodicWithdrawalInstructionsByAccount"]:
        if not token:
            logger.warning(f"No access token found for {api_name}, generating new token")
            token = client.get_bearer_token_cancel_swp()
            test_context[api_token_key] = token
            test_context["access_token"] = token
        headers = client.adding_header_parameters_cancel_swp_create_instruction(token, api_version="v1")
        
    elif api_name == "UpdateCustomer":
        if not token:
            logger.warning(f"No access token found for {api_name}, generating new token")
            token = client.get_bearer_token_cancel_swp()
            test_context[api_token_key] = token
            test_context["access_token"] = token
        headers = client.adding_header_parameters_cancel_swp_create_instruction(token, api_version="v2")
        
    elif api_name == "DMT_ManageInstructions_SLOA":
        headers = client.adding_header_parameters_for_dmt_manage_instructions()
        
    elif api_name == "validateConflictingOAs":
        headers = client.adding_header_parameters_for_validate_conflicting_oas()
        
    elif api_name == "TradeInfoSearch":
        if not token:
            logger.warning(f"No access token found for {api_name}, generating new token")
            token = client.get_bearer_token_cancel_swp()
            test_context[api_token_key] = token
            test_context["access_token"] = token
        headers = client.adding_header_parameters_for_ewm30(token)
        
    else:
        logger.warning(f"Unknown API name: {api_name}, using default headers")
        headers = {"accept": "text/plain"}
        client.session.headers.update(headers)

    test_context[f"{api_name.lower()}_request_headers"] = headers
    test_context[f"{api_name.lower()}_api_client"] = client
    test_context["request_headers"] = headers
    test_context["api_client"] = client

    logger.info(f"Added headers for {api_name}: {headers}")


@when(parsers.parse('User should design request body for "{meth}" and accType "{acctype}"'))
def design_request_body_cancel_swp(meth, acctype, test_context):
    """Design and store the request body for Cancel SWP based on withdrawal method."""
    logger.info(f"Designing request body for method '{meth}' and account type '{acctype}'")

    test_data = test_context.get("test_data", {})
    account_number = test_data.get("destination_account") or test_data.get("destination_account")
    
    if not account_number:
        account_number = test_context.get("destination_account")
    
    if not account_number:
        raise RuntimeError("account_number not found in test_context; ensure test data is loaded")

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")

    client: APIClient = test_context.get("cancel_swp_api_client")
    if not client:
        client = APIClient(session=requests.Session(), base_url="")

    body_json = client.design_request_body_cancel_swp(meth, acctype, account_number, tomorrow_date)
    
    test_context["cancel_swp_request_body"] = body_json
    test_context["cancel_swp_api_client"] = client

    with allure.step(f"Design request body for {meth} and {acctype}"):
        logger.info(f"Request body designed and stored: {body_json}")
        allure.attach(body_json, name="Request Body", attachment_type=allure.attachment_type.JSON)


@when(parsers.parse('User should design request body for state as "{state}" and postal code as "{code}" by updateAccountForBeta for SWP Establish'))
def design_request_body_update_account_beta(state: str, code: str, test_context: dict):
    """Design and store the request body for updateAccountForBeta endpoint"""
    logger.info(f"Designing request body for updateAccountForBeta: state={state}, postal_code={code}")
    
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("account_number") or test_data.get("destination_account")
    
    if not account_number:
        account_number = test_context.get("account_number")
    
    if not account_number:
        raise RuntimeError("account_number not found in test_context; ensure test data is loaded")
    
    body = {
        "requestHeader": {
            "externalReferenceId": "9daabc98-c969-43ad-94c1-0169d9370134",
            "applicationId": "amk-svc-02",
            "custodialId": "WWS",
            "requestor": {
                "identity": "2352683",
                "identityType": "SubId"
            },
            "requestAction": "Submit"
        },
        "updateAccountRequest": {
            "processingInstruction": "Submit",
            "accountNumber": int(account_number),
            "accountHolderInformation": {
                "contactInformation": {
                    "addressInformation": {
                        "state": state,
                        "postalCode": str(code)
                    }
                }
            }
        }
    }
    
    # Don't convert to JSON string - pass dict directly for proper JSON serialization
    test_context["request_body"] = body
    test_context["cancel_swp_request_body"] = body
    
    with allure.step(f"Design request body for updateAccountForBeta"):
        body_json = json.dumps(body)  # Only for logging
        logger.info(f"Request body: {body_json}")
        allure.attach(body_json, name="UpdateAccountForBeta Request Body", attachment_type=allure.attachment_type.JSON)


@when(parsers.parse('User should design request body for "{accountAddress}" API'))
def add_body_for_get_withdrawal_instruction_by_account(accountAddress, test_context):
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("destination_account") or test_data.get("account_number")
    
    if not account_number:
        account_number = test_context.get("destination_account") or test_context.get("account_number")
    
    if not account_number:
        raise RuntimeError("account_number not found in test_data or test_context")
    
    account_number_int = int(account_number) if str(account_number).replace('-', '').isdigit() else account_number
    
    json_string = (
        '{'
        '"requestHeader":{'
            '"externalReferenceId":"9daabc98-c969-43ad-94c1-0169d9370134",'
            '"applicationId":"amk-svc-02",'
            '"custodialId":"WWS",'
            '"requestor":{'
                '"identity":"2426862",'
                '"identityType":"SubId"'
            '},'
            '"requestAction":"Submit"'
        '},'
        '"getPeriodicWithdrawalInstructionsByAccountRequest":{'
            f'"accountNumber":{account_number_int},'
            '"instructionStatus":"Active"'
        '}'
        '}'
    )

    logger.info(f"the body is - {json_string}")
    test_context["request_body"] = json_string
    test_context["cancel_swp_request_body"] = json_string


@when(parsers.parse('User should post the response for "{endpoint_name}" endpoint'))
@then(parsers.parse('User should post the response for "{endpoint_name}" endpoint'))
def post_response_for_endpoint(endpoint_name, test_context):
    logger.info(f"Posting to endpoint: {endpoint_name}")

    api_client_key = f"{endpoint_name.lower()}_api_client"
    client: APIClient = test_context.get(api_client_key) or test_context.get("cancel_swp_api_client") or test_context.get("api_client")
    if not client:
        client = APIClient(session=requests.Session(), base_url="")

    test_data = test_context.get("test_data", {})
    account_number = test_data.get("destination_account") or test_data.get("destination_account")

    get_endpoints = [
        "GetPeriodicWithdrawalInstruction", "GetCheckPINS", "GetACHBank",
        "GetACHBankForContributions", "BankRoutingNumber", "InstructionOnFile",
        "restrictedCash", "GetDocumentsListByAccount", "ClientHousehold"
    ]
    
    body = None if endpoint_name in get_endpoints else (
        test_context.get("request_body") or 
        test_context.get("cancel_swp_request_body") or
        test_context.get(f"{endpoint_name.lower()}_request_body")
    )
    household_id = test_context.get("household_id")
    filter_value = "false"
    
    if endpoint_name == "ClientHousehold":
        filter_value = "true"

    headers_key = f"{endpoint_name.lower()}_request_headers"
    headers = test_context.get(headers_key) or test_context.get("request_headers") or test_context.get("cancel_swp_request_headers")

    response = client.post_response_for_endpoint(
        endpoint_name, 
        account_number=account_number, 
        body=body,
        household_id=household_id,
        filter_value=filter_value,
        headers=headers
    )

    test_context["last_api_response"] = response
    test_context[f"{endpoint_name.lower()}_api_client"] = client
    test_context["api_client"] = client

    with allure.step(f"Post response for {endpoint_name}"):
        logger.info(f"Response received with status code: {response.status_code}")
        allure.attach(
            response.text if response.text else "No response body",
            name=f"{endpoint_name} Response",
            attachment_type=allure.attachment_type.JSON if response.headers.get("content-type", "").find("json") >= 0 else allure.attachment_type.TEXT
        )


@then('User should verify the response body to confirm creation of instruction')
def verify_creation_of_instruction(test_context):
    """Verify response body contains a creation status of 'SUCCESS' or 'FAILURE'."""
    response = test_context.get("last_api_response")
    if response is None:
        raise RuntimeError("No last_api_response found in test_context; ensure a request was made before verification")

    with allure.step("Verify creation of instruction status in response"):
        client: APIClient = test_context.get("cancel_swp_api_client")
        if not client:
            client = APIClient(session=requests.Session(), base_url="")

        status = client.retriving_value_object_from_response(response, "responseHeader.status")

        if status == "SUCCESS":
            assert status == "SUCCESS", f"The status is --> {status}"
        else:
            assert status == "FAILURE", f"The status is --> {status}"

        logger.info("The status is %s", status)


@then(parsers.parse('User should verify status code {code:d}'))
def verify_status_code(code: int, test_context: dict):
    """Verify last API response status code equals expected code."""
    response = test_context.get("last_api_response")
    if response is None:
        raise RuntimeError("No last_api_response found in test_context; ensure a request was made before verification")

    with allure.step(f"Verify response status code is {code}"):
        actual = getattr(response, 'status_code', None)
        assert actual == code, f"Expected status code {code}, got {actual}. Response body: {getattr(response, 'text', '')}"
        logger.info(f"Verified response status code: {actual}")


@when("User should add request body parameters for createPerodicAIP")
def add_body_parameters_for_create_periodic_aip(test_context: dict):
    """Add request body parameters for CreatePeriodicAIP endpoint"""
    logger.info("Adding request body parameters for CreatePeriodicAIP")
    
    # Get or create API client
    client: APIClient = test_context.get("cancel_swp_api_client")
    if not client:
        client = APIClient(session=requests.Session(), base_url="")
    
    # Design the CreatePeriodicAIP request body
    body = {
        "processingInstruction": "Submit",
        "dollarAmount": 400.09,
        "frequency": "Monthly",
        "beginningDate": "2025-05-30",
        "endDate": "",
        "periodicSourceCode": "IRACC",
        "externalId": "A003023996",
        "instanceId": "234284",
        "achInstructionNumber": "1",
        "accountId": "AK5825",
        "accountName": "Dave L Achstein, Rollover IRA"
    }
    
    # Store body in test context
    test_context["request_body"] = body
    test_context["cancel_swp_api_client"] = client
    
    logger.info("Request body parameters added for CreatePeriodicAIP")
    logger.info(f"Request body: {body}")


@when("User should add request body parameters for TradeInfoSearch API")
@then("User should add request body parameters for TradeInfoSearch API")
def add_body_parameters_for_trade_info_search(test_context: dict):
    logger.info("")
    
    account_id = test_context.get("account_id")
    
    body = [account_id]
    
    test_context["request_body"] = body
    print(f"Adding Body to Request: {body}")
    
    logger.info("")


@then(parsers.parse('User should verify status code {status_code:d} for ClientHousehold Accounts Display'))
def verify_status_code_for_client_household(status_code: int, test_context: dict):

    with allure.step(f"Verify status code {status_code} for ClientHousehold Accounts Display"):
        # Retrieve the API response from test_context
        response = test_context.get("last_api_response")
        
        if not response:
            raise ValueError("No API response found in test_context. Ensure an API call was made prior to this step.")
        
        actual_status_code = response.status_code
        
        logger.info(f"Verifying status code - Expected: {status_code}, Actual: {actual_status_code}")
        
        try:
            assert actual_status_code == status_code, \
                f"Status code mismatch. Expected: {status_code}, Got: {actual_status_code}"
            
            # Store validation result
            test_context['validate_api_success'] = True
            
            logger.info(f"Status code verification passed: {actual_status_code}")
            
            allure.attach(
                f"Expected Status Code: {status_code}\nActual Status Code: {actual_status_code}\nValidation: PASSED",
                name="ClientHousehold Status Code Verification",
                attachment_type=allure.attachment_type.TEXT
            )
            
        except AssertionError as e:
            test_context['validate_api_success'] = False
            
            logger.error(f"Status code verification failed: {str(e)}")
        
            allure.attach(
                f"Expected Status Code: {status_code}\nActual Status Code: {actual_status_code}\n\nResponse Body:\n{response.text[:500]}",
                name="ClientHousehold Status Code Verification FAILED",
                attachment_type=allure.attachment_type.TEXT
            )
            
            raise


@then("User should extract details from TradeInfoSearch API and store it in generic variables")
def extract_details_from_trade_info_search(test_context: dict):
    response = test_context.get("last_api_response")
    
    if not response:
        raise ValueError("No API response found in test_context")
    
    response_json = response.json()
    
    account_trade_info_list = response_json.get("accountTradeInfo")
    
    trade_info = account_trade_info_list[0]
    
    print(trade_info)
    
    test_context["accountTradeInfo"] = trade_info


@when(parsers.parse('User sends GET request to Beneficiary Household API with household ID "{household_id}"'))
def send_get_request_beneficiary_household(household_id: str, api_utility_page: APIUtilityPage, test_context: dict):
    """Send GET request to Beneficiary Household API and store response in test_context"""
    logger.info(f"Sending GET request to Beneficiary Household API with household ID: {household_id}")
    
    with allure.step(f"GET Beneficiary Household data for ID: {household_id}"):
        depth = test_context.get("api_depth", 1)
        response = api_utility_page.getBeneficiaryHouseholdData(household_id, depth)
        
        test_context["beneficiary_household_response"] = response
        test_context["last_api_response"] = response
        test_context["household_id"] = household_id
        
        allure.attach(
            response.text,
            name=f"Beneficiary Household Response - {household_id}",
            attachment_type=allure.attachment_type.JSON
        )
        
        logger.info(f"GET request completed. Status Code: {response.status_code}")


@then(parsers.parse('User should receive status code "{status_code}" from Beneficiary Household API'))
def validate_beneficiary_household_status_code(status_code: str, api_utility_page: APIUtilityPage, test_context: dict):
    """Validate response status code from Beneficiary Household API"""
    logger.info(f"Validating Beneficiary Household API response status code: {status_code}")
    
    expected_status_code = int(status_code)
    response = test_context.get("beneficiary_household_response")
    
    if not response:
        raise ValueError("No Beneficiary Household API response found in test_context")
    
    actual_status_code = response.status_code
    
    with allure.step(f"Verify status code is {expected_status_code}"):
        assert actual_status_code == expected_status_code, \
            f"Expected status code {expected_status_code} but got {actual_status_code}"
        
        test_context["api_validation_success"] = True
        
        logger.info(f"Status code validation passed: {actual_status_code} == {expected_status_code}")
        
        allure.attach(
            f"Expected: {expected_status_code}\nActual: {actual_status_code}\nValidation: PASSED",
            name="Beneficiary Household Status Code Validation",
            attachment_type=allure.attachment_type.TEXT
        )


@then('User should extract account holder names from Beneficiary Household API response')
def extract_account_holder_names(test_context: dict, beneficiary_household_service, manage_bene_page):
    """Extract account holder names from API response, get names from page, and compare"""
    logger.info("Extracting account holder names from Beneficiary Household API response and comparing with page")
    
    response = test_context.get("beneficiary_household_response")
    
    if not response:
        raise ValueError("No Beneficiary Household API response found in test_context")
    
    with allure.step("Extract and Compare Account Holder Names"):
        # Get names from API response
        api_account_holder_names = beneficiary_household_service.getAccountHolderNames(response)
        test_context["api_account_holder_names"] = api_account_holder_names
        test_context["account_holder_count"] = len(api_account_holder_names)
        
        logger.info(f"Extracted {len(api_account_holder_names)} account holder names from API: {api_account_holder_names}")
        
        # Get names from page UI
        page_account_holder_names = manage_bene_page.get_all_account_holder_names()
        test_context["page_account_holder_names"] = page_account_holder_names
        
        logger.info(f"Found {len(page_account_holder_names)} account holder names on page: {page_account_holder_names}")
        
        # Compare API and Page names
        assert len(api_account_holder_names) == len(page_account_holder_names), \
            f"Account holder count mismatch: API has {len(api_account_holder_names)}, Page has {len(page_account_holder_names)}"
        
        for api_name in api_account_holder_names:
            assert api_name in page_account_holder_names, \
                f"Account holder '{api_name}' from API not found on page. Page names: {page_account_holder_names}"
        
        logger.info(f"All API account holder names match with page UI")
        
        allure.attach(
            f"API Names:\n" + "\n".join(api_account_holder_names) + 
            f"\n\nPage Names:\n" + "\n".join(page_account_holder_names) +
            f"\n\nValidation: PASSED - All names match",
            name="Account Holder Names Comparison",
            attachment_type=allure.attachment_type.TEXT
        )


@when(parsers.parse('User sends GET request to Beneficiary Household API with household ID "{household_id}" and depth "{depth}"'))
def send_beneficiary_household_api_request(household_id, depth, test_context, beneficiary_household_service):

    logger.info(f"Sending GET request to Beneficiary Household API - ID: {household_id}, Depth: {depth}")
    
    response = beneficiary_household_service.getBeneficiaryHouseholdData(
        household_id=household_id,
        depth=int(depth)
    )
    
    test_context["beneficiary_household_response"] = response
    test_context["last_api_response"] = response
    test_context["household_id"] = household_id
    test_context["api_depth"] = int(depth)
    
    logger.info(f"API request completed with status code: {response.status_code}")
    
    allure.attach(
        response.text,
        name=f"Beneficiary Household Response - {household_id} (Depth: {depth})",
        attachment_type=allure.attachment_type.JSON
    )

