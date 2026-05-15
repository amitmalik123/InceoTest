"""
Establish Automatic Investment Plan (AIP) step definitions
"""

import re

import allure
from playwright.sync_api import Page
from pytest_bdd import when, then, parsers

from config.settings import get_settings
from pages.establish_aip_add_aip_page import EstablishAIPAddAIPPage
from pages.establish_aip_confirmation_page import EstablishAIPConfirmationPage
from pages.establish_aip_landing_page import EstablishAIPLandingPage
from pages.establish_aip_origination_selection_page import EstablishAIPOriginationSelectionPage
from pages.establish_aip_summary_page import EstablishAIPSummaryPage
from utils.allure_logger import get_allure_logger
from utils.constants.constants import Constants

logger = get_allure_logger(__name__)


def normalize_account_info(text: str) -> str:
    """Normalize account information text for comparison
    
    Removes extra spaces, special characters, and normalizes format
    """
    # Remove dollar signs, commas in numbers, parentheses, and extra spaces
    normalized = re.sub(r'[\$,\(\)]', '', text)
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    # Convert to lowercase for case-insensitive comparison
    return normalized.strip().lower()


def extract_account_number(text: str) -> str:
    """Extract account number from account information text"""
    # Look for patterns like "13222266" or "Account # 13222266" or "- 13222266 -"
    match = re.search(r'(?:account\s*#\s*)?(\d{8})', text, re.IGNORECASE)
    return match.group(1) if match else ""


def verify_account_info_match(expected: str, actual: str) -> bool:
    """Flexible account information comparison
    
    Compares key components:
    - Account number must match
    - Name must be present in both
    - Account type must be present in both
    """
    # Extract account numbers
    expected_account_num = extract_account_number(expected)
    actual_account_num = extract_account_number(actual)
    
    # Account number must match if present in expected
    if expected_account_num and actual_account_num:
        if expected_account_num != actual_account_num:
            logger.warning(f"Account number mismatch: {expected_account_num} vs {actual_account_num}")
            return False
    
    # Normalize both strings
    expected_norm = normalize_account_info(expected)
    actual_norm = normalize_account_info(actual)
    
    # Extract key components from expected (first few words are usually the name)
    expected_parts = expected_norm.split()
    
    # Check if key components are in actual
    # Look for name components (first 2-3 words typically)
    if len(expected_parts) >= 2:
        # Check if first 2 words (likely name) are in actual
        name_part = ' '.join(expected_parts[:2])
        if name_part not in actual_norm:
            logger.warning(f"Name part '{name_part}' not found in actual")
            return False
    
    # Check for account type keywords
    account_type_keywords = ['individual', 'joint', 'ira', 'roth']
    expected_has_type = any(keyword in expected_norm for keyword in account_type_keywords)
    if expected_has_type:
        # At least one account type keyword should be in actual
        if not any(keyword in actual_norm for keyword in account_type_keywords):
            logger.warning("No account type keyword found in actual")
            return False
    
    return True


@when("User clicks on next button and jumps to Establish AIP Landing Page")
def click_next_and_jump_to_establish_aip_landing_page(
    page: Page, account_wizard_page, test_context: dict
):
    """Click next button on account wizard and navigate to Establish AIP Landing Page"""
    with allure.step("Click next button and jump to Establish AIP Landing Page"):
        logger.info("Clicking Next button to navigate to Establish AIP Landing Page")
        
        # Click next button on account wizard page
        account_wizard_page.next_button.wait_for(state='visible', timeout=10000)
        account_wizard_page.next_button.click()
        
        # Wait for next button to be clickable again (page transition)
        page.wait_for_timeout(5000)
        
        # Create EstablishAIPLandingPage instance and store in test_context
        establish_aip_landing_page = EstablishAIPLandingPage(page)
        establish_aip_landing_page.wait_for_page_load()
        test_context['establish_aip_landing_page'] = establish_aip_landing_page
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Establish AIP Landing Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Navigated to Establish AIP Landing Page")


