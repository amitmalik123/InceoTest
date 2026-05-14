from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import setup_logger
from utils.wait_utils import wait_for_element_stable

logger = setup_logger(__name__)


class AddACHConfirmationPage(BasePage):
    """Page object for Add ACH Instructions Confirmation Page"""
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        
        # Locators
        self.confirmation_header = page.locator("//span[text()='Request Confirmation']")
        self.confirmation_details_list = page.locator("//h3[@aria-label]/following-sibling::span")
        self.single_investment_account = page.locator("//li[@class]")
        self.investment_accounts_list = page.locator("//ol")
        self.close_button = page.locator("//button[text()='Close']")
        self.subheader_household = page.locator("//span[text()='Client Household']/following-sibling::div")
        self.subheader_advisor_id = page.locator("//span[text()='Advisor ID']/following-sibling::div")
        self.request_banner = page.locator("//div[@aria-label='confirmation-screen-status']")
        self.information_banner = page.locator("//button[@aria-label='info']/parent::p/parent::div")
        self.item_number = page.locator("//h3[text()='Item number:']/following-sibling::a")
        
        # Page verification
        if page_verification:
            self._verify_page_loaded()
    
    def _verify_page_loaded(self):
        """Verify the confirmation page has loaded"""
        page_name = "Add ACH Confirmation Page"
        try:
            self.page.wait_for_load_state('networkidle', timeout=45000)
            self.page.wait_for_timeout(2000)
            
            # Check if confirmation header is visible
            is_visible = self.confirmation_header.is_visible(timeout=10000)
            
            if is_visible:
                logger.info(f"{page_name} verification: PASSED")
            else:
                logger.warning(f"{page_name} verification: FAILED")
        except Exception as e:
            logger.error(f"{page_name} verification failed with error: {e}")
    
    def get_confirmation_details(self) -> list:
        """Get all confirmation details as list of text values"""
        logger.info("Getting confirmation details")
        
        # Use stable wait instead of manual wait_for
        # This handles SPA rendering, animations, and re-renders
        stable_locator = wait_for_element_stable(
            self.confirmation_details_list.first,
            timeout=15.0,
            check_animations=True
        )
        
        # Get all elements
        elements = self.confirmation_details_list.all()
        logger.info(f"Found {len(elements)} confirmation detail elements")
        
        # Extract text from each element
        text_values = [elem.inner_text().strip() for elem in elements]
        logger.info(f"Confirmation details text: {text_values}")
        
        return text_values
    
    def get_confirmation_page_other_details(self) -> list:
        """Get other confirmation page details (household, advisor ID, banners)"""
        logger.info("Getting other confirmation page details")
        details_list = []
        
        self.subheader_household.wait_for(state='visible', timeout=5000)
        details_list.append(self.subheader_household.inner_text())
        details_list.append(self.subheader_advisor_id.inner_text())
        details_list.append(self.request_banner.inner_text())
        details_list.append(self.information_banner.inner_text())
        
        logger.info(f"Other details: {details_list}")
        return details_list
    
    def get_item_number(self) -> str:
        """Get the item number from confirmation page"""
        logger.info("Getting item number from confirmation page")
        item_text = self.item_number.inner_text()
        logger.info(f"Item number: {item_text}")
        return item_text
    
    def validate_hyperlink(self) -> bool:
        """Validate if item number is a hyperlink"""
        logger.info("Validating if item number is a hyperlink")
        is_visible = self.item_number.is_visible()
        logger.info(f"Item number hyperlink visible: {is_visible}")
        return is_visible
    
    def get_investment_account_confirm_page(self) -> str:
        """Get single investment account from confirmation page"""
        logger.info("Getting single investment account")
        account_text = self.single_investment_account.inner_text()
        logger.info(f"Investment account: {account_text}")
        return account_text
    
    def get_investment_accounts_confirm_page(self) -> str:
        """Get multiple investment accounts from confirmation page"""
        logger.info("Getting multiple investment accounts")
        accounts_text = self.investment_accounts_list.inner_text()
        logger.info(f"Investment accounts: {accounts_text}")
        return accounts_text
    
    def click_item_number(self):
        """Click on the item number to navigate to tracking center in same page"""
        logger.info("Clicking item number")
        
        self.item_number.click()
        self.page.wait_for_load_state('networkidle', timeout=30000)
        self.page.wait_for_timeout(3000)
        
        logger.info("Item number clicked, navigated in same page")
        return self.page
        
        logger.info("Item number clicked and switched to new tab")
        return new_page
