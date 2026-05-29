from playwright.sync_api import Locator, Page

from pages.oam.base_page import BasePage
from locators.oam import clients_locators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ClientsPage(BasePage):
    PAGE_PATH = "en.aspx"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        # More specific locator to avoid "Learn More" link
        locators = clients_locators.initialize_locators(page)
        self.clients_link: Locator = locators["clients_link"]
        self.account_list_link: Locator = locators["account_list_link"]

    def navigate(self) -> None:
        logger.info(f"ClientsPage navigate - Current URL: {self.page.url}")
        url = f"{self.base_url}{self.PAGE_PATH}"
        # Just wait for page to be ready, don't navigate if already there
        if (
            self.base_url
            and self.base_url.rstrip("/") in self.page.url
            and "login" not in self.page.url.lower()
        ):
            logger.info("Already logged in, waiting for page to be ready")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        else:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        logger.info("Clients page ready")

    def click_clients(self) -> None:
        logger.info("Clicking Clients link")
        self.click(self.clients_link)  # Use BasePage.click() for auto-healing
        logger.info("Clients link clicked")

    def click_account_list(self) -> None:
        logger.info("Clicking Account List link")
        self.click(self.account_list_link)  # Use BasePage.click() for auto-healing
        logger.info("Account List link clicked")
