"""
DM Tool Address Change Step Definitions
"""

import allure
import random
from playwright.sync_api import Page
from pytest_bdd import when, then, parsers

from pages.stp.stp_updateAddress.dmtool_page import DMToolPage
from pages.stp.stp_updateAddress.dm_tool_address_edit_modal import DMToolAddressEditModal
from pages.stp.stp_updateAddress.dm_tool_usps_modal import DMToolUSPSModal
from pages.stp.stp_updateAddress.dmt_address_change_confirmation_page import DMTAddressChangeConfirmationPage
from pages.stp.shared.account_wizard_page import AccountWizardPage
from utils.address_comparison import if_two_arrays_same
from utils.logger import setup_logger

logger = setup_logger(__name__)


@then("User should navigate To Address Change Edit Modal and click on Checkbox")
def navigate_to_edit_modal_and_click_checkbox(page: Page, dm_tool_page: DMToolPage, test_context: dict):
    """Navigate to Address Change Edit Modal and click on Checkbox"""
    logger.info("User should navigate To Address Change Edit Modal and click on Checkbox")
    
    with allure.step("Navigate to Address Change Edit Modal and click on Checkbox"):
       
        display_only_mailing_address = test_context.get('display_only_mailing_address', False)
        
        modal = dm_tool_page.navigate_to_address_change_edit_modal("dmToolPage", "Moving to address change modal")
      
        modal.perform_field_error_tests(display_only_mailing_address)
        
        modal.perform_po_test()
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Address Change Edit Modal - Checkbox Clicked", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Navigated to Address Change Edit Modal and clicked on Checkbox")


@then("User should fill all required data and click Save")
def fill_required_data_and_click_save(page: Page, 
                                       dm_tool_address_edit_modal: DMToolAddressEditModal,
                                       test_context: dict):
    """Fill all required address data and save"""
    with allure.step("Fill all required data and click Save"):
        logger.info("Step: Fill all required data and click Save")
        
        random_number = random.randint(1, 9999)
        
        dm_tool_address_edit_modal.populate_all_address_change_inputs(
            street=f"{random_number} Memorial Dr ",
            street_optional="",
            city="Avon",
            state="MA",
            zip_code="02322",
            extension="1919"
        )
        
        dm_tool_usps_modal = dm_tool_address_edit_modal.navigate_to_usps_modal()
        
        dm_tool_usps_modal.click_save()
        
        logger.info("Address data filled and saved")


@then(parsers.parse('User should fill PROD approved address "{street}" "{city}" "{state}" "{zip_code}" and click Save'))
def fill_prod_approved_address_and_click_save(page: Page,
                                               dm_tool_address_edit_modal: DMToolAddressEditModal,
                                               test_context: dict,
                                               street: str,
                                               city: str,
                                               state: str,
                                               zip_code: str):
    """Fill a PROD-approved address and save"""
    PROD_APPROVED_ADDRESSES = [
        {"street": "3200 N Central Ave 7th Floor", "city": "Phoenix",  "state": "AZ", "zip_code": "85012"},
        {"street": "1655 Grant St 10th floor",     "city": "Concord",  "state": "CA", "zip_code": "94520"},
    ]
    with allure.step(f"Fill PROD approved address: {street}, {city}, {state} {zip_code} and click Save"):
        logger.info(f"Step: Fill PROD approved address - {street}, {city}, {state} {zip_code}")

        # Guard: only allow pre-approved addresses on PROD
        requested = {"street": street.strip(), "city": city.strip(), "state": state.strip(), "zip_code": zip_code.strip()}
        if requested not in PROD_APPROVED_ADDRESSES:
            raise ValueError(
                f"Address not in PROD approved list: {requested}. "
                f"Allowed addresses: {PROD_APPROVED_ADDRESSES}"
            )

        dm_tool_address_edit_modal.populate_all_address_change_inputs(
            street=street,
            street_optional="",
            city=city,
            state=state,
            zip_code=zip_code,
            extension=""
        )

        dm_tool_usps_modal = dm_tool_address_edit_modal.navigate_to_usps_modal()
        dm_tool_usps_modal.click_save()

        # Store entered address in context so PROD confirmation step can use it
        test_context['prod_entered_address'] = {
            "street": street, "city": city, "state": state, "zip_code": zip_code
        }

        logger.info(f"PROD approved address filled and saved: {street}, {city}, {state} {zip_code}")


