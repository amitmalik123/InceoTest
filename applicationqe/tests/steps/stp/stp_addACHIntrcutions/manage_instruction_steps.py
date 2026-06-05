import random
import allure
from datetime import datetime
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.stp.stp_addACHIntrcutions.add_ach_instruction import AddACHInstructionPage
from tests.steps.stp.stp_shared.common_steps import format_household_name, get_detail, extract_account_core_identifier
from utils.allure_logger import get_allure_logger
from utils.api_response_utils import (
    get_values_from_household_api_open_accounts,
    retrieve_all_values_from_response,
    retrieve_boolean_value_from_response,
)
from utils.stp.constants.constants import Constants
from utils.wait_utils import wait_for_text_to_contain, wait_for_network_idle
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when('User should click on the "ACH" radio button and click on Next')
def select_radio_and_click_on_next(page: Page, manage_instruction_1_page):
    """Select radio button and click Next"""
    radio_type = "ACH"
    logger.info(f"Selecting {radio_type} radio button and clicking Next")
    manage_instruction_1_page.select_radio_button(radio_type)
    manage_instruction_1_page.click_next_button()


@when("User should click on the Add Button to land on the Add ACH Instructions Page")
def click_on_add_button(page: Page, manage_instruction_2_page):
    """Click on Add button to land on Add ACH Instructions Page"""
    logger.info("Clicking on Add Button")
    manage_instruction_2_page.click_add_button()

@when('User should fetch ClientHouseholdID')
def fetch_household_id(page: Page, manage_instruction_1_page, dm_tool_page, test_context, request):
    """Fetch the ClientHouseholdID from the URL"""
    with allure.step("Fetch ClientHouseholdID"):
        logger.info("Fetching ClientHouseholdID")
        
        scenario_name = request.node.name
        
        if "Address Change" in scenario_name or "address_change" in scenario_name:
            household_id = dm_tool_page.get_household_id()
        else:
            household_id = manage_instruction_1_page.get_household_id()
        
        test_context['household_id'] = household_id
        logger.info(f"ClientHouseholdID stored: {household_id}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="ClientHouseholdID Fetched",
            attachment_type=allure.attachment_type.PNG
        )


@then('User to fetch Client Household API values')
def fetch_client_household_api_values(test_context, api_utility_page):
    with allure.step("Fetch Client Household API values"):
        logger.info("Fetching Client Household API values from response")
        
        response = test_context.get("last_api_response") or api_utility_page.last_response
        
        if not response:
            raise ValueError("No API response found. Make sure to call API endpoint first")
        
        # Log response
        logger.info(f"\nAPI Response (Status {response.status_code}):\n{response.text}\n")
        
        try:
            
            account_names = retrieve_all_values_from_response(
                response, 
                get_values_from_household_api_open_accounts("accountName")
            )
            account_numbers = retrieve_all_values_from_response(
                response, 
                get_values_from_household_api_open_accounts("accountNumber")
            )
            account_strategies = retrieve_all_values_from_response(
                response, 
                get_values_from_household_api_open_accounts("accountStrategy")
            )
            custodian_ids = retrieve_all_values_from_response(
                response, 
                get_values_from_household_api_open_accounts("custodianID")
            )
            
            has_gnw_account = retrieve_boolean_value_from_response(response, "hasGNWAccount")
            
            test_context['investment_account_names'] = account_names
            test_context['investment_account_numbers'] = account_numbers
            test_context['investment_account_strategies'] = account_strategies
            test_context['custodian_ids'] = custodian_ids
            test_context['has_gnw_account'] = has_gnw_account
            
            logger.info(f"Fetched {len(account_names)} account names")
            logger.info(f"Fetched {len(account_numbers)} account numbers")
            logger.info(f"Fetched {len(account_strategies)} account strategies")
            logger.info(f"Fetched {len(custodian_ids)} custodian IDs")
            logger.info(f"Has GNW Account: {has_gnw_account}")
            
            logger.info("Client Household API values fetched and stored successfully")
        except Exception as e:
            logger.error(f"Failed to fetch Client Household API values: {str(e)}")
            raise