@when("User verifies Account Information on Landing Page")
def verify_account_information_on_landing_page(page: Page, test_context: dict):
    """Verify account information on Establish AIP Landing Page"""
    with allure.step("Verify Account Information on Landing Page"):
        logger.info("Verifying Account Information on Establish AIP Landing Page")
        
        # Get page instance from test_context
        establish_aip_landing_page = test_context.get('establish_aip_landing_page')
        
        if not establish_aip_landing_page:
            # Create new instance if not in context
            establish_aip_landing_page = EstablishAIPLandingPage(page)
            test_context['establish_aip_landing_page'] = establish_aip_landing_page
        
        # Get actual account information from page
        actual_account_info = establish_aip_landing_page.get_account_information_text()
        logger.info(f"Actual Account Information: {actual_account_info}")
        
        # Get expected account information from test_data
        test_data = test_context.get('test_data', {})
        expected_account_info = test_data.get('AccountInformation', '')
        
        # If not in test_data, try to use account details from earlier step
        if not expected_account_info:
            account_details = test_context.get('establish_aip_account_details', [])
            if account_details:
                expected_account_info = ', '.join(account_details)
        
        logger.info(f"Expected Account Information: {expected_account_info}")
        
        # Verify account information
        if expected_account_info:
            # Use flexible comparison
            match = verify_account_info_match(expected_account_info, actual_account_info)
            
            assert match, (
                f"Account Information mismatch!\n"
                f"Expected: {expected_account_info}\n"
                f"Actual: {actual_account_info}"
            )
            logger.info("Account Information verification PASSED")
        else:
            logger.info("Account Information retrieved (no expected value to compare)")
        
        # Attach to Allure report
        allure.attach(
            f"Expected: {expected_account_info}\nActual: {actual_account_info}",
            name="Account Information Verification",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User clicks on the Add button in the Establish AIP Landing Page")
def click_add_button_on_establish_aip_landing_page(page: Page, test_context: dict):
    """Click on Add button in Establish AIP Landing Page"""
    with allure.step("Click Add button in Establish AIP Landing Page"):
        logger.info("Clicking Add button in Establish AIP Landing Page")
        
        # Get page instance from test_context
        establish_aip_landing_page = test_context.get('establish_aip_landing_page')
        
        if not establish_aip_landing_page:
            establish_aip_landing_page = EstablishAIPLandingPage(page)
            test_context['establish_aip_landing_page'] = establish_aip_landing_page
        
        # Click add button and get next page object
        origination_selection_page = establish_aip_landing_page.click_add_button()
        test_context['establish_aip_origination_selection_page'] = origination_selection_page
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Clicking Add Button",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Add button clicked and navigated to Origination Selection Page")


@when("User verifies Account Information on Origination Selection Page")
def verify_account_information_on_origination_page(page: Page, test_context: dict):
    """Verify account information on Origination Selection Page"""
    with allure.step("Verify Account Information on Origination Selection Page"):
        logger.info("\n")
        logger.info("Verifying Account Information on Origination Selection Page")
        
        # Get page instance from test_context
        origination_selection_page = test_context.get('establish_aip_origination_selection_page')
        
        if not origination_selection_page:
            origination_selection_page = EstablishAIPOriginationSelectionPage(page)
            test_context['establish_aip_origination_selection_page'] = origination_selection_page
        
        # Get actual account information from page
        actual_text = origination_selection_page.get_account_information_text()
        logger.info(f"Actual Account Information: {actual_text}")
        
        # Get expected account information from test_data
        test_data = test_context.get('test_data', {})
        expected_text = test_data.get('AccountInformation', '')
        
        # If not in test_data, try to use account details from earlier step
        if not expected_text:
            account_details = test_context.get('establish_aip_account_details', [])
            if account_details:
                expected_text = ', '.join(account_details)
        
        logger.info(f"Expected Account Information: {expected_text}")
        
        # Verify account information
        if expected_text:
            # Use flexible comparison
            match = verify_account_info_match(expected_text, actual_text)
            
            assert match, (
                f"Account Information mismatch on Origination Page!\n"
                f"Expected: {expected_text}\n"
                f"Actual: {actual_text}"
            )
            logger.info("Account Information verification PASSED")
            logger.info(f"Account Information verification --> {actual_text}")
        else:
            logger.info("Account Information retrieved (no expected value to compare)")
            logger.info(f"Account Information verification --> {actual_text}")
        
        # Attach to Allure report
        allure.attach(
            f"Expected: {expected_text}\nActual: {actual_text}",
            name="Account Information Verification - Origination Page",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Verified on Origination Page",
            attachment_type=allure.attachment_type.PNG
        )


