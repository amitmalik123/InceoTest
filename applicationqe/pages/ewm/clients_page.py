from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ClientsPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/en.aspx'
    NEW_NAV_PAGE_URL = 'https://app.test01.assetmark.com/dashboard'

    def __init__(self, page: Page):
        super().__init__(page)
        self.clients_link: Locator = page.get_by_role('link', name='Clients')
        self.account_list_link: Locator = page.get_by_role('link', name='Account List')
        self.accounts_link_new_nav: Locator = page.get_by_role('link', name='Accounts')
        self.add_client_button: Locator = page.get_by_role("button", name="Add a Client")

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

    def click_add_client(self) -> None:
        """Click the add a client button on clients page."""
        logger.info("Clicking add a client button")
        try:
            self.add_client_button.wait_for(state="visible", timeout=30000)
            self._click_element_with_strategies(self.add_client_button, "Add a Client button")
        except PlaywrightTimeoutError:
            logger.warning(
                "Add a Client button did not become visible in 30s; using JS fallback on attached element"
            )
            self.add_client_button.first.wait_for(state="attached", timeout=10000)
            self.add_client_button.first.evaluate("el => el.click()")
        self.wait_for_spinner_to_disappear(timeout=30)
        logger.info("Add a client button clicked")

    def navigate_to_new_nav(self) -> None:
        logger.info(f"Navigating to new nav page: {self.NEW_NAV_PAGE_URL}")
        self.page.goto(self.NEW_NAV_PAGE_URL)
        self.dismiss_cookie_banner()
        logger.info("New nav page loaded successfully")

    def click_account_list_new_nav(self) -> None:
        logger.info("Clicking Accounts link in new nav")
        self.accounts_link_new_nav.click()
        logger.info("Accounts link clicked")

