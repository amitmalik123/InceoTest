"""
Cancel Automatic Investment Plan (AIP) step definitions
"""

import allure
from playwright.sync_api import Page
from pytest_bdd import when, then

from pages.stp.stp_aip.stp_cancelAip.cancel_aip_page import CancelAIPPage
from utils.logger import setup_logger

logger = setup_logger(__name__)


@when("User clicks on next button and jumps to Cancel AIP Landing Page")
def click_next_and_jump_to_cancel_aip_landing_page(page: Page, account_wizard_page, cancel_aip_page: CancelAIPPage):
    """Click next button on account wizard and navigate to Cancel AIP Landing Page"""
    with allure.step("Click next button and jump to Cancel AIP Landing Page"):
        logger.info("Clicking Next button to navigate to Cancel AIP Landing Page")
        
        account_wizard_page.next_button.wait_for(state='visible', timeout=10000)
        account_wizard_page.next_button.click()
        cancel_aip_page.wait_for_page_load()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Cancel AIP Landing Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Navigated to Cancel AIP Landing Page")


@then("User refreshes the page to view the API created")
def refresh_page_to_view_api_created(page: Page, cancel_aip_page: CancelAIPPage):
    """Refresh the landing page to view API created AIP"""
    with allure.step("Refresh page to view API created AIP"):
        logger.info("Refreshing page")
        cancel_aip_page.refresh_landing_page()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Refreshed Landing Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Page refreshed")


@when("User should be able to select Future End Date in calendar field")
@then("User should be able to select Future End Date in calendar field")
def select_future_end_date_in_calendar(page: Page, cancel_aip_page: CancelAIPPage):
    """Select Future End Date radio and pick a valid date from the calendar"""
    with allure.step("Select Future End Date in calendar field"):
        logger.info("Selecting Future End Date in calendar field")
        cancel_aip_page.select_future_end_date()
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Future End Date Selected",
            attachment_type=allure.attachment_type.PNG,
        )
        logger.info("Future End Date selected")


@then("User should validate AIP is displayed and click on AIP details on Landing Page")
def validate_and_click_aip_details(page: Page, cancel_aip_page: CancelAIPPage):
    """Validate AIP is displayed and click on AIP details"""
    with allure.step("Validate AIP is displayed and click on AIP details"):
        logger.info("Validating AIP is displayed")
        
        page.wait_for_timeout(3000)
        is_displayed = cancel_aip_page.validate_aip_displayed()
        assert is_displayed, "AIP is not displayed on Landing Page"
        
        logger.info("AIP is displayed, clicking on AIP details")
        aip_details = cancel_aip_page.click_on_aip_to_be_deleted()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="AIP Selected",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info(f"Clicked on AIP details: {aip_details}")


@then("User selects the first AIP and clicks the Delete Button")
def select_aip_and_click_delete(page: Page, cancel_aip_page: CancelAIPPage):
    """Select first AIP and click Delete button"""
    with allure.step("Select first AIP and click Delete button"):
        logger.info("Clicking Delete button")
        
        page.wait_for_timeout(1000)
        cancel_aip_page.click_delete_button()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Delete Button Clicked",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Delete button clicked")


@then("User is able to Navigate to the Selection Layout Page")
def navigate_to_selection_layout_page(page: Page, cancel_aip_page: CancelAIPPage):
    """Validate navigation to Selection Layout Page"""
    with allure.step("Navigate to Selection Layout Page"):
        logger.info("Validating Selection Layout Page")
        
        is_visible = cancel_aip_page.validate_aip_to_be_deleted()
        assert is_visible, "Selection Layout Page not displayed"
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Selection Layout Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Selection Layout Page validated")


@then("User is able to Validate End Date is displayed and selects the appropriate radio button for End Date selection")
def validate_and_select_end_date(page: Page, cancel_aip_page: CancelAIPPage):
    """Validate End Date is displayed and select radio button"""
    with allure.step("Validate and select End Date"):
        logger.info("Validating and selecting End Date")
        
        is_selected = cancel_aip_page.validate_end_date_radio_button()
        assert is_selected, "End Date radio button not selected"
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="End Date Selected",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("End Date radio button selected")


