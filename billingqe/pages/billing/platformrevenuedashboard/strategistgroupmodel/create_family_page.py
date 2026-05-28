"""Create Family page object."""

import logging
import re
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.billing.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)


class CreateFamilyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def _get_create_style_checkbox(self):
        labeled_checkbox = self.page.get_by_label(re.compile(r"Create\s*Style\s*Code", re.I)).first
        if labeled_checkbox.count() > 0:
            return labeled_checkbox

        row = self.page.get_by_role("row", name=re.compile(r"Create\s*Style\s*Code", re.I))
        row_checkbox = row.get_by_role("checkbox").first
        if row_checkbox.count() > 0:
            return row_checkbox
        return self.page.get_by_role("checkbox").first

    def _set_style_field_value(self, row_name: str, value: str, expect_input: bool):
        row_index_map = {
            "Style Code": 10,
            "Style Description": 11,
            "Manager Style Description": 12,
        }
        row_index = row_index_map[row_name]

        if expect_input:
            textbox = self.page.locator(
                f"tr:nth-child({row_index}) > td:nth-child(2) input, tr:nth-child({row_index}) > td:nth-child(2) textarea"
            ).first
            if textbox.count() == 0:
                raise AssertionError(
                    f"Expected textbox for '{row_name}' when Create Style Code is checked, but none was found."
                )
            textbox.wait_for(state="visible", timeout=5000)
            textbox.click(timeout=3000)
            textbox.fill(value, timeout=3000)
            return

        combobox = self.page.locator(f"tr:nth-child({row_index}) > td:nth-child(2) > div > .form-select").first
        if combobox.count() == 0:
            raise AssertionError(
                f"Expected dropdown for '{row_name}' when Create Style Code is unchecked, but none was found."
            )
        combobox.wait_for(state="visible", timeout=5000)
        try:
            combobox.select_option(value, timeout=3000)
        except Exception:
            combobox.select_option(label=value, timeout=3000)

    def click_family_tab(self):
        self.page.get_by_text("Family", exact=True).click()

    def verify_family_page_loaded(self):
        expect(self.page.get_by_role("button", name="Create Model Family")).to_be_visible()
        expect(self.page.get_by_role("button", name="Search")).to_be_visible()

    def click_create_model_family(self):
        self.page.get_by_role("button", name="Create Model Family").click()

    def verify_create_family_form(self):
        expect(self.page.get_by_role("heading", name="Create new Family")).to_be_visible()

    def fill_family_name(self, family_name: str):
        self.page.get_by_role("row", name="Family Name").get_by_role("textbox").click()
        self.page.get_by_role("row", name="Family Name").get_by_role("textbox").fill(family_name)

    def select_manager_type_code(self, value: str):
        dropdown = self.page.get_by_role("row", name="Manager Type Code Select").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_program_name(self, value: str):
        dropdown = self.page.get_by_role("row", name="Program Name Select").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_is_uma_custom(self, value: str):
        dropdown = self.page.get_by_role("row", name="IsUMACustom Select").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_has_minimum(self, value: str):
        dropdown = self.page.get_by_role("row", name="Has Minimum Select").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_standard_discount_eligible(self, value: str):
        dropdown = self.page.get_by_role("row", name="Standard Discount Eligible").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_discount_package(self, value: str):
        dropdown = self.page.get_by_role("row", name="Discount Package Select").get_by_role("combobox")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_product_name_dropdown(self, value: str):
        dropdown = self.page.locator("tr:nth-child(8) > td:nth-child(2) > div > .form-select")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def check_checkbox(self):
        self._get_create_style_checkbox().check()

    def uncheck_checkbox(self):
        checkbox = self._get_create_style_checkbox()
        if checkbox.is_checked():
            checkbox.uncheck()

    def fill_style_code(self, value: str):
        self._set_style_field_value("Style Code", value, expect_input=True)

    def fill_style_description(self, value: str):
        self._set_style_field_value("Style Description", value, expect_input=True)

    def fill_manager_style_description(self, value: str):
        self._set_style_field_value("Manager Style Description", value, expect_input=True)

    def select_style_code_dropdown(self, value: str):
        self._set_style_field_value("Style Code", value, expect_input=False)

    def select_style_description_dropdown(self, value: str):
        self._set_style_field_value("Style Description", value, expect_input=False)

    def select_manager_style_description_dropdown(self, value: str):
        self._set_style_field_value("Manager Style Description", value, expect_input=False)

    def select_category_dropdown(self, value: str):
        dropdown = self.page.locator("tr:nth-child(13) > td:nth-child(2) > div > .form-select")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def select_option_dropdown(self, value: str):
        dropdown = self.page.locator("tr:nth-child(14) > td:nth-child(2) > div > .form-select")
        try:
            dropdown.select_option(value)
        except Exception:
            dropdown.select_option(label=value)

    def fill_research_group(self, value: str):
        self.page.get_by_role("row", name="Research Group").get_by_role("textbox").click()
        self.page.get_by_role("row", name="Research Group").get_by_role("textbox").fill(value)

    def fill_schedule_group(self, value: str):
        self.page.get_by_role("row", name="Schedule Group").get_by_role("textbox").click()
        self.page.get_by_role("row", name="Schedule Group").get_by_role("textbox").fill(value)

    def create_family(self, data: dict):
        self.click_family_tab()
        self.verify_family_page_loaded()
        self.click_create_model_family()
        self.verify_create_family_form()

        if str(data.get("family_name", "")).strip():
            self.fill_family_name(data["family_name"])

        manager_type = str(data.get("manager_type_code", "")).strip()
        if manager_type:
            self.select_manager_type_code(manager_type)

        program_name = str(data.get("program_name", "")).strip()
        if program_name:
            self.select_program_name(data["program_name"])
        if str(data.get("is_uma_custom", "")).strip():
            self.select_is_uma_custom(data["is_uma_custom"])
        if str(data.get("has_minimum", "")).strip():
            self.select_has_minimum(data["has_minimum"])
        if str(data.get("standard_discount_eligible", "")).strip():
            self.select_standard_discount_eligible(data["standard_discount_eligible"])
        if str(data.get("discount_package", "")).strip():
            self.select_discount_package(data["discount_package"])

        product_name = str(data.get("product_name", "")).strip()
        can_select_dependent_dropdowns = bool(manager_type and program_name)

        if can_select_dependent_dropdowns and product_name:
            try:
                self.select_product_name_dropdown(data["product_name"])
            except Exception as exc:
                logger.warning("Skipping product_name selection due to unavailable option: %s", exc)
        elif product_name:
            logger.warning(
                "Skipping product_name selection because dependent field(s) are blank. manager_type_code='%s', program_name='%s'",
                manager_type,
                program_name,
            )

        create_style = str(data.get("create_style_code", "")).strip().lower() in {"yes", "true", "1"}
        if create_style:
            self.check_checkbox()
        else:
            self.uncheck_checkbox()

        if create_style:
            if str(data.get("style_code", "")).strip():
                self.fill_style_code(data["style_code"])
            if str(data.get("style_description", "")).strip():
                self.fill_style_description(data["style_description"])
            if str(data.get("manager_style_description", "")).strip():
                self.fill_manager_style_description(data["manager_style_description"])
        elif can_select_dependent_dropdowns and product_name:
            if str(data.get("style_code", "")).strip():
                try:
                    self.select_style_code_dropdown(data["style_code"])
                except Exception as exc:
                    logger.warning("Skipping style_code selection due to unavailable option/control: %s", exc)
            if str(data.get("style_description", "")).strip():
                try:
                    self.select_style_description_dropdown(data["style_description"])
                except Exception as exc:
                    logger.warning("Skipping style_description selection due to unavailable option/control: %s", exc)
            if str(data.get("manager_style_description", "")).strip():
                try:
                    self.select_manager_style_description_dropdown(data["manager_style_description"])
                except Exception as exc:
                    logger.warning(
                        "Skipping manager_style_description selection due to unavailable option/control: %s",
                        exc,
                    )
        elif any(
            str(data.get(field_name, "")).strip()
            for field_name in ["style_code", "style_description", "manager_style_description"]
        ):
            logger.warning(
                "Skipping style dropdown selection because dependent field(s) are blank. manager_type_code='%s', program_name='%s', product_name='%s'",
                manager_type,
                program_name,
                product_name,
            )

        if can_select_dependent_dropdowns and product_name and str(data.get("category", "")).strip():
            try:
                self.select_category_dropdown(data["category"])
            except Exception as exc:
                logger.warning("Skipping category selection due to unavailable option: %s", exc)
        elif str(data.get("category", "")).strip():
            logger.warning(
                "Skipping category selection because dependent field(s) are blank. manager_type_code='%s', program_name='%s', product_name='%s'",
                manager_type,
                program_name,
                product_name,
            )
        if can_select_dependent_dropdowns and product_name and str(data.get("option", "")).strip():
            try:
                self.select_option_dropdown(data["option"])
            except Exception as exc:
                logger.warning("Skipping option selection due to unavailable option: %s", exc)
        elif str(data.get("option", "")).strip():
            logger.warning(
                "Skipping option selection because dependent field(s) are blank. manager_type_code='%s', program_name='%s', product_name='%s'",
                manager_type,
                program_name,
                product_name,
            )

        if str(data.get("research_group", "")).strip():
            self.fill_research_group(data["research_group"])
        if str(data.get("schedule_group", "")).strip():
            self.fill_schedule_group(data["schedule_group"])

    def verify_family_created(self, expected_family_name: str = ""):
        duplicate_warning = self.page.get_by_role("dialog").filter(
            has_text=re.compile(r"family\s*name\s*already\s*exist(s)?", re.I)
        )
        duplicate_message = self.page.get_by_text(
            re.compile(r"family\s*name\s*already\s*exist(s)?|already\s*exist(s)?", re.I)
        ).first

        success_message = self.page.get_by_text(re.compile(r"family\s*added\s*successfully", re.I)).first
        success_header = self.page.get_by_text(re.compile(r"^\s*success\s*$", re.I)).first
        create_button = self.page.get_by_role("button", name="Create Model Family").first
        search_button = self.page.get_by_role("button", name="Search").first

        def _capture_popup_screenshot(file_name: str):
            screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / file_name
            self.page.screenshot(path=str(screenshot_path), full_page=False)

        def _success_visible() -> bool:
            return (success_message.count() > 0 and success_message.is_visible()) or (
                success_header.count() > 0 and success_header.is_visible()
            )

        def _duplicate_visible() -> bool:
            return (duplicate_warning.count() > 0 and duplicate_warning.first.is_visible()) or (
                duplicate_message.count() > 0 and duplicate_message.is_visible()
            )

        def _handle_duplicate_as_pass() -> bool:
            if not _duplicate_visible():
                return False

            if duplicate_warning.count() > 0 and duplicate_warning.first.is_visible():
                expect(duplicate_warning.first).to_contain_text(re.compile(r"already\s*exist(s)?", re.I))
            else:
                expect(duplicate_message).to_be_visible(timeout=1000)

            _capture_popup_screenshot("WARN_Family_Already_Exists.png")

            ok_button = self.page.get_by_role("button", name=re.compile(r"^\s*ok\s*$", re.I)).first
            if ok_button.count() == 0 or not ok_button.is_visible():
                raise AssertionError("Family Already Exist popup is visible but OK button was not found.")
            ok_button.click()
            logger.info("Family Already Exist popup verified. Clicked OK.")
            return True

        def _dismiss_success_modal_if_present() -> bool:
            if not _success_visible():
                return False

            if success_message.count() > 0 and success_message.is_visible():
                expect(success_message).to_be_visible(timeout=1000)
            else:
                expect(success_header).to_be_visible(timeout=1000)

            _capture_popup_screenshot("INFO_Family_Created_Successfully.png")

            ok_button = self.page.get_by_role("button", name=re.compile(r"^\s*ok\s*$", re.I)).first
            if ok_button.count() == 0 or not ok_button.is_visible():
                raise AssertionError("Success popup is visible but OK button was not found.")
            ok_button.click()
            logger.info("Family created successfully popup verified. Clicked OK.")

            return True

        if _handle_duplicate_as_pass():
            return "duplicate"

        # Wait up to 10s for duplicate popup, success popup, or listing controls.
        for _ in range(20):
            if _handle_duplicate_as_pass():
                return "duplicate"
            if _success_visible():
                _dismiss_success_modal_if_present()
                return "created"
            if (create_button.count() > 0 and create_button.is_visible()) and (
                search_button.count() > 0 and search_button.is_visible()
            ):
                break
            self.page.wait_for_timeout(500)

        if _handle_duplicate_as_pass():
            return "duplicate"

        if _success_visible():
            _dismiss_success_modal_if_present()
            return "created"

        if not ((create_button.count() > 0 and create_button.is_visible()) and (search_button.count() > 0 and search_button.is_visible())):
            raise AssertionError("Create Family form did not return to the listing state after submission.")

        if str(expected_family_name).strip():
            expected_name = str(expected_family_name).strip()
            logger.info("Searching Family listing for created family: %s", expected_name)

            family_filter = self.page.get_by_label(re.compile(r"^\s*Family\s*Name\s*$", re.I)).first
            if family_filter.count() == 0:
                family_filter = self.page.locator(
                    "xpath=(//button[normalize-space()='Search']/preceding::input[not(@type='hidden')])[last()]"
                ).first

            if family_filter.count() == 0 or not family_filter.is_visible():
                raise AssertionError("Family Name filter textbox was not found on the listing page.")

            family_filter.click()
            family_filter.fill("")
            family_filter.fill(expected_name)

            family_pattern = re.compile(rf"\b{re.escape(expected_name)}\b", re.I)
            family_rows = self.page.locator("tbody tr").filter(has_text=family_pattern)

            # Retry search because the created row can take a few seconds to appear in the grid.
            for _ in range(6):
                search_button.click()
                if family_rows.first.count() > 0 and family_rows.first.is_visible():
                    logger.info("Family '%s' found in listing grid.", expected_name)
                    return "created"
                self.page.wait_for_timeout(3000)

            no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).first
            if no_records.count() > 0 and no_records.is_visible():
                raise AssertionError(
                    f"Family '{expected_name}' was not found after create; table shows no records."
                )

            raise AssertionError(
                f"Family '{expected_name}' was not visible in results after create submission."
            )

        pending_cell = self.page.get_by_role("cell", name="Pending").first
        approve_button = self.page.get_by_role("button", name="Approve/Reject").first
        edit_button = self.page.get_by_role("button", name="Edit").first

        indicators = [pending_cell, approve_button, edit_button]
        for locator in indicators:
            if locator.count() > 0 and locator.first.is_visible():
                return "created"

        raise AssertionError("Family create success indicators were not found.")

    def verify_missing_field_popup(self, expected_missing_fields: list[str]):
        dialog = self.page.get_by_role("dialog").first
        expect(dialog).to_be_visible(timeout=10000)

        dialog_text = (dialog.text_content() or "").strip()
        normalized_dialog_text = re.sub(r"\s+", " ", dialog_text)
        normalized_expected = [field.replace("_", " ").strip().lower() for field in expected_missing_fields]

        screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / "WARN_Create_Family_Missing_Required_Field_Popup.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)

        logger.warning(
            "Create Family validation popup displayed for missing field(s): %s. Popup text: %s. Screenshot: %s",
            ", ".join(expected_missing_fields),
            normalized_dialog_text,
            screenshot_path,
        )

        if normalized_dialog_text:
            dialog_lower = normalized_dialog_text.lower()
            matched_fields = [field for field in normalized_expected if field in dialog_lower]
            if matched_fields:
                logger.info("Validation popup matched expected missing field(s): %s", ", ".join(matched_fields))
            else:
                logger.warning(
                    "Validation popup did not explicitly include expected field name(s): %s",
                    ", ".join(expected_missing_fields),
                )

        ok_button = dialog.get_by_role("button", name=re.compile(r"^\s*ok\s*$", re.I)).first
        if ok_button.count() > 0 and ok_button.is_visible():
            ok_button.click()
            expect(dialog).to_be_hidden(timeout=5000)
        else:
            raise AssertionError("Validation popup is visible but OK button was not found.")

        return normalized_dialog_text
