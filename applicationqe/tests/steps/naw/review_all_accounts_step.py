"""Review All Accounts Step Definitions for BDD tests"""

import logging
from pytest_bdd import when, then

from pages.ewm.review_all_accounts_page import ReviewAllAccountsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@then("User navigates to review all accounts tab and click on proceed to create documents button")
def step_navigate_to_review_all_accounts_and_click_create_documents(
    test_context: dict, review_all_accounts_page: ReviewAllAccountsPage
):
    """Navigate to review all accounts tab and click on create documents button"""
    logger.info("Starting review all accounts step")
        
    test_data = test_context.get("test_data", {})
        
    # Verify the review accounts page with client information
    fname = test_data.get("AccountHolderFirstName", "")
    lname = test_data.get("AccountHolderLastName", "")
    bday = test_data.get("AccountHolderBirthDate", "")
        
    logger.info(f"Verifying account page for: {fname} {lname}")
    review_all_accounts_page.verify_review_account_page(fname, lname, bday)
        
    # Check if all approval points are completed
    logger.info("Checking if all required steps are approved")
    review_all_accounts_page.check_if_all_approved()
        
    # Confirm clients documents and navigate to create documents page
    logger.info("Confirming client documents")
    review_all_accounts_page.confirm_clients_documents()
        
    logger.info("Successfully navigated to create documents page")
