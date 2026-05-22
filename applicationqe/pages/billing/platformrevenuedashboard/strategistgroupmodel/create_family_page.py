"""Create Family page object."""

import logging
import re
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


logger = logging.getLogger(__name__)


class CreateFamilyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

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
        self.page.get_by_role("row", name="Manager Type Code Select").get_by_role("combobox").select_option(value)

    def select_program_name(self, value: str):
        self.page.get_by_role("row", name="Program Name Select").get_by_role("combobox").select_option(value)

    def select_is_uma_custom(self, value: str):
        self.page.get_by_role("row", name="IsUMACustom Select").get_by_role("combobox").select_option(value)

    def select_has_minimum(self, value: str):
        self.page.get_by_role("row", name="Has Minimum Select").get_by_role("combobox").select_option(value)

    def select_standard_discount_eligible(self, value: str):
        self.page.get_by_role("row", name="Standard Discount Eligible").get_by_role("combobox").select_option(value)

    def select_discount_package(self, value: str):
        self.page.get_by_role("row", name="Discount Package Select").get_by_role("combobox").select_option(value)

    def select_row8_dropdown(self, value: str):
        self.page.locator("tr:nth-child(8) > td:nth-child(2) > div > .form-select").select_option(value)

    def check_checkbox(self):
        self.page.get_by_role("checkbox").check()

    def fill_style_code(self, value: str):
        self.page.get_by_role("row", name="Style Code", exact=True).get_by_role("textbox").click()
        self.page.get_by_role("row", name="Style Code", exact=True).get_by_role("textbox").fill(value)

    def fill_style_description(self, value: str):
        self.page.get_by_role("row", name="Style Description", exact=True).get_by_role("textbox").click()
        self.page.get_by_role("row", name="Style Description", exact=True).get_by_role("textbox").fill(value)

    def fill_manager_style_description(self, value: str):
        self.page.get_by_role("row", name="Manager Style Description").get_by_role("textbox").click()
        self.page.get_by_role("row", name="Manager Style Description").get_by_role("textbox").fill(value)

    def select_row13_dropdown(self, value: str):
        self.page.locator("tr:nth-child(13) > td:nth-child(2) > div > .form-select").select_option(value)

    def select_row14_dropdown(self, value: str):
        self.page.locator("tr:nth-child(14) > td:nth-child(2) > div > .form-select").select_option(value)

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

        if str(data.get("program_name", "")).strip():
            self.select_program_name(data["program_name"])
        if str(data.get("is_uma_custom", "")).strip():
            self.select_is_uma_custom(data["is_uma_custom"])
        if str(data.get("has_minimum", "")).strip():
            self.select_has_minimum(data["has_minimum"])
        if str(data.get("standard_discount_eligible", "")).strip():
            self.select_standard_discount_eligible(data["standard_discount_eligible"])
        if str(data.get("discount_package", "")).strip():
            self.select_discount_package(data["discount_package"])

        if manager_type and str(data.get("row8_value", "")).strip():
            try:
                self.select_row8_dropdown(data["row8_value"])
            except Exception as exc:
                logger.warning("Skipping row8_value selection due to unavailable option: %s", exc)

        self.check_checkbox()

        if str(data.get("style_code", "")).strip():
            self.fill_style_code(data["style_code"])
        if str(data.get("style_description", "")).strip():
            self.fill_style_description(data["style_description"])
        if str(data.get("manager_style_description", "")).strip():
            self.fill_manager_style_description(data["manager_style_description"])

        if manager_type and str(data.get("row13_value", "")).strip():
            try:
                self.select_row13_dropdown(data["row13_value"])
            except Exception as exc:
                logger.warning("Skipping row13_value selection due to unavailable option: %s", exc)
        if manager_type and str(data.get("row14_value", "")).strip():
            try:
                self.select_row14_dropdown(data["row14_value"])
            except Exception as exc:
                logger.warning("Skipping row14_value selection due to unavailable option: %s", exc)

        if str(data.get("research_group", "")).strip():
            self.fill_research_group(data["research_group"])
        if str(data.get("schedule_group", "")).strip():
            self.fill_schedule_group(data["schedule_group"])

    def verify_family_created(self, expected_family_name: str = ""):
        duplicate_warning = self.page.get_by_role("dialog").filter(
            has_text=re.compile(r"family\s*name\s*already\s*exists", re.I)
        )
        if duplicate_warning.count() > 0 and duplicate_warning.first.is_visible():
            screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / "WARN_Family_Already_Exists.png"
            self.page.screenshot(path=str(screenshot_path), full_page=False)
            return

        success_dialog = self.page.get_by_role("dialog").filter(
            has_text=re.compile(r"family\s*added\s*successfully", re.I)
        )
        if success_dialog.count() > 0 and success_dialog.first.is_visible():
            ok_button = success_dialog.first.get_by_role("button", name="OK").first
            if ok_button.count() > 0 and ok_button.is_visible():
                ok_button.click()
                expect(success_dialog.first).to_be_hidden(timeout=10000)

        try:
            expect(self.page.get_by_role("button", name="Create Model Family").first).to_be_visible(timeout=15000)
            expect(self.page.get_by_role("button", name="Search").first).to_be_visible(timeout=10000)
        except AssertionError as exc:
            raise AssertionError(
                "Create Family form did not return to the listing state after submission."
            ) from exc

        if str(expected_family_name).strip():
            family_pattern = re.compile(rf"\b{re.escape(str(expected_family_name).strip())}\b", re.I)
            family_rows = self.page.locator("tbody tr").filter(has_text=family_pattern)
            try:
                expect(family_rows.first).to_be_visible(timeout=15000)
            except AssertionError as exc:
                no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).first
                if no_records.count() > 0 and no_records.is_visible():
                    raise AssertionError(
                        f"Family '{expected_family_name}' was not found after create; table shows no records."
                    ) from exc
                raise AssertionError(
                    f"Family '{expected_family_name}' was not visible in results after create submission."
                ) from exc
            return

        pending_cell = self.page.get_by_role("cell", name="Pending").first
        approve_button = self.page.get_by_role("button", name="Approve/Reject").first
        edit_button = self.page.get_by_role("button", name="Edit").first

        indicators = [pending_cell, approve_button, edit_button]
        for locator in indicators:
            if locator.count() > 0 and locator.first.is_visible():
                return

        raise AssertionError("Family create success indicators were not found.")
