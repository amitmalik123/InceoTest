"""Account Setup Step Definitions for BDD tests"""

import logging
from playwright.sync_api import Page
from pytest_bdd import when, then, parsers

from pages.ewm.account_setup_page import AccountSetupPage
from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger


logger = get_allure_logger(__name__)


class AccountSetupStep:
    """Helper class for account setup step methods"""

    def __init__(self, test_context: dict, account_setup_page: AccountSetupPage):
        """
        Initialize AccountSetupStep
        
        Args:
            test_context: Test context containing test data
            account_setup_page: AccountSetupPage instance
        """
        self.test_context = test_context
        self.account_setup_page = account_setup_page
        self.test_data = test_context.get("test_data", {})
        self.reg_type = None
        self.custodian = None

    def get_reg_type_and_custodian(self):
        """Extract registration type and custodian from test data"""
        reg_types = self.test_data.get("RegistrationType", "").split(",")
        if len(reg_types) <= 1:
            self.reg_type = reg_types[0].strip()
        else:
            self.reg_type = reg_types[1].strip()
        
        self.custodian = self.test_data.get("Custodian", "")
        logger.info(f"Registration Type: {self.reg_type}, Custodian: {self.custodian}")


# ========== STEP DEFINITIONS ==========

@when("User navigates to account holder tab and enter require information")
def step_navigate_to_account_setup_page_and_enter_data(test_context, account_setup_page: AccountSetupPage):
    """Navigate to account setup page and enter required account holder information"""
    logger.info("Starting account setup step")
        
    # Initialize step helper
    step_helper = AccountSetupStep(test_context, account_setup_page)
    step_helper.get_reg_type_and_custodian()
        
    test_data = test_context.get("test_data", {})
        
    # Verify custodial interview page list
    account_setup_page.verify_custodial_interview_page_list(
        test_data.get("ClientType", ""),
        step_helper.custodian
    )
        
    # Verify donor page text if applicable
    account_setup_page.verify_donor_page_text(
        test_data.get("ClientType", ""),
        step_helper.custodian
    )
        
    # Click add new account
    account_setup_page.click_add_new_account(
        test_data.get("ClientType", ""),
        step_helper.reg_type,
        "click Account Holder button: "
    )
        
    # Add account information
    account_setup_page.add_account(
        test_data.get("ClientType", ""),
        test_data.get("AccountHolderFirstName", ""),
        test_data.get("AccountHolderMiddleName", ""),
        test_data.get("AccountHolderLastName", ""),
        test_data.get("AccountHolderBirthDate", ""),
        test_data.get("AccountHolderSSN", ""),
        "Add Account Holder info: ",
        "enter account holder info session"
    )
        
    # Add phone and email
    account_setup_page.add_phone_and_email(
        test_data.get("AccountHolderPhone", ""),
        test_data.get("AccountHolderEmail", "")
    )
        
    # Add home address
    account_setup_page.add_account_home_address(
        test_data.get("AccountHolderAddressLine1", ""),
        test_data.get("AccountHolderCity", ""),
        test_data.get("AccountHolderState", ""),
        test_data.get("AccountHolderZip", ""),
        "Address info: ",
        "enter address details on address modal"
    )
        
    # Add mother's maiden name if applicable
    account_setup_page.add_mother_maiden_name(
        test_data.get("ClientType", ""),
        step_helper.custodian,
        step_helper.reg_type,
        "abcde"
    )
        
    # Add custodian-specific information
    account_setup_page.add_custodian_info(
        step_helper.custodian,
        step_helper.reg_type,
        test_data.get("ClientType", ""),
        test_data.get("EmploymentStatus", ""),
        test_data.get("SourceOfIncome", ""),
        test_data.get("AccountHolderAddressLine1", "")
    )
        
    # Save account
    account_setup_page.save_account(
        test_data.get("ClientType", ""),
        "Save button: ",
        "click on account holder save button"
    )
    account_setup_page.notSavedError()
        
    logger.info("Account setup page navigation and data entry completed successfully")


