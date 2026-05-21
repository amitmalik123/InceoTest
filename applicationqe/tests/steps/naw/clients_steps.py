from playwright.sync_api import Page
from pytest_bdd import when

# Reuse all existing common steps for client scenarios.
from tests.steps.common_steps import *  # noqa: F401,F403
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("User clicks on the add a client button")
def click_add_client_button(page: Page, clients_page):
    """Click the add a client button on test01 clients page."""
    with logger.step("Click add a client button", page=page):
        clients_page.click_add_client()
