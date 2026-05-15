"""Search Model page object for Strategist Group Model."""

import logging
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


logger = logging.getLogger(__name__)

ACTION_EDIT = "Edit"
ACTION_APPROVE_REJECT = "Approve/Reject"
MODEL_TABLE_ROWS_SELECTOR = "tbody tr"


class SearchModelPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

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

    def search_model_by_id(self, model_id: str):
        model_value = str(model_id).strip()
        if not model_value:
            raise ValueError("Model ID cannot be blank")

        # First, clear any existing search to reset backend state.
        search_input = self.page.get_by_role("textbox").first
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
        
        # Set the search value using type instead of fill to handle input limitations
        search_input.click()
        search_input.clear()  # Ensure field is clear
        self.page.wait_for_timeout(100)
        
        # Type the value character by character with small delays to ensure it captures
        for char in model_value:
            search_input.type(char, delay=50)
        
        self.page.wait_for_timeout(200)

        # Verify search input value is actually set before clicking search
        input_value = search_input.input_value()
        logger.info("Search input before button click: set '%s', got '%s'", model_value, input_value)
        
        if input_value != model_value:
            logger.warning(
                "Search input value mismatch: expected '%s', got '%s'. Clearing and trying fill() method.",
                model_value,
                input_value
            )
            search_input.fill("")
            self.page.wait_for_timeout(100)
            search_input.fill(model_value)
            input_value = search_input.input_value()
            logger.info("After fill(): set '%s', got '%s'", model_value, input_value)

        search_button = self.page.get_by_role("button", name="Search")
        expect(search_button).to_be_visible(timeout=10000)
        
        # Capture the current row count before search to detect grid changes.
        old_row_locator = self.page.locator(MODEL_TABLE_ROWS_SELECTOR)
        old_row_count = old_row_locator.count()
        logger.info("Grid state before search: %d row(s), search value: '%s'", old_row_count, input_value)
        
        search_button.click()

        # Wait for grid refresh indicators when present, then allow UI settle.
        try:
            self.page.locator("[role='progressbar'], [class*='loading'], [class*='spinner'], [class*='skeleton']").first.wait_for(
                state="hidden", timeout=15000
            )
        except Exception:
            pass

        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        self.page.wait_for_timeout(800)
        
        # Verify grid state has actually changed after search.
        for attempt in range(10):
            new_row_count = self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count()
            no_records_msg = self.page.get_by_text(re.compile(r"no\s+records\s+found", re.I)).count()
            
            logger.info(
                "Grid state after search (attempt %d): %d row(s), %d 'no records' message(s)",
                attempt + 1,
                new_row_count,
                no_records_msg
            )
            
            # Search is considered complete when:
            # 1. Row count changed from before, OR
            # 2. "No records found" message appeared, OR
            # 3. After multiple attempts (at least one full cycle through attempts)
            if new_row_count != old_row_count or no_records_msg > 0 or attempt >= 3:
                break
            
            self.page.wait_for_timeout(300)
        
        logger.info("Searched model id: %s", model_value)

    def _capture_no_records_screenshot(self, model_id: str):
        screenshot_dir = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = re.sub(r"[^A-Za-z0-9_-]+", "_", str(model_id).strip()) or "blank"
        screenshot_path = screenshot_dir / f"NO_MODEL_RECORDS_{safe_model}_{timestamp}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=False)
        logger.info("No-record screenshot saved: %s", screenshot_path)

    def has_model_rows(self) -> bool:
        return self.page.locator(MODEL_TABLE_ROWS_SELECTOR).count() > 0

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

        # If we got here, rows have action buttons - data exists unexpectedly
        try:
            sample_text = rows.nth(0).inner_text().strip()[:100]
        except Exception:
            sample_text = "[unable to retrieve text]"
        
        raise AssertionError(
            f"Expected no-record state for model '{model_id}', but result rows with actions are present. "
            f"Sample row text: '{sample_text}'"
        )

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

        logger.info("Validated status-based action button rules for %s model row(s)", row_count)