@when("User navigates to trustee tab and enter require information")
def step_navigate_to_trustee_tab_and_enter_data(test_context, account_setup_page: AccountSetupPage):
    """Navigate to trustee tab and enter required trustee information"""
    logger.info("Starting trustee setup step")
        
    # Initialize step helper
    step_helper = AccountSetupStep(test_context, account_setup_page)
    step_helper.get_reg_type_and_custodian()
        
    test_data = test_context.get("test_data", {})
        
    # Click add new account (for trustee) - passing reg_type directly
    account_setup_page.click_add_new_account(
        test_data.get("ClientType", ""),
        step_helper.reg_type,
        "click Account Holder button: "
    )
        
    # Add account information
    account_setup_page.add_account(
        test_data.get("ClientType", ""),
        test_data.get("AccountHolderFirstName", ""),
        test_data.get("AccountHolderMiddleName", ""),
        test_data.get("AccountHolderLastName", ""),
        test_data.get("AccountHolderBirthDate", ""),
        test_data.get("AccountHolderSSN", ""),
        "Add Account Holder info: ",
        "enter account holder info session"
    )
        
    # Add phone and email
    account_setup_page.add_phone_and_email(
        test_data.get("AccountHolderPhone", ""),
        test_data.get("AccountHolderEmail", "")
    )
        
    # Add home address
    account_setup_page.add_account_home_address(
        test_data.get("AccountHolderAddressLine1", ""),
        test_data.get("AccountHolderCity", ""),
        test_data.get("AccountHolderState", ""),
        test_data.get("AccountHolderZip", ""),
        "Address info: ",
        "enter address details on address modal"
    )
        
    # Add custodian-specific information (matching Java - 4 required params, source_of_income optional)
    account_setup_page.add_custodian_info(
        step_helper.custodian,
        step_helper.reg_type,
        test_data.get("ClientType", ""),
        test_data.get("EmploymentStatus", ""),
        test_data.get("SourceOfIncome", ""),
        test_data.get("AccountHolderAddressLine1", "")
    )
        
    # Save account
    account_setup_page.save_account(
        test_data.get("ClientType", ""),
        "Save button: ",
        "click on beneficiary save button"
    )
        
    logger.info("Trustee setup page navigation and data entry completed successfully")


@then("User clicks on account information button")
def step_navigate_to_account_information_page(account_setup_page: AccountSetupPage):
    """Click on account information button"""
    account_setup_page.click_account_information_button(
        "Account information button: ",
        "click on account information button"
    )
    logger.info("Clicked on account information button")


@then("User clicks on account features button")
def step_clicks_on_account_features_button(
    test_context: dict, account_setup_page: AccountSetupPage
):
    """Click on account features button with TMS handling"""
    # Check if TMS is eligible and click TMS button first if needed
    if ConstructPortfolioStep.is_tms_eligible:
        logger.info("TMS eligible - clicking Tax Management Service button first")
        account_setup_page.click_tax_management_service_button(
            "Tax Management Service button: ",
            "click on Tax Management Service button"
        )
        
    # Click account features button
    account_setup_page.click_account_feature_button(
        "Account Feature button: ",
        "click on account feature button"
    )
    logger.info("Clicked on account features button")


@then("User click on online access document delivery button without fundingpage")
def step_click_online_access_document_delivery_button_without_fundingpage(
    account_setup_page: AccountSetupPage
):
    """Click on Online Access & Document Delivery button directly from Account Setup page (C72080)"""
    account_setup_page.click_online_document_delivery_button(
        "Online Document Delivery Button:",
        "Click On Online Document Delivery Button"
    )
    logger.info("Clicked on Online Access & Document Delivery button")


@then("User clicks on LLC Information button")
def step_clicks_on_llc_information_button(account_setup_page: AccountSetupPage):
    """Click on LLC Information button"""
    account_setup_page.click_llc_info_button(
        "LLC Information button: ",
        "click on LLC Information button"
    )
    logger.info("Clicked on LLC Information button")


@then("User clicks on grantor button")
def step_clicks_on_grantor_button(account_setup_page: AccountSetupPage):
    """Click on Grantor or Additional Party button"""
    account_setup_page.click_grantor_button(
        "Grantor button: ",
        "click on grantor button"
    )
    logger.info("Clicked on grantor button")


@then("User clicks on trust information button")
def step_clicks_on_trust_information_button(account_setup_page: AccountSetupPage):
    """Click on Trust Information button"""
    account_setup_page.click_trust_info_button(
        "Trust Information Button: ",
        "Click on Trust Information Button"
    )
    logger.info("Clicked on Trust Information button")