@when("User clicks on View Details and verifies Instruction Details modal closes with cross and Close button")
def user_clicks_view_details_and_verifies_modal(page: Page, test_context: dict):
    """Click on View Details and verify Instruction Details modal closes with cross and Close button"""
    with allure.step("Verify View Details modal functionality"):
        logger.info("\n")
        logger.info("Clicking View Details and verifying modal functionality")
        
        # Get page instance from test_context
        origination_selection_page = test_context.get('establish_aip_origination_selection_page')
        
        if not origination_selection_page:
            origination_selection_page = EstablishAIPOriginationSelectionPage(page)
            test_context['establish_aip_origination_selection_page'] = origination_selection_page
        
        # Call the method to verify modal functionality
        origination_selection_page.click_view_details_and_verify_modal()
        
        logger.info("View Details Modal Verification --> Verified cross and Close button functionality")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="View Details Modal Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User should see the required texts on Select Origination page and clicks on Next")
def validate_texts_on_origination_page(page: Page, test_context: dict):
    """Validate required texts on Origination Selection page and click Next"""
    with allure.step("Validate texts on Select Origination page and click Next"):
        logger.info("\n")
        logger.info("Validating required texts on Origination Selection page")
        
        # Get page instance from test_context
        origination_selection_page = test_context.get('establish_aip_origination_selection_page')
        
        if not origination_selection_page:
            origination_selection_page = EstablishAIPOriginationSelectionPage(page)
            test_context['establish_aip_origination_selection_page'] = origination_selection_page
        
        # Verify header
        assert origination_selection_page.is_header_visible(), \
            "Header 'Add Automatic Investment Plan (AIP)' is not visible"
        logger.info("Verified text --> Add Automatic Investment Plan (AIP)")
        
        # Verify subheader
        assert origination_selection_page.is_sub_header_visible(), \
            "Subheader 'Select the origination for the new automatic investment plan.' is not visible"
        logger.info("Verified text --> Select the origination for the new automatic investment plan.")
        
        # Verify origination label
        assert origination_selection_page.is_origination_label_visible(), \
            "Label 'Origination *' is not visible"
        logger.info("Verified text --> Origination *")
        
        # Verify help text
        assert origination_selection_page.is_origination_help_text_visible(), \
            "Helper text is not visible"
        logger.info("Verified text --> Select which ACH Instructions on file...")
        
        # Verify info note
        assert origination_selection_page.is_info_note_visible(), \
            "Info note is not visible"
        logger.info("Verified text --> Info note displayed")
        
        # Take screenshot after verification
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Page Elements Verified",
            attachment_type=allure.attachment_type.PNG
        )
        
        # Select instruction
        origination_selection_page.select_instruction()
        logger.info("Selecting ACH Instruction --> Selected")
        
        # Capture the selected origination for summary verification
        selected_origination = origination_selection_page.get_selected_origination_text()
        test_data = test_context.get('test_data', {})
        test_data['AIPOrigination'] = selected_origination
        test_context['test_data'] = test_data
        logger.info(f"Captured Origination --> {selected_origination}")
        
        # Click Next button and navigate to Add AIP page
        add_aip_page = origination_selection_page.click_next_button()
        test_context['establish_aip_add_aip_page'] = add_aip_page
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Navigated to Add AIP Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Clicked Next button and navigated to Add AIP Page")


