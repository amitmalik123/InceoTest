"""
Withdrawal Method Modal Page Object

Handles interactions with the Withdrawal Method selection modal that appears
during withdrawal request flow when SLOA options are available.
"""

from playwright.sync_api import FrameLocator, Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_swp.locators.withdrawal_method_modal_locators import WithdrawalMethodModalLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class WithdrawalMethodModalPage(BasePage):
    """Page object for Withdrawal Method Modal"""
    
    def __init__(self, page: Page, frame: FrameLocator = None):
        super().__init__(page)
        loc = WithdrawalMethodModalLocators
        
        # Get the iframe context if not provided
        if frame is None:
            self.frame = page.frame_locator(loc.IFRAME)
        else:
            self.frame = frame
        
        # Modal header
        self.modal_header = self.frame.locator(loc.MODAL_HEADER)
        
        # Radio buttons for withdrawal methods
        self.ach_radio = self.frame.locator(loc.ACH_RADIO)
        self.wire_radio = self.frame.locator(loc.WIRE_RADIO)
        self.check_radio = self.frame.locator(loc.CHECK_RADIO)
        
        # Continue button
        self.continue_button = self.frame.locator(loc.CONTINUE_BUTTON)
        
        # Selected instructions table
        self.selected_instructions_table = self.frame.locator(loc.SELECTED_INSTRUCTIONS_TABLE)
    
    def wait_for_modal_visible(self, timeout: int = 20000):
        """Wait for withdrawal method modal to be visible"""
        logger.info("Waiting for Withdrawal Method Modal to be visible")
        self.modal_header.wait_for(state='visible', timeout=timeout)
        logger.info("[OK] Withdrawal Method Modal is visible")
    
    def click_ach(self, sloa_option: str):
        """
        Click ACH radio button and select SLOA option
        
        Args:
            sloa_option: "Yes" for SLOA Yes, "No" for SLOA No, or specific bank details
        """
        logger.info(f"Selecting ACH withdrawal method with SLOA option: {sloa_option}")
        
        # Wait for modal to be visible
        self.wait_for_modal_visible()
        
        # Click ACH radio button
        self.ach_radio.wait_for(state='visible', timeout=10000)
        self.ach_radio.click()
        logger.info("[OK] ACH radio button clicked")
        
        # Wait for SLOA options to load
        self.page.wait_for_timeout(1000)
        
        # Select SLOA option
        if sloa_option.upper() == "YES":
            # Select first SLOA Yes option
            sloa_yes_radio = self.frame.locator("(//input[@value='DEL_METH_ACH_SLOA'])[1]")
            if sloa_yes_radio.count() > 0:
                sloa_yes_radio.click()
                logger.info("[OK] SLOA Yes option selected")
            else:
                raise Exception("SLOA Yes option not found")
        elif sloa_option.upper() == "NO":
            # Select new instructions
            new_instructions_radio = self.frame.locator("#rbAchNewBank")
            new_instructions_radio.click()
            logger.info("[OK] New Instructions (SLOA No) selected")
        else:
            # Select specific bank option
            bank_radio = self.frame.locator(f"//label[contains(text(), '{sloa_option}')]//ancestor::td//input[@name='DEL_METH_ACH']")
            bank_radio.click()
            logger.info(f"[OK] Bank option selected: {sloa_option}")
    
    def click_check(self, sloa_option: str):
       
        logger.info(f"Selecting Check withdrawal method with SLOA option: {sloa_option}")
        
        self.wait_for_modal_visible()
        
        self.check_radio.wait_for(state='visible', timeout=10000)
        self.check_radio.click()
        logger.info("[OK] Check radio button clicked")
        
        self.page.wait_for_timeout(2000)
        data_loaded = (
            self.frame.locator("text='Instructions on File'").count() > 0 or
            self.frame.locator("text='Enter the bank information on the PDF form.'").count() > 0
        )
        
        if not data_loaded:
            logger.warning("Expected text not found after clicking Check radio")
        
        if sloa_option == "NewInstructions":
            new_instructions_radio = self.frame.locator("#rbChkAddrNew")
            new_instructions_radio.wait_for(state='visible', timeout=10000)
            new_instructions_radio.click()
            logger.info("[OK] New Instructions radio selected")
            
        elif sloa_option != "":
            self.page.wait_for_timeout(1000)
            
            if "NO" in sloa_option.upper():
                no_radio = self.frame.locator(
                    "//label[contains(text(),'No')]"
                    "/parent::td/parent::tr/parent::tbody/parent::table/parent::td/child::div/"
                    "child::span/child::input[@name='DEL_METH_CHECK_MAILTO']"
                )
                no_radio.wait_for(state='visible', timeout=10000)
                no_radio.click()
                logger.info(f"[OK] {sloa_option} option selected")
                
            elif "SLOA" in sloa_option.upper():
                self.page.wait_for_timeout(1000)
                sloa_radio = self.frame.locator(
                    f"//td//table//td//label[contains(text(),'{sloa_option}')]"
                    "/parent::td/parent::tr/parent::tbody/parent::table/parent::td/child::div"
                )
                sloa_radio.wait_for(state='visible', timeout=10000)
                sloa_radio.click()
                logger.info(f"[OK] {sloa_option} option selected")
                
            else:
                # yes_radio = self.frame.locator(
                #     "//td//table//td//label[contains(text(),'Yes')]"
                #     "/parent::td/parent::tr/parent::tbody/parent::table/parent::td/child::div/"
                #     "child::span/child::input[@name='DEL_METH_CHECK_MAILTO']"
                # )
                yes_radio = self.frame.locator("//input[@id='rbChkAddrOnSloa0']")
                yes_radio.wait_for(state='visible', timeout=10000)
                yes_radio.click()
                logger.info(f"[OK] {sloa_option} (Yes) option selected")
                
        else:
            first_radio = self.frame.locator(
                "/html[1]/body[1]/form[1]/div[3]/div[1]/div[2]/div[1]/table[1]/"
                "tbody[1]/tr[2]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/span[1]/input[1]"
            )
            first_radio.wait_for(state='visible', timeout=10000)
            first_radio.click()
            logger.info("[OK] First radio option selected")
        
        logger.info("[OK] Check withdrawal method selected successfully")
    
    def get_selected_ach_details(self, sloa_option: str) -> list:
        
        logger.info(f"Fetching selected ACH details for SLOA: {sloa_option}")
        
        details = []
        
        try:
            self.selected_instructions_table.wait_for(state='visible', timeout=10000)
            
            bank_name_elements = self.selected_instructions_table.locator("//label[contains(@id,'BankName')]")
            if bank_name_elements.count() > 1:
                bank_name = bank_name_elements.nth(1).inner_text()
            else:
                bank_name = bank_name_elements.first.inner_text()
            details.append(bank_name)
            logger.info(f"Bank Name: {bank_name}")
            
            account_elements = self.selected_instructions_table.locator("//label[contains(@id,'ACNum')]")
            if account_elements.count() > 1:
                account_number = account_elements.nth(1).inner_text()
            else:
                account_number = account_elements.first.inner_text()
            details.append(account_number)
            logger.info(f"Account Number: {account_number}")
            
            aba_elements = self.selected_instructions_table.locator("//label[contains(@id,'ABA')]")
            if aba_elements.count() > 1:
                aba_routing = aba_elements.nth(1).inner_text()
            else:
                aba_routing = aba_elements.first.inner_text()
            details.append(aba_routing)
            logger.info(f"ABA Routing: {aba_routing}")
            
            customer_elements = self.selected_instructions_table.locator("//label[contains(@id,'CustomerName')]")
            if customer_elements.count() > 1:
                customer_name = customer_elements.nth(1).inner_text()
            else:
                customer_name = customer_elements.first.inner_text()
            details.append(customer_name)
            logger.info(f"Customer Name: {customer_name}")
            
            details.append(sloa_option)
            logger.info(f"SLOA Option: {sloa_option}")
            
            logger.info("[OK] Successfully fetched all ACH payee details")
            
        except Exception as e:
            logger.error(f"Failed to fetch ACH details: {str(e)}")
            raise
        
        return details
    
    def get_selected_check_details(self, sloa_option: str) -> list:
        
        logger.info(f"Fetching selected Check details for SLOA: {sloa_option}")
        
        details = []
        
        try:
            self.selected_instructions_table.wait_for(state='visible', timeout=10000)
            
            name_elements = self.selected_instructions_table.locator("//label[contains(@id,'Name')]")
            if name_elements.count() > 1:
                payee_name = name_elements.nth(1).inner_text()
            else:
                payee_name = name_elements.first.inner_text()
            details.append(payee_name)
            logger.info(f"Payee Name: {payee_name}")
            
            addr1_elements = self.selected_instructions_table.locator("//label[contains(@id,'Addr1')]")
            if addr1_elements.count() > 1:
                address_line = addr1_elements.nth(1).inner_text()
            else:
                address_line = addr1_elements.first.inner_text()
            details.append(address_line)
            logger.info(f"Address Line 1: {address_line}")
            
            city_elements = self.selected_instructions_table.locator("//label[contains(@id,'City')]")
            if city_elements.count() > 1:
                city = city_elements.nth(1).inner_text()
            else:
                city = city_elements.first.inner_text()
            details.append(city)
            logger.info(f"City: {city}")
            
            state_elements = self.selected_instructions_table.locator("//label[contains(@id,'State')]")
            if state_elements.count() > 1:
                state = state_elements.nth(1).inner_text()
            else:
                state = state_elements.first.inner_text()
            details.append(state)
            logger.info(f"State: {state}")
            
            zip_elements = self.selected_instructions_table.locator("//label[contains(@id,'Zip')]")
            if zip_elements.count() > 1:
                zip_code = zip_elements.nth(1).inner_text()
            else:
                zip_code = zip_elements.first.inner_text()
            details.append(zip_code)
            logger.info(f"Zip: {zip_code}")
            
            details.append(sloa_option)
            logger.info(f"SLOA Option: {sloa_option}")
            
            logger.info("[OK] Successfully fetched all Check payee details")
            
        except Exception as e:
            logger.error(f"Failed to fetch Check details: {str(e)}")
            raise
        
        return details
    
    def click_continue(self, sloa_option: str):
        """
        Click continue button in Withdrawal Method Modal
        
        Args:
            sloa_option: "Yes" navigates to MIMO page, "No" navigates to DocuSign
        """
        logger.info(f"Clicking continue button with SLOA option: {sloa_option}")
        
        self.continue_button.wait_for(state='visible', timeout=10000)
        self.continue_button.click()
        logger.info("[OK] Continue button clicked")
        
        self.page.wait_for_timeout(1000)
        
        if sloa_option.upper() == "YES":
            logger.info("Expected navigation: MIMO Transaction Request Page")
        else:
            logger.info("Expected navigation: DocuSign Page")