@then("User clicks on Trustors button")
def step_clicks_on_trustors_button(account_setup_page: AccountSetupPage):
    """Click on Trustors button"""
    account_setup_page.click_trustors_button(
        "Trustors Button: ",
        "Click on Trustors Button"
    )
    logger.info("Clicked on Trustors button")


@when("User fills additional account information")
def step_user_fills_additional_account_information(
    test_context: dict, account_setup_page: AccountSetupPage
):
    """Fill additional account information - matches Java accountSetupPage logic"""
    logger.info("Filling additional account information")
    test_data = test_context["test_data"]
        
    # Initialize step helper
    step_helper = AccountSetupStep(test_context, account_setup_page)
    step_helper.get_reg_type_and_custodian()
        
    # Select account from list (only for registration types that show account list)
    # IRA Individual types go directly to form, so skip account list selection
    reg_type_lower = step_helper.reg_type.lower()
    skip_account_list = any(keyword in reg_type_lower for keyword in [
        "ira individual", 
        "roth ira individual",
        "beneficiary roth ira individual",
        "beneficiary ira individual"
    ])
        
    if not skip_account_list:
        first_name = test_data.get("AccountHolderFirstName", "")
        last_name = test_data.get("AccountHolderLastName", "")
    #    account_setup_page.select_account_from_list(first_name, last_name)
    else:
        logger.info(f"Skipping account list selection for {step_helper.reg_type} - goes directly to form")
        
    # 1. Add Info Page SSN (AssetMark Trust 401/Roth IRA Trust, Pershing Roth IRA Trust)
    ssn = test_data.get("AccountHolderSSN", "")
    if ssn:
        account_setup_page.add_info_page_ssn(ssn, step_helper.reg_type, step_helper.custodian)
        
    # 2. Account Additional Info (custodian/registration-specific logic)
    # Get the correct state value from test data
    state_param = test_data.get("State", "")
    source_of_income = test_data.get("SourceOfIncome", "")
        
    account_setup_page.account_additional_info(
        step_helper.reg_type,
        step_helper.custodian,
        test_data.get("AccountHolderFirstName", ""),
        test_data.get("AccountHolderLastName", ""),
        state_param,  # This should be "AA" from CSV
        source_of_income,  # This should be "Gift" from CSV
        test_data.get("TypeOfTrustAddDes", ""),
        test_data.get("MaritalStatus", ""),
        test_data.get("PurposeOfAccount", "General Investing"),
        state_param,  # state_name parameter
        "No",  # sub_advisory_type - from ConstructPortfolioStep.isSubAdvisory
        test_data.get("FAAPaymentMethod", "")
    )
        
    # 4. Select trustees needed to give authorization instructions (AssetMark Trust only)
    trustees_needed = test_data.get("TrusteesNeededToGiveAuthorizationInstructions", "")
    if trustees_needed:
        account_setup_page.select_trusts_needed_to_give_authorizations(
            trustees_needed,
            step_helper.reg_type,
            step_helper.custodian
        )
        
    # 5. Enter date of trust (Fidelity, Pershing, AssetMark Trust)
    date_of_trust = test_data.get("DateOfTrust", "")
    if date_of_trust:
        account_setup_page.enter_date_of_trust(
            date_of_trust,
            step_helper.reg_type,
            step_helper.custodian
        )
        
    # 6. Select type of trust (Fidelity, AssetMark Trust, Pershing Roth IRA Trust)
    type_of_trust = (
        test_data.get("TypeOfTrust_Addtional_Distinction", "")
        or test_data.get("TypeOfTrustAddDes", "")
        or test_data.get("TypeOfTrust", "")
    )
    if type_of_trust:
        account_setup_page.select_type_trust(
            type_of_trust,
            step_helper.reg_type,
            step_helper.custodian
        )
        
    # 7. Enter plan established date (AssetMark Trust 401 accounts only)
    plan_date = test_data.get("PlanWasEstablished", "")
    if plan_date:
        account_setup_page.enter_plan_established_on(
            plan_date,
            step_helper.reg_type,
            step_helper.custodian
        )
        
    # 8. Enter decedent name (AssetMark Roth IRA Trust/Individual)
    first_name = test_data.get("AccountHolderFirstName", "")
    last_name = test_data.get("AccountHolderLastName", "")
    if first_name and last_name:
        account_setup_page.enter_decedent_name(
            first_name,
            last_name,
            step_helper.reg_type,
            step_helper.custodian
        )
        
    # 9. Set IPG Financial Advisor Authorization (IPG channel only)
    fa_auth_level = test_data.get("IPGFAAuthorization", "")
    channel = test_data.get("Channel", "")
    if fa_auth_level or channel:
        account_setup_page.set_ipg_financial_advisor_authorization(
            fa_auth_level,
            channel
        )
       
    # Extra wait and verification for SDBA accounts to ensure fields are filled
    if "self-directed brokerage account" in step_helper.reg_type.lower():
        logger.info("SDBA account detected - adding extra stabilization wait")
        # Wait for page to fully settle after all SDBA fields are filled
        account_setup_page.page.wait_for_load_state("domcontentloaded", timeout=10000)
        account_setup_page.wait_for_loading_data()
        account_setup_page.page.wait_for_timeout(2000)
        logger.info("SDBA account fields filled and page stabilized")

    account_setup_page.notSavedError()
        
    logger.info("Additional account information filled successfully")

