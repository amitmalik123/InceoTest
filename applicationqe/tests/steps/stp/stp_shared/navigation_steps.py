import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from pages.stp.shared.account_detail_page import AccountDetailPage
from pages.stp.shared.account_list_page import AccountListPage
from pages.stp.shared.clients_page import ClientsPage
from pages.stp.shared.new_nav_wrapper_page import NewNavWrapperPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I navigate to Clients menu")
def navigate_to_clients_menu(page: Page, clients_page: ClientsPage):
    logger.info("Navigating to clients menu")
    allure.attach(page.screenshot(), name="Before Navigate to Clients", attachment_type=allure.attachment_type.PNG)
    clients_page.navigate()
    allure.attach(page.screenshot(), name="Before Click Clients", attachment_type=allure.attachment_type.PNG)
    clients_page.click_clients()


@when("I click on Account List")
def click_on_account_list(page: Page, clients_page: ClientsPage):
    """Click on Account List menu item"""
    logger.info("Clicking Account List")
    clients_page.click_account_list()


@then("I should see the Account List page")
def verify_account_list_page_loaded(page: Page):
    """Verify Account List page is loaded"""
    logger.info(f"Verifying Account List page loaded - URL: {page.url}")
    page.wait_for_load_state("domcontentloaded", timeout=30000)


@when("User is on the accountlist tab and search with the accountNo")
def verify_account_list_page_loaded_and_search(
    page: Page, account_list_page: AccountListPage, test_context
):
    """Verify Account List page is loaded and search for client"""
    with allure.step("Verify Account List page is loaded and search for client"):
        # Check if iframe context override exists (for manage_bene scenario)
        if 'account_list_page_iframe' in test_context:
            account_list_page = test_context['account_list_page_iframe']
            logger.info("Using iframe context for account list page")
        
        logger.info(f"Account list page loaded. Current URL: {page.url}")
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Account List Page", attachment_type=allure.attachment_type.PNG
        )

        client_id = test_context['test_data']['client_id']
        logger.info(f"Searching for client: {client_id}")
        allure.attach(
            client_id,
            name="Client ID",
            attachment_type=allure.attachment_type.TEXT,
        )
        
        # Store account_number in test_context for later validation
        test_context['account_number'] = client_id
        logger.info(f"Stored account_number in test_context: {client_id}")
        
        account_list_page.search_client(client_id)
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Account List After Search", attachment_type=allure.attachment_type.PNG
        )


@when("User should click on searched account and navigate to account wizard page")
def click_searched_account_and_navigate_to_wizard(
    page: Page,
    account_list_page: AccountListPage,
    account_detail_page: AccountDetailPage,
    test_context,
):
    """Click on searched account and navigate to account wizard page"""
    with allure.step("Click on searched account and navigate to account wizard page"):
        # Check if iframe context override exists (for manage_bene scenario)
        if 'account_list_page_iframe' in test_context:
            account_list_page = test_context['account_list_page_iframe']
            logger.info("Using iframe context for account selection")
        
        logger.info(f"Current URL: {page.url}")
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account List Before Selection",
            attachment_type=allure.attachment_type.PNG,
        )
        account_list_page.select_account(
            test_context["test_data"]["account_name"], test_context["test_data"]["client_id"]
        )
        
        # Wait for navigation to account detail page
        try:
            page.wait_for_load_state("networkidle", timeout=60000)
        except Exception:
            # networkidle can be slow on test11; domcontentloaded is enough to proceed
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="After Account Selection", attachment_type=allure.attachment_type.PNG
        )
        account_detail_page.click_account_wizard()
        page.wait_for_timeout(20000)
        logger.info(f"Navigated to Account Wizard. Current URL: {page.url}")
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Account Wizard Page", attachment_type=allure.attachment_type.PNG
        )


