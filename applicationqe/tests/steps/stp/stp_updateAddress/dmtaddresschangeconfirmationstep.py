"""
DMT Address Change Confirmation Step Definitions
"""

import allure
from playwright.sync_api import Page
from pytest_bdd import when, parsers

from pages.stp.stp_updateAddress.dmtool_page import DMToolPage
from pages.stp.stp_updateAddress.dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage
from utils.logger import setup_logger

logger = setup_logger(__name__)


@when(parsers.parse('User visits confirmation page to verify Address details for {test}'))
def verify_confirmation_page_address_details(page: Page, 
                                              dm_tool_page: DMToolPage,
                                              dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage,
                                              test_context: dict, 
                                              test: str):
    """Verify Address details on confirmation page"""
    with allure.step(f"User visits confirmation page to verify Address details for {test}"):
        logger.info(f"Step: Verify Address details on confirmation page for {test}")
        
        household = dm_tool_page.get_household_id()
        advisor = dm_tool_page.get_advisor_id()
        
        display_only_mailing = test_context.get('display_only_mailing_address', False)
        
        dmt_address_change_confirmation_page.check_ui_elements_exist(display_only_mailing)
        logger.info("Confirmation screen: All UI elements exist verification PASSED")
        
        mailing_before = test_context.get('mailing_address_before', [])
        legal_before = test_context.get('legal_address_before', [])
        
        mailing_after = dm_tool_page.return_address("mailing")
        legal_after = dm_tool_page.return_address("legal")
        
        if test.lower() == "checkbox":
            result = dmt_address_change_confirmation_page.check_data_is_correct(
                mailing_before=mailing_before,
                legal_before=legal_before,
                mailing_after=mailing_after,
                legal_after=legal_after,
                household=household,
                advisor=advisor,
                display_only_mailing_address=display_only_mailing
            )
            assert result, "All displayed data is correct verification FAILED"
            logger.info("Mailing Address comparison: Verification Passed")
            logger.info("Legal Address comparison: Verification Passed")
            logger.info("Household value comparison: Verification Passed")
            logger.info("Advisor value comparison: Verification Passed")
            
        elif test.lower() == "mailing":
            result = dmt_address_change_confirmation_page.check_data_is_correct(
                mailing_before=mailing_before,
                legal_before=legal_before,
                mailing_after=mailing_after,
                legal_after=["No changes"],
                household=household,
                advisor=advisor,
                display_only_mailing_address=display_only_mailing
            )
            assert result, "All displayed data is correct verification FAILED"
            
        elif test.lower() == "legal":
            result = dmt_address_change_confirmation_page.check_data_is_correct(
                mailing_before=mailing_before,
                legal_before=legal_before,
                mailing_after=["No changes"],
                legal_after=legal_after,
                household=household,
                advisor=advisor,
                display_only_mailing_address=display_only_mailing
            )
            assert result, "All displayed data is correct verification FAILED"
        
        logger.info("Confirmation screen: All displayed data is correct verification PASSED")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Confirmation Page - {test}",
            attachment_type=allure.attachment_type.PNG
        )


@when("User retrieves ItemNumber and clicks on Close Btn")
def retrieve_item_number_and_close(page: Page,
                                    dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage,
                                    test_context: dict):
    """Retrieve ItemNumber and click Close button"""
    with allure.step("User retrieves ItemNumber and clicks on Close Btn"):
        logger.info("Step: Retrieve ItemNumber and click Close")
        
        item_number = dmt_address_change_confirmation_page.get_item_number()
        test_context['item_number'] = item_number
        logger.info(f"The item number from UI: {item_number}")
        
        dmt_address_change_confirmation_page.click_close()
        
        logger.info("Item number retrieved and Close button clicked")
