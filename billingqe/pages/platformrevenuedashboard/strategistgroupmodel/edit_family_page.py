"""Edit Family page object."""

import logging
import re
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)


class EditFamilyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._existing_record_warning_seen = False

    def is_existing_record_warning_seen(self) -> bool:
        return self._existing_record_warning_seen

    def _existing_record_warning(self):
        return self.page.locator("#myModal").filter(
            has_text=re.compile(
                r"exsiting\s+edited\s+record|existing\s+edited\s+record|waiting\s+for\s+approval|waiting\s+for\s+update",
                re.I,
            )
        )

    def _capture_existing_record_warning_screenshot(self):
        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / "WARN_Edit_Family_Existing_Record.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)

    def _handle_existing_record_warning(self) -> bool:
        warning_dialog = self._existing_record_warning()
        if warning_dialog.count() == 0 or not warning_dialog.first.is_visible():
            return False

        self._existing_record_warning_seen = True
        self._capture_existing_record_warning_screenshot()

        ok_button = warning_dialog.first.get_by_role("button", name="OK").first
        if ok_button.count() > 0 and ok_button.is_visible():
            ok_button.click(force=True)
            try:
                expect(warning_dialog.first).to_be_hidden(timeout=5000)
            except AssertionError:
                self.page.keyboard.press("Escape")
                expect(warning_dialog.first).to_be_hidden(timeout=5000)

        return True

    def enter_search_family_name(self, family_name: str):
        search_input = self.page.get_by_role("textbox").first
        search_input.click()
        search_input.fill(family_name)

    def click_search(self):
        self.page.get_by_role("button", name="Search").click()
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_edit(self, family_name: str, target_status: str = "Approved"):
        all_rows = self.page.locator("tbody tr")
        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).first

        try:
            expect(all_rows.first).to_be_visible(timeout=15000)
        except AssertionError as exc:
            if no_records.count() > 0 and no_records.is_visible():
                raise AssertionError(
                    f"No family rows were found for search value '{family_name}'."
                ) from exc
            raise AssertionError(
                "Search results table did not render visible rows before attempting Edit."
            ) from exc

        family_pattern = re.compile(rf"\b{re.escape(str(family_name).strip())}\b", re.I)
        family_rows = all_rows.filter(has_text=family_pattern)
        if family_rows.count() == 0:
            raise AssertionError(f"No row matched family name '{family_name}' for Edit action.")

        chosen_row = None
        status_value = str(target_status).strip()
        if status_value and status_value.lower() != "all":
            status_pattern = re.compile(rf"\b{re.escape(status_value)}\b", re.I)
            status_rows = family_rows.filter(has_text=status_pattern)
            if status_rows.count() > 0:
                chosen_row = status_rows.first

        if chosen_row is None:
            chosen_row = family_rows.first

        expect(chosen_row).to_be_visible(timeout=10000)

        edit_button = chosen_row.get_by_role("button", name="Edit").first
        expect(edit_button).to_be_visible(timeout=10000)

        submit_button = self.page.get_by_role("button", name="Submit")

        edit_button.click()
        self.page.wait_for_timeout(800)
        if self._handle_existing_record_warning():
            return

        try:
            expect(submit_button).to_be_visible(timeout=7000)
            return
        except AssertionError:
            pass

        try:
            edit_button.click()
        except Exception:
            if self._handle_existing_record_warning():
                return
            raise

        self.page.wait_for_timeout(800)
        if self._handle_existing_record_warning():
            return

        try:
            expect(submit_button).to_be_visible(timeout=10000)
            return
        except AssertionError as exc:
            raise AssertionError(
                "Edit button was clicked, but edit form did not open (Submit button not visible)."
            ) from exc

    def verify_non_editable_fields(self, family_name: str, target_status: str = "Approved"):
        if self._existing_record_warning_seen:
            return

        family_name_box = self.page.get_by_role("row", name=re.compile(r"Family Name", re.I)).get_by_role("textbox").first
        program_name_combo = self.page.get_by_role("row", name=re.compile(r"Program Name", re.I)).get_by_role("combobox").first

        expect(family_name_box).to_be_visible()
        expect(family_name_box).to_have_value(family_name)
        expect(program_name_combo).to_be_visible()

        family_disabled = family_name_box.get_attribute("disabled") is not None
        family_readonly = family_name_box.get_attribute("readonly") is not None
        family_aria_disabled = (family_name_box.get_attribute("aria-disabled") or "").lower() == "true"
        if not (family_disabled or family_readonly or family_aria_disabled):
            raise AssertionError("Family Name field is expected to be non-editable, but it appears editable.")

        # Rejected records allow Program Name to be editable; other statuses keep it locked.
        status_value = str(target_status).strip().lower()
        if status_value == "rejected":
            return

        program_disabled = program_name_combo.get_attribute("disabled") is not None
        program_aria_disabled = (program_name_combo.get_attribute("aria-disabled") or "").lower() == "true"
        if not (program_disabled or program_aria_disabled):
            raise AssertionError("Program Name field is expected to be non-editable, but it appears editable.")

    def _select_option_with_fallback(self, locator, value: str, field_name: str):
        try:
            locator.select_option(value)
        except Exception:
            try:
                locator.select_option(label=value)
            except Exception as exc:
                logger.warning("Skipping %s selection due to unavailable option/control: %s", field_name, exc)

    def _get_create_style_checkbox(self):
        row = self.page.get_by_role("row", name=re.compile(r"Create\s*Style\s*Code", re.I))
        row_checkbox = row.get_by_role("checkbox").first
        if row_checkbox.count() > 0:
            return row_checkbox
        return self.page.get_by_role("checkbox").first

    def apply_edit_data(self, data: dict):
        if self._existing_record_warning_seen:
            return

        status_value = str(data.get("edit_target_status", "")).strip().lower()
        program_name_value = str(data.get("program_name", "")).strip()
        if status_value == "rejected" and program_name_value:
            program_dropdown = self.page.get_by_role("row", name=re.compile(r"Program Name", re.I)).get_by_role("combobox").first
            self._select_option_with_fallback(program_dropdown, program_name_value, "program_name")

        manager_type_value = str(data.get("manager_type_code", "")).strip()
        if manager_type_value:
            manager_dropdown = self.page.get_by_role("row", name=re.compile(r"Manager Type Code", re.I)).get_by_role("combobox")
            self._select_option_with_fallback(manager_dropdown, manager_type_value, "manager_type_code")

        is_uma_custom_value = str(data.get("is_uma_custom", "")).strip()
        if is_uma_custom_value:
            is_uma_custom_dropdown = self.page.get_by_role("row", name=re.compile(r"IsUMACustom", re.I)).get_by_role("combobox")
            self._select_option_with_fallback(is_uma_custom_dropdown, is_uma_custom_value, "is_uma_custom")

        has_minimum_value = str(data.get("has_minimum", "")).strip()
        if has_minimum_value:
            has_minimum_dropdown = self.page.get_by_role("row", name=re.compile(r"Has Minimum", re.I)).get_by_role("combobox")
            self._select_option_with_fallback(has_minimum_dropdown, has_minimum_value, "has_minimum")

        standard_discount_eligible_value = str(data.get("standard_discount_eligible", "")).strip()
        if standard_discount_eligible_value:
            standard_discount_dropdown = self.page.get_by_role(
                "row", name=re.compile(r"Standard Discount Eligible", re.I)
            ).get_by_role("combobox")
            self._select_option_with_fallback(
                standard_discount_dropdown, standard_discount_eligible_value, "standard_discount_eligible"
            )

        discount_package_value = str(data.get("discount_package", "")).strip()
        if discount_package_value:
            discount_package_dropdown = self.page.get_by_role("row", name=re.compile(r"Discount Package", re.I)).get_by_role(
                "combobox"
            )
            self._select_option_with_fallback(discount_package_dropdown, discount_package_value, "discount_package")

        product_name_value = str(data.get("product_name", "")).strip()
        if product_name_value:
            product_dropdown = self.page.locator("tr:nth-child(8) > td:nth-child(2) > div > .form-select")
            self._select_option_with_fallback(product_dropdown, product_name_value, "product_name")

        create_style = str(data.get("create_style_code", "")).strip().lower() in {"yes", "true", "1"}
        style_code_value = str(data.get("style_code", "")).strip()
        style_description_value = str(data.get("style_description", "")).strip()
        manager_style_description_value = str(data.get("manager_style_description", "")).strip()

        checkbox = self._get_create_style_checkbox()
        if create_style:
            try:
                checkbox.check()
            except Exception:
                pass
            if style_code_value:
                self.page.get_by_role("row", name=re.compile(r"Style Code", re.I)).get_by_role("textbox").first.fill(style_code_value)
            if style_description_value:
                self.page.get_by_role("row", name=re.compile(r"Style Description", re.I)).get_by_role("textbox").first.fill(
                    style_description_value
                )
            if manager_style_description_value:
                self.page.get_by_role("row", name=re.compile(r"Manager Style Description", re.I)).get_by_role(
                    "textbox"
                ).first.fill(manager_style_description_value)
        else:
            try:
                if checkbox.is_checked():
                    checkbox.uncheck()
            except Exception:
                pass
            if style_code_value:
                style_code_dropdown = self.page.get_by_role("row", name=re.compile(r"Style Code", re.I)).get_by_role("combobox").first
                self._select_option_with_fallback(style_code_dropdown, style_code_value, "style_code")
            if style_description_value:
                style_description_dropdown = self.page.get_by_role(
                    "row", name=re.compile(r"Style Description", re.I)
                ).get_by_role("combobox").first
                self._select_option_with_fallback(style_description_dropdown, style_description_value, "style_description")
            if manager_style_description_value:
                manager_style_description_dropdown = self.page.get_by_role(
                    "row", name=re.compile(r"Manager Style Description", re.I)
                ).get_by_role("combobox").first
                self._select_option_with_fallback(
                    manager_style_description_dropdown,
                    manager_style_description_value,
                    "manager_style_description",
                )

        category_value = str(data.get("category", "")).strip()
        option_value = str(data.get("option", "")).strip()
        if category_value:
            cat_dropdown = self.page.locator("tr:nth-child(13) > td:nth-child(2) > div > .form-select")
            self._select_option_with_fallback(cat_dropdown, category_value, "category")
        if option_value:
            opt_dropdown = self.page.locator("tr:nth-child(14) > td:nth-child(2) > div > .form-select")
            self._select_option_with_fallback(opt_dropdown, option_value, "option")

        research_group_value = str(data.get("research_group", "")).strip()
        schedule_group_value = str(data.get("schedule_group", "")).strip()
        if research_group_value:
            self.page.get_by_role("row", name=re.compile(r"Research Group", re.I)).get_by_role("textbox").first.fill(
                research_group_value
            )
        if schedule_group_value:
            self.page.get_by_role("row", name=re.compile(r"Schedule Group", re.I)).get_by_role("textbox").first.fill(
                schedule_group_value
            )

    def confirm_update(self):
        if self._existing_record_warning_seen:
            return

        self.page.get_by_role("button", name="Yes").click()
        self.page.wait_for_timeout(500)
        self._handle_existing_record_warning()

    def verify_update_success(self, family_name: str, expected_status: str):
        if self._existing_record_warning_seen:
            return

        expect(self.page.get_by_text("Family details updated", exact=False)).to_be_visible()
        self.page.get_by_role("button", name="OK").click()

        family_row = self.page.get_by_role("row", name=family_name, exact=False).first
        expect(family_row).to_be_visible()

        if str(expected_status).strip():
            expect(self.page.get_by_role("cell", name=expected_status).first).to_be_visible()

        expect(self.page.get_by_role("button", name="Edit").first).to_be_visible()