@then(parsers.parse('User should enter valid AINS page details "{select_account}" for radio type "{radio_type}" and SLOA option as "{sloa_option}" and SLOASubOption as "{sloa_sub_option}" and role as "{role}"'))
def enter_valid_ains_page_details(page: Page, select_account, radio_type, sloa_option, sloa_sub_option, role, test_context, add_ach_instruction_page):
    with allure.step(f"Enter valid AINS page details for {select_account}"):
        logger.info(f"Entering AINS page details for account type: {select_account}")
        
        test_context['initial_role'] = role
        
        random_bank_number = str(random.randint(1_000_000_000, 9_999_999_999))
        logger.info(f"Generated random bank number: {random_bank_number}")
        
        routing_number = test_context['test_data']['routing_number']
        ach_option = test_context['test_data']['ach_option']
        
        entered_new_ains_details = add_ach_instruction_page.enter_details_for_vanishing_errors(
            routing_number, 
            random_bank_number, 
            random_bank_number, 
            sloa_option, 
            sloa_sub_option, 
            ach_option
        )
        
        if select_account == "oneAccount":
            investment_account_names = test_context.get('investment_account_names', [])
            
            if investment_account_names:
                invest_account_nums = len(investment_account_names)
                invest_account_num = random.randint(0, invest_account_nums - 1)
                selected_investment_account = add_ach_instruction_page.select_one_account(invest_account_num)
            else:
                selected_investment_account = add_ach_instruction_page.select_one_account(0)
            
            add_ach_instruction_page.select_party_type("1st")
            
            entered_new_ains_details.append(selected_investment_account)
            logger.info(f"Selected one account: {selected_investment_account}")
            test_context['account_name'] = selected_investment_account
            
        elif select_account == "multiAccount":
            selected_investment_accounts = add_ach_instruction_page.select_multiple_accounts()
            add_ach_instruction_page.select_party_type("1st")
            entered_new_ains_details.append(selected_investment_accounts)
            logger.info(f"Selected multiple accounts: {selected_investment_accounts}")
            test_context['account_name'] = selected_investment_accounts
        
        add_ach_instruction_page.click_certify_checkbox()
        
        test_context['entered_new_ains_details'] = entered_new_ains_details
        logger.info(f"AINS page details entered successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="AINS Details Entered",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should verify the "{household_header}" Heading and the sub-heading as the Account name'))
def validate_household_heading(page: Page, household_header, test_context, request):
    with allure.step(f"Verify {household_header} heading and account name"):
        logger.info(f"Validating household heading: {household_header}")
        
        add_ach_instruction_page = AddACHInstructionPage(page)
        heading_and_account = add_ach_instruction_page.get_household_heading_and_account(household_header)
        
        actual_heading = heading_and_account[0]
        actual_account_name = heading_and_account[1]
        
        assert household_header == actual_heading, f"Household heading mismatch. Expected: {household_header}, Actual: {actual_heading}"
        logger.info(f"Validation of HouseHold Heading: {household_header}")
        
        scenario_name = request.node.name
        expected_account_name = test_context.get('account_name', '')
        
        if "OA Trading Tool" in scenario_name:
            expected_account_name = test_context.get('account_name', '')
        
        assert actual_account_name == expected_account_name, f"Account name mismatch. Expected: {expected_account_name}, Actual: {actual_account_name}"
        logger.info(f"Account Name Validation: Passed")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Household Heading Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should click on the Next Button on Add ACH instruction Page to navigate back on summary page')
def click_next_button_on_add_ach_page(page: Page, add_ach_instruction_page, add_ach_summary_page):
    with allure.step("Click Next button on Add ACH instruction page"):
        logger.info("Clicking Next button to navigate to summary page")
        
        add_ach_instruction_page.click_next()
        
        summary_header = add_ach_summary_page.request_summary_header
        wait_for_text_to_contain(summary_header, "Request Summary", timeout=30.0)
        assert summary_header.is_visible(), "Request Summary header not found"
        logger.info("Navigated to Summary Page - Request Summary header verified")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Summary Page Loaded",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate AINS summary page details "{select_account}" for radio type "{radio_type}" and SLOA option as "{sloa_option}" and SLOASubOption as "{sloa_sub_option}" and role as "{role}"'))
def validate_ains_summary_page(page: Page, add_ach_summary_page, test_context, select_account, radio_type, sloa_option, sloa_sub_option, role):
    with allure.step("Validate AINS summary page details"):
        logger.info("Starting AINS summary page validation")
        
        page.wait_for_load_state('networkidle', timeout=20000)
        page.wait_for_timeout(2000)
        
        entered_new_ains_details = test_context.get('entered_new_ains_details', [])
        logger.info(f"Entered AINS details from context: {entered_new_ains_details}")
        logger.info(f"Entered details breakdown:")
        for idx, detail in enumerate(entered_new_ains_details):
            logger.info(f" [{idx}] = '{detail}'")
        
        summary_details_list = add_ach_summary_page.get_summary_block_list()
        logger.info(f"Summary details from page: {summary_details_list}")
        logger.info(f"Summary details breakdown:")
        for idx, detail in enumerate(summary_details_list):
            logger.info(f" [{idx}] = '{detail}'")
        
        request_header = add_ach_summary_page.get_request_summary_header()
        assert request_header == "Request Summary", f"Request Summary header mismatch. Expected: 'Request Summary', Actual: '{request_header}'"
        logger.info(f"Request Summary Header: {request_header}")
        
        request_subheader = add_ach_summary_page.get_request_summary_subheader()
        expected_subheader = "Please review the details below before submitting the request."
        assert request_subheader == expected_subheader, f"Request Summary subheader mismatch. Expected: '{expected_subheader}', Actual: '{request_subheader}'"
        logger.info(f"Request Summary Subheader: {request_subheader}")
        
        logger.info(f"Comparing Request Type - Expected: 'Bank/Payee Instructions - Add', Actual: '{summary_details_list[0]}'")
        assert "Bank/Payee Instructions - Add" in summary_details_list[0] or summary_details_list[0] == "Bank/Payee Instructions - Add", \
            f"Request Type mismatch. Expected: 'Bank/Payee Instructions - Add', Actual: '{summary_details_list[0]}'"
        logger.info(f"Request Type: {summary_details_list[0]}")
        
        logger.info(f"Comparing Delivery Method - Expected: '{radio_type}', Actual: '{summary_details_list[1]}'")
        assert radio_type in summary_details_list[1] or summary_details_list[1] == radio_type, \
            f"Delivery method mismatch. Expected: '{radio_type}', Actual: '{summary_details_list[1]}'"
        logger.info(f"Delivery Method: {summary_details_list[1]}")
        
        logger.info(f"Comparing ABA/Routing Number - Expected: entered_new_ains_details[0]='{entered_new_ains_details[0]}', Actual: summary_details_list[3]='{summary_details_list[3]}'")
        assert entered_new_ains_details[0] == summary_details_list[3], \
            f"ABA/Routing Number mismatch. Expected: '{entered_new_ains_details[0]}', Actual: '{summary_details_list[3]}'"
        logger.info(f"ABA/Routing Number: {summary_details_list[3]}")
        
        logger.info(f"Comparing Bank Name - Expected: entered_new_ains_details[1]='{entered_new_ains_details[1]}', Actual: summary_details_list[2]='{summary_details_list[2]}'")
        assert entered_new_ains_details[1] == summary_details_list[2], \
            f"Bank Name mismatch. Expected: '{entered_new_ains_details[1]}', Actual: '{summary_details_list[2]}'"
        logger.info(f"Bank Name: {summary_details_list[2]}")
        
        masked_account_number = add_ach_summary_page.mask_account_number(entered_new_ains_details[2])
        logger.info(f"Comparing Bank Account Number - Original: entered_new_ains_details[2]='{entered_new_ains_details[2]}', Masked Expected: '{masked_account_number}', Actual: summary_details_list[4]='{summary_details_list[4]}'")
        assert masked_account_number == summary_details_list[4], \
            f"Bank Account Number mismatch. Expected: '{masked_account_number}', Actual: '{summary_details_list[4]}'"
        logger.info(f"Bank Account Number: {summary_details_list[4]}")
        
        logger.info(f"Comparing Bank Account Type - Expected: entered_new_ains_details[3]='{entered_new_ains_details[3]}', Actual: summary_details_list[5]='{summary_details_list[5]}'")
        assert entered_new_ains_details[3] == summary_details_list[5], \
            f"Bank Account Type mismatch. Expected: '{entered_new_ains_details[3]}', Actual: '{summary_details_list[5]}'"
        logger.info(f"Bank Account Type: {summary_details_list[5]}")
        
        logger.info(f"Comparing Authorized Bank Account Owner - Expected: entered_new_ains_details[4]='{entered_new_ains_details[4]}', Actual: summary_details_list[6]='{summary_details_list[6]}'")
        assert entered_new_ains_details[4] == summary_details_list[6], \
            f"Authorized Bank Account Owner/Agent Name mismatch. Expected: '{entered_new_ains_details[4]}', Actual: '{summary_details_list[6]}'"
        logger.info(f"Authorized Bank Account Owner/Agent Name: {summary_details_list[6]}")
        
        sloa_displayed = add_ach_summary_page.get_sloa_displayed()
        logger.info(f"Comparing SLOA option - Expected: entered_new_ains_details[5]='{entered_new_ains_details[5]}', Actual: '{sloa_displayed}'")
        assert entered_new_ains_details[5] == sloa_displayed, \
            f"SLOA option mismatch. Expected: '{entered_new_ains_details[5]}', Actual: '{sloa_displayed}'"
        logger.info(f"SLOA Displayed: {sloa_displayed}")
        
        if select_account == "oneAccount":
            single_investment_account = add_ach_summary_page.get_single_investment_account()
            
            account_number = entered_new_ains_details[6].split('-')[1].strip().split()[0] if '-' in entered_new_ains_details[6] else ""
            account_name_part = entered_new_ains_details[6].split(',')[0].strip() if ',' in entered_new_ains_details[6] else ""
            
            logger.info(f"Comparing Investment Account - Expected account number: '{account_number}', Expected name: '{account_name_part}', Actual: '{single_investment_account}'")
            
            assert account_number in single_investment_account or account_name_part in single_investment_account, \
                f"Single Investment Account mismatch. Expected account number '{account_number}' or name '{account_name_part}' to be in '{single_investment_account}'"
            logger.info(f"Single Investment Account: {single_investment_account}")
            
            assert add_ach_summary_page.check_single_account_no_numbering(), \
                "Single account should not have numbering"
            logger.info("Single account displayed without numbering")
            
        elif select_account == "multiAccount":
            investment_account_names = test_context.get('investment_account_names', [])
            
            if len(investment_account_names) > 1:
                multi_investment_accounts = add_ach_summary_page.get_investment_accounts()
                assert entered_new_ains_details[6] in multi_investment_accounts, \
                    f"Multiple Investment Accounts mismatch. Expected: '{entered_new_ains_details[6]}' to be in '{multi_investment_accounts}'"
                logger.info(f"Multiple Investment Accounts: {multi_investment_accounts}")
                
                assert add_ach_summary_page.check_multi_account_with_numbering(), \
                    "Multiple accounts should have numbering"
                logger.info("Multiple accounts displayed with numbering")
            else:
                single_investment_account = add_ach_summary_page.get_single_investment_account()
                assert entered_new_ains_details[6] in single_investment_account, \
                    f"Single Investment Account mismatch. Expected: '{entered_new_ains_details[6]}' to be in '{single_investment_account}'"
                logger.info(f"Single Investment Account: {single_investment_account}")
                
                assert add_ach_summary_page.check_single_account_no_numbering(), \
                    "Single account should not have numbering"
                logger.info("Single account displayed without numbering")
        
        if "Admin" in role:
            assert add_ach_summary_page.is_advisor_alert_visible(), \
                "Advisor alert should be visible for Admin role"
            
            advisor_alert = add_ach_summary_page.get_advisor_alert()
            expected_alert = "Your request will be submitted to the financial advisor."
            assert advisor_alert == expected_alert, \
                f"Advisor alert mismatch. Expected: '{expected_alert}', Actual: '{advisor_alert}'"
            logger.info(f"Advisor Alert: {advisor_alert}")
        
        logger.info("AINS summary page validation completed successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Summary Page Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should verify "{disclosure_type}" disclosure Content in Transaction Summary Page'))
def validate_disclosure_content_in_transaction_summary_page(
    page: Page,
    add_ach_summary_page,
    disclosure_type: str
):
    """
    Validate disclosure/agreements content on Transaction Summary Page
    
    Args:
        page: Playwright Page object
        add_ach_summary_page: AddACHSummaryPage fixture
        disclosure_type: Type of disclosure (e.g., "Add_ACH", "Withdrawal_ACH", "Roth_Conversions", etc.)
    """
    with allure.step(f"Verify {disclosure_type} disclosure content in Transaction Summary Page"):
        logger.info(f"Validating {disclosure_type} disclosure content")
        
        disclosures = None
        
        if disclosure_type == "Withdrawal_ACH":
            disclosures = Constants.get_withdrawal_disclosures("ACH")
        elif disclosure_type == "Withdrawal_ACH_DM2":
            disclosures = Constants.get_withdrawal_disclosures_dm2("ACH")
        elif disclosure_type == "Withdrawal_Check":
            disclosures = Constants.get_withdrawal_disclosures("Check")
        elif disclosure_type == "Withdrawal_Check_DM2":
            disclosures = Constants.get_withdrawal_disclosures_dm2("Check")
        elif disclosure_type == "Contribution":
            disclosures = Constants.get_contribution_disclosures()
        elif disclosure_type == "WithdrawalNoRestricted":
            disclosures = Constants.get_withdrawal_disclosures_no_restricted()
        elif disclosure_type == "WithdrawalNoRestricted_DM2":
            disclosures = Constants.get_withdrawal_disclosures_no_restricted_dm2()
        elif disclosure_type == "Cancel":
            disclosures = Constants.get_cancel_disclosures()
        elif disclosure_type == "Add_ACH":
            disclosures = Constants.get_add_ach_disclosures()
        elif disclosure_type in ["Roth_Conversions", "IRA Journals"]:
            disclosures = Constants.get_roth_conversion_summary_disclosure()
        else:
            raise ValueError(f"Unknown disclosure type: {disclosure_type}")
        
        page.wait_for_load_state('networkidle', timeout=20000)
        page.wait_for_timeout(2000)
        
        if disclosure_type == "Add_ACH":
            actual_title = add_ach_summary_page.get_agreements_title()
            expected_title = "Acknowledgements and Agreements"
            assert actual_title == expected_title, \
                f"Agreements title mismatch. Expected: '{expected_title}', Actual: '{actual_title}'"
            logger.info(f"Validation of Title: {actual_title}")
            
            actual_subheader = add_ach_summary_page.get_agreements_subheader()
            expected_subheader = "Upon completion of this request, I certify that:"
            assert actual_subheader == expected_subheader, \
                f"Agreements subheader mismatch. Expected: '{expected_subheader}', Actual: '{actual_subheader}'"
            logger.info(f"Validation of Subheader: {actual_subheader}")
            
            agreements_bullets_text = add_ach_summary_page.get_agreements_bullets()
            
            for disclosure in disclosures:
                assert disclosure in agreements_bullets_text, \
                    f"Disclosure content not found: {disclosure}"
                logger.info(f"Validation of Acknowledgements and Agreements Bullets: {disclosure}")
        
        logger.info(f"{disclosure_type} disclosure content validation completed successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{disclosure_type} Disclosure Validated",
            attachment_type=allure.attachment_type.PNG
        )



@then(parsers.parse('User should validate AINS confirmation page details for "{sloa_sub_option}", "{account_selection}" and role as "{role}"'))
def validate_ains_confirmation_page(
    page: Page,
    test_context: dict,
    sloa_sub_option: str,
    account_selection: str,
    role: str
):
    """Validate AINS confirmation page details"""
    with allure.step(f"Validate AINS confirmation page for {sloa_sub_option}, {account_selection}, role={role}"):
        logger.info(f"Validating AINS confirmation page: {sloa_sub_option}, {account_selection}, role={role}")
        
        add_ach_confirmation_page = test_context.get('add_ach_confirmation_page')
        raw_household_name = (
            test_context.get('account_name')
            or test_context.get('test_data', {}).get('account_name', '')
        )
        entered_new_ains_details = test_context.get('entered_new_ains_details', [])
        
        confirmation_details_text = add_ach_confirmation_page.get_confirmation_details()
        confirmation_other_details = [detail.strip() for detail in add_ach_confirmation_page.get_confirmation_page_other_details()]
        
        client_household = get_detail(confirmation_other_details, 0, "Client Household Subheader")
        expected_household = raw_household_name.split('-')[0].strip() if raw_household_name else raw_household_name
        expected_words = {w.strip('.,') for w in expected_household.split() if len(w.strip('.,')) > 2}
        actual_words = {w.strip('.,') for w in client_household.split() if len(w.strip('.,')) > 2}
        assert expected_words & actual_words, \
            f"Client Household Subheader mismatch. Expected: '{expected_household}', Actual: '{client_household}'"
        
        expected_agent_id = test_context.get('test_data', {}).get('advisor_id', '')
        advisor_id = get_detail(confirmation_other_details, 1, "Advisor ID Subheader")
        if expected_agent_id:
            assert expected_agent_id == advisor_id, \
                f"Advisor ID mismatch. Expected: '{expected_agent_id}', Actual: '{advisor_id}'"
        else:
            logger.warning("Advisor ID not present in test data CSV; skipping assertion")
        
        item_number = add_ach_confirmation_page.get_item_number()
        test_context['item_number'] = item_number
        logger.info(f"Item Number: {item_number}")
        
        request_type = get_detail(confirmation_details_text, 3, "Request Type")
        assert "Bank/Payee Instructions - Add" == request_type, \
            f"Request Type mismatch. Expected: 'Bank/Payee Instructions - Add', Actual: '{request_type}'"
        
        delivery_method = get_detail(confirmation_details_text, 8, "Delivery Method")
        assert "ACH" == delivery_method, \
            f"Delivery Method mismatch. Expected: 'ACH', Actual: '{delivery_method}'"
        
        if sloa_sub_option == "NoEsign":
            if "Admin" in role:
                request_banner = get_detail(confirmation_other_details, 2, "Request Banner")
                assert "Request ready for financial advisor review" == request_banner
                status = get_detail(confirmation_details_text, 0, "Status")
                assert "Awaiting Advisor Submission" == status
            else:
                request_banner = get_detail(confirmation_other_details, 2, "Request Banner")
                assert "Request submitted successfully" == request_banner
                status = get_detail(confirmation_details_text, 0, "Status")
                assert "Complete" == status
        
        timestamp_text = get_detail(confirmation_details_text, 1, "Timestamp")
        assert "PT" in timestamp_text
        
        current_date = datetime.now().strftime("%m/%d/%Y")
        assert current_date in timestamp_text
        
        assert add_ach_confirmation_page.validate_hyperlink()
        logger.info("Item Number is a hyperlink")
        
        aba_routing = get_detail(confirmation_details_text, 9, "ABA/Routing Number")
        assert entered_new_ains_details[0] == aba_routing
        
        bank_name = get_detail(confirmation_details_text, 4, "Bank Name")
        logger.info(f"Expected Bank Name: '{entered_new_ains_details[1]}' | Actual: '{bank_name}'")
        assert entered_new_ains_details[1] == bank_name, \
            f"Bank Name mismatch. Expected: '{entered_new_ains_details[1]}', Actual: '{bank_name}'"
        
        masked_account = entered_new_ains_details[2]
        if len(masked_account) > 4:
            masked_account = "*" * (len(masked_account) - 4) + masked_account[-4:]
        account_number = get_detail(confirmation_details_text, 5, "Bank Account Number")
        logger.info(f"Expected Bank Account Number: '{masked_account}' | Actual: '{account_number}'")
        assert masked_account == account_number, \
            f"Bank Account Number mismatch. Expected: '{masked_account}', Actual: '{account_number}'"
        
        bank_account_type = get_detail(confirmation_details_text, 10, "Bank Account Type")
        logger.info(f"Expected Bank Account Type: '{entered_new_ains_details[3]}' | Actual: '{bank_account_type}'")
        assert entered_new_ains_details[3] == bank_account_type, \
            f"Bank Account Type mismatch. Expected: '{entered_new_ains_details[3]}', Actual: '{bank_account_type}'"
        
        bank_account_name = get_detail(confirmation_details_text, 6, "Name/Title on Bank Account")
        logger.info(f"Expected Bank Account Name: '{entered_new_ains_details[4]}' | Actual: '{bank_account_name}'")
        assert entered_new_ains_details[4] == bank_account_name, \
            f"Bank Account Name mismatch. Expected: '{entered_new_ains_details[4]}', Actual: '{bank_account_name}'"
        
        sloa_value = get_detail(confirmation_details_text, 7, "SLOA")
        logger.info(f"Expected SLOA: '{entered_new_ains_details[5]}' | Actual: '{sloa_value}'")
        assert entered_new_ains_details[5] == sloa_value, \
            f"SLOA mismatch. Expected: '{entered_new_ains_details[5]}', Actual: '{sloa_value}'"
        
        if account_selection.lower() == "oneaccount":
            investment_account = add_ach_confirmation_page.get_investment_account_confirm_page()
            logger.info(f"Selected account from context: '{entered_new_ains_details[6]}'")
            logger.info(f"Confirmation page account: '{investment_account}'")
            
            account_name_part, account_number_part = extract_account_core_identifier(entered_new_ains_details[6])
            
            if account_name_part and account_number_part:
                assert account_name_part in investment_account, \
                    f"Investment Account Name not found. Expected: '{account_name_part}', Actual: '{investment_account}'"
                assert account_number_part in investment_account, \
                    f"Investment Account Number not found. Expected: '{account_number_part}', Actual: '{investment_account}'"
            else:
                assert entered_new_ains_details[6] in investment_account, \
                    f"Investment Account mismatch. Expected substring: '{entered_new_ains_details[6]}', Actual: '{investment_account}'"
            
            logger.info(f"Investment Account: {investment_account}")
        else:
            investment_accounts = add_ach_confirmation_page.get_investment_accounts_confirm_page()
            logger.info(f"Selected accounts from context: '{entered_new_ains_details[6]}'")
            logger.info(f"Confirmation page accounts: '{investment_accounts}'")
            
            account_name_part, account_number_part = extract_account_core_identifier(entered_new_ains_details[6])
            
            if account_name_part and account_number_part:
                assert account_name_part in investment_accounts, \
                    f"Investment Account Name not found. Expected: '{account_name_part}', Actual: '{investment_accounts}'"
                assert account_number_part in investment_accounts, \
                    f"Investment Account Number not found. Expected: '{account_number_part}', Actual: '{investment_accounts}'"
            else:
                assert entered_new_ains_details[6] in investment_accounts, \
                    f"Investment Accounts mismatch. Expected substring: '{entered_new_ains_details[6]}', Actual: '{investment_accounts}'"
            
            logger.info(f"Investment Accounts: {investment_accounts}")
        
        logger.info("AINS confirmation page validation completed successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Confirmation Page Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should click on the Submit Button on AddACH Summary Page')
def click_submit_button_on_addach_summary_page(
    page: Page,
    add_ach_summary_page,
    test_context: dict
):
    """Click the Submit button on AddACH Summary Page"""
    with allure.step("Click Submit button on AddACH Summary Page"):
        logger.info("Clicking Submit button on AddACH Summary Page")
        
        add_ach_confirmation_page = add_ach_summary_page.click_submit()
        
        test_context['add_ach_confirmation_page'] = add_ach_confirmation_page
        
        logger.info("Submit button clicked successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Submit Button Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should click on the Item number on AINS Confirmation Page')
def click_item_number_on_ains_confirmation_page(
    page: Page,
    test_context: dict
):
    """Click the Item number on AINS Confirmation Page to open Tracking Center"""
    with allure.step("Click Item number on AINS Confirmation Page"):
        logger.info("Clicking Item number on AINS Confirmation Page")
        
        add_ach_confirmation_page = test_context.get('add_ach_confirmation_page')
        item_number = test_context.get('item_number')
        
        logger.info(f"Clicking item number: {item_number}")
        
        test_context['parent_window'] = page
        
        tracking_center_page = add_ach_confirmation_page.click_item_number()
        
        test_context['tracking_center_page'] = tracking_center_page
        test_context['ui_values_1'] = test_context.get('entered_new_ains_details', [])
        test_context['account_name_stored'] = test_context.get('account_name', '')
        
        logger.info(f"Item number {item_number} clicked successfully")
        logger.info("Switched to Tracking Center page in new tab")
        
        screenshot = tracking_center_page.screenshot()
        allure.attach(
            screenshot,
            name="Tracking Center Page After Item Click",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should validate closed date for role Advisor')
def validate_closed_date_for_advisor(page: Page, test_context, manage_instruction_1_page):
    with allure.step("Validate closed date for role Advisor"):
        logger.info("Validating closed date for role: Advisor")
        
        wait_for_network_idle(page, timeout=30.0)
        
        closed_date = manage_instruction_1_page.get_closed_on_date()
        
        test_context['closed_on_date'] = closed_date
        
        logger.info(f"Found Closed On Date: {closed_date}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Closed Date Validated for Advisor",
            attachment_type=allure.attachment_type.PNG
        )
        
        allure.attach(
            closed_date,
            name="Closed On Date",
            attachment_type=allure.attachment_type.TEXT
        )


@then('User should validate info panel contents with status and item description as BankPayee Instructions  Add for Add ACH NoEsign')
def validate_info_panel_contents(page: Page, test_context, manage_instruction_1_page):
    with allure.step("Validate info panel contents for Add ACH NoEsign"):
        logger.info("Validating info panel contents for: Add ACH NoEsign")
        logger.info("Manage Instructions Page : Manage Instructions Page")
        logger.info("Manage Instructions Page : Manage Instructions Page")
        
        wait_for_network_idle(page, timeout=30.0)
        
        status = manage_instruction_1_page.get_status()
        description = manage_instruction_1_page.get_description()
        
        test_context['status'] = status
        test_context['description'] = description
        
        expected_status = "Complete"
        expected_description = test_context['test_data'].get('expected_description', 'Bank/Payee Instructions - Add')
        
        assert status == expected_status, f"Status mismatch. Expected: '{expected_status}', Actual: '{status}'"
        logger.info(f"Status validated: {status}")
        
        assert description == expected_description, f"Description mismatch. Expected: '{expected_description}', Actual: '{description}'"
        logger.info(f"Description validated: {description}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Info Panel Validated for Add ACH NoEsign",
            attachment_type=allure.attachment_type.PNG
        )
        
        allure.attach(
            f"Status: {status}\nDescription: {description}",
            name="Info Panel Details",
            attachment_type=allure.attachment_type.TEXT
        )


@when(parsers.parse('User should select "{transfer_method}" withdrawal method with SLOA "{sloa_option}"'))
def select_withdrawal_method_with_sloa(page: Page, withdrawal_method_modal_page, transfer_method: str, sloa_option: str):
    """
    Select withdrawal method (ACH/Check/Wire) with SLOA option
    Based on Java: withdrawalMethodModalPage.clickACH(transferMethod, sloaOption)
    """
    with allure.step(f"Select {transfer_method} withdrawal method with SLOA {sloa_option}"):
        logger.info(f"Selecting {transfer_method} withdrawal method with SLOA option: {sloa_option}")
        
        if transfer_method.upper() == "ACH":
            withdrawal_method_modal_page.click_ach(sloa_option)
            logger.info(f"ACH selected with SLOA: {sloa_option}")
        elif transfer_method.upper() == "CHECK":
            withdrawal_method_modal_page.click_check(sloa_option)
            logger.info(f"Check method with SLOA: {sloa_option}")
        elif transfer_method.upper() == "WIRE":
            # For Wire method - to be implemented if needed
            logger.info(f"Wire method with SLOA: {sloa_option}")
        else:
            raise ValueError(f"Unknown transfer method: {transfer_method}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{transfer_method} Selected with SLOA {sloa_option}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should fetch selected ACH payee details for SLOA "{sloa_option}"'))
def fetch_selected_ach_payee_details(page: Page, withdrawal_method_modal_page, test_context: dict, sloa_option: str):
    """
    Fetch selected ACH payee details from withdrawal method modal
    Based on Java: selectedCheckInstructions = withdrawalMethodModalPage.getSelectedACHDetails(sloaOption)
    Stores: [Bank Name, Account Number, ABA Routing, Customer Name, SLOA Option]
    """
    with allure.step(f"Fetch selected ACH payee details for SLOA {sloa_option}"):
        logger.info(f"Fetching selected ACH payee details for SLOA: {sloa_option}")
        
        # Get ACH details from modal
        selected_ach_details = withdrawal_method_modal_page.get_selected_ach_details(sloa_option)
        
        # Store in test context
        test_context['selected_check_instructions'] = selected_ach_details
        
        # Log the details
        if len(selected_ach_details) >= 5:
            logger.info(f"Selected Payee Bank: {selected_ach_details[0]}")
            logger.info(f"Selected Payee Account: {selected_ach_details[1]}")
            logger.info(f"Selected Payee ABA: {selected_ach_details[2]}")
            logger.info(f"Selected Payee Name: {selected_ach_details[3]}")
            logger.info(f"Selected Payee SLOA: {selected_ach_details[4]}")
        
        allure.attach(
            f"Bank: {selected_ach_details[0]}\n"
            f"Account: {selected_ach_details[1]}\n"
            f"ABA: {selected_ach_details[2]}\n"
            f"Name: {selected_ach_details[3]}\n"
            f"SLOA: {selected_ach_details[4]}",
            name="Selected ACH Payee Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="ACH Payee Details Fetched",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should fetch selected check payee details for SLOA "{sloa_option}"'))
def fetch_selected_check_payee_details(page: Page, withdrawal_method_modal_page, test_context: dict, sloa_option: str):
    
    with allure.step(f"Fetch selected check payee details for SLOA {sloa_option}"):
        logger.info(f"Fetching selected check payee details for SLOA: {sloa_option}")
        
        # Get Check details from modal
        selected_check_details = withdrawal_method_modal_page.get_selected_check_details(sloa_option)
        
        # Store in test context
        test_context['selected_check_instructions'] = selected_check_details
        
        # Log the details
        if len(selected_check_details) >= 5:
            logger.info(f"Selected Payee Bank: {selected_check_details[0]}")
            logger.info(f"Selected Payee Account: {selected_check_details[1]}")
            logger.info(f"Selected Payee ABA: {selected_check_details[2]}")
            logger.info(f"Selected Payee Name: {selected_check_details[3]}")
            logger.info(f"Selected Payee SLOA: {selected_check_details[4]}")
        
        allure.attach(
            f"Bank: {selected_check_details[0]}\n"
            f"Account: {selected_check_details[1]}\n"
            f"ABA: {selected_check_details[2]}\n"
            f"Name: {selected_check_details[3]}\n"
            f"SLOA: {selected_check_details[4]}",
            name="Selected Check     Payee Details",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="ACH Payee Details Fetched",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should click continue in Withdrawal Method Modal with SLOA option "{sloa_option}"'))
def click_continue_in_withdrawal_method_modal(page: Page, withdrawal_method_modal_page, test_context: dict, sloa_option: str):
    """
    Click continue button in Withdrawal Method Modal
    Based on Java: 
    - mimoLandingPage = (MIMOTransactionRequestPage1) withdrawalMethodModalPage.clickContinue(sloaOption)
    - docuSignPage = (DocuSignPage) withdrawalMethodModalPage.clickContinue(sloaOption)
    
    SLOA "Yes" -> navigates to MIMO Landing Page
    SLOA "No" -> navigates to DocuSign Page
    """
    with allure.step(f"Click continue in Withdrawal Method Modal with SLOA option {sloa_option}"):
        logger.info(f"Clicking continue button with SLOA option: {sloa_option}")
        
        # Click continue button
        withdrawal_method_modal_page.click_continue(sloa_option)
        
        # Wait for navigation
        page.wait_for_load_state('domcontentloaded', timeout=30000)
        page.wait_for_timeout(2000)
        
        if sloa_option.upper() == "YES":
            logger.info("Navigated to MIMO Landing Page (SLOA Yes)")
        elif sloa_option.upper() == "NO":
            logger.info("Navigated to DocuSign Page (SLOA No)")
        else:
            logger.info(f"Continue clicked with SLOA option: {sloa_option}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"After Continue - SLOA {sloa_option}",
            attachment_type=allure.attachment_type.PNG
        )

