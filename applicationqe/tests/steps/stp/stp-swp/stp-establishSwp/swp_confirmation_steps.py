import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from swp_establish_confirmation_page import SWPEstablishConfirmationPage
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_confirmation_page(page: Page, test_context: dict) -> SWPEstablishConfirmationPage:
    swp_confirmation_page = test_context.get('swp_establish_confirmation_page')
    if swp_confirmation_page is None:
        swp_confirmation_page = SWPEstablishConfirmationPage(page)
        test_context['swp_establish_confirmation_page'] = swp_confirmation_page
    return swp_confirmation_page


@then(parsers.parse('User should validate the Header Section of "{sub_heading}".'))
def validate_header_section_swp_establish(
    page: Page,
    test_context: dict,
    sub_heading: str
):
    with allure.step(f"Validate Header Section of {sub_heading}"):
        logger.info(f"Validating Header Section of: {sub_heading}")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        test_data = test_context.get('test_data', {})
        advisor_id = test_data.get('advisor_id', '')
        swp_confirmation_page.validate_header_section(advisor_id)
        allure.attach(
            page.screenshot(),
            name=f"Header Section Validated - {sub_heading}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should get Item Number from Confirmation Page for SWP Establish'))
def get_item_number_swp_establish(
    page: Page,
    test_context: dict
):
    with allure.step("Get Item Number from Confirmation Page for SWP Establish"):
        logger.info("Getting Item Number from Confirmation Page")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        item_number = swp_confirmation_page.get_item_number()
        test_context['item_number'] = item_number
        test_context['swp_establish_item_number'] = item_number
        logger.info(f"The Item number is --> {item_number}")
        allure.attach(
            page.screenshot(),
            name=f"Item Number Retrieved - {item_number}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate "{section_name}" contents where "{status_header}" as "{status_value}", "{date_header}" , "{submitted_by_header}" and "{item_number_header}" for SWP Establish'))
def validate_transaction_summary_details_swp_establish(
    page: Page,
    test_context: dict,
    section_name: str,
    status_header: str,
    status_value: str,
    date_header: str,
    submitted_by_header: str,
    item_number_header: str
):
    with allure.step(f"Validate {section_name} contents"):
        logger.info(f"Validating {section_name} section contents")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        test_data = test_context.get('test_data', {})
        actual_status = swp_confirmation_page.validate_transaction_summary(
            section_name=section_name,
            status_header=status_header,
            status_value=status_value,
            date_header=date_header,
            submitted_by_header=submitted_by_header,
            item_number_header=item_number_header,
            login_user_role=test_context.get('login_user_role', ''),
            login_user_name=test_context.get('login_user_name', ''),
            admin_name=test_data.get('admin_name', ''),
        )
        test_context['online_swp_establish_request_status'] = actual_status
        allure.attach(
            page.screenshot(),
            name=f"{section_name} Section Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should verify confirmation screen success message as "{status_message}" for SWP Establish.'))
def verify_confirmation_screen_success_message_swp_establish(
    page: Page,
    test_context: dict,
    status_message: str
):
    with allure.step(f"Verify confirmation screen success message: {status_message}"):
        logger.info(f"Verifying confirmation screen success message: {status_message}")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        swp_confirmation_page.verify_success_message(status_message)
        allure.attach(
            page.screenshot(),
            name=f"Confirmation Status Validated - {status_message}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should click on item number for SWP Establish'))
def click_item_number_swp_establish(
    page: Page,
    test_context: dict
):
    with allure.step("Click on item number for SWP Establish"):
        logger.info("Clicking on item number link")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        test_context['parent_window'] = page
        new_page = swp_confirmation_page.click_item_number_link()
        test_context['item_details_page_tab'] = new_page
        logger.info("Item number link clicked and switched to new tab")
        allure.attach(
            new_page.screenshot(),
            name="Item Number Link Clicked",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should validate all header details and their values for "{request_type}" and method as "{method}" on the SWP Establish Confirmation Page'))
def validate_all_header_details_swp_establish(
    page: Page,
    test_context: dict,
    request_type: str,
    method: str
):
    with allure.step(f"Validate all header details: {request_type}, {method}"):
        logger.info(f"Validating all header details for request type: {request_type}, method: {method}")
        swp_confirmation_page = get_confirmation_page(page, test_context)
        additional_details = test_context.get('all_request_details_for_confirmation', [])
        swp_confirmation_page.validate_all_header_details(request_type, method, additional_details)
        allure.attach(
            page.screenshot(),
            name="Header Details Validated",
            attachment_type=allure.attachment_type.PNG
        )
