from playwright.sync_api import Page
from pytest_bdd import then

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("User navigates to portfolio details page and click on Account setup button")
def user_navigates_to_portfolio_details_page_and_click_on_account_setup_button(
    page: Page, portfolio_details_page, test_context
):
    """
    Navigate to portfolio details page and click on Account setup button.
    """
    logger.info("Navigating to portfolio details page and clicking Account setup button")
    
    # Click on account setup button
    portfolio_details_page.go_to_account_setup(
        "Account Setup Button: ", 
        "click on account setup button"
    )
    
    logger.info("Successfully navigated to Account Setup page")
