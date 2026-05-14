"""
DM Tool Address Edit Modal Page Object
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import setup_logger

if TYPE_CHECKING:
    from pages.dm_tool_usps_modal import DMToolUSPSModal

logger = setup_logger(__name__)


class DMToolAddressEditModal(BasePage):
    """Page object for DM Tool Address Edit Modal"""
    
    PAGE_NAME = "DM Tool Address Edit Modal"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Modal elements
        self.modal_title = "//h2[contains(text(),'Edit Address')]"
        self.modal_container = "//div[@role='dialog']"
        self.modal_title_text = "//div[@data-testid='form-name']//h2"
        self.place_to_click_outside = "//div[@data-testid='form-name']//h2"
        self.no_po_text = ".form-warning h3"
        
        # Div sections (matching Java)
        self.address_line_div = "//div[@data-testid='addressLine1Div']"
        self.address_line_optional_div = "//div[@data-testid='addressLine2Div']"
        self.city_div = "//div[@data-testid='cityDiv']"
        self.state_div = "//div[@aria-label='form-select-item']"
        self.zip_div = "//div[@data-testid='zipCodeDiv']"
        self.extension_div = "//div[@data-testid='extensionDiv']"
        
        # Form input fields (matching Java implementation)
        self.street_input = "//div[@aria-label='form-input-item']//input[@name='addressLine1']"
        self.street2_input = "//div[@aria-label='form-input-item']//input[@name='addressLine2']"
        self.city_input = "//div[@aria-label='form-input-item']//input[@name='city']"
        self.state_dropdown = "//div[@aria-label='form-select-item']//select"
        self.zip_input = "//div[@aria-label='form-input-item']//input[@name='zipCode']"
        self.zip_extension_input = "//div[@aria-label='form-input-item']//input[@name='extension']"
        
        # Label texts (matching Java)
        self.address_line_text = "//div[@aria-label='form-input-item']//label[@for='addressLine1']"
        self.address_line_optional_text = "//div[@aria-label='form-input-item']//label[@for='addressLine2']"
        self.city_text = "//div[@aria-label='form-input-item']//label[@for='city']"
        self.state_text = "//div[@aria-label='form-select-item']//label[@for='state']"
        self.zip_text = "//div[@aria-label='form-input-item']//label[@for='zipCode']"
        self.extension_text = "[for='extension']"
        
        # PO Box checkbox (matching Java)
        self.po_box_checkbox = "//span[@aria-label='checkbox']"
        self.po_box_checkbox_ios = "[type='checkbox']"
        
        # Error message elements (matching Java)
        self.update_error_text = "//span[@aria-label='error-message']"
        
        # Action buttons (matching Java)
        self.next_button = "//div[@role='presentation']/div[3]//form//button[2]"
        self.cancel_button = "//div[@role='presentation']/div[3]//form//button[1]"
        self.back_button = "//button[text()='Back']"
        
        # Static test data (matching Java)
        self.RANDOM_ADDRESS = "300 Memorial Drive"
        self.RANDOM_CITY = "Avon"
        self.RANDOM_ZIP = "02322"
        self.RANDOM_STATE = "MA"
        self.RANDOM_EXTENSION = "1919"
        
        self.zip_pattern = "^\\d{5}"
        self.extension_pattern = "^\\d{4}"
        self.contains_letter = ".*[a-zA-Z].*"
        
        self.ERROR_PO = "Legal Address cannot be a P.O. BOX"
        
    def wait_for_modal_to_load(self) -> None:
        """Wait for Address Edit Modal to be visible"""
        logger.info("Waiting for Address Edit Modal to load")
        try:
            self.page.wait_for_selector(self.modal_container, timeout=10000)
            self.page.wait_for_selector(self.modal_title, timeout=10000)
            logger.info("[OK] Address Edit Modal loaded")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            logger.error(f"Error waiting for modal: {e}")
            raise
    
    def click_po_box_checkbox(self) -> None:
        """Click the 'Set as Mailing Address' checkbox - clean implementation"""
        logger.info("Clicking PO Box checkbox")
        
        try:
            # Wait for checkbox to be visible
            checkbox = self.page.locator(self.po_box_checkbox)
            checkbox.wait_for(state='visible', timeout=10000)
            
            # Click the checkbox
            checkbox.click()
            logger.info("[OK] PO Box checkbox clicked")
            
            # Small wait for UI to settle
            self.page.wait_for_timeout(500)
            
        except Exception as e:
            logger.error(f"Error clicking PO Box checkbox: {e}")
            raise
    
    def perform_field_error_tests(self, display_only_mailing_address: bool) -> None:

        self.click_out_required_test("Edit Modal", "Checking if error appears when clicking outside")
        self.all_empty_required_test("Edit Modal", "Checking if errors appear when empty fields", display_only_mailing_address)
        self.clear_all_address_change_inputs("Edit Modal " , " Clearing all inputs")
        self.zip_required_test("Edit Modal " , " Checking if zip error appears when it is empty",display_only_mailing_address)
        self.verify_dropdown_acts_correctly("Edit Modal " , " Checking if drop-down works correctly")
        self.check_zip_rules("Edit Modal " , "  Checking for Zip errors")
        self.check_extension_rules("Edit Modal " , " Checking for Extension errors")

    def click_out_required_test(self, step_name: str, log_message: str) -> None:
        logger.info(f"{step_name}: {log_message}")

        outside = self.page.locator(self.place_to_click_outside)

        elements = [
            self.page.locator(self.address_line_div),
            self.page.locator(self.city_div),
            self.page.locator(self.state_div),
            self.page.locator(self.zip_div),
        ]

        field_names = ["Street Address", "City", "State", "ZIP Code"]
        failed_fields = []

        for element, field_name in zip(elements, field_names):
            element.click()
            logger.info(f"Clicked {field_name} field")
            self.page.wait_for_timeout(1000)

            outside.click()
            logger.info(f"Clicked outside to trigger {field_name} validation")
            self.page.wait_for_timeout(1000)

            if not self.is_error_present(element):
                logger.error(f"{field_name}: Validation error NOT present")
                failed_fields.append(field_name)
            else:
                logger.info(f"{field_name}: Validation error present")

        if failed_fields:
            error_msg = f"{step_name}: {log_message} - Validation FAILED for fields: {', '.join(failed_fields)}"
            logger.error(error_msg)
            assert False, error_msg

        logger.info(f"{step_name}: All required field validations passed")
    
    def is_error_present(self, field_div_locator) -> bool:
        ERROR_ENTRY = "Invalid entry"
        ERROR_REQUIRED = "Required field"
        
        try:
            page_content = self.page.content().lower()
            if ERROR_ENTRY.lower() in page_content or ERROR_REQUIRED.lower() in page_content:
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def all_empty_required_test(self, step_name: str, log_message: str, display_only_mailing_address: bool) -> None:
        logger.info(f"{step_name}: {log_message}")
        
        street_element = self.page.locator(self.address_line_div)
        street_element2 = self.page.locator(self.address_line_optional_div)
        city_element = self.page.locator(self.city_div)
        state_element = self.page.locator(self.state_div)
        zip_element = self.page.locator(self.zip_div)
        
        address = self.page.locator(self.street_input)
        address2 = self.page.locator(self.street2_input)
        
        address.fill("Text")
        self.click_next()
        self.check_error_appeared(city_element, "City", display_only_mailing_address)
        self.check_error_appeared(state_element, "State", display_only_mailing_address)
        self.check_error_appeared(zip_element, "Zip", display_only_mailing_address)
        
        self.clean_input(address)
        self.click_next()
        self.check_error_appeared(street_element, "Street address", display_only_mailing_address)
        
        address.fill("Text")
        self.check_error_disappears(street_element, "Street address", display_only_mailing_address)
        
        address.fill("sdfghfgrweasdfhgfesrtdgjtewyasrdhretsrydtreaysd")
        self.click_next()
        self.check_error_appeared(street_element, "Street address", display_only_mailing_address)
        
        self.clean_input(address)
        address.fill("Text")
        self.click_next()
        self.check_error_disappears(street_element, "Street address", display_only_mailing_address)
        
        self.clean_input(address2)
        address2.fill("sdfghfgrweasdfhgfesrtdgjtewyasrdhretsrydtreaysd")
        self.click_next()
        self.check_error_appeared(street_element2, "Street address", display_only_mailing_address)
        
        self.clean_input(address2)
        address2.fill("Text")
        self.click_next()
        self.check_error_disappears(street_element2, "Street address", display_only_mailing_address)
        
        self.clean_input(self.page.locator(self.city_input))
        self.page.locator(self.city_input).fill("sdfghfgrweasdfhgfesrtdgjtewyasrdhretsrydtreaysd")
        self.click_next()
        self.check_error_appeared(city_element, "City", display_only_mailing_address)
        
        self.clean_input(self.page.locator(self.city_input))
        self.page.locator(self.city_input).fill("Text")
        self.click_next()
        self.check_error_disappears(city_element, "City", display_only_mailing_address)
        
        self.populate_dropdown("CA")
        self.check_error_disappears(state_element, "State", display_only_mailing_address)
    
    def check_error_appeared(self, element, element_name: str, display_only_mailing_address: bool) -> None:
        ERROR_ENTRY = "Invalid entry"
        ERROR_REQUIRED = "Required field"
        ERROR_CHARACTER_LIMIT1 = "Address Line 1 cannot exceed 30 characters."
        ERROR_CHARACTER_LIMIT2 = "Address Line 2 cannot exceed 30 characters."
        ERROR_CHARACTER_LIMIT_CITY = "City cannot exceed 16 characters."
        
        element_source = element.evaluate("el => el.outerHTML")
        
        if display_only_mailing_address == False:
            if ERROR_ENTRY in element_source or ERROR_REQUIRED in element_source or ERROR_CHARACTER_LIMIT1 in element_source or ERROR_CHARACTER_LIMIT2 in element_source or ERROR_CHARACTER_LIMIT_CITY in element_source:
                logger.info(f"{self.PAGE_NAME} Error appeared on {element_name} input : Verification PASSED")
            else:
                logger.info(f"{self.PAGE_NAME} : Error appeared on {element_name} input Verification FAILED")
                assert False, f"{self.PAGE_NAME} : Error appeared on {element_name} input Verification FAILED"
        else:
            if ERROR_ENTRY in element_source or ERROR_REQUIRED in element_source or ERROR_CHARACTER_LIMIT1 in element_source or ERROR_CHARACTER_LIMIT2 in element_source or ERROR_CHARACTER_LIMIT_CITY in element_source:
                logger.info(f"{self.PAGE_NAME} Error appeared on {element_name} input : Verification PASSED")
            else:
                logger.info(f"{self.PAGE_NAME} : Error appeared on {element_name} input Verification FAILED")
                assert False, f"{self.PAGE_NAME} : Error appeared on {element_name} input Verification FAILED"
    
    def check_error_disappears(self, element, element_name: str, display_only_mailing_address: bool) -> None:
        ERROR_ENTRY = "Invalid entry"
        ERROR_REQUIRED = "Required field"
        ERROR_CHARACTER_LIMIT1 = "Address Line 1 cannot exceed 30 characters."
        ERROR_CHARACTER_LIMIT2 = "Address Line 2 cannot exceed 30 characters."
        ERROR_CHARACTER_LIMIT_CITY = "City cannot exceed 16 characters."
        
        element_source = element.evaluate("el => el.outerHTML")
        
        if display_only_mailing_address == False:
            if ERROR_ENTRY not in element_source and ERROR_REQUIRED not in element_source and ERROR_CHARACTER_LIMIT1 not in element_source and ERROR_CHARACTER_LIMIT2 not in element_source and ERROR_CHARACTER_LIMIT_CITY not in element_source:
                logger.info(f"{self.PAGE_NAME} Error disappeared on {element_name} input : Verification PASSED")
            else:
                logger.info(f"{self.PAGE_NAME} : Error disappeared {element_name} input Verification FAILED")
                assert False, f"{self.PAGE_NAME} : Error disappeared {element_name} input Verification FAILED"
        else:
            if ERROR_ENTRY not in element_source and ERROR_REQUIRED not in element_source and ERROR_CHARACTER_LIMIT1 not in element_source and ERROR_CHARACTER_LIMIT2 not in element_source and ERROR_CHARACTER_LIMIT_CITY not in element_source:
                logger.info(f"{self.PAGE_NAME} Error disappeared on {element_name} input : Verification PASSED")
            else:
                logger.info(f"{self.PAGE_NAME} : Error disappeared {element_name} input Verification FAILED")
                assert False, f"{self.PAGE_NAME} : Error disappeared {element_name} input Verification FAILED"
    
    def clean_input(self, element) -> None:
        element.click()
        element.clear()
        input_text = element.input_value()
        if input_text is not None:
            for i in range(len(input_text)):
                element.press("Backspace")
        element.fill(" ")
    
    def clear_all_address_change_inputs(self, step_name: str, log_message: str) -> None:
        self.clean_input(self.page.locator(self.street_input))
        self.clean_input(self.page.locator(self.street2_input))
        self.clean_input(self.page.locator(self.city_input))
        self.clean_input(self.page.locator(self.zip_extension_input))
        self.clean_input(self.page.locator(self.zip_input))
    
    def populate_dropdown(self, value: str) -> None:
        self.page.locator(self.state_dropdown).select_option(value)
    
    def zip_required_test(self, step_name: str, log_message: str, display_only_mailing_address: bool) -> None:
        zip_element = self.page.locator(self.zip_div)
        self.clean_input(self.page.locator(self.zip_input))
        self.click_next()
        self.check_error_appeared(zip_element, "Zip", display_only_mailing_address)
        self.page.locator(self.zip_input).fill(self.RANDOM_ZIP)
        self.check_error_disappears(zip_element, "Zip", display_only_mailing_address)
    
    def verify_dropdown_acts_correctly(self, step_name: str, log_message: str) -> None:
        dropdown = self.page.locator(self.state_dropdown)
        first_letters = []
        dropdown.click()
        options = dropdown.locator("option").all()
        for option in options:
            text = option.text_content()
            if text != "":
                first_letters.append(text)
        if self.check_if_in_alphabetic_order("", first_letters):
            logger.info(f"{self.PAGE_NAME} State drop-down elements are in alphabetical order : verification PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : State drop-down elements are in alphabetical order verification FAILED")
            assert False, f"{self.PAGE_NAME} : State drop-down elements are in alphabetical order verification FAILED"
        dropdown.select_option("CA")
    
    def check_if_in_alphabetic_order(self, prefix: str, items: list) -> bool:
        sorted_items = sorted(items)
        return items == sorted_items
    
    def check_zip_rules(self, step_name: str, log_message: str) -> None:
        import re
        fail = False
        zip_input = self.page.locator(self.zip_input)
        zip_div_el = self.page.locator(self.zip_div)
        
        self.clean_input(zip_input)
        zip_input.fill("123456")
        if re.match(self.zip_pattern, zip_input.input_value()):
            logger.info(f"{self.PAGE_NAME} Zip code input can not be longer than 5 : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Zip code input can not be longer than 5 verification is FAILED")
            fail = True
        
        self.clean_input(zip_input)
        zip_input.fill("DFKL")
        if not re.match(self.contains_letter, zip_input.input_value()):
            logger.info(f"{self.PAGE_NAME} Zip code input can not have letters : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Zip code input can not have letters verification is FAILED")
            fail = True
        
        self.clean_input(zip_input)
        zip_input.fill("1234")
        self.click_next()
        if self.is_error_present(zip_div_el):
            logger.info(f"{self.PAGE_NAME} Zip code input can not be too short : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Zip code input can not be too short verification is FAILED")
            fail = True
        
        self.clean_input(self.page.locator(self.zip_input))
        self.page.locator(self.zip_input).fill("14444++++55")
        if re.match(self.zip_pattern, self.page.locator(self.zip_input).input_value()):
            logger.info(f"{self.PAGE_NAME} Zip code input can not be have longer input with ++ hack : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Zip code input can not be have longer input with ++ hack verification is FAILED")
            fail = True
        
        if not fail:
            logger.info(f"{self.PAGE_NAME} Zip code rules : verification is PASSED")
        else:
            assert fail == False, f"{self.PAGE_NAME} --> Zip code rules : verification is FAILED"
    
    def check_extension_rules(self, step_name: str, log_message: str) -> None:
        import re
        fail = False
        extension_div_el = self.page.locator(self.extension_div)
        extension = self.page.locator(self.zip_extension_input)
        
        extension.fill("123456")
        extension.click()
        if re.match(self.extension_pattern, self.page.locator(self.zip_extension_input).input_value()):
            logger.info(f"{self.PAGE_NAME} Extension input can not be longer than 4 : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Extension input can not be longer than 4 verification is FAILED")
            fail = True
        
        self.clean_input(extension)
        extension.fill("5F4D66")
        self.click_next()
        if not re.match(self.contains_letter, self.page.locator(self.zip_extension_input).input_value()):
            logger.info(f"{self.PAGE_NAME} Extension input can not have letters : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Extension input can not have letters verification is FAILED")
            fail = True
        
        self.clean_input(extension)
        extension.fill("124")
        self.click_next()
        if self.is_error_present(extension_div_el):
            logger.info(f"{self.PAGE_NAME} Extension input can not be too short : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Extension input can not be too short verification is FAILED")
            fail = True
        
        if not fail:
            logger.info(f"{self.PAGE_NAME} Extension code rules : verification is PASSED")
        
        self.clean_input(extension)
        extension.fill("1234++665")
        if re.match(self.extension_pattern, self.page.locator(self.zip_extension_input).input_value()):
            logger.info(f"{self.PAGE_NAME} Extension input can not have longer inputs via ++ hack : verification is PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : Extension input can not have longer inputs via ++ hack verification is FAILED")
            fail = True
        
        if fail:
            logger.info(f"{self.PAGE_NAME} Extension code rules : verification is PASSED")
            assert False, f"{self.PAGE_NAME} --> Extension code rules : verification is FAILED"
        else:
            logger.info(f"{self.PAGE_NAME} Extension code rules : verification is PASSED")
    
    def perform_po_test(self) -> None:
        self.populate_all_address_change_inputs_simple()
        pos = ["BOX"]
        for po in pos:
            self.clean_only_addresses("Edit Modal", "Clearing address inputs")
            self.populate_only_addresses("Edit Model", "Populating address inputs", po, po)
            self.click_next()
            self.po_error_test("Edit Modal", "Checking if PO error appeared", po)
        self.clear_all_address_change_inputs("Edit Modal", "Clearing all inputs")
    
    def populate_all_address_change_inputs_simple(self) -> None:
        self.page.locator(self.street_input).fill(self.RANDOM_ADDRESS)
        self.page.locator(self.city_input).fill(self.RANDOM_CITY)
        self.populate_dropdown(self.RANDOM_STATE)
        self.page.locator(self.zip_input).fill(self.RANDOM_ZIP)
        self.page.locator(self.zip_extension_input).fill(self.RANDOM_EXTENSION)
    
    def clean_only_addresses(self, step_name: str, log_message: str) -> None:
        self.clean_input(self.page.locator(self.street_input))
        self.clean_input(self.page.locator(self.street2_input))
    
    def populate_only_addresses(self, step_name: str, log_message: str, address: str, address_opt: str) -> None:
        self.page.locator(self.street_input).fill(address)
        self.page.locator(self.street2_input).fill(address_opt)
    
    def po_error_test(self, step_name: str, log_message: str, po: str) -> None:
        addr1_src_contains_error = self.does_element_contain_text(self.page.locator(self.address_line_div), self.ERROR_PO)
        addr2_src_contains_error = self.does_element_contain_text(self.page.locator(self.address_line_optional_div), self.ERROR_PO)
        if addr1_src_contains_error and addr2_src_contains_error:
            logger.info(f"{self.PAGE_NAME} : {self.ERROR_PO} Displayed on both inputs verification when entered {po} PASSED")
        else:
            logger.info(f"{self.PAGE_NAME} : {self.ERROR_PO} Displayed on both inputs verification when entered {po} FAILED")
            assert False, f"{self.PAGE_NAME} : {self.ERROR_PO} Displayed on both inputs verification when entered {po} FAILED"
    
    def does_element_contain_text(self, element, text: str) -> bool:
        element_html = element.evaluate("el => el.outerHTML")
        return text in element_html
    
    def click_checkbox(self, step_name: str, log_message: str, browser: str) -> None:
        logger.info(f"{step_name} : {log_message}")
        checkbox = self.page.locator(self.po_box_checkbox)
        checkbox.wait_for(state='visible', timeout=10000)
        checkbox.click()

    
    def populate_all_address_change_inputs(self,
                                           street: str,
                                           street_optional: str,
                                           city: str,
                                           state: str,
                                           zip_code: str,
                                           extension: str = "") -> None:
        logger.info("Populating address change inputs")
        logger.info(f"Address: {street}, {street_optional}, {city}, {state} {zip_code}-{extension}")
        
        logger.info(f"Filling street: {street}")
        self.page.fill(self.street_input, street)
        
        if street_optional and street_optional.strip():
            logger.info(f"Filling street2: {street_optional}")
            self.page.fill(self.street2_input, street_optional)
        
        logger.info(f"Filling city: {city}")
        self.page.fill(self.city_input, city)
        
        logger.info(f"Selecting state: {state}")
        self.page.select_option(self.state_dropdown, state)
        
        logger.info(f"Filling ZIP: {zip_code}")
        self.page.fill(self.zip_input, zip_code)
        logger.info("[OK] ZIP filled")
        
        if extension and extension.strip():
            logger.info(f"Filling ZIP extension: {extension}")
            self.page.fill(self.zip_extension_input, extension)
        
        self.page.wait_for_timeout(500)
        
        logger.info("[OK] All address inputs populated")
    
    def click_next(self) -> None:
        """Click the Next button"""
        logger.info("Clicking Next button")
        try:
            next_btn = self.page.locator(self.next_button)
            next_btn.wait_for(state='visible', timeout=5000)
            next_btn.click()
            logger.info("Next button clicked")
            self.page.wait_for_timeout(1500)
        except Exception as e:
            logger.error(f"Error clicking Next button: {e}")
            raise
    
    def navigate_to_usps_modal(self) -> 'DMToolUSPSModal':
        """Navigate to USPS address validation modal by clicking Next
        
        Returns:
            DMToolUSPSModal instance
        """
        from pages.dm_tool_usps_modal import DMToolUSPSModal
        
        logger.info("Navigating to USPS modal")
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            next_button = self.page.locator(self.next_button)
            next_button.wait_for(state='visible', timeout=10000)
            next_button.click()
            logger.info(f"{self.PAGE_NAME}: Clicking next button")
            
            address_input_invisible = self.page.locator(self.street_input).is_hidden()
            if not address_input_invisible:
                logger.warning(f"{self.PAGE_NAME}: FAILED to navigate to USPS modal")
            
            return DMToolUSPSModal(self.page)
            
        except Exception as e:
            logger.error(f"Error navigating to USPS modal: {e}")
            raise
    
    def click_cancel(self) -> None:
        """Click the Cancel button to close modal"""
        logger.info("Clicking Cancel button")
        try:
            cancel_btn = self.page.locator(self.cancel_button)
            cancel_btn.wait_for(state='visible', timeout=5000)
            cancel_btn.click()
            logger.info("Cancel button clicked")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            logger.error(f"Error clicking Cancel button: {e}")
            raise
    
    def click_back(self) -> None:
        """Click the Back button"""
        logger.info("Clicking Back button")
        try:
            back_btn = self.page.locator(self.back_button)
            back_btn.wait_for(state='visible', timeout=5000)
            back_btn.click()
            logger.info("Back button clicked")
            self.page.wait_for_timeout(1000)
        except Exception as e:
            logger.error(f"Error clicking Back button: {e}")
            raise
