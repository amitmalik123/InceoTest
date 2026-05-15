import allure
from playwright.sync_api import Page
from pytest_bdd import parsers,when, then
import pytest

from mimo_transaction_request_page import MIMOTransactionRequestPage
from mimo_transaction_request_page2 import MIMOTransactionRequestPage2
from mimo_transaction_summary_page import MIMOTransactionSummaryPage
from utils.logger import setup_logger
import re

logger = setup_logger(__name__)


@when(parsers.parse('User should select Bank for Contributions request with sloa "{sloa_option}"'))
def select_bank_for_contributions_request(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, sloa_option: str):
    """Select bank for contributions request with SLOA option"""
    with allure.step(f"Select Bank for Contributions request with SLOA: {sloa_option}"):
        logger.info(f"Selecting bank for contributions with SLOA option: {sloa_option}")
        
        mimo_transaction_page.select_bank_for_contributions(sloa_option)
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Bank Selected - SLOA {sloa_option}",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should click next in MIMO Landing Page')
def click_next_in_mimo_landing_page(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, mimo_transaction_page2: MIMOTransactionRequestPage2):
    """Click next button in MIMO landing page to navigate to page 2"""
    with allure.step("Click Next in MIMO Landing Page"):
        logger.info("Clicking Next button in MIMO Landing Page")
        
        mimo_transaction_page.click_next()
        page.wait_for_timeout(20000)
        # mimo_transaction_page2.wait_for_page_load()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Navigated to MIMO Transaction Request Page 2",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should verify Account information displayed on MimoTransaction1 page')
def user_should_verify_account_information_displayed_on_mimo_transaction1_page(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, test_context: dict):
    """Verify account information on MIMO Transaction Request Page (MIMO 1)."""
    with allure.step("Verify account information displayed on MimoTransaction1 page"):
        if mimo_transaction_page.is_hardstop_visible():
            message = (
                "The account selected does not have any active systematic withdrawal plans on file. "
                "Please select another option type in Account Wizard."
            )
            pytest.skip(message)

        account_details = test_context.get("account_details_mimo1")
        if not account_details:
            raise RuntimeError("account_details_mimo1 not found in test_context; ensure it was captured earlier")

        request_type = test_context.get("request_type", "").lower()
        partial_match = "cancel" in request_type or "swp" in request_type.lower()

        mimo_transaction_page.validate_account_details_information(account_details, partial_match=partial_match)
        logger.info("User verifies Account Information on MIMO Transaction Request Page 1")


