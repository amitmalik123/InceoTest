"""Search Model page object for Strategist Group Model."""

import logging
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.billing.platformrevenuedashboard.common.base_page import BasePage


logger = logging.getLogger(__name__)

ACTION_EDIT = "Edit"
ACTION_APPROVE_REJECT = "Approve/Reject"
MODEL_TABLE_ROWS_SELECTOR = "tbody tr"
MODEL_ID_MAX_LENGTH = 6
DEFAULT_PAGE_SIZE = 20


class SearchModelPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._accepted_search_value = ""

    def navigate_to_strategist_group_model(self):
        self.page.get_by_role("link", name="Strategist Group Model").click()
        self.page.wait_for_load_state("domcontentloaded")

    def click_model_tab(self):
        self.page.get_by_text("Model", exact=True).click()

    def verify_model_page_loaded(self):
        expect(self.page.get_by_text("Model", exact=True)).to_be_visible(timeout=10000)
        expect(self.page.locator("div").filter(has_text=re.compile(r"^Model ID$"))).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Family Name").first).to_be_visible(timeout=10000)
        expect(self.page.get_by_text("Status").first).to_be_visible(timeout=10000)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _click_search_and_wait(self):
        """Click Search button and wait briefly for the API response to render."""
        search_button = self.page.get_by_role("button", name="Search")
        search_button.click()
        self.page.wait_for_timeout(2000)

    def _ensure_filtered_grid(self):
        """If the grid still shows the default unfiltered page, re-search once."""
        if not self._accepted_search_value:
            return
        row_count = self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count()
        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).count()
        if row_count >= DEFAULT_PAGE_SIZE and no_records == 0:
            # Grid is still showing default data — re-search silently
            search_input = self.page.get_by_role("textbox").first
            current_val = search_input.input_value()
            if current_val != self._accepted_search_value:
                search_input.fill(self._accepted_search_value)
                self.page.wait_for_timeout(200)
            self._click_search_and_wait()

    # ── Search ───────────────────────────────────────────────────────────────

    def search_model_by_id(self, model_id: str):
        model_value = str(model_id).strip()
        if not model_value:
            raise ValueError("Model ID cannot be blank")

        search_input = self.page.get_by_role("textbox").first
        search_button = self.page.get_by_role("button", name="Search")

        # Step 1: Clear any existing search to reset backend state.
        search_input.click()
        search_input.fill("")
        self.page.wait_for_timeout(200)

        # Try to find and click a "Clear" or "Reset" button if it exists.
        try:
            clear_button = self.page.get_by_role("button", name=re.compile(r"clear|reset", re.I))
            if clear_button.count() > 0:
                clear_button.first.click()
                self.page.wait_for_timeout(400)
                logger.info("Clicked Clear/Reset button to reset search state")
        except Exception:
            pass

        # Step 2: Truncate to max field length and fill the search value.
        if len(model_value) > MODEL_ID_MAX_LENGTH:
            truncated = model_value[:MODEL_ID_MAX_LENGTH]
            logger.info(
                "Model ID '%s' exceeds max field length (%d). Truncating to '%s'.",
                model_value, MODEL_ID_MAX_LENGTH, truncated,
            )
            model_value = truncated

        search_input.click()
        search_input.clear()
        self.page.wait_for_timeout(100)
        search_input.fill(model_value)
        self.page.wait_for_timeout(300)

        # Step 3: Read back what the field actually accepted.
        self._accepted_search_value = search_input.input_value()
        if self._accepted_search_value != model_value:
            logger.warning(
                "Search field accepted '%s' (length=%d) instead of '%s' (length=%d) "
                "— field likely has a maxlength constraint. Proceeding with accepted value.",
                self._accepted_search_value,
                len(self._accepted_search_value),
                model_value,
                len(model_value),
            )

        # Step 4: Click Search and wait for results.
        expect(search_button).to_be_visible(timeout=10000)
        self._click_search_and_wait()

        # Step 5: If grid still shows default data, re-search once.
        self._ensure_filtered_grid()

        row_count = self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count()
        logger.info(
            "Searched model id: %s (accepted: '%s') — grid rows: %d",
            model_value,
            self._accepted_search_value,
            row_count,
        )

    # ── Screenshots ──────────────────────────────────────────────────────────

    def _capture_no_records_screenshot(self, model_id: str):
        screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = re.sub(r"[^A-Za-z0-9_-]+", "_", str(model_id).strip()) or "blank"
        screenshot_path = screenshot_dir / f"NO_MODEL_RECORDS_{safe_model}_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)
        logger.info("No-record screenshot saved: %s", screenshot_path)

    # ── Grid state checks ────────────────────────────────────────────────────

    def has_model_rows(self) -> bool:
        """Return True only if the grid has real data rows with action buttons."""
        self._ensure_filtered_grid()

        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I))
        if no_records.count() > 0:
            try:
                if no_records.first.is_visible():
                    return False
            except Exception:
                pass

        rows = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        row_count = rows.count()
        if row_count == 0:
            return False

        # Verify at least one row has an action button (real data, not stale defaults).
        for index in range(row_count):
            row = rows.nth(index)
            try:
                has_edit = row.get_by_role("button", name=ACTION_EDIT).count() > 0
                has_approve_reject = row.get_by_role("button", name=ACTION_APPROVE_REJECT).count() > 0
                if has_edit or has_approve_reject:
                    return True
            except Exception:
                pass

        return False

    def verify_no_records_found(self, model_id: str):
        rows = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        row_count = rows.count()
        logger.info("Checking no-records state: found %d row(s)", row_count)

        # Check for explicit "no records found" message first
        no_records = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I))
        if no_records.count() > 0:
            try:
                if no_records.first.is_visible():
                    self._capture_no_records_screenshot(model_id=model_id)
                    logger.info("No records message found for model: %s", model_id)
                    return
            except Exception:
                pass

        # If no rows, consider it no-records state
        if row_count == 0:
            self._capture_no_records_screenshot(model_id=model_id)
            logger.info("No rows found for model: %s", model_id)
            return

        # Check if rows have actual action buttons (sign of real data)
        has_any_action_button = False
        for index in range(row_count):
            row = rows.nth(index)
            try:
                has_edit = row.get_by_role("button", name=ACTION_EDIT).count() > 0
                has_approve_reject = row.get_by_role("button", name=ACTION_APPROVE_REJECT).count() > 0
                if has_edit or has_approve_reject:
                    has_any_action_button = True
                    break
            except Exception:
                pass

        if not has_any_action_button:
            self._capture_no_records_screenshot(model_id=model_id)
            logger.info("No action buttons found in rows for model: %s", model_id)
            return

        # If we got here, rows have action buttons — data exists unexpectedly
        try:
            sample_text = rows.nth(0).inner_text().strip()[:100]
        except Exception:
            sample_text = "[unable to retrieve text]"

        raise AssertionError(
            f"Expected no-record state for model '{model_id}', but result rows with actions are present. "
            f"Sample row text: '{sample_text}'"
        )

    # ── Status & action button validation ────────────────────────────────────

    def _normalize_status(self, row_locator) -> str:
        status_patterns = {
            "pending": re.compile(r"^Pending$", re.I),
            "new": re.compile(r"^New$", re.I),
            "approved": re.compile(r"^Approved$", re.I),
            "approve": re.compile(r"^Approve$", re.I),
            "rejected": re.compile(r"^Rejected$", re.I),
            "reject": re.compile(r"^Reject$", re.I),
        }
        for status_key, pattern in status_patterns.items():
            if row_locator.locator("td").filter(has_text=pattern).count() > 0:
                return status_key
        return ""

    def verify_action_button_visibility_by_status(self):
        self._ensure_filtered_grid()

        rows = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        row_count = rows.count()
        if row_count == 0:
            # Allow a short settling window for async grid refresh before asserting.
            for _ in range(8):
                self.page.wait_for_timeout(250)
                row_count = rows.count()
                if row_count > 0:
                    break

        logger.info("Found %d model row(s) after search", row_count)
        if row_count == 0:
            raise AssertionError(
                "Expected model search results, but no table rows were rendered for a valid model_id"
            )

        expected_action_by_status = {
            "pending": ACTION_APPROVE_REJECT,
            "new": ACTION_EDIT,
            "approved": ACTION_EDIT,
            "approve": ACTION_EDIT,
            "rejected": ACTION_EDIT,
            "reject": ACTION_EDIT,
        }

        for index in range(row_count):
            row = rows.nth(index)
            status_key = self._normalize_status(row)
            if not status_key:
                row_text = row.inner_text().strip()
                raise AssertionError(
                    f"Could not identify status for row {index + 1}. Row text: '{row_text}'"
                )

            expected_action = expected_action_by_status[status_key]
            opposite_action = ACTION_EDIT if expected_action == ACTION_APPROVE_REJECT else ACTION_APPROVE_REJECT

            expected_button = row.get_by_role("button", name=expected_action)
            opposite_button = row.get_by_role("button", name=opposite_action)

            if expected_button.count() == 0:
                raise AssertionError(
                    f"Row {index + 1} with status '{status_key}' does not show expected '{expected_action}' button"
                )
            if opposite_button.count() > 0:
                raise AssertionError(
                    f"Row {index + 1} with status '{status_key}' shows unexpected '{opposite_action}' button"
                )

        logger.info("Validated status-based action button rules for %d model row(s)", row_count)
