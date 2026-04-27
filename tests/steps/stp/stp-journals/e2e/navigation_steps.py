import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I navigate to Clients menu')
def navigate_to_clients_menu(clients_page):
    """Navigate to clients menu"""
    with allure.step("Navigate to Clients menu"):
        logger.info("Navigating to clients menu")
        clients_page.navigate()
        clients_page.click_clients()


@when('I click on Account List')
def click_on_account_list(clients_page):
    """Click on Account List menu item"""
    with allure.step("Click on Account List"):
        logger.info("Clicking Account List")
        clients_page.click_account_list()


@then('I should see the Account List page')
def verify_account_list_page_loaded(page: Page):
    """Verify Account List page is loaded"""
    with allure.step("Verify Account List page is loaded"):
        page.wait_for_load_state('load', timeout=30000)
        page.wait_for_load_state('networkidle', timeout=30000)
        logger.info(f"Account list page loaded. Current URL: {page.url}")
        page.wait_for_timeout(3000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Account List Page", attachment_type=allure.attachment_type.PNG)

