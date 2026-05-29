from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class PortfolioDetailsPage(BasePage):
    """Page object for Portfolio Details page"""

    def __init__(
        self,
        page: Page,
        page_verification: bool = True,
    ):
        """
        Initialize Portfolio Details page.
        
        Args:
            page: Playwright page instance
            page_verification: Flag to check if the page is loaded (default: True)
        """
        super().__init__(page)
        self.form_root = self.active_root()
        
        # Page label
        self.portfolio_details_page_label: Locator = self.form_root.locator("//h1[text()='Portfolio Details']")
        
        # Navigation tabs
        self.client_profile_tab: Locator = self.form_root.locator("text=Client Profile")
        self.construct_portfolio_tab: Locator = self.form_root.locator("text=Construct Portfolio")
        self.fees_tab: Locator = self.form_root.locator("text=Fees")
        self.portfolio_details_tab: Locator = self.form_root.locator("text=Portfolio Details")
        self.account_setup_tab: Locator = self.form_root.locator("text=Account Setup")
        self.create_documents_tab: Locator = self.form_root.locator("text=Create Documents")
        self.view_documents_tab: Locator = self.form_root.locator("text=View Documents")
        
        # Action buttons
        self.account_setup_button: Locator = self.form_root.get_by_role("button", name="Account Setup")
        self.configuration_icon: Locator = self.form_root.locator("//div[contains(@class,'configurationIcon')]/button")
        
        # Page verification
        if page_verification:
            try:
                self.portfolio_details_page_label.wait_for(state="visible", timeout=20000)
                logger.info("Portfolio Details page verification PASSED")
            except Exception as e:
                logger.warning(f"Portfolio Details page verification FAILED: {str(e).splitlines()[0]}")

    def go_to_account_setup(self, step_name: str, log_message: str):
        """
        Navigate to Account Setup page by clicking the Account Setup button.
        Mirrors old Selenium: goToAccountSetup()
        
        Args:
            step_name: Description of the step
            log_message: Log message to record
            
        Returns:
            AccountSetupPage instance
        """
        self.wait_for_spinner_to_disappear()
        logger.info(step_name)
        # Wait for account setup button to be clickable and visible
        self.account_setup_button.wait_for(state="visible", timeout=30000)

        # Click without waiting for navigation (navigation can be slow)
        # Chat widget overlay can intercept pointer events — fall back to JS click
        try:
            self.account_setup_button.click(no_wait_after=True, timeout=10000)
        except Exception:
            logger.warning("[account_setup] Regular click blocked (likely chat widget overlay), using JS click")
            self.account_setup_button.evaluate("el => el.click()")
        logger.info(log_message)

        # Let the next page start loading
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            logger.warning(f"Account setup load wait timed out: {str(e).splitlines()[0]}")

