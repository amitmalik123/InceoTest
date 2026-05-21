"""
API Endpoint Constants
Contains all API endpoints used for testing
"""


class APIEndpoints:
    """API endpoint URLs for different environments"""
    
    # Base URLs
    BASE_TEST11 = "https://test11.ewealthmanager.com"
    BASE_TEST12 = "https://test12.ewealthmanager.com"
    BASE_API = "https://test.api.assetmark.com"
    
    # Customer Management APIs
    GetCustomersByAccount = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/CustomerManagement/GetCustomersByAccount"
    GetCustomerDetails = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/CustomerManagement/GetCustomerDetails"
    GetAccountsBySSNAndAgentId = "https://app-maintenanceapi-test-test12.azurewebsites.net/api/v1/CustomerManagement/GetAccountsBySSNAndAgentId"
    UpdateCustomer = "https://test.api.assetmark.com/Custodialaccountservicing/CustomerManagement/UpdateCustomer"
    
    # ACH Instructions APIs
    GetACHInstructionsByAccount = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/GetACHInstructionsByAccount"
    CreateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/CreateACHInstruction"
    DeactivateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/DeactivateACHInstruction"
    ActivateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/ActivateACHInstruction"
    ACHInstructionSubmissionRequest = "https://app-mnginstruction-test-test11.azurewebsites.net/api/v1/InstructionSubmission/ACHInstructionSubmissionRequest"
    
    # Bank APIs
    BankRoutingNumber = "https://t01-abaroutingresource-test12.azurewebsites.net/api/v1/BankRoutingNumber/"
    
    # Payee Instructions APIs
    GetPayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/GetPayeeInstructions"
    CreatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/CreatePayeeInstructions"
    ActivatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/ActivatePayeeInstructions"
    DeactivatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/DeactivatePayeeInstructions"
    
    # Account Management APIs
    InstructionsOnFile = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/InstructionOnFile/"
    RestrictedCash = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/OAs/"
    ValidateConflictingOAs = "https://app-maintenanceapi-test-test12.azurewebsites.net/api/v1/OAs/validateConflictingOAs"
    
    # Document Management APIs
    GetDocumentsListByAccount = "https://test.api.assetmark.com/Custodialaccountservicing/AccountDocuments/GetDocumentsListByAccount"
    DeleteDocumentForAccount = "https://test.api.assetmark.com/Custodialaccountservicing/AccountDocuments/DeleteDocumentForAccount"
    
    # AIP APIs
    CreatePeriodicAIP = "https://app-mngcontributions-test-test12.azurewebsites.net/api/v1/AIP/CreatePeriodicAIP/"
    
    # Trade APIs
    TradeInfoSearch = "https://test.tenant1.ewm3.assetmark.net/tradeactions/api/v1/accounts/tradeinfo/search"
    
    # Household APIs
    @staticmethod
    def GetClientHousehold(household_id: str, filter_value: str = "false") -> str:
        """Generate ClientHousehold API URL with household ID and filter value"""
        return f"https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/Household/{household_id}?accountFilter={filter_value}"
    
    # DMT APIs
    DMT_ManageInstructions_SLOA = "https://app-mnginstruction-test-test11.azurewebsites.net/api/v1/InstructionSubmission/DMT_ManageInstructions_SLOA"
