from typing import Any

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ClientsPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/en.aspx'

    def __init__(self, page: Page):
        super().__init__(page)
        self.clients_link: Locator = page.get_by_role('link', name='Clients')
        self.account_list_link: Locator = page.get_by_role('link', name='Account List')

    def navigate(self) -> None:
        logger.info(f"ClientsPage navigate - Current URL: {self.page.url}")
        # If already on the page, just ensure elements are visible
        if self.PAGE_URL in self.page.url:
            logger.info("Already on clients page, waiting for Clients link")
            self.clients_link.wait_for(state='visible', timeout=10000)
        else:
            logger.info(f"Navigating to: {self.PAGE_URL}")
            self.page.goto(self.PAGE_URL, wait_until='networkidle', timeout=30000)
            logger.info("Waiting for Clients link to be visible")
            self.clients_link.wait_for(state='visible', timeout=10000)
        logger.info("Clients page ready")

    def click_clients(self) -> None:
        logger.info("Clicking Clients link")
        self.clients_link.click()
        logger.info("Clients link clicked")

    def click_account_list(self) -> None:
        logger.info("Clicking Account List link")
        self.account_list_link.click()
        logger.info("Account List link clicked")

