import re
import allure
from playwright.sync_api import Page
from pytest_bdd import when, then, parsers

from pages.stp.stp_mimotransactionpage.mimo_transaction_summary_page import MIMOTransactionSummaryPage
from pages.stp.stp_mimotransactionpage.mimo_confirmation_page import MIMOConfirmationPage
from utils.stp.constants.constants import Constants
from utils.logger import setup_logger
from datetime import datetime
from zoneinfo import ZoneInfo

logger = setup_logger(__name__)


@then(parsers.parse('User validate "{section}" Section for "{delivery_method}" Contribution and "{reason}" reason in Transaction Summary Page for "{account_type}"'))
def validation_of_request_details_section_in_transaction_summary_page(
    page: Page, 
    mimo_summary_page, 
    test_context,
    section: str, 
    delivery_method: str, 
    reason: str, 
    account_type: str
):
    """Validate request details section in transaction summary page"""
    with allure.step(f"Validate {section} Section - Contribution: {delivery_method}, Reason: {reason}, Type: {account_type}"):
        logger.info(f"Validating request details section: {section}")
        
        category_name = section
        contribution_type = delivery_method
        contribution_reason = reason
        ira_or_non_ira = account_type
        
        summary_page_details = mimo_summary_page.get_summary_page_details(category_name)
        
        cash = test_context.get('cash_amount', '0.01')
        contribution_date = test_context.get('contribution_date', '')
        
        # Validate Request Type
        assert summary_page_details.get("Request Type") == "Contribution", \
            f"Expected 'Contribution', got '{summary_page_details.get('Request Type')}'"
        logger.info("Request Type validated: Contribution")
        
        # Validate Delivery Method
        assert summary_page_details.get("Delivery Method") == contribution_type, \
            f"Expected '{contribution_type}', got '{summary_page_details.get('Delivery Method')}'"
        logger.info(f"Delivery Method validated: {contribution_type}")
        
        # Validate Frequency
        assert summary_page_details.get("Frequency") == "One-Time", \
            f"Expected 'One-Time', got '{summary_page_details.get('Frequency')}'"
        logger.info("Frequency validated: One-Time")
        
        # Validate Amount
        expected_amount = f"${cash}"
        assert summary_page_details.get("Amount") == expected_amount, \
            f"Expected '{expected_amount}', got '{summary_page_details.get('Amount')}'"
        logger.info(f"Amount validated: {expected_amount}")
        
        # Validate Contribution Date
        if contribution_date:
            assert summary_page_details.get("Contribution Date") == contribution_date, \
                f"Expected '{contribution_date}', got '{summary_page_details.get('Contribution Date')}'"
            logger.info(f"Contribution Date validated: {contribution_date}")
        
        # Validate Contribution Reason for IRA
        if ira_or_non_ira == "IRA":
            assert summary_page_details.get("Contribution Reason") == contribution_reason, \
                f"Expected '{contribution_reason}', got '{summary_page_details.get('Contribution Reason')}'"
            logger.info(f"Contribution Reason validated: {contribution_reason}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{section} Section Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse(
    'User should validate "{category_name}" contents where "{req_type}" as "{req_type_value}",'
    '"{delivery}" as "{delivery_type}" ,"{frequency}" as "{frequency_value}" and "{amount}"'
))
def validate_request_details_contents_in_transaction_summary_page(
    page: Page,
    mimo_summary_page,
    test_context: dict,
    category_name: str,
    req_type: str,
    req_type_value: str,
    delivery: str,
    delivery_type: str,
    frequency: str,
    frequency_value: str,
    amount: str
):
    logger.info("\n")

    with allure.step(f"Validate {category_name} contents"):
        summary_page_details = mimo_summary_page.get_summarypage_details(category_name)

        # Validate Request Type
        actual_req_type = summary_page_details.get(req_type)
        assert actual_req_type == req_type_value, \
            f"Validation of {req_type}: Expected '{req_type_value}', got '{actual_req_type}'"
        logger.info(f"{req_type}: {actual_req_type}")

        # Validate Delivery Method
        actual_delivery = summary_page_details.get(delivery)
        assert actual_delivery == delivery_type, \
            f"Validation of {delivery}: Expected '{delivery_type}', got '{actual_delivery}'"
        logger.info(f"{delivery}: {actual_delivery}")

        # Validate Frequency
        actual_frequency = summary_page_details.get(frequency)
        assert actual_frequency == frequency_value, \
            f"Validation of {frequency}: Expected '{frequency_value}', got '{actual_frequency}'"
        logger.info(f"{frequency}: {actual_frequency}")

        # Log Amount
        actual_amount = summary_page_details.get(amount)
        if actual_amount:
            logger.info(f"{amount}: {actual_amount.split('.')[0]}")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{category_name} validated",
            attachment_type=allure.attachment_type.PNG
        )

    logger.info("\n")