@when("the advisor enters a valid contribution amount")
def the_advisor_enters_a_valid_contribution_amount(page: Page, test_context: dict):
    """Enter a valid contribution amount"""
    with allure.step("Enter a valid contribution amount"):
        logger.info("Entering contribution amount")
        
        # Get page instance from test_context
        add_aip_page = test_context.get('establish_aip_add_aip_page')
        
        if not add_aip_page:
            add_aip_page = EstablishAIPAddAIPPage(page)
            test_context['establish_aip_add_aip_page'] = add_aip_page
        
        # Enter contribution amount
        add_aip_page.enter_contribution_amount("1")
        logger.info("Amount Field --> Entered Amount as 1")
        
        # Capture the contribution amount for summary verification
        captured_amount = add_aip_page.get_contribution_amount()
        test_data = test_context.get('test_data', {})
        test_data['AIPContributionAmount'] = captured_amount
        test_context['test_data'] = test_data
        logger.info(f"Captured Contribution Amount --> {captured_amount}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Contribution Amount Entered",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('the advisor selects the frequency as "{frequency}"'))
def the_advisor_selects_the_frequency_as(page: Page, test_context: dict, frequency: str):
    """Select frequency option"""
    with allure.step(f"Select frequency as {frequency}"):
        logger.info(f"Selecting frequency: {frequency}")
        
        # Get page instance from test_context
        add_aip_page = test_context.get('establish_aip_add_aip_page')
        
        if not add_aip_page:
            add_aip_page = EstablishAIPAddAIPPage(page)
            test_context['establish_aip_add_aip_page'] = add_aip_page
        
        # Select frequency and verify all options
        add_aip_page.select_frequency(frequency)
        logger.info(f"Frequency --> Check all frequency options and select {frequency}")
        
        # Capture the selected frequency for summary verification
        selected_frequency = add_aip_page.get_selected_frequency_text()
        test_data = test_context.get('test_data', {})
        test_data['AIPFrequency'] = selected_frequency
        test_context['test_data'] = test_data
        logger.info(f"Captured Frequency --> {selected_frequency}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Frequency {frequency} Selected",
            attachment_type=allure.attachment_type.PNG
        )


