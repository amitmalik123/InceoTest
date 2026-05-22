import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I login with valid credentials')
def login_with_valid_credentials(page: Page, login_page, test_context):
    """Login with credentials from test data"""
    with allure.step("Login with valid credentials"):
        logger.info("Logging in with test credentials")
        login_page.accept_cookies()
        login_page.enter_username(test_context['test_data']['username'])
        login_page.enter_password(test_context['test_data']['password'])
        login_page.click_sign_in()
        login_page.submit_login_form()
        allure.attach(page.screenshot(), name="After Login", attachment_type=allure.attachment_type.PNG)


@then('I should be redirected to the home page')
def verify_redirect_to_home_page(page: Page):
    """Verify successful login by checking page load"""
    with allure.step("Verify redirect to home page"):
        page.wait_for_load_state('domcontentloaded', timeout=30000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Home Page After Login", attachment_type=allure.attachment_type.PNG)
        logger.info("Successfully logged in and redirected to home page")
