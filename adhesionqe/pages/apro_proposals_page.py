"""APro Proposals aggregator page object.

This is a thin facade that delegates to 8 specialized step POMs and the prospects list POM.
It provides backward compatibility via __getattr__ delegation, so existing step files
don't need any changes when using proposal_page.method_name().
"""

from playwright.sync_api import Locator, Page

from pages.apro_step_allocation import ProposalAllocationPage
from pages.apro_step_details import ProposalDetailsPage
from pages.apro_step_fees import ProposalFeesPage
from pages.apro_step_generate import ProposalGeneratePage
from pages.apro_step_history import ProposalHistoryPage
from pages.apro_step_holdings import ProposalHoldingsPage
from pages.apro_step_risk import ProposalRiskPage
from pages.apro_step_tax_management import ProposalTaxManagementPage
from pages.prospects_list_page import ProspectsListPage
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AproProposalsPage(BasePage):
    """Thin aggregator POM for APro proposal wizard and prospects list.

    Composes 8 step-specific POMs and ProspectsListPage, delegating via __getattr__
    for transparent method access. Step files need zero changes — they keep using
    proposal_page.method_name() and the right POM handles it automatically.

    Example:
        proposal_page.set_client_name("John")  # Routes to self.details.set_client_name()
        proposal_page.answer_all_questions()   # Routes to self.risk.answer_all_questions()
        proposal_page.select_allocation(0)     # Routes to self.allocation.select_allocation()
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # --- Shared locators (used by multiple step POMs) ---
        # Overlay that appears behind modal dialogs
        self.overlay: Locator = page.locator("div.k-overlay")

        # Generic container for the proposal modal steps
        self.proposal_modal: Locator = page.locator("div.k-window")

        # Step navigation buttons (will be scoped dynamically to visible step)
        self.wizard_cancel_button: Locator = self.proposal_modal.locator(
            "button[data-wizard-reset]"
        )

        # --- Shared state attributes ---
        self.expected_client_name: str | None = None
        self.expected_allocation_name: str | None = None
        self.expected_strategy: str | None = None
        self.expected_investment_amount: float | None = None
        self.expected_advisor_name: str | None = None
        self.accounts_tracker = None  # API response tracker fixture

        # --- Step POM instances ---
        self.details = ProposalDetailsPage(page, base_url)
        self.risk = ProposalRiskPage(page, base_url)
        self.allocation = ProposalAllocationPage(page, base_url)
        self.tax_management = ProposalTaxManagementPage(page, base_url)
        self.holdings = ProposalHoldingsPage(page, base_url)
        self.fees = ProposalFeesPage(page, base_url)
        self.generate = ProposalGeneratePage(page, base_url)
        self.history = ProposalHistoryPage(page, base_url)
        self._list = ProspectsListPage(page, base_url)

        # Store POMs list for __getattr__ delegation (via object.__setattr__ to avoid recursion)
        object.__setattr__(
            self,
            "_pom_list",
            [
                self.details,
                self.risk,
                self.allocation,
                self.tax_management,
                self.holdings,
                self.fees,
                self.generate,
                self.history,
                self._list,
            ],
        )

    def __getattr__(self, name):
        """Transparently delegate attribute access to the appropriate step POM.

        Try each POM in order until one has the attribute. This allows step files
        to call proposal_page.any_step_method() without knowing which POM owns it.
        """
        pom_list = object.__getattribute__(self, "_pom_list")
        for pom in pom_list:
            try:
                return object.__getattribute__(pom, name)
            except AttributeError:
                continue

        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def click_next(self) -> None:
        """Click Next button on the currently visible wizard step with retry logic.

        Detects which step is visible and delegates to that step POM's click_next().
        Retries every 1 second for up to 10 seconds in case button is not immediately ready.
        """
        import time

        # Detect current step by checking which wizard div is visible
        for i in range(8):
            try:
                step_div = self.page.locator(f"#proposal-wizard-{i}")
                if step_div.is_visible():
                    # Route to the correct step POM with retry logic
                    step_poms = [
                        self.details,  # 0
                        self.risk,  # 1
                        self.allocation,  # 2
                        self.tax_management,  # 3
                        self.holdings,  # 4
                        self.fees,  # 5
                        self.generate,  # 6
                        self.history,  # 7
                    ]

                    # Retry up to 10 times (every 1 second)
                    last_error = None
                    for attempt in range(10):
                        try:
                            step_poms[i].click_next()  # type: ignore[attr-defined]
                            return
                        except Exception as e:
                            last_error = e
                            if attempt < 9:
                                logger.warning(
                                    f"click_next attempt {attempt + 1} failed, retrying in 1s: {e}"
                                )
                                time.sleep(1)

                    # If all retries failed, raise the last error
                    if last_error:
                        raise last_error
                    return
            except Exception:
                continue

        raise RuntimeError("Could not determine current wizard step for click_next()")

    def click_previous(self) -> None:
        """Click Previous button on the currently visible wizard step with retry logic.

        Detects which step is visible and delegates to that step POM's click_previous().
        Retries every 1 second for up to 10 seconds in case button is not immediately ready.
        """
        import time

        # Detect current step by checking which wizard div is visible
        for i in range(8):
            try:
                step_div = self.page.locator(f"#proposal-wizard-{i}")
                if step_div.is_visible():
                    # Route to the correct step POM with retry logic
                    step_poms = [
                        self.details,  # 0
                        self.risk,  # 1
                        self.allocation,  # 2
                        self.tax_management,  # 3
                        self.holdings,  # 4
                        self.fees,  # 5
                        self.generate,  # 6
                        self.history,  # 7
                    ]

                    # Retry up to 10 times (every 1 second)
                    last_error = None
                    for attempt in range(10):
                        try:
                            step_poms[i].click_previous()  # type: ignore[attr-defined]
                            return
                        except Exception as e:
                            last_error = e
                            if attempt < 9:
                                logger.warning(
                                    f"click_previous attempt {attempt + 1} failed, retrying in 1s: {e}"
                                )
                                time.sleep(1)

                    # If all retries failed, raise the last error
                    if last_error:
                        raise last_error
                    return
            except Exception:
                continue

        raise RuntimeError("Could not determine current wizard step for click_previous()")

    # --- Shared utility methods (not delegated) ---

    def wait_for_overlay(self, timeout: int = 10000) -> None:
        """Wait until the overlay is visible (modal shown)."""
        logger.info("Waiting for modal overlay to be visible")
        self.wait_for_element(self.overlay, state="visible", timeout=timeout)

    def wait_for_overlay_to_disappear(self, timeout: int = 10000) -> None:
        """Wait until the overlay is gone/hidden (modal closed)."""
        logger.info("Waiting for modal overlay to disappear")
        self.wait_for_element(self.overlay, state="hidden", timeout=timeout)

    def wait_for_proposal_step(self, step_selector: str, timeout: int = 10000) -> None:
        """Wait for a proposal step element to be visible.

        Args:
            step_selector: CSS selector for the step content
            timeout: Wait timeout in ms
        """
        logger.info(f"Waiting for proposal step selector: {step_selector}")
        locator = self.page.locator(step_selector)
        self.wait_for_element(locator, state="visible", timeout=timeout)

    def _get_visible_wizard_step(self):
        """Return the currently visible wizard step container Locator.

        Searches through all 8 step containers and returns the first visible one,
        or falls back to the first step if none are visible.
        """
        steps = self.page.locator('div[id^="proposal-wizard-"]')
        try:
            count = steps.count()
        except Exception:
            return steps.first

        for i in range(count):
            step = steps.nth(i)
            try:
                if step.is_visible():
                    return step
            except Exception:
                continue

        # Fallback: return first step
        return steps.first

    def _wait_for_enabled_in_step(self, selector: str, timeout: int = 10000) -> str | None:
        """Wait until a button matching selector inside the visible step is enabled.

        Returns the selector string if matched, or None on timeout.
        """
        logger.info(f"Waiting for enabled element in step: {selector}")
        import time
        from contextlib import suppress

        end = time.time() + (int(timeout) / 1000.0)
        with suppress(Exception):
            while time.time() < end:
                button = self.page.locator(selector)
                with suppress(Exception):
                    if button.is_enabled() and button.is_visible():
                        return selector
                self.page.wait_for_timeout(200)

        return None

    def click_step(self, step_index: int) -> None:
        """Click a step in the top wizard navigator (0-7).

        Args:
            step_index: 0-based step index (0=Details, 7=History)

        Raises:
            ValueError: If step index is out of range or step is disabled
        """
        logger.info(f"Clicking step {step_index} in wizard navigator")

        # Look for step tabs using role="tab" selector (the <a> elements inside <li> tags)
        # Wait for tabs to be visible first
        step_tabs = self.page.locator('a.k-step-link[role="tab"]')
        step_tabs.first.wait_for(state="visible", timeout=5000)

        tab_count = step_tabs.count()
        logger.info(f"Found {tab_count} step tabs")

        if step_index >= tab_count:
            raise ValueError(
                f"Step index {step_index} out of range (found {tab_count} tabs). "
                f"Valid indices are 0-{tab_count - 1}"
            )

        # Get the target tab
        target_tab = step_tabs.nth(step_index)

        # Check if the step is disabled
        is_disabled = target_tab.get_attribute("aria-disabled") == "true"
        if is_disabled:
            raise ValueError(
                f"Step index {step_index} is disabled and cannot be clicked. "
                f"aria-disabled='true' indicates this step is not yet available."
            )

        # Click the tab at the specified index
        target_tab.click()

        # Wait for the step to load
        self.page.wait_for_load_state("networkidle", timeout=5000)

    def get_row_data(self, row_index: int) -> dict:
        """Get data from a proposal row in the prospects list grid.

        Delegates to ProspectsListPage.get_row_data() for proper column extraction.

        Args:
            row_index: 0-based row index in the proposals table

        Returns:
            Dictionary mapping column names to cell text for all columns
        """
        return self._list.get_row_data(row_index)
