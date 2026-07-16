from typing import Any, Union

from playwright.sync_api import FrameLocator, Locator, Page

from pages.base_page import BasePage
from pages.ewm.locators.account_detail_locators import AccountDetailLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AccountDetailPage(BasePage):
    PAGE_PATH = "AccountsAnalysis/Clients/AccountDetail"

    def __init__(self, context: Union[Page, FrameLocator]):
        # Keep EWM behavior for normal Page usage, but allow STP iframe context too.
        if isinstance(context, Page):
            super().__init__(context)
            self.context = context
            self.page = context
        else:
            # Minimal init for FrameLocator compatibility (used by STP manage-bene flow).
            self.context = context
            self.page = None
            self.base_url = ""
            self.home_url = ""
            self.logger = logger

        loc = AccountDetailLocators
        # Use specific ID to avoid ambiguity with the main menu Account Wizard link
        self.account_wizard_link: Locator = context.locator(loc.ACCOUNT_WIZARD_LINK)
        self.funded_radio_input: Locator = context.locator(loc.FUNDED_RADIO_INPUT)
        self.move_assets_between_accounts_list_item: Locator = context.get_by_text(loc.MOVE_ASSETS_TEXT)
        # Use specific ID to avoid ambiguity with the header
        self.roth_ira_conversion_list_item: Locator = context.locator(loc.ROTH_IRA_CONVERSION)
        self.next_button: Locator = context.get_by_role("button", name=loc.NEXT_BUTTON)
        self.manage_account_button: Locator = context.locator(loc.MANAGE_ACCOUNT_CONTAINER).get_by_role(
            "button", name=loc.MANAGE_ACCOUNT_BUTTON
        )
        self.manage_beneficiaries_link: Locator = context.locator(loc.MANAGE_BENEFICIARIES_LINK)

    def navigate(self, url: str = None) -> None:
        if url:
            logger.info(f"Navigating to account detail page: {url}")
            self.page.goto(url)
        else:
            logger.info("Waiting for account detail page to load")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.account_wizard_link.wait_for(state='visible', timeout=15000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard button on account detail page")
        self.account_wizard_link.wait_for(state="visible", timeout=60000)
        self.account_wizard_link.click()
        if self.page:
            self.page.wait_for_load_state("networkidle", timeout=120000)
            self.dismiss_cookie_banner()
        logger.info("Account Wizard button clicked")

    def select_funded_radio(self) -> None:
        logger.info("Selecting Funded radio button")
        self.funded_radio_input.check()
        logger.info("Funded radio selected")

    def select_move_assets_between_accounts(self) -> None:
        logger.info("Selecting Move Assets Between Accounts")
        self.move_assets_between_accounts_list_item.click()
        logger.info("Move Assets Between Accounts selected")

    def select_roth_ira_conversion(self) -> None:
        logger.info("Selecting Roth IRA Conversion")
        self.roth_ira_conversion_list_item.click()
        logger.info("Roth IRA Conversion selected")

    def click_next(self) -> None:
        logger.info("Clicking Next button")
        self.next_button.click()
        logger.info("Next button clicked")

    def click_manage_account(self) -> None:
        logger.info("Clicking Manage Account button on account detail page")
        self.manage_account_button.wait_for(state="visible", timeout=20000)
        self.manage_account_button.click()
        logger.info("Manage Account button clicked")

    def verify_manage_beneficiaries_link_present(self) -> bool:
        """Verify Manage Beneficiaries link is present and return status."""
        try:
            self.manage_beneficiaries_link.wait_for(state="visible", timeout=10000)
            link_text = self.manage_beneficiaries_link.text_content()
            logger.info(f"Manage Beneficiaries link found with text: {link_text}")
            return True
        except Exception as e:
            logger.error(f"Manage Beneficiaries link not found: {e}")
            return False

    def get_manage_beneficiaries_text(self) -> str:
        """Get text content of Manage Beneficiaries link."""
        self.manage_beneficiaries_link.wait_for(state="visible", timeout=10000)
        return self.manage_beneficiaries_link.text_content() or ""

    def dismiss_cookie_banner(self) -> None:
        """Dismiss OneTrust/Ketch privacy overlays if present."""
        if not self.page:
            return

        try:
            accept_btn = self.page.locator("button.save-preference-btn-handler")
            accept_btn.wait_for(state="visible", timeout=8000)
            accept_btn.click()
            self.page.locator(".onetrust-pc-dark-filter").wait_for(state="hidden", timeout=8000)
            logger.info("Cookie consent banner dismissed")
        except Exception:
            pass

        try:
            dark_filter = self.page.locator(".onetrust-pc-dark-filter")
            if dark_filter.count() > 0 and dark_filter.is_visible():
                self.page.evaluate(
                    """() => {
                        const el = document.querySelector('.onetrust-pc-dark-filter');
                        if (el) el.style.display = 'none';
                        const sdk = document.getElementById('onetrust-consent-sdk');
                        if (sdk) sdk.style.display = 'none';
                    }"""
                )
                logger.info("OneTrust overlay force-hidden via JS")
        except Exception:
            pass

        try:
            ketch_btn = self.page.locator("#ketch-banner-button-primary")
            if ketch_btn.count() > 0:
                ketch_btn.wait_for(state="visible", timeout=5000)
                ketch_btn.click()
                self.page.locator("#ketch-consent-banner").wait_for(state="hidden", timeout=5000)
                logger.info("Ketch privacy banner dismissed")
        except Exception:
            pass

