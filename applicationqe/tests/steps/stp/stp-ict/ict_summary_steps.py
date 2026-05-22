import allure
from playwright.sync_api import Page
from pytest_bdd import when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I click Next on ICT Summary')
def click_next_on_ict_summary(page: Page, ict_summary_page):
    """Click Next on the ICT Summary page"""
    with allure.step('Click Next on ICT Summary'):
        logger.info('Clicking Next on ICT Summary page')
        ict_summary_page.click_next()
        screenshot = page.screenshot()
        allure.attach(screenshot, name='ICT Summary - Next Clicked', attachment_type=allure.attachment_type.PNG)
        allure.attach(screenshot, name='ICT Summary - Next Clicked', attachment_type=allure.attachment_type.PNG)
