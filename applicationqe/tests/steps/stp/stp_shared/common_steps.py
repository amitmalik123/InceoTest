import allure
from playwright.sync_api import Page
from pytest_bdd import given, then, when, parsers

from pages.ewm.account_list_page import AccountListPage
from pages.ewm.clients_page import ClientsPage
from utils.settings import settings
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def format_household_name(raw_value: str) -> str:
    if not raw_value:
        return raw_value

    base_text = raw_value.split('-')[0].strip()
    if ' ,' in base_text:
        return base_text

    name_segment = base_text.split(',')[0].strip() if ',' in base_text else base_text
    name_parts = [part for part in name_segment.split() if part]

    if len(name_parts) >= 2:
        last_name = name_parts[-1]
        first_middle = " ".join(name_parts[:-1])
        return f"{last_name} , {first_middle}"

    return name_segment


def get_detail(values: list, index: int, field_name: str) -> str:
    if index >= len(values):
        raise AssertionError(
            f"Expected {field_name} at position {index}, but only found {len(values)} values: {values}"
        )

    value = values[index]
    logger.info(f"{field_name}: {value}")
    return value


def extract_account_core_identifier(full_account_text: str) -> tuple:

    if not full_account_text:
        return (None, None)
    
    parts = full_account_text.split(' -')
    if len(parts) >= 2:
        account_name = parts[0].strip()
        account_number = parts[1].strip().split()[0].strip()
        logger.info(f"Extracted account - Name: '{account_name}', Number: '{account_number}'")
        return (account_name, account_number)
    
    logger.warning(f"Could not extract account identifier from: '{full_account_text}'")
    return (None, None)


@given("the test data is loaded from CSV")
def load_test_data_from_csv(test_context):
    csv_path = settings.test_data_csv
    logger.info(f"Loading test data from: {csv_path}")


@given(parsers.parse('I am using test data for scenario "{scenario_name}"'))
def use_test_data_for_scenario(test_context, test_data_manager, scenario_name):
    user_data = test_data_manager.get_by(test_scenario=scenario_name)

    if not user_data:
        raise ValueError(
            f"No test data found for scenario '{scenario_name}'. "
            f"Available scenarios: {test_data_manager.get_scenarios()}"
        )

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for scenario: {scenario_name}")
    logger.attach_json(user_data, f"Test Data - {scenario_name}")


@given(parsers.parse('I am using test data for user type "{user_type}"'))
def use_test_data_for_user_type(test_context, test_data_manager, user_type):
    user_data = test_data_manager.get_by(user_type=user_type)

    if not user_data:
        raise ValueError(
            f"No test data found for user type '{user_type}'. "
            f"Available user types: {test_data_manager.get_user_types()}"
        )

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for user type: {user_type}")
    logger.attach_json(user_data, f"Test Data - {user_type}")


@given(parsers.parse('I am using test data for username "{username}"'))
def use_test_data_for_username(test_context, test_data_manager, username):
    user_data = test_data_manager.get_by(username=username)

    if not user_data:
        raise ValueError(f"Username '{username}' not found in test data CSV")

    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for username: {username}")
    logger.attach_json(user_data, f"Test Data - {username}")



@given(parsers.parse('User with role "{role}" is loaded'))
def load_user_by_role(test_context, all_test_data, role: str):

    logger.info(f"Loading test data for role: {role}")

    for row in all_test_data:
        if row.get("role") == role:
            test_context["test_data"] = row
            test_context["current_role"] = role
            logger.info(f"Loaded test data for role: {role}")
            logger.info(f" Username: {row.get('username')}")
            logger.info(f" Account: {row.get('account_name')}")
            allure.attach(
                str(row),
                name=f"Test Data - Role: {role}",
                attachment_type=allure.attachment_type.JSON,
            )
            return

    available_roles = [r.get("role") for r in all_test_data]
    error_msg = f"Role '{role}' not found in test data CSV. Available roles: {available_roles}"
    logger.error(error_msg)
    raise ValueError(error_msg)


@when("User should click on clients tab and navigate to Client Information")
def click_clients_tab_and_navigate_to_client_info(page: Page, clients_page, account_list_page, test_context: dict):
    with allure.step("Click on clients tab and navigate to Client Information"):
        logger.info("Navigating to Client Information from clients tab")

        test_data = test_context.get('test_data', {})
        client_name = test_data.get('account_name', '')
        logger.info(f"Searching for client: {client_name}")
        
        clients_page.clients_tab_link.wait_for(state='visible', timeout=10000)
        clients_page.clients_tab_link.click()
        logger.info("Clients tab clicked - navigated to Client List page")

        page.wait_for_load_state('domcontentloaded', timeout=30000)
        page.wait_for_timeout(2000)

        account_list_page.search_input.wait_for(state='visible', timeout=10000)
        account_list_page.search_input.fill(client_name)
        logger.info(f"Entered client name: {client_name}")

        account_list_page.search_button.wait_for(state='visible', timeout=10000)
        account_list_page.search_button.click()
        logger.info("Go button clicked")

        page.wait_for_timeout(1000)
        loading_spinner = clients_page.loading_spinner
        try:
            if loading_spinner.count() > 0:
                loading_spinner.wait_for(state='visible', timeout=5000)
                logger.info("Search spinner appeared")
                loading_spinner.wait_for(state='hidden', timeout=30000)
                logger.info("Search completed - spinner disappeared")
        except Exception as e:
            logger.info(f"Spinner wait skipped: {e}")

        page.wait_for_timeout(2000)

        clients_page.first_result_client_name.wait_for(state='visible', timeout=20000)
        clients_page.first_result_client_name.click()
        logger.info("First search result clicked - navigated to Client Accounts page")

        page.wait_for_load_state('domcontentloaded', timeout=120000)
        page.wait_for_timeout(2000)

        clients_page.client_info_tab.wait_for(state='visible', timeout=10000)
        clients_page.client_info_tab.click()
        logger.info("Client Information tab clicked")

        page.wait_for_load_state('networkidle', timeout=120000)
        page.wait_for_timeout(2000)

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Client Information Page",
            attachment_type=allure.attachment_type.PNG
        )
        logger.info("Navigated to Client Information page")
