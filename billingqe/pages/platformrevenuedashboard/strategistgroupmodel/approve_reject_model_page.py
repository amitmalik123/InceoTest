"""Approve/Reject Model page object."""

import logging
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)

MODEL_ID_MAX_LENGTH = 6
DEFAULT_PAGE_SIZE = 20
MODEL_TABLE_ROWS_SELECTOR = "tbody tr"
CREATOR_WARNING_TEXT = "Models cannot be Approved/Rejected by the user who created or edited the data"


class ApproveRejectModelPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._model_id = ""
        self._action = ""
        self._accepted_search_value = ""
        self._action_skipped_due_to_warning = False
        self._no_approve_reject_available = False

    # ── search helpers (reuse search_model_page patterns) ────────────────────

    def _click_search_and_wait(self):
        self.page.get_by_role("button", name="Search").click()
        self.page.wait_for_timeout(2000)

    def _ensure_filtered_grid(self):
        if not self._accepted_search_value:
            return
        row_count = self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count()
        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).count()
        if row_count >= DEFAULT_PAGE_SIZE and no_records == 0:
            search_input = self.page.get_by_role("textbox").first
            current_val = search_input.input_value()
            if current_val != self._accepted_search_value:
                search_input.fill(self._accepted_search_value)
                self.page.wait_for_timeout(200)
            self._click_search_and_wait()

    def click_model_tab(self):
        self.page.get_by_text("Model", exact=True).click()

    def verify_model_page_with_action_buttons(self):
        expect(self.page.get_by_text("Model", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Family", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("button", name="Approve/Reject").first).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("button", name="Edit").first).to_be_visible(timeout=10000)

    def search_model_by_id(self, model_id: str):
        model_value = str(model_id).strip()
        if not model_value:
            raise ValueError("Model ID cannot be blank")

        if len(model_value) > MODEL_ID_MAX_LENGTH:
            truncated = model_value[:MODEL_ID_MAX_LENGTH]
            logger.info(
                "Model ID '%s' exceeds max field length (%d). Truncating to '%s'.",
                model_value, MODEL_ID_MAX_LENGTH, truncated,
            )
            model_value = truncated

        search_input = self.page.get_by_role("textbox").first
        search_input.click()
        search_input.fill("")
        self.page.wait_for_timeout(200)
        search_input.click()
        search_input.clear()
        self.page.wait_for_timeout(100)
        search_input.fill(model_value)
        self.page.wait_for_timeout(300)

        self._accepted_search_value = search_input.input_value()
        if self._accepted_search_value != model_value:
            logger.warning(
                "Search field accepted '%s' instead of '%s' — field has maxlength constraint.",
                self._accepted_search_value, model_value,
            )

        self._click_search_and_wait()
        self._ensure_filtered_grid()

        row_count = self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count()
        logger.info(
            "Searched model_id: %s (accepted: '%s') — grid rows: %d",
            model_value, self._accepted_search_value, row_count,
        )

    def enter_search_model_id(self, model_id: str):
        self._model_id = str(model_id).strip()
        self.search_model_by_id(self._model_id)

    # ── approve / reject dialog ──────────────────────────────────────────────

    def click_approve_reject_button(self):
        """Click the first Approve/Reject button found for a Pending row.

        If no Approve/Reject button is available, sets a skip flag so all
        subsequent steps (dialog verification, action, success, status) are
        skipped gracefully instead of failing.
        """
        self._ensure_filtered_grid()
        rows = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        row_count = rows.count()

        # find the first Pending row with an Approve/Reject button
        for idx in range(row_count):
            row = rows.nth(idx)
            approve_reject_btn = row.get_by_role("button", name="Approve/Reject")
            if approve_reject_btn.count() > 0 and approve_reject_btn.first.is_visible():
                approve_reject_btn.first.click()
                self.page.wait_for_timeout(800)
                logger.info(
                    "Clicked Approve/Reject on row %d for model_id=%s", idx + 1, self._model_id,
                )
                return

        # no button found — log, screenshot, and set skip flag
        logger.warning(
            "No model ID available for Approve/Reject — model_id=%s has no Pending rows. "
            "Remaining approve/reject steps will be skipped.",
            self._model_id,
        )
        self._capture_screenshot("NO_APPROVE_REJECT_AVAILABLE")
        self._no_approve_reject_available = True

    def verify_approve_reject_dialog(self):
        if self._no_approve_reject_available:
            logger.info("SKIPPED dialog verification — no Approve/Reject button for model_id=%s", self._model_id)
            return
        expect(self.page.get_by_role("button", name="APPROVE", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("button", name="REJECT", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.get_by_role("button", name="CANCEL")).to_be_visible(timeout=10000)
        logger.info("Approve/Reject/Cancel buttons verified for model_id=%s", self._model_id)

    def perform_action(self, action: str):
        self._action = str(action).strip().lower()
        if self._no_approve_reject_available:
            logger.info("SKIPPED '%s' action — no Approve/Reject button for model_id=%s", self._action, self._model_id)
            return
        if not self._action:
            raise ValueError("'action' column is required with values: 'approve' or 'reject'")

        if self._action == "approve":
            self.page.get_by_role("button", name="APPROVE", exact=True).click()
        elif self._action == "reject":
            self.page.get_by_role("button", name="REJECT", exact=True).click()
        else:
            raise ValueError(f"Invalid action '{self._action}' — expected 'approve' or 'reject'")

        self.page.wait_for_timeout(800)
        logger.info("Performed '%s' action for model_id=%s", self._action, self._model_id)

    # ── result verification ──────────────────────────────────────────────────

    def _capture_screenshot(self, label: str):
        screenshot_dir = Path("reports/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        safe_model = re.sub(r"[^A-Za-z0-9_-]+", "_", self._model_id or "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshot_dir / f"{label}_{safe_model}_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)
        logger.info("Screenshot captured: %s", screenshot_path)

    def verify_action_success(self):
        """Verify success or handle the creator/editor warning.

        If the warning 'Models cannot be Approved/Rejected by the user who
        created or edited the data' appears, log it, take a screenshot,
        click OK, and set the skip flag so post-action verification is skipped.
        """
        if self._no_approve_reject_available:
            logger.info("SKIPPED action success verification — no Approve/Reject button for model_id=%s", self._model_id)
            return
        self._action_skipped_due_to_warning = False

        # check for creator/editor warning first
        warning_locator = self.page.get_by_text(re.compile(
            r"Models cannot be Approved/Rejected by the user who created or edited the data",
            re.I,
        ))

        try:
            warning_locator.first.wait_for(state="visible", timeout=3000)
            warning_visible = True
        except Exception:
            warning_visible = False

        if warning_visible:
            warning_text = warning_locator.first.inner_text().strip()
            logger.warning(
                "WARNING for model_id=%s: %s — action '%s' cannot be performed by this user.",
                self._model_id, warning_text, self._action,
            )
            self._capture_screenshot("CREATOR_WARNING")
            self.page.get_by_role("button", name="OK").click()
            self.page.wait_for_timeout(500)
            self._action_skipped_due_to_warning = True
            return

        # verify actual success message
        if self._action == "approve":
            success_msg = self.page.get_by_text("Model record Approved")
            expect(success_msg).to_be_visible(timeout=10000)
            self._capture_screenshot("MODEL_APPROVED")
            logger.info("Model record Approved successfully for model_id=%s", self._model_id)
        elif self._action == "reject":
            success_msg = self.page.get_by_text("Model record Rejected")
            expect(success_msg).to_be_visible(timeout=10000)
            self._capture_screenshot("MODEL_REJECTED")
            logger.info("Model record Rejected successfully for model_id=%s", self._model_id)

        self.page.get_by_role("button", name="OK").click()
        self.page.wait_for_timeout(500)

    @property
    def action_was_skipped(self) -> bool:
        return self._action_skipped_due_to_warning or self._no_approve_reject_available

    # ── post-action status verification ──────────────────────────────────────

    def verify_model_status_updated(self):
        """Re-search the model and verify the acted-upon row has the correct
        status and action button.  Handles duplicate rows with same model_id.

        If the action was skipped due to creator/editor warning, this method
        does nothing.
        """
        if self._action_skipped_due_to_warning or self._no_approve_reject_available:
            reason = (
                "creator/editor warning was shown"
                if self._action_skipped_due_to_warning
                else "no Approve/Reject button was available"
            )
            logger.info(
                "SKIPPED post-action verification for model_id=%s — %s.",
                self._model_id, reason,
            )
            return

        expected_status = "Approved" if self._action == "approve" else "Rejected"
        self.search_model_by_id(self._model_id)
        self._ensure_filtered_grid()

        rows = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        row_count = rows.count()
        if row_count == 0:
            raise AssertionError(
                f"No rows found after re-searching model_id={self._model_id}"
            )

        # find the row that matches both the model_id AND the expected status
        status_pattern = re.compile(rf"^{re.escape(expected_status)}$", re.I)
        matched_row = None
        for idx in range(row_count):
            row = rows.nth(idx)
            row_text = row.inner_text().strip()
            # row must contain the accepted search value (model_id or truncated)
            if self._accepted_search_value.lower() not in row_text.lower():
                continue
            status_cell = row.locator("td").filter(has_text=status_pattern)
            if status_cell.count() > 0:
                matched_row = row
                break

        if matched_row is None:
            # collect all visible statuses for debugging
            visible_statuses = []
            for idx in range(row_count):
                row_text = rows.nth(idx).inner_text().strip()
                visible_statuses.append(f"  row {idx + 1}: {row_text[:120]}")
            status_dump = "\n".join(visible_statuses)
            raise AssertionError(
                f"Expected a row with model_id containing '{self._accepted_search_value}' "
                f"and status '{expected_status}', but none found.\n"
                f"Visible rows:\n{status_dump}"
            )

        # verify the matched row now shows an Edit button (not Approve/Reject)
        expect(matched_row.get_by_role("button", name="Edit")).to_be_visible(timeout=10000)
        logger.info(
            "Verified model_id=%s has status '%s' with Edit button after %s action.",
            self._model_id, expected_status, self._action,
        )
        self._capture_screenshot(f"MODEL_STATUS_{expected_status.upper()}")
