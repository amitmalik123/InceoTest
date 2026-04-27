"""
BDD step definitions for Account Management - Account Suspension flow.

Steps cover:
  - Login (reuses existing step from change_investments_steps)
  - Navigate to Account Wizard and search client
  - Select request and type in Account Management
  - Complete and Print
  - DocuSign flow (Continue & Finish)
  - Fetch tracking ID and close
  - Upload PDF
  - Verify tracking ID starts with B
"""

from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from pages.account_list_page import AccountListPage
from pages.account_management_page import AccountManagementPage
from pages.clients_page import ClientsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


# ------------------------------------------------------------------
# Given: Login
# ------------------------------------------------------------------


@given("User login into ewm application on test11 environment")
def user_login_into_ewm_application(authenticated_page: Page, test_context: dict):
    """
    Verify the user is authenticated on the eWealthManager application.
    The `authenticated_page` fixture handles session storage / auto-login.
    """
    current_url = authenticated_page.url
    logger.info(f"Verifying login status - Current URL: {current_url}")
    if current_url and "login" not in current_url.lower():
        logger.info("User is already authenticated (session storage)")
        return
    error_msg = "AUTHENTICATION FAILED: User is not logged in on test11."
    logger.error(error_msg)
    raise AssertionError(error_msg)


# ------------------------------------------------------------------
# When: Navigate to Account Wizard and search client
# ------------------------------------------------------------------


@when("User is on the account wizard tab and search the client")
def navigate_to_account_wizard_and_search(
    authenticated_page: Page,
    clients_page: ClientsPage,
    account_list_page: AccountListPage,
    test_context: dict,
):
    """
    Navigate to Clients > Account List, search the client, select the
    account, then navigate to Account Wizard.
    """
    client_id = test_context["test_data"]["client_id"]
    account_name = test_context["test_data"]["account_name"]

    # Step 1: Navigate to Clients > Account List
    logger.info("Navigating to Clients menu")
    clients_page.navigate()
    clients_page.click_clients()
    logger.info("Clicking Account List")
    clients_page.click_account_list()
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    logger.info("Account List page loaded")

    # Step 2: Search for the client
    logger.info(f"Searching for client: {client_id}")
    account_list_page.search_client(client_id)
    logger.info(f"Search completed for client: {client_id}")

    # Step 3: Select the account
    logger.info(f"Selecting account: {account_name}")
    account_list_page.select_account(account_name, client_id)
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    logger.info("Account selected, on Holdings/Detail page")

    # Step 4: Click Account Wizard
    logger.info("Clicking Account Wizard link")
    account_wizard_link = authenticated_page.locator("#clientDetailAccountDetailAnchor")
    account_wizard_link.wait_for(state="visible", timeout=15000)
    
    # Use increased timeout (60s) for click to allow page navigation to complete
    # Some environments (test10, slow networks) may take 30-60s for navigation
    logger.info("Waiting for page navigation after Account Wizard click...")
    account_wizard_link.click(timeout=60000)
    
    # Wait for page to fully load after navigation
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=45000)
    authenticated_page.wait_for_load_state("networkidle", timeout=45000)
    
    logger.info(f"Account Wizard page loaded: {authenticated_page.url}")


# ------------------------------------------------------------------
# And: Select request and type in Account Management
# ------------------------------------------------------------------


@when(parsers.parse('Select request "{request_name}" and type "{type_name}" in Account Management'))
def select_request_and_type(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
    request_name: str,
    type_name: str,
):
    """Select the specified request and type in the Account Management section."""
    logger.info(f"Selecting request: '{request_name}', type: '{type_name}'")
    account_management_page.select_request_and_type(request_name, type_name)
    logger.info("Request and type selected in Account Management")


# ------------------------------------------------------------------
# When: Click Complete and Print
# ------------------------------------------------------------------


@when("User clicks on complete and print button")
def click_complete_and_print(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
):
    """Click the Complete and Print button."""
    logger.info("Clicking 'Complete and Print' button")
    account_management_page.click_complete_and_print()
    logger.info("'Complete and Print' clicked")


# ------------------------------------------------------------------
# Then: DocuSign - Continue & Finish
# ------------------------------------------------------------------


@then("User navigates to docu sign page and clicks on Continue and Finish button")
def handle_docusign(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
):
    """Handle the DocuSign redirect — click Continue & Finish."""
    logger.info("Handling DocuSign page")
    account_management_page.handle_docusign_page()
    logger.info("DocuSign completed")


# ------------------------------------------------------------------
# And: Fetch tracking ID and close
# ------------------------------------------------------------------


@then("Fetch the tracking id and click on close button")
def fetch_tracking_id_and_close(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
    test_context: dict,
):
    """Fetch the tracking ID from the confirmation page and click Close."""
    logger.info("Fetching tracking ID")
    tracking_id = account_management_page.fetch_tracking_id()
    test_context["tracking_id"] = tracking_id
    logger.info(f"Tracking ID captured: {tracking_id}")

    account_management_page.click_close_button()
    logger.info("Close button clicked")


# ------------------------------------------------------------------
# And: Upload PDF
# ------------------------------------------------------------------


@then("User upload the PDF file")
def upload_pdf(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
):
    """Upload a PDF file on the tracking center page."""
    logger.info("Uploading PDF file")
    account_management_page.upload_pdf()
    logger.info("PDF uploaded successfully")


# ------------------------------------------------------------------
# And: Verify tracking ID starts with B
# ------------------------------------------------------------------


@then("User verify the tracking Id starts with B")
def verify_tracking_id_starts_with_b(
    authenticated_page: Page,
    account_management_page: AccountManagementPage,
    test_context: dict,
):
    """Verify that the captured tracking ID starts with 'B'."""
    tracking_id = test_context.get("tracking_id", "")
    logger.info(f"Verifying tracking ID: '{tracking_id}' starts with 'B'")
    account_management_page.verify_tracking_id_starts_with("B", tracking_id)
    logger.info(f"Tracking ID '{tracking_id}' verified — starts with B")