@then(parsers.parse('User should validate "{Message}" under the section "{Heading}"'))
def validate_instruction_on_file_heading(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, Message: str, Heading: str):
    """Validate the 'Instructions on file' heading and its message."""
    with allure.step(f"Validate message under section: {Heading}"):
        logger.info(f"Validating Instructions on file heading: expected '{Heading}', message expected '{Message}'")

        heading_text = mimo_transaction_page.get_instructions_on_file_heading()
        message_text = mimo_transaction_page.get_instructions_message()

        assert heading_text == Heading, f"Expected heading '{Heading}', got '{heading_text}'"
        assert message_text == Message, f"Expected message '{Message}', got '{message_text}'"

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Instructions On File - {Heading}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse(
    'User should Validate under the Transaction Details left section the "{title}" title, '
    '"{limit}" value, "{contributed}" value and "{remaining}" value'
))
def verify_transaction_details_header_current(
    page: Page,
    mimo_transaction_page2: MIMOTransactionRequestPage2,
    title: str,
    limit: str,
    contributed: str,
    remaining: str
):
    """Validate current year transaction details"""
    with allure.step(f"Validate Transaction Details - Current Year: {title}"):
        logger.info(f"Validating current year transaction details: {title}, {limit}, {contributed}, {remaining}")
        
        current_year_title = mimo_transaction_page2.get_current_year_title().upper()
        contribution_limit_title = mimo_transaction_page2.get_current_contribution_limit_title_with_value()
        contributed_title = mimo_transaction_page2.get_current_contribution_title()
        remaining_title = mimo_transaction_page2.get_current_remaining_title()
        
        assert current_year_title == title.upper(), f"Expected '{title}', got '{current_year_title}'"
        assert contribution_limit_title == limit, f"Expected '{limit}', got '{contribution_limit_title}'"
        assert contributed_title == contributed, f"Expected '{contributed}', got '{contributed_title}'"
        assert remaining_title == remaining, f"Expected '{remaining}', got '{remaining_title}'"
        
        logger.info("Current year transaction details validated successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Transaction Details - Current Year Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should Validate under the Transaction Details right section the "{title}" title, "{limit}" value, "{contributed}" value and "{remaining}" value'))
def verify_transaction_details_header_previous(
    page: Page,
    mimo_transaction_page2: MIMOTransactionRequestPage2,
    title: str,
    limit: str,
    contributed: str,
    remaining: str
):
    """Validate prior year transaction details"""
    with allure.step(f"Validate Transaction Details - Prior Year: {title}"):
        logger.info(f"Validating prior year transaction details: {title}, {limit}, {contributed}, {remaining}")
        
        prior_year_title = mimo_transaction_page2.get_prior_year_title().upper()
        contribution_limit_title = mimo_transaction_page2.get_prior_contribution_limit_title_with_value()
        contributed_title = mimo_transaction_page2.get_prior_contribution_title()
        remaining_title = mimo_transaction_page2.get_prior_remaining_title()
        
        assert prior_year_title == title.upper(), f"Expected '{title}', got '{prior_year_title}'"
        assert contribution_limit_title == limit, f"Expected '{limit}', got '{contribution_limit_title}'"
        assert contributed_title == contributed, f"Expected '{contributed}', got '{contributed_title}'"
        assert remaining_title == remaining, f"Expected '{remaining}', got '{remaining_title}'"
        
        logger.info("Prior year transaction details validated successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Transaction Details - Prior Year Validated",
            attachment_type=allure.attachment_type.PNG
        )


@when('User Enter cash in MIMO Transaction request Page')
def enter_cash_in_mimo_transaction_request_page(page: Page, mimo_transaction_page2: MIMOTransactionRequestPage2, test_context):
    """Enter cash amount in MIMO transaction request page"""
    with allure.step("Enter cash amount in MIMO Transaction Request Page"):
        logger.info("Entering cash amount in MIMO Transaction Request Page")
        
        # Using fixed amount as per Java code
        cash = "0.01"
        test_context['cash_amount'] = cash
        
        mimo_transaction_page2.enter_cash(cash)
        logger.info(f"Cash amount entered: {cash}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Cash Amount Entered: {cash}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should select "{string}" as Contribution Reason'))
def select_reason_from_dropdown(page: Page, mimo_transaction_page2: MIMOTransactionRequestPage2, test_context, string: str):
    """Select contribution reason from dropdown"""
    with allure.step(f"Select Contribution Reason: {string}"):
        logger.info(f"Selecting contribution reason: {string}")
        
        mimo_transaction_page2.select_distribution(string)
        
        selected_reason = mimo_transaction_page2.get_selected_distribution_reason()
        test_context['selected_distribution_reason'] = selected_reason
        
        logger.info(f"Selected contribution reason: {selected_reason}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Contribution Reason Selected: {selected_reason}",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should increase the Contribution Date from the System')
def increase_the_contribution_date(mimo_transaction_page2: MIMOTransactionRequestPage2):
    """Increase contribution date from system"""
    with allure.step("Increase Contribution Date"):
        logger.info("Increasing contribution date")
        mimo_transaction_page2.increase_contribution_date()


@when('User should get contribution date')
def get_contribution_date(mimo_transaction_page2: MIMOTransactionRequestPage2, test_context):
    """Get contribution date value"""
    with allure.step("Get Contribution Date"):
        logger.info("Getting contribution date")
        contribution_date = mimo_transaction_page2.get_contribution_date()
        test_context['contribution_date'] = contribution_date
        logger.info(f"Contribution date: {contribution_date}")


@then(parsers.parse('User should verify "{string}" Important Notes Section'))
def validate_important_notes_section(page: Page, mimo_transaction_page2: MIMOTransactionRequestPage2, string: str):
    """Validate important notes section contains expected title"""
    with allure.step(f"Verify Important Notes Section: {string}"):
        logger.info(f"Validating important notes section contains: {string}")
        
        important_notes = mimo_transaction_page2.get_important_notes()
        
        assert string in important_notes, f"Expected '{string}' to be in important notes, but got: {important_notes}"
        
        logger.info(f"Important notes validated. Contains: {important_notes}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Important Notes Section Validated",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should click next in MIMO Transaction Request Page')
def click_next_in_mimo_second_page(page: Page, mimo_transaction_page2: MIMOTransactionRequestPage2, mimo_summary_page: MIMOTransactionSummaryPage):
    """Click next button in MIMO transaction request page 2 and wait for summary page to load"""
    with allure.step("Click Next in MIMO Transaction Request Page"):
        logger.info("Clicking Next button in MIMO Transaction Request Page 2")

        mimo_transaction_page2.press_next()

        # short buffer to allow navigation to start, then wait for summary page load
        page.wait_for_timeout(1500)
        mimo_summary_page.wait_for_page_load()

        logger.info("Navigated to MIMO Transaction Summary Page")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Navigated to MIMO Summary Page",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('Enter details "{federal}" Federal Tax, "{state}" State Tax, "{distribution}" Distribution and "{memo}" checkMemo'))
def enter_details_in_mimo_transaction_request_page(
    page: Page,
    mimo_transaction_page2: MIMOTransactionRequestPage2,
    test_context: dict,
    federal: str,
    state: str,
    distribution: str,
    memo: str
):
    """Enter withdrawal details including federal tax, state tax, distribution reason, and check memo"""
    with allure.step(f"Enter details: Federal Tax={federal}, State Tax={state}, Distribution={distribution}, CheckMemo={memo}"):
        logger.info(f"Entering withdrawal details: Federal Tax={federal}, State Tax={state}, Distribution={distribution}, CheckMemo={memo}")
        
        # Handle Federal Tax
        if federal == "No":
            logger.info("Selecting 'Do Not Withhold' for federal tax")
            mimo_transaction_page2.select_do_not_withhold_federal_tax()
        else:
            logger.info(f"Entering federal tax withholding: {federal}")
            mimo_transaction_page2.enter_federal_withholding(federal)
        
        # Handle State Tax
        if state == "No":
            logger.info("Selecting 'Do Not Withhold' for state tax")
            mimo_transaction_page2.select_do_not_withhold_state_tax()
        elif state == "Do Not Require":
            logger.info("State tax requirement skipped (Do Not Require)")
            # No action needed for "Do Not Require"
            pass
        else:
            logger.info(f"Entering state tax withholding: {state}")
            mimo_transaction_page2.enter_tax_withholding(state)
        
        # Handle Distribution Reason
        if distribution == "Any":
            logger.info("Selecting 'Any' distribution reason (first available)")
            mimo_transaction_page2.select_any_distribution_reason()
        else:
            logger.info(f"Selecting distribution reason: {distribution}")
            mimo_transaction_page2.select_distribution(distribution)
        
        # Capture selected distribution reason
        selected_distribution_reason = mimo_transaction_page2.get_selected_distribution_reason()
        test_context['selected_distribution_reason'] = selected_distribution_reason
        logger.info(f"Selected distribution reason: {selected_distribution_reason}")
        
        # Handle Check Memo
        if memo in ["checkSTP", "checkSTR"]:
            logger.info(f"Filling check memo field with: {memo}")
            mimo_transaction_page2.fill_check_memo_field(memo)
        else:
            logger.info(f"Check memo value '{memo}' not recognized as valid (checkSTP/checkSTR). Skipping.")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Withdrawal Details Entered",
            attachment_type=allure.attachment_type.PNG
        )


@then('User Should check the number of Records and Validate the Pagination Concept')
def verify_pagination_for_instruction(page: Page, mimo_transaction_page: MIMOTransactionRequestPage):
    """Validate pagination for instructions list on MIMO landing page."""
    with allure.step("Verify pagination for instruction records"):
        mimo_transaction_page.verify_pagination()

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Pagination Verified",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should select First instruction displayed for "{method}"'))
def user_should_select_first_instruction(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, method: str):
    """Select the first instruction displayed for the given method."""
    with allure.step(f"Select first instruction for method: {method}"):
        logger.info(f"Selecting first instruction for: {method}")
        mimo_transaction_page.select_first_instruction_by_method(method)


@then('User should get the UI value from the Instructions for Selected Radio')
def user_should_get_ui_value_from_instructions(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, test_context: dict):
    """Capture UI values from the selected instruction and store in test_context."""
    with allure.step("Get UI values from selected instruction"):
        ui_values = mimo_transaction_page.get_ui_values_from_instructions_for_first()
        test_context['UIValues1'] = ui_values
        logger.info(f"Captured UI values for selected instruction: {ui_values}")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Selected Instruction UI Values", attachment_type=allure.attachment_type.PNG)


@then('User should click on the Expand Btn for Selected Instruction')
def user_should_click_on_expand_btn(page: Page, mimo_transaction_page: MIMOTransactionRequestPage):
    """Click expand button for the currently selected instruction."""
    with allure.step("Click expand on selected instruction"):
        mimo_transaction_page.click_expand_icon_for_selected_instruction()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Expanded Instruction", attachment_type=allure.attachment_type.PNG)


@then('User should store the UI Value to be validated')
def user_should_store_address_value_from_ui(page: Page, mimo_transaction_page: MIMOTransactionRequestPage, test_context: dict):
    """Store the address/destination value from the expanded view into test_context."""
    with allure.step("Store address value from expanded view"):
        address_value = mimo_transaction_page.get_address_value_from_expanded_view()
        test_context['AddressValue'] = address_value
        logger.info(f"Stored AddressValue from expanded view: {address_value}")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Stored Address Value", attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('User should validate "{category_name}" contents where "{dist_reason_header}","{federal_tax_header}" as "{federal_tax_value}", "{state_tax_header}" as "{state_tax_value}","{state_header}" and "{net_dist_header}"'))
def validate_qualified_information_details(
    page: Page,
    mimo_summary_page: MIMOTransactionSummaryPage,
    test_context: dict,
    category_name: str,
    dist_reason_header: str,
    federal_tax_header: str,
    federal_tax_value: str,
    state_tax_header: str,
    state_tax_value: str,
    state_header: str,
    net_dist_header: str
):
   
    with allure.step(f"Validate {category_name} contents"):
        logger.info(f"Validating {category_name} section")
        logger.info(f"Expected - Federal Tax: {federal_tax_value}, State Tax: {state_tax_value}")
        
        # Get summary page details for the category
        summary_page_details = mimo_summary_page.get_summary_page_details(category_name)
        
        # Extract values from summary
        federal_tax = summary_page_details.get(federal_tax_header, "")
        state_tax = summary_page_details.get(state_tax_header, "")
        
        # Get cash value from test context (set during "Enter cash" step)
        cash = test_context.get('cash', '0')
        cash_amount = int(cash.replace('$', '').replace(',', ''))
        net_dist_value = cash_amount
        
        # Handle three conditional scenarios
        if federal_tax_value == "Waived" and state_tax_value == "Waived":
            # Scenario 1: Both taxes waived
            logger.info("Scenario: Both federal and state taxes are waived")
            
            assert federal_tax == federal_tax_value, \
                f"Validation of {federal_tax_header} Value - Expected: {federal_tax_value}, Actual: {federal_tax}"
            logger.info(f"{federal_tax_header} validation passed: {federal_tax}")
            
            assert state_tax == state_tax_value, \
                f"Validation of {state_tax_header} Value - Expected: {state_tax_value}, Actual: {state_tax}"
            logger.info(f"{state_tax_header} validation passed: {state_tax}")
            
            # Net distribution = full cash amount (no withholding)
            net_dist_value = cash_amount
            
        elif state_tax_value == "N/A":
            # Scenario 2: Federal has percentage, state is N/A
            logger.info("Scenario: Federal tax percentage, state N/A")
            
            # Federal tax format: "15%\n$150"
            federal_parts = federal_tax.split('\n')
            federal_tax_percent = federal_parts[0] if len(federal_parts) > 0 else ""
            federal_tax_amount = 0
            if len(federal_parts) > 1:
                federal_tax_amount = int(federal_parts[1].replace('$', '').replace(',', ''))
            
            # Calculate expected federal tax amount
            expected_federal_percent = int(federal_tax_value.replace('%', ''))
            expected_federal_amount = int((cash_amount * expected_federal_percent) / 100)
            
            assert federal_tax_percent == federal_tax_value, \
                f"Validation of {federal_tax_header} Percent - Expected: {federal_tax_value}, Actual: {federal_tax_percent}"
            logger.info(f"{federal_tax_header} percent validation passed: {federal_tax_percent}")
            
            assert federal_tax_amount == expected_federal_amount, \
                f"Validation of {federal_tax_header} Amount - Expected: ${expected_federal_amount}, Actual: ${federal_tax_amount}"
            logger.info(f"{federal_tax_header} amount validation passed: ${federal_tax_amount}")
            
            assert state_tax == state_tax_value, \
                f"Validation of {state_tax_header} Value - Expected: {state_tax_value}, Actual: {state_tax}"
            logger.info(f"{state_tax_header} validation passed: {state_tax}")
            
            # Net distribution = cash - federal withholding
            net_dist_value = cash_amount - federal_tax_amount
            
        else:
            # Scenario 3: Both federal and state have percentage values
            logger.info("Scenario: Both federal and state taxes have percentage values")
            
            # Parse federal tax (format: "15%\n$150")
            federal_parts = federal_tax.split('\n')
            federal_tax_percent = federal_parts[0] if len(federal_parts) > 0 else ""
            federal_tax_amount = 0
            if len(federal_parts) > 1:
                federal_tax_amount = int(federal_parts[1].replace('$', '').replace(',', ''))
            
            # Parse state tax (format: "5%\n$50")
            state_parts = state_tax.split('\n')
            state_tax_percent = state_parts[0] if len(state_parts) > 0 else ""
            state_tax_amount = 0
            if len(state_parts) > 1:
                state_tax_amount = int(state_parts[1].replace('$', '').replace(',', ''))
            
            # Calculate expected amounts
            expected_federal_percent = int(federal_tax_value.replace('%', ''))
            expected_federal_amount = int((cash_amount * expected_federal_percent) / 100)
            
            expected_state_percent = int(state_tax_value.replace('%', ''))
            expected_state_amount = int((cash_amount * expected_state_percent) / 100)
            
            # Validate federal tax
            assert federal_tax_percent == federal_tax_value, \
                f"Validation of {federal_tax_header} Percent - Expected: {federal_tax_value}, Actual: {federal_tax_percent}"
            logger.info(f"{federal_tax_header} percent validation passed: {federal_tax_percent}")
            
            assert federal_tax_amount == expected_federal_amount, \
                f"Validation of {federal_tax_header} Amount - Expected: ${expected_federal_amount}, Actual: ${federal_tax_amount}"
            logger.info(f"{federal_tax_header} amount validation passed: ${federal_tax_amount}")
            
            # Validate state tax
            assert state_tax_percent == state_tax_value, \
                f"Validation of {state_tax_header} Percent - Expected: {state_tax_value}, Actual: {state_tax_percent}"
            logger.info(f"{state_tax_header} percent validation passed: {state_tax_percent}")
            
            assert state_tax_amount == expected_state_amount, \
                f"Validation of {state_tax_header} Amount - Expected: ${expected_state_amount}, Actual: ${state_tax_amount}"
            logger.info(f"{state_tax_header} amount validation passed: ${state_tax_amount}")
            
            # Net distribution = cash - federal withholding - state withholding
            net_dist_value = cash_amount - federal_tax_amount - state_tax_amount
        
        # Get UI values for additional validations
        ui_values = mimo_summary_page.list_string_summary_page_qualified_values()
        
        # Validate distribution reason
        actual_dist_reason = summary_page_details.get(dist_reason_header, "")
        selected_dist_reason = test_context.get('selected_distribution_reason', "")
        
        assert actual_dist_reason == selected_dist_reason, \
            f"Validation of {dist_reason_header} - Expected: {selected_dist_reason}, Actual: {actual_dist_reason}"
        logger.info(f"{dist_reason_header} validation passed: {actual_dist_reason}")
        
        # Validate state (from UI values - index 2)
        if len(ui_values) > 2:
            actual_state = summary_page_details.get(state_header, "")
            expected_state = ui_values[2]
            
            assert actual_state == expected_state, \
                f"Validation of {state_header} - Expected: {expected_state}, Actual: {actual_state}"
            logger.info(f"{state_header} validation passed: {actual_state}")
        
        # Validate net distribution amount
        actual_net_dist = summary_page_details.get(net_dist_header, "")
        actual_net_dist_amount = int(actual_net_dist.replace('$', '').replace(',', '').replace('.00', '').split('.')[0])
        
        assert actual_net_dist_amount == net_dist_value, \
            f"Validation of {net_dist_header} - Expected: ${net_dist_value}, Actual: ${actual_net_dist_amount}"
        logger.info(f"{net_dist_header} validation passed: ${actual_net_dist_amount}")
        
        logger.info(f"All validations passed for {category_name}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{category_name} Validation Passed",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate "Request Details" for non-IRA withdrawal with "{delivery_method}", "{request_type}" and "{frequency}"'))
def validate_request_details_on_summary_page(page: Page, mimo_summary_page: MIMOTransactionSummaryPage, delivery_method: str, request_type: str, frequency: str):
    with allure.step("Validate Request Details on Transaction Summary page"):
        actual_req_type = mimo_summary_page.get_field_value("Request Type")
        assert actual_req_type == request_type, \
            f"Request Type mismatch. Expected '{request_type}', got '{actual_req_type}'"
        logger.info(f"Request Type validated: {actual_req_type}")

        actual_delivery = mimo_summary_page.get_field_value("Delivery Method")
        assert actual_delivery == delivery_method, \
            f"Delivery Method mismatch. Expected '{delivery_method}', got '{actual_delivery}'"
        logger.info(f"Delivery Method validated: {actual_delivery}")

        actual_frequency = mimo_summary_page.get_field_value("Frequency")
        assert actual_frequency == frequency, \
            f"Frequency mismatch. Expected '{frequency}', got '{actual_frequency}'"
        logger.info(f"Frequency validated: {actual_frequency}")

        actual_amount = mimo_summary_page.get_field_value("Amount")
        logger.info(f"Amount value: {actual_amount}")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Request Details Validated",
            attachment_type=allure.attachment_type.PNG
        )

