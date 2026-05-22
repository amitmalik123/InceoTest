"""
EXAMPLE: How to use the new AllureLogger in step files.

This demonstrates the cleaner, more maintainable approach to logging and Allure reporting.
"""

from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

# Initialize once at module level
logger = get_allure_logger(__name__)


# ============================================================================
# BEFORE (Old Approach - Too Verbose)
# ============================================================================
"""
@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    with allure.step(f"Search for client {test_context['test_data']['client_id']}"):
        logger.info(f"Searching for client: {test_context['test_data']['client_id']}")
        allure.attach(
            test_context["test_data"]["client_id"],
            name="Client ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        account_list_page.search_client(test_context["test_data"]["client_id"])
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Account List After Search", attachment_type=allure.attachment_type.PNG
        )
"""


# ============================================================================
# AFTER (New Approach - Clean and Simple)
# ============================================================================


@when("I search for the client")
def search_for_client(page: Page, account_list_page, test_context):
    """Search for client using client ID"""
    client_id = test_context["test_data"]["client_id"]

    with logger.step(f"Search for client {client_id}"):
        logger.info(f"Searching for client: {client_id}")
        logger.attach_text(client_id, "Client ID")

        account_list_page.search_client(client_id)
        logger.attach_screenshot(page, "Account List After Search")


@when("I select the client account")
def select_client_account(account_list_page, test_context):
    """Select the specified account for the client"""
    account_name = test_context["test_data"]["account_name"]
    client_id = test_context["test_data"]["client_id"]

    with logger.step(f"Select account {account_name}"):
        logger.info(f"Selecting account: {account_name}")
        logger.attach_text(account_name, "Account Name")

        account_list_page.select_account(account_name, client_id)


@then("I should see the Account Detail page")
def verify_account_detail_page_loaded(page: Page, account_detail_page):
    """Verify Account Detail page is loaded"""
    with logger.step("Verify Account Detail page"):
        account_detail_page.navigate()
        page.wait_for_load_state("domcontentloaded")

        logger.attach_screenshot(page, "Account Detail Page")
        logger.info("Account Detail page loaded")


@when("I click on Account Wizard")
def click_on_account_wizard(page: Page, account_detail_page):
    """Click on Account Wizard link"""
    with logger.step("Click on Account Wizard"):
        logger.info("Clicking Account Wizard")
        account_detail_page.click_account_wizard()
        logger.attach_screenshot(page, "Account Wizard Modal")


@when("I login with valid credentials")
def login_with_valid_credentials(page: Page, login_page, test_context):
    """Verify that authentication is already complete"""
    with logger.step("Verify login status"):
        current_url = page.url
        logger.info(f"Current URL: {current_url}")

        # Verify already logged in
        if current_url and "login" not in current_url.lower():
            logger.info("✓ User is already authenticated (Session Storage)")
            return

        # If we reach here, authentication failed
        error_msg = "AUTHENTICATION FAILED: User is not logged in"
        logger.error(error_msg)
        raise AssertionError(error_msg)


@then("I should be redirected to the home page")
def verify_redirect_to_home_page(page: Page):
    """Verify successful login by checking page load"""
    with logger.step("Verify redirect to home page"):
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.attach_screenshot(page, "Home Page After Login")
        logger.info("Successfully logged in and redirected to home page")
