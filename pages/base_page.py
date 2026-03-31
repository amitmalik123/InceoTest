# pages/base_page.py

"""
Base Page class with common functionality for all page objects
"""

import logging
import os
import re
from typing import Any, Callable, Literal, Optional

import allure
from playwright.sync_api import Download, Error as PlaywrightError
from playwright.sync_api import FrameLocator, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.auto_healing import AutoHealingEngine

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects.
    Provides common functionality like navigation, waits, and assertions.
    """

    _healing_engine: Optional[AutoHealingEngine] = None  # Shared across all page objects

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = base_url or ""
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize healing engine once
        if BasePage._healing_engine is None:
            BasePage._healing_engine = AutoHealingEngine("locator_mappings.json")
            self.logger.info("Auto-healing engine initialized")

    def navigate_to(
        self,
        url: str,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
    ) -> None:
        """Navigate to a specific URL"""
        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        self.logger.info(f"Navigating to: {full_url}")
        self.page.goto(full_url, wait_until=wait_until)
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    # dynamic wait method(condition based)
    def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: int = 30000,
    ) -> None:
        """Wait for page to reach specified load state"""
        self.logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    # static wait method
    def wait_for_timeout(self, milliseconds: int) -> None:
        """Wait for a specific amount of time"""
        self.page.wait_for_timeout(milliseconds)

    # ------------------------------------------------------------------
    # Auto-healing helper
    # ------------------------------------------------------------------

    def _heal_and_retry(self, locator: Locator, action_fn: Callable[[Locator], Any]) -> Any:
        """Try *action_fn* on *locator*; on failure, auto-heal and retry.

        Args:
            locator: Original Playwright locator.
            action_fn: Receives a (possibly healed) locator and performs the
                       desired interaction.  Its return value is propagated.

        Returns:
            Whatever *action_fn* returns.

        Raises:
            The original exception when every healing strategy fails.
        """
        try:
            return action_fn(locator)
        except (PlaywrightError, PlaywrightTimeoutError, Exception):
            self.logger.warning("Action failed with original locator")
            self.logger.info("🔧 Auto-healing: Trying alternative strategies...")

            selector_str = str(locator)

            # Strategy 1: text-based name extraction
            if "name=" in selector_str:
                match = re.search(r'name=["\']([^"\']+)["\']', selector_str)
                if match:
                    text = match.group(1)
                    self.logger.info(f"Trying text-based healing with: '{text}'")
                    healed = self.page.get_by_text(text, exact=True)
                    if healed.count() > 0:
                        self.logger.info(f"Auto-healing SUCCESS - Found by text '{text}'")
                        return action_fn(healed)

            # Strategy 2: AutoHealingEngine
            if self._healing_engine is not None:
                healed_locator, _ = self._healing_engine.find_element(self.page, selector_str)
                if healed_locator:
                    self.logger.info("Auto-healing SUCCESS using healing engine!")
                    return action_fn(healed_locator)

            self.logger.error("Auto-healing FAILED - element not found")
            raise

    # ------------------------------------------------------------------
    # Element interaction methods (all delegate to _heal_and_retry)
    # ------------------------------------------------------------------

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        """Click an element with wait and logging - includes auto-healing."""
        self.logger.info("Clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()

        self._heal_and_retry(locator, _action)

    def fill(self, locator: Locator, text: str, timeout: int = 10000) -> None:
        """Fill a text field with wait and logging - includes auto-healing."""
        self.logger.info("Filling field with text")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.fill(text)

        self._heal_and_retry(locator, _action)

    def get_text(self, locator: Locator, timeout: int = 10000) -> str:
        """Get text content from an element with auto-healing."""

        def _action(loc: Locator) -> str:
            loc.wait_for(state="visible", timeout=timeout)
            return loc.text_content() or ""

        return self._heal_and_retry(locator, _action)

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        """Check if element is visible"""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(
        self,
        locator: Locator,
        state: Literal["attached", "detached", "hidden", "visible"] = "visible",
        timeout: int = 10000,
    ) -> None:
        """Wait for element to reach specified state with auto-healing."""
        self.logger.info(f"Waiting for element to be {state}")

        def _action(loc: Locator) -> None:
            loc.wait_for(state=state, timeout=timeout)

        self._heal_and_retry(locator, _action)

    def screenshot(self, name: str) -> bytes:
        """Take a screenshot and return bytes"""
        self.logger.info(f"Taking screenshot: {name}")
        return self.page.screenshot()

    def screenshot_with_allure(self, name: str, path: Optional[str] = None) -> bytes:
        """
        Take a screenshot, optionally save to disk, and attach to Allure report.

        Args:
            name: Name for the Allure attachment
            path: Optional file path to save screenshot to disk

        Returns:
            Screenshot bytes
        """
        self.logger.info(f"Taking screenshot: {name}")
        if path:
            screenshot_bytes = self.page.screenshot(path=path)
            self.logger.info(f"Screenshot saved: {path}")
        else:
            screenshot_bytes = self.page.screenshot()

        # Attach to Allure report
        allure.attach(screenshot_bytes, name=name, attachment_type=allure.attachment_type.PNG)
        return screenshot_bytes

    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    def go_back(self) -> None:
        """Navigate back in browser history"""
        self.logger.info("Navigating back")
        self.page.go_back()

    def refresh(self) -> None:
        """Refresh the current page"""
        self.logger.info("Refreshing page")
        self.page.reload()

    def empty_field(self, locator: Locator, timeout: int = 10000) -> None:
        """Clear a field by clicking and filling with empty string, with auto-healing."""
        self.logger.info("Clearing field")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()
            loc.fill("")

        self._heal_and_retry(locator, _action)

    def select_option(
        self,
        locator: Locator,
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        timeout: int = 10000,
    ) -> list[str]:
        """Select an option from a <select> dropdown with auto-healing.

        Provide exactly one of value, label, or index.
        Returns list of selected option values.
        """
        self.logger.info("Selecting option from dropdown")

        def _action(loc: Locator) -> list[str]:
            loc.wait_for(state="visible", timeout=timeout)
            if value is not None:
                return loc.select_option(value=value)
            elif label is not None:
                return loc.select_option(label=label)
            elif index is not None:
                return loc.select_option(index=index)
            raise ValueError("Provide one of: value, label, or index")

        return self._heal_and_retry(locator, _action)

    def check(self, locator: Locator, timeout: int = 10000) -> None:
        """Check a checkbox (no-op if already checked) with auto-healing."""
        self.logger.info("Checking checkbox")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.check()

        self._heal_and_retry(locator, _action)

    def uncheck(self, locator: Locator, timeout: int = 10000) -> None:
        """Uncheck a checkbox (no-op if already unchecked) with auto-healing."""
        self.logger.info("Unchecking checkbox")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.uncheck()

        self._heal_and_retry(locator, _action)

    def scroll_into_view(self, locator: Locator, timeout: int = 10000) -> None:
        """Scroll the page until the element is visible in the viewport."""
        self.logger.info("Scrolling element into view")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="attached", timeout=timeout)
            loc.scroll_into_view_if_needed()

        self._heal_and_retry(locator, _action)

    def focus(self, locator: Locator, timeout: int = 10000) -> None:
        """Set focus on an element with auto-healing."""
        self.logger.info("Focusing element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.focus()

        self._heal_and_retry(locator, _action)

    def upload_file(
        self,
        file_path: str | list[str],
        locator: Optional[Locator] = None,
        trigger_locator: Optional[Locator] = None,
        timeout: int = 10000,
    ) -> None:
        """Upload file(s) via a file input or a file chooser dialog.

        Option A – direct input: pass *locator* pointing to an ``<input type="file">``
        element. Uses ``set_input_files`` directly (works even when the input is hidden).

        Option B – file chooser dialog: pass *trigger_locator* (the button/link that
        opens the OS file picker). The method listens for the ``filechooser`` event
        and calls ``set_files`` on the dialog.

        Provide exactly one of *locator* or *trigger_locator*.
        """
        paths = file_path if isinstance(file_path, list) else [file_path]
        self.logger.info(f"Uploading file(s): {paths}")

        if locator:
            def _action(loc: Locator) -> None:
                loc.wait_for(state="attached", timeout=timeout)
                loc.set_input_files(paths)

            self._heal_and_retry(locator, _action)

        elif trigger_locator:
            def _action(loc: Locator) -> None:
                with self.page.expect_file_chooser(timeout=timeout) as fc_info:
                    loc.click()
                file_chooser = fc_info.value
                file_chooser.set_files(paths)

            self._heal_and_retry(trigger_locator, _action)

        else:
            raise ValueError("Provide one of: locator (file input) or trigger_locator (button that opens picker)")
    

    # ------------------------------------------------------------------
    # Keyboard methods
    # ------------------------------------------------------------------

    def press_key(self, key: str, locator: Optional[Locator] = None, timeout: int = 10000) -> None:
        """Press a keyboard key (Enter, Escape, Tab, ArrowDown, etc.).

        If a locator is provided, the key press is scoped to that element with auto-healing.
        Otherwise, it fires on the page level.
        """
        self.logger.info(f"Pressing key: {key}")
        if locator:
            def _action(loc: Locator) -> None:
                loc.wait_for(state="visible", timeout=timeout)
                loc.press(key)

            self._heal_and_retry(locator, _action)
        else:
            self.page.keyboard.press(key)

    def type_text(self, locator: Locator, text: str, delay: int = 50, timeout: int = 10000) -> None:
        """Type text character-by-character into an element.

        Useful for inputs that rely on keydown/keyup events and don't work with fill().
        """
        self.logger.info("Typing text character-by-character")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()
            loc.press_sequentially(text, delay=delay)

        self._heal_and_retry(locator, _action)

    def keyboard_shortcut(self, keys: str) -> None:
        """Execute a keyboard shortcut (e.g., 'Control+a', 'Control+c', 'Meta+v').

        Uses Playwright's keyboard.press which accepts modifier+key combos.
        """
        self.logger.info(f"Keyboard shortcut: {keys}")
        self.page.keyboard.press(keys)

    # ------------------------------------------------------------------
    # Mouse methods
    # ------------------------------------------------------------------

    def double_click(self, locator: Locator, timeout: int = 10000) -> None:
        """Double-click an element with auto-healing."""
        self.logger.info("Double-clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.dblclick()

        self._heal_and_retry(locator, _action)

    def right_click(self, locator: Locator, timeout: int = 10000) -> None:
        """Right-click (context menu) an element with auto-healing."""
        self.logger.info("Right-clicking element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click(button="right")

        self._heal_and_retry(locator, _action)

    def hover(self, locator: Locator, timeout: int = 10000) -> None:
        """Hover over an element with auto-healing."""
        self.logger.info("Hovering over element")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.hover()

        self._heal_and_retry(locator, _action)

    def drag_and_drop(
        self, source: Locator, target: Locator, timeout: int = 10000
    ) -> None:
        """Drag source element and drop onto target element with auto-healing."""
        self.logger.info("Drag and drop")

        def _action(src: Locator) -> None:
            src.wait_for(state="visible", timeout=timeout)
            target.wait_for(state="visible", timeout=timeout)
            src.drag_to(target)

        self._heal_and_retry(source, _action)

    # ------------------------------------------------------------------
    # Download handling
    # ------------------------------------------------------------------

    def download_file(
        self,
        trigger_locator: Locator,
        save_path: Optional[str] = None,
        filename: Optional[str] = None,
        timeout: int = 30000,
    ) -> Download:
        """Click a link/button that triggers a download and return the Download object.

        Files are saved to ``reports/downloads/`` by default (cleaned at session start).
        Pass *save_path* to override the full destination, or *filename* to override
        just the file name within the default downloads folder.

        Args:
            trigger_locator: Element that initiates the download.
            save_path: Optional full path to save the file (takes priority over *filename*).
            filename: Optional custom file name (used inside ``reports/downloads/``).
                      Defaults to the browser-suggested filename.
            timeout: Max wait for the download to start.

        Returns:
            Playwright Download object (has .path(), .suggested_filename, .url, etc.).
        """
        self.logger.info("Waiting for download...")

        with self.page.expect_download(timeout=timeout) as dl_info:
            trigger_locator.click()

        download = dl_info.value
        self.logger.info(f"Download started: {download.suggested_filename}")

        name = filename or download.suggested_filename
        dest = save_path or f"reports/downloads/{name}"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        download.save_as(dest)
        self.logger.info(f"Download saved to: {dest}")

        return download

    # ------------------------------------------------------------------
    # Iframe support
    # ------------------------------------------------------------------

    def get_frame(self, selector: str) -> FrameLocator:
        """Get a FrameLocator for interacting with elements inside an iframe.

        Args:
            selector: CSS selector or iframe name/id.
                      e.g. "iframe#content", "iframe[name='main']", "#myFrame"

        Returns:
            FrameLocator that can chain .locator() calls inside the iframe.

        Usage::

            frame = self.get_frame("iframe#content")
            frame.locator("#submit").click()
        """
        self.logger.info(f"Accessing iframe: {selector}")
        return self.page.frame_locator(selector)
