"""Approve/Reject Family page object."""

import logging
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)


class ApproveRejectFamilyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def click_family_tab(self):
        self.page.get_by_text("Family", exact=True).click()

    def verify_family_page_with_approve_reject(self):
        expect(self.page.locator("div").filter(has_text=re.compile(r"^Create Model Family$"))).to_be_visible()
        expect(self.page.get_by_role("button", name="Create Model Family")).to_be_visible()
        expect(self.page.get_by_role("button", name="Approve/Reject").first).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("button", name="Edit").first).to_be_visible(timeout=10000)

    def enter_search_family_name(self, family_name: str):
        search_input = self.page.get_by_role("textbox").first
        search_input.click()
        search_input.fill(family_name)

    def click_search(self):
        search_button = self.page.get_by_role("button", name="Search")
        expect(search_button).to_be_visible()
        search_button.click()
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            # Some environments keep background network activity; continue with DOM-based checks.
            pass
        self.page.wait_for_timeout(500)

    def verify_search_results(self):
        table_rows = self.page.locator("tbody tr")
        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).first

        try:
            expect(table_rows.first).to_be_visible(timeout=15000)
            return
        except AssertionError as original_error:
            if no_records.count() > 0 and no_records.is_visible():
                raise AssertionError(
                    "Search returned no records when table results were expected."
                ) from original_error

            row_count = table_rows.count()
            raise AssertionError(
                f"Search did not render visible table rows. Current row count: {row_count}"
            ) from original_error

    def select_search_status(self, status: str):
        status_value = str(status or "").strip() or "ALL"
        status_dropdown = self.page.get_by_role("combobox").first
        expect(status_dropdown).to_be_visible(timeout=10000)
        try:
            status_dropdown.select_option(status_value)
        except Exception:
            status_dropdown.select_option(label=status_value)

    def search_family_with_filters(self, family_name: str, status: str = "ALL"):
        self.enter_search_family_name(family_name)
        self.select_search_status(status)
        self.click_search()

    def verify_search_results_match_text(self, search_text: str):
        normalized_search = str(search_text).strip().lower()
        if not normalized_search:
            raise ValueError("Search text cannot be blank for search result validation")

        rows = self.page.locator("tbody tr")
        row_count = rows.count()
        if row_count == 0:
            raise AssertionError("Search returned no table rows when matching rows were expected")

        for index in range(row_count):
            row_text = rows.nth(index).inner_text().strip().lower()
            if normalized_search not in row_text:
                raise AssertionError(
                    f"Row {index + 1} does not match search text '{search_text}'. Row text: '{row_text}'"
                )

    def verify_search_results_have_status(self, expected_status: str):
        target_status = str(expected_status).strip()
        if not target_status:
            raise ValueError("Expected status cannot be blank")

        rows = self.page.locator("tbody tr")
        row_count = rows.count()
        if row_count == 0:
            raise AssertionError("Search returned no table rows when status-matched rows were expected")

        pattern = re.compile(rf"^{re.escape(target_status)}$", re.I)
        for index in range(row_count):
            row = rows.nth(index)
            status_cell = row.locator("td").filter(has_text=pattern)
            if status_cell.count() == 0:
                raise AssertionError(
                    f"Row {index + 1} does not contain expected status '{target_status}'."
                )

    def verify_search_results_have_action_buttons(self):
        rows = self.page.locator("tbody tr")
        row_count = rows.count()
        if row_count == 0:
            raise AssertionError("Search returned no rows when action-button validation was expected")

        for index in range(row_count):
            row = rows.nth(index)
            has_edit = row.get_by_role("button", name="Edit").count() > 0
            has_approve_reject = row.get_by_role("button", name="Approve/Reject").count() > 0
            if not (has_edit or has_approve_reject):
                raise AssertionError(
                    f"Row {index + 1} does not contain Edit or Approve/Reject action button"
                )

    def verify_no_records_found_message(self):
        no_records_message = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).first
        expect(no_records_message).to_be_visible(timeout=10000)

        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshot_dir / f"NO_RECORDS_FOUND_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)

    def click_approve_reject_button(self):
        approve_reject_button = self.page.get_by_role("button", name="Approve/Reject").first
        expect(approve_reject_button).to_be_visible()
        approve_reject_button.click()
        self.page.wait_for_timeout(800)

    def verify_approve_reject_dialog(self):
        expect(self.page.get_by_role("heading", name="Approve / Reject Family")).to_be_visible()
        expect(self.page.get_by_role("button", name="APPROVE")).to_be_visible()
        expect(self.page.get_by_role("button", name="REJECT")).to_be_visible()
        expect(self.page.get_by_role("button", name="CANCEL")).to_be_visible()

    def click_approve(self):
        approve_button = self.page.get_by_role("button", name="APPROVE")
        expect(approve_button).to_be_visible()
        approve_button.click()
        self.page.wait_for_timeout(800)

    def click_reject(self):
        reject_button = self.page.get_by_role("button", name="REJECT")
        expect(reject_button).to_be_visible()
        reject_button.click()
        self.page.wait_for_timeout(800)

    def click_cancel(self):
        cancel_button = self.page.get_by_role("button", name="CANCEL")
        expect(cancel_button).to_be_visible()
        cancel_button.click()
        self.page.wait_for_timeout(800)

    def _capture_action_screenshot(self, action: str, family_name: str = ""):
        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        normalized_family = re.sub(r"[^A-Za-z0-9_-]+", "_", str(family_name).strip()) or "unknown_family"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"{action}_{normalized_family}_{timestamp}.png"
        screenshot_path = screenshot_dir / screenshot_name

        self.page.screenshot(path=str(screenshot_path), full_page=False)

    def verify_approval_success_message(self, family_name: str = ""):
        success_message = self.page.get_by_text("Family record Approved")
        expect(success_message).to_be_visible(timeout=10000)
        self._capture_action_screenshot("APPROVED", family_name)

    def verify_rejection_success_message(self, family_name: str = ""):
        success_message = self.page.get_by_text("Family record Rejected")
        expect(success_message).to_be_visible(timeout=10000)
        self._capture_action_screenshot("REJECTED", family_name)

    def click_ok_button(self):
        ok_button = self.page.get_by_role("button", name="OK")
        expect(ok_button).to_be_visible()
        ok_button.click()
        self.page.wait_for_timeout(800)

    def verify_family_status_approved(self, family_name: str):
        self.enter_search_family_name(family_name)
        self.click_search()

        target_row = self.page.locator("tbody tr").filter(has_text=family_name).first
        expect(target_row).to_be_visible(timeout=10000)

        approved_status = target_row.locator("td").filter(has_text=re.compile(r"^Approved$", re.I))
        expect(approved_status.first).to_be_visible(timeout=10000)

        edit_button = target_row.get_by_role("button", name="Edit")
        expect(edit_button).to_be_visible(timeout=10000)

    def verify_family_status_rejected(self, family_name: str):
        self.enter_search_family_name(family_name)
        self.click_search()

        target_row = self.page.locator("tbody tr").filter(has_text=family_name).first
        expect(target_row).to_be_visible(timeout=10000)

        rejected_status = target_row.locator("td").filter(has_text=re.compile(r"^Rejected$", re.I))
        expect(rejected_status.first).to_be_visible(timeout=10000)

        edit_button = target_row.get_by_role("button", name="Edit")
        expect(edit_button).to_be_visible(timeout=10000)
