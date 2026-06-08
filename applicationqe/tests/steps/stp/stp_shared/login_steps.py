from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I login with valid credentials")
def login_with_valid_credentials(page: Page, login_page, test_context):
    """
    Verification step - Does NOT perform login (handled by page fixture in conftest.py)

    This step ONLY verifies that authentication is already complete.
    The page fixture in conftest.py handles actual login via session storage.

    If this step finds user is NOT logged in, it will FAIL the test
    rather than performing login as a fallback.
    """
    current_url = page.url
    logger.info(f"Verifying login status - Current URL: {current_url}")

    # Verify already logged in (session storage should handle this)
    if current_url and "login" not in current_url.lower():
        logger.info("[OK] User is already authenticated (Session Storage)")
        return

    # If we reach here, authentication failed - FAIL THE TEST
    error_msg = "AUTHENTICATION FAILED: User is not logged in. Session storage did not work!"
    logger.error(error_msg)
    raise AssertionError(error_msg)


@then("I should be redirected to the home page")
def verify_redirect_to_home_page(page: Page):
    """Verify successful login by checking page load"""
    logger.info("Verifying redirect to home page")
    page.wait_for_load_state("domcontentloaded", timeout=30000)

@when("User should click on user profile and sign out")
def user_click_profile_and_signout(page: Page, login_page):
    """
    Step: Click on user profile button and then sign out
    """
    logger.info("User clicking on profile and signing out")
    
    # Wait for page to be fully loaded first
    page.wait_for_load_state("networkidle", timeout=10000)
    page.wait_for_timeout(1000)  # Small additional wait for UI to render
    
    # Click user profile button with longer timeout
    try:
        login_page.user_profile.wait_for(state="visible", timeout=10000)
        login_page.user_profile.click()
        logger.info("[OK] User profile button clicked")
    except Exception as e:
        logger.error(f"Failed to click user profile button: {str(e)}")
        raise
    
    # Wait for dropdown menu to appear
    page.wait_for_timeout(1000)
    
    # Click sign out button
    try:
        login_page.signout.wait_for(state="visible", timeout=10000)
        login_page.signout.click()
        logger.info("[OK] Sign Out button clicked")
    except Exception as e:
        logger.error(f"Failed to click sign out button: {str(e)}")
        raise
    
    page.wait_for_load_state("networkidle", timeout=10000)
    
    logger.info("[OK] User signed out successfully")

@when("User should click on logout link")
def user_click_logout(page: Page, login_page):
    """Step: Click on the Logout link to sign out"""
    logger.info("User clicking on logout link")
    
    try:
        login_page.click_logout()
        logger.info("[OK] User logged out successfully via logout link")
    except Exception as e:
        logger.error(f"Failed to click logout link: {str(e)}")
        raise
