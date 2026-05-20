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
        
        # Dismiss overlay after navigation (it may appear on new pages)
        self.page.wait_for_timeout(500)
        self._dismiss_onetrust_overlay()

    # dynamic wait method(condition based)
    def wait_for_load_state(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: int = 120000,
    ) -> None:
        """Wait for page to reach specified load state (default: 120s for slow environments)"""
        self.logger.info(f"Waiting for load state: {state} (timeout: {timeout}ms)")
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

    def _dismiss_ketch_overlay(self) -> None:
        """
        Dismiss Ketch cookie consent overlay (the "We value your privacy" dialog).
        Clicks "Accept All" if the Ketch consent banner is visible.
        """
        try:
            # Ketch consent banner uses an iframe or shadow DOM sometimes,
            # but on this site it appears as a regular DOM element
            accept_btn = self.page.get_by_role("button", name="Accept All")
            if accept_btn.count() > 0 and accept_btn.first.is_visible(timeout=2000):
                self.logger.info("Ketch cookie consent detected - clicking 'Accept All'")
                accept_btn.first.click(timeout=5000)
                self.page.wait_for_timeout(500)
                self.logger.info("Ketch cookie consent dismissed via 'Accept All'")
                return
        except Exception:
            pass
        
        try:
            # Fallback: Try locating by exact text match
            accept_btn = self.page.locator("button:has-text('Accept All')").first
            if accept_btn.is_visible(timeout=1000):
                self.logger.info("Ketch consent found via text selector - clicking")
                accept_btn.click(timeout=5000)
                self.page.wait_for_timeout(500)
                self.logger.info("Ketch cookie consent dismissed")
        except Exception:
            pass

    def _dismiss_onetrust_overlay(self) -> None:
        """
        Dismiss cookie consent overlays (OneTrust or Ketch) that may block other interactions.
        Uses multiple strategies to ensure removal.
        """
        # Try Ketch consent first (newer consent manager on the site)
        self._dismiss_ketch_overlay()
        
        try:
            # Check if overlay or consent SDK exists
            sdk = self.page.locator("div#onetrust-consent-sdk")
            if sdk.count() == 0:
                return  # No OneTrust present
            
            overlay = self.page.locator("div.onetrust-pc-dark-filter")
            banner = self.page.locator("div#onetrust-banner-sdk")
            if overlay.count() == 0 and banner.count() == 0:
                return  # SDK present but no visible overlay/banner
            
            self.logger.warning("OneTrust overlay detected - attempting dismissal")
            
            # Strategy 1: Click "Reject All" button by various selectors
            try:
                reject_btn = self.page.locator(
                    "button.ot-pc-refuse-all-handler, "
                    "button[data-onetrust-reject-all], "
                    "button:has-text('Reject All')"
                ).first
                if reject_btn.is_visible(timeout=2000):
                    self.logger.info("Found 'Reject All' button - clicking it")
                    reject_btn.click(timeout=5000)
                    self.page.wait_for_timeout(500)
                    self.logger.info("OneTrust overlay dismissed via 'Reject All'")
                    return
            except Exception as e:
                self.logger.warning(f"Strategy 1 (Reject All) failed: {e}")
            
            # Strategy 2: Click "Confirm My Choices" button
            try:
                confirm_btn = self.page.locator(
                    "button.save-preference-btn-handler, "
                    "button:has-text('Confirm My Choices')"
                ).first
                if confirm_btn.is_visible(timeout=2000):
                    self.logger.info("Found 'Confirm My Choices' button - clicking it")
                    confirm_btn.click(timeout=5000)
                    self.page.wait_for_timeout(500)
                    self.logger.info("OneTrust overlay dismissed via 'Confirm My Choices'")
                    return
            except Exception as e:
                self.logger.warning(f"Strategy 2 (Confirm My Choices) failed: {e}")
            
            # Strategy 3: Click close button (X icon)
            try:
                close_btn = self.page.locator("button.onetrust-close-btn-handler")
                if close_btn.count() > 0:
                    self.logger.info("Found close button - clicking it")
                    close_btn.first.click(timeout=5000)
                    self.page.wait_for_timeout(500)
                    self.logger.info("OneTrust overlay dismissed via close button")
                    return
            except Exception as e:
                self.logger.warning(f"Strategy 3 (Close button) failed: {e}")
            
            # Strategy 4: JavaScript removal - force remove overlay and backdrop
            try:
                self.logger.info("Removing OneTrust overlay via JavaScript")
                self.page.evaluate("""
                () => {
                    const sdk = document.querySelector('div#onetrust-consent-sdk');
                    if (sdk) { sdk.remove(); }
                    document.body.style.overflow = 'auto';
                    return true;
                }
                """)
                self.page.wait_for_timeout(300)
                self.logger.info("OneTrust overlay removed via JavaScript")
            except Exception as e:
                self.logger.warning(f"Strategy 4 (JavaScript removal) failed: {e}")
        except Exception as e:
            self.logger.debug(f"OneTrust dismissal check failed: {e}")

    def click(self, locator: Locator, timeout: int = 120000) -> None:
        """Click an element with wait and logging - includes auto-healing and overlay handling.
        
        Args:
            locator: Playwright locator to click
            timeout: Timeout in milliseconds (default 120000ms = 2 minutes for slow headless environments)
        """
        self.logger.info(f"Clicking element (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            # Dismiss overlay before attempting click
            self._dismiss_onetrust_overlay()
            
            loc.wait_for(state="visible", timeout=timeout)
            try:
                # ✅ CRITICAL: Pass timeout to loc.click() - otherwise uses Playwright's 30s default
                loc.click(timeout=timeout)
            except PlaywrightTimeoutError as e:
                # If click fails due to overlay blocking, try with force=True
                if "intercepts pointer events" in str(e):
                    self.logger.warning(f"Click blocked by overlay - retrying with force=True (timeout: {timeout}ms)")
                    self._dismiss_onetrust_overlay()  # Try dismissal again
                    self.page.wait_for_timeout(200)
                    # ✅ CRITICAL: Pass timeout here too
                    loc.click(force=True, timeout=timeout)
                else:
                    raise

        self._heal_and_retry(locator, _action)

    def fill(self, locator: Locator, text: str, timeout: int = 120000) -> None:
        """Fill a text field with wait and logging - includes auto-healing.
        
        Args:
            locator: Playwright locator for the input field
            text: Text to fill
            timeout: Timeout in milliseconds (default 120000ms for slow environments)
        """
        self.logger.info(f"Filling field with text (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            # Dismiss overlay before fill (fill internally clicks the element first)
            self._dismiss_onetrust_overlay()
            loc.wait_for(state="visible", timeout=timeout)
            # ✅ CRITICAL: Pass timeout to loc.fill()
            loc.fill(text, timeout=timeout)

        self._heal_and_retry(locator, _action)

    def get_text(self, locator: Locator, timeout: int = 120000) -> str:
        """Get text content from an element with auto-healing.
        
        Args:
            locator: Playwright locator for the element
            timeout: Timeout in milliseconds (default 120000ms for slow environments)
            
        Returns:
            Text content of the element, or empty string if not found
        """

        def _action(loc: Locator) -> str:
            # ✅ CRITICAL: Pass timeout to loc.text_content()
            loc.wait_for(state="visible", timeout=timeout)
            return loc.text_content(timeout=timeout) or ""

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
        timeout: int = 120000,
    ) -> None:
        """Wait for element to reach specified state with auto-healing (default: 120s for slow environments)."""
        self.logger.info(f"Waiting for element to be {state} (timeout: {timeout}ms)")

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
        
        # Dismiss overlay after refresh (it may reappear)
        self.page.wait_for_timeout(500)
        self._dismiss_onetrust_overlay()

    def empty_field(self, locator: Locator, timeout: int = 120000) -> None:
        """Clear a field by clicking and filling with empty string, with auto-healing (default: 120s)."""
        self.logger.info(f"Clearing field (timeout: {timeout}ms)")

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
        timeout: int = 120000,
    ) -> list[str]:
        """Select an option from a <select> dropdown with auto-healing (default: 120s).

        Provide exactly one of value, label, or index.
        Returns list of selected option values.
        """
        self.logger.info(f"Selecting option from dropdown (timeout: {timeout}ms)")

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

    def check(self, locator: Locator, timeout: int = 120000) -> None:
        """Check a checkbox (no-op if already checked) with auto-healing (default: 120s)."""
        self.logger.info(f"Checking checkbox (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.check()

        self._heal_and_retry(locator, _action)

    def uncheck(self, locator: Locator, timeout: int = 120000) -> None:
        """Uncheck a checkbox (no-op if already unchecked) with auto-healing (default: 120s)."""
        self.logger.info(f"Unchecking checkbox (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.uncheck()

        self._heal_and_retry(locator, _action)

    def scroll_into_view(self, locator: Locator, timeout: int = 120000) -> None:
        """Scroll the page until the element is visible in the viewport (default: 120s)."""
        self.logger.info(f"Scrolling element into view (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="attached", timeout=timeout)
            loc.scroll_into_view_if_needed()

        self._heal_and_retry(locator, _action)

    def focus(self, locator: Locator, timeout: int = 120000) -> None:
        """Set focus on an element with auto-healing (default: 120s)."""
        self.logger.info(f"Focusing element (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.focus()

        self._heal_and_retry(locator, _action)

    def upload_file(
        self,
        file_path: str | list[str],
        locator: Optional[Locator] = None,
        trigger_locator: Optional[Locator] = None,
        timeout: int = 120000,
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

    def press_key(self, key: str, locator: Optional[Locator] = None, timeout: int = 120000) -> None:
        """Press a keyboard key (Enter, Escape, Tab, ArrowDown, etc.) (default: 120s).

        If a locator is provided, the key press is scoped to that element with auto-healing.
        Otherwise, it fires on the page level.
        """
        self.logger.info(f"Pressing key: {key} (timeout: {timeout}ms)")
        if locator:
            def _action(loc: Locator) -> None:
                loc.wait_for(state="visible", timeout=timeout)
                loc.press(key)

            self._heal_and_retry(locator, _action)
        else:
            self.page.keyboard.press(key)

    def type_text(self, locator: Locator, text: str, delay: int = 50, timeout: int = 120000) -> None:
        """Type text character-by-character into an element (default: 120s).

        Useful for inputs that rely on keydown/keyup events and don't work with fill().
        """
        self.logger.info(f"Typing text character-by-character (timeout: {timeout}ms)")

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

    def double_click(self, locator: Locator, timeout: int = 120000) -> None:
        """Double-click an element with auto-healing (default: 120s)."""
        self.logger.info(f"Double-clicking element (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.dblclick()

        self._heal_and_retry(locator, _action)

    def right_click(self, locator: Locator, timeout: int = 120000) -> None:
        """Right-click (context menu) an element with auto-healing (default: 120s)."""
        self.logger.info(f"Right-clicking element (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.click(button="right")

        self._heal_and_retry(locator, _action)

    def hover(self, locator: Locator, timeout: int = 120000) -> None:
        """Hover over an element with auto-healing (default: 120s)."""
        self.logger.info(f"Hovering over element (timeout: {timeout}ms)")

        def _action(loc: Locator) -> None:
            loc.wait_for(state="visible", timeout=timeout)
            loc.hover()

        self._heal_and_retry(locator, _action)

    def drag_and_drop(
        self, source: Locator, target: Locator, timeout: int = 120000
    ) -> None:
        """Drag source element and drop onto target element with auto-healing (default: 120s)."""
        self.logger.info(f"Drag and drop (timeout: {timeout}ms)")

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
        timeout: int = 120000,
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
        dest = save_path or f"reports/oam/downloads/{name}"
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
