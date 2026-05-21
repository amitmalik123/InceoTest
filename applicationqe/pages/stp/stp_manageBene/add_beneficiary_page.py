from typing import Union, List
from datetime import datetime
from playwright.sync_api import Locator, Page, FrameLocator

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_manageBene.locators.add_beneficiary_locators import AddBeneficiaryLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AddBeneficiaryPage(BasePage):

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        loc = AddBeneficiaryLocators
        
        self.dont_save_button: Locator = context.get_by_role("button", name=loc.DONT_SAVE_BUTTON)
        self.save_button: Locator = context.locator(loc.SAVE_BUTTON)
        
        self.add_beneficiary_title: Locator = context.locator(loc.ADD_BENEFICIARY_TITLE)
        
        self.beneficiary_dropdown: Locator = context.locator(loc.BENEFICIARY_DROPDOWN).first
        self.beneficiary_dropdown_menu: Locator = context.locator(loc.BENEFICIARY_DROPDOWN_MENU)
        
        self.beneficiary_heading: Locator = context.locator(loc.BENEFICIARY_HEADING)
        
        self.first_name_input: Locator = context.locator(loc.FIRST_NAME_INPUT)
        self.last_name_input: Locator = context.locator(loc.LAST_NAME_INPUT)
        self.ssn_input: Locator = context.locator(loc.SSN_INPUT)
        self.dob_input: Locator = context.locator(loc.DOB_INPUT)
        
        self.name_input: Locator = context.locator(loc.NAME_INPUT)
        self.date_of_trust_input: Locator = context.locator(loc.DATE_OF_TRUST_INPUT)
        
        self.taxIdDropdown: Locator = context.locator(loc.TAX_ID_DROPDOWN)
        self.taxIdInput: Locator = context.locator(loc.TAX_ID_INPUT)
        
        self.tinInput: Locator = context.locator(loc.TIN_INPUT)
        
        self.spouse_radio: Locator = context.locator(loc.SPOUSE_RADIO)
        self.non_spouse_radio: Locator = context.locator(loc.NON_SPOUSE_RADIO)
        self.trust_radio: Locator = context.locator(loc.TRUST_RADIO)
        self.entity_radio: Locator = context.locator(loc.ENTITY_RADIO)
        
        self.account_selection_box: Locator = context.locator(loc.ACCOUNT_SELECTION_BOX)
        self.account_checkboxes: Locator = context.locator(loc.ACCOUNT_CHECKBOXES)
        self.per_stirpes_checkbox: Locator = context.locator(loc.PER_STIRPES_CHECKBOX).first
        self.first_account_checkbox: Locator = context.locator(loc.FIRST_ACCOUNT_CHECKBOX)
        self.account_boxes: Locator = context.locator(loc.ACCOUNT_BOXES)
        
        self.modal_header: Locator = context.locator(loc.MODAL_HEADER)
        
        self.error_messages: Locator = context.locator(loc.ERROR_MESSAGES)
        
        self.first_name_error: Locator = context.locator(loc.FIRST_NAME_ERROR)
        self.last_name_error: Locator = context.locator(loc.LAST_NAME_ERROR)
        self.name_error: Locator = context.locator(loc.NAME_ERROR)
        self.account_selection_error: Locator = context.locator(loc.ACCOUNT_SELECTION_ERROR)
        
        self.confirmation_modal: Locator = context.locator(loc.CONFIRMATION_MODAL)
        self.confirm_button: Locator = context.locator(loc.CONFIRM_BUTTON)
        
        self.tooltip: Locator = context.locator(loc.TOOLTIP)
        
        self.calendar_icon_button: Locator = context.get_by_role("button", name=loc.CALENDAR_CHOOSE_DATE)
        self.calendar_grid: Locator = context.locator(loc.CALENDAR_GRID)
        self.calendar_month_label: Locator = context.locator(loc.CALENDAR_MONTH_LABEL)
        self.calendar_next_month_button: Locator = context.locator(loc.CALENDAR_NEXT_MONTH_BUTTON)
        self.calendar_previous_month_button: Locator = context.locator(loc.CALENDAR_PREVIOUS_MONTH_BUTTON)
        self.calendar_date_buttons: Locator = context.locator("button[role='gridcell']")

    def click_dont_save_button(self) -> None:
        
        logger.info("Clicking 'Don't Save' button")
        self.dont_save_button.wait_for(state="visible", timeout=5000)
        self.dont_save_button.click()
        logger.info("[OK] 'Don't Save' button clicked successfully")

    def click_save_button(self) -> None:
        
        logger.info("Clicking 'Save' button")
        
        self.save_button.wait_for(state="visible", timeout=10000)
        self.save_button.scroll_into_view_if_needed()
        self.save_button.wait_for(state="attached", timeout=5000)
        self.save_button.click(timeout=10000)
        logger.info("[OK] 'Save' button clicked successfully")

    def is_add_beneficiary_title_visible(self) -> bool:
        
        logger.info("Checking if 'Add a Beneficiary' title is visible")
        is_visible = self.add_beneficiary_title.is_visible()
        logger.info(f"'Add a Beneficiary' title visible: {is_visible}")
        return is_visible

    def get_add_beneficiary_title_text(self) -> str:
        
        logger.info("Getting 'Add a Beneficiary' title text")
        self.add_beneficiary_title.wait_for(state="visible", timeout=5000)
        title_text = self.add_beneficiary_title.inner_text()
        logger.info(f"Title text: {title_text}")
        return title_text

    def select_beneficiary_from_dropdown(self, beneficiary_name: str = "New") -> None:
        
        logger.info(f"Clicking beneficiary dropdown to select: {beneficiary_name}")
        
        self.beneficiary_dropdown.click()
        logger.info("Beneficiary dropdown opened")
        
        self.beneficiary_dropdown_menu.wait_for(state="visible", timeout=5000)
        
        data_value = beneficiary_name.lower()
        option = self.context.locator(f"li[role='option'][data-value='{data_value}']")
        option.wait_for(state="visible", timeout=3000)
        option.click()
        
        logger.info(f"[OK] Selected '{beneficiary_name}' from beneficiary dropdown")
    
    def select_beneficiary_type_as(self, bene_type: str) -> None:
        
        logger.info(f"Selecting beneficiary type: {bene_type}")
        self.select_beneficiary_from_dropdown(bene_type)
        logger.info(f"[OK] Beneficiary type '{bene_type}' selected successfully")

    def select_existing_beneficiary_by_name(self, name: str) -> str:
        """Open the beneficiary dropdown and select the option matching `name` exactly.

        XPath axis used:
          //ul[@role='listbox']
            /descendant::li[@role='option']
              [normalize-space()='{name}']
        Navigates from the listbox container down through all descendant option items
        to the one whose visible text equals the requested beneficiary name.
        """
        logger.info(f"Opening beneficiary dropdown to select option matching: '{name}'")
        self.beneficiary_dropdown.click()
        self.beneficiary_dropdown_menu.wait_for(state="visible", timeout=5000)

        xpath = (
            f"//ul[@role='listbox']"
            f"/descendant::li[@role='option'][normalize-space()='{name}']"
        )
        option = self.context.locator(f"xpath={xpath}")
        option.wait_for(state="visible", timeout=5000)
        display_name = option.inner_text().strip()
        option.click()

        logger.info(f"[OK] Selected existing beneficiary by name: '{display_name}'")
        return display_name

    def select_first_existing_beneficiary(self) -> str:
        
        logger.info("Opening beneficiary dropdown to select first existing beneficiary")
        self.beneficiary_dropdown.click()
        self.beneficiary_dropdown_menu.wait_for(state="visible", timeout=5000)

        existing_option = self.context.locator("li[role='option']:not([data-value='new'])").first
        existing_option.wait_for(state="visible", timeout=5000)

        bene_name = existing_option.inner_text().strip()
        logger.info(f"Found existing beneficiary: {bene_name}")
        existing_option.click()

        logger.info(f"[OK] Selected existing beneficiary: {bene_name}")
        return bene_name

    def verify_existing_beneficiary_fields_disabled(self, relation: str = 'Spouse') -> dict:
        
        logger.info(f"Verifying personal fields disabled for existing beneficiary (relation={relation})")

        relation_lower = relation.lower()
        if relation_lower in ('trust', 'entity'):
            # Trust/Entity: single Name field
            name_field = self.context.locator("xpath=//p[text()='Name']/following-sibling::div//input")
            name_field.wait_for(state="attached", timeout=10000)
            results = {'name': name_field.is_disabled()}
        else:
            # Spouse / Non-Spouse: First Name, Last Name, SSN, DOB
            self.first_name_input.wait_for(state="attached", timeout=10000)
            results = {
                'first_name': self.first_name_input.is_disabled(),
                'last_name': self.last_name_input.is_disabled(),
                'ssn': self.ssn_input.is_disabled(),
                'dob': self.dob_input.is_disabled(),
            }

        logger.info(f"Field disabled status: {results}")
        return results

    def select_designation_as(self, relation: str) -> None:
        
        logger.info(f"Selecting relationship type: {relation}")
        
        radio_map = {
            "spouse": self.spouse_radio,
            "non-spouse": self.non_spouse_radio,
            "trust": self.trust_radio,
            "entity": self.entity_radio
        }
        
        relation_key = relation.lower()
        if relation_key not in radio_map:
            raise ValueError(f"Invalid relationship type: {relation}. Must be one of: Spouse, Non-Spouse, Trust, Entity")
        
        radio_button = radio_map[relation_key]
        
        if not radio_button.is_checked():
            logger.info(f"  - Radio button for '{relation}' not checked, clicking now")
            radio_button.click()
        else:
            logger.info(f"  - Radio button for '{relation}' already checked, skipping click")
        
        logger.info(f"[OK] Relationship type '{relation}' selected successfully")
    
    def validate_beneficiary_heading(self, expected_text: str = "Beneficiary") -> bool:
        
        logger.info(f"Validating beneficiary heading: {expected_text}")
        actual_text = self.get_beneficiary_heading_text()
        is_valid = expected_text in actual_text
        logger.info(f"Heading validation result: {is_valid}")
        return is_valid
    
    def get_beneficiary_heading_text(self) -> str:
        
        self.beneficiary_heading.wait_for(state="visible", timeout=5000)
        heading_text = self.beneficiary_heading.inner_text()
        logger.info(f"Beneficiary heading text: {heading_text}")
        return heading_text
    
    def enter_first_name(self, first_name: str) -> None:
        
        logger.info(f"Entering first name: {first_name}")
        self.first_name_input.fill(first_name)
        logger.info(f"[OK] First name entered: {first_name}")
    
    def enter_last_name(self, last_name: str) -> None:
       
        logger.info(f"Entering last name: {last_name}")
        self.last_name_input.fill(last_name)
        logger.info(f"[OK] Last name entered: {last_name}")
    
    def enter_social_security_number(self, ssn: str) -> None:
       
        logger.info(f"Entering SSN: {ssn[:3]}-**-{ssn[-4:]}")
        self.ssn_input.fill(ssn)
        logger.info("[OK] SSN entered")
    
    def enter_date_of_birth(self, dob: str) -> None:
        
        logger.info(f"Entering date of birth: {dob}")
        self.dob_input.fill(dob)
        logger.info(f"[OK] Date of birth entered: {dob}")
    
    def enter_name(self, name: str) -> None:
       
        logger.info(f"Entering name: {name}")
        self.name_input.fill(name)
        logger.info(f"[OK] Name entered: {name}")
    
    def enter_date_of_trust(self, date: str) -> None:
       
        logger.info(f"Entering date of trust: {date}")
        self.date_of_trust_input.fill(date)
        logger.info(f"[OK] Date of trust entered: {date}")
    
    def selectTaxIdType(self, optionText: str) -> None:
       
        logger.info(f"Selecting Tax ID type: {optionText}")
        self.taxIdDropdown.scroll_into_view_if_needed()
        self.taxIdDropdown.click()
        
        optionXpath = f"//li[normalize-space()='{optionText}']"
        option = self.context.locator(f"xpath={optionXpath}")
        option.wait_for(state="visible", timeout=5000)
        option.click()
        
        logger.info(f"[OK] Tax ID type selected: {optionText}")
    
    def enterTaxIdValue(self, taxId: str) -> None:
        
        logger.info(f"Entering Tax ID value: {taxId[:3]}-**-{taxId[-4:]}")
        self.taxIdInput.scroll_into_view_if_needed()
        self.taxIdInput.fill(taxId)
        logger.info("[OK] Tax ID value entered")
    
    def enterTinValue(self, tin: str) -> None:
       
        logger.info(f"Entering TIN value: {tin[:2]}-**-{tin[-4:]}")
        self.tinInput.scroll_into_view_if_needed()
        self.tinInput.fill(tin)
        logger.info("[OK] TIN value entered")

    def select_account_by_name(self, account_name: str, should_select: bool = True) -> None:
       
        action = "Selecting" if should_select else "Deselecting"
        logger.info(f"{action} account containing '{account_name}'")
        
        xpath = f"//div[contains(text(), '{account_name}')]/ancestor::div[contains(@class, 'MuiCardContent-root')]//input[@type='checkbox']"
        account_checkbox = self.page.locator(f"xpath={xpath}")
        
        account_checkbox.wait_for(state="visible", timeout=5000)
        
        account_checkbox.scroll_into_view_if_needed()
        logger.info(f"Scrolled to account checkbox for '{account_name}'")
        
        is_currently_checked = account_checkbox.is_checked()
        logger.info(f"Account checkbox current state: {'checked' if is_currently_checked else 'unchecked'}")
        
        if should_select and not is_currently_checked:
            account_checkbox.check()
            logger.info(f"[OK] Account '{account_name}' checkbox checked")
        elif not should_select and is_currently_checked:
            account_checkbox.uncheck()
            logger.info(f"[OK] Account '{account_name}' checkbox unchecked")
        else:
            logger.info(f"Account '{account_name}' checkbox already in desired state, no action needed")

    def select_designation_for_account(self, account_name: str, designation: str) -> None:
       
        logger.info(f"Selecting '{designation}' designation for account containing '{account_name}'")
        
        if designation not in ["Primary", "Contingent"]:
            raise ValueError(f"Invalid designation '{designation}'. Must be 'Primary' or 'Contingent'")
        
        xpath = f"//div[contains(text(), '{account_name}')]/ancestor::div[contains(@class, 'MuiCardContent-root')]//input[@type='radio'][@value='{designation}']"
        radio_button = self.page.locator(f"xpath={xpath}")
        
        radio_button.wait_for(state="visible", timeout=5000)
        
        radio_button.scroll_into_view_if_needed()
        logger.info(f"Scrolled to radio button '{designation}' for '{account_name}'")
        
        is_disabled = radio_button.is_disabled()
        if is_disabled:
            logger.warning(f"Radio button '{designation}' for account '{account_name}' is disabled, cannot select")
            return
        
        is_currently_checked = radio_button.is_checked()
        logger.info(f"Radio button '{designation}' current state: {'checked' if is_currently_checked else 'unchecked'}")
        
        if not is_currently_checked:
            radio_button.check()
            logger.info(f"[OK] '{designation}' designation selected for account '{account_name}'")
        else:
            logger.info(f"'{designation}' designation already selected for account '{account_name}', no action needed")

    def selectAtLeastOneAccountForBeneficiary(self) -> None:
        """Select the first available account for beneficiary."""
        logger.info("Selecting at least one account for beneficiary")
        
        self.first_account_checkbox.scroll_into_view_if_needed()
        logger.info("Scrolled to first account checkbox")
        
        self.first_account_checkbox.check()
        logger.info("Account selected successfully")

    def click_per_stirpes_checkbox(self) -> None:
        """Click the Per Stirpes checkbox input."""
        logger.info("Clicking Per Stirpes checkbox")

        self.per_stirpes_checkbox.wait_for(state="attached", timeout=10000)
        self.per_stirpes_checkbox.scroll_into_view_if_needed()
        self.per_stirpes_checkbox.check(force=True)

        logger.info("[OK] Per Stirpes checkbox clicked successfully")

    def is_per_stirpes_checkbox_checked(self) -> bool:
        """Return whether the Per Stirpes checkbox is currently checked."""
        logger.info("Checking current state of Per Stirpes checkbox")

        self.per_stirpes_checkbox.wait_for(state="attached", timeout=10000)
        is_checked = self.per_stirpes_checkbox.is_checked()

        logger.info(f"Per Stirpes checkbox checked: {is_checked}")
        return is_checked

    def toggle_per_stirpes_checkbox(self) -> bool:
        """Toggle the Per Stirpes checkbox and return the new checked state."""
        logger.info("Toggling Per Stirpes checkbox")

        self.per_stirpes_checkbox.wait_for(state="attached", timeout=10000)
        self.per_stirpes_checkbox.scroll_into_view_if_needed()

        is_checked = self.per_stirpes_checkbox.is_checked()
        logger.info(f"Current Per Stirpes checkbox state: {'checked' if is_checked else 'unchecked'}")

        if is_checked:
            self.per_stirpes_checkbox.uncheck(force=True)
            logger.info("Per Stirpes checkbox was checked and is now unchecked")
        else:
            self.per_stirpes_checkbox.check(force=True)
            logger.info("Per Stirpes checkbox was unchecked and is now checked")

        new_state = self.per_stirpes_checkbox.is_checked()
        logger.info(f"[OK] Per Stirpes checkbox toggled successfully. New state: {new_state}")
        return new_state

    def select_multiple_accounts_for_beneficiary(self) -> None:
        """Select multiple accounts for beneficiary (all available)."""
        logger.info("Selecting multiple accounts for beneficiary")
        
        accounts = self.account_checkboxes.all()
        
        for account in accounts:
            account.scroll_into_view_if_needed()
            account.check()
        
        logger.info(f"Selected {len(accounts)} accounts successfully")

    def do_not_select_any_account_for_beneficiary(self) -> None:
        """Ensure no accounts are selected."""
        logger.info("Ensuring no accounts are selected")
        
        accounts = self.account_checkboxes.all()
        for account in accounts:
            account.scroll_into_view_if_needed()
            account.uncheck()
        
        logger.info("All accounts deselected")

    def select_account_by_name_with_designation(self, account_name: str, designation: str) -> None:
        
        logger.info(f"Selecting account '{account_name}' with designation '{designation}'")
        
        account_checkbox = self.context.locator(
            f"//div[contains(@class, 'MuiBox-root') and contains(text(), '{account_name}')]"
            f"/parent::div/preceding-sibling::span[contains(@class, 'MuiCheckbox-root')]"
            f"//input[@type='checkbox']"
        )
        
        account_checkbox.scroll_into_view_if_needed()
        logger.info(f"Scrolled to checkbox for account: {account_name}")
        
        account_checkbox.check()
        logger.info(f"Account checkbox selected for: {account_name}")
        
        designation_radio = self.context.locator(
            f"//div[contains(@class, 'MuiBox-root') and contains(text(), '{account_name}')]"
            f"/ancestor::div[contains(@class,'MuiCardContent-root')][1]"
            f"//input[@type='radio'][@value='{designation}'][not(@disabled)]"
        )
        
        designation_radio.scroll_into_view_if_needed()
        logger.info(f"Scrolled to {designation} radio button for account: {account_name}")
        
        designation_radio.check()
        logger.info(f"[OK] Account '{account_name}' selected with designation '{designation}'")

    def select_accounts_with_designation(self, account_index: int, designation: str) -> None:
        
        logger.info(f"Selecting account {account_index} with designation '{designation}'")

        # Target individual account cards (MuiCard-root WITHOUT a MuiCardHeader-root child).
        # The outer "Add Beneficiary to Account(s)" wrapper card has a MuiCardHeader-root,
        # so excluding it ensures the nth index maps directly to the nth account row.
        account_card = self.context.locator(
            f"(//p[normalize-space()='Add Beneficiary to Account(s)']"
            f"/parent::div"
            f"//div[contains(@class,'MuiCard-root')]"
            f"[not(./div[contains(@class,'MuiCardHeader-root')])]"
            f"[.//input[@type='radio']]"
            f")[{account_index}]"
        )

        account_checkbox = account_card.locator("input[type='checkbox']")
        account_checkbox.scroll_into_view_if_needed()
        logger.info(f"Scrolled to account {account_index} checkbox")

        # If the checkbox is already pre-checked and disabled (e.g. Trust/Entity existing bene
        # where the account was previously associated), skip checking it.
        if not account_checkbox.is_disabled():
            account_checkbox.check()
            logger.info(f"Account {account_index} checkbox selected")
        else:
            logger.info(f"Account {account_index} checkbox already pre-selected (disabled) — skipping check")

        # The designation radio may already be pre-set and disabled for existing Trust/Entity benes.
        # Only click if it is enabled; otherwise verify it already has the correct value.
        designation_radio_enabled = account_card.locator(
            f"input[type='radio'][value='{designation}']:not([disabled])"
        )
        designation_radio_any = account_card.locator(
            f"input[type='radio'][value='{designation}']"
        )

        if designation_radio_enabled.count() > 0:
            designation_radio_enabled.scroll_into_view_if_needed()
            logger.info(f"Scrolled to {designation} radio button for account {account_index}")
            designation_radio_enabled.check()
            logger.info(f"[OK] Account {account_index} designation set to '{designation}'")
        elif designation_radio_any.count() > 0 and designation_radio_any.first.is_checked():
            logger.info(
                f"Account {account_index} '{designation}' radio is already pre-selected (disabled) — skipping"
            )
        else:
            raise AssertionError(
                f"Cannot set designation '{designation}' on account {account_index}: "
                f"radio is disabled and not pre-selected with the expected value."
            )

    def is_account_selection_box_highlighted_red(self) -> bool:
        """Check if account selection box is highlighted in red."""
        logger.info("Checking if account selection box is highlighted in red")
        style = self.account_selection_box.evaluate("el => window.getComputedStyle(el).borderColor")
        is_red = "red" in str(style).lower() or "rgb(255, 0, 0)" in str(style)
        logger.info(f"Account selection box highlighted in red: {is_red}")
        return is_red

    def are_account_boxes_highlighted_red(self) -> bool:
        """Check if individual account boxes are highlighted in red."""
        logger.info("Checking if account boxes are highlighted in red")
        account_boxes = self.account_boxes.all()
        
        for box in account_boxes:
            style = box.evaluate("el => window.getComputedStyle(el).borderColor")
            if "red" not in str(style).lower() and "rgb(255, 0, 0)" not in str(style):
                return False
        
        logger.info(f"All {len(account_boxes)} account boxes highlighted in red")
        return True

    def get_error_message(self) -> str:
        
        logger.info("Retrieving error message")
        error_text = self.error_messages.first.inner_text()
        logger.info(f"Error message: {error_text}")
        return error_text

    def get_all_error_messages(self) -> List[str]:
        
        logger.info("Retrieving all error messages")
        errors = []
        error_elements = self.error_messages.all()
        for error in error_elements:
            errors.append(error.inner_text())
        logger.info(f"Found {len(errors)} error messages")
        return errors

    def get_first_name_error_message(self) -> str:
            
        logger.info("Retrieving first name error message")
        try:
            if self.first_name_error.is_visible(timeout=2000):
                error_text = self.first_name_error.inner_text()
                logger.info(f"First name error message: {error_text}")
                return error_text
            else:
                logger.info("First name error message not visible")
                return ""
        except Exception as e:
            logger.warning(f"Could not get first name error message: {e}")
            return ""

    def get_last_name_error_message(self) -> str:
        
        logger.info("Retrieving last name error message")
        try:
            if self.last_name_error.is_visible(timeout=2000):
                error_text = self.last_name_error.inner_text()
                logger.info(f"Last name error message: {error_text}")
                return error_text
            else:
                logger.info("Last name error message not visible")
                return ""
        except Exception as e:
            logger.warning(f"Could not get last name error message: {e}")
            return ""

    def get_name_error_message(self) -> str:
        """Get name field error message (for Trust/Entity)."""
        logger.info("Retrieving name error message")
        try:
            if self.name_error.is_visible(timeout=2000):
                error_text = self.name_error.inner_text()
                logger.info(f"Name error message: {error_text}")
                return error_text
            else:
                logger.info("Name error message not visible")
                return ""
        except Exception as e:
            logger.warning(f"Could not get name error message: {e}")
            return ""

    def get_account_selection_error_message(self) -> str:
        """Get account selection error message."""
        logger.info("Retrieving account selection error message")
        try:
            self.account_selection_error.wait_for(state="visible", timeout=3000)
            error_text = self.account_selection_error.inner_text()
            logger.info(f"Account selection error message: {error_text}")
            return error_text
        except Exception as e:
            logger.warning(f"Could not get account selection error message: {e}")
            return ""

    def get_tooltip_text(self) -> str:
        """Get tooltip text if displayed."""
        logger.info("Retrieving tooltip text")
        tooltip_text = self.tooltip.inner_text() if self.tooltip.is_visible() else ""
        logger.info(f"Tooltip text: {tooltip_text}")
        return tooltip_text

    def is_confirmation_modal_displayed(self) -> bool:
        """Check if confirmation modal is displayed."""
        logger.info("Checking if confirmation modal is displayed")
        is_displayed = self.confirmation_modal.is_visible() if self.confirmation_modal.count() > 0 else False
        logger.info(f"Confirmation modal displayed: {is_displayed}")
        return is_displayed

    def click_confirm_button_in_modal(self) -> None:
        """Click confirm button in confirmation modal."""
        logger.info("Clicking confirm button in modal")
        self.confirm_button.click()
        logger.info("Confirm button clicked")

    def is_modal_closed(self) -> bool:
        """Check if Add Beneficiary modal is closed."""
        logger.info("Checking if modal is closed")
        is_closed = not self.modal_header.is_visible() if self.modal_header.count() > 0 else True
        logger.info(f"Modal closed: {is_closed}")
        return is_closed

    def wait_for_modal_to_close(self, timeout: int = 10000) -> None:
        """Wait for the Add Beneficiary modal to close."""
        logger.info(f"Waiting for modal to close (timeout: {timeout}ms)")
        self.modal_header.wait_for(state="hidden", timeout=timeout)
        logger.info("Modal closed successfully")

    def clickCalendarIcon(self) -> None:
        """
        Click on the calendar icon button to open the date picker.
        Uses accessible aria-label to locate the calendar button.
        """
        logger.info("Clicking calendar icon to open date picker")
        
        self.calendar_icon_button.wait_for(state="visible", timeout=10000)
        self.calendar_icon_button.scroll_into_view_if_needed()
        self.calendar_icon_button.click()
        self.calendar_grid.wait_for(state="visible", timeout=5000)
        
        logger.info("[OK] Calendar icon clicked successfully, date picker opened")

    def validateFutureDatesAreDisabled(self) -> None:

        logger.info("Validating that future dates are disabled in calendar")

        if not self.calendar_grid.is_visible():
            logger.info("Calendar not visible, clicking calendar icon first")
            self.clickCalendarIcon()

        today = datetime.now()
        logger.info(f"Current date: {today.strftime('%Y-%m-%d')}")

        month_label = self.calendar_month_label.inner_text()
        logger.info(f"Calendar displaying: {month_label}")

        future_dates_checked, disabled_future_dates = self._check_future_dates_in_current_view(today)

        # If today is the last day of the month there are no future dates visible in the
        # current month view.  Navigate forward one month, verify every date there is
        # disabled, then navigate back so the calendar is left in its original state.
        navigated_to_next_month = False
        if future_dates_checked == 0:
            logger.info(
                "No future dates found in current month view "
                "(today may be the last day of the month). "
                "Navigating to next month to verify all its dates are disabled."
            )
            self.calendar_next_month_button.click()
            self.context.wait_for_timeout(400)
            next_month_label = self.calendar_month_label.inner_text()
            logger.info(f"Moved to next month: {next_month_label}")
            navigated_to_next_month = True

            future_dates_checked, disabled_future_dates = self._check_future_dates_in_current_view(today)

            # Navigate back to the original month
            self.calendar_previous_month_button.click()
            self.context.wait_for_timeout(400)
            logger.info("Navigated back to original month")

        logger.info(f"Future dates checked: {future_dates_checked}")
        logger.info(f"Disabled future dates: {disabled_future_dates}")

        assert future_dates_checked > 0, (
            "No future dates found to validate even after checking next month. "
            "Cannot confirm future-date restriction is working."
        )
        assert disabled_future_dates == future_dates_checked, (
            f"Not all future dates are disabled. "
            f"Expected {future_dates_checked}, but only {disabled_future_dates} are disabled"
        )

        logger.info("[OK] All future dates are correctly disabled and not selectable")

    def _check_future_dates_in_current_view(self, today: datetime) -> tuple[int, int]:
        """
        Scan the currently visible calendar month for dates strictly after today.
        Returns (future_dates_checked, disabled_future_dates).
        """
        today_only = today.date()
        all_date_buttons = self.calendar_date_buttons.all()
        logger.info(f"Total date buttons in view: {len(all_date_buttons)}")

        future_dates_checked = 0
        disabled_future_dates = 0

        for date_button in all_date_buttons:
            date_text = date_button.inner_text().strip()
            if not date_text.isdigit():
                continue

            timestamp_str = date_button.get_attribute("data-timestamp")
            if not timestamp_str:
                continue

            timestamp_ms = int(timestamp_str)
            date_obj = datetime.fromtimestamp(timestamp_ms / 1000)
            date_only = date_obj.date()

            if date_only > today_only:
                future_dates_checked += 1

                is_disabled = date_button.get_attribute("disabled") is not None
                has_disabled_class = "Mui-disabled" in (date_button.get_attribute("class") or "")
                aria_disabled = date_button.get_attribute("aria-disabled") == "true"

                if is_disabled or has_disabled_class or aria_disabled:
                    disabled_future_dates += 1
                    logger.info(f"[OK] Future date {date_text} ({date_only}) is correctly disabled")
                else:
                    logger.error(f"[FAIL] Future date {date_text} ({date_only}) is NOT disabled!")
                    raise AssertionError(
                        f"Future date {date_text} ({date_only}) should be disabled but is selectable"
                    )

        return future_dates_checked, disabled_future_dates
