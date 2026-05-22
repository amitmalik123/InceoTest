from typing import Union, List, Optional
from playwright.sync_api import Locator, Page, FrameLocator

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_manageBene.locators.update_beneficiary_locators import UpdateBeneficiaryLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class UpdateBeneficiaryPage(BasePage):
    """
    Page object for Update/Manage Beneficiaries landing page.
    Handles beneficiary management including add, edit, delete, and allocation.
    Covers all interactive elements from the Manage Beneficiaries workflow.
    """

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        loc = UpdateBeneficiaryLocators
        
        # ==================== Header Elements ====================
        self.back_button: Locator = context.locator(loc.BACK_BUTTON)
        self.client_name: Locator = context.locator(loc.CLIENT_NAME)
        self.client_account_number: Locator = context.locator(loc.CLIENT_ACCOUNT_NUMBER)
        
        # ==================== Stepper ====================
        self.stepper_container: Locator = context.locator(loc.STEPPER_CONTAINER)
        self.step_1_update_beneficiaries: Locator = context.locator(loc.STEP_1_UPDATE_BENEFICIARIES)
        self.step_2_esignature_details: Locator = context.locator(loc.STEP_2_ESIGNATURE_DETAILS)
        self.step_3_review: Locator = context.locator(loc.STEP_3_REVIEW)
        
        # ==================== Beneficiaries Section ====================
        self.beneficiaries_card: Locator = context.locator(loc.BENEFICIARIES_CARD)
        self.add_button: Locator = context.locator(loc.ADD_BUTTON)
        
        # ==================== Account Cards ====================
        self.account_cards: Locator = context.locator(loc.ACCOUNT_CARDS)
        self.account_card_title: Locator = context.locator(loc.ACCOUNT_CARD_TITLE)
        
        # ==================== Primary Beneficiaries Section ====================
        self.primary_section_header: Locator = context.locator(loc.PRIMARY_SECTION_HEADER)
        self.primary_beneficiary_name: Locator = context.locator(loc.PRIMARY_BENEFICIARY_NAME)
        self.primary_beneficiary_relation: Locator = context.locator(loc.PRIMARY_BENEFICIARY_RELATION)
        
        # ==================== Contingent Beneficiaries Section ====================
        self.contingent_section_header: Locator = context.locator(loc.CONTINGENT_SECTION_HEADER)
        self.contingent_beneficiary_name: Locator = context.locator(loc.CONTINGENT_BENEFICIARY_NAME)
        self.contingent_empty_state: Locator = context.locator(loc.CONTINGENT_EMPTY_STATE)
        
        # ==================== Beneficiary Action Buttons ====================
        self.edit_beneficiary_button: Locator = context.locator(loc.EDIT_BENEFICIARY_BUTTON)
        self.delete_beneficiary_button: Locator = context.locator(loc.DELETE_BENEFICIARY_BUTTON)
        
        # ==================== Allocation Fields ====================
        self.allocation_input: Locator = context.locator(loc.ALLOCATION_INPUT)
        self.allocation_percentage_symbol: Locator = context.locator(loc.ALLOCATION_PERCENTAGE_SYMBOL)
        self.allocate_equally_button: Locator = context.locator(loc.ALLOCATE_EQUALLY_BUTTON)
        self.total_allocation: Locator = context.locator(loc.TOTAL_ALLOCATION)
        
        # ==================== Signature Options Section ====================
        self.signature_options_card: Locator = context.locator(loc.SIGNATURE_OPTIONS_CARD)
        self.signature_options_label: Locator = context.locator(loc.SIGNATURE_OPTIONS_LABEL)
        self.electronic_signature_radio: Locator = context.locator(loc.ELECTRONIC_SIGNATURE_RADIO)
        self.physical_signature_radio: Locator = context.locator(loc.PHYSICAL_SIGNATURE_RADIO)
        self.signature_client_required_text: Locator = context.locator(loc.SIGNATURE_CLIENT_REQUIRED_TEXT)
        
        # ==================== Bottom Action Button ====================
        self.continue_button: Locator = context.locator(loc.CONTINUE_BUTTON)

        # ==================== Single-Account Section Playwright Locators ====================
        self.account_sections: Locator = context.locator(loc.ACCOUNT_SECTIONS)

    # ==================== Navigation & Wait Methods ====================
    def wait_for_page_load(self) -> None:
        """Wait for the Update Beneficiaries page to load completely."""
        logger.info("Waiting for Update Beneficiaries page to load")
        self.beneficiaries_card.wait_for(state="visible", timeout=10000)
        self.add_button.wait_for(state="visible", timeout=10000)
        logger.info("Page loaded - beneficiaries section visible")

    # ==================== Header Methods ====================
    def get_client_name(self) -> str:
        """Get the client name from the header."""
        logger.info("Retrieving client name")
        name = self.client_name.inner_text()
        logger.info(f"Client name: {name}")
        return name

    def get_client_account_number(self) -> str:
        """Get the client account number from the header."""
        logger.info("Retrieving client account number")
        account_number = self.client_account_number.inner_text()
        logger.info(f"Account number: {account_number}")
        return account_number

    def click_back_button(self) -> None:
        """Click the back button to return to previous page."""
        logger.info("Clicking back button")
        self.back_button.click()
        logger.info("Back button clicked")

    # ==================== Stepper Navigation ====================
    def get_current_step(self) -> str:
        """Get the current active step in the stepper."""
        logger.info("Retrieving current step")
        active_step = self.page.locator("span.MuiStepLabel-label.Mui-active").inner_text()
        logger.info(f"Current step: {active_step}")
        return active_step

    def is_step_completed(self, step_number: int) -> bool:
        """Check if a step is marked as completed."""
        logger.info(f"Checking if step {step_number} is completed")
        step_icon = self.page.locator(f"div.MuiStep-root:nth-child({step_number}) div.MuiStepIcon-root")
        is_completed = step_icon.evaluate("el => el.classList.contains('Mui-completed')")
        logger.info(f"Step {step_number} completed: {is_completed}")
        return is_completed

    # ==================== Add Beneficiary ====================
    def click_add_beneficiary_button(self) -> None:
        """Click the Add button to open Add Beneficiary modal."""
        logger.info("Clicking Add Beneficiary button")
        self.add_button.click()
        logger.info("Add Beneficiary button clicked - modal should open")

    # ==================== Account Card Methods ====================
    def get_account_cards_count(self) -> int:
        """Get the number of account cards displayed."""
        logger.info("Getting count of account cards")
        count = self.account_card_title.count()
        logger.info(f"Number of account cards: {count}")
        return count

    def get_account_card_by_index(self, index: int) -> Locator:
        """Get a specific account card by index."""
        logger.info(f"Retrieving account card at index {index}")
        return self.account_card_title.nth(index - 1)

    def get_account_name_and_number(self, card_index: int) -> str:
        """Get the account name and number from a card."""
        logger.info(f"Getting account name and number from card {card_index}")
        card_text = self.account_card_title.nth(card_index - 1).inner_text()
        logger.info(f"Account info: {card_text}")
        return card_text

    # ==================== Beneficiary Details ====================
    def get_primary_beneficiaries(self, card_index: int) -> List[str]:
        """Get list of primary beneficiaries for an account."""
        logger.info(f"Retrieving primary beneficiaries from card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        primary_section = card.locator("span.MuiTypography-cardHeaderTitle:has-text('Primary')").first
        
        beneficiary_names = card.locator("span.MuiTypography-cardTextPrimary").all_text_contents()
        logger.info(f"Primary beneficiaries: {beneficiary_names}")
        return beneficiary_names

    def get_contingent_beneficiaries(self, card_index: int) -> List[str]:
        """Get list of contingent beneficiaries for an account."""
        logger.info(f"Retrieving contingent beneficiaries from card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        contingent_section = card.locator("span.MuiTypography-cardHeaderTitle:has-text('Contingent')").first
        
        if self.contingent_empty_state.is_visible():
            logger.info("No contingent beneficiaries")
            return []
        
        beneficiary_names = card.locator("span.MuiTypography-cardTextPrimary").all_text_contents()
        logger.info(f"Contingent beneficiaries: {beneficiary_names}")
        return beneficiary_names

    def get_beneficiary_relationship(self, card_index: int, beneficiary_name: str) -> str:
        """Get the relationship type (Spouse/Non-Spouse) for a beneficiary."""
        logger.info(f"Getting relationship for {beneficiary_name} in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        beneficiary_row = card.locator(f"span.MuiTypography-cardTextPrimary:has-text('{beneficiary_name}')").first
        
        relationship = beneficiary_row.locator("..//span.MuiTypography-cardTextSecondary").inner_text()
        logger.info(f"Relationship: {relationship}")
        return relationship

    # ==================== Edit & Delete Operations ====================
    def click_edit_beneficiary(self, card_index: int, beneficiary_name: str) -> None:
        """Click the edit button for a specific beneficiary."""
        logger.info(f"Clicking edit button for {beneficiary_name} in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        edit_button = card.locator(f"button[aria-label*='Edit {beneficiary_name}']").first
        edit_button.click()
        
        logger.info(f"Edit button clicked for {beneficiary_name}")

    def click_delete_beneficiary(self, card_index: int, beneficiary_name: str) -> None:
        """Click the delete button for a specific beneficiary."""
        logger.info(f"Clicking delete button for {beneficiary_name} in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        delete_button = card.locator(f"button[aria-label*='Delete {beneficiary_name}']").first
        delete_button.click()
        
        logger.info(f"Delete button clicked for {beneficiary_name}")

    # ==================== Allocation Methods ====================
    def set_allocation_percentage(self, card_index: int, beneficiary_name: str, percentage: str) -> None:
        """Set the allocation percentage for a beneficiary."""
        logger.info(f"Setting allocation for {beneficiary_name} to {percentage}%")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        allocation_field = card.locator(f"input[type='number']").nth(0)
        allocation_field.clear()
        allocation_field.fill(percentage)
        
        logger.info(f"Allocation set to {percentage}%")

    def get_allocation_percentage(self, card_index: int, beneficiary_index: int) -> str:
        """Get the allocation percentage for a beneficiary."""
        logger.info(f"Getting allocation for beneficiary {beneficiary_index} in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        allocation_value = card.locator(f"input[type='number']").nth(beneficiary_index).input_value()
        
        logger.info(f"Allocation value: {allocation_value}%")
        return allocation_value

    def click_allocate_equally(self, card_index: int) -> None:
        """Click the Allocate Equally button for an account."""
        logger.info(f"Clicking Allocate Equally button in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        allocate_button = card.locator("button:has-text('Allocate Equally')").first
        allocate_button.click()
        
        logger.info("Allocate Equally button clicked")

    def is_allocate_equally_button_enabled(self, card_index: int) -> bool:
        """Check if the Allocate Equally button is enabled."""
        logger.info(f"Checking if Allocate Equally button is enabled in card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        allocate_button = card.locator("button:has-text('Allocate Equally')").first
        
        is_enabled = allocate_button.evaluate("el => !el.disabled")
        logger.info(f"Allocate Equally button enabled: {is_enabled}")
        return is_enabled

    def get_total_allocation(self, card_index: int) -> str:
        """Get the total allocation percentage for an account."""
        logger.info(f"Getting total allocation for card {card_index}")
        
        card = self.page.locator("div.MuiCard-root").nth(card_index)
        total_text = card.locator("p.MuiTypography-body1:has-text('Total:')").inner_text()
        
        logger.info(f"Total allocation: {total_text}")
        return total_text

    # ==================== Signature Options ====================
    def select_electronic_signature(self) -> None:
        """Select Electronic Signature option."""
        logger.info("Selecting Electronic Signature option")
        self.electronic_signature_radio.click()
        self.electronic_signature_radio.check()
        logger.info("Electronic Signature selected")

    def select_physical_signature(self) -> None:
        """Select Physical Signature option."""
        logger.info("Selecting Physical Signature option")
        self.physical_signature_radio.click()
        self.physical_signature_radio.check()
        logger.info("Physical Signature selected")

    def get_selected_signature_option(self) -> str:
        """Get the currently selected signature option."""
        logger.info("Getting selected signature option")
        
        is_electronic_checked = self.electronic_signature_radio.is_checked()
        
        if is_electronic_checked:
            option = "Electronic"
            logger.info("Selected option: Electronic Signature")
        else:
            option = "Physical"
            logger.info("Selected option: Physical Signature")
        
        return option

    def is_signature_client_required_text_visible(self) -> bool:
        """Check if 'Client signature is required' text is visible."""
        logger.info("Checking if client signature required text is visible")
        is_visible = self.signature_client_required_text.is_visible()
        logger.info(f"Text visible: {is_visible}")
        return is_visible

   
    def is_add_button_enabled(self) -> bool:
        """Check if the Add button is enabled."""
        logger.info("Checking if Add button is enabled")
        is_enabled = self.add_button.evaluate("el => !el.disabled")
        logger.info(f"Add button enabled: {is_enabled}")
        return is_enabled

    def is_continue_button_enabled(self) -> bool:
        """Check if the Continue button is enabled."""
        logger.info("Checking if Continue button is enabled")
        is_enabled = self.continue_button.evaluate("el => !el.disabled")
        logger.info(f"Continue button enabled: {is_enabled}")
        return is_enabled

    def does_account_have_beneficiaries(self, card_index: int) -> bool:
        """Check if an account has any beneficiaries."""
        logger.info(f"Checking if card {card_index} has beneficiaries")
        
        empty_state = self.page.locator("span.MuiTypography-emptyStateText:has-text('No beneficiaries')")
        has_beneficiaries = not empty_state.is_visible()
        
        logger.info(f"Has beneficiaries: {has_beneficiaries}")
        return has_beneficiaries

   
    def click_continue_button(self) -> None:
        """Click the Continue button to proceed to e-Signature Details."""
        logger.info("Clicking Continue button")
        self.continue_button.click()
        logger.info("Continue button clicked - moving to e-Signature Details")

   
    def get_single_primary_account_section(self) -> Optional[Locator]:
        """
        Scan all individual account sections and return the one with exactly
        1 primary beneficiary. Uses Playwright locators for better reliability.
        """
        logger.info("Scanning all account sections for one with exactly 1 primary beneficiary")

        section_count = self.account_sections.count()
        logger.info(f"Total account sections found: {section_count}")

        for i in range(section_count):
            section = self.account_sections.nth(i)
            
            # Count primary beneficiary name spans within this section's Primary area
            primary_names = section.locator("span.MuiTypography-cardTextPrimary")
            primary_count = primary_names.count()

            # Get section title for logging
            section_title = section.locator(".MuiCardHeader-title").first.inner_text()
            logger.info(f"Section '{section_title}': {primary_count} primary beneficiary row(s)")

            if primary_count == 1:
                logger.info(f"[MATCH] Section '{section_title}' has exactly 1 primary beneficiary")
                return section

        logger.info("No section with exactly 1 primary beneficiary was found")
        return None

    def click_allocate_equally_for_section(self, section: Locator) -> bool:
        """
        Click the 'Allocate Equally' button inside the provided section Locator,
        only if it is currently enabled.

        Returns:
            True if button was clicked, False if it was disabled.
        """
        button = section.get_by_role("button", name="Allocate Equally")
        is_enabled: bool = button.is_enabled()
        logger.info(f"'Allocate Equally' button enabled state in section: {is_enabled}")

        if is_enabled:
            button.click()
            logger.info("'Allocate Equally' button clicked successfully")
            return True

        logger.info("'Allocate Equally' button is disabled — click skipped")
        return False
    def get_section_with_n_primary_beneficiaries(self, count: int) -> Optional[Locator]:
        
        logger.info(f"Scanning all account sections for one with exactly {count} primary beneficiaries")

        section_count = self.account_sections.count()
        logger.info(f"Total account sections found: {section_count}")

        for i in range(section_count):
            section = self.account_sections.nth(i)
            
            primary_names = section.locator("span.MuiTypography-cardTextPrimary")
            primary_count = primary_names.count()

            section_title = section.locator(".MuiCardHeader-title").first.inner_text()
            logger.info(f"Section '{section_title}': {primary_count} primary beneficiary row(s)")

            if primary_count == count:
                logger.info(f"[MATCH] Section '{section_title}' has exactly {count} primary beneficiaries")
                return section

        logger.info(f"No section with exactly {count} primary beneficiaries was found")
        return None

    def get_first_multi_bene_primary_section(self) -> Optional[Locator]:
        """
        Dynamically finds the first Primary beneficiary section on the page that:
          - contains MORE THAN ONE beneficiary row (input[type='number'] count > 1)
          - has its 'Allocate Equally' button ENABLED

        This avoids hardcoding a specific count (e.g. exactly 2) and works for any
        section where allocation splitting is meaningful.

        Returns:
            Locator for the matching section, or None if none found.
        """
        logger.info(
            "Scanning all account sections for the first Primary section "
            "with more than one beneficiary and Allocate Equally enabled"
        )

        section_count = self.account_sections.count()
        logger.info(f"Total account sections found: {section_count}")

        for i in range(section_count):
            section = self.account_sections.nth(i)
            section_title = section.locator(".MuiCardHeader-title").first.inner_text().strip()

            # Count only PRIMARY allocation inputs (before the first Allocate Equally button)
            primary_inputs_xpath = (
                ".//input[@type='number' "
                "and following::button[normalize-space(.)='Allocate Equally'] "
                "and not(preceding::button[normalize-space(.)='Allocate Equally'])]"
            )
            primary_inputs = section.locator(f"xpath={primary_inputs_xpath}")
            bene_count = primary_inputs.count()
            logger.info(f"Section '{section_title}': {bene_count} PRIMARY allocation input(s)")

            if bene_count < 2:
                logger.info(f"  Skipping '{section_title}' — only {bene_count} primary beneficiary")
                continue

            allocate_btn = section.get_by_role("button", name="Allocate Equally")
            btn_count = allocate_btn.count()
            if btn_count == 0:
                logger.info(f"  Skipping '{section_title}' — no Allocate Equally button found")
                continue

            is_enabled = allocate_btn.first.is_enabled()
            if not is_enabled:
                logger.info(f"  Skipping '{section_title}' — Allocate Equally button is disabled")
                continue

            logger.info(
                f"[MATCH] Section '{section_title}' has {bene_count} PRIMARY beneficiaries "
                f"with Allocate Equally enabled"
            )
            return section

        logger.info(
            "No Primary section found with multiple beneficiaries and Allocate Equally enabled"
        )
        return None

    def get_primary_allocation_percentages(self, section: Locator) -> list[str]:
        """
        Get the allocation percentage values for PRIMARY beneficiaries only.

        Scopes to inputs that appear BEFORE the first 'Allocate Equally' button
        in DOM order — this isolates Primary inputs from Contingent inputs
        within the same account card.

        Returns:
            List of allocation percentage strings (e.g., ['50', '50'])
        """
        # XPath: input[type='number'] that has a following 'Allocate Equally' button
        # but NO preceding 'Allocate Equally' button — i.e., belongs to Primary group.
        primary_inputs_xpath = (
            ".//input[@type='number' "
            "and following::button[normalize-space(.)='Allocate Equally'] "
            "and not(preceding::button[normalize-space(.)='Allocate Equally'])]"
        )
        allocation_inputs = section.locator(f"xpath={primary_inputs_xpath}")
        count = allocation_inputs.count()

        allocations = []
        for i in range(count):
            value = allocation_inputs.nth(i).input_value()
            allocations.append(value)
            logger.info(f"Primary beneficiary {i+1} allocation: {value}%")

        return allocations

    def get_all_two_primary_account_sections(self) -> list[Locator]:
        
        logger.info("Scanning all account sections for those with exactly 2 primary beneficiaries")
        
        section_count = self.account_sections.count()
        logger.info(f"Total account sections found: {section_count}")
        
        two_primary_sections = []
        
        for i in range(section_count):
            section = self.account_sections.nth(i)
            primary_names = section.locator("span.MuiTypography-cardTextPrimary")
            primary_count = primary_names.count()
            
            section_title = section.locator(".MuiCardHeader-title").first.inner_text()
            logger.info(f"Section '{section_title}': {primary_count} primary beneficiary row(s)")
            
            if primary_count == 2:
                logger.info(f"[MATCH] Section '{section_title}' has exactly 2 primary beneficiaries")
                two_primary_sections.append(section)
        
        logger.info(f"Found {len(two_primary_sections)} section(s) with exactly 2 primary beneficiaries")
        return two_primary_sections

    def is_allocation_equal(self, section: Locator) -> bool:
        """
        Check if the allocation percentages in the given section are equally distributed.
        
        Args:
            section: The beneficiary section Locator
            
        Returns:
            True if all allocations are equal, False otherwise
        """
        allocations = self.get_primary_allocation_percentages(section)
        
        if len(allocations) < 2:
            logger.info("Less than 2 beneficiaries, cannot determine equal distribution")
            return False
        
        # Convert to float for comparison (handle '50', '50.0', '50.00', etc.)
        allocation_values = [float(alloc) for alloc in allocations]
        
        # Check if all values are equal, allowing <=0.01 rounding tolerance.
        # Round to 2dp before comparing to avoid float precision issues
        # (e.g. 33.34 - 33.33 = 0.01000...1563 in Python, not exactly 0.01)
        min_val = min(allocation_values)
        max_val = max(allocation_values)
        is_equal = round(max_val - min_val, 2) <= 0.01
        
        logger.info(f"Allocations: {allocations} - Equal distribution: {is_equal}")
        return is_equal

    def make_allocation_unequal(self, section: Locator) -> None:
        """
        Edit allocation inputs to make the distribution unequal.
        This modifies the first allocation input to create an unequal distribution.
        
        Args:
            section: The beneficiary section Locator
        """
        logger.info("Making allocation distribution unequal")
        
        allocations = self.get_primary_allocation_percentages(section)
        
        if len(allocations) < 2:
            logger.warning("Less than 2 beneficiaries, cannot make unequal")
            return
        
        allocation_inputs = section.locator("input[type='number']")
        
        # Get current values
        first_value = float(allocations[0])
        second_value = float(allocations[1])
        
        logger.info(f"Current allocations: {allocations}")
        
        # If already unequal, do nothing
        if abs(first_value - second_value) > 0.01:
            logger.info("Allocation is already unequal, no changes needed")
            return
        
        # Make it unequal - set first to 40%, second to 60%
        first_input = allocation_inputs.nth(0)
        second_input = allocation_inputs.nth(1)
        
        # Clear and fill with new values
        first_input.click()
        first_input.fill("")
        first_input.fill("40")
        logger.info(f"Set first beneficiary allocation to 40%")
        
        second_input.click()
        second_input.fill("")
        second_input.fill("60")
        logger.info(f"Set second beneficiary allocation to 60%")
        
        # Wait for the page to update
        self.context.wait_for_timeout(500)
        
        # Verify the change
        new_allocations = self.get_primary_allocation_percentages(section)
        logger.info(f"New allocations after making unequal: {new_allocations}")

    def verify_allocation_is_equal(self, section: Locator) -> bool:
        """
        Verify that allocations in the section are equally distributed.
        This is useful for assertions in tests.
        
        Args:
            section: The beneficiary section Locator
            
        Returns:
            True if equal, raises AssertionError if not
        """
        allocations = self.get_primary_allocation_percentages(section)
        is_equal = self.is_allocation_equal(section)
        
        if not is_equal:
            raise AssertionError(f"Allocations are not equal: {allocations}")
        
        logger.info(f"✓ Verified: Allocations are equal: {allocations}")
        return True

    def get_section_total_text(self, section: Locator) -> str:
        """
        Read the 'Total: X.XX%' text displayed below the Allocate Equally button
        in a beneficiary section.

        DOM: <p class="...css-ry5fxz">Total: 100.00%</p>
        """
        total_el = section.locator("p:has-text('Total:')")
        total_el.first.wait_for(state="visible", timeout=10000)
        text = total_el.first.inner_text().strip()
        logger.info(f"Section total text: '{text}'")
        return text

    def get_section_total_percentage(self, section: Locator) -> float:
        """
        Extract the numeric total percentage from the section total text,
        e.g. 'Total: 100.00%' → 100.0
        """
        import re
        text = self.get_section_total_text(section)
        match = re.search(r"([\d.]+)%", text)
        value = float(match.group(1)) if match else 0.0
        logger.info(f"Section total percentage: {value}%")
        return value

    # ==================== Allocation Field & Group Total Validation ====================

    def set_allocation_value(self, section: Locator, index: int, value: str) -> str:
        """
        Set the allocation input at the given index to the specified string value.
        Reads the value before and after entry for logging/validation.
        
        Uses click(click_count=3) to select-all existing text before filling,
        then presses Tab to trigger field-level validation (blur).

        Args:
            section: The beneficiary section Locator
            index:   0-based index of the allocation input within the section
            value:   String value to enter (e.g. '50.00', '00.01', '100.01')

        Returns:
            The actual value read back from the input after entry
        """
        allocation_inputs = section.locator("input[type='number']")
        target_input = allocation_inputs.nth(index)

        # Read and log the current value BEFORE making any change
        before_value = target_input.input_value()
        logger.info(f"Allocation input[{index}] value BEFORE entry: '{before_value}'")

        # Select-all via triple-click then overwrite with fill
        target_input.click(click_count=3)
        target_input.fill(value)

        # Trigger field validation by blurring (Tab moves focus away)
        target_input.press("Tab")

        # Read and log the actual value AFTER entry
        after_value = allocation_inputs.nth(index).input_value()
        logger.info(f"Allocation input[{index}] value AFTER entry: '{after_value}' (intended: '{value}')")

        return after_value

    def is_allocation_input_in_error(self, section: Locator, index: int) -> bool:
        """
        Return True if the allocation input at *index* shows a FIELD-LEVEL error state.

        Only checks aria-invalid="true" on the <input> element itself.
        This deliberately excludes group-total errors (Mui-error on the container)
        because those fire on all inputs whenever the sum ≠ 100%, even when the
        individual field value is format- and range-valid.

        Args:
            section: The beneficiary section Locator
            index:   0-based index of the allocation input
        """
        allocation_inputs = section.locator("input[type='number']")
        target_input = allocation_inputs.nth(index)

        aria_invalid = target_input.get_attribute("aria-invalid")
        is_error = aria_invalid == "true"
        logger.info(
            f"Allocation input[{index}] aria-invalid='{aria_invalid}' → field-level error: {is_error}"
        )
        return is_error

    def get_section_total_text(self, section: Locator) -> str:
        """
        Return the raw 'Total: XX.XX%' string displayed at the bottom of the section.
        Example return value: 'Total: 100.00%'
        """
        total_el = section.locator("p.MuiTypography-body1:has-text('Total:')")
        text = total_el.first.inner_text()
        logger.info(f"Section total text: '{text}'")
        return text

    def is_group_total_in_error_state(self, section: Locator) -> bool:
        """
        Return True when the beneficiary group total triggers an error state.

        When the Primary allocations do not sum to 100.00%, the application
        highlights ALL inputs in the group. This is detected by:
          1. Presence of at least one div.MuiOutlinedInput-root.Mui-error
          2. OR at least one input[aria-invalid='true']

        Args:
            section: The beneficiary section Locator
        """
        # Check for Mui-error on any input container
        error_containers = section.locator("div.MuiOutlinedInput-root.Mui-error")
        if error_containers.count() > 0:
            logger.info(f"Group total error detected via Mui-error ({error_containers.count()} container(s))")
            return True

        # Fallback: check aria-invalid on any input
        invalid_inputs = section.locator("input[type='number'][aria-invalid='true']")
        if invalid_inputs.count() > 0:
            logger.info(f"Group total error detected via aria-invalid ({invalid_inputs.count()} input(s))")
            return True

        logger.info("Group total is valid — no error state detected")
        return False

    def set_two_primary_allocations(self, section: Locator, value1: str, value2: str) -> None:
        """
        Set the first and second allocation inputs inside a 2-primary-account section.
        Triggers validation blur after each update.

        Args:
            section: The beneficiary section Locator (must have at least 2 primary inputs)
            value1:  Value to enter in the first allocation input
            value2:  Value to enter in the second allocation input
        """
        logger.info(f"Setting two-primary allocations: [{value1}%, {value2}%]")
        self.set_allocation_value(section, 0, value1)
        self.set_allocation_value(section, 1, value2)
        # Final blur so the group-total validation fires
        self.context.wait_for_timeout(400)
        logger.info(f"Two-primary allocations set: {value1}% / {value2}%")

    # ==================== Delete / Undo / Badge State Methods ====================

    def get_deletable_primary_delete_buttons(self, section: Locator) -> Locator:
        """
        Return all ENABLED delete buttons in the Primary group of a section.

        Uses XPath axis to scope to inputs before the first 'Allocate Equally' button
        (= Primary group only), and excludes disabled buttons (last-remaining primary bene
        cannot be deleted).

        Returns:
            Locator matching all enabled Delete buttons in the Primary group
        """
        xpath = (
            ".//button["
            "contains(@aria-label,'Delete') "
            "and not(@disabled) "
            "and following::button[normalize-space(.)='Allocate Equally'] "
            "and not(preceding::button[normalize-space(.)='Allocate Equally'])"
            "]"
        )
        return section.locator(f"xpath={xpath}")

    def get_bene_name_from_delete_button(self, delete_btn: Locator) -> str:
        """
        Extract the beneficiary name from a delete button's aria-label.
        e.g. 'Delete Tim Fujita Jr' → 'Tim Fujita Jr'
        """
        aria_label = delete_btn.get_attribute("aria-label") or ""
        return aria_label.replace("Delete ", "").strip()

    def is_removed_badge_visible(self, section: Locator, bene_name: str) -> bool:
        """
        Check whether the REMOVED chip badge is visible for a given beneficiary name.

        XPath axis: from the bene name span, find the first REMOVED span that follows it.
        """
        removed = section.locator(
            f"xpath=.//span[normalize-space(text())='{bene_name}']"
            f"/following::span[normalize-space(text())='REMOVED'][1]"
        )
        visible = removed.count() > 0 and removed.first.is_visible()
        logger.info(f"REMOVED badge visible for '{bene_name}': {visible}")
        return visible

    def get_undo_button_for_removed_bene(self, section: Locator) -> Locator:
        """
        Return the undo icon button that appears next to a REMOVED badge.

        XPath axis: from the REMOVED span, find the first following button whose
        aria-label contains 'Undo'.
        """
        return section.locator(
            "xpath=.//span[normalize-space(text())='REMOVED']"
            "/following::button[contains(@aria-label,'Undo')][1]"
        )

    def click_undo_removal(self, section: Locator) -> None:
        """
        Click the undo icon button next to the REMOVED badge to restore the beneficiary.
        """
        undo_btn = self.get_undo_button_for_removed_bene(section)
        undo_btn.wait_for(state="visible", timeout=5000)
        label = undo_btn.get_attribute("aria-label") or "undo"
        undo_btn.click()
        self.context.wait_for_timeout(400)
        logger.info(f"Clicked undo button: '{label}'")

    def is_bene_row_present(self, section: Locator, bene_name: str) -> bool:
        """
        Return True if a name span for the given beneficiary is found in the section.
        """
        span = section.locator(f"xpath=.//span[normalize-space(text())='{bene_name}']")
        present = span.count() > 0
        logger.info(f"Bene row present for '{bene_name}': {present}")
        return present

    def is_edit_button_visible_for_bene(self, section: Locator, bene_name: str) -> bool:
        """
        Return True if the Edit button is visible for a beneficiary row.
        Used to confirm a row is fully active (not in REMOVED state).

        XPath axis: from the name span, find the first Edit button that follows it.
        """
        edit_btn = section.locator(
            f"xpath=.//span[normalize-space(text())='{bene_name}']"
            f"/following::button[contains(@aria-label,'Edit')][1]"
        )
        visible = edit_btn.count() > 0 and edit_btn.first.is_visible()
        logger.info(f"Edit button visible for '{bene_name}': {visible}")
        return visible

    def is_added_badge_visible(self, section: Locator, bene_name: str) -> bool:
        """
        Return True if the ADDED chip badge is visible for a given beneficiary name.

        XPath axis: from the bene name span, find the first ADDED span that follows it.
        """
        added = section.locator(
            f"xpath=.//span[normalize-space(text())='{bene_name}']"
            f"/following::span[normalize-space(text())='ADDED'][1]"
        )
        visible = added.count() > 0 and added.first.is_visible()
        logger.info(f"ADDED badge visible for '{bene_name}': {visible}")
        return visible

    def click_delete_for_added_bene(self, section: Locator) -> None:
        """
        Click the delete button for the newly added beneficiary (identified by ADDED badge).

        XPath axis: from the ADDED badge span, find the first following Delete button
        in document order — this is the delete button on the same row as the new bene.
        """
        delete_btn = section.locator(
            "xpath=.//span[normalize-space(text())='ADDED']"
            "/following::button[contains(@aria-label,'Delete')][1]"
        )
        delete_btn.wait_for(state="visible", timeout=5000)
        label = delete_btn.get_attribute("aria-label") or "delete"
        delete_btn.first.click()
        self.context.wait_for_timeout(400)
        logger.info(f"Clicked delete for ADDED bene: '{label}'")

    # ------------------------------------------------------------------
    # Allocation state after delete / after undo
    # ------------------------------------------------------------------

    def get_removed_bene_allocation_value(self, section: Locator) -> str:
        """
        Return the allocation input value shown for the REMOVED beneficiary row.
        After deletion the field should display '0' or '0.00'.

        XPath: first input[type='number'] in DOM order after the REMOVED badge span —
        i.e., the disabled input on the same row as the deleted bene.
        """
        alloc_input = section.locator(
            "xpath=.//span[normalize-space(text())='REMOVED']"
            "/following::input[@type='number'][1]"
        )
        alloc_input.wait_for(state="attached", timeout=5000)
        value = alloc_input.input_value()
        logger.info(f"REMOVED bene allocation input value: '{value}'")
        return value

    def is_removed_bene_allocation_disabled(self, section: Locator) -> bool:
        """
        Return True if the allocation input on the REMOVED beneficiary row is disabled.
        """
        alloc_input = section.locator(
            "xpath=.//span[normalize-space(text())='REMOVED']"
            "/following::input[@type='number'][1]"
        )
        alloc_input.wait_for(state="attached", timeout=5000)
        disabled = alloc_input.is_disabled()
        logger.info(f"REMOVED bene allocation input disabled: {disabled}")
        return disabled

    def get_active_primary_allocations(self, section: Locator) -> list[str]:
        """
        Return allocation values for PRIMARY beneficiaries that are NOT in REMOVED state
        (i.e. their allocation inputs are enabled).

        Uses the same Primary-group scoping XPath as get_primary_allocation_percentages
        but adds 'not(@disabled)' so REMOVED-row inputs are excluded.
        """
        primary_active_xpath = (
            ".//input[@type='number' "
            "and not(@disabled) "
            "and following::button[normalize-space(.)='Allocate Equally'] "
            "and not(preceding::button[normalize-space(.)='Allocate Equally'])]"
        )
        inputs = section.locator(f"xpath={primary_active_xpath}")
        count = inputs.count()
        values = []
        for i in range(count):
            val = inputs.nth(i).input_value()
            values.append(val)
            logger.info(f"Active primary bene {i+1} allocation: {val}%")
        return values

    # ------------------------------------------------------------------
    # Section title
    # ------------------------------------------------------------------

    def get_section_title(self, section: Locator) -> str:
        """Return the account card title text from the given section locator."""
        return section.locator(".MuiCardHeader-title").first.inner_text().strip()

    # ------------------------------------------------------------------
    # ADDED badge helpers
    # ------------------------------------------------------------------

    def get_added_badge_for_bene_by_name(self, full_name: str) -> Locator:
        """
        Return the ADDED badge Locator for a beneficiary identified by full name.
        Uses a page-level XPath that navigates from the bene name span to its ADDED badge.
        """
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary')][contains(text(),'{full_name}')]"
            f"/ancestor::div[contains(@class,'MuiBox-root')]"
            f"/following-sibling::div//span[text()='ADDED']"
        )
        return self.context.locator(f"xpath={xpath}")

    def has_added_badge_in_section(self, section: Locator) -> bool:
        """Return True if any ADDED badge span is present in the given section."""
        badge = section.locator("xpath=.//span[normalize-space(text())='ADDED']")
        result = badge.count() > 0
        logger.info(f"ADDED badge present in section: {result}")
        return result

    def is_any_added_badge_visible(self) -> bool:
        """Return True if any ADDED badge element is visible anywhere on the page."""
        badge = self.context.locator("span:has-text('ADDED'), div:has-text('ADDED')").first
        result = badge.is_visible()
        logger.info(f"Any ADDED badge visible on page: {result}")
        return result

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def is_back_button_visible(self) -> bool:
        """Return True if a Back navigation button (aria-label*='Back') is visible."""
        return self.context.locator("button[aria-label*='Back']").is_visible()