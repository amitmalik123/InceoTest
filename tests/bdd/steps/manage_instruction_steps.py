import random

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.add_ach_instruction import AddACHInstructionPage
from utils.allure_logger import get_allure_logger
from utils.api_response_utils import (
    get_values_from_household_api_open_accounts,
    retrieve_all_values_from_response,
    retrieve_boolean_value_from_response,
)
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


@when('User should click on the "ACH" radio button and click on Next')
def select_radio_and_click_on_next(authenticated_page: Page, manage_instruction_1_page):
    """Select radio button and click Next"""
    radio_type = "ACH"
    logger.info(f"Selecting {radio_type} radio button and clicking Next")
    manage_instruction_1_page.select_radio_button(radio_type)
    manage_instruction_1_page.click_next_button()


@when("User should click on the Add Button to land on the Add ACH Instructions Page")
def click_on_add_button(authenticated_page: Page, manage_instruction_2_page):
    """Click on Add button to land on Add ACH Instructions Page"""
    logger.info("Clicking on Add Button")
    manage_instruction_2_page.click_add_button()


@when("User should fetch ClientHouseholdID")
def fetch_household_id(
    authenticated_page: Page, manage_instruction_1_page, dmtool_page, test_context, request
):
    """Fetch the ClientHouseholdID from the URL"""
    logger.info("Fetching ClientHouseholdID")

    # Check scenario name to determine which page object to use
    scenario_name = request.node.name

    if "Address Change" in scenario_name or "address_change" in scenario_name:
        household_id = dmtool_page.get_household_id()
    else:
        household_id = manage_instruction_1_page.get_household_id()

    # Store in test context for later use
    test_context["household_id"] = household_id
    logger.info(f"ClientHouseholdID stored: {household_id}")


@then("User to fetch Client Household API values")
def fetch_client_household_api_values(test_context, api_utility_page):
    logger.info("Fetching Client Household API values from response")

    if not api_utility_page.last_response:
        raise ValueError("No API response found. Make sure to call API endpoint first")

    try:
        response = api_utility_page.last_response

        # Fetch account details using JSON paths
        account_names = retrieve_all_values_from_response(
            response, get_values_from_household_api_open_accounts("accountName")
        )
        account_numbers = retrieve_all_values_from_response(
            response, get_values_from_household_api_open_accounts("accountNumber")
        )
        account_strategies = retrieve_all_values_from_response(
            response, get_values_from_household_api_open_accounts("accountStrategy")
        )
        custodian_ids = retrieve_all_values_from_response(
            response, get_values_from_household_api_open_accounts("custodianID")
        )

        # Fetch hasGNWAccount boolean value
        has_gnw_account = retrieve_boolean_value_from_response(response, "hasGNWAccount")

        # Store all values in test context
        test_context["investment_account_names"] = account_names
        test_context["investment_account_numbers"] = account_numbers
        test_context["investment_account_strategies"] = account_strategies
        test_context["custodian_ids"] = custodian_ids
        test_context["has_gnw_account"] = has_gnw_account

        # Log extracted values
        logger.info(f"Fetched {len(account_names)} account names")
        logger.info(f"Fetched {len(account_numbers)} account numbers")
        logger.info(f"Fetched {len(account_strategies)} account strategies")
        logger.info(f"Fetched {len(custodian_ids)} custodian IDs")
        logger.info(f"Has GNW Account: {has_gnw_account}")

        logger.info("✓ Client Household API values fetched and stored successfully")
    except Exception as e:
        logger.error(f"Failed to fetch Client Household API values: {str(e)}")
        raise


@then(
    parsers.parse(
        'User should enter valid AINS page details "{select_account}" for radio type "{radio_type}" and SLOA option as "{sloa_option}" and SLOASubOption as "{sloa_sub_option}" and role as "{role}"'
    )
)
def enter_valid_ains_page_details(
    authenticated_page: Page,
    select_account,
    radio_type,
    sloa_option,
    sloa_sub_option,
    role,
    test_context,
    add_ach_instruction_page,
):
    logger.info(f"Entering AINS page details for account type: {select_account}")

    test_context["initial_role"] = role

    random_bank_number = str(random.randint(1_000_000_000, 9_999_999_999))
    logger.info(f"Generated random bank number: {random_bank_number}")

    entered_new_ains_details = add_ach_instruction_page.enter_details_for_vanishing_errors(
        "121000358", random_bank_number, random_bank_number, sloa_option, sloa_sub_option, "Yes"
    )

    if select_account == "oneAccount":
        investment_account_names = test_context.get("investment_account_names", [])

        if investment_account_names:
            invest_account_nums = len(investment_account_names)
            invest_account_num = random.randint(0, invest_account_nums - 1)
            selected_investment_account = add_ach_instruction_page.select_one_account(
                invest_account_num
            )
        else:
            selected_investment_account = add_ach_instruction_page.select_one_account(0)

        entered_new_ains_details.append(selected_investment_account)
        logger.info(f"Selected one account: {selected_investment_account}")

    elif select_account == "multiAccount":
        selected_investment_accounts = add_ach_instruction_page.select_multiple_accounts()
        entered_new_ains_details.append(selected_investment_accounts)
        logger.info(f"Selected multiple accounts: {selected_investment_accounts}")

    test_context["entered_new_ains_details"] = entered_new_ains_details
    logger.info("✓ AINS page details entered successfully")


@when(
    parsers.parse(
        'User should verify the "{household_header}" Heading and the sub-heading as the Account name'
    )
)
def validate_household_heading(
    authenticated_page: Page, household_header, test_context, request, soft_assert
):
    logger.info(f"Validating household heading: {household_header}")

    add_ach_instruction_page = AddACHInstructionPage(authenticated_page)
    heading_and_account = add_ach_instruction_page.get_household_heading_and_account(
        household_header
    )

    actual_heading = heading_and_account[0]
    actual_account_name = heading_and_account[1]

    scenario_name = request.node.name
    expected_account_name = test_context.get("account_name", "")

    if "OA Trading Tool" in scenario_name:
        expected_account_name = test_context.get("account_name", "")

    # Use soft_assert fixture - auto-validates at test end
    soft_assert.assert_equal(
        actual_heading,
        household_header,
        f"Household heading mismatch. Expected: {household_header}, Actual: {actual_heading}",
    )
    soft_assert.assert_equal(
        actual_account_name,
        expected_account_name,
        f"Account name mismatch. Expected: {expected_account_name}, Actual: {actual_account_name}",
    )

    logger.info(f"Validation of HouseHold Heading: {household_header}")
    logger.info("Account Name Validation: Passed")


@then(
    "User should click on the Next Button on Add ACH instruction Page to navigate back on summary page"
)
def click_next_button_on_add_ach_page(authenticated_page: Page, add_ach_instruction_page):
    logger.info("Clicking Next button to navigate to summary page")

    add_ach_instruction_page.click_next()

    summary_header = authenticated_page.locator("text='Request Summary'")
    Assertions.assert_true(summary_header.is_visible(), "Request Summary header not found")
    logger.info("Navigated to Summary Page - Request Summary header verified")
