from typing import Union
from playwright.sync_api import Locator, Page, FrameLocator

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageBenePage(BasePage):
    PAGE_URL = "https://app.dev01.assetmark.com/bene/landing-page?householdid=CE6VZ3"

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        # Use specific ID to avoid ambiguity with the main menu Account Wizard link
        self.account_wizard_link: Locator = context.locator("#clientDetailAccountDetailAnchor")
        self.funded_radio_input: Locator = context.locator(
            "input#ctl00_cphContentArea_rdlAccountList_1[type='radio']"
        )
        self.move_assets_between_accounts_list_item: Locator = context.get_by_text(
            "Move Assets Between Accounts"
        )
        # Use specific ID to avoid ambiguity with the header
        self.roth_ira_conversion_list_item: Locator = context.locator("#lstSubCategory5")
        self.next_button: Locator = context.get_by_role("button", name="Next")
        self.manage_account_button = context.locator("div.actionButtons").get_by_role("button", name="Manage Account")
        self.manage_beneficiaries_link: Locator = context.locator("#ctl00_cphContentArea_lnkManageBeneficiary")
        
        # ==================== Beneficiary Card List ====================
        self.beneficiary_cards: Locator = context.locator("div.MuiCard-root:has(p.MuiTypography-body1)")
        self.first_beneficiary_card: Locator = context.locator("div.MuiCard-root:has(p.MuiTypography-body1)").first
        self.first_beneficiary_name: Locator = context.locator("div.MuiCard-root:has(p.MuiTypography-body1) p.MuiTypography-body1").first
        self.first_beneficiary_ssn: Locator = context.locator("div.MuiCard-root:has(p.MuiTypography-body1) p.MuiTypography-body1").nth(1)
        self.beneficiary_card_expand_button: Locator = context.locator("div.MuiCard-root svg.MuiSvgIcon-root").first


    def navigate(self) -> None:
        logger.info(f"Navigating to account detail page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.dismiss_cookie_banner()
        self.account_wizard_link.wait_for(state="visible", timeout=15000)
        logger.info("Account detail page loaded, Account Wizard link visible")

    # ==================== First Beneficiary Selection ====================
    def get_first_beneficiary_name(self) -> str:
        """Get the name of the first beneficiary from the list."""
        logger.info("Getting first beneficiary name")
        
        self.first_beneficiary_name.wait_for(state="visible", timeout=5000)
        name = self.first_beneficiary_name.inner_text()
        
        logger.info(f"First beneficiary name: {name}")
        return name

    def get_first_beneficiary_ssn(self) -> str:
        """Get the masked SSN of the first beneficiary from the list."""
        logger.info("Getting first beneficiary SSN")
        
        self.first_beneficiary_ssn.wait_for(state="visible", timeout=5000)
        ssn = self.first_beneficiary_ssn.inner_text()
        
        logger.info(f"First beneficiary SSN: {ssn}")
        return ssn

    def click_first_beneficiary_card(self) -> None:
        """Click on the first beneficiary card to expand/select it."""
        logger.info("Clicking first beneficiary card")
        
        self.first_beneficiary_card.wait_for(state="visible", timeout=5000)
        self.first_beneficiary_card.click()
        
        logger.info("[OK] First beneficiary card clicked")

    def click_first_beneficiary_expand_button(self) -> None:
        """Click the expand/arrow button on the first beneficiary card."""
        logger.info("Clicking first beneficiary expand button")
        
        self.beneficiary_card_expand_button.wait_for(state="visible", timeout=5000)
        self.beneficiary_card_expand_button.click()
        
        logger.info("[OK] First beneficiary expand button clicked")

    def get_first_beneficiary_details(self) -> dict:
        """Get all details (name and SSN) of the first beneficiary."""
        logger.info("Getting first beneficiary complete details")
        
        name = self.get_first_beneficiary_name()
        ssn = self.get_first_beneficiary_ssn()
        
        details = {
            "name": name,
            "ssn": ssn
        }
        
        logger.info(f"First beneficiary details: {details}")
        return details

    def is_first_beneficiary_card_visible(self) -> bool:
        """Check if the first beneficiary card is visible on the page."""
        logger.info("Checking if first beneficiary card is visible")
        
        is_visible = self.first_beneficiary_card.is_visible()
        logger.info(f"First beneficiary card visible: {is_visible}")
        return is_visible

    def count_beneficiary_cards(self) -> int:
        """Count total number of beneficiary cards in the list."""
        logger.info("Counting beneficiary cards")
        
        count = self.beneficiary_cards.count()
        logger.info(f"Total beneficiary cards: {count}")
        return count
    
    def get_all_account_holder_names(self) -> list:
        """Get names of all account holders displayed on the page."""
        logger.info("Getting all account holder names from page")
        
        self.beneficiary_cards.first.wait_for(state="visible", timeout=5000)
        
        account_holder_names = []
        card_count = self.beneficiary_cards.count()
        
        for i in range(card_count):
            card = self.beneficiary_cards.nth(i)
            name_element = card.locator("p.MuiTypography-body1").first
            name = name_element.inner_text()
            account_holder_names.append(name)
        
        logger.info(f"[OK] Found {len(account_holder_names)} account holders: {account_holder_names}")
        return account_holder_names

    def click_first_beneficiary_detail(self) -> None:
        """Click on the first beneficiary to view details/expand."""
        logger.info("Clicking first beneficiary to view details")

        # Wait for the page to fully settle before looking for cards;
        # the landing page loads asynchronously and 5 s is too short on
        # slower environments or first loads.
        self.page.wait_for_load_state('networkidle')
        self.first_beneficiary_card.wait_for(state="visible", timeout=15000)
        self.first_beneficiary_card.click()
        self.page.wait_for_load_state('networkidle')

        logger.info("[OK] First beneficiary detail clicked and page loaded")
    
    def click_account_holder_by_name(self, account_holder_name: str) -> None:
        """Click on a specific account holder card by name."""
        logger.info(f"Searching for and clicking account holder: {account_holder_name}")
        
        self.beneficiary_cards.first.wait_for(state="visible", timeout=5000)
        
        card_count = self.beneficiary_cards.count()
        clicked = False
        
        for i in range(card_count):
            card = self.beneficiary_cards.nth(i)
            name_element = card.locator("p.MuiTypography-body1").first
            name = name_element.inner_text()
            
            if name == account_holder_name:
                logger.info(f"Found matching account holder at index {i}: {name}")
                card.click()
                self.page.wait_for_load_state('networkidle')
                clicked = True
                break
        
        if not clicked:
            available_names = [self.beneficiary_cards.nth(i).locator("p.MuiTypography-body1").first.inner_text() 
                             for i in range(card_count)]
            raise ValueError(
                f"Account holder '{account_holder_name}' not found on page. "
                f"Available names: {available_names}"
            )
        
        logger.info(f"[OK] Clicked on account holder '{account_holder_name}' and page loaded")

    def wait_for_add_button_ready(self) -> None:
        """Wait for the Add Beneficiary button to be ready after fallback navigation."""
        logger.info("Waiting for Add button to be ready")
        
        add_button = self.page.locator("button[aria-label='Add']")
        add_button.wait_for(state="visible", timeout=5000)
        
        logger.info("[OK] Add button is ready")

   