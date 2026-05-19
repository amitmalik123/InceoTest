from playwright.sync_api import Page
from pytest_bdd import when

# Reuse all existing common steps for temporary scenarios.
from tests.steps.common_steps import *  # noqa: F401,F403
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("Login application")
def login_application(page: Page, navbar_login_page, test_context):
    """Temporary navbar login using same test data sheet credentials."""
    with logger.step("Login application", page=page):
        test_data = test_context.get("test_data", {})
        username = test_data.get("username") or test_data.get("UserName")
        password = test_data.get("password") or test_data.get("Password")

        if not username or not password:
            raise ValueError(
                "Missing credentials in test data. Expected 'username'/'password' "
                "or 'UserName'/'Password' columns."
            )

        navbar_login_page.login_application(username, password)