@then("I verify account wizard page is loaded")
def verify_account_wizard_page_is_loaded(page: Page, account_wizard_page):
    """Verify Account Wizard page is loaded"""
    logger.info(f"Verifying Account Wizard page is loaded at {page.url}")
    account_wizard_page.verify_account_wizard_page_loaded()


@when("I navigate to Clients menu in new nav bar")
def navigate_to_clients_menu(page: Page, clients_page: ClientsPage):
    """Navigate to clients menu"""
    logger.info("Navigating to clients menu")
    allure.attach(page.screenshot(), name="Before Navigate to Clients (New Nav)", attachment_type=allure.attachment_type.PNG)
    clients_page.navigate_to_new_nav()
    allure.attach(page.screenshot(), name="Before Click Clients (New Nav)", attachment_type=allure.attachment_type.PNG)
    clients_page.click_clients()

@when("I click on Account List on new nav bar")
def click_on_account_list(page: Page, clients_page: ClientsPage):
    """Click on Account List menu item"""
    logger.info("Clicking Account List")
    clients_page.click_account_list_new_nav()
    screenshot = page.screenshot()
    allure.attach(screenshot, name="Account Wizard Page", attachment_type=allure.attachment_type.PNG)

@when("User switch to new iframe for account list page")
def switch_to_new_iframe_for_account_list_page(page: Page, test_context, request):
    """
    Switch to iframe context for account list page.
    This step ONLY affects the manage_bene scenario.
    Creates new AccountListPage instance with iframe context.
    """
    with allure.step("Switch to iframe context for account list page"):
        logger.info("Switching to new iframe for account list page")
        
        # Get iframe context from wrapper page
        wrapper_page = NewNavWrapperPage(page)
        iframe_context = wrapper_page.get_iframe_context()
        
        # Create new AccountListPage with iframe context and store in test_context
        test_context['account_list_page_iframe'] = AccountListPage(iframe_context)
        logger.info("Account list page initialized with iframe context")
        
        # Store reference for subsequent steps to use
        request.node._account_list_page_override = test_context['account_list_page_iframe']


@when("User should click on searched account and navigate to manage account page")
def click_searched_account_and_navigate_to_manage_account(
    page: Page,
    account_list_page: AccountListPage,
    account_detail_page: AccountDetailPage,
    new_nav_wrapper_page: NewNavWrapperPage,
    test_context,
):
    """Click on searched account and navigate to manage account page"""
    with allure.step("Click on searched account and navigate to manage account page"):
        # Check if iframe context override exists (for manage_bene scenario)
        iframe_context = None
        if 'account_list_page_iframe' in test_context:
            account_list_page = test_context['account_list_page_iframe']
            logger.info("Using iframe context for account selection")
            # Get iframe context - after selection, detail page is also in iframe
            iframe_context = new_nav_wrapper_page.get_iframe_context()
        
        logger.info(f"Current URL: {page.url}")
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Account List Before Selection",
            attachment_type=allure.attachment_type.PNG,
        )
        account_list_page.select_account(
            test_context["test_data"]["account_name"], test_context["test_data"]["client_id"]
        )
        
        # Wait for navigation/content load
        page.wait_for_timeout(3000)
        
        logger.info(f"After account selection. Current URL: {page.url}")
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="After Account Selection", attachment_type=allure.attachment_type.PNG
        )
        
        # Account detail page is NOT in iframe - use regular page context
        account_detail_page.click_manage_account()
        
        page.wait_for_timeout(2000)
        logger.info(f"Clicked Manage Account button. Current URL: {page.url}")        
        
        # After clicking Manage Account, page redirects and may have a new iframe
        # Get the NEW iframe context for the Manage Beneficiaries page
        if iframe_context:
            iframe_context = new_nav_wrapper_page.get_iframe_context()
            test_context['account_detail_page_iframe'] = iframe_context
            logger.info("Got NEW iframe context after redirect to manage account page - stored in test_context")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot, name="Manage Account Page", attachment_type=allure.attachment_type.PNG
        )
