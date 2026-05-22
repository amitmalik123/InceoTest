import allure
from playwright.sync_api import Page
from pytest_bdd import then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@then('I should see all required ICT forms')
def verify_required_ict_forms_present(page: Page, create_forms_page):
    with allure.step('Verify required ICT forms are present'):
        logger.info('Verifying required forms on Create Forms page')
        create_forms_page.verify_required_forms_present()
        allure.attach(page.screenshot(), name='Create Forms - Forms Verified', attachment_type=allure.attachment_type.PNG)


@when('I click Complete and Submit on Create Forms')
def click_complete_and_submit(page: Page, create_forms_page):
    with allure.step('Click Complete and Submit'):
        logger.info('Clicking Complete and Submit on Create Forms page')
        create_forms_page.click_complete_and_submit()
        allure.attach(page.screenshot(), name='Create Forms - Complete and Submit Clicked', attachment_type=allure.attachment_type.PNG)


@when('I select Proceed without client signature')
def select_proceed_without_signature(page: Page, create_forms_page):
    with allure.step('Select Proceed without client signature and continue to DocuSign'):
        logger.info('Selecting proceed without client signature radio')
        create_forms_page.select_proceed_without_signature()
        logger.info('Clicking Continue to proceed to DocuSign')
        create_forms_page.click_continue_on_popup()
        allure.attach(page.screenshot(), name='Create Forms - Proceed Without Signature',
                      attachment_type=allure.attachment_type.PNG)


@when('I click Continue on signature window')
def click_continue_on_signature_window(page: Page, create_forms_page):
    with allure.step('Click Continue on signature window'):
        logger.info('Clicking Continue on signature window')
        create_forms_page.click_continue_on_popup()
        page.wait_for_timeout(2000)
        allure.attach(page.screenshot(), name='Create Forms - Continue Clicked', attachment_type=allure.attachment_type.PNG)
