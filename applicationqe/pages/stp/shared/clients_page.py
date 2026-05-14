from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ClientsPage(BasePage):
    PAGE_URL = "https://test11.ewealthmanager.com/en.aspx"
    NEW_NAV_PAGE_URL = "https://app.test01.assetmark.com/dashboard"

    def __init__(self, page: Page):
        super().__init__(page)
        # More specific locator to avoid "Learn More" link
        self.clients_link: Locator = page.get_by_role("link", name="Clients", exact=True)
        self.account_list_link: Locator = page.get_by_role("link", name="Account List", exact=True)
        self.accounts_link_new_nav = page.get_by_role("link", name="Accounts")
        
        # Client navigation locators (used in common_steps.py)
        self.clients_tab_link: Locator = page.locator("//*[@id='mainMenuWrapper']//li/a[@href='/AccountsAnalysis/Clients/ClientList']")
        self.loading_spinner: Locator = page.locator("#theLoadingImage")
        self.first_result_client_name: Locator = page.locator("//td[contains(@class,'clientName')]").first
        self.client_info_tab: Locator = page.get_by_role('link', name='Client Information')
        self.mailing_address_section: Locator = page.locator("//div[@aria-label='mailing-address-section'] | //section[contains(@class,'mailing-address')]")

    def navigate(self) -> None:
        logger.info(f"ClientsPage navigate - Current URL: {self.page.url}")
        # Just wait for page to be ready, don't navigate if already there

        if "ewealthmanager.com" in self.page.url and "login" not in self.page.url.lower():
            logger.info("Already logged in, waiting for page to be ready")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
           
            self.page.wait_for_timeout(2000)
        else:
            logger.info(f"Navigating to: {self.PAGE_URL}")
            self.page.goto(self.PAGE_URL, wait_until="domcontentloaded", timeout=60000)
        logger.info("Clients page ready")

    def click_clients(self) -> None:
        logger.info("Clicking Clients link")
        self.click(self.clients_link)  # Use BasePage.click() for auto-healing
        logger.info("Clients link clicked")

    def click_account_list(self) -> None:
        logger.info("Clicking Account List link")
        self.page.locator("#loadingImageModal").wait_for(state="hidden", timeout=60000)
        self.click(self.account_list_link, timeout=60000)  # Use BasePage.click() for auto-healing
        logger.info("Account List link clicked")

    def navigate_to_new_nav(self) -> None:
        logger.info(f"Navigating to new nav page: {self.NEW_NAV_PAGE_URL}")
        self.page.goto(self.NEW_NAV_PAGE_URL)
        self.dismiss_cookie_banner()
        logger.info("New nav page loaded successfully")

    def click_account_list_new_nav(self) -> None:
        logger.info("Clicking Accounts link in new nav")
        self.click(self.accounts_link_new_nav)
        logger.info("Accounts link clicked")
    