@then('User should enter "notobtain" as Signature Options for account on the Selection Page')
@when('User should enter "{signature_option}" as Signature Options for account on the Selection Page')
def select_signature_options(page: Page, cancel_aip_page: CancelAIPPage, signature_option: str = "notobtain"):
    """Select signature option on Selection Page"""
    with allure.step(f"Select signature option: {signature_option}"):
        logger.info(f"Selecting signature option: {signature_option}")
        
        cancel_aip_page.select_signature_option(signature_option)
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Signature Option Selected - {signature_option}",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info(f"Signature option '{signature_option}' selected")


@then("User should click on the Next Button on the Selection Page")
def click_next_button_on_selection_page(page: Page, cancel_aip_page: CancelAIPPage):
    """Click Next button on Selection Page"""
    with allure.step("Click Next button on Selection Page"):
        logger.info("Clicking Next button")
        
        page.wait_for_timeout(5000)
        cancel_aip_page.click_next_button()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Summary Page",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Next button clicked, navigated to Summary Page")


@then("User should click on the Submit Button on Cancel AIP Summary Page")
def click_submit_button_on_summary_page(page: Page, cancel_aip_page: CancelAIPPage):
    """Click Submit button on Cancel AIP Summary Page"""
    with allure.step("Click Submit button on Summary Page"):
        logger.info("Clicking Submit button")

        page.wait_for_timeout(2000)
        cancel_aip_page.click_summary_submit_button()

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Confirmation Page",
            attachment_type=allure.attachment_type.PNG
        )

        logger.info("Submit button clicked")


@then("User should click on the Submit For Review Button on Cancel AIP Summary Page")
def click_submit_for_review_button_on_summary_page(page: Page, cancel_aip_page: CancelAIPPage):
    """Click Submit For Review button on Cancel AIP Summary Page (Future End Date flow)"""
    with allure.step("Click Submit For Review button on Summary Page"):
        logger.info("Clicking Submit For Review button")

        page.wait_for_timeout(2000)
        cancel_aip_page.submit_review_button.wait_for(state='visible', timeout=20000)
        cancel_aip_page.submit_review_button.click()

        try:
            cancel_aip_page.spinner_loading.wait_for(state='hidden', timeout=30000)
            logger.info("Submit For Review processing complete")
        except Exception as e:
            logger.warning(f"Spinner wait after Submit For Review failed: {e}")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Confirmation Page - Submit For Review",
            attachment_type=allure.attachment_type.PNG
        )

        logger.info("Submit For Review button clicked")


@when("User should get Item Number from Confirmation Page for Cancel AIP")
@then("User should get Item Number from Confirmation Page for Cancel AIP")
def get_item_number_from_confirmation_page(page: Page, cancel_aip_page: CancelAIPPage, test_context: dict):
    """Get Item Number from Confirmation Page"""
    with allure.step("Get Item Number from Confirmation Page"):
        logger.info("Getting Item Number")
        
        page.wait_for_timeout(5000)
        item_number = cancel_aip_page.get_item_number()
        
        test_context['item_number'] = item_number
        
        allure.attach(
            f"Item Number: {item_number}",
            name="Item Number",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Item Number Retrieved",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info(f"Item Number: {item_number}")


@when("User should click on item number for Cancel AIP")
@then("User should click on item number for Cancel AIP")
def click_item_number_for_cancel_aip(page: Page, cancel_aip_page: CancelAIPPage):
    """Click on item number to open Item Details"""
    with allure.step("Click on item number"):
        logger.info("Clicking on item number")
        
        page.wait_for_timeout(2000)
        cancel_aip_page.click_item_number()
        
        pages = page.context.pages
        if len(pages) > 1:
            new_page = pages[-1]
            screenshot = new_page.screenshot()
            allure.attach(
                screenshot,
                name="Item Details Page",
                attachment_type=allure.attachment_type.PNG
            )
        
        logger.info("Item number clicked")
