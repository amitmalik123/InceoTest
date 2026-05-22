"""Edit Family page object."""

import logging
import re
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


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
        screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
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

    def apply_edit_data(self, data: dict):
        if self._existing_record_warning_seen:
            return

        status_value = str(data.get("edit_target_status", "")).strip().lower()
        if status_value == "rejected" and str(data.get("program_name", "")).strip():
            self.page.get_by_role("row", name=re.compile(r"Program Name", re.I)).get_by_role("combobox").first.select_option(
                data["program_name"]
            )

        self.page.get_by_role("row", name=re.compile(r"Manager Type Code", re.I)).get_by_role("combobox").select_option(
            data["manager_type_code"]
        )
        self.page.get_by_role("row", name=re.compile(r"IsUMACustom", re.I)).get_by_role("combobox").select_option(
            data["is_uma_custom"]
        )
        self.page.get_by_role("row", name=re.compile(r"Has Minimum", re.I)).get_by_role("combobox").select_option(
            data["has_minimum"]
        )
        self.page.get_by_role("row", name=re.compile(r"Standard Discount Eligible", re.I)).get_by_role("combobox").select_option(
            data["standard_discount_eligible"]
        )
        self.page.get_by_role("row", name=re.compile(r"Discount Package", re.I)).get_by_role("combobox").select_option(
            data["discount_package"]
        )
        product_name_value = data.get("product_name") or data.get("row8_value")
        self.page.locator("tr:nth-child(8) > td:nth-child(2) > div > .form-select").select_option(product_name_value)

        if str(data.get("create_style_code", "")).strip().lower() in {"yes", "true", "1"}:
            self.page.get_by_role("checkbox").check()

        self.page.get_by_role("row", name=re.compile(r"Style Code", re.I)).get_by_role("textbox").first.fill(data["style_code"])
        self.page.get_by_role("row", name=re.compile(r"Style Description", re.I)).get_by_role("textbox").first.fill(
            data["style_description"]
        )
        self.page.get_by_role("row", name=re.compile(r"Manager Style Description", re.I)).get_by_role("textbox").first.fill(
            data["manager_style_description"]
        )

        category_value = data.get("category") or data.get("row13_value")
        option_value = data.get("option") or data.get("row14_value")
        self.page.locator("tr:nth-child(13) > td:nth-child(2) > div > .form-select").select_option(category_value)
        self.page.locator("tr:nth-child(14) > td:nth-child(2) > div > .form-select").select_option(option_value)

        self.page.get_by_role("row", name=re.compile(r"Research Group", re.I)).get_by_role("textbox").first.fill(
            data["research_group"]
        )
        self.page.get_by_role("row", name=re.compile(r"Schedule Group", re.I)).get_by_role("textbox").first.fill(
            data["schedule_group"]
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