@when(parsers.parse("User decides to retain existing account or not {retainAccount}"))
def condition_to_retain_existing_account(
    test_context: dict, account_setup_page: AccountSetupPage, retainAccount: str
):
    """Navigate to Account information page and select existing client"""
    test_context["retain_existing_account_boolean"] = retainAccount
    logger.info(f"Deciding to retain existing account: {retainAccount}")
    account_number = account_setup_page.condition_to_retain_existing_account(test_context, retainAccount)
    if account_number:
        test_context["custodian_account_number"] = account_number
    if retainAccount.lower() == "no":
        logger.info("User chose not to retain existing account, proceeding without setting custodian account number")
        step_clicks_on_account_features_button(test_context, account_setup_page)
        step_clicks_on_funding_method_button(account_setup_page)
        # Enter funding method
        test_data = test_context.get("test_data", {})
        funding_method = test_data.get("FundingMethod", "")
        account_setup_page.enter_funding_method(funding_method)
        # Click online access document delivery button
        account_setup_page.click_online_document_delivery_button(
            "Online Access & Document Delivery button: ",
            "click on Online Access & Document Delivery button on Funding tab"
        )
             

@when("Navigate to Account information page and select existing client")
def step_navigate_to_account_information_and_select_existing_client(
    test_context: dict, account_setup_page: AccountSetupPage
):
    """Navigate to Account information page and select existing client"""
    logger.info("Selecting existing client for account")
        
    # Initialize step helper
    step_helper = AccountSetupStep(test_context, account_setup_page)
    step_helper.get_reg_type_and_custodian()
        
    test_data = test_context.get("test_data", {})
        
    # Click existing account with required parameters
    account_setup_page.click_existing_account(
        custodian=step_helper.custodian,
        reg_type=step_helper.reg_type,
        first_name=test_data.get("AccountHolderFirstName", ""),
        last_name=test_data.get("AccountHolderLastName", ""),
        date_of_birth=test_data.get("AccountHolderBirthDate", ""),
        country_name=test_data.get("Country", "")
    )
        
    logger.info("Successfully selected existing client")


@when("Navigate to LLC information page and enter info")
def step_navigate_to_llc_information_page_and_enter_info(test_context: dict, account_setup_page: AccountSetupPage):
    """Navigate to LLC information page and enter required information"""
    # Initialize step helper
    step_helper = AccountSetupStep(test_context, account_setup_page)
    step_helper.get_reg_type_and_custodian()
        
    test_data = test_context.get("test_data", {})
        
    # Add TIN number
    account_setup_page.add_tin_number(
        step_helper.custodian,
        step_helper.reg_type,
        test_data.get("AccountHolderSSN", "")
    )
        
    # Select LLC type
    account_setup_page.select_llc_type(
        step_helper.custodian,
        step_helper.reg_type
    )
        
    # Add beneficial ownership details
    beneficial_data = {
        "first_name": "Elaine",
        "last_name": "Jjessamine",
        "dob": "1/1/1960",
        "ssn": "368367217",
        "address_line1": "1293 Birdnest",
        "city": "Alhambra",
        "state": "CA",
        "zip": "91803"
    }
        
    account_setup_page.add_beneficial_ownership_details(
        step_helper.custodian,
        step_helper.reg_type,
        beneficial_data
    )
    account_setup_page.notSavedError()
        
    logger.info("LLC information entered successfully")


