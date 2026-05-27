import allure
from playwright.sync_api import Page
from pytest_bdd import when

from utils.logger import setup_logger

logger = setup_logger(__name__)


@when('I answer Client Suitability questions')
def answer_client_suitability_questions(page: Page, client_suitability_page, test_context):
    """Answer all 3 suitability questions using values from test data."""
    with allure.step('Answer Client Suitability questions'):
        data = test_context['test_data']
        q1 = int(data['Suitability_q1_answer'])
        q2 = int(data['Suitability_q2_answer'])
        q3 = int(data['Suitability_q3_answer'])
        logger.info(f'Answering suitability questions: Q1={q1}, Q2={q2}, Q3={q3}')
        client_suitability_page.select_answers(q1, q2, q3)
        screenshot = page.screenshot()
        allure.attach(screenshot, name='Client Suitability - Answered', attachment_type=allure.attachment_type.PNG)


@when('I click Next on Client Suitability')
def click_next_on_client_suitability(page: Page, client_suitability_page):
    """Click Next on the Client Suitability page"""
    with allure.step('Click Next on Client Suitability page'):
        logger.info('Clicking Next on Client Suitability page')
        client_suitability_page.click_next()
        allure.attach(page.screenshot(), name="Client Suitability Next Clicked", attachment_type=allure.attachment_type.PNG)