@then(parsers.parse('User should verify the changes in Address For {test} and click submit'))
def verify_address_changes_and_submit(page: Page, dm_tool_page: DMToolPage, test_context: dict, test: str):
    """Verify address changes and submit the request"""
    with allure.step(f"Verify the changes in Address For {test} and click submit"):
        logger.info(f"Step: Verify the changes in Address For {test} and click submit")
        
        mailing_after = dm_tool_page.return_address("mailing")
        legal_after = dm_tool_page.return_address("legal")
        
        if test.lower() == "checkbox" or test.lower() == "mailing":
            mailing_before = test_context.get('mailing_address_before', [])
            
            addresses_same = if_two_arrays_same(mailing_before, mailing_after)
            
            assert not addresses_same, "Mailing address did not change"
            logger.info("Mailing - Before and After Address values are not same: Verification Passed")
        
        if test.lower() == "checkbox" or test.lower() == "legal":
            legal_before = test_context.get('legal_address_before', [])
            
            addresses_same = if_two_arrays_same(legal_before, legal_after)
            
            assert not addresses_same, "Legal address did not change"
            logger.info("Legal - Before and After Address values are not same: Verification Passed")
        
        dm_tool_page.click_submit()

        logger.info("Address changes verified and submitted")


@when(parsers.parse('User visits PROD confirmation page to verify Address details for {test}'))
def verify_confirmation_page_address_details_prod(page: Page,
                                                   dm_tool_page: DMToolPage,
                                                   dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage,
                                                   test_context: dict,
                                                   test: str):
    """PROD-specific: Verify confirmation page using address stored from the fill step"""
    with allure.step(f"PROD: Verify Address details on confirmation page for {test}"):
        logger.info(f"Step: PROD confirmation page verification for {test}")

        household = dm_tool_page.get_household_id()
        advisor = dm_tool_page.get_advisor_id()
        display_only_mailing = test_context.get('display_only_mailing_address', False)

        dmt_address_change_confirmation_page.check_ui_elements_exist(display_only_mailing)
        logger.info("Confirmation screen: All UI elements exist - PASSED")

        # PROD: read household and advisor from the confirmation page UI (not URL parsing)
        prod_household = dmt_address_change_confirmation_page.get_household_id_prod()
        prod_advisor = dmt_address_change_confirmation_page.get_advisor_name_prod()

        mailing_before = test_context.get('mailing_address_before', [])
        legal_before = test_context.get('legal_address_before', [])

        # Use the address that was entered in the PROD fill step (not re-read from DM Tool page)
        entered = test_context.get('prod_entered_address', {})
        mailing_after = [entered.get('street', ''), entered.get('city', ''),
                         entered.get('state', ''), entered.get('zip_code', '')]
        legal_after = mailing_after

        result = dmt_address_change_confirmation_page.check_data_is_correct(
            mailing_before=mailing_before,
            legal_before=legal_before,
            mailing_after=mailing_after,
            legal_after=legal_after,
            household=prod_household,
            advisor=prod_advisor,
            display_only_mailing_address=display_only_mailing
        )
        assert result, "PROD confirmation page data verification FAILED"
        logger.info("PROD Address confirmation page: Verification Passed")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="PROD Address Confirmation Page", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User visits Update Addresses section to verify New Address details and click Cancel'))
