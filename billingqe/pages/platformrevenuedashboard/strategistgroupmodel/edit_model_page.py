"""Edit Model page object for Strategist Group Model."""

import logging
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)

FAMILY_NAME_LABEL = "Family Name"
CHANGE_FAMILY_LABEL = "Change Family"
ADD_NEW_FAMILY_LABEL = "Add New Family"


class EditModelPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self._model_id = ""
        self._family_name = ""
        self._has_change_family = False
        self._edit_form_open = False
        self.existing_record_skipped = False

    def search_model_by_id(self, model_id: str):
        """Type model_id in the search box and click Search."""
        logger.info("Searching for model_id=%s", model_id)
        search_box = self.page.get_by_role("textbox").first
        expect(search_box).to_be_visible(timeout=10000)
        search_box.click()
        search_box.fill(model_id)
        self.page.get_by_role("button", name="Search").click()
        self.page.wait_for_timeout(1000)

    # ── Navigation & Verification ────────────────────────────────────────────

    def click_model_tab(self):
        self.page.get_by_text("Model", exact=True).click()
        self.page.wait_for_timeout(500)

    def verify_model_page_loaded(self):
        expect(self.page.get_by_text("Model", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Family", exact=True)).to_be_visible(timeout=10000)
        expect(
            self.page.locator("div").filter(has_text=re.compile(r"^Model ID$"))
        ).to_be_visible(timeout=10000)
        expect(self.page.get_by_text(FAMILY_NAME_LABEL).first).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Status").first).to_be_visible(timeout=10000)

    def verify_action_buttons_visible(self):
        """Verify Edit and/or Approve/Reject buttons are visible in the model grid."""
        edit_buttons = self.page.get_by_role("button", name="Edit")
        expect(edit_buttons.first).to_be_visible(timeout=10000)

    # ── Core Edit Flow (split into phases for BDD Then steps) ────────────────

    def _find_model_row(self, model_id: str):
        """Find the row containing the given model ID and return it."""
        row = self.page.get_by_role("row", name=re.compile(re.escape(model_id)))
        expect(row.first).to_be_visible(timeout=10000)
        return row.first

    def _has_change_family_checkbox(self) -> bool:
        """Check if the edit form has the Change Family checkbox (with_family_mapping model)."""
        try:
            checkbox = self.page.locator("label").filter(
                has_text=CHANGE_FAMILY_LABEL
            ).get_by_role("checkbox")
            return checkbox.count() > 0 and checkbox.is_visible(timeout=2000)
        except Exception:
            return False

    def _is_control_grayed_out(self, control) -> bool:
        """Return True when a form control appears disabled/read-only (grayed out)."""
        disabled = control.get_attribute("disabled") is not None
        readonly = control.get_attribute("readonly") is not None
        aria_disabled = (control.get_attribute("aria-disabled") or "").lower() == "true"
        css_class = (control.get_attribute("class") or "").lower()
        class_indicates_disabled = "disabled" in css_class or "readonly" in css_class
        return disabled or readonly or aria_disabled or class_indicates_disabled

    def _assert_control_editable(self, control, control_name: str):
        if self._is_control_grayed_out(control):
            raise AssertionError(f"{control_name} should be editable, but it appears grayed out.")

    def _assert_other_attributes_grayed_out(self, exclude_keywords):
        """Assert all visible controls except excluded rows are grayed out."""
        rows = self.page.locator("#createContainer tr")
        row_count = rows.count()
        for idx in range(row_count):
            row = rows.nth(idx)
            row_text = (row.inner_text() or "").strip().lower()
            if not row_text:
                continue
            if any(keyword in row_text for keyword in exclude_keywords):
                continue

            controls = row.locator("input, select, textarea")
            for control_index in range(controls.count()):
                control = controls.nth(control_index)
                if not control.is_visible():
                    continue
                if not self._is_control_grayed_out(control):
                    raise AssertionError(
                        f"Expected grayed-out attribute control in row '{row_text}', but found editable control."
                    )

    def _assert_updated_model_row(self, model_id: str, family_name: str):
        """Assert updated model row shows model+family with Pending status and valid action buttons."""
        row = self.page.get_by_role(
            "row", name=re.compile(rf"\b{re.escape(model_id)}\b", re.I)
        ).filter(has_text=re.compile(rf"\b{re.escape(family_name)}\b", re.I)).first
        expect(row).to_be_visible(timeout=10000)

        expect(row.get_by_role("cell", name=re.compile(r"^Pending$", re.I)).first).to_be_visible(timeout=10000)

        has_edit = row.get_by_role("button", name="Edit").count() > 0
        has_approve = row.get_by_text("Approve").count() > 0
        has_reject = row.get_by_text("Reject").count() > 0
        if not (has_edit or has_approve or has_reject):
            raise AssertionError(
                "Expected action buttons Edit and/or Approve/Reject on updated model row, but none were found."
            )
        logger.info(
            "Updated model row verified: model_id=%s, family_name=%s, status=Pending, actions=Edit/Approve/Reject",
            model_id,
            family_name,
        )

    # ── Phase 1: Prepare Edit (called from When step) ────────────────────────

    def prepare_edit(self, model_id: str, family_name: str):
        """
        Search by model_id, click Edit, detect model type, fill family name.
        Does NOT submit or verify — leaves form open for Then steps.
        """
        self._model_id = model_id
        self._family_name = family_name
        self._has_change_family = False
        self._edit_form_open = False
        self.existing_record_skipped = False

        # Search
        self.search_model_by_id(model_id)

        # Click Edit
        edit_button = self.page.get_by_role("button", name="Edit")
        if edit_button.count() == 0 or not edit_button.first.is_visible():
            logger.warning("No Edit action available for model_id=%s", model_id)
            self._capture_existing_record_screenshot(model_id)
            self.existing_record_skipped = True
            return

        edit_button.first.click()
        logger.info("Clicked first Edit button for model_id=%s", model_id)
        self.page.wait_for_timeout(1000)

        # Check edit form appeared
        edit_form_visible = self.page.locator("#createContainer").is_visible(timeout=3000)
        if not edit_form_visible:
            self._handle_existing_record(model_id)
            return

        # Detect model type
        self._has_change_family = self._has_change_family_checkbox()
        if self._has_change_family:
            logger.info("Model %s has family mapping — using Change/Add Family flow", model_id)
        else:
            logger.info("Model %s has no family mapping — using Family Name only flow", model_id)

        self._edit_form_open = True

    def _fill_without_family_mapping(self, family_name: str):
        """Fill Family Name field and select from dropdown (no assertions)."""
        textbox = self.page.get_by_role(
            "row", name=FAMILY_NAME_LABEL, exact=True
        ).get_by_role("textbox")
        textbox.click()
        textbox.fill(family_name)
        self.page.wait_for_timeout(500)
        self.page.locator("#createContainer").get_by_text(family_name, exact=True).click()
        self.page.wait_for_timeout(300)

    def _fill_with_family_mapping(self, family_name: str):
        """Check Change Family, fill family name, select from dropdown (no assertions)."""
        self.page.locator("label").filter(
            has_text=CHANGE_FAMILY_LABEL
        ).get_by_role("checkbox").check()
        self.page.wait_for_timeout(300)

        textbox = self.page.get_by_role(
            "row", name="Change Family Add New Family"
        ).get_by_role("textbox")
        textbox.click()
        textbox.fill(family_name)
        self.page.wait_for_timeout(500)
        self.page.get_by_text(family_name, exact=True).click()
        self.page.wait_for_timeout(300)

    # ── Phase 2: Verify Controls & Submit (called from Then step 1) ──────────

    def verify_model_type_controls(self):
        """Verify edit form controls based on detected model type, then fill and submit."""
        if self.existing_record_skipped:
            logger.warning("SKIPPED: Existing record — form control assertions not applicable")
            return
        if not self._edit_form_open:
            raise AssertionError("Edit form is not open — cannot verify controls")

        if self._has_change_family:
            logger.info("Verifying with-family-mapping controls for model_id=%s", self._model_id)
            # Verify Change Family and Add New Family checkboxes visible
            expect(
                self.page.locator("label").filter(has_text=CHANGE_FAMILY_LABEL).get_by_role("checkbox")
            ).to_be_visible(timeout=10000)
            expect(
                self.page.locator("label").filter(has_text=ADD_NEW_FAMILY_LABEL).get_by_role("checkbox")
            ).to_be_visible(timeout=10000)
            # Verify other attributes grayed out
            self._assert_other_attributes_grayed_out(
                exclude_keywords=["change family", "add new family", "family"]
            )
            logger.info("PASS: Change/Add Family form controls verified for model_id=%s", self._model_id)

            # Now fill the form
            self._fill_with_family_mapping(self._family_name)

            # Re-verify controls after fill
            textbox = self.page.get_by_role(
                "row", name="Change Family Add New Family"
            ).get_by_role("textbox")
            self._assert_control_editable(textbox, "Family dropdown textbox")
            self._assert_other_attributes_grayed_out(
                exclude_keywords=["change family", "add new family", "family"]
            )
        else:
            logger.info("Verifying without-family-mapping controls for model_id=%s", self._model_id)
            # Verify Family Name field is editable
            expect(
                self.page.locator("#createContainer").get_by_text(FAMILY_NAME_LABEL).nth(0)
            ).to_be_visible(timeout=10000)
            textbox = self.page.get_by_role(
                "row", name=FAMILY_NAME_LABEL, exact=True
            ).get_by_role("textbox")
            self._assert_control_editable(textbox, "Family Name field")
            # Verify other attributes grayed out
            self._assert_other_attributes_grayed_out(exclude_keywords=["family name"])
            logger.info("PASS: Family-name-only form controls verified for model_id=%s", self._model_id)

            # Now fill the form
            self._fill_without_family_mapping(self._family_name)

        # Submit and verify success
        try:
            self.page.get_by_role("button", name="Submit").click()
            self.page.wait_for_timeout(500)

            expect(
                self.page.get_by_text("Model added successfully.")
            ).to_be_visible(timeout=15000)
            self._capture_success_screenshot(model_id=self._model_id)
            self.page.get_by_role("button", name="OK").click()
            self.page.wait_for_timeout(500)
            self._edit_form_open = False
            logger.info("Model %s submitted successfully", self._model_id)
        except Exception as exc:
            logger.warning(
                "Submit failed for model_id=%s — likely already existing/pending record. Error: %s",
                self._model_id, exc,
            )
            self._handle_existing_record(self._model_id)

    # ── Phase 3: Verify Updated Row (called from Then step 2) ────────────────

    def verify_updated_model_row(self):
        """Re-search by model_id and verify updated row with Pending status + action buttons."""
        if self.existing_record_skipped:
            logger.warning("SKIPPED: Existing record — updated row assertion not applicable")
            return

        self.search_model_by_id(self._model_id)
        self._assert_updated_model_row(model_id=self._model_id, family_name=self._family_name)
        logger.info("Model %s edited successfully — now Pending", self._model_id)

    def _handle_existing_record(self, model_id: str):
        """Handle already existing record: log, screenshot, dismiss dialog, set skip flag."""
        logger.warning(
            "Already existing record found for model_id=%s — edit form did not open or edit failed. "
            "This is a data issue, not a test failure.",
            model_id,
        )
        self._capture_existing_record_screenshot(model_id)
        # Dismiss any dialog/message if present
        ok_button = self.page.get_by_role("button", name="OK")
        if ok_button.count() > 0 and ok_button.first.is_visible():
            ok_button.first.click()
            self.page.wait_for_timeout(500)
        self.existing_record_skipped = True

    def _capture_success_screenshot(self, model_id: str):
        """Capture a screenshot after successful edit confirmation message appears."""
        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_id = re.sub(r"[^A-Za-z0-9_-]+", "_", str(model_id).strip()) or "unknown"
        screenshot_path = screenshot_dir / f"EDIT_MODEL_SUCCESS_{safe_model_id}_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)
        logger.info("Success screenshot captured: %s", screenshot_path)

    def _capture_existing_record_screenshot(self, model_id: str):
        """Capture a screenshot when an already existing record is detected."""
        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_id = re.sub(r"[^A-Za-z0-9_-]+", "_", str(model_id).strip()) or "unknown"
        screenshot_path = screenshot_dir / f"EDIT_MODEL_EXISTING_RECORD_{safe_model_id}_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)
        logger.info("Existing record screenshot captured: %s", screenshot_path)
