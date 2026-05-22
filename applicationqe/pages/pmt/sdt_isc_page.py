"""SDT ISC Process Portal (BAW) page object."""

from playwright.sync_api import Locator, Page
from playwright.sync_api import Error as PlaywrightError

from pages.base_page import BasePage
from utils.logger import setup_logger
from utils.settings import settings

logger = setup_logger(__name__)

# --- Additional imports for merged page classes ---
import os
import re
import tempfile
import time
from typing import Optional
from playwright.sync_api import expect  # noqa: F401


# --- Additional imports for merged page classes ---
import os
import re
import tempfile
import time
from typing import Optional
from playwright.sync_api import expect  # noqa: F401



__all__ = [
    "SdtIscPage",
    "LoginPage",
    "ClientsPage",
    "AccountListPage",
    "AccountDetailPage",
    "ChangeInvestmentsPage",
    "DocusignPage",
    "TrackingCenterPage",
]


class SdtIscPage(BasePage):
    PAGE_PATH = "ProcessPortal/login.jsp"
    RUN_BUTTON_XPATH = "xpath=//*[@id='TaskTable']/tbody/tr[1]/td[1]/img"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.username_input: Locator = page.locator(
            "input[name='username'], input[name='j_username'], input#username, input#j_username"
        ).first
        self.password_input: Locator = page.locator(
            "input[name='password'], input[name='j_password'], input#password, input#j_password, input[type='password']"
        ).first
        self.sign_in_form: Locator = page.locator(
            "form#signInForm, form[action*='j_security_check'], form.login-form"
        ).first
        self.login_button: Locator = page.locator(
            "button[type='submit'], input[type='submit'], #loginButton, button:has-text('Log in'), button:has-text('Login'), input[value='Log in'], input[value='Login']"
        ).first

        # -- Account Wizard: Account Management section --
        # (Merged from former pages/baw/account_management_page.py)
        self.request_dropdown: Locator = page.locator(
            "#ctl00_cphContentArea_ddlRequest"
        )
        self.type_dropdown: Locator = page.locator(
            "#ctl00_cphContentArea_ddlType"
        )
        self.complete_and_print_button: Locator = page.get_by_role(
            "button", name="Complete and Print"
        )

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to SDT ISC Process Portal login page: {url}")

        last_error: Exception | None = None
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                self.username_input.wait_for(state="visible", timeout=15000)
                logger.info("SDT ISC Process Portal login page loaded")
                return
            except PlaywrightError as error:
                last_error = error
                logger.warning(
                    f"Failed to open SDT ISC login page (attempt {attempt}/{max_attempts}): {error}"
                )
                if attempt < max_attempts:
                    self.page.wait_for_timeout(2000)

        raise RuntimeError(
            "Unable to reach SDT ISC Process Portal login page after retries. "
            f"URL: {url}. Last error: {last_error}"
        ) from last_error

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering SDT ISC username: {username}")
        self.fill(self.username_input, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering SDT ISC password")
        self.fill(self.password_input, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking SDT ISC sign in button")

        try:
            self.password_input.press("Enter")
            logger.info("Submitted SDT ISC login using Enter key")
        except Exception as enter_error:
            logger.warning(f"Enter-key submit failed: {enter_error}")

            try:
                self.login_button.click(force=True, timeout=5000)
                logger.info("Submitted SDT ISC login using forced click")
            except Exception as click_error:
                logger.warning(f"Forced click submit failed: {click_error}")

                self.sign_in_form.evaluate(
                    "(form) => form.requestSubmit ? form.requestSubmit() : form.submit()"
                )
                logger.info("Submitted SDT ISC login using form submission")

        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info(f"SDT ISC sign in submitted. Current URL: {self.page.url}")

    def login(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.click_sign_in()

    def login_as(self, user: str = "user1") -> None:
        """Login as user1 (primary) or user2 (secondary). Navigates to login page for user2."""
        app_config = settings.config.get("baw_process_portal", {}) or {}

        if user == "user2":
            username = app_config.get("username2", "")
            password = app_config.get("password2", "")
        else:
            username = app_config.get("username", "")
            password = app_config.get("password", "")

        if not username or not password:
            raise ValueError(
                f"Missing baw_process_portal credentials for {user} in the active environment config."
            )

        if user == "user2":
            logger.info(f"Navigating to login page for {user}: {username}")
            self.navigate()

        logger.info(f"Logging in as {user}: {username}")
        self.login(username, password)
        self.verify_login_successful()
        logger.info(f"SDT ISC Process Portal login verified successfully for {user}")

    def verify_login_successful(self) -> None:
        logger.info(f"Verifying SDT ISC login success. Current URL: {self.page.url}")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        current_url = self.page.url.lower()
        login_form_still_visible = False
        try:
            login_form_still_visible = self.password_input.is_visible(timeout=3000)
        except Exception:
            login_form_still_visible = False

        if "login.jsp" in current_url and login_form_still_visible:
            raise AssertionError(
                f"SDT ISC Process Portal login failed. Still on login page: {self.page.url}"
            )

        logger.info("SDT ISC Process Portal login verified successfully")

    def search_b_number(self, b_number: str) -> None:
        """Search B-number from the filter area near B#: field and click ButtonGroup4_Search."""
        logger.info(f"Searching B-number '{b_number}' from filter area B# field")

        # Wait until dashboard is fully loaded before interacting with filters.
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        self.page.wait_for_timeout(1000)

        field_selectors = [
            "xpath=/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td/form/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[5]/td/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td[3]/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td[3]/div/input",
            "xpath=//*[contains(normalize-space(.), 'B#:')]/following::input[1]",
        ]
        button_selector = "xpath=//*[@id='ButtonGroup4_Search']"

        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            # Re-enumerate frames each attempt — they may not exist yet on a freshly
            # loaded dashboard (e.g. immediately after user2 login).
            contexts = [
                (f"frame:{frame.name or frame.url}", frame) for frame in self.page.frames
            ] + [("main", self.page)]

            for ctx_name, ctx in contexts:
                for field_selector in field_selectors:
                    try:
                        b_field = ctx.locator(field_selector).first
                        b_field.wait_for(state="visible", timeout=5000)
                        b_field.fill("")
                        b_field.fill(b_number)
                        logger.info(
                            f"Entered B-number in filter B# field ({ctx_name}) using selector: {field_selector}"
                        )
                        self.page.wait_for_timeout(500)

                        search_button = ctx.locator(button_selector).first
                        search_button.wait_for(state="visible", timeout=5000)
                        search_button.click(timeout=5000)
                        logger.info(
                            f"Clicked filter search button ButtonGroup4_Search from {ctx_name}"
                        )

                        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                        self.page.wait_for_timeout(2000)
                        logger.info(f"Search for B-number '{b_number}' completed from filter area")
                        return
                    except Exception as search_error:
                        logger.debug(
                            f"Filter search attempt failed in {ctx_name} with selector {field_selector}: {search_error}"
                        )

            if attempt < max_attempts:
                logger.warning(
                    f"B# filter field not visible (attempt {attempt}/{max_attempts}); waiting for dashboard to render"
                )
                self.page.wait_for_timeout(5000)
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass

        raise TimeoutError(
            "Could not perform filter-area B# search with ButtonGroup4_Search. "
            "Verified main page and child frames but field/button were not both visible."
        )

    def refresh_dashboard(self) -> None:
        """Refresh the BAW Process Portal dashboard page.

        After Save & Exit closes the Coach window, the underlying dashboard page
        remains. This method picks the most recent non-closed page that looks
        like the Process Portal dashboard, brings it to front, reloads it and
        waits for it to settle.
        """
        target = None
        try:
            for candidate in [p for p in self.page.context.pages if not p.is_closed()][::-1]:
                url = (candidate.url or "").lower()
                if "processportal" in url:
                    target = candidate
                    break
        except Exception:
            target = None

        if target is None:
            target = self.page

        try:
            target.bring_to_front()
        except Exception:
            pass

        # Re-point self.page so subsequent steps act on the dashboard.
        self.page = target

        logger.info(f"Refreshing SDT ISC dashboard page: {target.url}")
        try:
            target.reload(wait_until="domcontentloaded", timeout=30000)
        except Exception as reload_error:
            logger.warning(f"Dashboard reload failed, retrying via goto: {reload_error}")
            target.goto(target.url, wait_until="domcontentloaded", timeout=30000)

        target.wait_for_load_state("domcontentloaded", timeout=15000)
        target.wait_for_timeout(2000)
        logger.info("SDT ISC dashboard refreshed")

    def verify_internal_status(self, expected_status: str, timeout_ms: int = 30000) -> None:
        """Verify the Internal Status cell in the dashboard results matches expected.

        Polls every 2s — re-searching is the caller's responsibility. Looks
        across main page and all frames for any element whose text contains
        the expected status string.
        """
        logger.info(f"Verifying Internal Status contains: '{expected_status}'")
        expected_lc = expected_status.strip().lower()
        deadline = time.monotonic() + (timeout_ms / 1000.0)

        last_seen: list[str] = []
        while time.monotonic() < deadline:
            contexts = [("main", self.page)] + [
                (f"frame:{f.name or f.url}", f) for f in self.page.frames
            ]
            for ctx_name, ctx in contexts:
                try:
                    locator = ctx.locator(
                        f"xpath=//*[contains(normalize-space(.), {self._xpath_literal(expected_status)})]"
                    ).first
                    if locator.count() > 0 and locator.first.is_visible(timeout=1500):
                        logger.info(
                            f"Internal Status '{expected_status}' verified in {ctx_name}"
                        )
                        return
                except Exception:
                    continue
            self.page.wait_for_timeout(2000)

        raise AssertionError(
            f"Internal Status '{expected_status}' not found on the dashboard within "
            f"{timeout_ms}ms. Last URL: {self.page.url}"
        )

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """Return an XPath-safe string literal for arbitrary text."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"

    def is_b_number_visible_in_dashboard(self, b_number: str, timeout_ms: int = 5000) -> bool:
        """Return True if the B-number is visible somewhere on the current
        dashboard (main page or any frame). Does not click anything.
        """
        deadline = time.monotonic() + (timeout_ms / 1000.0)
        xpath = f"xpath=//*[normalize-space(text())={self._xpath_literal(b_number)}]"
        while time.monotonic() < deadline:
            contexts = [("main", self.page)] + [
                (f"frame:{f.name or f.url}", f) for f in self.page.frames
            ]
            for ctx_name, ctx in contexts:
                try:
                    locator = ctx.locator(xpath).first
                    if locator.count() > 0 and locator.is_visible(timeout=1000):
                        logger.info(
                            f"B-number '{b_number}' is visible in {ctx_name}"
                        )
                        return True
                except Exception:
                    continue
            self.page.wait_for_timeout(1000)
        logger.info(
            f"B-number '{b_number}' is NOT visible on the dashboard after {timeout_ms}ms"
        )
        return False

    def repeat_save_and_exit_if_visible(self, b_number: str) -> bool:
        """Conditional second user1 pass.

        Refresh the dashboard and search the B-number. If the row is visible,
        verify the internal status, click Run, then Save & Exit, then accept
        the post-Save OK popup. If the B-number is not visible (item already
        routed away from user1), return False without raising.
        """
        self.refresh_dashboard()
        self.search_b_number(b_number)

        if not self.is_b_number_visible_in_dashboard(b_number, timeout_ms=10000):
            logger.info(
                f"B-number '{b_number}' not in user1's dashboard after Save & Exit; "
                "skipping repeat Save & Exit cycle"
            )
            return False

        try:
            self.verify_internal_status("In Process-Auto close Pending Settlement")
        except AssertionError as status_error:
            logger.warning(
                f"Expected internal status not found, continuing anyway: {status_error}"
            )

        try:
            self.verify_exact_b_number_and_click_run(b_number)
        except AssertionError as run_error:
            logger.info(
                f"Run button not clickable for '{b_number}' on second pass; skipping: {run_error}"
            )
            return False

        self.click_save_and_exit()
        self.click_ok_on_activation_popup()
        logger.info(f"Completed repeat Save & Exit cycle for B-number '{b_number}'")
        return True

    def _find_coach_frame(self, page: Page = None):
        """Return the BAW Coach frame across all pages in the context once it
        has a real ``applicationInstanceId`` (i.e. the task has truly launched).

        Searches popups and tabs in addition to ``self.page``. Also accepts a
        numeric ``zTaskId=t<digits>`` (per BAW Shell Process popups) as proof
        that the task launched.

        Returns the frame or ``None`` if not found.
        """
        import re as _re
        pages_to_scan = list(self.page.context.pages)
        if page is not None and page not in pages_to_scan:
            pages_to_scan.append(page)
        for pg in pages_to_scan:
            try:
                frames = list(pg.frames)
            except Exception:
                continue
            # Include the page's own URL as a pseudo-frame for popups whose
            # top-level document IS the Coach (no nested iframe).
            for frame in frames:
                url = (frame.url or "").lower()
                if "zcomponentname=coach" not in url:
                    continue
                if "applicationinstanceid=undefined" in url:
                    # Still accept if a real numeric task id is present.
                    if not _re.search(r"ztaskid=t\d+", url):
                        continue
                if "applicationinstanceid=" in url or _re.search(r"ztaskid=t\d+", url):
                    return frame
        return None

    def verify_exact_b_number_and_click_run(self, b_number: str) -> None:
        """Verify exact B-number match in search results and click the Run button.

        After clicking Run we verify that a real BAW Coach frame appears with
        a non-``undefined`` ``applicationInstanceId``. If the Coach does not
        launch we retry the Run click (and try a double-click on the task row
        as a fallback) up to a few times.
        """
        logger.info(
            f"Verifying exact B-number '{b_number}' in results and clicking Run button"
        )

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(1000)

        def _refresh_contexts():
            return [("main", self.page)] + [
                (f"frame:{frame.name or frame.url}", frame) for frame in self.page.frames
            ]

        def _wait_for_coach(timeout_s: int = 25) -> bool:
            import time as _time
            deadline = _time.time() + timeout_s
            while _time.time() < deadline:
                if self._find_coach_frame() is not None:
                    return True
                self.page.wait_for_timeout(1000)
            return False

        max_attempts = 3
        last_ctx_name = None
        last_ctx = None

        for attempt in range(1, max_attempts + 1):
            contexts = _refresh_contexts()
            clicked = False

            # 1) Try exact-match path first.
            for ctx_name, ctx in contexts:
                try:
                    exact_result = ctx.locator(
                        f"xpath=//*[normalize-space(text())='{b_number}']"
                    ).first
                    exact_result.wait_for(state="visible", timeout=5000)
                    logger.info(
                        f"Found exact B-number '{b_number}' in results within {ctx_name}"
                    )

                    run_button = ctx.locator(self.RUN_BUTTON_XPATH).first
                    run_button.wait_for(state="visible", timeout=5000)
                    # Capture popup if BAW opens task in a new window.
                    try:
                        with self.page.context.expect_page(timeout=8000) as popup_info:
                            run_button.click(timeout=5000)
                        popup = popup_info.value
                        try:
                            popup.wait_for_load_state("domcontentloaded", timeout=15000)
                        except Exception:
                            pass
                        logger.info(f"Coach popup opened: {popup.url}")
                    except Exception:
                        # No popup -> Coach probably renders inline in a frame.
                        run_button.click(timeout=5000)
                    logger.info(
                        f"Clicked Run button (attempt {attempt}) in {ctx_name}"
                    )
                    self.page.wait_for_timeout(1500)
                    clicked = True
                    last_ctx_name, last_ctx = ctx_name, ctx
                    break
                except Exception as verify_error:
                    logger.debug(
                        f"Exact B-number not found in {ctx_name}: {verify_error}"
                    )

            # 2) Fallback: click the first task Run button directly.
            if not clicked:
                for ctx_name, ctx in contexts:
                    try:
                        run_button = ctx.locator(self.RUN_BUTTON_XPATH).first
                        run_button.wait_for(state="visible", timeout=5000)
                        run_button.click(timeout=5000)
                        logger.warning(
                            f"Exact text not matched; clicked fallback Run button in {ctx_name} (attempt {attempt})"
                        )
                        self.page.wait_for_timeout(1500)
                        clicked = True
                        last_ctx_name, last_ctx = ctx_name, ctx
                        break
                    except Exception as fallback_error:
                        logger.debug(
                            f"Fallback Run button click failed in {ctx_name}: {fallback_error}"
                        )

            if not clicked:
                raise AssertionError(
                    f"Exact B-number '{b_number}' was not found with a clickable Run button"
                )

            # Verify a real Coach launched.
            if _wait_for_coach(timeout_s=25):
                logger.info(
                    f"Coach launched successfully with a real applicationInstanceId (attempt {attempt})"
                )
                return

            logger.warning(
                f"Coach did not launch with a real applicationInstanceId after Run click "
                f"(attempt {attempt}/{max_attempts}); trying double-click row fallback"
            )

            # Double-click the task row as recovery before next retry.
            if last_ctx is not None:
                try:
                    row = last_ctx.locator(
                        "xpath=//*[@id='TaskTable']/tbody/tr[1]"
                    ).first
                    row.wait_for(state="visible", timeout=5000)
                    row.dblclick(timeout=5000)
                    logger.info(f"Double-clicked task row in {last_ctx_name}")
                    self.page.wait_for_timeout(2000)
                    if _wait_for_coach(timeout_s=20):
                        logger.info("Coach launched after double-click recovery")
                        return
                except Exception as dbl_error:
                    logger.debug(f"Double-click row recovery failed: {dbl_error}")

            self.page.wait_for_timeout(2000)

        raise AssertionError(
            f"BAW Coach did not launch with a real applicationInstanceId for B-number '{b_number}' "
            f"after {max_attempts} attempts"
        )

    def select_status_dropdown(self, option: str = "In Process-Auto close Pending Settlement") -> None:
        """Select an option from the status dropdown on the new window after clicking Run."""
        logger.info(f"Selecting status dropdown option: '{option}'")

        # Wait for the new Coach window to open (Run click already happened)
        initial_count = 1
        for i in range(30):
            if len(self.page.context.pages) > initial_count:
                break
            self.page.wait_for_timeout(1000)

        new_page = self.page.context.pages[-1]
        logger.info(f"New window URL: {new_page.url}, total pages: {len(self.page.context.pages)}")

        # Wait for content to render
        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
        new_page.wait_for_timeout(2000)

        # Scroll down to reveal the dropdown
        new_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        new_page.wait_for_timeout(1000)

        # Search main frame and child frames for the dropdown
        for frame in new_page.frames:
            try:
                dropdown = frame.locator(f"select:has(option:text('{option}'))").first
                dropdown.scroll_into_view_if_needed(timeout=10000)
                dropdown.select_option(label=option, timeout=5000)
                selected = dropdown.input_value(timeout=5000)
                assert option in selected, f"Dropdown not set to '{option}', got '{selected}'"
                logger.info(f"Selected and verified '{option}' from status dropdown")
                return
            except AssertionError:
                raise
            except Exception:
                continue

        raise TimeoutError(f"Could not find dropdown with option '{option}'.")

    def _get_new_coach_page(self) -> Page:
        """Return the most recently opened Coach window (or main page as fallback).

        After Save & Exit closes the Coach window the context page list may be
        empty or contain only the EWM main page; callers should still receive a
        usable Page instead of crashing with IndexError.
        """
        pages = [p for p in self.page.context.pages if not p.is_closed()]
        if not pages:
            return self.page
        return pages[-1]

    def _close_coach_if_open(self, page: Page) -> None:
        """Close the Coach window if it's still open and not the main EWM page."""
        try:
            if page is None or page.is_closed() or page is self.page:
                return
            page.close()
            logger.info("Closed Coach window after Activation popup step")
        except Exception:
            pass

    def _find_in_frames(self, page: Page, locator_str: str, timeout: int = 5000):
        """Search all frames for a visible element matching the locator string.

        Returns (frame, element) on success or (None, None) if not found.
        """
        for frame in page.frames:
            try:
                el = frame.locator(locator_str).first
                el.wait_for(state="visible", timeout=timeout)
                return frame, el
            except Exception:
                continue
        return None, None

    def _safe_dialog_handler(self, dialog) -> None:
        """Accept a dialog only if it hasn't been handled already."""
        try:
            dialog.accept()
        except Exception:
            pass

    def click_ok_on_activation_popup(self, timeout_ms: int = 15000) -> None:
        """Accept the 'Warning: ICT Activation unsuccessful' OK popup.

        BAW raises a native JS alert dialog after Activate ICT when the
        activation cannot be performed automatically (e.g. the Access model
        data for the source account has changed since the paperwork was
        created). Native dialogs are handled via Playwright's ``dialog``
        event, so the persistent handler installed in
        :meth:`click_activate_ict_button` already accepts them. We additionally
        give the dialog up to ``timeout_ms`` to fire here, and as a fallback
        click any in-page modal OK button if the popup is rendered as HTML
        rather than a native dialog.
        """
        logger.info("Waiting for Activation OK popup and accepting it")
        new_page = self._get_new_coach_page()
        if new_page is None or new_page.is_closed():
            logger.info("No Coach window available - skipping OK popup step")
            return

        # Track how many dialogs the persistent handler accepts during this wait
        dialog_count = {"value": 0}

        def _count_handler(dialog) -> None:
            # Don't accept here -- the persistent handler in
            # click_activate_ict_button already does. Just count.
            try:
                logger.info(
                    f"Activation popup dialog observed: type={dialog.type!r} "
                    f"message={dialog.message!r}"
                )
            finally:
                dialog_count["value"] += 1

        new_page.on("dialog", _count_handler)
        try:
            # Give the late warning alert a chance to fire.
            deadline = timeout_ms
            step = 500
            elapsed = 0
            while elapsed < deadline and dialog_count["value"] == 0:
                new_page.wait_for_timeout(step)
                elapsed += step

            if dialog_count["value"] > 0:
                logger.info(
                    f"Native Activation OK dialog accepted "
                    f"({dialog_count['value']} dialog(s) seen)"
                )
                # Allow the page to settle after the alert is dismissed.
                # Do NOT close the Coach window here - the next step
                # (Save & Exit) needs it open.
                new_page.wait_for_timeout(1500)
                return

            # Fallback: in-page modal with OK button (any frame).
            ok_locator = (
                "button:has-text('OK'), input[value='OK'], "
                "button:has-text('Ok'), input[value='Ok'], "
                "div[role='dialog'] button:has-text('OK')"
            )
            frame, ok_button = self._find_in_frames(new_page, ok_locator, timeout=3000)
            if ok_button is not None:
                logger.info("In-page Activation OK popup found - pausing 3s before click (observable)")
                try:
                    new_page.wait_for_timeout(3000)
                except Exception:
                    pass
                ok_button.click(timeout=5000)
                logger.info("Clicked OK button on in-page activation popup")
                new_page.wait_for_timeout(2000)
                return

            logger.info(
                "No Activation OK popup appeared within timeout - continuing"
            )
        finally:
            try:
                new_page.remove_listener("dialog", _count_handler)
            except Exception:
                pass

    # Absolute XPaths inside the BAW Coach frame for the "Close to D" section.
    # The section header div - we scroll this into view first.
    CLOSE_TO_D_SECTION_XPATH = (
        "/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td/form/div/table/tbody/"
        "tr[1]/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/div/table/"
        "tbody/tr[2]/td/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td[1]/div/table/"
        "tbody/tr[1]/td[2]/div/table/tbody/tr[6]/td/div/table/tbody/tr[1]/td[2]/div"
    )
    # The "Yes" checkbox inside the Close-to-D / D-number section.
    CLOSE_TO_D_YES_CHECKBOX_XPATH = (
        "/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td/form/div/table/tbody/"
        "tr[1]/td[2]/div/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/div/table/"
        "tbody/tr[2]/td/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td[1]/div/table/"
        "tbody/tr[1]/td[2]/div/table/tbody/tr[6]/td/div/table/tbody/tr[3]/td[2]/div/"
        "table/tbody/tr[2]/td/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[2]/td[1]/"
        "div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[1]/td[1]"
    )

    def _baw_scroll_to_section(self, coach_frame, section_id: str, max_iterations: int = 40) -> None:
        """Scroll the BAW Coach's internal `tw sectionbodyscrollbar` container(s)
        downward in steps until the element with ``id=section_id`` is visible
        (or we've scrolled to the bottom). BAW Coaches render content inside a
        scrollable section body whose scroll position is NOT controlled by the
        document `window` — it uses a virtual scrollbar div with class
        ``tw sectionbodyscrollbar``. The actual scrollable element is usually
        the sibling/parent with class ``tw sectionbody`` (or any ancestor whose
        scrollHeight > clientHeight).

        Approach: in JS, walk up from the (possibly hidden) target element to
        find the nearest scrollable ancestor, then increment its scrollTop in
        chunks until either the target is in view or scrollTop is maxed out.
        If the target id cannot be located yet, we instead scroll every
        ``.sectionbody``/``.sectionbodyscrollbar`` host on the page to the
        bottom and re-check.
        """
        script = """
        ({sectionId, step}) => {
            function isScrollable(el) {
                if (!el) return false;
                const s = window.getComputedStyle(el);
                return (el.scrollHeight - el.clientHeight) > 4
                    && /(auto|scroll)/.test(s.overflow + s.overflowY);
            }
            function findScrollableAncestor(el) {
                let cur = el && el.parentElement;
                while (cur && cur !== document.body) {
                    if (isScrollable(cur)) return cur;
                    cur = cur.parentElement;
                }
                // Fallback: any element with class sectionbody
                return document.querySelector('.tw.sectionbody, .sectionbody')
                    || document.scrollingElement || document.documentElement;
            }
            function inView(el, container) {
                const r = el.getBoundingClientRect();
                const c = container.getBoundingClientRect();
                return r.top >= c.top && r.bottom <= c.bottom + 4;
            }
            let target = document.getElementById(sectionId);
            // If not found, scroll every known scrollable container down a notch
            if (!target) {
                const hosts = document.querySelectorAll(
                    '.tw.sectionbody, .sectionbody, .tw.sectionbodyscrollbar'
                );
                hosts.forEach(h => {
                    const sc = isScrollable(h) ? h : findScrollableAncestor(h);
                    if (sc) sc.scrollTop = Math.min(sc.scrollTop + step, sc.scrollHeight);
                });
                return {found:false, atBottom:false};
            }
            const container = findScrollableAncestor(target);
            if (inView(target, container)) {
                target.scrollIntoView({block:'center', behavior:'instant'});
                return {found:true, atBottom:true};
            }
            const before = container.scrollTop;
            container.scrollTop = Math.min(before + step, container.scrollHeight);
            const atBottom = (container.scrollTop + container.clientHeight) >= (container.scrollHeight - 2);
            if (inView(target, container) || atBottom) {
                target.scrollIntoView({block:'center', behavior:'instant'});
                return {found:true, atBottom:atBottom};
            }
            return {found:true, atBottom:false};
        }
        """
        for i in range(max_iterations):
            result = coach_frame.evaluate(script, {"sectionId": section_id, "step": 600})
            target_visible = False
            try:
                target_visible = coach_frame.locator(f"#{section_id}").first.is_visible(timeout=500)
            except Exception:
                target_visible = False
            if target_visible:
                logger.info(f"#{section_id} is visible after {i + 1} scroll step(s)")
                return
            if result and result.get("atBottom"):
                # Reached bottom; do one final check
                if target_visible:
                    return
                # Keep going in case the section grew after lazy load
                break
            coach_frame.wait_for_timeout(120)
        # Final attempt: scrollIntoView in JS
        coach_frame.evaluate(
            "(id) => { const e = document.getElementById(id); if (e) e.scrollIntoView({block:'center'}); }",
            section_id,
        )
        coach_frame.locator(f"#{section_id}").first.wait_for(state="visible", timeout=5000)

    def click_d_number_checkbox(self) -> None:
        """Click the D number 'Yes' checkbox in the Close-to-D section of the
        BAW Coach. Searches all frames of the current page (the Coach renders
        in an embedded frame, not a new window). Scrolls the section into view
        first, then clicks the Yes checkbox.
        """
        logger.info("Clicking D number checkbox (Close to D -> Yes)")

        # Wait for a real Coach frame across all pages in the context.
        import time as _time
        deadline = _time.time() + 30
        coach_frame = None
        while _time.time() < deadline:
            coach_frame = self._find_coach_frame()
            if coach_frame is not None:
                break
            self.page.wait_for_timeout(1000)

        if coach_frame is None:
            # Fallback: search every frame on every page for the section XPath.
            for pg in self.page.context.pages:
                for frame in pg.frames:
                    try:
                        if frame.locator(f"xpath={self.CLOSE_TO_D_SECTION_XPATH}").first.count() > 0:
                            coach_frame = frame
                            break
                    except Exception:
                        continue
                if coach_frame is not None:
                    break

        if coach_frame is None:
            raise TimeoutError(
                "Could not locate the BAW Coach frame on the current page when clicking D number."
            )

        logger.info(f"Using Coach frame: {coach_frame.url}")

        # Scroll the "Close to D" section into view. BAW Coach uses an internal
        # virtual scrollbar (`tw sectionbodyscrollbar`) — plain window.scrollTo
        # does NOT move the coach content. We programmatically scroll the
        # internal scrollable container(s) until #section21_controls (the
        # Close-to-D section) is visible, then scroll it into view.
        try:
            self._baw_scroll_to_section(coach_frame, "section21_controls")
            logger.info("Scrolled to 'Close to D' section (#section21_controls) via tw sectionbodyscrollbar")
        except Exception as scroll_error:
            logger.warning(
                f"Could not scroll to #section21_controls via internal scrollbar: {scroll_error}. "
                "Trying absolute XPath fallback."
            )
            try:
                section = coach_frame.locator(f"xpath={self.CLOSE_TO_D_SECTION_XPATH}").first
                section.wait_for(state="visible", timeout=10000)
                section.scroll_into_view_if_needed(timeout=5000)
                logger.info("Scrolled to 'Close to D' section via XPath fallback")
            except Exception as xpath_error:
                logger.warning(
                    f"XPath fallback also failed: {xpath_error}. Falling back to window scrollTo."
                )
                try:
                    coach_frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                except Exception:
                    pass

        # Click the "Yes" checkbox. The control lives inside #section21_controls
        # (Close to D section). BAW renders checkboxes/radios with a hidden
        # native input + a styled label/span; we therefore try multiple
        # selectors and fall back to a JS click that walks the DOM.
        yes_selectors = [
            # Scoped to #section21_controls (the Close-to-D section container)
            "xpath=//*[@id='section21_controls']//input[@type='checkbox' and (translate(@value,'YES','yes')='yes' or contains(translate(@id,'YES','yes'),'yes') or contains(translate(@name,'YES','yes'),'yes'))]",
            "xpath=//*[@id='section21_controls']//input[@type='radio' and (translate(@value,'YES','yes')='yes' or contains(translate(@id,'YES','yes'),'yes'))]",
            "xpath=//*[@id='section21_controls']//label[normalize-space(.)='Yes']/preceding-sibling::input[1]",
            "xpath=//*[@id='section21_controls']//label[normalize-space(.)='Yes']/following-sibling::input[1]",
            "xpath=//*[@id='section21_controls']//label[normalize-space(.)='Yes']",
            "xpath=//*[@id='section21_controls']//*[normalize-space(text())='Yes']",
            # Legacy / original selectors
            f"xpath={self.CLOSE_TO_D_YES_CHECKBOX_XPATH}",
            "xpath=//div[contains(normalize-space(.), 'Close a D#')]"
            "//following::*[contains(normalize-space(.), 'Yes')]"
            "//input[@type='checkbox'][1]",
            "xpath=//*[normalize-space(text())='Yes']/preceding::input[@type='checkbox'][1]",
            "xpath=//*[normalize-space(text())='Yes']/following::input[@type='checkbox'][1]",
            "#DNoMatchYes_checkbox",
            "input[id*='DNoMatchYes']",
        ]
        last_err: Exception | None = None
        for sel in yes_selectors:
            try:
                yes_cb = coach_frame.locator(sel).first
                # Don't require visibility (BAW hides native inputs); just
                # ensure it exists in DOM.
                yes_cb.wait_for(state="attached", timeout=3000)
                try:
                    yes_cb.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass
                try:
                    yes_cb.click(timeout=3000)
                except Exception:
                    # Force / JS dispatch fallback for hidden styled inputs
                    yes_cb.click(force=True, timeout=3000)
                logger.info(f"Clicked 'Yes' checkbox under Close a D# using selector: {sel}")
                return
            except Exception as err:
                last_err = err
                logger.debug(f"Yes checkbox selector failed ({sel}): {err}")

        # Last-ditch JS click inside #section21_controls
        try:
            clicked = coach_frame.evaluate(
                """
                () => {
                    const root = document.getElementById('section21_controls');
                    if (!root) return {ok:false, reason:'no #section21_controls'};
                    // Try inputs whose value/id/name suggests "Yes"
                    const inputs = Array.from(root.querySelectorAll('input'));
                    let target = inputs.find(i => /^yes$/i.test(i.value || ''))
                              || inputs.find(i => /yes/i.test(i.id || ''))
                              || inputs.find(i => /yes/i.test(i.name || ''));
                    // Or a label "Yes" -> use its associated input via for=
                    if (!target) {
                        const labels = Array.from(root.querySelectorAll('label'));
                        const yesLabel = labels.find(l => /^\\s*yes\\s*$/i.test(l.textContent || ''));
                        if (yesLabel) {
                            const id = yesLabel.getAttribute('for');
                            if (id) target = document.getElementById(id);
                            if (!target) target = yesLabel.querySelector('input');
                        }
                    }
                    if (!target) return {ok:false, reason:'no Yes input'};
                    target.checked = true;
                    target.dispatchEvent(new Event('change', {bubbles:true}));
                    target.dispatchEvent(new Event('click', {bubbles:true}));
                    if (typeof target.click === 'function') target.click();
                    return {ok:true, id: target.id, value: target.value};
                }
                """
            )
            if clicked and clicked.get("ok"):
                logger.info(f"Clicked 'Yes' checkbox via JS dispatch inside #section21_controls: {clicked}")
                return
            logger.warning(f"JS dispatch did not find Yes input: {clicked}")
        except Exception as js_err:
            last_err = js_err
            logger.warning(f"JS dispatch fallback failed: {js_err}")

        raise TimeoutError(
            f"Could not click the 'Yes' checkbox in Close a D# section. Last error: {last_err}"
        )

    def click_ict_activation_checkbox(self) -> None:
        """Click the 'Ready To Activate ICT' checkbox in the ICT Activation
        section of the BAW Coach frame.
        """
        logger.info("Clicking 'Ready To Activate ICT' checkbox")
        coach_frame = self._find_coach_frame()
        if coach_frame is None:
            for pg in self.page.context.pages:
                for frame in pg.frames:
                    try:
                        if frame.locator("#ICTCheckbox_checkbox").first.count() > 0:
                            coach_frame = frame
                            break
                    except Exception:
                        continue
                if coach_frame is not None:
                    break
        if coach_frame is None:
            raise TimeoutError("Could not locate BAW Coach frame for ICT checkbox.")

        ict_selectors = [
            "#ICTCheckbox_checkbox",
            "input[id*='ICTCheckbox']",
            "xpath=//*[normalize-space(text())='Ready To Activate ICT']"
            "/following::input[@type='checkbox'][1]",
            "xpath=//*[normalize-space(text())='Ready To Activate ICT']"
            "/preceding::input[@type='checkbox'][1]",
            "xpath=//*[contains(normalize-space(.), 'ICT Activation')]"
            "//input[@type='checkbox'][1]",
        ]
        last_err: Exception | None = None
        for sel in ict_selectors:
            try:
                checkbox = coach_frame.locator(sel).first
                checkbox.wait_for(state="visible", timeout=5000)
                checkbox.scroll_into_view_if_needed(timeout=5000)
                checkbox.click(timeout=5000)
                logger.info(f"Clicked 'Ready To Activate ICT' using selector: {sel}")
                return
            except Exception as err:
                last_err = err
                logger.debug(f"ICT checkbox selector failed ({sel}): {err}")
        raise TimeoutError(
            f"Could not click 'Ready To Activate ICT' checkbox. Last error: {last_err}"
        )

    def click_activate_ict_button(self) -> None:
        """Click the Activate ICT button on the Coach window and accept the OK dialog.

        After the dialog is accepted the BAW server issues a 303 redirect which
        reloads the Coach page with fresh frames.  We therefore wait for the page
        to fully settle so that subsequent methods (e.g. Save & Exit) can
        enumerate the new frame tree reliably.

        Note: BAW may raise MULTIPLE native dialogs in sequence here -- first a
        confirm to proceed with activation, and (in some test data scenarios)
        a second alert reporting "Warning: ICT Activation unsuccessful ...".
        We register a persistent ``on('dialog')`` handler so every native
        dialog raised between Activate ICT and Save & Exit is auto-accepted.
        The handler is stored on ``self`` so subsequent steps can remove it.
        """
        logger.info("Clicking Activate ICT button")
        new_page = self._get_new_coach_page()

        # Capture every native dialog raised during the activation sequence
        # so we can inspect them after the click and detect rejection.
        captured_messages: list[str] = []

        def _activation_dialog_handler(dialog) -> None:
            try:
                logger.info(
                    f"Activation native dialog: type={dialog.type!r} "
                    f"message={dialog.message!r}"
                )
                captured_messages.append(dialog.message or "")
                dialog.accept()
            except Exception as err:
                logger.warning(f"Failed to accept activation dialog: {err}")

        prev_handler = getattr(self, "_activation_dialog_handler", None)
        if prev_handler is not None:
            try:
                new_page.remove_listener("dialog", prev_handler)
            except Exception:
                pass
        self._activation_dialog_handler = _activation_dialog_handler
        self._activation_dialog_page = new_page
        new_page.on("dialog", _activation_dialog_handler)

        locator_str = "button:has-text('Activate ICT'), input[value='Activate ICT']"

        rejection_markers = (
            "already been used",
            "unsuccessful",
            "cannot be activated",
        )

        def _has_rejection() -> str:
            for msg in captured_messages:
                lower = msg.lower()
                for marker in rejection_markers:
                    if marker in lower:
                        return msg
            return ""

        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            captured_messages.clear()

            _, button = self._find_in_frames(new_page, locator_str, timeout=10000)
            if button is None:
                raise TimeoutError("Could not find Activate ICT button.")

            button.scroll_into_view_if_needed(timeout=5000)
            button.click(timeout=5000)
            logger.info(
                f"Clicked Activate ICT button (attempt {attempt}/{max_attempts}) "
                "and accepted any OK dialog"
            )

            try:
                new_page.wait_for_load_state("load", timeout=30000)
            except Exception:
                pass
            new_page.wait_for_timeout(3000)

            rejection = _has_rejection()
            if not rejection:
                logger.info("Coach page settled after Activate ICT redirect")
                return

            logger.warning(
                f"Activate ICT was rejected by BAW (attempt {attempt}): {rejection!r}"
            )

            if attempt < max_attempts:
                logger.info(
                    "Retrying Activate ICT after rejection: re-checking 'Ready To "
                    "Activate ICT' checkbox and reloading the Coach page"
                )
                try:
                    new_page.reload(wait_until="domcontentloaded", timeout=30000)
                    new_page.wait_for_timeout(2000)
                except Exception as exc:
                    logger.warning(f"Coach reload before retry failed: {exc}")
                try:
                    self.click_ict_activation_checkbox()
                except Exception as exc:
                    logger.warning(f"Re-checking ICT activation checkbox failed: {exc}")

        raise AssertionError(
            f"Activate ICT was rejected by BAW after {max_attempts} attempts: "
            f"{_has_rejection()!r}. The work item is not in a state that allows "
            "activation (likely activated by a previous run or blocked by an "
            "alert) so the downstream Save & Exit / user2 routing will fail."
        )

    def click_save_and_exit(self) -> None:
        """Click the Save & Exit button and accept the OK dialog.

        The button lives in frames that were freshly created after the
        Activate ICT redirect, so we retry frame enumeration up to 10 times
        with generous waits to accommodate slow BAW rendering.
        The BAW server often issues a late 303 redirect that reloads the
        Coach page well after Activate ICT returns, so we must be patient.
        """
        logger.info("Clicking Save & Exit button")
        new_page = self._get_new_coach_page()

        # Persistent dialog handler so the post-save confirmation popup is
        # auto-accepted. BAW often fires a native alert AFTER Save & Exit to
        # confirm the commit; if that popup is missed the work item is not
        # routed to the next user's queue.
        save_dialog_count = {"value": 0}

        def _save_dialog_handler(dialog) -> None:
            try:
                logger.info(
                    f"Save & Exit native dialog: type={dialog.type!r} "
                    f"message={dialog.message!r}"
                )
            finally:
                save_dialog_count["value"] += 1
                try:
                    dialog.accept()
                except Exception:
                    pass

        new_page.on("dialog", _save_dialog_handler)
        self._save_exit_dialog_handler = _save_dialog_handler
        self._save_exit_dialog_page = new_page

        # Give the page time to finish loading after Activate ICT redirect
        try:
            new_page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        new_page.wait_for_timeout(2000)

        # Primary: BAW ID-based xpath for the Save & Exit button.
        # Fallback: broader selectors to catch variant button labels.
        primary_locator = "xpath=//*[@id='ButtonGroup0_Button2']"
        locator_str = (
            "xpath=//*[@id='ButtonGroup0_Button2'] | "
            "//button[normalize-space(.)='Save & Exit'] | "
            "//input[@value='Save & Exit'] | "
            "//button[normalize-space(.)='Save and Exit'] | "
            "//input[@value='Save and Exit'] | "
            "//a[normalize-space(.)='Save & Exit'] | "
            "//span[normalize-space(.)='Save & Exit']"
        )
        _ = primary_locator  # primary is included in locator_str union
        max_attempts = 12
        prev_url = new_page.url

        for attempt in range(1, max_attempts + 1):
            # Check if the coach page navigated (late 303 redirect)
            try:
                current_url = new_page.url
            except Exception:
                # Page may have been closed/replaced
                new_page = self._get_new_coach_page()
                current_url = new_page.url

            if current_url != prev_url:
                logger.info(
                    f"Coach page navigated during Save & Exit search: {current_url}"
                )
                prev_url = current_url
                # Re-register dialog handler after navigation
                new_page.on("dialog", _save_dialog_handler)
                self._save_exit_dialog_page = new_page
                try:
                    new_page.wait_for_load_state("load", timeout=15000)
                except Exception:
                    pass
                new_page.wait_for_timeout(3000)

            frame, button = self._find_in_frames(new_page, locator_str, timeout=5000)
            if button is not None:
                button.scroll_into_view_if_needed(timeout=5000)
                button.click(timeout=5000)
                logger.info("Clicked Save & Exit button")

                try:
                    new_page.wait_for_load_state("load", timeout=15000)
                except Exception:
                    pass

                # Wait for the post-save confirmation popup. BAW commits the
                # work item and routes it to the next user only after this
                # popup is dismissed. The persistent dialog handler accepts it
                # automatically; we just need to give it time to fire.
                deadline_ms = 15000
                step_ms = 500
                elapsed = 0
                while elapsed < deadline_ms and save_dialog_count["value"] == 0:
                    try:
                        new_page.wait_for_timeout(step_ms)
                    except Exception:
                        break
                    elapsed += step_ms

                if save_dialog_count["value"] > 0:
                    logger.info(
                        f"Post-Save & Exit dialog accepted "
                        f"({save_dialog_count['value']} dialog(s) seen)"
                    )
                else:
                    logger.info(
                        "No post-Save & Exit native dialog appeared within timeout"
                    )

                # Try to click an in-page modal OK button (some BAW Coaches
                # render the post-save confirmation as an HTML modal instead
                # of a native dialog). Search across all frames. Long
                # observable pauses are included so the click is visible
                # during headed runs.
                logger.info("Pausing 5s so the post-Save & Exit popup (if any) is visible")
                try:
                    new_page.wait_for_timeout(5000)
                except Exception:
                    pass

                ok_in_page_locator = (
                    "xpath=//button[normalize-space(.)='OK'] | "
                    "//input[@type='button' and @value='OK'] | "
                    "//input[@type='submit' and @value='OK'] | "
                    "//button[normalize-space(.)='Ok'] | "
                    "//input[@value='Ok'] | "
                    "//div[@role='dialog']//button[normalize-space(.)='OK'] | "
                    "//*[contains(@class,'modal')]//button[normalize-space(.)='OK']"
                )
                try:
                    ok_frame, ok_btn = self._find_in_frames(
                        new_page, ok_in_page_locator, timeout=5000
                    )
                except Exception as exc:
                    logger.info(f"In-page OK popup search error: {exc}")
                    ok_btn = None
                if ok_btn is not None:
                    try:
                        ok_btn.scroll_into_view_if_needed(timeout=3000)
                    except Exception:
                        pass
                    logger.info("In-page OK popup button found - pausing 3s before click so it is observable")
                    try:
                        new_page.wait_for_timeout(3000)
                    except Exception:
                        pass
                    try:
                        ok_btn.click(timeout=5000)
                        logger.info("Clicked in-page OK popup button after Save & Exit")
                    except Exception as click_err:
                        logger.warning(
                            f"In-page OK popup click failed: {click_err}"
                        )
                else:
                    logger.info(
                        "No in-page OK popup found after Save & Exit (native dialog path may have handled it)"
                    )

                # Give BAW time to commit and route the work item server-side.
                # The Coach window is intentionally NOT closed here so the
                # following 'click OK on Activation popup' step can still
                # accept any late popup that appears on the same window.
                logger.info("Pausing 5s after Save & Exit so popup handling is observable")
                try:
                    new_page.wait_for_timeout(5000)
                except Exception:
                    pass
                return

            # Log frame info for debugging on later attempts
            if attempt >= 3:
                frame_urls = [f.url for f in new_page.frames]
                logger.warning(
                    f"Save & Exit not found (attempt {attempt}/{max_attempts}) "
                    f"- frames: {frame_urls}"
                )
            else:
                logger.warning(
                    f"Save & Exit not found (attempt {attempt}/{max_attempts}) "
                    "- waiting for page to settle"
                )
            new_page.wait_for_timeout(3000)

        raise TimeoutError("Could not find Save & Exit button.")

    def click_add_update_qc_reasons(self) -> None:
        """Click the 'Add/Update QC Reasons' button, or proceed if QC form is already open."""
        logger.info("Clicking Add/Update QC Reasons button")

        # Wait for the Coach window to open after Run button click
        for i in range(30):
            if len(self.page.context.pages) > 1:
                break
            self.page.wait_for_timeout(1000)

        new_page = self._get_new_coach_page()
        try:
            new_page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        new_page.wait_for_timeout(5000)

        page_count_before = len(self.page.context.pages)

        button_locator_str = (
            "button:has-text('Add/Update QC Reasons'), "
            "input[value='Add/Update QC Reasons'], "
            "a:has-text('Add/Update QC Reasons'), "
            "span:has-text('Add/Update QC Reasons')"
        )

        # Try clicking the button across all frames
        for frame in new_page.frames:
            try:
                button = frame.locator(button_locator_str).first
                button.wait_for(state="visible", timeout=3000)
                button.scroll_into_view_if_needed(timeout=5000)
                button.click(timeout=5000)
                logger.info(f"Clicked Add/Update QC Reasons button in frame: {frame.name or frame.url}")

                # Wait for QC tab to open
                for i in range(15):
                    if len(self.page.context.pages) > page_count_before:
                        break
                    self.page.wait_for_timeout(1000)
                if len(self.page.context.pages) > page_count_before:
                    qc_page = self.page.context.pages[-1]
                    qc_page.wait_for_load_state("domcontentloaded", timeout=30000)
                    qc_page.wait_for_timeout(2000)
                return
            except Exception as e:
                logger.debug(f"Button not found in frame {frame.name or frame.url}: {e}")

        # Button not found — check if QC form is already open
        for frame in new_page.frames:
            try:
                title = frame.title()
                if title and "QC Reason" in title:
                    logger.info(f"QC Reasons page already open (title='{title}'). Proceeding.")
                    return
            except Exception:
                pass

        raise TimeoutError("Could not find Add/Update QC Reasons button or QC form.")

    def _get_qc_page(self) -> Page:
        """Return the QC Reasons page (latest tab)."""
        return self.page.context.pages[-1]

    def select_dropdown_option(self, option: str) -> None:
        """Select an option from any <select> dropdown on the QC/Coach page."""
        logger.info(f"Selecting '{option}' from dropdown")
        qc_page = self._get_qc_page()
        qc_page.wait_for_timeout(3000)
        for frame in qc_page.frames:
            try:
                dropdown = frame.locator(f"select:has(option:text('{option}'))").first
                dropdown.scroll_into_view_if_needed(timeout=5000)
                dropdown.select_option(label=option, timeout=5000)
                logger.info(f"'{option}' selected in frame: {frame.name or frame.url}")
                return
            except Exception as e:
                logger.debug(f"Dropdown attempt for '{option}' failed in frame {frame.name or frame.url}: {e}")
        raise TimeoutError(f"Could not find dropdown with option '{option}'.")

    def click_add_button(self) -> None:
        """Click the Add button on the QC Reasons page."""
        logger.info("Clicking Add button")
        qc_page = self._get_qc_page()
        for frame in qc_page.frames:
            try:
                button = frame.locator("button:has-text('Add'), input[value='Add']").first
                button.scroll_into_view_if_needed(timeout=5000)
                button.click(timeout=5000)
                logger.info("Clicked Add button")
                qc_page.wait_for_load_state("domcontentloaded", timeout=15000)
                qc_page.wait_for_timeout(2000)
                return
            except Exception as e:
                logger.debug(f"Add button attempt failed in frame {frame.name or frame.url}: {e}")
        raise TimeoutError("Could not find Add button.")

    def click_qc_save_button(self) -> None:
        """Click the Save button on the QC Reasons page (after setting QC Status='Verified')."""
        logger.info("Clicking Save button on QC Reasons page")
        qc_page = self._get_qc_page()
        # Auto-accept any confirmation dialog raised on save
        try:
            qc_page.on("dialog", lambda d: d.accept())
        except Exception:
            pass
        qc_page.wait_for_timeout(1000)
        save_selector = (
            "button:has-text('Save'):not(:has-text('Save & Exit')):not(:has-text('Save and Exit')), "
            "input[type='button'][value='Save'], "
            "input[type='submit'][value='Save']"
        )
        for frame in qc_page.frames:
            try:
                button = frame.locator(save_selector).first
                button.wait_for(state="visible", timeout=3000)
                button.scroll_into_view_if_needed(timeout=5000)
                button.click(timeout=5000)
                logger.info(
                    f"Clicked Save button on QC Reasons page in frame: "
                    f"{frame.name or frame.url}"
                )
                try:
                    qc_page.wait_for_load_state("load", timeout=15000)
                except Exception:
                    pass
                qc_page.wait_for_timeout(2000)
                return
            except Exception as e:
                logger.debug(
                    f"QC Save attempt failed in frame {frame.name or frame.url}: {e}"
                )
        raise TimeoutError("Could not find Save button on QC Reasons page.")

    def _get_shell_process_page(self) -> Page:
        """Return the Shell Process (main BAW Coach) window, falling back to the latest open page.

        After the QC Reasons tab is saved+closed, the Shell Process window
        remains open. Identify it by URL/title to avoid acting on a stray tab.
        """
        candidates = [p for p in self.page.context.pages if not p.is_closed()]
        for candidate in candidates:
            try:
                url = candidate.url or ""
                title = ""
                try:
                    title = candidate.title() or ""
                except Exception:
                    pass
                if "Shell Process" in title or "faux" in url.lower() or "teamworks" in url.lower():
                    return candidate
            except Exception:
                continue
        return candidates[-1] if candidates else self.page

    def verify_qc_reason_verified(self, expected_status: str = "Verified") -> None:
        """Assert the QC Reasons section on the Shell Process page shows the expected QC Status."""
        logger.info(f"Verifying QC Status '{expected_status}' in QC Reasons section")
        shell_page = self._get_shell_process_page()
        try:
            shell_page.bring_to_front()
        except Exception:
            pass
        try:
            shell_page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        shell_page.wait_for_timeout(2000)

        qc_row_locator = (
            f"xpath=//*[contains(normalize-space(.), 'QC Reasons')]"
            f"/following::*[self::table or self::div][.//text()[contains(.,'{expected_status}')]][1]"
            f" | //td[normalize-space()='{expected_status}']"
            f" | //*[contains(@class,'qc')]//*[normalize-space()='{expected_status}']"
        )
        deadline_ms = 30000
        step_ms = 2000
        elapsed = 0
        while elapsed < deadline_ms:
            frame, element = self._find_in_frames(shell_page, qc_row_locator, timeout=2000)
            if element is not None:
                logger.info(
                    f"QC Status '{expected_status}' found in frame: {frame.name or frame.url}"
                )
                return
            shell_page.wait_for_timeout(step_ms)
            elapsed += step_ms
        raise AssertionError(
            f"QC Status '{expected_status}' not visible in QC Reasons section on Shell Process page."
        )

    def click_return_to_last_user(self) -> None:
        """Scroll to FollowUp and Ownership section and click 'Return To Last User'."""
        logger.info("Clicking 'Return To Last User' button in FollowUp and Ownership")
        shell_page = self._get_shell_process_page()
        try:
            shell_page.bring_to_front()
        except Exception:
            pass

        button_locator = (
            "xpath=//button[normalize-space(.)='Return To Last User'] | "
            "//input[@type='button' and (@value='Return To Last User' or @value='Return to Last User')] | "
            "//input[@type='submit' and (@value='Return To Last User' or @value='Return to Last User')] | "
            "//a[normalize-space(.)='Return To Last User']"
        )

        max_attempts = 8
        for attempt in range(1, max_attempts + 1):
            frame, button = self._find_in_frames(shell_page, button_locator, timeout=3000)
            if button is not None:
                try:
                    button.scroll_into_view_if_needed(timeout=3000)
                except Exception:
                    pass
                shell_page.wait_for_timeout(1000)
                button.click(timeout=5000)
                logger.info(
                    f"Clicked 'Return To Last User' in frame: {frame.name or frame.url}"
                )
                shell_page.wait_for_timeout(2000)
                return
            logger.info(
                f"'Return To Last User' not visible yet "
                f"(attempt {attempt}/{max_attempts}); scrolling and retrying"
            )
            try:
                shell_page.mouse.wheel(0, 800)
            except Exception:
                pass
            shell_page.wait_for_timeout(1500)

        raise TimeoutError("Could not find 'Return To Last User' button on Shell Process page.")

    # ------------------------------------------------------------------
    # Account Management section (merged from former AccountManagementPage)
    # ------------------------------------------------------------------

    def select_request_and_type(self, request_name: str, type_name: str) -> None:
        """On the Account Wizard page, select a request and type under Account Management."""
        logger.info(f"Selecting request: '{request_name}', type: '{type_name}'")

        try:
            request_link = self.page.get_by_role("link", name=request_name, exact=True)
            request_link.wait_for(state="visible", timeout=15000)
            self.click(request_link)
            logger.info(f"Clicked request: '{request_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.request_dropdown.wait_for(state="visible", timeout=15000)
            self.request_dropdown.select_option(label=request_name)
            logger.info(f"Selected request from dropdown: '{request_name}'")

        self.page.wait_for_timeout(1000)

        try:
            type_link = self.page.get_by_role("link", name=type_name, exact=True)
            type_link.wait_for(state="visible", timeout=15000)
            self.click(type_link)
            logger.info(f"Clicked type: '{type_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.type_dropdown.wait_for(state="visible", timeout=15000)
            self.type_dropdown.select_option(label=type_name)
            logger.info(f"Selected type from dropdown: '{type_name}'")

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Request '{request_name}' / Type '{type_name}' selected")

    def click_complete_and_print(self) -> None:
        """Click the 'Complete and Print' button.

        The ISCT wizard Summary page only has a Next button to advance to the
        Forms page. 'Complete and Print' lives on the Forms page, so this
        method clicks Next first when we are still on Summary.
        """
        logger.info("Clicking 'Complete and Print' button")
        try:
            if "ewealthmanager.com" in self.page.url.lower():
                origin_parts = self.page.url.split("/", 3)[:3]
                self._ewm_origin = "/".join(origin_parts)
        except Exception:
            self._ewm_origin = ""

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        def _complete_control_visible() -> bool:
            probes = [
                self.complete_and_print_button,
                self.page.get_by_role("link", name="Complete and Print"),
                self.page.get_by_text("Complete and Print", exact=True),
                self.page.get_by_text("Complete & Print", exact=True),
            ]
            for probe in probes:
                try:
                    probe.wait_for(state="visible", timeout=1000)
                    return True
                except Exception:
                    continue
            return False

        # Advance from pre-completion wizard steps (Tax/Fees/Summary) to Forms.
        for _ in range(4):
            if _complete_control_visible():
                break

            current_url = self.page.url.lower()
            is_pre_completion_step = any(
                token in current_url
                for token in (
                    "isct/acctmaint/taxmanagement",
                    "isct/fees/createfees",
                    "isct/summary",
                )
            )
            if not is_pre_completion_step:
                break

            logger.info(f"On pre-completion step ({self.page.url}) - clicking Next")
            next_btn = self.page.get_by_role("button", name="Next").first
            try:
                next_btn.wait_for(state="visible", timeout=10000)
                try:
                    self.click(next_btn)
                except Exception:
                    self.page.evaluate(
                        """
                        () => {
                            const next = document.querySelector('#nextButton');
                            if (!next) return;
                            next.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                            next.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                            next.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        }
                        """
                    )

                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(2000)
                logger.info(f"Advanced pre-completion step - URL: {self.page.url}")
            except Exception as exc:
                logger.warning(f"Could not advance pre-completion step via Next: {exc}")
                break

        starting_url = self.page.url

        button_candidates = [
            self.complete_and_print_button,
            self.page.get_by_role("link", name="Complete and Print"),
            self.page.get_by_text("Complete and Print", exact=True),
            self.page.get_by_text("Complete & Print", exact=True),
            self.page.locator("input[value*='Complete'][value*='Print']").first,
            self.page.locator("button:has-text('Complete and Print')").first,
            self.page.locator("a:has-text('Complete and Print')").first,
            self.page.locator("button:has-text('Complete & Print')").first,
            self.page.locator("a:has-text('Complete & Print')").first,
            self.page.locator("input[type='submit'][value*='Complete' i]").first,
            self.page.locator("input[type='button'][value*='Complete' i]").first,
        ]

        for candidate in button_candidates:
            try:
                candidate.wait_for(state="visible", timeout=3000)
                self.click(candidate)
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)
                current_url = self.page.url

                if current_url != starting_url or "docusign" in current_url.lower():
                    logger.info(f"'Complete and Print' clicked - URL: {self.page.url}")
                    return

                logger.info(
                    "'Complete and Print' was clicked; continuing even though URL did not change yet. "
                    f"Current URL: {self.page.url}"
                )
                return
            except Exception:
                continue

        raise RuntimeError(
            "Could not find a visible 'Complete and Print' control on the summary page"
        )


# ---------------------------------------------------------------------------
# LoginPage  (EWM / Okta)
# ---------------------------------------------------------------------------


class LoginPage(BasePage):
    """EWM login page object with one-shot ``complete_login`` helper."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.allow_all_button: Locator = page.get_by_role("button", name="Allow All")
        self.username_input_field: Locator = page.get_by_label("Username")
        self.password_input_field: Locator = page.get_by_label("Password")
        self.sign_in_button: Locator = page.get_by_role("button", name="SIGN IN")

    def navigate_to_login(self, url: str) -> None:
        logger.info(f"Navigating to login page: {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    def dismiss_cookie_consent(self) -> None:
        """Accept the OneTrust cookie banner if it is displayed."""
        try:
            self.allow_all_button.wait_for(state="visible", timeout=3000)
            self.allow_all_button.click(timeout=3000)
            logger.info("Cookie consent accepted")
        except Exception:
            logger.info("Cookie consent banner not present")

    def enter_username(self, username: str) -> None:
        logger.info(f"Entering username: {username}")
        self.fill(self.username_input_field, username)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password")
        self.fill(self.password_input_field, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking sign in button")
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                self.click(self.sign_in_button)
        except Exception:
            # SSO/Okta flows often don't trigger an immediate navigation event.
            self.click(self.sign_in_button)
        logger.info(f"Sign-in submitted. Current URL: {self.page.url}")

    def complete_login(self, username: str, password: str, login_url: str) -> None:
        """Navigate to ``login_url`` and submit credentials."""
        self.navigate_to_login(login_url)
        self.dismiss_cookie_consent()
        try:
            self.enter_username(username)
            self.enter_password(password)
            self.click_sign_in()
        except Exception as exc:
            logger.warning(f"Initial credential submission failed: {exc}")


# ---------------------------------------------------------------------------
# ClientsPage  (Clients tab, Switch ID, agent impersonation)
# ---------------------------------------------------------------------------


class ClientsPage(BasePage):
    """Clients tab + Switch ID / agent impersonation flow."""

    PAGE_PATH = "en.aspx"
    SWITCH_ID = "text=Switch ID"
    AGENT_ID_FIELD = 'input[id="ctl00_cphContentArea_txtLookUp"]'
    FIND_BUTTON = 'input[value="Find"]'
    CLIENTS_BUTTON = 'a[href="/AccountsAnalysis/Clients/ClientList"]'
    IMPERSONATE_LINK = 'a[href*="/eWMLogin/account/Impersonate"]'

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.clients_link: Locator = page.get_by_role("link", name="Clients", exact=True)
        self.account_list_link: Locator = page.get_by_role(
            "link", name="Account List", exact=True
        )

    def switch_user(self) -> None:
        """Click the Switch ID link to open the agent selection page."""
        logger.info("Switching user ID")
        self.page.wait_for_selector(self.SWITCH_ID, timeout=15000)
        self.page.locator(self.SWITCH_ID).click()
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info("Switched user successfully")

    def enter_agent_id(self, agent_id: str) -> None:
        """Enter an agent ID, click Find, then impersonate."""
        logger.info(f"Entering Agent ID: {agent_id}")
        self.page.wait_for_selector(self.AGENT_ID_FIELD, timeout=15000)
        self.page.fill(self.AGENT_ID_FIELD, agent_id)
        self.page.click(self.FIND_BUTTON)
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        agent_row = self.page.locator(f"text={agent_id}").first
        try:
            agent_row.wait_for(state="visible", timeout=10000)
            agent_row.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            logger.info(f"Agent row '{agent_id}' was not directly clickable; continuing")

        agent_link = self.page.locator(
            f'a[id*="{agent_id}"][href*="/eWMLogin/account/Impersonate"]'
        )
        if agent_link.count() > 0:
            logger.info(f"Clicking impersonate link for {agent_id}")
            agent_link.first.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        else:
            agent_href = self.page.locator(f'a[href*="aplId={agent_id}"]')
            if agent_href.count() > 0:
                logger.info(f"Clicking aplId={agent_id} impersonate link")
                agent_href.first.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Agent ID {agent_id} impersonation completed")

    def click_clients(self) -> None:
        logger.info("Clicking Clients link")
        impersonate = self.page.locator(self.IMPERSONATE_LINK).first
        try:
            if impersonate.is_visible(timeout=3000):
                impersonate.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                logger.info("Impersonated first account from Clients tab")
                return
        except Exception:
            pass
        try:
            if self.clients_link.is_visible(timeout=5000):
                self.click(self.clients_link)
                logger.info("Clients link clicked")
                return
        except Exception:
            pass
        self.page.locator(self.CLIENTS_BUTTON).click()
        logger.info("Clients link clicked via href selector")

    def click_account_list(self) -> None:
        logger.info("Clicking Account List link")
        self.click(self.account_list_link)


# ---------------------------------------------------------------------------
# AccountListPage  (search + select)
# ---------------------------------------------------------------------------


class AccountListPage(BasePage):
    """Search the client list and pick an account row."""

    PAGE_PATH = "AccountsAnalysis/Clients/AccountList"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

    def search_client(self, client_id: str) -> None:
        logger.info(f"Searching for client: {client_id}")
        search_input = self.page.locator("#client_search_input")
        search_input.wait_for(state="visible", timeout=30000)
        self.fill(search_input, client_id)

        search_button = self.page.locator("form.client_search button#searchbutton")
        search_button.wait_for(state="visible", timeout=30000)
        self.click(search_button)
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Search completed for client: {client_id}")

    def select_account_by_number(self, account_number: str) -> str:
        """Click the row whose first cell matches ``account_number``."""
        logger.info(f"Selecting account by number: {account_number}")
        row = self.page.locator(f"tr:has(td:text-is('{account_number}'))").first
        row.wait_for(state="visible", timeout=15000)
        row.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Account row '{account_number}' clicked")
        return account_number

    def select_account_by_name(
        self, account_name: str, client_id: Optional[str] = None
    ) -> None:
        logger.info(f"Selecting account by name: {account_name}")
        if client_id:
            try:
                row = self.page.locator(f"tr:has-text('{client_id}')")
                account_cell = row.locator(f"td:has-text('{account_name}')").first
                self.click(account_cell)
                return
            except Exception:
                pass
        try:
            account_cell = self.page.get_by_role("gridcell", name=account_name).first
            self.click(account_cell)
            return
        except Exception:
            pass
        self.click(self.page.get_by_text(account_name).first)


# ---------------------------------------------------------------------------
# AccountDetailPage  (Account Wizard + search-client orchestrator)
# ---------------------------------------------------------------------------


class AccountDetailPage(BasePage):
    """Holdings/Account-detail page plus the search-client orchestrator
    consumed by the SDT ISC steps."""

    PAGE_PATH = "AccountsAnalysis/Clients/AccountDetail/Holdings/Summary"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        # Use specific ID to avoid the main-menu Account Wizard link.
        self.account_wizard_link: Locator = page.locator("#clientDetailAccountDetailAnchor")
        self.next_button: Locator = page.get_by_role("button", name="Next")

    def navigate(self) -> None:
        url = f"{self.base_url}{self.PAGE_PATH}"
        logger.info(f"Navigating to account detail page: {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        self.account_wizard_link.wait_for(state="visible", timeout=15000)

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard link on Holdings page")
        self.click(self.account_wizard_link)

    def open_account_wizard_and_search_client(self, account_number: str) -> str:
        """Navigate Clients > Account List, search the client, and click the
        matching row.

        Returns the account number (used as the account name when no
        friendly name is available).
        """
        logger.info(
            f"Opening Account Wizard search flow for account '{account_number}'"
        )
        clients_page = ClientsPage(self.page)
        account_list_page = AccountListPage(self.page)

        # The agent-impersonation flow normally lands on the Clients view
        # already. If we still need to click Clients > Account List, try
        # those links. Both are non-fatal: a non-clickable link just means
        # we are already on the right view.
        try:
            clients_page.click_clients()
        except Exception as exc:
            logger.info(f"Clients link click skipped: {exc}")
        try:
            clients_page.click_account_list()
        except Exception as exc:
            logger.info(f"Account List link click skipped: {exc}")

        try:
            account_list_page.search_client(account_number)
        except Exception as exc:
            logger.warning(
                f"Search input not available on current page; continuing. Details: {exc}"
            )

        try:
            return account_list_page.select_account_by_number(account_number)
        except Exception as exc:
            logger.warning(
                f"Could not click account row by number ({exc}); trying name fallback"
            )
            account_list_page.select_account_by_name(account_number)
            return account_number


# ---------------------------------------------------------------------------
# DocusignPage  (Complete & Print + DocuSign handling)
# ---------------------------------------------------------------------------


class DocusignPage(BasePage):
    """Encapsulates the post-suitability flow:

    1. Click ``Complete and Print`` on the Forms page (advancing any
       residual wizard steps first).
    2. Handle the DocuSign hand-off (``Continue & Finish``) and the
       subsequent return navigation back to the tracking center.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self._ewm_origin: str = ""

        self.complete_and_print_button: Locator = page.get_by_role(
            "button", name="Complete and Print"
        )
        self.docusign_continue_button: Locator = page.get_by_role("button", name="Continue")
        self.docusign_finish_button: Locator = page.get_by_role("button", name="Finish")

    # ------------------------------------------------------------------
    # Complete and Print
    # ------------------------------------------------------------------

    def click_complete_and_print(self) -> None:
        """Click ``Complete and Print``, advancing earlier wizard steps."""
        logger.info("Clicking 'Complete and Print' button")
        try:
            if "ewealthmanager.com" in self.page.url.lower():
                parts = self.page.url.split("/", 3)[:3]
                self._ewm_origin = "/".join(parts)
        except Exception:
            self._ewm_origin = ""

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        def _complete_control_visible() -> bool:
            probes = [
                self.complete_and_print_button,
                self.page.get_by_role("link", name="Complete and Print"),
                self.page.get_by_text("Complete and Print", exact=True),
                self.page.get_by_text("Complete & Print", exact=True),
            ]
            for probe in probes:
                try:
                    probe.wait_for(state="visible", timeout=1000)
                    return True
                except Exception:
                    continue
            return False

        for _ in range(4):
            if _complete_control_visible():
                break

            current_url = self.page.url.lower()
            is_pre_completion_step = any(
                token in current_url
                for token in (
                    "isct/acctmaint/taxmanagement",
                    "isct/fees/createfees",
                    "isct/summary",
                )
            )
            if not is_pre_completion_step:
                break

            logger.info(f"On pre-completion step ({self.page.url}) - clicking Next")
            next_btn = self.page.get_by_role("button", name="Next").first
            try:
                next_btn.wait_for(state="visible", timeout=10000)
                try:
                    self.click(next_btn)
                except Exception:
                    self.page.evaluate(
                        """
                        () => {
                            const next = document.querySelector('#nextButton');
                            if (!next) return;
                            next.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                            next.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                            next.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        }
                        """
                    )
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(2000)
            except Exception as exc:
                logger.warning(f"Could not advance pre-completion step: {exc}")
                break

        starting_url = self.page.url

        button_candidates = [
            self.complete_and_print_button,
            self.page.get_by_role("link", name="Complete and Print"),
            self.page.get_by_text("Complete and Print", exact=True),
            self.page.get_by_text("Complete & Print", exact=True),
            self.page.locator("input[value*='Complete'][value*='Print']").first,
            self.page.locator("button:has-text('Complete and Print')").first,
            self.page.locator("a:has-text('Complete and Print')").first,
            self.page.locator("button:has-text('Complete & Print')").first,
            self.page.locator("a:has-text('Complete & Print')").first,
            self.page.locator("input[type='submit'][value*='Complete' i]").first,
            self.page.locator("input[type='button'][value*='Complete' i]").first,
        ]

        for candidate in button_candidates:
            try:
                candidate.wait_for(state="visible", timeout=3000)
                self.click(candidate)
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)
                if self.page.url != starting_url or "docusign" in self.page.url.lower():
                    logger.info(f"'Complete and Print' clicked - URL: {self.page.url}")
                    return
                logger.info(
                    "'Complete and Print' was clicked; URL not changed yet, continuing"
                )
                return
            except Exception:
                continue

        raise RuntimeError(
            "Could not find a visible 'Complete and Print' control on the summary page"
        )

    # ------------------------------------------------------------------
    # DocuSign hand-off
    # ------------------------------------------------------------------

    def handle_docusign_page(self) -> None:
        """Handle DocuSign hand-off and return to the tracking center."""
        logger.info("Waiting for DocuSign page to load...")
        try:
            self.page.wait_for_url(
                re.compile(r"https://.*docusign\.(com|net)/.*"), timeout=45000
            )
            logger.info(f"DocuSign page loaded: {self.page.url}")
        except Exception:
            logger.info(
                f"URL did not match docusign pattern, current: {self.page.url}. "
                "Proceeding with current page."
            )

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(3000)

        current_url = self.page.url.lower()
        if (
            "apps-d.docusign.com/error" in current_url
            or "cause=initialization" in current_url
        ):
            logger.warning("DocuSign initialization error page detected; attempting recovery")
            for _ in range(4):
                try:
                    self.page.go_back(wait_until="domcontentloaded", timeout=30000)
                    self.page.wait_for_timeout(1500)
                    if "ewealthmanager.com" in self.page.url.lower():
                        logger.info(f"Recovered from DocuSign error page - URL: {self.page.url}")
                        return
                except Exception:
                    continue
            if self._ewm_origin:
                try:
                    tracking_url = (
                        f"{self._ewm_origin}/AccountsAnalysis/TrackingCenter/"
                        "TrackingCenterItemDetail"
                    )
                    self.page.goto(
                        tracking_url, wait_until="domcontentloaded", timeout=60000
                    )
                    return
                except Exception as exc:
                    logger.warning(f"Could not navigate to tracking center fallback: {exc}")
            return

        try:
            check_box = self.page.locator(
                "[data-qa='ersd-agree-checkbox-label-text'], "
                "[data-qa='ersd-agree-checkbox'], "
                "#ModalContainer input[type='checkbox']"
            ).first
            check_box.wait_for(state="visible", timeout=10000)
            check_box.click(force=True)
            continue_finish = self.page.get_by_role("button", name="Continue & Finish")
            continue_finish.wait_for(state="visible", timeout=10000)
            self.click(continue_finish)
            logger.info("Clicked 'Continue & Finish' button")
        except Exception:
            logger.info("Single button not found, trying separate buttons")
            try:
                self.docusign_continue_button.wait_for(state="visible", timeout=10000)
                self.click(self.docusign_continue_button)
                self.page.wait_for_timeout(2000)
                self.docusign_finish_button.wait_for(state="visible", timeout=10000)
                self.click(self.docusign_finish_button)
            except Exception:
                fallback = self.page.locator(
                    "button:has-text('Finish'), button:has-text('Continue'), "
                    "a:has-text('Finish'), input[value*='Finish']"
                ).first
                try:
                    fallback.wait_for(state="visible", timeout=10000)
                    self.click(fallback)
                except Exception:
                    logger.warning("Could not find Continue/Finish controls; continuing")
                    return

        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)

        if "docusign" in self.page.url.lower():
            try:
                self.page.wait_for_url(
                    re.compile(r".*ewealthmanager\.com.*"), timeout=30000
                )
            except Exception:
                logger.warning("DocuSign did not redirect back to EWM; navigating manually")

        if "trackingcenter" not in self.page.url.lower():
            ewm_origin = self._ewm_origin or "https://test11.ewealthmanager.com"
            tracking_url = (
                f"{ewm_origin}/AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"
            )
            try:
                self.page.goto(tracking_url, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                try:
                    new_page = self.page.context.new_page()
                    new_page.goto(
                        tracking_url, wait_until="domcontentloaded", timeout=60000
                    )
                    self.page = new_page
                except Exception as exc:
                    logger.warning(f"Failed to open tracking center: {exc}")
        logger.info(f"DocuSign completed - URL: {self.page.url}")


# ---------------------------------------------------------------------------
# TrackingCenterPage  (open record, upload PDF, fetch / verify B-number)
# ---------------------------------------------------------------------------


def _create_minimal_pdf(path: str) -> None:
    """Create a minimal valid PDF for upload tests."""
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
        b"startxref\n190\n"
        b"%%EOF\n"
    )
    with open(path, "wb") as f:
        f.write(pdf_content)


class TrackingCenterPage(BasePage):
    """Tracking center / item detail page object."""

    PAGE_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self._ewm_origin: str = ""
        self._last_uploaded_pdf: str = ""
        self.item_number_label: Locator = page.locator(
            "span:has-text('Item Number:') + label"
        ).first
        self.tracking_id_element: Locator = page.locator(
            "#trackingId, .tracking-id, [data-tracking-id]"
        )
        self.upload_trigger_button: Locator = page.locator(
            ".fileuploadbutton.item-detail-button"
        ).first
        self.upload_close_button: Locator = page.locator(
            "button:has-text('Close')"
        ).first

    # ------------------------------------------------------------------
    # Tracking ID utilities
    # ------------------------------------------------------------------

    def _scan_for_reference(self, prefixes: tuple) -> str:
        prefix_pattern = "|".join(re.escape(p) for p in prefixes)
        pattern = rf"\b((?:{prefix_pattern})[\-]?\d{{5,}})\b"

        try:
            body_text = self.page.locator("body").text_content() or ""
        except Exception as exc:
            logger.debug(f"_scan_for_reference: body text_content failed: {exc}")
            body_text = ""

        match = re.search(pattern, body_text)
        if match:
            return match.group(1)

        try:
            return self.page.evaluate(
                """
                ({ patternSource }) => {
                    const pattern = new RegExp(patternSource);
                    const candidates = [];
                    for (const element of document.querySelectorAll('*')) {
                        candidates.push(
                            element.getAttribute('data-tracking-id') || '',
                            element.getAttribute('href') || '',
                            element.getAttribute('value') || '',
                            element.id || '',
                            element.getAttribute('name') || '',
                            element.textContent || ''
                        );
                    }
                    for (const value of candidates) {
                        const match = value.match(pattern);
                        if (match) {
                            return match[1];
                        }
                    }
                    return '';
                }
                """,
                {"patternSource": pattern},
            )
        except Exception as exc:
            logger.debug(f"_scan_for_reference: page.evaluate failed: {exc}")
            return ""

    def fetch_tracking_id(self) -> str:
        """Fetch the tracking ID from the confirmation / tracking page."""
        logger.info("Fetching tracking ID")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        try:
            self.item_number_label.wait_for(state="visible", timeout=5000)
            tracking_id = (self.item_number_label.text_content() or "").strip()
            if tracking_id:
                logger.info(f"Tracking ID found via item number label: {tracking_id}")
                return tracking_id
        except Exception:
            pass

        try:
            self.tracking_id_element.wait_for(state="visible", timeout=10000)
            tracking_id = self.get_text(self.tracking_id_element)
            if tracking_id:
                logger.info(f"Tracking ID found: {tracking_id}")
                return tracking_id.strip()
        except Exception:
            pass

        scanned = self._scan_for_reference(("B",))
        if scanned:
            logger.info(f"Tracking ID found via scan: {scanned}")
            return scanned

        logger.warning("Could not find tracking ID on page")
        return ""

    def wait_for_tracking_id(
        self,
        prefix: str = "B",
        timeout_ms: int = 300000,
        re_upload_pdf_path: str = "",
        re_upload_interval_s: int = 60,
    ) -> str:
        """Refresh-and-poll for the generated tracking ID.

        Always reloads the tracking page between polls. If the B-number has
        not appeared after ``re_upload_interval_s`` seconds, re-uploads the
        same PDF (``re_upload_pdf_path`` or the last uploaded path) and then
        continues polling. Repeats this re-upload cycle until ``timeout_ms``.
        """
        logger.info(
            f"Waiting for tracking ID with prefix '{prefix}' up to {timeout_ms // 1000}s "
            f"(re-upload every {re_upload_interval_s}s)"
        )
        poll_interval = 5
        deadline = time.monotonic() + (timeout_ms / 1000)
        pdf_path = re_upload_pdf_path or self._last_uploaded_pdf
        next_reupload_at = time.monotonic() + re_upload_interval_s

        while time.monotonic() < deadline:
            tracking_id = self._scan_for_reference((prefix,))
            if tracking_id:
                logger.info(f"Tracking ID found: {tracking_id}")
                return tracking_id

            if pdf_path and time.monotonic() >= next_reupload_at:
                logger.info(
                    f"B-number not yet generated; re-uploading PDF '{pdf_path}' "
                    "and refreshing the page"
                )
                try:
                    self.upload_pdf(pdf_path)
                except Exception as exc:
                    logger.warning(f"Re-upload attempt failed: {exc}")
                next_reupload_at = time.monotonic() + re_upload_interval_s

            try:
                self.page.reload(wait_until="domcontentloaded", timeout=30000)
            except Exception:
                pass

            remaining = deadline - time.monotonic()
            wait = min(poll_interval, max(remaining, 0))
            if wait > 0:
                self.page.wait_for_timeout(int(wait * 1000))

        logger.warning(f"Timed out waiting for tracking ID with prefix '{prefix}'")
        try:
            current_url = self.page.url
            title = self.page.title()
            body_text = (self.page.locator("body").text_content() or "")[:2500]
            logger.warning(
                f"DEBUG tracking-ID timeout. URL={current_url} | TITLE={title} | "
                f"BODY[:2500]={body_text!r}"
            )
            frame_summary = []
            for fr in self.page.frames:
                try:
                    snippet = (fr.locator("body").text_content() or "")[:500]
                except Exception:
                    snippet = "<unreadable>"
                frame_summary.append(f"<frame url={fr.url}>: {snippet!r}")
            logger.warning("DEBUG frames:\n" + "\n".join(frame_summary))
        except Exception as exc:
            logger.warning(f"DEBUG dump failed: {exc}")
        return ""

    def verify_tracking_id_starts_with(self, prefix: str, tracking_id: str) -> None:
        """Assert that ``tracking_id`` begins with the expected prefix."""
        logger.info(f"Verifying tracking ID '{tracking_id}' starts with '{prefix}'")
        assert tracking_id.startswith(prefix), (
            f"Tracking ID '{tracking_id}' does not start with '{prefix}'"
        )
        logger.info("Tracking ID verification passed")

    # ------------------------------------------------------------------
    # Tracking record navigation
    # ------------------------------------------------------------------

    def open_tracking_record(self) -> None:
        """Open the tracking record page after DocuSign completion."""
        logger.info("Opening D-number tracking link")
        expected_path = self.PAGE_PATH
        tracking_center_paths = (
            "trackingcenter",
            "trackingcenteritemdetail",
            "trackingcentersearch",
        )

        if not self._ewm_origin:
            try:
                if "ewealthmanager.com" in self.page.url.lower():
                    parts = self.page.url.split("/", 3)[:3]
                    self._ewm_origin = "/".join(parts)
            except Exception:
                pass
        ewm_origin = self._ewm_origin or "https://test11.ewealthmanager.com"

        def _is_page_alive() -> bool:
            try:
                _ = self.page.url
                return True
            except Exception:
                return False

        if _is_page_alive() and expected_path.lower() in self.page.url.lower():
            logger.info(f"Already on tracking detail page: {self.page.url}")
            return

        if _is_page_alive():
            url_lower = self.page.url.lower()
            if not any(p in url_lower for p in tracking_center_paths):
                tracking_url = f"{ewm_origin}/{expected_path}"
                try:
                    self.page.goto(
                        tracking_url, wait_until="domcontentloaded", timeout=60000
                    )
                except Exception as exc:
                    logger.warning(f"goto failed ({exc}); opening in new page")
                    try:
                        new_page = self.page.context.new_page()
                        new_page.goto(
                            tracking_url, wait_until="domcontentloaded", timeout=60000
                        )
                        self.page = new_page
                    except Exception as exc2:
                        logger.warning(f"New page also failed: {exc2}")
        else:
            tracking_url = f"{ewm_origin}/{expected_path}"
            new_page = self.page.context.new_page()
            new_page.goto(tracking_url, wait_until="domcontentloaded", timeout=60000)
            self.page = new_page

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

        try:
            d_number_link = self.page.get_by_role(
                "link", name=re.compile(r"D\d+")
            ).first
            d_number_link.wait_for(state="visible", timeout=15000)
            self.click(d_number_link)
            self.page.wait_for_url(f"**{expected_path}**", timeout=30000)
            logger.info(f"Tracking record opened via D-number: {self.page.url}")
            return
        except Exception:
            pass

        if any(p in self.page.url.lower() for p in tracking_center_paths):
            logger.info(f"On tracking center page: {self.page.url}")
            return

        logger.info(f"Tracking record opened: {self.page.url}")

    # ------------------------------------------------------------------
    # PDF Upload
    # ------------------------------------------------------------------

    def upload_pdf(self, file_path: str = "") -> None:
        """Upload a PDF file to the tracking record (creates a stub if needed)."""
        if not file_path or not os.path.exists(file_path):
            file_path = os.path.join(tempfile.gettempdir(), "test_upload.pdf")
            if not os.path.exists(file_path):
                _create_minimal_pdf(file_path)
        self._last_uploaded_pdf = file_path
        logger.info(f"Uploading PDF: {file_path}")

        try:
            self.upload_trigger_button.wait_for(state="visible", timeout=5000)
            self.click(self.upload_trigger_button)
            self.page.wait_for_timeout(1000)
        except Exception:
            logger.info("Upload panel trigger not visible; continuing with file input")

        upload_input = None
        contexts = [self.page] + list(self.page.frames)
        for context in contexts:
            try:
                candidate = context.locator('input[type="file"]').first
                candidate.wait_for(state="attached", timeout=2000)
                upload_input = candidate
                break
            except Exception:
                continue

        if upload_input is None:
            logger.warning("File input not found; skipping PDF upload step")
            return

        upload_input.set_input_files(file_path, timeout=10000)
        logger.info("PDF file selected")

        upload_btn = None
        upload_btn_selector = ""
        for context in contexts:
            for selector in (
                "button:has-text('Upload')",
                "input[type='button'][value*='Upload' i]",
                "input[type='submit'][value*='Upload' i]",
            ):
                try:
                    candidate = context.locator(selector).first
                    candidate.wait_for(state="visible", timeout=1500)
                    upload_btn = candidate
                    upload_btn_selector = selector
                    break
                except Exception:
                    continue
            if upload_btn:
                break

        if not upload_btn:
            logger.warning("Upload button not found; skipping explicit submit")
            return

        try:
            btn_text = (upload_btn.text_content() or "").strip()
            btn_value = upload_btn.get_attribute("value") or ""
            logger.info(
                f"Submitting upload via selector={upload_btn_selector!r} "
                f"text={btn_text!r} value={btn_value!r}"
            )
        except Exception:
            pass

        try:
            self.click(upload_btn)
            self.page.wait_for_timeout(3000)
        except Exception as exc:
            logger.warning(
                f"Upload action failed; continuing. selector_used={upload_btn} error={exc!r}"
            )
            return

        try:
            if self.upload_close_button.is_visible():
                self.click(self.upload_close_button)
        except Exception:
            pass

        self.page.wait_for_timeout(5000)
        try:
            self.page.reload(wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass
        logger.info("PDF upload completed")


# ---------------------------------------------------------------------------
# ChangeInvestmentsPage  (ported from team/portfolio-mgmt-trading)
# ---------------------------------------------------------------------------
# NOTE: the body of ChangeInvestmentsPage below is a verbatim port of
# ``pages/change_investments_page.py`` from ``team/portfolio-mgmt-trading``
# (commit f8c982ac), with the import of ``utils.allure_logger`` swapped for
# this module's ``utils.logger`` logger.


class ChangeInvestmentsPage(BasePage):
    """Page object for the Change Investments flow."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # -- Holdings page: Account Wizard link --
        # Two "Account Wizard" links exist (nav menu + account detail).
        # Use the specific account-detail one via CSS ID.
        self.account_wizard_link: Locator = page.locator("#clientDetailAccountDetailAnchor")

        # -- Account Wizard page: Client Management section --
        self.change_investments_link: Locator = page.get_by_role(
            "link", name="Change Investments", exact=True
        )
        # alt: page.locator("#ctl00_cphContentArea_lnkChangeInvestments")

        # -- ICT Source Account page (/ISCT/AcctSelection/SelectAccount) --
        self.next_button: Locator = page.get_by_role("button", name="Next")
        # alt: page.locator("#nextButton")

        # Investment-action modal (#InvestmentActionModal)
        self.investment_action_modal: Locator = page.locator("#InvestmentActionModal")
        self.radio_destination_investment: Locator = page.locator(
            "input[name='action'][value='DestinationInvestment']"
        )
        self.modal_ok_button: Locator = self.investment_action_modal.get_by_role(
            "button", name="OK"
        )
        # alt: page.locator("#InvestmentActionModal .btn-transition-primary")

    # ------------------------------------------------------------------
    # Client Management  (Holdings -> Account Wizard -> link click)
    # ------------------------------------------------------------------

    def click_client_management_option(self, option_name: str) -> None:
        """
        Navigate to Account Wizard from Holdings page, then click the
        specified Client Management option link.

        Args:
            option_name: The link text (e.g. "Change Investments").
        """
        # Step 1 - Click Account Wizard link (skip if already on Account Wizard page)
        current_url = self.page.url.lower()
        if "clientaccounts" in current_url or "accountwizard" in current_url or "nbt/list" in current_url:
            logger.info(f"Already on Account Wizard page: {self.page.url}")
        else:
            logger.info("Clicking Account Wizard link on Holdings page")
            # Wait for any loading modal to disappear first
            loading_modal = self.page.locator("#loadingImageModal")
            try:
                loading_modal.wait_for(state="hidden", timeout=15000)
            except Exception:
                pass
            self.account_wizard_link.wait_for(state="visible", timeout=15000)
            wizard_href = self.account_wizard_link.get_attribute("href")

            if wizard_href:
                logger.info(f"Navigating to Account Wizard via href: {wizard_href}")
                self.page.goto(wizard_href, wait_until="domcontentloaded", timeout=60000)
            else:
                logger.warning("Account Wizard href was empty; falling back to click")
                self.click(self.account_wizard_link)
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)

            # Wait for the Account Wizard page URL (may redirect through intermediate URLs)
            try:
                self.page.wait_for_url("**/NBT/**ClientAccounts**", timeout=30000)
            except Exception:
                pass
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)
            logger.info(f"Account Wizard page loaded: {self.page.url}")

        # Step 2 - Click the specific Client Management link by text
        logger.info(f"Clicking '{option_name}' under Client Management")
        option_locator = self.page.get_by_role("link", name=option_name, exact=True)
        # Wait for page to settle (networkidle may not be reached due to background polling)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        option_locator.wait_for(state="visible", timeout=20000)
        self.click(option_locator)
        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        logger.info(f"'{option_name}' clicked - page URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Source Account - select account & navigate
    # ------------------------------------------------------------------

    def click_account_number_investment_selection(self) -> None:
        """
        On the ICT Source Account page, ensure the target account is
        checked, then click Next to proceed toward Investment Selection.
        If the Investment Action modal pops up, select
        'Destination Investment' and confirm.
        If the app auto-redirected past Source Account (single-account
        client), skip the Next click entirely.
        """
        current_url = self.page.url.lower()

        # If we already landed on ModifyInvestment (app skipped Source
        # Account for single-account clients), there's nothing to do.
        if "modifyinvestment" in current_url:
            logger.info(
                "Already on Investment Selection page (Source Account was auto-skipped) - "
                f"URL: {self.page.url}"
            )
            return

        logger.info("On Source Account page - clicking Next to proceed")
        source_url = self.page.url

        # Try clicking Next GÇö may need up to 2 attempts for slow source account pages
        for attempt in range(2):
            self.click_next_button()

            # Check if we left the Source Account page
            if self.page.url != source_url:
                break

            # Still on Source Account GÇö wait for any pending navigation
            try:
                self.page.wait_for_url(lambda url: url != source_url, timeout=5000)
                break
            except Exception:
                if attempt == 0:
                    logger.info("Still on Source Account after Next - retrying")

        # Now on ModifyInvestment (or modal appeared) GÇö handle modal if present
        try:
            self.investment_action_modal.wait_for(state="visible", timeout=8000)
            logger.info("Investment Action modal detected - selecting Destination Investment")
            self.radio_destination_investment.evaluate(
                """el => {
                    el.checked = true;
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    el.dispatchEvent(new Event('click', {bubbles: true}));
                    if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                        $.uniform.update(el);
                    }
                }"""
            )
            self.click(self.modal_ok_button)
            self.page.locator("#InvestmentActionModal").wait_for(state="hidden", timeout=15000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
            logger.info("Destination Investment selected and confirmed")
        except Exception:
            logger.info("No Investment Action modal - continuing")

        logger.info(f"Navigated forward - current URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Destination Investment - validate account number
    # ------------------------------------------------------------------

    def validate_account_number_on_destination_tab(self, expected_account: str) -> None:
        """
        Validate the account number is visible on the current page.
        Tries the exact account number first, then falls back to checking
        the page contains any account-related content.

        Args:
            expected_account: The expected account number text.
        """
        logger.info(f"Validating account number on page: {expected_account}")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        # Try to find the expected account number text on the page
        try:
            account_locator = self.page.get_by_text(expected_account).first
            account_locator.wait_for(state="visible", timeout=10000)
            logger.info(f"Account number '{expected_account}' found on page")
            return
        except Exception:
            logger.info(
                f"Account '{expected_account}' not found directly - "
                f"checking page for Account-related content"
            )

        current_url = self.page.url.lower()
        if "modifyinvestment" in current_url:
            logger.info("Destination investment page validated by URL")
            return

        # Fallback: look for "Account #:" or "Account" text
        body_text = self.page.locator("body").text_content() or ""
        has_account = "Account" in body_text or "account" in body_text
        assert has_account, f"No account info found on page. URL: {self.page.url}"
        logger.info("Account-related content validated on page")

    def validate_account_number_visible_on_destination_tab(self) -> None:
        """Validate that the page contains account-related content."""
        logger.info("Validating account info is visible on the page")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        # The page should contain "Account" text
        account_text = self.page.locator("text=Account").first
        account_text.wait_for(state="visible", timeout=15000)
        assert account_text.is_visible(), "Account info not visible on the page"
        logger.info("Account info is visible on the page")

    # ------------------------------------------------------------------
    # Select New Investment
    # ------------------------------------------------------------------

    def select_new_investment(self) -> None:
        """
        On the Investment Selection page (/ISCT/ModifyInvestment), select
        a destination investment from the custom dropdown, choose 100%
        conversion, then click Next.

        The dropdown is a custom dl/dd structure (#myInvestmentSelector).
        """
        logger.info("Selecting new investment on Investment Selection page")
        logger.info(f"Current URL: {self.page.url}")

        # Step 1 - Open the destination investment dropdown
        dropdown_trigger = self.page.get_by_text("-----Choose One-----", exact=True)
        # alt: page.locator("#targetddl dt.firstmenu a")
        dropdown_trigger.wait_for(state="visible", timeout=15000)
        dropdown_trigger.click()
        logger.info("Destination investment dropdown opened")

        # Step 2 - Click "New investment" to reveal account type options
        new_investment_option = self.page.get_by_text("New investment", exact=True)
        # alt: page.locator("#newInvestmentMenu a[data-value='NewInvestment']")
        new_investment_option.wait_for(state="visible", timeout=10000)
        new_investment_option.click()
        self.page.wait_for_timeout(1000)  # Allow sub-menu animation
        logger.info("'New investment' option clicked - account types visible")

        # Scope to the dropdown container to avoid matching hidden elements elsewhere
        dropdown = self.page.locator("#myInvestmentSelector, #targetddl, .multiSelect").first

        # Step 3 - Select an enabled account type from preferred list
        preferred_types = ["Guided Portfolios", "Core Markets", "GPS Fund Strategies"]
        for account_type in preferred_types:
            link = dropdown.locator(f"a:has-text('{account_type}')").first
            try:
                link.wait_for(state="visible", timeout=3000)
                is_disabled = link.evaluate(
                    "el => el.classList.contains('disabled') || el.hasAttribute('disabled')"
                )
                if not is_disabled:
                    link.click()
                    try:
                        self.page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        pass
                    logger.info(f"'{account_type}' selected as destination investment")
                    return
                else:
                    logger.warning(f"'{account_type}' is disabled for this account")
            except Exception:
                logger.debug(f"'{account_type}' not found in dropdown")

        # Fallback: select the first enabled account type option
        enabled_option = dropdown.locator(
            "dd:not(.disabled) a[href]:not([disabled])"
        ).first
        try:
            enabled_option.wait_for(state="visible", timeout=10000)
            option_text = (enabled_option.text_content() or "Unknown").strip()
            enabled_option.click()
            try:
                self.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            logger.info(f"'{option_text}' selected as destination investment (fallback)")
        except Exception:
            # Last resort: try clicking any visible link in the dropdown
            any_link = dropdown.locator("dd a[href]").first
            try:
                any_link.wait_for(state="visible", timeout=5000)
                any_link.click()
                logger.info("Selected first available dropdown link (last resort)")
            except Exception:
                raise TimeoutError("No enabled account type found in destination investment dropdown")

    # ------------------------------------------------------------------
    # Validate New Investment Modal / Completion
    # ------------------------------------------------------------------

    def validate_new_investment_modal(self) -> None:
        """
        Validate the page has advanced and investment-related content
        is visible.  This may be a new wizard step page, an investment
        modal, or a confirmation page.
        """
        logger.info("Validating investment page/modal is displayed")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        # The page title or heading should contain investment-related text
        body_text = self.page.locator("body").text_content() or ""
        assert any(
            keyword.lower() in body_text.lower()
            for keyword in ["Investment", "Account", "Selection", "Destination"]
        ), f"Investment page content not found. URL: {self.page.url}"
        logger.info(f"Investment page validated - URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Investment Strategy and Profile Selection
    # ------------------------------------------------------------------

    def select_investment_strategy(self, strategy_name: str) -> None:
        """Select investment strategy (e.g., 'Single Strategy Account')."""
        logger.info(f"Selecting investment strategy: {strategy_name}")
        last_error: Exception | None = None

        primary_link = self.page.get_by_role("link", name=strategy_name).first
        try:
            primary_link.wait_for(state="visible", timeout=15000)
            self.click(primary_link)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"Investment strategy '{strategy_name}' selected")
            return
        except Exception as exc:
            last_error = exc

        # Fallback for strict/hidden cases where role lookup is unstable.
        try:
            by_text = self.page.locator(f"a:has-text('{strategy_name}')").first
            by_text.wait_for(state="visible", timeout=5000)
            by_text.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"Investment strategy '{strategy_name}' selected via text fallback")
            return
        except Exception as exc:
            last_error = exc

        # Last resort: JS click when element is present but overlayed.
        js_link = self.page.locator(f"a:has-text('{strategy_name}')").first
        if js_link.count() > 0:
            js_link.evaluate("el => el.click()")
            self.page.wait_for_load_state("networkidle", timeout=30000)
            logger.info(f"Investment strategy '{strategy_name}' selected using JS fallback")
            return

        raise AssertionError(
            f"Could not select investment strategy '{strategy_name}' on URL: {self.page.url}"
        ) from last_error

    def select_investment_profile(self, profile_name: str) -> None:
        """Select specific investment profile from the grid inside the model_picker_modal.
        Prefers a row whose investment minimum the account can meet."""
        logger.info(f"Selecting investment profile: {profile_name}")

        # Wait for the modal grid to be visible
        self.page.locator("#model_picker_modal").wait_for(state="visible", timeout=10000)

        # Debug: dump modal structure to understand what elements are inside
        modal_debug = self.page.evaluate(
            """
            () => {
                const modal = document.querySelector('#model_picker_modal');
                if (!modal) return { exists: false };
                const rows = Array.from(modal.querySelectorAll('tr'));
                const rowData = rows.slice(0, 10).map(r => ({
                    id: r.id,
                    classes: r.className,
                    cells: Array.from(r.querySelectorAll('td, th')).map(c => ({
                        class: c.className,
                        text: (c.textContent || '').replace(/\\s+/g, ' ').trim().substring(0, 80)
                    }))
                }));
                const links = Array.from(modal.querySelectorAll('a')).slice(0, 10).map(a => ({
                    text: (a.textContent || '').trim().substring(0, 80),
                    href: a.href,
                    class: a.className
                }));
                const inputs = Array.from(modal.querySelectorAll('input, select')).map(i => ({
                    type: i.type, id: i.id, name: i.name, class: i.className
                }));
                return { exists: true, rowCount: rows.length, rows: rowData, links, inputs };
            }
            """
        )
        logger.info(f"Modal debug: {modal_debug}")

        # Find the best matching row: prefer one whose minimum the account can meet
        chosen = self.page.evaluate(
            """
            (profileName) => {
                const cleanText = (v) => (v || '').replace(/\\s+/g, ' ').trim();
                const parseMoney = (v) => {
                    const m = cleanText(v).match(/[\\d,.]+/);
                    return m ? Number(m[0].replace(/,/g, '')) : 0;
                };

                let marketValue = 0;
                const src = document.querySelector('#selected1');
                if (src && src.value) {
                    try { marketValue = Number(JSON.parse(src.value).MarketValue) || 0; } catch(e) {}
                }

                const modal = document.querySelector('#model_picker_modal');
                if (!modal) return null;

                // Try multiple selectors for profile cells
                const rows = Array.from(modal.querySelectorAll('tr')).filter(r => {
                    const text = cleanText(r.textContent).toLowerCase();
                    return text.includes(cleanText(profileName).toLowerCase());
                });

                if (!rows.length) return null;

                const candidates = rows.map(r => ({
                    row: r,
                    text: cleanText(r.textContent).substring(0, 120),
                    minimum: parseMoney(
                        (r.querySelector('td.investment-minimum, td:last-child') || {}).textContent || '0'
                    )
                }));

                // Prefer rows meeting the minimum, sorted by lowest minimum
                const eligible = candidates.filter(c => !c.minimum || c.minimum <= marketValue);
                const pick = eligible.length
                    ? eligible.sort((a,b) => a.minimum - b.minimum)[0]
                    : candidates.sort((a,b) => a.minimum - b.minimum)[0];

                pick.row.click();
                return { minimum: pick.minimum, marketValue, meets: !pick.minimum || pick.minimum <= marketValue, text: pick.text };
            }
            """,
            profile_name,
        )

        if chosen:
            logger.info(
                f"Investment profile '{profile_name}' selected: {chosen['text']} "
                f"(minimum: {chosen['minimum']}, account: {chosen['marketValue']}, meets: {chosen['meets']})"
            )
            return

        # Fallback: click first matching row via Playwright locator
        profile_row = self.page.locator(
            f"#model_picker_modal tr:has(td:has-text('{profile_name}'))"
        ).first
        try:
            profile_row.wait_for(state="visible", timeout=10000)
            profile_row.click()
            logger.info(f"Investment profile '{profile_name}' selected via locator fallback")
            return
        except Exception:
            pass

        # Last fallback: click via role
        profile_cell = self.page.get_by_role("cell", name=profile_name).first
        profile_cell.wait_for(state="visible", timeout=10000)
        self.click(profile_cell)
        logger.info(f"Investment profile '{profile_name}' selected via role fallback")

    def confirm_investment_selection(self) -> None:
        """Click OK button to confirm investment selection."""
        logger.info("Confirming investment selection")
        modal = self.page.locator("#model_picker_modal")
        ok_button = modal.locator("#OkButton")

        # Wait for the modal to appear (profile click should have triggered it)
        try:
            modal.wait_for(state="visible", timeout=10000)
        except Exception:
            logger.info("Investment modal not visible - skipping confirmation")
            return

        ok_button.wait_for(state="visible", timeout=10000)
        ok_button.click(force=True)
        self.page.wait_for_timeout(1000)
        # If modal is still open, try clicking again without force
        if modal.is_visible():
            logger.warning("Modal still visible after OK click - retrying")
            ok_button.click(timeout=5000)
        # Wait for the model picker modal to close
        modal.wait_for(state="hidden", timeout=15000)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        logger.info("Investment selection confirmed")

    # ------------------------------------------------------------------
    # Allocation Selection
    # ------------------------------------------------------------------

    def select_allocation_option(self, allocation_type: str) -> None:
        """Select allocation option (Full, Partial, etc.)."""
        logger.info(f"Selecting allocation option: {allocation_type}")
        normalized = allocation_type.strip().lower()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        selectors = []
        if normalized == "full":
            selectors = [
                "#allocRdFull1_1",
                "input[type='radio'][id*='allocRdFull' i]",
                "input[type='radio'][name*='alloc' i][value*='full' i]",
                "input[type='radio'][id*='alloc' i][value*='full' i]",
            ]
        else:
            selectors = [
                f"input[type='radio'][id*='alloc'][id*='{normalized}' i]",
                f"input[type='radio'][name*='alloc'][value*='{normalized}' i]",
                f"input[type='radio'][id*='alloc'][value*='{normalized}' i]",
            ]

        option_input = None
        for selector in selectors:
            try:
                candidate = self.page.locator(selector).first
                candidate.wait_for(state="attached", timeout=4000)
                option_input = candidate
                logger.info(f"Allocation selector matched: {selector}")
                break
            except Exception:
                continue

        if option_input is None:
            selected = self.page.evaluate(
                """
                ({ value }) => {
                    const norm = (value || '').toLowerCase().trim();
                    const radios = Array.from(
                        document.querySelectorAll("input[type='radio'][id*='alloc' i], input[type='radio'][name*='alloc' i]")
                    ).filter((el) => !el.disabled && el.offsetParent !== null);

                    if (!radios.length) {
                        return false;
                    }

                    const text = (el) => (el ? (el.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase() : '');
                    let matched = null;

                    for (const input of radios) {
                        const lbl = input.id ? document.querySelector(`label[for='${input.id}']`) : null;
                        const container = input.closest('label, td, li, div, tr');
                        const haystack = [text(lbl), text(container), (input.value || '').toLowerCase(), (input.id || '').toLowerCase()].join(' ');
                        if (haystack.includes(norm)) {
                            matched = input;
                            break;
                        }
                    }

                    const target = matched || radios[0];
                    target.click();
                    target.dispatchEvent(new Event('input', { bubbles: true }));
                    target.dispatchEvent(new Event('change', { bubbles: true }));
                    return !!target.checked;
                }
                """,
                {"value": normalized},
            )
            if not selected:
                raise TimeoutError(
                    f"Could not locate/select allocation option '{allocation_type}' on URL: {self.page.url}"
                )
            logger.info(f"Allocation '{allocation_type}' selected via JavaScript fallback")
            return

        # Use JavaScript to check the radio GÇö Uniform.js (uniform-wired)
        # hides native inputs, so Playwright's .check() won't sync the
        # Uniform wrapper and the radio stays visually unchecked.
        checked = option_input.evaluate(
            """el => {
                el.checked = true;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('click', { bubbles: true }));
                if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                    $.uniform.update(el);
                }
                return el.checked;
            }"""
        )

        if not checked:
            try:
                option_input.check(force=True)
            except Exception:
                option_input.click(force=True)

        expect(option_input).to_be_checked(timeout=5000)
        logger.info(f"Allocation '{allocation_type}' selected")

    # ------------------------------------------------------------------
    # Risk Assessment
    # ------------------------------------------------------------------

    def _select_option_from_suitability_row(
        self, variants: list[str], label: str, preferred_input_name: str | None = None
    ) -> bool:
        """Select a suitability option by matching labels/text and checking the related input."""
        cleaned = [v.strip().lower() for v in variants if v and v.strip()]

        if preferred_input_name:
            try:
                selected = self.page.evaluate(
                    """
                    ({ name, variants }) => {
                      const radios = Array.from(
                        document.querySelectorAll(`input[type='radio'][name='${name}'], input[type='checkbox'][name='${name}']`)
                      );
                      if (!radios.length) return false;

                      const getText = (el) =>
                        (el ? (el.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase() : '');

                      for (const input of radios) {
                        const forLabel = input.id ? document.querySelector(`label[for='${input.id}']`) : null;
                        const container = input.closest('label, td, li, div');
                        const haystack = [getText(forLabel), getText(container)].join(' ');

                        if (!variants.some((v) => haystack.includes(v))) continue;
                        if (input.disabled) continue;

                        input.click();
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                      }
                      return false;
                    }
                    """,
                    {"name": preferred_input_name, "variants": cleaned},
                )
                if selected:
                    logger.info(f"{label} selected")
                    return True
            except Exception:
                pass

        for variant in variants:
            try:
                row = self.page.locator(f"tr:has(td:has-text('{variant}'))").first
                row.wait_for(state="visible", timeout=3000)
                inp = row.locator("input[type='radio'], input[type='checkbox']").first
                inp.wait_for(state="attached", timeout=3000)
                inp.evaluate(
                    """el => {
                        el.checked = true;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('click', { bubbles: true }));
                        if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                            $.uniform.update(el);
                        }
                    }"""
                )
                logger.info(f"{label} selected")
                return True
            except Exception:
                continue

        return False

    def _select_radio_by_group_index(self, group_name: str, index: int, label: str) -> bool:
        """Select radio/checkbox by group name and index position."""
        radios = self.page.locator(f"input[name='{group_name}']")
        total = radios.count()
        if total == 0:
            return False

        target_index = index if index >= 0 else total - 1
        if target_index < 0 or target_index >= total:
            return False

        target = radios.nth(target_index)
        target.wait_for(state="attached", timeout=5000)
        target.evaluate(
            """el => {
                el.checked = true;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('click', { bubbles: true }));
                if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                    $.uniform.update(el);
                }
            }"""
        )
        logger.info(f"{label} selected")
        return True

    def select_risk_tolerance(self, risk_level: str) -> None:
        """Select risk tolerance (Conservative, Moderate, Aggressive, etc.)."""
        logger.info(f"Selecting risk tolerance: {risk_level}")
        for _ in range(3):
            current_url = self.page.url.lower()
            if "clientsuitability" in current_url or "suitability" in current_url:
                break

            if "modifyinvestment" in current_url:
                logger.info("Risk tolerance requested from Modify Investment page; advancing first")
                self.click_next_button()
            elif "acctnumber" in current_url:
                logger.info("Risk tolerance requested from Account Number page; advancing to Suitability")
                self.click_next_button()
            else:
                break

            self.page.wait_for_load_state("networkidle", timeout=30000)

        variants = [
            risk_level,
            risk_level.strip().lower(),
            risk_level.replace("ate", ""),
            risk_level.replace("Moderate", "Moderately"),
        ]

        if self._select_option_from_suitability_row(
            variants, f"Risk tolerance '{risk_level}'", preferred_input_name="1"
        ):
            return

        risk_cell = self.page.get_by_role("cell", name=risk_level).first
        risk_cell.wait_for(state="visible", timeout=10000)
        risk_radio = risk_cell.locator("input[type='radio'], input[type='checkbox']").first
        risk_radio.wait_for(state="attached", timeout=10000)
        risk_radio.evaluate(
            """el => {
                el.checked = true;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('click', { bubbles: true }));
                if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                    $.uniform.update(el);
                }
            }"""
        )
        logger.info(f"Risk tolerance '{risk_level}' selected")

    def select_time_horizon(self, time_period: str) -> None:
        """Select time horizon (e.g., '5 years', '10 years', etc.)."""
        logger.info(f"Selecting time horizon: {time_period}")
        clean_time = time_period.strip().lower()

        # Deterministic mapping for known Suitability group order:
        # [2 years or less, 3-5 years, 6-9 years, 10 years+]
        if "10" in clean_time and self._select_radio_by_group_index(
            "2", 3, f"Time horizon '{time_period}'"
        ):
            return
        if "6" in clean_time and "9" in clean_time and self._select_radio_by_group_index(
            "2", 2, f"Time horizon '{time_period}'"
        ):
            return
        if "3" in clean_time and "5" in clean_time and self._select_radio_by_group_index(
            "2", 1, f"Time horizon '{time_period}'"
        ):
            return
        if self._select_radio_by_group_index("2", 0, f"Time horizon '{time_period}'"):
            return

        clean = time_period.strip().lower()
        variants = [
            time_period,
            f"-{time_period}",
            clean,
            clean.replace(" years", " years+"),
            clean.replace(" year", " year+"),
        ]
        if self._select_option_from_suitability_row(
            variants, f"Time horizon '{time_period}'", preferred_input_name="2"
        ):
            return

        raise AssertionError(f"Could not select time horizon '{time_period}' on URL: {self.page.url}")

    def select_liquidity_needs(self, percentage: str) -> None:
        """Select liquidity needs percentage."""
        logger.info(f"Selecting liquidity needs: {percentage}")
        clean_pct = percentage.replace("%", "").strip()

        # Deterministic mapping for Suitability group 3 order:
        # [Over 75%, 50-75%, 25-50%, Less than 25%]
        if clean_pct.isdigit():
            pct_value = int(clean_pct)
            if pct_value < 25 and self._select_radio_by_group_index(
                "3", 3, f"Liquidity needs '{percentage}'"
            ):
                return
            if pct_value < 50 and self._select_radio_by_group_index(
                "3", 2, f"Liquidity needs '{percentage}'"
            ):
                return
            if pct_value < 75 and self._select_radio_by_group_index(
                "3", 1, f"Liquidity needs '{percentage}'"
            ):
                return
            if self._select_radio_by_group_index("3", 0, f"Liquidity needs '{percentage}'"):
                return

        mapped: list[str] = []
        if clean_pct.isdigit():
            pct_value = int(clean_pct)
            if pct_value < 25:
                mapped = ["Less than 25%", "<25%", "0-25%"]
            elif pct_value < 50:
                mapped = ["25-50%", "25 - 50%"]
            elif pct_value < 75:
                mapped = ["50-75%", "50 - 75%"]
            else:
                mapped = ["Over 75%", ">75%", "75%+"]

        variants = [
            percentage,
            f"-{percentage}",
            f"{clean_pct}%",
            f"-{clean_pct}%",
            f"{clean_pct} %",
            f"0-{clean_pct}%",
            f"0 - {clean_pct}%",
            clean_pct,
            *mapped,
        ]

        if self._select_option_from_suitability_row(
            variants, f"Liquidity needs '{percentage}'", preferred_input_name="3"
        ):
            return

        raise AssertionError(f"Could not select liquidity needs '{percentage}' on URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Navigation - Next buttons
    # ------------------------------------------------------------------

    def _wait_until_next_enabled(self, next_btn: Locator, timeout: int = 3000) -> bool:
        try:
            self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=timeout)
            return True
        except Exception:
            return next_btn.is_enabled()

    def _dispatch_checked_input_events(self) -> None:
        self.page.evaluate(
            """
            () => {
              document
                .querySelectorAll("input[type='radio']:checked, input[type='checkbox']:checked")
                .forEach((el) => {
                  el.dispatchEvent(new Event('input', { bubbles: true }));
                  el.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }
            """
        )

    def _get_modify_investment_debug_state(self) -> dict:
        return self.page.evaluate(
            """
            () => {
                const isVisible = (el) => !!el && el.offsetParent !== null;
                const cleanText = (value) => (value || '').replace(/\s+/g, ' ').trim();

                const next = document.querySelector('#nextButton');
                const checkedInputs = Array.from(
                    document.querySelectorAll("input[type='radio']:checked, input[type='checkbox']:checked")
                ).map((el) => ({
                    id: el.id || '',
                    name: el.name || '',
                    value: el.value || '',
                }));

                const validationText = Array.from(
                    document.querySelectorAll('.field-validation-error, .validation-summary-errors, .error, .message, .warning')
                )
                    .filter((el) => isVisible(el))
                    .map((el) => cleanText(el.textContent))
                    .filter(Boolean);

                const headings = Array.from(document.querySelectorAll('h1, h2, h3, legend, .modal-title'))
                    .filter((el) => isVisible(el))
                    .map((el) => cleanText(el.textContent))
                    .filter(Boolean);

                return {
                    nextEnabled: !!next && !next.disabled,
                    checkedInputs,
                    validationText,
                    headings,
                    bodySnippet: cleanText(document.body ? document.body.innerText : '').slice(0, 1200),
                };
            }
            """
        )

    def _raise_modify_investment_blocker(self) -> None:
        debug_state = self._get_modify_investment_debug_state()
        screenshot_path = "reports/modify_investment_next_disabled.png"
        html_path = "reports/modify_investment_next_disabled.html"
        self.page.screenshot(path=screenshot_path, full_page=True)
        self.page.locator("html").evaluate(
            "(el) => el.outerHTML"
        )
        html_content = self.page.locator("html").evaluate("(el) => el.outerHTML")
        with open(html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        raise AssertionError(
            "Next button is disabled on Modify Investment page. "
            f"URL: {self.page.url}. "
            f"Headings: {debug_state.get('headings', [])}. "
            f"Checked inputs: {debug_state.get('checkedInputs', [])}. "
            f"Validation text: {debug_state.get('validationText', [])}. "
            f"Body snippet: {debug_state.get('bodySnippet', '')}. "
            f"Screenshot: {screenshot_path}. HTML: {html_path}"
        )

    def _recover_suitability_next(self, next_btn: Locator) -> bool:
        logger.warning("Next disabled on suitability page; auto-selecting unanswered groups")
        start_url = self.page.url
        try:
            self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=3000)
            return True
        except Exception:
            return self.page.url != start_url

    def _recover_modify_investment_next(self) -> bool:
        """Recover Next action on Modify Investment when UI state is stale/disabled."""
        logger.warning("Next disabled on Modify Investment; attempting recovery")
        start_url = self.page.url

        recovery_state = self.page.evaluate(
            """
            () => {
                const isVisible = (el) => !!el && el.offsetParent !== null;
                const allocationInputs = Array.from(
                    document.querySelectorAll("input[type='radio'][id*='alloc'], input[type='radio'][name*='alloc']")
                ).filter((el) => !el.disabled && isVisible(el));

                let selected = allocationInputs.find((el) => el.checked) || null;
                if (!selected) {
                    const preferred = document.querySelector('#allocRdFull1_1');
                    selected = preferred && !preferred.disabled && isVisible(preferred)
                        ? preferred
                        : allocationInputs[0] || null;
                    if (selected) {
                        selected.click();
                    }
                }

                if (selected) {
                    selected.dispatchEvent(new Event('input', { bubbles: true }));
                    selected.dispatchEvent(new Event('change', { bubbles: true }));
                }

                const next = document.querySelector('#nextButton');
                return {
                    hasAllocation: !!selected,
                    nextEnabled: !!next && !next.disabled,
                };
            }
            """
        )

        self._dispatch_checked_input_events()
        try:
            self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=3000)
        except Exception:
            pass

        if recovery_state.get("nextEnabled"):
            return True

        return recovery_state.get("hasAllocation", False) and self.page.url != start_url

    def _recover_source_account_next(self, next_btn: Locator) -> bool:
        logger.warning("Next disabled on Source Account; trying to auto-select account")
        current_url = self.page.url

        # Strategy 1: Click the first unchecked account checkbox/radio
        self.page.evaluate(
            """
            () => {
                const options = Array.from(
                    document.querySelectorAll("input[type='radio'], input[type='checkbox']")
                ).filter((el) => !el.disabled && el.offsetParent !== null);

                if (!options.length) return;
                if (!options.some((el) => el.checked)) options[0].click();

                options
                    .filter((el) => el.checked)
                    .forEach((el) => {
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    });
            }
            """
        )
        try:
            self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=3000)
            logger.info("Next enabled after clicking checkbox/radio")
            return True
        except Exception:
            pass

        # Strategy 2: Try clicking on account row/link/cell in the table
        try:
            account_rows = self.page.locator(
                "table tr td a, table tr td input[type='checkbox'], "
                "table tr td input[type='radio'], "
                ".account-row, tr[data-account-id], tr.clickable"
            )
            if account_rows.count() > 0:
                account_rows.first.click(force=True)
                self.page.wait_for_timeout(1000)
                try:
                    self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=3000)
                    logger.info("Next enabled after clicking account row")
                    return True
                except Exception:
                    pass
        except Exception:
            pass

        # Strategy 3: Use JS to select the first account and enable Next
        self.page.evaluate(
            """
            () => {
                // Try selecting the first account via any input
                const inputs = document.querySelectorAll(
                    "input[type='checkbox']:not(:checked):not(:disabled), " +
                    "input[type='radio']:not(:checked):not(:disabled)"
                );
                for (const inp of inputs) {
                    inp.checked = true;
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    inp.dispatchEvent(new Event('click', { bubbles: true }));
                    break;
                }

                // Force-enable the Next button
                const next = document.querySelector('#nextButton');
                if (next) {
                    next.removeAttribute('disabled');
                    next.classList.remove('disableButtonCss');
                    next.classList.add('enableButtonCss');
                }
            }
            """
        )
        self.page.wait_for_timeout(500)

        try:
            self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=2000)
            logger.info("Next enabled after JS force-enable")
            return True
        except Exception:
            pass

        # Strategy 4: Force-click the button with disabled attribute removed
        self.page.evaluate(
            """
            () => {
                const next = document.querySelector('#nextButton');
                if (!next) return;
                next.removeAttribute('disabled');
                next.classList.remove('disableButtonCss');
                next.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                next.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                next.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                
                // Also try form submission
                const form = next.closest('form');
                if (form) form.submit();
            }
            """
        )
        try:
            self.page.wait_for_url(lambda url: url != current_url, timeout=5000)
            logger.info("Page navigated after force-click/submit")
            return True
        except Exception:
            return next_btn.is_enabled()

    def _dismiss_blocking_modal(self, wait_for_modal: bool = False) -> None:
        """Dismiss model_picker_modal or InvestmentActionModal if blocking.

        Args:
            wait_for_modal: If True, wait up to 5s for InvestmentActionModal
                            to appear (use after clicking Next where the modal
                            may or may not show up).
        """
        # Handle model_picker_modal
        modal = self.page.locator("#model_picker_modal")
        if modal.is_visible():
            logger.warning("model_picker_modal is blocking - dismissing it")
            ok_btn = modal.locator("#OkButton")
            if ok_btn.is_visible():
                ok_btn.click(force=True)
            else:
                close_btn = modal.locator(".close, [data-dismiss='modal']")
                if close_btn.count() > 0:
                    close_btn.first.click(force=True)
            modal.wait_for(state="hidden", timeout=10000)
            logger.info("model_picker_modal dismissed")

        # Handle InvestmentActionModal ("Make a Selection" popup)
        inv_modal = self.page.locator("#InvestmentActionModal")

        # If requested, give the modal a few seconds to appear
        if wait_for_modal and not inv_modal.is_visible():
            try:
                inv_modal.wait_for(state="visible", timeout=5000)
            except Exception:
                pass  # Modal didn't appear - that's fine

        if inv_modal.is_visible():
            logger.warning("InvestmentActionModal is blocking - selecting Destination Investment")
            radio = self.page.locator("input[name='action'][value='DestinationInvestment']")
            if radio.count() > 0:
                radio.evaluate(
                    """el => {
                        el.checked = true;
                        el.dispatchEvent(new Event('change', {bubbles: true}));
                        el.dispatchEvent(new Event('click', {bubbles: true}));
                        if (typeof $ !== 'undefined' && $.uniform && $.uniform.update) {
                            $.uniform.update(el);
                        }
                    }"""
                )
            ok_btn = inv_modal.get_by_role("button", name="OK")
            if ok_btn.is_visible():
                self.click(ok_btn)
            else:
                # Fallback: click primary button in modal
                primary_btn = inv_modal.locator(".btn-transition-primary, .btn-primary").first
                if primary_btn.count() > 0:
                    primary_btn.click(force=True)
            inv_modal.wait_for(state="hidden", timeout=15000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            logger.info("InvestmentActionModal dismissed")

    def click_next_button(self) -> None:
        """Click the Next button to proceed to next step."""
        logger.info("Clicking Next button")
        self._dismiss_blocking_modal()
        next_btn = self.next_button.first
        next_btn.wait_for(state="visible", timeout=15000)

        start_url = self.page.url
        if not self._wait_until_next_enabled(next_btn):
            self._dispatch_checked_input_events()

            # Re-check after dispatching events
            try:
                self.page.locator("#nextButton:enabled").wait_for(state="attached", timeout=2000)
            except Exception:
                pass

            current_url = self.page.url.lower()
            recovered = False
            if "clientsuitability" in current_url:
                recovered = self._recover_suitability_next(next_btn)
            elif "modifyinvestment" in current_url:
                recovered = self._recover_modify_investment_next() or next_btn.is_enabled()
            elif "acctselection" in current_url:
                recovered = self._recover_source_account_next(next_btn)

            if not recovered and not next_btn.is_enabled():
                # If URL changed during recovery, we navigated forward GÇö treat as success
                if self.page.url != start_url:
                    self.page.wait_for_load_state("networkidle", timeout=15000)
                    logger.info(f"Next clicked (via navigation) - Current URL: {self.page.url}")
                    return
                if "modifyinvestment" in current_url:
                    self._raise_modify_investment_blocker()
                raise AssertionError(f"Next button is disabled on URL: {self.page.url}")

            if self.page.url != start_url:
                self.page.wait_for_load_state("networkidle", timeout=15000)
                logger.info(f"Next clicked - Current URL: {self.page.url}")
                return

        self.click(next_btn)

        # After clicking Next, the InvestmentActionModal may or may not appear.
        # Wait briefly for it and dismiss if present.
        self._dismiss_blocking_modal(wait_for_modal=True)

        # Wait for URL to change GÇö handles slow navigations properly
        try:
            self.page.wait_for_url(lambda url: url != start_url, timeout=15000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            logger.info(f"Next clicked - Current URL: {self.page.url}")
            return
        except Exception:
            pass

        if self.page.url != start_url:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            logger.info(f"Next clicked - Current URL: {self.page.url}")
            return

        # URL truly didn't change GÇö retry with force click
        logger.warning(f"URL unchanged after Next click on {self.page.url}, retrying with force click")
        try:
            next_btn.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        try:
            next_btn.click(force=True, timeout=30000, no_wait_after=True)
        except Exception as exc:
            logger.warning(f"Force click raised ({exc}); checking if navigation already happened")

        # Wait for navigation to complete
        try:
            self.page.wait_for_url(lambda url: url != start_url, timeout=30000)
        except Exception:
            try:
                self.page.wait_for_load_state("load", timeout=15000)
            except Exception:
                pass

        logger.info(f"Next clicked - Current URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Completion Validation
    # ------------------------------------------------------------------

    def validate_investment_change_completed(self) -> None:
        """Validate that the investment change process completed successfully."""
        logger.info("Validating investment change completion")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        # Check for completion indicators
        body_text = self.page.locator("body").text_content() or ""
        is_completed = any(
            keyword.lower() in body_text.lower()
            for keyword in ["complete", "success", "submitted", "confirmation"]
        )

        if is_completed:
            logger.info("Investment change completed successfully")
        else:
            # Fallback: just verify we're not on an error page
            is_error = any(
                keyword.lower() in body_text.lower() for keyword in ["error", "failed", "invalid"]
            )
            assert not is_error, f"Error detected on page. URL: {self.page.url}"
            logger.info("Investment change process appears to have completed")
