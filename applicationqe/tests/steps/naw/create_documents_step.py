"""Create Documents Step Definitions for BDD tests"""

import logging
from pytest_bdd import then

from pages.ewm.create_documents_page import CreateDocumentsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("User click on create documents button")
def step_click_on_create_documents_button(
    test_context: dict, create_documents_page: CreateDocumentsPage
):
    """Click on create documents button and navigate to view documents page"""
    with logger.step("Click create documents button", page=create_documents_page.page):
        create_documents_page.create_documents_confirmation()
        logger.info("Successfully navigated to View Documents page")