@when("the advisor chooses the start and end dates from the calendar")
def the_advisor_chooses_start_and_end_dates_from_the_calendar(page: Page, test_context: dict):
    """Choose start and end dates from calendar"""
    with allure.step("Choose start and end dates from calendar"):
        logger.info("Selecting start and end dates")
        
        # Get page instance from test_context
        add_aip_page = test_context.get('establish_aip_add_aip_page')
        
        if not add_aip_page:
            add_aip_page = EstablishAIPAddAIPPage(page)
            test_context['establish_aip_add_aip_page'] = add_aip_page
        
        # Before: capture page state before opening any calendar
        allure.attach(page.screenshot(), name="Date Fields - Before Selection", attachment_type=allure.attachment_type.PNG)

        # Select start and end dates
        add_aip_page.select_start_and_end_dates()

        # Capture the start and end dates for summary verification
        start_date = add_aip_page.get_start_date()
        end_date = add_aip_page.get_end_date()
        test_data = test_context.get('test_data', {})
        test_data['AIPStartDate'] = start_date
        test_data['AIPEndDate'] = end_date
        test_context['test_data'] = test_data
        logger.info(f"Captured Start Date --> {start_date}")
        logger.info(f"Captured End Date --> {end_date}")

        allure.attach(
            f"Start Date: {start_date}\nEnd Date: {end_date}",
            name="Selected Dates",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(page.screenshot(), name="Dates Selected - Final State", attachment_type=allure.attachment_type.PNG)


@when("User verifies Account Information on Add AIP Page")
def verify_account_information_on_add_aip_page(page: Page, test_context: dict):
    """Verify account information on Add AIP Page"""
    with allure.step("Verify Account Information on Add AIP Page"):
        logger.info("\n")
        logger.info("Verifying Account Information on Add AIP Page")
        
        # Get page instance from test_context
        add_aip_page = test_context.get('establish_aip_add_aip_page')
        
        if not add_aip_page:
            add_aip_page = EstablishAIPAddAIPPage(page)
            test_context['establish_aip_add_aip_page'] = add_aip_page
        
        # Get actual account information from page
        actual_text = add_aip_page.get_account_information_text()
        logger.info(f"Actual Account Information: {actual_text}")
        
        # Get expected account information from test_data
        test_data = test_context.get('test_data', {})
        expected_text = test_data.get('AccountInformation', '')
        
        # If not in test_data, try to use account details from earlier step
        if not expected_text:
            account_details = test_context.get('establish_aip_account_details', [])
            if account_details:
                expected_text = ', '.join(account_details)
        
        logger.info(f"Expected Account Information: {expected_text}")
        
        # Verify account information
        if expected_text:
            # Use flexible comparison
            match = verify_account_info_match(expected_text, actual_text)
            
            assert match, (
                f"Account Information mismatch on Add AIP Page!\n"
                f"Expected: {expected_text}\n"
                f"Actual: {actual_text}"
            )
            logger.info("Account Information verification PASSED")
            logger.info(f"Account Information verification --> {actual_text}")
        else:
            logger.info("Account Information retrieved")
            logger.info(f"Account Information verification --> {actual_text}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Verified on Add AIP Page",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User selects the signature option "{option}" and clicks Next'))
def user_selects_signature_option_and_clicks_next(page: Page, test_context: dict, option: str):
    """Select signature option and click Next"""
    with allure.step(f"Select signature option and click Next"):
        logger.info(f"Selecting signature option: {option}")
        
        # Get page instance from test_context
        add_aip_page = test_context.get('establish_aip_add_aip_page')
        
        if not add_aip_page:
            add_aip_page = EstablishAIPAddAIPPage(page)
            test_context['establish_aip_add_aip_page'] = add_aip_page
        
        # Select signature option and click Next
        allure.attach(page.screenshot(), name="Signature Options Page - Before Selection", attachment_type=allure.attachment_type.PNG)
        summary_page = add_aip_page.select_and_verify_signature_option_and_click_next(option)
        test_context['establish_aip_summary_page'] = summary_page
        logger.info(f"Signature options --> Check all options and select: {option}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Navigated to Summary Page",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies all values on the Summary Page")
def user_verifies_all_values_on_summary_page(page: Page, test_context: dict):
    """Verify all values on Summary Page"""
    with allure.step("Verify all values on Summary Page"):
        logger.info("\n")
        logger.info("Verifying all values on Summary Page")
        
        # Get page instance from test_context
        summary_page = test_context.get('establish_aip_summary_page')
        
        if not summary_page:
            summary_page = EstablishAIPSummaryPage(page)
            test_context['establish_aip_summary_page'] = summary_page
        
        # Verify the summary page is visible
        summary_page.verify_summary_section_visible()
        logger.info("Summary Page Verification --> Summary section is visible")
        
        # Get test data
        test_data = test_context.get('test_data', {})
        
        # Assert fixed values
        summary_page.assert_request_type("Automatic Investment Plan - Establish")
        summary_page.assert_delivery_method("ACH")
        
        # Assert captured values from previous pages
        summary_page.assert_origination(test_data.get('AIPOrigination', ''))
        summary_page.assert_frequency(test_data.get('AIPFrequency', ''))
        summary_page.assert_amount(test_data.get('AIPContributionAmount', ''))
        summary_page.assert_start_date(test_data.get('AIPStartDate', ''))
        summary_page.assert_end_date(test_data.get('AIPEndDate', ''))
        
        logger.info("All Summary Values Verification --> All values verified successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Summary Page Values Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies the Acknowledgements and Agreements section")
def user_verifies_acknowledgements_section(page: Page, test_context: dict):
    """Verify Acknowledgements and Agreements section"""
    with allure.step("Verify Acknowledgements and Agreements section"):
        logger.info("\n")
        logger.info("Verifying Acknowledgements and Agreements section")
        
        # Get page instance from test_context
        summary_page = test_context.get('establish_aip_summary_page')
        
        if not summary_page:
            summary_page = EstablishAIPSummaryPage(page)
            test_context['establish_aip_summary_page'] = summary_page
        
        # Get expected acknowledgements based on account type (IRA vs Non-IRA)
        current_role = test_context.get('current_role', '')
        if current_role == 'ira-account':
            if get_settings().env == 'prod':
                expected_acknowledgements = "|".join(Constants.get_establish_aip_disclosures_ira_prod())
            else:
                expected_acknowledgements = "|".join(Constants.get_establish_aip_disclosures_ira())
        else:
            expected_acknowledgements = "|".join(Constants.get_establish_aip_disclosures())
        
        try:
            summary_page.verify_acknowledgements_section(expected_acknowledgements)
            logger.info("Acknowledgements Section Verification --> Verified successfully")

            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="Acknowledgements Section Verified",
                attachment_type=allure.attachment_type.PNG
            )
        except AssertionError:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="Acknowledgements Section FAILED",
                attachment_type=allure.attachment_type.PNG
            )
            raise


@when("User clicks the Submit button")
def user_clicks_submit_button(page: Page, test_context: dict):
    """Click Submit button"""
    with allure.step("Click Submit button"):
        logger.info("\n")
        logger.info("Clicking Submit button")
        
        # Get page instance from test_context
        summary_page = test_context.get('establish_aip_summary_page')
        
        if not summary_page:
            summary_page = EstablishAIPSummaryPage(page)
            test_context['establish_aip_summary_page'] = summary_page
        
        # Click Submit button and navigate to Confirmation page
        confirmation_page = summary_page.click_submit_button()
        test_context['establish_aip_confirmation_page'] = confirmation_page
        logger.info("Submit Button --> Clicked successfully, landed on Confirmation Page")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Navigated to Confirmation Page",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies the success banner on Confirmation Page")
