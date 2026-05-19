from playwright.sync_api import Page
from pytest_bdd import when, then

# Reuse all existing common steps for dashboard scenarios.
from applicationqe.tests.steps.common_steps import *  # noqa: F401,F403
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("User clicks on the clients tab")
def click_clients_tab(page: Page, dashboard_page):
    """Click the Clients navigation tab on the dashboard."""
    dashboard_page.click_clients_tab()