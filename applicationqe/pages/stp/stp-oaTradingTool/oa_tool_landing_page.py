from playwright.sync_api import Page
from pages.stp.shared.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OAToolLandingPage(BasePage):
    PAGE_NAME = "Trading Instructions"
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        
        # Account Information
        self.client_household = page.locator("//span[text()='Account Information']//parent::div//parent::div/following-sibling::div/child::div")
        self.market_value_amount = page.locator("//span[text()='Market Value']/parent::div//following-sibling::span")
        self.cash_available_amount = page.locator("//span[text()='Cash Available']/parent::div//following-sibling::span")
        self.restricted_cash_amount = page.locator("//span[text()='Restricted Cash']/parent::div//following-sibling::span")
        
        # Info icons
        self.market_value_info_icon = page.locator("//span[text()='Market Value']/following-sibling::button")
        self.cash_available_info_icon = page.locator("//span[text()='Cash Available']/following-sibling::button")
        self.restricted_cash_info_icon = page.locator("//span[text()='Restricted Cash']/following-sibling::button")
        
        # Info popups
        self.market_value_info_popup = page.locator("(//span[text()='Market Value']/parent::div/parent::div/parent::div)[1]")
        self.cash_available_info_popup = page.locator("(//span[text()='Cash Available']/parent::div/parent::div/parent::div)[1]")
        self.restricted_cash_info_popup = page.locator("(//span[text()='Restricted Cash']/parent::div/parent::div/parent::div)[1]")
        
        # Other elements
        self.request_type_container = page.locator("//div[@id='request-type-container']")
        self.advisor_id = page.locator("//p[contains(text(),'Advisor ID')] | //div[contains(text(),'Advisor ID')]")
        self.disabled_radio_buttons1 = page.locator("(//button[@tabindex='-1'])[1]")
        self.disabled_radio_buttons2 = page.locator("(//button[@tabindex='-1'])[2]")
        self.next_button = page.locator("//span[text()='Next']")
        self.button_otw = page.locator("//p[contains(text(),'One Time Withdrawal')]")
        self.bottom_hyperlinks = page.locator("(//div[contains(text(),'Privacy and Security')] //parent::div//div) | (//p[contains(text(),'Privacy and Security')] //parent::a/parent::div//child::a)")
        self.assetmark_bottom_heading = page.locator("p[class*='Copyright-module__desktopText']")
        self.assetmark_image = page.locator("img[alt='AssetMark']")
        
        if page_verification:
            is_visible = page.locator("//span[text()='Trading and Account Management'] | //p[text()='Trading and Account Management']").is_visible(timeout=45000)
            if is_visible:
                logger.info(f"{self.PAGE_NAME} verification : {self.PAGE_NAME} verification is PASSED")
            else:
                logger.info(f"{self.PAGE_NAME} verification is FAILED")
    
    def get_household_heading_locator(self, household_header: str):
        """Helper method to get household heading locator"""
        return self.page.locator(f"//span[text()='{household_header}']")
    
    def get_household_account_locator(self, household_header: str):
        """Helper method to get household account locator"""
        return self.page.locator(f"//span[text()='{household_header}']/following-sibling::span")
    
    def get_market_value(self) -> str:
        return self.market_value_amount.inner_text()
    
    def get_cash_available(self) -> str:
        return self.cash_available_amount.inner_text()
    
    def get_restricted_cash(self) -> str:
        return self.restricted_cash_amount.inner_text()
    
    def click_market_value_info(self):
        self.market_value_info_icon.click()
    
    def click_cash_available_info(self):
        self.cash_available_info_icon.click()
    
    def click_restructed_cash_info(self):
        self.restricted_cash_info_icon.click()
    
    def get_request_type_container_text(self) -> str:
        return self.request_type_container.inner_text()
    
    def are_buttons_clickable(self) -> bool:
        button1_enabled = self.disabled_radio_buttons1.is_enabled()
        button2_enabled = self.disabled_radio_buttons1.is_enabled()
        if button1_enabled and button2_enabled:
            return True
        else:
            return False
    
    def click_otw(self):
        self.button_otw.click()
    
    def click_next(self):
        self.next_button.click()
        from oa_tool_transaction_page import OAToolTransactionPage
        return OAToolTransactionPage(self.page)
    
    def get_advisor_id(self) -> str:
        return self.advisor_id.inner_text()
    
    def get_household_heading_and_account(self, household_header: str) -> list:
        heading_text = self.get_household_heading_locator(household_header).inner_text()
        account_text = self.get_household_account_locator(household_header).inner_text()
        return [heading_text, account_text]
    
    def get_bottom_hyperlinks(self) -> list:
        self.bottom_hyperlinks.first.wait_for(state="visible")
        elements = self.bottom_hyperlinks.all()
        return [elem.inner_text() for elem in elements]
    
    def get_assetmark_bottom_heading(self) -> str:
        return self.assetmark_bottom_heading.inner_text()
    
    def verify_assetmark_image(self) -> bool:
        return self.assetmark_image.is_visible()
