"""APro Proposal Allocation step (wizard-2)."""

import time

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalAllocationPage(BasePage):
    """Page object for APro proposal Allocation step (wizard-2).

    Handles allocation grid selection, tab filtering, and card population
    with allocation details, risk/reward data, and performance grids.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 3 (Allocation) container
        self.step_allocation_panel: Locator = page.locator("#proposal-wizard-2")

        # Allocation grid rows (data rows only, excludes header)
        self.ALLOCATION_ROWS_SELECTOR = '#proposal-wizard-2 [role="row"][data-uid]'
        self.allocation_rows: Locator = self.page.locator(self.ALLOCATION_ROWS_SELECTOR)

        # Filter tabs
        self.filter_tab_objective: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="objective"]'
        )
        self.filter_tab_performance: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="performance"]'
        )
        self.filter_tab_fee: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="fee"]'
        )

        # Selected allocation details cards
        self.selected_allocation_card: Locator = page.locator("#proposal-allocation-card")
        self.selected_allocation_details: Locator = page.locator("#proposal-allocation-details")
        self.risk_reward_card: Locator = page.locator("#proposal-risk-reward-card")

    def wait_for_allocation_step(self, timeout: int = 10000) -> None:
        """Wait for the Allocation (wizard step 3, proposal-wizard-2) to be visible."""
        logger.info("Waiting for Allocation (proposal-wizard-2) step to be visible")
        self.wait_for_element(self.step_allocation_panel, state="visible", timeout=timeout)

    def select_objective_tab(self) -> None:
        """Select the Objective filter tab."""
        logger.info("Selecting Objective tab")
        self.click(self.filter_tab_objective)

    def select_performance_tab(self) -> None:
        """Select the Performance filter tab."""
        logger.info("Selecting Performance tab")
        self.click(self.filter_tab_performance)

    def select_fee_tab(self) -> None:
        """Select the Fee filter tab."""
        logger.info("Selecting Fee tab")
        self.click(self.filter_tab_fee)

    def select_allocation(self, index: int = 0) -> str:
        """Select allocation at the given row index.

        Waits for the selected allocation details card to populate,
        returns the allocation name.

        Args:
            index: 0-based row index in the allocation grid

        Returns:
            Allocation name from the selected row
        """
        logger.info(f"Selecting allocation at index {index}")

        # Get the row and click it
        row = self.allocation_rows.nth(index)
        row.wait_for(state="visible", timeout=10000)

        # Extract the allocation name (usually first cell)
        allocation_name = row.locator("td").first.inner_text().strip()
        logger.info(f"Allocation name: {allocation_name}")

        # Click the row to select
        self.click(row)

        # Wait for card details to populate after selection
        self._wait_for_card_populated(self.selected_allocation_card, timeout=10000)

        return allocation_name

    def select_allocation_by_name(self, name: str, timeout: int = 10000) -> None:
        """Select allocation by name (supports partial matching).

        Searches for an allocation row containing the given name as a substring.
        Case-insensitive matching.

        Args:
            name: Allocation name or partial name to match (e.g., "Blackrock 10-90")
            timeout: Wait timeout in ms
        """
        logger.info(f"Selecting allocation by name (partial match): {name}")

        # Find row containing the name (case-insensitive via has_text)
        row = self.allocation_rows.filter(has_text=name)
        row.wait_for(state="visible", timeout=timeout)

        # Click to select
        self.click(row)

        # Wait for card to populate
        self._wait_for_card_populated(self.selected_allocation_card, timeout=timeout)
        logger.info(f"Allocation '{name}' selected")

    def select_allocation_by_partial_name(self, partial_name: str, timeout: int = 10000) -> str:
        """Select allocation by partial name match (case-insensitive).

        Searches all allocation rows for one whose name contains the given text.
        Performs case-insensitive matching.

        Args:
            partial_name: Partial allocation name to search for (e.g., "Blackrock", "Target")
            timeout: Wait timeout in ms

        Returns:
            Full allocation name of the selected row
        """
        logger.info(f"Selecting allocation by partial name: {partial_name}")

        # Use JavaScript to find data row (skip header) with case-insensitive partial match
        result = self.page.evaluate(
            f"""
        (function() {{
            const partial = '{partial_name}'.toLowerCase();
            const rows = document.querySelectorAll('[role="row"][data-uid]');

            for (let row of rows) {{
                const text = row.textContent.toLowerCase();
                if (text.includes(partial)) {{
                    return text.trim();
                }}
            }}
            return null;
        }})()
        """
        )

        if not result:
            raise ValueError(f"No allocation found matching '{partial_name}'")

        # Now select it using the has_text filter
        row = self.allocation_rows.filter(has_text=partial_name)
        row.first.wait_for(state="visible", timeout=timeout)
        self.click(row.first)

        # Wait for card to populate
        self._wait_for_card_populated(self.selected_allocation_card, timeout=timeout)
        logger.info(f"Allocation matching '{partial_name}' selected: {result}")

        return result

    def get_selected_allocation_details(self, timeout: int = 10000) -> dict:
        """Extract details from the selected allocation card.

        Returns:
            Dict with keys: name, description, objective, performance, fees
        """
        logger.info("Retrieving selected allocation details")

        # Wait for card to be visible and populated
        self.wait_for_element(self.selected_allocation_card, state="visible", timeout=timeout)
        self._wait_for_card_populated(self.selected_allocation_card, timeout=timeout)

        # Extract visible text from card
        card_text = self.selected_allocation_card.inner_text()

        details = {
            "card_text": card_text,
            "visible": True,
        }

        logger.info(f"Allocation details: {details}")
        return details

    def is_risk_reward_name_visible(self, expected_name: str, timeout: int = 10000) -> bool:
        """Check if expected allocation name appears in the risk/reward card.

        Args:
            expected_name: Name to search for
            timeout: Wait timeout in ms

        Returns:
            True if name found, False otherwise
        """
        logger.info(f"Checking if '{expected_name}' is visible in risk/reward card")

        try:
            self.wait_for_element(self.risk_reward_card, state="visible", timeout=timeout)
            card_text = self.risk_reward_card.inner_text()

            is_visible = expected_name.lower() in card_text.lower()
            logger.info(f"Name visibility: {is_visible}")
            return is_visible
        except Exception as exc:
            logger.error(f"Error checking risk/reward name: {exc}")
            return False

    def _wait_for_card_populated(self, locator: Locator, timeout: int = 10000) -> None:
        """Wait for a card to be fully populated with content.

        Checks for SVG elements, grid data, or text content as indicators
        of a populated card.

        Args:
            locator: The card locator to wait for
            timeout: Max wait time in ms
        """
        logger.info(f"Waiting for card content to populate for locator: {locator}")

        end_time = time.time() + (timeout / 1000.0)

        while time.time() < end_time:
            try:
                # Check for various indicators of populated content
                if locator.locator("svg").count() > 0:
                    logger.info("Card populated: SVG element found")
                    return

                if locator.locator(".k-grid tbody tr").count() > 0:
                    logger.info("Card populated: Grid rows found")
                    return

                # Check for text content
                text = locator.inner_text().strip()
                if text and len(text) > 20:  # Reasonable amount of text
                    logger.info(f"Card populated: Text content found ({len(text)} chars)")
                    return

                # Brief pause before retry
                self.page.wait_for_timeout(200)

            except Exception:
                # Element may not be fully mounted yet
                self.page.wait_for_timeout(200)
                continue

        raise TimeoutError(f"Card content did not populate within {timeout}ms: {locator}")

    def is_tms_column_visible(self, timeout: int = 5000) -> bool:
        """Check if TMS column is visible in the allocation grid.

        TMS column visibility indicates account-level TMS eligibility.
        If the column is not visible, the account is ineligible and
        the proposal will auto-skip the Tax Management step.

        Args:
            timeout: Wait timeout in ms

        Returns:
            True if TMS column header is visible, False otherwise
        """
        logger.info("Checking if TMS column is visible in allocation grid")

        try:
            # Look for TMS column header in the grid
            # The grid header contains columnheader elements with specific text
            tms_column = self.step_allocation_panel.locator("columnheader:has-text('TMS')")

            # Try to find it with a short timeout
            tms_column.wait_for(state="visible", timeout=timeout)
            logger.info("TMS column is visible - account is TMS-eligible")
            return True

        except Exception as exc:
            logger.info(f"TMS column not visible - account is TMS-ineligible: {exc}")
            return False

    def is_allocation_tms_eligible(
        self, allocation_name: str | None = None, row_index: int | None = None, timeout: int = 5000
    ) -> bool:
        """Check if allocation has TMS eligibility.

        Looks for the TMS icon (img element) in the TMS column of the specified allocation.
        Only meaningful if is_tms_column_visible() returns True.

        Args:
            allocation_name: Allocation name or partial name to search for (e.g., "Blackrock 10-90").
                           If provided, row_index is ignored. Supports partial matching.
            row_index: 0-based row index in the allocation grid (used only if allocation_name is None).
                      Defaults to 0 (first allocation).
            timeout: Wait timeout in ms

        Returns:
            True if allocation has TMS icon/indicator, False otherwise
        """
        try:
            # Determine which row to check
            if allocation_name is not None:
                logger.info(f"Checking if allocation '{allocation_name}' is TMS-eligible")
                # Find row by allocation name (case-insensitive partial match)
                row = self.allocation_rows.filter(has_text=allocation_name)
                row = row.first
                row.wait_for(state="visible", timeout=timeout)
            else:
                # Use row index (default to first row if not specified)
                if row_index is None:
                    row_index = 0
                logger.info(f"Checking if allocation at row {row_index} is TMS-eligible")
                row = self.allocation_rows.nth(row_index)
                row.wait_for(state="visible", timeout=timeout)

            # Look for TMS icon (img) in the TMS column cell of this row
            # The TMS column is typically the 3rd column in the grid
            tms_cell = row.locator("td").nth(2)  # 0-indexed: 0=Name, 1=Program, 2=TMS

            # If an img exists in the TMS cell, it's TMS-eligible
            tms_icon = tms_cell.locator("img")
            tms_icon.wait_for(state="visible", timeout=timeout)

            logger.info("Allocation is TMS-eligible (icon found)")
            return True

        except Exception as exc:
            logger.info(f"Allocation is TMS-ineligible (no icon): {exc}")
            return False

    def click_next(self) -> None:
        """Click Next button to proceed to Tax Management step."""
        logger.info("Clicking Next from Allocation step")
        next_button = self.step_allocation_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-2 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button to go back to Risk Assessment step."""
        logger.info("Clicking Previous from Allocation step")
        prev_button = self.step_allocation_panel.locator("button[data-wizard-previous]")
        prev_button.click()