@then("User clicks on funding method button")
def step_clicks_on_funding_method_button(
    account_setup_page: AccountSetupPage
):
    """Click on funding method button"""
    account_setup_page.go_to_funding_method_page(
        "Funding Method button: ",
        "click on Funding Method button"
    )
    logger.info("Clicked on funding method button and navigated to funding page")


@when("User navigates to funding tab and enter funding method")
def step_bdd_navigate_to_funding_tab_and_enter_funding_method(
    test_context: dict, account_setup_page: AccountSetupPage
):
    """Select funding method on funding tab based on custodian type"""
    test_data = test_context.get("test_data", {})
    funding_method = test_data.get("FundingMethod", "")
    account_setup_page.enter_funding_method(funding_method)
    logger.info("Funding method entered successfully")


@then("User click on online access document delivery button")
def step_bdd_click_online_access_document_delivery_button(
    account_setup_page: AccountSetupPage
):
    """Click on Online Access & Document Delivery button"""
    account_setup_page.click_online_document_delivery_button(
        "Online Access & Document Delivery button: ",
        "click on Online Access & Document Delivery button on Funding tab"
    )
    logger.info("Clicked on Online Access & Document Delivery button")


@when("User navigates to online access document delivery tab and click on review all accounts button")
def step_click_review_all_accounts_button(account_setup_page: AccountSetupPage):
    """Click on review all accounts button"""
    account_setup_page.review_all_accounts(
        "Review all accounts button: ",
        "click on review all accounts button"
    )
    logger.info("Clicked on review all accounts button")


@then("User clicks on Participant button")
def step_clicks_on_participant_button(account_setup_page: AccountSetupPage):
    """Click on Participant button"""
    with logger.step("User clicks on Participant button", page=account_setup_page.page):
        account_setup_page.click_participant_button(
            "Participant Button: ",
            "Click on Participant Button"
        )
        logger.info("Clicked on Participant button")


@then("User fills participant information and click on save button")
def step_fills_participant_info_and_save(test_context, account_setup_page: AccountSetupPage, _pytest_bdd_example):
    """Fill participant information and click save"""
    with logger.step("User fills participant information and click on save button", page=account_setup_page.page):
        test_data = test_context.get("test_data", {})
        participant_name = _pytest_bdd_example.get("ParticipantName", "")
        participant_type = _pytest_bdd_example.get("ParticipantType", "New Participant")
        account_setup_page.fill_participant_info(
            first_name=test_data.get("AccountHolderFirstName", ""),
            last_name=test_data.get("AccountHolderLastName", ""),
            birth_date=test_data.get("AccountHolderBirthDate", ""),
            ssn=test_data.get("AccountHolderSSN", ""),
            participant_name=participant_name,
            participant_type=participant_type
        )
        logger.info(f"Filled participant information with ParticipantName='{participant_name}', ParticipantType='{participant_type}' and clicked save")


@then("User clicks on retirement plan information button")
def step_clicks_on_retirement_plan_information_button(account_setup_page: AccountSetupPage):
    """Click on Retirement Plan Information button"""
    with logger.step("User clicks on retirement plan information button", page=account_setup_page.page):
        account_setup_page.click_retirement_plan_info_button(
            "Retirement Plan Information",
            "click retirement plan information button: "
        )
        logger.info("Clicked on Retirement Plan Information button")


