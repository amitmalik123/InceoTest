from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OAToolTransactionPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