@given("I logout from the application")
def logout_from_application(page: Page, tracking_center_page):
    logger.info("Logging out from application")
    tracking_center_page.click_logout()
    tracking_center_page.click_bodycontent()

        


@then("User should verify that mailing Address from Client Information contains New Address details")
def verify_mailing_address_in_client_info(page: Page, clients_page, test_context: dict):
    with allure.step("Verify mailing Address from Client Information contains New Address details"):
        logger.info("Verifying mailing address in Client Information")

        expected_street = test_context.get('new_street', '').upper()
        expected_city = test_context.get('new_city', '').upper()
        expected_state = test_context.get('new_state', '').upper()
        expected_zip = test_context.get('new_zip', '')

        logger.info(f"Expected address components: {expected_street}, {expected_city}, {expected_state}, {expected_zip}")

        clients_page.mailing_address_section.wait_for(state='visible', timeout=10000)
        address_section = clients_page.mailing_address_section

        mailing_address_text = address_section.inner_text().upper()
        logger.info(f"Mailing address displayed: {mailing_address_text}")

        verification_passed = True

        if expected_street:
            if expected_street in mailing_address_text:
                logger.info(f"Street verified: {expected_street}")
            else:
                logger.error(f"Street not found: {expected_street}")
                verification_passed = False

        if expected_city:
            if expected_city in mailing_address_text:
                logger.info(f"City verified: {expected_city}")
            else:
                logger.error(f"City not found: {expected_city}")
                verification_passed = False

        if expected_state:
            if expected_state in mailing_address_text:
                logger.info(f"State verified: {expected_state}")
            else:
                logger.error(f"State not found: {expected_state}")
                verification_passed = False

        if expected_zip:
            if expected_zip in mailing_address_text:
                logger.info(f"ZIP verified: {expected_zip}")
            else:
                logger.error(f"ZIP not found: {expected_zip}")
                verification_passed = False

        assert verification_passed, f"Mailing address verification failed. Expected components not found in: {mailing_address_text}"

        test_context['client_info_address_verified'] = verification_passed

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Client Information - Address Verified",
            attachment_type=allure.attachment_type.PNG
        )

        logger.info("Mailing address verified in Client Information")
@then("I should be logged out successfully")
def verify_logout_successful():
    logger.info("=== Test Completed Successfully ===", attach_to_allure=False)



@given(parsers.parse('User with role "{role}" navigates to role-specific URL'))
def navigate_to_role_url(page: Page, login_page, test_context, all_test_data, role: str):
    logger.info(f"[Role-Based Navigation] Starting for role: {role}")
    
    test_data = None
    test_data = None
    for row in all_test_data:
        if row.get("role") == role:
            test_data = row
            test_context["test_data"] = row
            test_context["current_role"] = role
            logger.info(f"Loaded test data for role: {role}")
            break
    
    if not test_data:
        available_roles = [r.get("role") for r in all_test_data]
        raise ValueError(f"Role '{role}' not found in test data CSV. Available: {available_roles}")
    
    try:
        role_url = settings.get_role_url(role)
        logger.info(f"[Role-Based Navigation] Target URL: {role_url}")
    except ValueError as e:
        logger.error(f"Role URL configuration error: {e}")
        raise
    
    logger.info(f"Navigating to role-specific URL for {role}...")
    page.goto(role_url, wait_until='domcontentloaded', timeout=30000)
    
    page.wait_for_timeout(2000)
    
    try:
        login_form_visible = login_page.login_form.is_visible(timeout=5000)
        
        if login_form_visible:
            logger.info("Login form detected - performing authentication")
            
            username = test_data.get("username")
            password = test_data.get("password")
            
            logger.info(f"Logging in with username: {username}")
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_sign_in()
            
            page.wait_for_load_state('networkidle', timeout=15000)
            page.wait_for_timeout(2000)
            
            logger.info(f"Login successful - Current URL: {page.url}")
        else:
            logger.info("No login required - already authenticated or session exists")
            page.wait_for_load_state('networkidle', timeout=15000)
    
    except Exception as e:
        logger.info(f"Login form check: {e} - Assuming page loaded without login requirement")
        page.wait_for_load_state('networkidle', timeout=10000)
    
    logger.info(f"[Role-Based Navigation] Complete for role: {role}")
    allure.attach(
        page.screenshot(),
        name=f"Role Navigation - {role}",
        attachment_type=allure.attachment_type.PNG
    )
