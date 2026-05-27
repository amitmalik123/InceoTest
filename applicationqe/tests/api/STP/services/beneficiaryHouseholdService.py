from tests.api.stp.models.beneficiaryHouseholdModel import BeneficiaryHouseholdModel
from config.stp.stp_moneyin_moneyout.api_endpoints import APIEndpoints
from utils.settings import settings
from utils.allure_logger import get_allure_logger
import requests
import urllib3

# Disable SSL warnings for dev/test environments with self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_allure_logger(__name__)


class BeneficiaryHouseholdService:
    
    def __init__(self):
        self.last_response = None 
    
    def _get_auth_token(self):
        """Get authentication token from settings"""
        return settings.api_auth_token
    
    def getBeneficiaryHouseholdData(self, household_id: str, depth: int = 1):
        """
        Fetch beneficiary household data from API.
        Returns raw response object for validation in step definitions.
        """
        logger.info(f"Fetching beneficiary household data for ID: {household_id}, Depth: {depth}")
        
        url = APIEndpoints.GetBeneficiaryHousehold(household_id, depth)
        
        logger.info(f"API URL: {url}")
        
        headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        }
        
        auth_token = self._get_auth_token()
        if auth_token:
            headers['Authorization'] = auth_token
        
        response = requests.get(url, headers=headers, verify=False)
        self.last_response = response
        
        logger.info(f"Response Status Code: {response.status_code}")
        
        return response
    
    def parseResponseToModel(self, response):
        """
        Parse API response into BeneficiaryHouseholdModel for structured data access.
        
        Args:
            response: requests.Response object
            
        Returns:
            BeneficiaryHouseholdModel if status 200, None otherwise
        """
        if response.status_code == 200:
            try:
                data = response.json()
                model = BeneficiaryHouseholdModel.from_json(data)
                logger.info(f"Parsed response to model: {model.get_household_name()}")
                return model
            except Exception as e:
                logger.error(f"Failed to parse response to model: {e}")
                return None
        return None
    
    def getAccountHolderNames(self, response):
        """
        Extract account holder names from API response.
        
        Args:
            response: requests.Response object
            
        Returns:
            List of account holder names
        """
        if response.status_code == 200:
            try:
                data = response.json()
                account_holders = data.get('dataSource', {}).get('accounts.parties.accountHolders', [])
                names = [holder.get('fullName', '') for holder in account_holders]
                logger.info(f"Found {len(names)} account holders")
                return names
            except Exception as e:
                logger.error(f"Failed to extract account holder names: {e}")
                return []
        return []
    
    def validateHouseholdName(self, response, expected_name: str):
        """
        Validate household name from response.
        Works with both raw response and BeneficiaryHouseholdModel.
        """
        if isinstance(response, BeneficiaryHouseholdModel):
            actual_name = response.get_household_name()
        else:
            data = response.json()
            actual_name = data.get('dataSource', {}).get('meta', {}).get('householdName', '')
        
        assert actual_name == expected_name, \
            f"Expected household name '{expected_name}', but got '{actual_name}'"
        
        logger.info(f"Household name validation passed: {actual_name}")
    
    def validateAccountHolderCount(self, response, expected_count: int):
        """
        Validate account holder count from response.
        Works with both raw response and BeneficiaryHouseholdModel.
        """
        if isinstance(response, BeneficiaryHouseholdModel):
            actual_count = response.get_account_holder_count()
        else:
            data = response.json()
            actual_count = data.get('dataSource', {}).get('meta', {}).get('totalAccountHolders', 0)
        
        assert actual_count == expected_count, \
            f"Expected {expected_count} account holders, but got {actual_count}"
        
        logger.info(f"Account holder count validation passed: {actual_count}")
    
    def validateAccountHolderExists(self, response, holder_name: str):
        """
        Validate that account holder exists in response.
        Works with both raw response and BeneficiaryHouseholdModel.
        """
        if isinstance(response, BeneficiaryHouseholdModel):
            account_holder = response.get_account_holder_by_name(holder_name)
        else:
            data = response.json()
            account_holders = data.get('dataSource', {}).get('accounts.parties.accountHolders', [])
            account_holder = None
            for holder in account_holders:
                if holder.get('fullName') == holder_name:
                    account_holder = holder
                    break
        
        assert account_holder is not None, \
            f"Account holder '{holder_name}' not found in household"
        
        logger.info(f"Account holder validation passed: {holder_name} found")
        
        return account_holder
