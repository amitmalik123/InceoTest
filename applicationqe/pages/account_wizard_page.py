from typing import Optional

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from locators import account_wizard_locators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountWizardPage(BasePage):
    PAGE_PATH = "DNeWM/NBT/List/ClientAccounts.aspx"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = account_wizard_locators.initialize_locators(page)
        self.account_wizard_link: Locator = locators["account_wizard_link"]
        self.account_wizard_header: Locator = locators["account_wizard_header"]
        self.selected_account_label: Locator = locators["selected_account_label"]
        self.client_name: Locator = locators["client_name"]

    def navigate(self) -> None:
        logger.info(f"AccountWizardPage navigate - Current URL: {self.page.url}")
        url = f"{self.base_url}{self.PAGE_PATH}"

        if self.PAGE_PATH in self.page.url:
            logger.info("Already on account wizard page")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        else:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until="networkidle", timeout=60000)
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
