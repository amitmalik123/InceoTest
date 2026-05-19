"""BAW Step Definitions for BDD tests"""

from pytest_bdd import given

from applicationqe.pages.baw.baw_login_page import BawLoginPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@given('User should login to BAW application and click on the dashboard')
def step_login_to_baw_and_navigate_dashboard(test_context, baw_login_page: BawLoginPage):
    """
    Login to BAW application by navigating to the BAW URL and signing in
    using BAW credentials from the test data sheet.

    Args:
        test_context: Test context containing test_data dict (loaded from Excel)
        baw_login_page: BAW login page object fixture
    """
    with logger.step("Login to BAW application", page=baw_login_page.page):
        logger.info("Starting BAW login")

        test_data = test_context.get("test_data", {})
        baw_username = (test_data.get("BawUserName") or "").strip()
        baw_password = (test_data.get("BawUserPassword") or "").strip()

        if not baw_username or not baw_password:
            error_msg = (
                "BAW credentials (BawUserName/BawUserPassword) not found in test data"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("BAW Username found in test data")

        # Navigate to BAW (direct navigation)
        baw_page = baw_login_page.navigate_to_baw()

        # Perform login
        baw_login_page.login(
            username=baw_username,
            password=baw_password,
            baw_page=baw_page,
        )

        logger.info("BAW login completed successfully")
