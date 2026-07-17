from typing import Optional

from playwright.sync_api import Locator, Page

from config.settings import get_settings
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountWizardPage(BasePage):
    PAGE_PATH = "DNeWM/NBT/List/AccountWizard.aspx"

    def __init__(self, page: Page, base_url: str = ""):
        resolved_base_url = base_url or get_settings().base_url
        super().__init__(page, base_url=resolved_base_url)
        self.account_wizard_link: Locator = page.get_by_role("link", name="Account Wizard")
        self.account_wizard_header: Locator = page.get_by_role("heading", name="Account Wizard")
        self.go_button: Locator = page.locator('#ctl00_cphContentArea_Button1')
        self.announcement_popup: Locator = page.locator("#promoChatCloseIcon")

    def navigate(self) -> None:
        logger.info(f"AccountWizardPage navigate - Current URL: {self.page.url}")
        url = f"{self.base_url}{self.PAGE_PATH}"

        if self.PAGE_PATH in self.page.url:
            logger.info("Already on account wizard page")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        else:
            logger.info(f"Navigating to: {url}")
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    break
                except Exception as e:
                    if "net::ERR_ABORTED" in str(e) and attempt < max_retries:
                        logger.warning(f"[navigate] net::ERR_ABORTED on attempt {attempt}, retrying after wait")
                        self.page.wait_for_timeout(3000)
                    else:
                        raise
        logger.info("Account wizard page ready")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard link")
        self.account_wizard_link.wait_for(state="visible", timeout=10000)
        self.click(self.account_wizard_link)
        logger.info("Account Wizard link clicked")

    def verify_account_wizard_page_loaded(self, expected_client_name: Optional[str] = None) -> None:
        logger.info("Verifying Account Wizard page is loaded")

        self.account_wizard_header.wait_for(state="visible", timeout=10000)
        header_text = self.get_text(self.account_wizard_header)

        if header_text and "Account Wizard" in header_text:
            logger.info(f"Account Wizard page loaded successfully. Header: {header_text}")
        else:
            raise Exception(
                f"Account Wizard page header not found or incorrect. Found: {header_text}"
            )

        if expected_client_name:
            self.client_name.wait_for(state="visible", timeout=10000)
            client_name_text = self.get_text(self.client_name)
            logger.info(f"Client name displayed: {client_name_text}")

            if expected_client_name not in client_name_text:
                raise Exception(
                    f"Expected client name '{expected_client_name}' not found. Found: {client_name_text}"
                )
            logger.info(f"Client name verified: {client_name_text}")

    def fetch_selected_account_information(self):
        """Fetch the selected account information from the radio button label"""
        account_text = self.get_text(self.selected_account_label)
        logger.info(f"Selected account information: {account_text}")
        return account_text.split("(")

    def click_add_ach_instructions(self):
        """Click on Add ACH Instructions link"""
        logger.info("Clicking Add ACH Instructions link")
        add_ach_link = self.page.get_by_role(
            "link", name="Add ACH Instructions and/or Standing Letter of Authorization"
        )
        add_ach_link.wait_for(state="visible", timeout=30000)
        self.click(add_ach_link)

        # Wait for navigation/modal to load
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        logger.info("Add ACH Instructions link clicked")

    def click_Go_Button(self):
        """Backward-compatible step used by existing NAW scenarios."""
        logger.info("Clicking Go button for New Client creation")
        self.navigate()

        # Dismiss any cookie/chat popups that may block controls
        self.close_chat_popups()

        if self.account_wizard_link.is_visible():
            self.account_wizard_link.click(timeout=15000)
            logger.info("Account Wizard link clicked")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        if self.announcement_popup.is_visible(timeout=5000):
            self.click(self.announcement_popup)
            logger.info("Announcement popup closed")

        self.go_button.wait_for(state="visible", timeout=30000)
        # Go button triggers __doPostBack — expect_navigation listens BEFORE click fires,
        # no_wait_after prevents click from hanging on "waiting for scheduled navigations"
        with self.page.expect_navigation(timeout=60000, wait_until="domcontentloaded"):
            self.go_button.click(no_wait_after=True)
        logger.info("Go button clicked")
