"""Account Setup Step Definitions for BDD tests"""

import logging
from playwright.sync_api import Page
from pytest_bdd import when, then
from utils.allure_logger import get_allure_logger
from utils.excel_utils import ExcelUtils
logger = get_allure_logger(__name__)

@when("cancel already created journal")
def cancel_added_journal(home_page: HomePage, test_context):
    home_page.clickCancelLink()