@then(parsers.parse('User should validate "{section_name}" contents where "{dist_reason_header}","{federal_tax_header}" as "{federal_tax_value}", "{state_tax_header}" as "{state_tax_value}","{state_header}" and "{net_dist_amount_header}"'))
def validate_qualified_information_contents_in_transaction_summary_page(
    page: Page,
    mimo_summary_page: MIMOTransactionSummaryPage,
    test_context: dict,
    section_name: str,
    dist_reason_header: str,
    federal_tax_header: str,
    federal_tax_value: str,
    state_tax_header: str,
    state_tax_value: str,
    state_header: str,
    net_dist_amount_header: str
):
    """Validate QUALIFIED INFORMATION contents in transaction summary page - stores values for later confirmation page validation"""
    with allure.step(f"Validate {section_name} contents"):
        logger.info(f"\nValidating {section_name} section in transaction summary page\n")
        
        # Get all QUALIFIED INFORMATION details as dictionary
        summary_page_details = mimo_summary_page.get_summary_page_details(section_name)
        
        # Store values in test_context for confirmation page validation (matches Java UISummaryPageValues)
        ui_summary_values = []
        
        # Validate Distribution Reason
        dist_reason_value = summary_page_details.get(dist_reason_header, "")
        logger.info(f"Validation of {section_name} - {dist_reason_header}: {dist_reason_value}")
        ui_summary_values.append(dist_reason_value)
        
        # Validate Federal Tax Withholding
        federal_tax = summary_page_details.get(federal_tax_header, "")
        assert federal_tax_value.lower() in federal_tax.lower(), \
            f"Validation of {section_name} - {federal_tax_header}: Expected to contain '{federal_tax_value}', got '{federal_tax}'"
        logger.info(f"Validation of {section_name} - {federal_tax_header}: {federal_tax}")
        ui_summary_values.append(federal_tax)
        
        # Validate State Tax Withholding  
        state_tax = summary_page_details.get(state_tax_header, "")
        assert state_tax_value.lower() in state_tax.lower(), \
            f"Validation of {section_name} - {state_tax_header}: Expected to contain '{state_tax_value}', got '{state_tax}'"
        logger.info(f"Validation of {section_name} - {state_tax_header}: {state_tax}")
        
        # Get State value
        state_value = summary_page_details.get(state_header, "")
        logger.info(f"Validation of {section_name} - {state_header}: {state_value}")
        ui_summary_values.append(state_value)
        
        # Get Net Distribution Amount (matches Java - just log it)
        net_dist_amount = summary_page_details.get(net_dist_amount_header, "")
        logger.info(f"Validation of {section_name} - {net_dist_amount_header}: {net_dist_amount}")
        ui_summary_values.append(net_dist_amount)
        
        # Store in test_context for confirmation page validation (matches Java UISummaryPageValues list)
        test_context['ui_summary_page_values'] = ui_summary_values
        logger.info(f"Stored UI Summary Page Values: {ui_summary_values}")
        
        logger.info(f"\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{section_name} Contents Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should verify "{string}" disclosure Content in Transaction Summary Page'))
def validation_of_disclosure_content_in_transaction_summary_page(
    page: Page,
    mimo_summary_page,
    string: str
):
    """Validate disclosure content in transaction summary page"""
    with allure.step(f"Verify {string} disclosure Content"):
        logger.info(f"Validating disclosure content: {string}")
        
        disclosure_type = string
        disclosures = []
        
        # Determine which disclosure list to use
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
        
        # Validate based on disclosure type
        if disclosure_type == "Cancel":
            disclosures_title = mimo_summary_page.get_disclosures_title_for_cancel_swp()
            disclaimer_text = mimo_summary_page.get_disclaimer_text_for_cancel_swp()
            disclosures_list = mimo_summary_page.get_disclosures_list_for_cancel_swp()
            
            assert disclosures_title == Constants.DISCLOSURES_TITLE, \
                f"Expected '{Constants.DISCLOSURES_TITLE}', got '{disclosures_title}'"
            assert disclaimer_text == Constants.DISCLAIMER_TEXT, \
                f"Expected '{Constants.DISCLAIMER_TEXT}', got '{disclaimer_text}'"
            
            for disclosure in disclosures:
                assert disclosure in disclosures_list, \
                    f"Disclosure not found: {disclosure}"
                logger.info(f"Validated disclosure: {disclosure}")
        else:
            if disclosure_type == "Contribution":
                disclosures_title = mimo_summary_page.get_disclosures_title_for_contribution()
                disclosures_list = mimo_summary_page.get_disclosures_list_for_contribution()
            
            else:
                disclosures_title = mimo_summary_page.get_disclosures_title()
                disclosures_list = mimo_summary_page.get_disclosures_list()
            disclaimer_text = mimo_summary_page.get_disclaimer_text()
           
            
            assert disclosures_title.lower() == Constants.DISCLOSURES_TITLE.lower(), \
                f"Expected '{Constants.DISCLOSURES_TITLE}', got '{disclosures_title}'"
            assert disclaimer_text == Constants.DISCLAIMER_TEXT, \
                f"Expected '{Constants.DISCLAIMER_TEXT}', got '{disclaimer_text}'"
            
            for disclosure in disclosures:
                assert disclosure in disclosures_list, \
                    f"Disclosure not found: {disclosure}"
                logger.info(f"Validated disclosure: {disclosure}")
        
        logger.info(f"All disclosures validated for {disclosure_type}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{disclosure_type} Disclosure Validated",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should click Submit button in MIMO Summary Page for "{string}"'))
def click_submit_button_in_mimo_summary_page(page: Page, mimo_summary_page, string: str):
    """Click submit button in MIMO summary page"""
    with allure.step(f"Click Submit button: {string}"):
        logger.info(f"Clicking submit button type: {string}")
        
        if string == "STR":
            mimo_summary_page.click_submit_for_review()
            mimo_summary_page.wait_for_page_load()  # Wait for next page
        elif string == "STP":
            mimo_summary_page.click_submit()
            mimo_summary_page.wait_for_page_load()
        elif string == "Esign":
            mimo_summary_page.click_esign_and_submit()
        else:
            mimo_summary_page.click_submit_or_submit_for_review_button()
            mimo_summary_page.wait_for_page_load()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Submit Button Clicked - {string}",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should verify Account information displayed on MimoSummarypage')
def user_should_verify_account_information_displayed_on_mimo_summary_page(page: Page, mimo_summary_page: MIMOTransactionSummaryPage, test_context):
    """Verify account information on MIMO Transaction Summary Page (MIMO Summary)."""
    with allure.step("Verify account information displayed on MimoSummarypage"):
        account_details = test_context.get("account_details_mimo1")
        if not account_details:
            raise RuntimeError("account_details_mimo1 not found in test_context; ensure it was captured earlier")

        mimo_summary_page.validate_account_details_information_from_mimo_summary(account_details)
        logger.info("User verifies Account Information on MIMO Summary Page")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Verified on Summary Page",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate under the "{request_header}" Heading and their respective values as the "{request_type}" as "{request_value}", "{delivery}", "{frequency}", "{amount}", "{cancel_date}" and "{distribution_type}"'))
def verify_request_details_content(page: Page, mimo_summary_page: MIMOTransactionSummaryPage, test_context: dict, request_header: str, request_type: str, request_value: str, delivery: str, frequency: str, amount: str, cancel_date: str, distribution_type: str):
    """Validate REQUEST DETAILS heading and their respective values in MIMO summary page"""
    with allure.step(f"Validate {request_header} Heading and values"):
        logger.info(f"Validating {request_header} heading and values")
        
        # Validate Request Header
        actual_header = mimo_summary_page.get_request_header()
        assert actual_header == request_header, f"Request Header mismatch. Expected: '{request_header}', Actual: '{actual_header}'"
        logger.info(f"Request Header validated: {actual_header}")
        
        # Get all headers
        headers = mimo_summary_page.get_headers()
        logger.info(f"Found {len(headers)} headers")
        
        # Validate Request Type Header (index 2)
        assert headers[2] == request_type, f"Request Type Header mismatch. Expected: '{request_type}', Actual: '{headers[2]}'"
        logger.info(f"Request Type Header: {headers[2]}")
        
        # Validate Delivery Header (index 3)
        assert headers[3] == delivery, f"Delivery Header mismatch. Expected: '{delivery}', Actual: '{headers[3]}'"
        logger.info(f"Delivery Header: {headers[3]}")
        
        # Validate Frequency Header (index 4)
        assert headers[4] == frequency, f"Frequency Header mismatch. Expected: '{frequency}', Actual: '{headers[4]}'"
        logger.info(f"Frequency Header: {headers[4]}")
        
        # Validate Amount Header (index 5)
        assert headers[5] == amount, f"Amount Header mismatch. Expected: '{amount}', Actual: '{headers[5]}'"
        logger.info(f"Amount Header: {headers[5]}")
        
        # Validate Cancel Date Header (index 6)
        assert headers[6] == cancel_date, f"Cancel Date Header mismatch. Expected: '{cancel_date}', Actual: '{headers[6]}'"
        logger.info(f"Cancel Date Header: {headers[6]}")
        
        # Validate Distribution Type Header (index 7)
        assert headers[7] == distribution_type, f"Distribution Type Header mismatch. Expected: '{distribution_type}', Actual: '{headers[7]}'"
        logger.info(f"Distribution Type Header: {headers[7]}")
        
        # Get all values
        values = mimo_summary_page.verify_destination_values()
        logger.info(f"Found {len(values)} values")
        
        # Validate Request Value (index 2)
        assert values[2] == request_value, f"Request Value mismatch. Expected: '{request_value}', Actual: '{values[2]}'"
        logger.info(f"Request Value: {values[2]}")
        
        # Get UI values from test context (captured from Instructions on File)
        ui_values = test_context.get('ui_values_from_selected_instruction', [])
        if ui_values:
            # Method Validation (index 3) - compare with UI value index 1
            if len(ui_values) > 1 and len(values) > 3:
                assert values[3] == ui_values[1], f"Method mismatch. Expected: '{ui_values[1]}', Actual: '{values[3]}'"
                logger.info(f"Method validated: {values[3]}")
            
            # Frequency Validation (index 4) - compare with UI value index 3
            if len(ui_values) > 3 and len(values) > 4:
                assert values[4] == ui_values[3], f"Frequency mismatch. Expected: '{ui_values[3]}', Actual: '{values[4]}'"
                logger.info(f"Frequency validated: {values[4]}")
            
            # Amount Validation (index 5) - compare with UI value index 2
            if len(ui_values) > 2 and len(values) > 5:
                assert values[5] == ui_values[2], f"Amount mismatch. Expected: '{ui_values[2]}', Actual: '{values[5]}'"
                logger.info(f"Amount validated: {values[5]}")
            
            # Distribution Type Validation (index 7) - compare with UI value index 5
            if len(ui_values) > 5 and len(values) > 7:
                assert values[7] == ui_values[5], f"Distribution Type mismatch. Expected: '{ui_values[5]}', Actual: '{values[7]}'"
                logger.info(f"Distribution Type validated: {values[7]}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="REQUEST DETAILS Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate "Request Details" additional fields where "{cancel_date}" and "{distribution_type}"'))
def validate_request_details_additional_fields(page: Page, mimo_summary_page: MIMOTransactionSummaryPage, cancel_date: str, distribution_type: str):
    """Validate additional REQUEST DETAILS fields (Cancellation Date and Distribution Type)"""
    with allure.step(f"Validate Request Details additional fields: {cancel_date}, {distribution_type}"):
        logger.info(f"Validating additional fields: {cancel_date}, {distribution_type}")
        
        # Get summary page details as dictionary
        summary_page_details = mimo_summary_page.get_summarypage_details("Request Details")
        
        # Validate Cancellation Date field exists
        actual_cancel_date = summary_page_details.get(cancel_date)
        assert actual_cancel_date is not None, f"Field '{cancel_date}' not found in Request Details"
        logger.info(f"{cancel_date}: {actual_cancel_date}")
        
        # Validate Distribution Type field exists
        actual_distribution_type = summary_page_details.get(distribution_type)
        assert actual_distribution_type is not None, f"Field '{distribution_type}' not found in Request Details"
        logger.info(f"{distribution_type}: {actual_distribution_type}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Additional REQUEST DETAILS Fields Validated",
            attachment_type=allure.attachment_type.PNG
        )


# MIMO Confirmation Page Steps

@then(parsers.parse('User should verify title of the page "{string}"'))
def validation_of_confirmation_page_title(page: Page, mimo_confirmation_page, string: str):
    """Validate confirmation page title"""
    with allure.step(f"Verify Page Title: {string}"):
        logger.info(f"Validating confirmation page title: {string}")
        
        mimo_confirmation_page.wait_for_page_load()
        
        page_title = mimo_confirmation_page.get_page_title().upper()
        
        assert page_title == string.upper(), \
            f"Expected '{string}', got '{page_title}'"
        
        logger.info(f"Page title validated: {page_title}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Confirmation Page Title Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should verify confirmation screen success message as "{string}"'))
def validation_of_confirmation_screen_status(page: Page, mimo_confirmation_page, string: str):
    """Validate confirmation screen status"""
    with allure.step(f"Verify Confirmation Screen Status: {string}"):
        logger.info(f"Validating confirmation screen status: {string}")
        
        status = mimo_confirmation_page.get_confirmation_screen_status()
        
        assert status == string, \
            f"Expected '{string}', got '{status}'"
        
        logger.info(f"Confirmation screen status validated: {status}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Confirmation Status Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should validate Print button is enabled for TSC')
def print_btn_enabled(mimo_confirmation_page):
    """Validate print button is enabled"""
    with allure.step("Validate Print button is enabled"):
        logger.info("Validating Print button is enabled")
        
        assert mimo_confirmation_page.print_button_enabled(), \
            "Print button should be enabled"
        
        logger.info("Print button is enabled")


@when(parsers.parse('User should click print button and Validate the Tab size as {int_value:d} in Confirmation Page'))
def click_print_button_in_confirmation_page(page: Page, mimo_confirmation_page, int_value: int):
    """Click print button and validate tab size"""
    with allure.step(f"Click Print button and validate tab size: {int_value}"):
        logger.info("Clicking Print button")
        
        tab_size = mimo_confirmation_page.click_print_button()
        
        assert tab_size == int_value, \
            f"Expected {int_value} tabs, got {tab_size}"
        
        logger.info(f"Total number of tabs validated: {tab_size}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Print Button Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should verify account information displayed in confirmation page')
def verify_account_information_displayed_in_confirmation_page(
    page: Page,
    mimo_confirmation_page,
    test_context
):
    """Verify account information displayed in confirmation page"""
    with allure.step("Verify Account Information"):
        
        # Extract test_data from context (nested dictionary from CSV row)
        test_data = test_context.get('test_data', {})
        account_number = test_data.get('client_id', '')
        account_name = test_data.get('account_name', '')
        
        conf_account_number = mimo_confirmation_page.get_account_number()
        conf_account_name = mimo_confirmation_page.get_account_name()
        conf_account_strategy = mimo_confirmation_page.get_account_strategy()
        
        assert conf_account_number == account_number, \
            f"Expected account number '{account_number}', got '{conf_account_number}'"
        
        assert account_name in conf_account_name, \
            f"Account name '{conf_account_name}' should contain '{account_name}'"
        
        logger.info(f"Account strategy: {conf_account_strategy}")
        logger.info("Account information validated successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Validated",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should click on item number')
def click_item_number(mimo_confirmation_page, test_context):
    """Click on item number"""
    with allure.step("Click on Item Number"):
        logger.info("Clicking on Item Number")
        
        item_number = mimo_confirmation_page.get_item_number_section_text()
        test_context['item_number'] = item_number
        
        new_page = mimo_confirmation_page.click_item_number()
        test_context['item_details_page'] = new_page
        
        logger.info(f"Clicked on Item Number: {item_number}")


@then(parsers.parse('User should validate "{section_name}" contents where "{status_header}" as "{status_value}", "{date_header}" , "{submitted_by_header}" and "{item_number_header}"'))
def validation_of_transaction_summary_details_in_confirmation_page(
    page: Page,
    mimo_confirmation_page,
    section_name: str,
    status_header: str,
    status_value: str,
    date_header: str,
    submitted_by_header: str,
    item_number_header: str
):
    """Validate Transaction Summary details in confirmation page - matches Java validationOfTransactionSummaryDetailsInConfirmationPage"""
    with allure.step(f"Validate {section_name} contents"):
        logger.info("\n")
        
        # Get current date in US/Pacific time (app displays dates in PT)
        current_date = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m/%d/%Y")
        
        # Validate Status Section - matches Java: getStatus().getSectionTitle() and getStatus().getText()
        status_title = mimo_confirmation_page.get_status_section_title()
        status_text = mimo_confirmation_page.get_status_section_text()
        
        assert status_title == status_header, \
            f"Validation of {section_name} section Label: Expected '{status_header}', got '{status_title}'"
        logger.info(f"Validation of {section_name} section Label: {status_title}")
        
        assert status_text == status_value, \
            f"Validation of {section_name} section Value: Expected '{status_value}', got '{status_text}'"
        logger.info(f"Validation of {section_name} section Value: {status_text}")
        
        # Validate Date Section - matches Java: getDate().getSectionTitle() and getDate().getText().contains(time)
        date_title = mimo_confirmation_page.get_date_section_title()
        date_text = mimo_confirmation_page.get_date_section_text()
        
        assert date_title == date_header, \
            f"Validation of {section_name} section Label: Expected '{date_header}', got '{date_title}'"
        logger.info(f"Validation of {section_name} section Label: {date_title}")
        
        # Date should CONTAIN current date (matching Java's .contains() check)
        assert current_date in date_text, \
            f"Validation of {section_name} section Value: Expected date to contain '{current_date}', got '{date_text}'"
        logger.info(f"Validation of {section_name} section Value: {current_date}")
        
        # Validate Submitted By Section - matches Java: getSubmittedBy().getSectionTitle()
        # Note: Java has value assertion commented out, so we only validate the title
        submitted_by_title = mimo_confirmation_page.get_submitted_by_section_title()
        
        assert submitted_by_title == submitted_by_header, \
            f"Validation of {section_name} section Label: Expected '{submitted_by_header}', got '{submitted_by_title}'"
        logger.info(f"Validation of {section_name} section Label: {submitted_by_title}")
        
        # Validate Item Number Section - matches Java: getItemNumber().getSectionTitle()
        item_number_title = mimo_confirmation_page.get_item_number_section_title()
        
        assert item_number_title == item_number_header, \
            f"Validation of {section_name} section Label: Expected '{item_number_header}', got '{item_number_title}'"
        logger.info(f"Validation of {section_name} section Label: {item_number_title}")
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{section_name} Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User validate "{section}" contents where "{req_type_header}" as "{req_type_value}","{delivery_header}" as "{delivery_value}" ,"{frequency_header}" as "{frequency_value}" and "{amount_header}" in Confirmation Page for "{ira_or_non_ira}"'))
def validation_of_request_details_in_confirmation_page(
    page: Page,
    mimo_confirmation_page,
    test_context: dict,
    section: str,
    req_type_header: str,
    req_type_value: str,
    delivery_header: str,
    delivery_value: str,
    frequency_header: str,
    frequency_value: str,
    amount_header: str,
    ira_or_non_ira: str
):
    """Validate Request Details section in confirmation page"""
    with allure.step(f"Validate {section} in confirmation page"):
        logger.info(f"Validating Request Details section: {section}")


        request_type = mimo_confirmation_page.get_request_type_title()
        request_details = mimo_confirmation_page.get_request_type_text()

        assert request_type == req_type_header, \
            f"Validation of {section} section Label: Expected '{req_type_header}', got '{request_type}'"
        logger.info(f"Validation of {section} section Label: {request_type}")

        assert request_details == req_type_value, \
            f"Validation of {section} section Value: Expected '{req_type_value}', got '{request_details}'"
        logger.info(f"Validation of {section} section Value: {request_details}")

        # Delivery Method
        delivery_title = mimo_confirmation_page.get_delivery_method_title()
        delivery_text = mimo_confirmation_page.get_delivery_method_text()

        assert delivery_title == delivery_header, \
            f"Delivery Method label mismatch: Expected '{delivery_header}', got '{delivery_title}'"
        assert delivery_text == delivery_value, \
            f"Delivery Method value mismatch: Expected '{delivery_value}', got '{delivery_text}'"
        logger.info(f"Delivery Method validated: {delivery_text}")

        # Frequency
        frequency_title = mimo_confirmation_page.get_frequency_title()
        frequency_text = mimo_confirmation_page.get_frequency_text()

        assert frequency_title == frequency_header, \
            f"Frequency label mismatch: Expected '{frequency_header}', got '{frequency_title}'"
        assert frequency_text == frequency_value, \
            f"Frequency value mismatch: Expected '{frequency_value}', got '{frequency_text}'"
        logger.info(f"Frequency validated: {frequency_text}")

        # Amount
        amount_title = mimo_confirmation_page.get_amount_title() if req_type_value != "Contribution" else mimo_confirmation_page.get_contribution_amount_title()
        amount_text = mimo_confirmation_page.get_amount_text() if req_type_value != "Contribution" else mimo_confirmation_page.get_contribution_amount_text()

        assert amount_title == amount_header, \
            f"Amount label mismatch: Expected '{amount_header}', got '{amount_title}'"

        if req_type_value == "Contribution" and ira_or_non_ira == "IRA":
            contrib_date_title = mimo_confirmation_page.get_contribution_date_title()
            contrib_date_text = mimo_confirmation_page.get_contribution_date_text()
            contrib_reason_title = mimo_confirmation_page.get_contribution_reason_title()
            contrib_reason_text = mimo_confirmation_page.get_contribution_reason_text()

            assert contrib_date_title == "Contribution Date", \
                f"Contribution Date label mismatch: Expected 'Contribution Date', got '{contrib_date_title}'"
            expected_contrib_date = test_context.get('contribution_date', '')
            if expected_contrib_date:
                assert contrib_date_text == expected_contrib_date, \
                    f"Contribution Date mismatch: Expected '{expected_contrib_date}', got '{contrib_date_text}'"

            assert contrib_reason_title == "Contribution Reason", \
                f"Contribution Reason label mismatch: Expected 'Contribution Reason', got '{contrib_reason_title}'"
            expected_reason = test_context.get('selected_distribution_reason', '')
            if expected_reason:
                assert contrib_reason_text == expected_reason, \
                    f"Contribution Reason mismatch: Expected '{expected_reason}', got '{contrib_reason_text}'"
       

@then(parsers.parse('User should validate "{request_details_header}" contents where "{request_type}" is "{request_type_value}", "{delivery_method}" is "{delivery_method_value}", "{frequency_header}", "{amount_header}", "{cancellation_date_header}" and "{distribution_type_header}" for  Cancel SWP'))
def validate_request_details_for_cancel_swp(
    page: Page,
    mimo_confirmation_page: MIMOConfirmationPage,
    test_context: dict,
    request_details_header: str,
    request_type: str,
    request_type_value: str,
    delivery_method: str,
    delivery_method_value: str,
    frequency_header: str,
    amount_header: str,
    cancellation_date_header: str,
    distribution_type_header: str
):
    """Validate REQUEST DETAILS contents for Cancel SWP in confirmation page - matches Java validateRequestDetailsForCancelSWP"""
    with allure.step(f"Validate {request_details_header} for Cancel SWP"):
        logger.info("\n")
        logger.info(f"Validating {request_details_header} for Cancel SWP")
        
        # Get REQUEST DETAILS header
        actual_header = mimo_confirmation_page.get_request_details_header()
        assert actual_header == request_details_header, \
            f"RequestDetails Heading mismatch: Expected '{request_details_header}', got '{actual_header}'"
        logger.info(f"RequestDetails Heading: {actual_header}")
        
        # Get all REQUEST DETAILS values as text
        request_details_text = mimo_confirmation_page.get_request_details_values()
        logger.info(f"Request Details text: {request_details_text}")
        
        # Validate Request Type Heading
        assert request_type in request_details_text, \
            f"RequestType Heading not found in: {request_details_text}"
        logger.info(f"RequestType Heading validated: {request_type}")
        
        # Validate Request Type Value
        assert request_type_value in request_details_text, \
            f"RequestType Value not found: {request_type_value}"
        logger.info(f"RequestType Value validated: {request_type_value}")
        
        # Validate Delivery Method Heading
        assert delivery_method in request_details_text, \
            f"DeliveryMethod Heading not found in: {request_details_text}"
        logger.info(f"DeliveryMethod Heading validated: {delivery_method}")
        
        # Validate Delivery Method Value
        assert delivery_method_value in request_details_text, \
            f"DeliveryMethod Value not found: {delivery_method_value}"
        logger.info(f"DeliveryMethod Value validated: {delivery_method_value}")
        
        # Get UI values from test context (captured from Instructions on File)
        ui_values = test_context.get('ui_values_from_selected_instruction', [])
        
        # Validate Frequency Heading
        assert frequency_header in request_details_text, \
            f"Frequency Heading not found in: {request_details_text}"
        logger.info(f"Frequency Heading validated: {frequency_header}")
        
        # Validate Frequency Value (from UI values index 3)
        if len(ui_values) > 3:
            frequency_value = ui_values[3]
            assert frequency_value in request_details_text, \
                f"Frequency Value not found: {frequency_value}"
            logger.info(f"Frequency Value validated: {frequency_value}")
        
        # Validate Amount Heading
        assert amount_header in request_details_text, \
            f"Amount Heading not found in: {request_details_text}"
        logger.info(f"Amount Heading validated: {amount_header}")
        
        # Validate Amount Value (from UI values index 2)
        if len(ui_values) > 2:
            amount_value = ui_values[2]
            assert amount_value in request_details_text, \
                f"Amount Value not found: {amount_value}"
            logger.info(f"Amount Value validated: {amount_value}")
        
        # Validate Cancellation Date Heading
        assert cancellation_date_header in request_details_text, \
            f"CancellationDate Heading not found in: {request_details_text}"
        logger.info(f"CancellationDate Heading validated: {cancellation_date_header}")
        
        # Validate Cancellation Date Value
        cancelled_date = mimo_confirmation_page.get_cancelled_date()
        if cancelled_date:
            assert cancelled_date in request_details_text, \
                f"CancellationDate Value not found: {cancelled_date}"
            logger.info(f"CancellationDate Value validated: {cancelled_date}")
        
        # Validate Distribution Type Heading
        assert distribution_type_header in request_details_text, \
            f"DistributionType Heading not found in: {request_details_text}"
        logger.info(f"DistributionType Heading validated: {distribution_type_header}")
        
        # Validate Distribution Type Value (from UI values index 5)
        if len(ui_values) > 5:
            distribution_type_value = ui_values[5]
            assert distribution_type_value in request_details_text, \
                f"DistributionType Value not found: {distribution_type_value}"
            logger.info(f"DistributionType Value validated: {distribution_type_value}")
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="REQUEST DETAILS for Cancel SWP Validated",
            attachment_type=allure.attachment_type.PNG
        )
        

@then(parsers.parse('User can validate "{section_name}" contents where "{dist_reason_header}","{federal_tax_header}" as "{federal_tax_value}", "{state_tax_header}" as "{state_tax_value}","{state_header}" and "{net_dist_amount_header}" in Confirmation Page'))
def validate_qualified_information_in_confirmation_page(
    page: Page,
    mimo_confirmation_page: MIMOConfirmationPage,
    test_context: dict,
    section_name: str,
    dist_reason_header: str,
    federal_tax_header: str,
    federal_tax_value: str,
    state_tax_header: str,
    state_tax_value: str,
    state_header: str,
    net_dist_amount_header: str
):
    """Validate QUALIFIED INFORMATION section in confirmation page - matches Java validationOfQualifiedInformationInConfirmationPage"""
    with allure.step(f"Validate {section_name} in Confirmation Page"):
        logger.info(f"\n")
        logger.info(f"Validating {section_name} section in confirmation page")
        
        # Get stored values from summary page (matches Java UISummaryPageValues)
        ui_summary_values = test_context.get('ui_summary_page_values', [])
        selected_dist_reason = test_context.get('selected_distribution_reason', '')
        
        # Validate Distribution Reason
        dist_reason_title = mimo_confirmation_page.get_distribution_reason_title()
        dist_reason_text = mimo_confirmation_page.get_distribution_reason_text()
        
        assert dist_reason_title == dist_reason_header, \
            f"Validation of {section_name} section Label: Expected '{dist_reason_header}', got '{dist_reason_title}'"
        logger.info(f"Validation of {section_name} section Label: {dist_reason_title}")
        
        assert dist_reason_text == selected_dist_reason, \
            f"Validation of {section_name} section Value: Expected '{selected_dist_reason}', got '{dist_reason_text}'"
        logger.info(f"Validation of {section_name} section Value: {dist_reason_text}")
        
        # Validate Federal Tax Withholding
        federal_tax_title = mimo_confirmation_page.get_federal_tax_withholding_title()
        federal_tax_text = mimo_confirmation_page.get_federal_tax_withholding_text()
        
        assert federal_tax_title == federal_tax_header, \
            f"Validation of {section_name} section Label: Expected '{federal_tax_header}', got '{federal_tax_title}'"
        logger.info(f"Validation of {section_name} section Label: {federal_tax_title}")
        
        assert federal_tax_value.lower() in federal_tax_text.lower(), \
            f"Validation of {section_name} section Value: Expected to contain '{federal_tax_value}', got '{federal_tax_text}'"
        logger.info(f"Validation of {section_name} section Value: {federal_tax_text}")
        
        # Validate State Tax Withholding
        state_tax_title = mimo_confirmation_page.get_state_tax_withholding_title()
        state_tax_text = mimo_confirmation_page.get_state_tax_withholding_text()
        
        assert state_tax_title == state_tax_header, \
            f"Validation of {section_name} section Label: Expected '{state_tax_header}', got '{state_tax_title}'"
        logger.info(f"Validation of {section_name} section Label: {state_tax_title}")
        
        assert state_tax_value.lower() in state_tax_text.lower(), \
            f"Validation of {section_name} section Value: Expected to contain '{state_tax_value}', got '{state_tax_text}'"
        logger.info(f"Validation of {section_name} section Value: {state_tax_text}")
        
        # Validate State of Residence
        state_title = mimo_confirmation_page.get_state_of_residence_title()
        state_text = mimo_confirmation_page.get_state_of_residence_text()
        
        assert state_title == state_header, \
            f"Validation of {section_name} section Label: Expected '{state_header}', got '{state_title}'"
        logger.info(f"Validation of {section_name} section Label: {state_title}")
        
        # Validate state value matches UISummaryPageValues.get(2) from Java
        if len(ui_summary_values) > 2:
            expected_state = ui_summary_values[2]
            assert state_text == expected_state, \
                f"Validation of {section_name} section Value: Expected '{expected_state}', got '{state_text}'"
            logger.info(f"Validation of {section_name} section Value: {state_text}")
        else:
            logger.warning(f"UI Summary Values not available for state validation. Got: {state_text}")
        
        # Net Distribution Amount validation is commented out in Java, so we just log it
        # net_dist_title = mimo_confirmation_page.get_net_distribution_amount_title()
        # net_dist_text = mimo_confirmation_page.get_net_distribution_amount_text()
        # logger.info(f"Net Distribution Amount: {net_dist_text}")
        
        logger.info(f"\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{section_name} Validated in Confirmation Page",
            attachment_type=allure.attachment_type.PNG
        )

@then(parsers.parse(
    'User should validate "{category_name}" contents where "{check_memo}" as "{check_memo_value}" and "{delivery}" as "{delivery_value}"'
))
def validate_distribution_details(
    category_name,
    check_memo,
    check_memo_value,
    delivery,
    delivery_value,
    mimo_summary_page,
    test_context: dict
):
    logger.info("\n")

    summary_page_details = mimo_summary_page.get_summarypage_details(category_name)
    
    selected_check_instructions = test_context.get('selected_check_instructions', [])

    assert summary_page_details.get("Payee Name") == selected_check_instructions[0].strip(), \
        f"Payee Name mismatch. Expected: {selected_check_instructions[0].strip()}, Actual: {summary_page_details.get('Payee Name')}"
    logger.info(f"Validation of Payee Name: {selected_check_instructions[0].strip()}")

    assert selected_check_instructions[1].strip() in summary_page_details.get("Address"), \
        f"Payee Address not found. Expected: {selected_check_instructions[1].strip()} in {summary_page_details.get('Address')}"
    logger.info(f"Validation of Payee Address: {selected_check_instructions[1]}")

    assert selected_check_instructions[2].strip() in summary_page_details.get("Address"), \
        f"Payee City not found. Expected: {selected_check_instructions[2].strip()} in {summary_page_details.get('Address')}"
    logger.info(f"Validation of Payee City: {selected_check_instructions[2]}")

    assert selected_check_instructions[3].strip() in summary_page_details.get("Address"), \
        f"Payee State not found. Expected: {selected_check_instructions[3].strip()} in {summary_page_details.get('Address')}"
    logger.info(f"Validation of Payee State: {selected_check_instructions[3]}")

    assert selected_check_instructions[4].strip() in summary_page_details.get("Address"), \
        f"Payee Zip not found. Expected: {selected_check_instructions[4].strip()} in {summary_page_details.get('Address')}"
    logger.info(f"Validation of Payee Zip: {selected_check_instructions[4]}")

    assert summary_page_details.get(check_memo) == check_memo_value, \
        f"Check Memo mismatch. Expected: {check_memo_value}, Actual: {summary_page_details.get(check_memo)}"
    logger.info(f"Validation of Check Memo: {check_memo_value}")

    assert summary_page_details.get(delivery) == delivery_value, \
        f"Mail Delivery mismatch. Expected: {delivery_value}, Actual: {summary_page_details.get(delivery)}"
    logger.info(f"Validation of Mail Delivery: {delivery_value}")


@then(parsers.parse('User should validate "REQUEST DETAILS" confirmation for non-IRA withdrawal with "{delivery_method}", "{request_type}" and "{frequency}"'))
def validate_request_details_section_on_confirmation_page(mimo_confirmation_page, delivery_method: str, request_type: str, frequency: str):
    with allure.step("Validate REQUEST DETAILS section on Confirmation page"):
        actual_req_type = mimo_confirmation_page.get_request_type_text()
        assert actual_req_type == request_type, \
            f"Request Type mismatch. Expected '{request_type}', got '{actual_req_type}'"
        logger.info(f"Request Type validated: {actual_req_type}")

        actual_delivery = mimo_confirmation_page.get_delivery_method_text()
        assert actual_delivery == delivery_method, \
            f"Delivery Method mismatch. Expected '{delivery_method}', got '{actual_delivery}'"
        logger.info(f"Delivery Method validated: {actual_delivery}")

        actual_frequency = mimo_confirmation_page.get_frequency_text()
        assert actual_frequency == frequency, \
            f"Frequency mismatch. Expected '{frequency}', got '{actual_frequency}'"
        logger.info(f"Frequency validated: {actual_frequency}")

        actual_amount = mimo_confirmation_page.get_amount_text()
        logger.info(f"Amount value: {actual_amount}")


@then(parsers.parse('User should validate "TRANSACTION SUMMARY" for non-IRA withdrawal with status "{status}"'))
def validate_transaction_summary_section_on_confirmation_page(page: Page, mimo_confirmation_page, status: str):
    with allure.step("Validate TRANSACTION SUMMARY section on Confirmation page"):
        actual_status = mimo_confirmation_page.get_status_section_text()
        assert actual_status == status, \
            f"Status mismatch. Expected '{status}', got '{actual_status}'"
        logger.info(f"Status validated: {actual_status}")

        submitted_by_title = mimo_confirmation_page.get_submitted_by_section_title()
        assert submitted_by_title == "Submitted By", \
            f"Submitted By label mismatch. Expected 'Submitted By', got '{submitted_by_title}'"
        logger.info(f"Submitted By label validated: {submitted_by_title}")

        item_number_title = mimo_confirmation_page.get_item_number_section_title()
        assert item_number_title == "Item Number", \
            f"Item Number label mismatch. Expected 'Item Number', got '{item_number_title}'"
        logger.info(f"Item Number label validated: {item_number_title}")

        item_number_value = mimo_confirmation_page.get_item_number_section_text()
        assert re.match(r'^A\d{9}$', item_number_value), \
            f"Item Number format invalid. Expected 'A' + 9 digits, got '{item_number_value}'"
        logger.info(f"Item Number value validated: {item_number_value}")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="TRANSACTION SUMMARY Validated",
            attachment_type=allure.attachment_type.PNG
        )

    