def verify_new_address_and_cancel(page: Page, account_wizard_page, test_context: dict):

    with allure.step("User visits Update Addresses section to verify New Address details and click Cancel"):
        logger.info("Step: Verify New Address details and click Cancel")
        
        # Navigate from Account Wizard to DM Tool page by clicking DM link
        logger.info("Clicking DM link to navigate to Update Addresses section")
        account_wizard_page.click_dm_link()
        
        # Create new DMToolPage instance after navigation
        dm_tool_page = DMToolPage(page)
        
        # Wait for DM Tool page data to load
        dm_tool_page.wait_for_data_to_load()
        
        # Get address type from test context
        address_type = test_context.get('address_type', 'mailing')
        
        # Get current address from page
        current_address = dm_tool_page.return_address(address_type)
        logger.info(f"Current {address_type} address: {current_address}")
        
        # Store in test context for later verification
        test_context[f'current_{address_type}_address'] = current_address
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Update Addresses - Before Cancel",
            attachment_type=allure.attachment_type.PNG
        )
        
        # Click Cancel button to return to Account Wizard
        dm_tool_page.click_cancel_button()
        logger.info("Returned to Account Wizard page")
        
        logger.info("Address verified and Cancel clicked")


@then("User should verify Address Change confirmation page")
def verify_address_change_confirmation(page: Page, 
                                        dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage,
                                        test_context: dict):
    """Verify Address Change confirmation page"""
    with allure.step("Verify Address Change confirmation page"):
        logger.info("Step: Verify Address Change confirmation page")
        
        # Wait for confirmation page to load
        dmt_address_change_confirmation_page.wait_for_page_load()
        
        # Get display mode from test context
        display_only_mailing = test_context.get('display_only_mailing_address', False)
        
        # Check UI elements exist
        dmt_address_change_confirmation_page.check_ui_elements_exist(display_only_mailing)
        
        # Get item number
        item_number = dmt_address_change_confirmation_page.get_item_number()
        test_context['address_change_item_number'] = item_number
        logger.info(f"Address Change Item Number: {item_number}")
        
        allure.attach(
            item_number,
            name="Address Change Item Number",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Address Change Confirmation Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Address Change confirmation page verified")


@then("User should verify all Address Change data on confirmation page")
def verify_all_address_change_data(page: Page,
                                     dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage,
                                     test_context: dict):
    """Verify all address change data on confirmation page"""
    with allure.step("Verify all Address Change data on confirmation page"):
        logger.info("Step: Verify all Address Change data on confirmation page")
        
        # Get data from test context
        mailing_before = test_context.get('mailing_address_before', [])
        legal_before = test_context.get('legal_address_before', None)
        mailing_after = test_context.get('mailing_address_after', [])
        legal_after = test_context.get('legal_address_after', None)
        household_id = test_context.get('household_id', '')
        advisor_name = test_context.get('advisor_name', '')
        display_only_mailing = test_context.get('display_only_mailing_address', False)
        
        logger.info(f"Verifying data with household: {household_id}, advisor: {advisor_name}")
        
        # Verify all data
        dmt_address_change_confirmation_page.check_data_is_correct(
            mailing_before=mailing_before,
            legal_before=legal_before,
            mailing_after=mailing_after,
            legal_after=legal_after,
            household=household_id,
            advisor=advisor_name,
            display_only_mailing_address=display_only_mailing
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Address Change Data Verified",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("All Address Change data verified on confirmation page")


@when("User should click on Address Change item number")
def click_address_change_item_number(page: Page, dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage):
    """Click on Address Change item number"""
    with allure.step("Click on Address Change item number"):
        logger.info("Step: Click on Address Change item number")
        
        # Click item number
        dmt_address_change_confirmation_page.click_item_number()
        
        # Wait for navigation to item details page
        page.wait_for_timeout(3000)
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Clicking Item Number",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Address Change item number clicked")


@when("User should close Address Change confirmation page")
def close_address_change_confirmation(page: Page, dmt_address_change_confirmation_page: DMTAddressChangeConfirmationPage):
    """Close Address Change confirmation page"""
    with allure.step("Close Address Change confirmation page"):
        logger.info("Step: Close Address Change confirmation page")
        
        # Click Close button
        dmt_address_change_confirmation_page.click_close()
        
        # Wait for navigation
        page.wait_for_timeout(2000)
        
        logger.info("Address Change confirmation page closed")
