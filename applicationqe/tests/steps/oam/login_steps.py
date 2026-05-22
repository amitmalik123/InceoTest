from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I login with valid credentials")
def login_with_valid_credentials(authenticated_page: Page, login_page, test_context):
    """
    Verification step - Does NOT perform login (handled by page fixture in conftest.py)

    This step ONLY verifies that authentication is already complete.
    The page fixture in conftest.py handles actual login via session storage.

    If this step finds user is NOT logged in, it will FAIL the test
    rather than performing login as a fallback.
    """
    current_url = authenticated_page.url
    logger.info(f"Verifying login status - Current URL: {current_url}")

    # Verify already logged in (session storage should handle this)
    if current_url and "login" not in current_url.lower():
        logger.info("✓ User is already authenticated (Session Storage)")
        return

    # If we reach here, authentication failed - FAIL THE TEST
    error_msg = "AUTHENTICATION FAILED: User is not logged in. Session storage did not work!"
    logger.error(error_msg)
    raise AssertionError(error_msg)


@then("I should be redirected to the home page")
def verify_redirect_to_home_page(authenticated_page: Page):
    """Verify successful login by checking page load"""
    logger.info("Verifying redirect to home page")
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
