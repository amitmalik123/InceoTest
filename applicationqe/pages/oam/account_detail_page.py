from playwright.sync_api import Locator, Page

from locators.oam import account_detail_locators
from pages.oam.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountDetailPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountDetail/Holdings/Summary"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = account_detail_locators.initialize_locators(page)
        self.account_wizard_link: Locator = locators["account_wizard_link"]
        self.funded_radio_input: Locator = locators["funded_radio_input"]
        self.move_assets_between_accounts_list_item: Locator = locators["move_assets_between_accounts_list_item"]
        self.roth_ira_conversion_list_item: Locator = locators["roth_ira_conversion_list_item"]
        self.next_button: Locator = locators["next_button"]

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to account detail page: {url}")
        self.page.goto(url)
        # Wait for network to stabilize (important for headless mode)
        self.page.wait_for_load_state("networkidle", timeout=120000)
        self.account_wizard_link.wait_for(state="visible", timeout=120000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard button on account detail page")
        # Pass increased timeout to click() method for headless mode compatibility
        self.click(self.account_wizard_link, timeout=120000)
        logger.info("Account Wizard button clicked")

    def select_funded_radio(self) -> None:
        logger.info("Selecting Funded radio button")
        self.funded_radio_input.check()
        logger.info("Funded radio selected")

    def select_move_assets_between_accounts(self) -> None:
        logger.info("Selecting Move Assets Between Accounts")
        # Pass increased timeout to click() method for headless mode compatibility
        self.click(self.move_assets_between_accounts_list_item, timeout=120000)
        logger.info("Move Assets Between Accounts selected")

    def select_roth_ira_conversion(self) -> None:
        logger.info("Selecting Roth IRA Conversion")
        # Pass increased timeout to click() method for headless mode compatibility
        self.click(self.roth_ira_conversion_list_item, timeout=120000)
        logger.info("Roth IRA Conversion selected")

    def click_next(self) -> None:
        logger.info("Clicking Next button")
        # Pass increased timeout to click() method for headless mode compatibility
        self.click(self.next_button, timeout=120000)
        logger.info("Next button clicked")
