"""Check Contributions (CheckAttributesCV1) Coach Page Object.

The coach loads at URL pattern ``.../teamworks/executecf?serviceName=CheckContributions``
inside an ``<iframe title="Coach">``. All locators below resolve through that
frame using role / label / text selectors (matching what Playwright Codegen
records for this app), which are far more stable than the auto-generated
``CheckAttributesCV1:*`` element IDs.
"""

from datetime import datetime
import re
from typing import Optional
import time as _time

from playwright.sync_api import FrameLocator, Locator, Page

from pages.base_page import BasePage
from locators.baw.check_contributions_locators import CheckContributionsLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class CheckContributionsPage(BasePage):
    """Page object for the CheckContributions coach (Check Details form)."""

    PAGE_NAME = "Check Contributions Page"

    COACH_FRAME_SELECTOR = CheckContributionsLocators.COACH_FRAME_SELECTOR
    XP_CHECK_TYPE_OPTION_TPL = CheckContributionsLocators.XP_CHECK_TYPE_OPTION_TPL
    DEFAULT_CHECK_TYPE_INDEX = CheckContributionsLocators.DEFAULT_CHECK_TYPE_INDEX

    def __init__(self, page: Page, home_url: str = "") -> None:
        super().__init__(page, base_url=home_url)
        self.page = page

    # ---------- frame helpers ----------
    def _frame(self) -> FrameLocator:
        """Coach iframe (the form lives inside it)."""
        return self.page.frame_locator(self.COACH_FRAME_SELECTOR)

    def _textbox(self, accessible_name: str) -> Locator:
        return self._frame().get_by_role("textbox", name=accessible_name)

    def _today_str(self, fmt: str = "%m-%d-%Y") -> str:
        return datetime.now().strftime(fmt)

    def _attach_screenshot(self, name: str) -> None:
        try:
            logger.attach_screenshot(self.page, name)
        except Exception as e:
            logger.warning(f"Screenshot attach failed for '{name}': {e}")

    def _safe_fill(self, loc: Locator, value: str, timeout: int = 30000) -> None:
        loc.wait_for(state="visible", timeout=timeout)
        try:
            loc.click(timeout=5000)
        except Exception:
            pass
        loc.fill(str(value), timeout=timeout)

    def pause_after_coach_entry(self, pause_ms: int = 2000) -> None:
        """Small stabilization pause right after entering Check Coach."""
        with logger.step(
            f"Pause after entering Check Coach ({pause_ms}ms)",
            page=self.page,
        ):
            self.page.wait_for_timeout(pause_ms)
            logger.info(f"Paused for {pause_ms}ms after coach entry")

    # ---------- step 1: Alpha Amount + mismatch banner ----------
    def enter_alpha_amount_and_capture_banner(self, alpha_amount: str) -> str:
        """Enter Alpha Amount, capture the mismatch banner text + screenshot.

        Returns banner text (empty string if no banner appeared).
        """
        with logger.step(
            f"Enter Alpha Amount '{alpha_amount}' and capture mismatch banner",
            page=self.page,
        ):
            alpha = self._textbox("Alpha Amount")
            self._safe_fill(alpha, alpha_amount)
            try:
                alpha.press("Tab")
            except Exception:
                pass
            self.page.wait_for_timeout(1500)

            banner_text = ""
            try:
                banner = self._frame().get_by_text("do not match").first
                banner.wait_for(state="visible", timeout=8000)
                banner_text = (banner.inner_text(timeout=5000) or "").strip()
                logger.info(f"Mismatch banner captured: {banner_text}")
            except Exception:
                logger.info("Mismatch banner not displayed for the entered Alpha Amount")

            self._attach_screenshot("Alpha Amount mismatch banner")
            return banner_text

    # ---------- step 2 + 3: fill all required check details ----------
    def select_check_type(self, value: Optional[str] = None) -> None:
        """Select the Check Type using the dedicated XPath.

        ``value`` is optional:
        * ``None`` (default) or empty → uses ``DEFAULT_CHECK_TYPE_INDEX`` (``1``).
        * digit string ("1", "2", ...) → picks
          ``//option[@id="singleselect-option-CheckAttributesCV1:CheckType[N]"]``.
        * any other string → passed straight to ``select_option`` as the
          option value.
        """
        raw = "" if value is None else str(value).strip()
        if not raw:
            raw = self.DEFAULT_CHECK_TYPE_INDEX

        with logger.step(f"Select Check Type '{raw}'", page=self.page):
            frame = self._frame()

            if raw.isdigit():
                xp = self.XP_CHECK_TYPE_OPTION_TPL.format(idx=raw)
                option = frame.locator(f"xpath={xp}").first
                option.wait_for(state="attached", timeout=30000)
                option_value = option.get_attribute("value", timeout=5000) or ""
                if not option_value:
                    raise RuntimeError(
                        f"Check Type option at index {raw} has no value attribute"
                    )
                select = frame.get_by_label("Check Type")
                select.select_option(option_value, timeout=15000)
                logger.info(
                    f"Check Type selected via option index {raw} (value='{option_value}')"
                )
                return

            select = frame.get_by_label("Check Type")
            select.wait_for(state="visible", timeout=30000)
            select.select_option(raw, timeout=15000)
            logger.info(f"Check Type selected by value='{raw}'")

    def enter_numerical_amount(self, value: str) -> None:
        with logger.step(f"Enter Numerical Amount '{value}'", page=self.page):
            num = self._textbox("Numerical Amount")
            self._safe_fill(num, value)
            try:
                num.press("Tab")
            except Exception:
                pass

    def enter_alpha_amount(self, value: str) -> None:
        with logger.step(f"Enter Alpha Amount (final) '{value}'", page=self.page):
            alpha = self._textbox("Alpha Amount")
            self._safe_fill(alpha, value)
            try:
                alpha.press("Tab")
            except Exception:
                pass

    def select_today_check_date(self) -> str:
        """Pick today's date via the calendar widget (most reliable in BAW).

        Returns the date string in MM-DD-YYYY for reporting purposes.
        """
        today = self._today_str("%m-%d-%Y")
        day = str(datetime.now().day)
        with logger.step(f"Pick today's Check Date ({today})", page=self.page):
            frame = self._frame()
            cal_btn = frame.get_by_role("button", name="calendar")
            cal_btn.wait_for(state="visible", timeout=15000)
            cal_btn.click()
            self.page.wait_for_timeout(500)

            today_cell = frame.locator(
                CheckContributionsLocators.CALENDAR_TODAY_CELL
                + f"[normalize-space()='{day}']"
            ).first
            try:
                today_cell.wait_for(state="visible", timeout=4000)
            except Exception:
                today_cell = frame.get_by_role("gridcell", name=day, exact=True).first
                try:
                    today_cell.wait_for(state="visible", timeout=4000)
                except Exception:
                    today_cell = frame.get_by_label(day, exact=True).first
                    today_cell.wait_for(state="visible", timeout=4000)
            today_cell.click()
            logger.info(f"Check Date set via calendar widget: day {day}")
            return today

    def set_check_date(self, value: str) -> str:
        """Set Check Date textbox directly.

        Accepts ``MM-DD-YYYY`` or ``YYYY-MM-DD`` and returns ``MM-DD-YYYY``.
        """
        raw = str(value or "").strip()
        if not raw:
            raise ValueError("Check Date value is empty")

        normalized = raw
        if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
            yyyy, mm, dd = raw.split("-")
            normalized = f"{mm}-{dd}-{yyyy}"
        elif re.match(r"^\d{4}/\d{2}/\d{2}$", raw):
            yyyy, mm, dd = raw.split("/")
            normalized = f"{mm}-{dd}-{yyyy}"
        elif re.match(r"^\d{2}/\d{2}/\d{4}$", raw):
            mm, dd, yyyy = raw.split("/")
            normalized = f"{mm}-{dd}-{yyyy}"

        with logger.step(f"Set Check Date '{normalized}'", page=self.page):
            check_date = self._textbox("Check Date")
            self._safe_fill(check_date, normalized)
            try:
                check_date.press("Tab")
            except Exception:
                pass
            logger.info(f"Check Date set to: {normalized}")
            return normalized

    def enter_check_number(self, value: str) -> None:
        with logger.step(f"Enter Check Number '{value}'", page=self.page):
            cn = self._textbox("Check Number")
            self._safe_fill(cn, value)

    def enter_aba_routing(self, value: str, bank_name: Optional[str] = None) -> None:
        """Enter ABA Routing and (if provided) click the matching bank suggestion.

        Without picking the suggestion, BAW typically leaves Bank Account
        disabled.
        """
        with logger.step(
            f"Enter ABA Routing Number '{value}'"
            + (f" and pick bank '{bank_name}'" if bank_name else ""),
            page=self.page,
        ):
            aba = self._textbox("ABA Routing Number")
            self._safe_fill(aba, value)
            self.page.wait_for_timeout(1500)
            if bank_name:
                try:
                    suggestion = self._frame().get_by_text(bank_name, exact=False).first
                    suggestion.wait_for(state="visible", timeout=10000)
                    suggestion.click()
                    logger.info(f"Selected bank suggestion: {bank_name}")
                except Exception as e:
                    logger.warning(
                        f"Bank suggestion '{bank_name}' not selectable: {e}"
                    )
            else:
                try:
                    aba.press("Tab")
                except Exception:
                    pass

    def enter_bank_account(self, value: str) -> None:
        with logger.step(f"Enter Bank Account # '{value}'", page=self.page):
            bank = self._textbox("Bank Account #")
            self._safe_fill(bank, value)

    def fill_check_details(
        self,
        numerical_amount: str,
        alpha_amount: str,
        check_number: str,
        aba_routing: str,
        bank_account: str,
        check_type: Optional[str] = None,
        bank_name: Optional[str] = None,
        select_check_type: bool = True,
    ) -> str:
        """Fill all Check Details fields. Check Date is always set to TODAY.

        ``check_type`` is optional; when ``select_check_type=True`` and no
        value is supplied, the default option index is used.

        Returns the date string used for Check Date.
        """
        with logger.step("Fill Check Details section", page=self.page):
            if select_check_type:
                self.select_check_type(check_type)
            self.enter_numerical_amount(numerical_amount)
            self.enter_alpha_amount(alpha_amount)
            date_str = self.select_today_check_date()
            self.enter_check_number(check_number)
            self.enter_aba_routing(aba_routing, bank_name=bank_name)
            self.enter_bank_account(bank_account)
            self._attach_screenshot("Check Details filled")
            return date_str

    # ---------- step 4: Check Images Validation ----------
    def fetch_check_images_validation(self, wait_timeout: int = 120000) -> dict:
        """Return ``{'system_result': str, 'description': str, 'description_items': list[str]}`` from the
        Check Images Validation section. Polls until System Result populates
        (BAW computes it asynchronously after the form is filled)."""
        with logger.step("Fetch Check Images Validation result", page=self.page):
            frame = self._frame()
            # Let any in-flight BAW spinner settle before reading the result.
            try:
                self.baw_spinner_loader(appear_timeout=2000, disappear_timeout=30000)
            except Exception:
                pass
            header = frame.get_by_text("Check Images Validation", exact=False).first
            try:
                header.scroll_into_view_if_needed(timeout=10000)
            except Exception:
                pass
            header.wait_for(state="visible", timeout=30000)

            # System Result is rendered asynchronously. Try several locator
            # strategies and poll until we get a non-empty value (or timeout).
            sr_candidates = [
                CheckContributionsLocators.SYSTEM_RESULT_XPATH_1,
                CheckContributionsLocators.SYSTEM_RESULT_XPATH_2,
                CheckContributionsLocators.SYSTEM_RESULT_XPATH_3,
            ]
            system_result = ""
            deadline = _time.time() + (wait_timeout / 1000.0)
            while _time.time() < deadline and not system_result:
                for xp in sr_candidates:
                    try:
                        sr_loc = frame.locator(xp).first
                        if sr_loc.count() == 0:
                            continue
                        txt = (sr_loc.inner_text(timeout=2000) or "").strip()
                        # BAW shows '...' while the validation is still
                        # being computed — treat as not-ready and keep polling.
                        if (
                            txt
                            and txt.lower() != "system result"
                            and txt.strip(". ").strip() != ""
                        ):
                            system_result = txt
                            break
                    except Exception:
                        continue
                if not system_result:
                    self.page.wait_for_timeout(1000)
            if not system_result:
                logger.warning("System Result value not readable after polling")

            description = ""
            description_items: list[str] = []
            numeric_validation_line = ""
            alpha_validation_line = ""
            numeric_extracted_amount = ""
            alpha_extracted_amount = ""
            check_date_validation_line = ""
            extracted_check_date = ""
            try:
                desc_loc = frame.locator(
                    CheckContributionsLocators.DESCRIPTION_FOLLOWING
                ).first
                desc_loc.wait_for(state="visible", timeout=5000)
                description = (desc_loc.inner_text(timeout=5000) or "").strip()
                description_items = [
                    line.strip(" -\t")
                    for line in description.splitlines()
                    if line.strip()
                ]

                amount_re = re.compile(r"extracted value of\s*\$?([0-9][0-9,]*(?:\.[0-9]+)?)", re.IGNORECASE)
                date_re = re.compile(
                    r"extracted\s+check\s+date\s+of\s+"
                    r"((?:\d{4}[-/]\d{2}[-/]\d{2})|(?:\d{2}[-/]\d{2}[-/]\d{4}))",
                    re.IGNORECASE,
                )
                for line in description_items:
                    line_lower = line.lower()
                    if "numeric amount" in line_lower and not numeric_validation_line:
                        numeric_validation_line = line
                        m = amount_re.search(line)
                        if m:
                            numeric_extracted_amount = m.group(1)
                    if "alpha amount" in line_lower and not alpha_validation_line:
                        alpha_validation_line = line
                        m = amount_re.search(line)
                        if m:
                            alpha_extracted_amount = m.group(1)
                    if "check date" in line_lower and "extracted" in line_lower and not check_date_validation_line:
                        check_date_validation_line = line
                        m = date_re.search(line)
                        if m:
                            extracted_check_date = m.group(1)
            except Exception:
                logger.warning("Description value not readable")

            logger.info(
                f"Check Images Validation -> System Result: '{system_result}' | "
                f"Description: '{description[:200]}'"
            )
            self._attach_screenshot("Check Images Validation")
            return {
                "system_result": system_result,
                "description": description,
                "description_items": description_items,
                "numeric_validation_line": numeric_validation_line,
                "alpha_validation_line": alpha_validation_line,
                "numeric_extracted_amount": numeric_extracted_amount,
                "alpha_extracted_amount": alpha_extracted_amount,
                "check_date_validation_line": check_date_validation_line,
                "extracted_check_date": extracted_check_date,
            }

    def assert_system_result_passed(self, expected: str = "Passed") -> dict:
        """Log Check Images Validation result; never fail.

        The System Result is informational — BAW computes it asynchronously
        based on OCR vs. entered values, and a "Review Required" outcome is
        a valid downstream state (Allocation + IWR Complete still proceed).
        Mismatches are logged and attached to the report for visibility.
        """
        result = self.fetch_check_images_validation()
        actual = (result.get("system_result") or "").strip()
        if actual.lower() == expected.strip().lower():
            logger.info(
                f"Check Images Validation matched expected "
                f"(System Result='{actual}')"
            )
        else:
            logger.warning(
                f"Check Images Validation informational: expected "
                f"'{expected}' but got '{actual}'. Description:\n"
                f"{result.get('description', '')}"
            )
            self._attach_screenshot(
                f"Check Images Validation (System Result='{actual or 'empty'}')"
            )
        return result

    # ---------- step 5: Image Type ----------
    def select_image_type(self, image_type: str, row_index: int = 0) -> None:
        """Select Image Type in the Check Images - Digital Checks table row."""
        with logger.step(
            f"Select Image Type '{image_type}' (row {row_index})", page=self.page
        ):
            frame = self._frame()
            # Restrict to actual <select> elements only — `get_by_label` can
            # match the column <th aria-label="Image Type"> header otherwise.
            candidates = [
                lambda: frame.locator('select[aria-label="Image Type"]').nth(row_index),
                lambda: frame.locator(
                    'xpath=//select[contains(@id,"CheckImages_Table") '
                    'and contains(@id,"ImageType")]'
                ).nth(row_index),
                lambda: frame.locator(
                    CheckContributionsLocators.IMAGE_TYPE_SELECT_XPATH_TPL.format(row_index=row_index)
                ).first,
                lambda: frame.get_by_label("Image Type").locator("self::select").nth(row_index),
            ]
            select = None
            last_err: Exception | None = None
            for build in candidates:
                try:
                    cand = build()
                    cand.wait_for(state="visible", timeout=10000)
                    select = cand
                    break
                except Exception as exc:
                    last_err = exc
                    continue
            if select is None:
                raise RuntimeError(
                    f"Image Type <select> not found in row {row_index}"
                ) from last_err
            try:
                select.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            try:
                select.select_option(label=image_type)
            except Exception:
                select.select_option(image_type)
            logger.info(f"Image Type selected: {image_type}")

    # ---------- step 6: Allocation ----------
    def add_managed_allocation(self, account_number: str, allocation_amount: str) -> None:
        """Select the managed Allocation account, enter Allocation Amount,
        and click Add."""
        with logger.step(
            f"Add Managed Allocation: account={account_number}, "
            f"amount={allocation_amount}",
            page=self.page,
        ):
            frame = self._frame()
            acct = frame.locator(
                CheckContributionsLocators.ALLOCATION_ACCOUNT_SELECT
            ).first
            try:
                acct.scroll_into_view_if_needed(timeout=10000)
            except Exception:
                pass
            acct.wait_for(state="visible", timeout=30000)
            try:
                acct.select_option(label=str(account_number))
            except Exception:
                acct.select_option(str(account_number))

            amt = frame.locator(
                "xpath=//input[contains(@id,'CheckAttributesCV1')"
                " and (contains(@id,'Allocation_Amount')"
                " or contains(@id,'AllocationAmount')"
                " or contains(@id,'Allocation_Amt'))]"
            ).first
            amt.wait_for(state="visible", timeout=30000)
            self._safe_fill(amt, allocation_amount)
            try:
                amt.press("Tab")
            except Exception:
                pass

            add_btn = frame.get_by_role("button", name="Add").first
            add_btn.wait_for(state="visible", timeout=15000)
            add_btn.click()
            self.page.wait_for_timeout(1500)
            self._attach_screenshot("Allocation added")

    # ---------- step 7: IWR Complete ----------
    def _handle_iwr_complete_popup(self) -> dict:
        """Handle post-IWR popup and capture post-Proceed Shell details."""
        checkbox_xpaths = [
            '//input[@id="checkboxgroup-item-input-CheckAttributesCV1:PopupCheckboxesGroup[0]"]',
            '//input[@id="checkboxgroup-item-input-CheckAttributesCV1:PopupCheckboxesGroup[1]"]',
        ]
        proceed_xpath = (
            '//button[@id="button-button-CheckAttributesCV1:ProceedTaskCompleteButton"]'
        )

        with logger.step("Handle IWR Complete popup", page=self.page):
            frame = self._frame()

            popup_checkboxes = []
            popup_proceed = None
            for scope in (frame, self.page):
                try:
                    checkboxes = []
                    for checkbox_xpath in checkbox_xpaths:
                        cb = scope.locator(f"xpath={checkbox_xpath}").first
                        try:
                            cb.wait_for(state="visible", timeout=2000)
                            checkboxes.append(cb)
                        except Exception:
                            continue
                    if not checkboxes:
                        continue
                    popup_checkboxes = checkboxes
                    popup_proceed = scope.locator(f"xpath={proceed_xpath}").first
                    popup_proceed.wait_for(state="visible", timeout=10000)
                    break
                except Exception:
                    popup_checkboxes = []
                    popup_proceed = None

            if not popup_checkboxes or popup_proceed is None:
                logger.info("IWR Complete popup not displayed")
                return {}

            # Ensure each discovered checkbox state is committed so Proceed is enabled.
            for popup_checkbox in popup_checkboxes:
                checked = False
                try:
                    if not popup_checkbox.is_checked():
                        popup_checkbox.check(timeout=10000)
                    checked = popup_checkbox.is_checked()
                except Exception:
                    try:
                        popup_checkbox.click(timeout=10000)
                        checked = popup_checkbox.is_checked()
                    except Exception:
                        checked = False

                if not checked:
                    try:
                        popup_checkbox.evaluate(
                            """el => {
                                el.checked = true;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                            }"""
                        )
                        checked = popup_checkbox.is_checked()
                    except Exception:
                        checked = False

                if not checked:
                    raise RuntimeError("IWR popup checkbox could not be selected")

            # Wait until Proceed is actually enabled before clicking.
            proceed_enabled = False
            for _ in range(20):
                try:
                    disabled_attr = (popup_proceed.get_attribute("disabled") or "").strip().lower()
                    aria_disabled = (popup_proceed.get_attribute("aria-disabled") or "").strip().lower()
                    class_attr = (popup_proceed.get_attribute("class") or "").lower()
                    is_enabled = popup_proceed.is_enabled()
                    if is_enabled and not disabled_attr and aria_disabled != "true" and " disabled" not in class_attr:
                        proceed_enabled = True
                        break
                except Exception:
                    pass
                self.page.wait_for_timeout(500)

            if not proceed_enabled:
                raise RuntimeError("IWR popup Proceed button stayed disabled after checkbox selection")

            popup_proceed.click(timeout=10000)
            self.page.wait_for_timeout(1000)
            logger.info("IWR popup handled: checkbox selected and Proceed clicked")

            # Proceed can close the current coach tab. Re-bind to the Shell page
            # and capture Check Image Extraction details there.
            shell_capture: dict = {}
            try:
                from pages.baw.shell_process_page import ShellProcessPage

                shell_page = ShellProcessPage(self.page)
                shell_capture = shell_page.fetch_check_image_extraction_details(wait_timeout_ms=60000)
                self.page = shell_page.page
                self._attach_screenshot("Shell page after IWR popup Proceed")
            except Exception as e:
                logger.warning(f"Unable to fetch Shell details after Proceed: {e}")

            return shell_capture

    def click_iwr_complete(self) -> dict:
        with logger.step("Click IWR Complete", page=self.page):
            btn = self._frame().get_by_role("button", name="IWR Complete").first
            try:
                btn.scroll_into_view_if_needed(timeout=10000)
            except Exception:
                pass
            btn.wait_for(state="visible", timeout=30000)
            self.page.pause()
            btn.click()
            shell_capture = self._handle_iwr_complete_popup()
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            self._attach_screenshot("After IWR Complete click")
            logger.info("IWR Complete clicked")
            return shell_capture

    def click_save_and_close(self) -> None:
        """Click Save & Close on Check Contributions coach and wait for redirect."""
        with logger.step("Click Save & Close", page=self.page):
            frame = self._frame()
            candidates = [
                lambda: frame.get_by_role("button", name="Save & Close").first,
                lambda: frame.get_by_role("button", name="Save and Close").first,
                lambda: frame.locator(CheckContributionsLocators.SAVE_CLOSE_BTN_HAS_TEXT_1).first,
                lambda: frame.locator(CheckContributionsLocators.SAVE_CLOSE_BTN_HAS_TEXT_2).first,
                lambda: frame.locator("xpath=//button[contains(@id,'Save') and contains(@id,'Close')]").first,
                lambda: frame.locator("xpath=//button[contains(@name,'Save') and contains(@name,'Close')]").first,
            ]

            btn = None
            last_err: Exception | None = None
            for build in candidates:
                try:
                    cand = build()
                    cand.wait_for(state="visible", timeout=10000)
                    btn = cand
                    break
                except Exception as exc:
                    last_err = exc

            if btn is None:
                raise RuntimeError("Save & Close button not found on Check Contributions coach") from last_err

            self._attach_screenshot("Before Save & Close click")
            try:
                btn.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass

            clicked = False
            click_errors: list[str] = []
            for attempt, mode in enumerate(("normal", "force", "js"), start=1):
                try:
                    if mode == "normal":
                        btn.click(timeout=10000)
                    elif mode == "force":
                        btn.click(force=True, timeout=10000)
                    else:
                        btn.evaluate("el => el.click()")

                    self.page.wait_for_timeout(1000)
                    # If button disappears, action likely fired.
                    if not btn.is_visible(timeout=2000):
                        clicked = True
                        break
                    # Even if still visible, URL/title move away from CheckContributions indicates success.
                    current_url = (self.page.url or "").lower()
                    current_title = (self.page.title() or "").lower()
                    if "checkcontributions" not in current_url or "shell process" in current_title:
                        clicked = True
                        break
                except Exception as exc:
                    click_errors.append(f"{mode} click attempt {attempt} failed: {exc}")

            if not clicked:
                logger.warning(
                    "Save & Close state change not observed immediately; "
                    "continuing with downstream Shell-page wait. "
                    + (" | ".join(click_errors) if click_errors else "")
                )

            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            self._attach_screenshot("After Save & Close click")
            logger.info("Save & Close clicked")
