import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I click on Select Destination Investments dropdown')
def click_select_destination_investments_dropdown(page: Page, select_destination_page):
    """Click Select Destination Investments dropdown"""
    with allure.step('Click Select Destination Investments dropdown'):
        logger.info('Clicking Select Destination Investments dropdown')
        select_destination_page.click_select_destination_investments_dropdown()
        allure.attach(page.screenshot(), name="Destination Dropdown Opened", attachment_type=allure.attachment_type.PNG)


@when('I select New Investment')
def select_new_investment(page: Page, select_destination_page):
    """Select New Investment option"""
    with allure.step('Select New Investment'):
        logger.info('Selecting New Investment')
        select_destination_page.select_new_investment()
        allure.attach(page.screenshot(), name="New Investment Selected", attachment_type=allure.attachment_type.PNG)


@when('I select Single Strategy Account under Open Design')
def select_single_strategy_account_under_open_design(page: Page, select_destination_page):
    """Select Single Strategy Account under Open Design"""
    with allure.step('Select Single Strategy Account under Open Design'):
        logger.info('Selecting Single Strategy Account under Open Design')
        select_destination_page.select_single_strategy_account_under_open_design()
        allure.attach(page.screenshot(), name="Single Strategy Account Selected", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('I choose "{model_name}" in Choose a New Investment'))
def choose_new_investment_model(page: Page, select_destination_page, model_name: str):
    """Choose model from Choose a New Investment dropdown"""
    with allure.step(f'Choose model in Choose a New Investment: {model_name}'):
        logger.info(f'Choosing model in Choose a New Investment: {model_name}')
        select_destination_page.choose_new_investment_model(model_name)
        allure.attach(page.screenshot(), name="Model Selected", attachment_type=allure.attachment_type.PNG)


@when('I click OK on Select Destination')
def click_ok_on_select_destination(page: Page, select_destination_page):
    """Click OK on Select Destination screen"""
    with allure.step('Click OK on Select Destination'):
        logger.info('Clicking OK on Select Destination')
        select_destination_page.click_ok()
        allure.attach(page.screenshot(), name="OK Clicked", attachment_type=allure.attachment_type.PNG)


@when('I select 100% radio button')
def select_one_hundred_percent_radio_button(page: Page, select_destination_page):
    """Select 100% radio button"""
    with allure.step('Select 100% radio button'):
        logger.info('Selecting 100% radio button')
        select_destination_page.select_one_hundred_percent()
        allure.attach(page.screenshot(), name="100 Percent Selected", attachment_type=allure.attachment_type.PNG)


@when('I click Next on Select Destination')
def click_next_on_select_destination(page: Page, select_destination_page):
    """Click Next on Select Destination screen"""
    with allure.step('Click Next on Select Destination'):
        logger.info('Clicking Next on Select Destination')
        select_destination_page.click_next()
        allure.attach(page.screenshot(), name="Select Destination Next Clicked", attachment_type=allure.attachment_type.PNG)
