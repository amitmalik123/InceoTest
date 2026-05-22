import allure
from playwright.sync_api import Page
from pytest_bdd import when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I enter fee on Create Fees page')
def enter_fee_on_create_fees_page(page: Page, create_fees_page, test_context):
    """Enter fee (flat or tiered) from test data on the Create Fees page."""
    with allure.step('Enter fee on Create Fees page'):
        fee_type  = test_context['test_data']['fee_type']
        fee_value = test_context['test_data']['fee_value']
        logger.info(f'Fee type: {fee_type}, value: {fee_value}')
        create_fees_page.enter_fee(fee_type, fee_value)
        screenshot = page.screenshot()
        allure.attach(screenshot, name='Create Fees - Fee Entered', attachment_type=allure.attachment_type.PNG)


#@when('I click Next on Create Fees')
#def click_next_on_create_fees(page: Page, create_fees_page):
  #  """Click Next on the Create Fees page"""
   # with allure.step('Click Next on Create Fees'):
   #     logger.info('Clicking Next on Create Fees page')
    #    create_fees_page.click_next()
    #    page.wait_for_timeout(500)
   #     screenshot = page.screenshot()
   #     allure.attach(screenshot, name='Create Fees - Next Clicked', attachment_type=allure.attachment_type.PNG)


@when('I click Next on Create Fees')
def click_next_on_create_fees(page: Page, create_fees_page):
    """Click Next on the Create Fees page"""
    with allure.step('Click Next on Create Fees'):
        logger.info('Clicking Next on Create Fees page')
        create_fees_page.click_next()
        screenshot = page.screenshot()
        allure.attach(screenshot, name='Create Fees - Next Clicked', attachment_type=allure.attachment_type.PNG)
