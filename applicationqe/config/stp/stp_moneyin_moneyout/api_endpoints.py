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
    GetCustomersByAccountForRoth = "https://test.api.assetmark.com/Custodialaccountservicing/Customers/GetCustomersByAccountForRoth"
    GetCustomerDetails = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/CustomerManagement/GetCustomerDetails"
    GetAccountsBySSNAndAgentId = "https://app-maintenanceapi-test-test12.azurewebsites.net/api/v1/CustomerManagement/GetAccountsBySSNAndAgentId"
    UpdateCustomer = (
        "https://test.api.assetmark.com/Custodialaccountservicing/CustomerManagement/UpdateCustomer"
    )

    # ACH Instructions APIs
    CreateACHInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/CreateACHInstruction"
    DeactivateACHInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/DeactivateACHInstruction"
    GetACHInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/GetACHInstructionsByAccount"
    GetACHInstructionsByAccount = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/GetACHInstructionsByAccount"
    CreateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/CreateACHInstruction"
    DeactivateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/DeactivateACHInstruction"
    ActivateACHInstruction = "https://test.api.assetmark.com/Custodialaccountservicing/ACHInstructions/ActivateACHInstruction"
    ACHInstructionSubmissionRequest = "https://app-mnginstruction-test-test11.azurewebsites.net/api/v1/InstructionSubmission/ACHInstructionSubmissionRequest"

    # Bank APIs
    BankRoutingNumber = "https://t01-abaroutingresource-test12.azurewebsites.net/api/v1/BankRoutingNumber/"
    GetACHBank = "https://t01-maintenancebackendapi-test11.aznct01appsvcenvint1.appserviceenvironment.net/api/v1/ACHBank/"
    GetACHBankForContribution = "https://t01-maintenancebackendapi-test11.aznct01appsvcenvint1.appserviceenvironment.net/api/v1/ACHBank/Contribution/"
    AddACHInstructions = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/ACHBank/ACHInstructions"
    GetCheckPINS = "https://t01-maintenancebackendapi-test11.aznct01appsvcenvint1.appserviceenvironment.net/api/v1/CheckPINS/"
    
    # Payee Instructions APIs
    GetPayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/GetPayeeInstructions"
    CreatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/CreatePayeeInstructions"
    ActivatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/ActivatePayeeInstructions"
    DeactivatePayeeInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PayeeInstructions/DeactivatePayeeInstructions"
    
    # Periodic Withdrawal / SWP APIs
    GetPeriodicWithdrawalInstruction = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/SWPInstructionOnFile/"
    GetPeriodicWithdrawalInstructionsByAccount = "https://test.api.assetmark.com/Custodialaccountservicing/PeriodicAccountWithdrawals/GetPeriodicWithdrawalInstructionsByAccount"
    CreatePeriodicWithdrawalInstructions = "https://test.api.assetmark.com/Custodialaccountservicing/PeriodicAccountWithdrawals/CreatePeriodicWithdrawalInstructions"
    GetSWPTradeRequestHistory = "https://func-withdrawalworkflowautomation-test-test12.azurewebsites.net/api/SWPTradeRequestHistory"
    
    # Account Management APIs
    GetAccountDetail = "https://test.api.assetmark.com/Custodialaccountservicing/Accounts/GetAccountDetail"
    UpdateAccountForBeta = "https://test.api.assetmark.com/Custodialaccountservicing/Accounts/updateAccount"
    PostUpdateAccount = "https://test.api.assetmark.com/Custodialaccountservicing/Accounts/updateAccount"
    GetAccountCustomAttributes = "https://test.api.assetmark.com/Custodialaccountservicing/AccountCustomAttributes/GetAccountCustomAttributes"
    UpdateAccountCustomAttributes = "https://test.api.assetmark.com/Custodialaccountservicing/AccountCustomAttributes/UpdateAccountCustomAttributes"
    InstructionsOnFile = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/InstructionsOnFile/"
    RestrictedCash = "https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/OAs/"
    ValidateConflictingOAs = (
        "https://app-maintenanceapi-test-test12.azurewebsites.net/api/v1/OAs/validateConflictingOAs"
    )

    # Document Management APIs
    GetDocumentsListByAccount = "https://test.api.assetmark.com/Custodialaccountservicing/AccountDocuments/GetDocumentsListByAccount"
    DeleteDocumentForAccount = "https://test.api.assetmark.com/Custodialaccountservicing/AccountDocuments/DeleteDocumentForAccount"

    # AIP APIs
    CreatePeriodicAIP = (
        "https://app-mngcontributions-test-test12.azurewebsites.net/api/v1/AIP/CreatePeriodicAIP/"
    )

    # Trade APIs
    TradeInfoSearch = "https://test.tenant1.ewm3.assetmark.net/tradeactions/api/v1/accounts/tradeinfo/search"
    
    # Feature Toggle APIs
    DMT_ManageInstructions_SLOA = "http://fpkt11gss1a:41026/api/featuretoggle/v1/Toggles/DMT_ManageInstructions_SLOA"
    
    # Household APIs
    @staticmethod
    def GetClientHousehold(household_id: str, filter_value: str = "false") -> str:
        """Generate ClientHousehold API URL with household ID and filter value"""
        return f"https://app-maintenanceapi-test-test11.azurewebsites.net/api/v1/Household/{household_id}?accountFilter={filter_value}"
    
    @staticmethod
    def GetBeneficiaryHousehold(household_id: str, depth: int = 1) -> str:
        """Generate Beneficiary Household API URL with household ID and depth parameter"""
        return f"https://application.dev01.assetmark.com/api/bene/v1/Household/{household_id}?depth={depth}"