def user_verifies_success_banner(page: Page, test_context: dict):
    """Verify success banner on Confirmation Page"""
    with allure.step("Verify success banner on Confirmation Page"):
        logger.info("\n")
        logger.info("Verifying success banner on Confirmation Page")
        
        # Get page instance from test_context
        confirmation_page = test_context.get('establish_aip_confirmation_page')
        
        if not confirmation_page:
            confirmation_page = EstablishAIPConfirmationPage(page)
            test_context['establish_aip_confirmation_page'] = confirmation_page
        
        confirmation_page.verify_success_banner_displayed()
        logger.info("Success Banner --> Request submitted successfully banner verified")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Success Banner Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies the Request Summary section on Confirmation Page")
def user_verifies_request_summary_on_confirmation_page(page: Page, test_context: dict):
    """Verify Request Summary section on Confirmation Page"""
    with allure.step("Verify Request Summary section on Confirmation Page"):
        logger.info("\n")
        logger.info("Verifying Request Summary section")
        
        # Get page instance from test_context
        confirmation_page = test_context.get('establish_aip_confirmation_page')
        
        if not confirmation_page:
            confirmation_page = EstablishAIPConfirmationPage(page)
            test_context['establish_aip_confirmation_page'] = confirmation_page
        
        # Verify Request Summary section is visible
        confirmation_page.verify_request_summary_section_visible()
        logger.info("Request Summary Section --> Visible")
        
        # Assert Status is Complete
        confirmation_page.assert_status_complete()
        logger.info("Status --> Complete")
        
        # Assert Item Number format (starts with A followed by digits)
        confirmation_page.assert_item_number_format()
        item_number = confirmation_page.get_item_number()
        logger.info(f"Item Number --> {item_number}")
        
        # Assert Submitted By (Agent Name) from test data
        test_data = test_context.get('test_data', {})
        agent_name = test_data.get('AgentName', '')
        if agent_name:
            confirmation_page.assert_submitted_by(agent_name)
        logger.info(f"Submitted By --> {agent_name}")
        
        # Log Submission Date/Time
        submission_datetime = confirmation_page.get_submission_datetime()
        logger.info(f"Submission Date/Time --> {submission_datetime}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Request Summary Section Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies the Request Details section on Confirmation Page")
