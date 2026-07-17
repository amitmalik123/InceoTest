

from typing import Union
from playwright.sync_api import Locator, Page, FrameLocator

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_manageBene.locators.edit_beneficiary_locators import EditBeneficiaryLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EditBeneficiaryPage(BasePage):

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        loc = EditBeneficiaryLocators

        self.page_title: Locator = context.locator(loc.PAGE_TITLE)

        self.dont_save_button: Locator = context.get_by_role("button", name=loc.DONT_SAVE_BUTTON)
        self.save_button: Locator = context.locator(loc.SAVE_BUTTON)

        self.beneficiary_combobox: Locator = context.locator(loc.BENEFICIARY_COMBOBOX)
        self.first_name_input: Locator = context.locator(loc.FIRST_NAME_INPUT)
        self.middle_name_input: Locator = context.locator(loc.MIDDLE_NAME_INPUT)
        self.last_name_input: Locator = context.locator(loc.LAST_NAME_INPUT)
        self.ssn_input: Locator = context.locator(loc.SSN_INPUT)
        self.dob_input: Locator = context.locator(loc.DOB_INPUT)

        self.relationship_radio_group: Locator = context.locator(loc.RELATIONSHIP_RADIO_GROUP)

        # Custom Request checkbox
        self.custom_request_label: Locator = context.locator(loc.CUSTOM_REQUEST_LABEL).first
        self.custom_request_checkbox: Locator = context.locator(loc.CUSTOM_REQUEST_CHECKBOX)

        # File input inside the Supporting Documentation section
        self.supporting_docs_file_input: Locator = context.locator(loc.SUPPORTING_DOCS_FILE_INPUT).first

    def is_edit_form_visible(self) -> bool:
        try:
            self.page_title.wait_for(state="visible", timeout=10000)
            return self.page_title.is_visible()
        except Exception:
            return False

    def get_first_name(self) -> str:
        return self.first_name_input.input_value()

    def get_last_name(self) -> str:
        return self.last_name_input.input_value()

    def get_selected_relationship(self) -> str:
        checked = self.context.locator(
            "xpath=//p[contains(text(),'Relationship to Account Holder')]"
            "/following-sibling::div//input[@type='radio' and @checked]"
        )
        try:
            return checked.first.get_attribute("value") or ""
        except Exception:
            return ""

    def verify_form_info(self, first_name: str, last_name: str, relationship: str) -> bool:

        logger.info(
            f"Verifying edit form: first_name='{first_name}', "
            f"last_name='{last_name}', relationship='{relationship}'"
        )

        if not self.is_edit_form_visible():
            logger.error("Edit Beneficiary form title not visible")
            return False

        actual_fn = self.get_first_name()
        actual_ln = self.get_last_name()
        actual_rel = self.get_selected_relationship()

        logger.info(
            f"Form values — first_name='{actual_fn}', "
            f"last_name='{actual_ln}', relationship='{actual_rel}'"
        )

        fn_ok = first_name.lower() in actual_fn.lower()
        ln_ok = last_name.lower() in actual_ln.lower()
        rel_ok = relationship.lower() == actual_rel.lower()

        if not fn_ok:
            logger.warning(f"First name mismatch: expected '{first_name}', got '{actual_fn}'")
        if not ln_ok:
            logger.warning(f"Last name mismatch: expected '{last_name}', got '{actual_ln}'")
        if not rel_ok:
            logger.warning(f"Relationship mismatch: expected '{relationship}', got '{actual_rel}'")

        return fn_ok and ln_ok and rel_ok

    def update_name_fields(self, new_first_name: str, new_last_name: str) -> None:
        logger.info(f"Updating name fields to '{new_first_name} {new_last_name}'")
        self.first_name_input.wait_for(state="visible", timeout=10000)
        self.first_name_input.fill(new_first_name)
        self.last_name_input.fill(new_last_name)
        logger.info(f"[OK] Name fields updated to '{new_first_name} {new_last_name}'")

    def select_designation_for_active_account(self, designation: str) -> None:
        logger.info(f"Selecting designation '{designation}' for active account")
        radio = self.context.locator(
            f"xpath=//input[@type='checkbox' and not(@disabled)]"
            f"/ancestor::div[contains(@class,'MuiCardContent-root')]"
            f"//input[@type='radio'][@value='{designation}' and not(@disabled)]"
        )
        radio.wait_for(state="visible", timeout=10000)
        radio.click(force=True)
        logger.info(f"[OK] Designation '{designation}' selected")

    def is_save_button_enabled(self) -> bool:
        return not self.save_button.is_disabled()

    def click_save(self) -> None:
        logger.info("Waiting for Save button to become enabled…")
        self.save_button.wait_for(state="visible", timeout=10000)
        self.context.locator(
            "button.MuiButton-containedPrimary:has-text('Save'):not([disabled])"
        ).wait_for(state="visible", timeout=10000)
        self.save_button.click()
        logger.info("[OK] Save button clicked")

    def verify_all_fields_disabled(self) -> dict:
        """
        Verifies that Beneficiary, First Name, Middle Name, Last Name,
        Social Security Number, and Date of Birth fields are all disabled.
        Returns a dict of {field_name: is_disabled} for reporting.
        """
        logger.info("Verifying all Edit Beneficiary form fields are disabled")

        results = {}

        # Beneficiary dropdown — combobox uses aria-disabled attribute
        try:
            self.beneficiary_combobox.wait_for(state="visible", timeout=10000)
            aria_disabled = self.beneficiary_combobox.get_attribute("aria-disabled")
            results["Beneficiary"] = aria_disabled == "true"
        except Exception as e:
            logger.warning(f"Beneficiary combobox check failed: {e}")
            results["Beneficiary"] = False

        # Standard input fields — use Playwright's is_disabled()
        field_locator_map = {
            "First Name": self.first_name_input,
            "Middle Name": self.middle_name_input,
            "Last Name": self.last_name_input,
            "Social Security Number": self.ssn_input,
            "Date of Birth": self.dob_input,
        }

        for field_name, locator in field_locator_map.items():
            try:
                locator.wait_for(state="attached", timeout=10000)
                results[field_name] = locator.is_disabled()
            except Exception as e:
                logger.warning(f"'{field_name}' field check failed: {e}")
                results[field_name] = False

        for field_name, is_disabled in results.items():
            status = "[OK] disabled" if is_disabled else "[FAIL] NOT disabled"
            logger.info(f"  {field_name}: {status}")

        return results

    def verify_relationship_selection(self, expected: str) -> dict:
        """
        Verifies the selected relationship radio button matches the expected value.
        Uses Playwright's is_checked() for reliable state detection with React.
        Returns {'expected': str, 'actual': str, 'match': bool}.
        """
        logger.info(f"Verifying selected relationship radio — expected: '{expected}'")

        radio_inputs = self.context.locator(
            "xpath=//p[contains(text(),'Relationship to Account Holder')]"
            "/following-sibling::div//input[@type='radio']"
        )
        radio_inputs.first.wait_for(state="attached", timeout=10000)

        actual = ""
        count = radio_inputs.count()
        for i in range(count):
            radio = radio_inputs.nth(i)
            value = radio.get_attribute("value") or ""
            if radio.is_checked():
                actual = value
                logger.info(f"  '{value}' radio is CHECKED")
            else:
                logger.info(f"  '{value}' radio is unchecked")

        match = expected.strip().lower() == actual.strip().lower()
        logger.info(
            f"Relationship check — expected: '{expected}', actual: '{actual}', match: {match}"
        )
        return {"expected": expected, "actual": actual, "match": match}

    def toggle_relationship_type(self, bene_type: str) -> dict:
        """
        Toggles the Relationship to Account Holder radio based on bene_type.

        Toggle logic:
          spouse     → already Spouse?     select Non-Spouse  : select Spouse
          non-spouse → already Non-Spouse? select Spouse      : select Non-Spouse
          trust      → already Trust?      select Entity      : select Trust
          entity     → already Entity?     select Trust       : select Entity

        After clicking, verifies mutual exclusivity:
          Spouse/Non-Spouse selected  →  Trust & Entity must be disabled
          Trust/Entity selected       →  Spouse & Non-Spouse must be disabled

        Returns:
          {
            'bene_type': str,      # normalised input
            'was_selected': str,   # radio value before toggle
            'now_selected': str,   # radio value after toggle
            'disabled_after': list,
            'exclusivity_ok': bool,
          }

        Raises:
          ValueError: if bene_type is not one of the four supported values.
        """
        normalised = bene_type.strip().lower()

        _toggle_map = {
            "spouse":     ("Spouse",     "Non-Spouse"),
            "non-spouse": ("Non-Spouse", "Spouse"),
            "trust":      ("Trust",      "Entity"),
            "entity":     ("Entity",     "Trust"),
        }

        if normalised not in _toggle_map:
            raise ValueError(
                f"Invalid bene_type '{bene_type}'. "
                f"Supported values: {list(_toggle_map.keys())}"
            )

        primary_value, alternate_value = _toggle_map[normalised]

        # Build per-value radio locators using XPath inside the radiogroup
        def _radio(value: str) -> Locator:
            return self.context.locator(
                f"xpath=//p[contains(text(),'Relationship to Account Holder')]"
                f"/following-sibling::div//input[@type='radio' and @value='{value}']"
            )

        # Wait for radios to be attached
        _radio(primary_value).wait_for(state="attached", timeout=10000)

        # Determine currently selected radio
        was_selected = ""
        for v in ("Spouse", "Non-Spouse", "Trust", "Entity"):
            try:
                if _radio(v).is_checked():
                    was_selected = v
                    break
            except Exception:
                pass

        logger.info(
            f"toggle_relationship_type('{bene_type}') — "
            f"currently selected: '{was_selected}', "
            f"primary target: '{primary_value}', alternate: '{alternate_value}'"
        )

        # Toggle: if primary is already selected, click alternate; else click primary
        target_value = alternate_value if was_selected == primary_value else primary_value
        target_radio = _radio(target_value)

        target_radio.wait_for(state="visible", timeout=10000)
        assert not target_radio.is_disabled(), (
            f"Cannot select '{target_value}' — radio is disabled on the form"
        )
        target_radio.click(force=True)
        logger.info(f"Clicked '{target_value}' radio")

        # Confirm new selection
        now_selected = ""
        for v in ("Spouse", "Non-Spouse", "Trust", "Entity"):
            try:
                if _radio(v).is_checked():
                    now_selected = v
                    break
            except Exception:
                pass

        assert now_selected == target_value, (
            f"Radio selection did not stick — expected '{target_value}', "
            f"got '{now_selected}'"
        )

        # Verify mutual exclusivity after toggle
        individual_group = {"Spouse", "Non-Spouse"}
        entity_group = {"Trust", "Entity"}
        expected_disabled = sorted(
            entity_group if now_selected in individual_group else individual_group
        )

        disabled_after = []
        for v in ("Spouse", "Non-Spouse", "Trust", "Entity"):
            try:
                if _radio(v).is_disabled():
                    disabled_after.append(v)
            except Exception:
                pass

        missing = [v for v in expected_disabled if v not in disabled_after]
        exclusivity_ok = len(missing) == 0

        if exclusivity_ok:
            logger.info(
                f"[OK] '{now_selected}' selected — opposite group "
                f"{expected_disabled} are all disabled"
            )
        else:
            logger.warning(
                f"[FAIL] '{now_selected}' selected — {missing} should be "
                f"disabled but are NOT"
            )

        return {
            "bene_type": normalised,
            "was_selected": was_selected,
            "now_selected": now_selected,
            "disabled_after": disabled_after,
            "expected_disabled": expected_disabled,
            "missing_disabled": missing,
            "exclusivity_ok": exclusivity_ok,
        }

    def verify_mutually_exclusive_relationship_radios(self) -> dict:
        """
        Verifies mutual exclusivity of relationship radio buttons.

        Rules (per DOM):
          - If Spouse or Non-Spouse is selected  → Trust AND Entity must be disabled
          - If Trust or Entity is selected        → Spouse AND Non-Spouse must be disabled

        Returns a report dict:
          {
            'selected': str,          # currently checked radio value
            'selected_group': str,    # 'individual' | 'entity'
            'disabled_radios': list,  # radio values where is_disabled()==True
            'enabled_radios':  list,  # radio values where is_disabled()==False
            'expected_disabled': list,
            'passed': bool,
          }
        """
        logger.info("Verifying mutual exclusivity of relationship radio buttons")

        radios = self.context.locator(
            "xpath=//p[contains(text(),'Relationship to Account Holder')]"
            "/following-sibling::div//input[@type='radio']"
        )
        radios.first.wait_for(state="attached", timeout=10000)

        count = radios.count()
        selected = ""
        disabled_radios = []
        enabled_radios = []

        for i in range(count):
            radio = radios.nth(i)
            value = radio.get_attribute("value") or f"radio_{i}"
            checked = radio.is_checked()
            disabled = radio.is_disabled()

            if checked:
                selected = value
            if disabled:
                disabled_radios.append(value)
            else:
                enabled_radios.append(value)

            logger.info(
                f"  '{value}': checked={checked}, disabled={disabled}"
            )

        individual_group = {"Spouse", "Non-Spouse"}
        entity_group = {"Trust", "Entity"}

        if selected in individual_group:
            selected_group = "individual"
            expected_disabled = sorted(entity_group)
        elif selected in entity_group:
            selected_group = "entity"
            expected_disabled = sorted(individual_group)
        else:
            selected_group = "unknown"
            expected_disabled = []

        missing = [v for v in expected_disabled if v not in disabled_radios]
        passed = len(missing) == 0

        if passed:
            logger.info(
                f"[OK] '{selected}' selected ({selected_group} group) — "
                f"opposite group {expected_disabled} are all disabled"
            )
        else:
            logger.warning(
                f"[FAIL] '{selected}' selected — expected {expected_disabled} disabled, "
                f"but {missing} are NOT disabled"
            )

        return {
            "selected": selected,
            "selected_group": selected_group,
            "disabled_radios": disabled_radios,
            "enabled_radios": enabled_radios,
            "expected_disabled": expected_disabled,
            "missing_disabled": missing,
            "passed": passed,
        }

    def click_dont_save(self) -> None:
        logger.info("Clicking 'Don't Save' button")
        self.dont_save_button.click()
        logger.info("[OK] 'Don't Save' button clicked")

    def check_custom_request(self) -> None:
        """Scroll to and check the Custom Request checkbox if not already checked.
        MUI hides the real <input> — we click the outer MuiCheckbox span instead.
        """
        logger.info("Scrolling to 'Custom Request' label and checking checkbox")
        self.custom_request_label.wait_for(state="visible", timeout=15000)
        self.custom_request_label.scroll_into_view_if_needed()
        self.context.wait_for_timeout(300)
        # The actual input is hidden; use it only for state checks.
        # Click the visible MuiCheckbox span to toggle the checkbox.
        checkbox_input = self.custom_request_checkbox
        checkbox_input.wait_for(state="attached", timeout=10000)
        if not checkbox_input.is_checked():
            # Click the outer clickable span, not the hidden input
            clickable_span = self.context.locator(
                "xpath=//div[normalize-space(text())='Custom Request']"
                "/parent::div"
                "/parent::div"
                "/span[contains(@class,'MuiCheckbox-root')]"
            )
            clickable_span.scroll_into_view_if_needed()
            clickable_span.click()
            self.context.wait_for_timeout(500)
        logger.info("[OK] Custom Request checkbox is checked")

    def is_section_heading_visible(self, section_name: str) -> bool:
        """Return True if a section heading containing *section_name* text is visible."""
        logger.info(f"Checking visibility of section: '{section_name}'")
        heading = self.context.get_by_text(section_name, exact=False).first
        try:
            heading.wait_for(state="visible", timeout=10000)
            return heading.is_visible()
        except Exception:
            return False

    def upload_supporting_document(self, pdf_path: str) -> None:
        """Set *pdf_path* on the Supporting Documentation file input."""
        logger.info(f"Uploading supporting document: {pdf_path}")
        self.supporting_docs_file_input.set_input_files(pdf_path)
        self.context.wait_for_timeout(1000)
        logger.info(f"[OK] Uploaded supporting document: {pdf_path}")