@when("User fills Retirement Plan Information")
def step_user_fills_retirement_plan_information(
    test_context: dict, account_setup_page: AccountSetupPage, _pytest_bdd_example
):
    """Fill Retirement Plan Information for 401k accounts"""
    with logger.step("User fills Retirement Plan Information", page=account_setup_page.page):
        logger.info("Filling Retirement Plan Information for 401k")
        test_data = test_context["test_data"]

        step_helper = AccountSetupStep(test_context, account_setup_page)
        step_helper.get_reg_type_and_custodian()

        custodian_lower = step_helper.custodian.lower()

        # 1. Fill TIN number
        tin_number = test_data.get("AccountHolderSSN", "")
        account_setup_page.add_tin_number(step_helper.custodian, step_helper.reg_type, tin_number)

        # Trim Full Legal Title to avoid BAW Max length(30) error
        account_setup_page.trim_full_legal_title()

        # 2. Account Additional Info
        state_param = test_data.get("State", "")
        source_of_income = test_data.get("SourceOfIncome", "")
        account_setup_page.account_additional_info(
            step_helper.reg_type,
            step_helper.custodian,
            test_data.get("AccountHolderFirstName", ""),
            test_data.get("AccountHolderLastName", ""),
            state_param,
            source_of_income,
            test_data.get("TypeOfTrustAddDes", ""),
            test_data.get("MaritalStatus", ""),
            test_data.get("PurposeOfAccount", ""),
            state_param,
            "No",
            test_data.get("FAAPaymentMethod", "")
        )

        # 3. Select trustees needed to give authorization instructions
        trustees_needed = test_data.get("TrusteesNeededToGiveAuthorizationInstructions", "")
        if trustees_needed and "assetmark trust" in custodian_lower:
            account_setup_page.select_trusts_needed_to_give_authorizations(
                trustees_needed,
                step_helper.reg_type,
                step_helper.custodian
            )

        # 4. Enter plan established date
        plan_date = test_data.get("PlanWasEstablished", "")
        if not plan_date:
            plan_date = "01012020"
            logger.info(f"PlanWasEstablished not provided, using default: {plan_date}")
        account_setup_page.enter_plan_established_on(
            str(plan_date),
            step_helper.reg_type,
            step_helper.custodian
        )

        # 5. Validate IRS Plan Document Section
        account_setup_page.validate_irs_plan_document_section(
            step_helper.reg_type,
            step_helper.custodian
        )

        # 6. Select IRS Plan Document type
        irs_plan_docu_type = _pytest_bdd_example.get("IRSPlanDocuType", "")
        epic_email = test_data.get("AccountHolderEmail", "")
        account_setup_page.select_irs_plan_document_type(irs_plan_docu_type, epic_email=str(epic_email).strip() if epic_email else "")

        account_setup_page.notSavedError()
        logger.info("Retirement Plan Information filled successfully")


@when("User fills Trust information")
def step_user_fills_trust_information(
    test_context: dict, account_setup_page: AccountSetupPage
):
    """Fill Trust information - Fidelity Trust specific: state, date of trust, type of trust"""
    with logger.step("User fills Trust information", page=account_setup_page.page):
        logger.info("Filling Trust information")
        test_data = test_context["test_data"]

        # Initialize step helper
        step_helper = AccountSetupStep(test_context, account_setup_page)
        step_helper.get_reg_type_and_custodian()

        # Select account from list
        first_name = test_data.get("AccountHolderFirstName", "")
        last_name = test_data.get("AccountHolderLastName", "")
        account_setup_page.select_account_from_list(first_name, last_name)

        # Account Additional Info (custodian/registration-specific logic)
        state_param = test_data.get("State", "")
        source_of_income = test_data.get("SourceOfIncome", "")

        account_setup_page.account_additional_info(
            step_helper.reg_type,
            step_helper.custodian,
            test_data.get("AccountHolderFirstName", ""),
            test_data.get("AccountHolderLastName", ""),
            state_param,
            source_of_income,
            test_data.get("TypeOfTrustAddDes", ""),
            test_data.get("MaritalStatus", ""),
            test_data.get("PurposeOfAccount", ""),
            state_param,
            "No",
            test_data.get("FAAPaymentMethod", "")
        )

        # Enter date of trust
        date_of_trust = test_data.get("DateOfTrust", "")
        if date_of_trust:
            account_setup_page.enter_date_of_trust(
                date_of_trust,
                step_helper.reg_type,
                step_helper.custodian
            )

        # Select type of trust
        type_of_trust = (
            test_data.get("TypeOfTrust_Addtional_Distinction", "")
            or test_data.get("TypeOfTrustAddDes", "")
            or test_data.get("TypeOfTrust", "")
        )
        if type_of_trust:
            account_setup_page.select_type_trust(
                type_of_trust,
                step_helper.reg_type,
                step_helper.custodian
            )

        account_setup_page.notSavedError()

        logger.info("Trust information filled successfully")