def user_verifies_request_details_on_confirmation_page(page: Page, test_context: dict):
    """Verify Request Details section on Confirmation Page"""
    with allure.step("Verify Request Details section on Confirmation Page"):
        logger.info("\n")
        logger.info("Verifying Request Details section")
        
        # Get page instance from test_context
        confirmation_page = test_context.get('establish_aip_confirmation_page')
        
        if not confirmation_page:
            confirmation_page = EstablishAIPConfirmationPage(page)
            test_context['establish_aip_confirmation_page'] = confirmation_page
        
        # Verify Request Details section is visible
        confirmation_page.verify_request_details_section_visible()
        logger.info("Request Details Section --> Visible")
        
        # Get test data
        test_data = test_context.get('test_data', {})
        
        # Assert fixed values
        confirmation_page.assert_request_type("Automatic Investment Plan - Establish")
        logger.info("Request Type --> Automatic Investment Plan - Establish")
        
        confirmation_page.assert_delivery_method("ACH")
        logger.info("Delivery Method --> ACH")
        
        # Assert captured values from previous pages
        origination = test_data.get('AIPOrigination', '')
        confirmation_page.assert_origination(origination)
        logger.info(f"Origination --> {origination}")
        
        frequency = test_data.get('AIPFrequency', '')
        confirmation_page.assert_frequency(frequency)
        logger.info(f"Frequency --> {frequency}")
        
        amount = test_data.get('AIPContributionAmount', '')
        confirmation_page.assert_amount(amount)
        logger.info(f"Amount --> {amount}")
        
        start_date = test_data.get('AIPStartDate', '')
        confirmation_page.assert_start_date(start_date)
        logger.info(f"Start Date --> {start_date}")
        
        end_date = test_data.get('AIPEndDate', '')
        confirmation_page.assert_end_date(end_date)
        logger.info(f"End Date --> {end_date}")
        
        logger.info("Request Details Verification --> All values verified successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Request Details Section Verified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User verifies Account Information on Confirmation Page")
def user_verifies_account_info_on_confirmation_page(page: Page, test_context: dict):
    """Verify Account Information on Confirmation Page"""
    with allure.step("Verify Account Information on Confirmation Page"):
        logger.info("\n")
        logger.info("Verifying Account Information on Confirmation Page")
        
        # Get page instance from test_context
        confirmation_page = test_context.get('establish_aip_confirmation_page')
        
        if not confirmation_page:
            confirmation_page = EstablishAIPConfirmationPage(page)
            test_context['establish_aip_confirmation_page'] = confirmation_page
        
        # Get actual account information from page
        actual_account_info = confirmation_page.get_account_information_text()
        logger.info(f"Actual Account Information: {actual_account_info}")
        
        # Get expected account information from test_data
        test_data = test_context.get('test_data', {})
        expected_account_info = test_data.get('AccountInformation', '')
        
        # If not in test_data, try to use account details from earlier step
        if not expected_account_info:
            account_details = test_context.get('establish_aip_account_details', [])
            if account_details:
                expected_account_info = ', '.join(account_details)
        
        logger.info(f"Expected Account Information: {expected_account_info}")
        
        # Verify account information
        if expected_account_info:
            # Use flexible comparison
            match = verify_account_info_match(expected_account_info, actual_account_info)
            
            assert match, (
                f"Account Information mismatch on Confirmation Page!\n"
                f"Expected: {expected_account_info}\n"
                f"Actual: {actual_account_info}"
            )
            logger.info("Account Information verification PASSED")
            logger.info(f"Account Information --> {actual_account_info}")
        else:
            logger.info("Account Information retrieved")
            logger.info(f"Account Information --> {actual_account_info}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account Information Verified on Confirmation Page",
            attachment_type=allure.attachment_type.PNG
        )


@when("User clicks the Close button")
def user_clicks_close_button(page: Page, test_context: dict):
    """Click Close button"""
    with allure.step("Click Close button"):
        logger.info("\n")
        logger.info("Clicking Close button")
        
        # Get page instance from test_context
        confirmation_page = test_context.get('establish_aip_confirmation_page')
        
        if not confirmation_page:
            confirmation_page = EstablishAIPConfirmationPage(page)
            test_context['establish_aip_confirmation_page'] = confirmation_page
        
        # Click Close button
        confirmation_page.click_close_button()
        logger.info("Close Button --> Clicked successfully")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Clicking Close Button",
            attachment_type=allure.attachment_type.PNG
        )

