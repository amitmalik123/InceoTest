from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional

import allure
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.stp.shared.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.settings import settings
from utils.wait_utils import WaitTimeoutError, wait_for_element_count

logger = get_allure_logger(__name__)

TIME_FORMAT = "%I:%M %p"  # corresponds to pattern "h:m a"


@dataclass
class OutlookOtpConfig:
    email: str
    password: str


class OutlookPage(BasePage):

    def __init__(self, page: Page, config: OutlookOtpConfig):
        super().__init__(page)
        self.config = config

        # Loading and UI elements
        self.loading_logo = page.locator("#loadingLogo")

        # Email time locators
        self.email_time_span = page.locator("//span[@class='_rWRU U2XB8 qq2gS cbNn0']")

        # Message and email locators
        self.message_rows = page.locator("div[role='option']")
        self.mail_body_container = page.locator('[data-test-id="mailMessageBodyContainer"]')

        # Sign-in field locators (multiple fallbacks)
        self.username_field_primary = page.locator("#i0116")
        self.username_field_fallback1 = page.locator("input[name='loginfmt']")
        self.username_field_fallback2 = page.locator("input[type='email']")

        # Password field locators (multiple fallbacks)
        self.password_field_primary = page.locator("#i0118")
        self.password_field_fallback1 = page.locator("input[name='passwd']")
        self.password_field_fallback2 = page.locator("input[type='password']")

        # Sign-in button locators (multiple fallbacks)
        self.signin_button_primary = page.locator("#idSIButton9")
        self.signin_button_fallback1 = page.locator("//input[@type='submit' and @value='Next']")
        self.signin_button_fallback2 = page.locator("//input[@type='submit' and @value='Sign in']")
        self.signin_button_fallback3 = page.locator("button[type='submit']")

        # Stay signed in prompt
        self.stay_signed_in_yes = page.locator("//input[@type='submit' and @value='Yes']")

        # Inbox and search related
        self.inbox_link = page.locator('[aria-label="Inbox"]')
        self.review_document_link = page.get_by_role("link", name="REVIEW DOCUMENT")

    @classmethod
    def from_config(cls, page: Page) -> "OutlookPage":

        email = os.getenv("OUTLOOK_USERNAME", "")
        password = os.getenv("OUTLOOK_PASSWORD", "")
        if not email or not password:
            raise ValueError(
                "Outlook credentials not found. "
                "Set OUTLOOK_USERNAME and OUTLOOK_PASSWORD env vars "
                "(via Key Vault in pipeline, or .env file locally)."
            )
        config = OutlookOtpConfig(email=email, password=password)
        return cls(page=page, config=config)

    # --- Public API -----------------------------------------------------

    def get_otp(
        self, submitting_time: time, max_wait_time_in_seconds: int, parent_page=None
    ) -> Optional[str]:
        """Read OTP from Outlook mail.

        Args:
            submitting_time: Time when 'Send Now' was clicked
            max_wait_time_in_seconds: Maximum time to wait for OTP
            parent_page: Page to bring to front when done (optional)

        Returns the 6-digit OTP as a string, or None if not found.
        """
        logger.info("Starting OTP retrieval from Outlook")
        otp: Optional[str] = None

        try:
            normalized_submitting = datetime.strptime(
                submitting_time.strftime(TIME_FORMAT), TIME_FORMAT
            ).time()
            logger.info(
                f"[OTP_DEBUG] normalized_submitting (Send Now time): {normalized_submitting.strftime(TIME_FORMAT)}"
            )

            # Calculate minimum acceptable email time (allow 2 minutes before Send Now for delivery delays)
            min_acceptable_datetime = datetime.combine(
                datetime.today(), normalized_submitting
            ) - timedelta(minutes=2)
            min_acceptable_time = min_acceptable_datetime.time()
            logger.info(
                f"[OTP_DEBUG] Min acceptable email time (Send Now - 2 min): {min_acceptable_time.strftime(TIME_FORMAT)}"
            )

            received_time = (datetime.now() - timedelta(minutes=10)).time()
            logger.info(
                f"[OTP_DEBUG] Initial received_time (current time - 10 min): {received_time.strftime(TIME_FORMAT)}"
            )

            self.page.bring_to_front()
            self.page.reload(wait_until="domcontentloaded")

            # Click first mail and check its timestamp
            logger.info("[OTP_DEBUG] Clicking first mail to check timestamp...")
            try:
                self.message_rows.first.click()
                self.page.wait_for_timeout(500)
                logger.info("[OTP_DEBUG] Clicked first mail")
            except Exception as ex:
                logger.warning(f"[OTP_DEBUG] Could not click first mail: {ex}")

            # Read timestamp from clicked mail
            mail_time = self._read_latest_mail_time()

            if mail_time is not None:
                logger.info(f"[OTP_DEBUG] First mail timestamp: {mail_time.strftime(TIME_FORMAT)}")
                logger.info(
                    f"[OTP_DEBUG] Comparing: {mail_time.strftime(TIME_FORMAT)} >= {min_acceptable_time.strftime(TIME_FORMAT)}? (tolerance: 2 min before Send Now)"
                )

                if mail_time >= min_acceptable_time:
                    logger.info(
                        "[OTP_DEBUG] First mail timestamp is within acceptable window, extracting OTP..."
                    )
                    otp = self._extract_otp_from_latest_mail()
                    if otp:
                        logger.info(f"[OTP_DEBUG] Successfully extracted OTP: {otp}")
                        return otp
                    else:
                        logger.warning("[OTP_DEBUG] Valid timestamp but no OTP found in body")
                else:
                    logger.info(
                        f"[OTP_DEBUG] First mail timestamp too old ({mail_time.strftime(TIME_FORMAT)} < {min_acceptable_time.strftime(TIME_FORMAT)}), will poll and retry..."
                    )
            else:
                logger.warning(
                    "[OTP_DEBUG] Could not read timestamp from first mail, will poll and retry..."
                )

            # Enter polling retry loop - refresh page and recheck first mail each time
            logger.info("[OTP_DEBUG] Entering polling retry loop...")
            step = 5
            poll_attempt = 0

            for _ in range(0, max_wait_time_in_seconds, step):
                poll_attempt += 1
                logger.info(f"[OTP_DEBUG] Poll attempt #{poll_attempt}")

                # Refresh page to get latest emails
                self.page.reload(wait_until="domcontentloaded")
                self.page.wait_for_timeout(step * 1000)
                logger.info(
                    f"[OTP_DEBUG] Poll #{poll_attempt}: Page refreshed, now navigating to OTP folder..."
                )

                # Navigate back to OTP folder
                try:
                    self._navigate_to_otp_folder()
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Navigated to OTP folder")
                except Exception as ex:
                    logger.warning(
                        f"[OTP_DEBUG] Poll #{poll_attempt}: Error navigating to OTP folder: {ex}"
                    )

                # Click first mail again
                try:
                    self.message_rows.first.click()
                    self.page.wait_for_timeout(500)
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Clicked first mail")
                except Exception as ex:
                    logger.warning(
                        f"[OTP_DEBUG] Poll #{poll_attempt}: Could not click first mail: {ex}"
                    )
                    continue

                # Read timestamp
                mail_time = self._read_latest_mail_time()

                if mail_time is not None:
                    logger.info(
                        f"[OTP_DEBUG] Poll #{poll_attempt}: First mail timestamp: {mail_time.strftime(TIME_FORMAT)}"
                    )
                    logger.info(
                        f"[OTP_DEBUG] Poll #{poll_attempt}: Comparing: {mail_time.strftime(TIME_FORMAT)} >= {min_acceptable_time.strftime(TIME_FORMAT)}? (tolerance: 2 min before Send Now)"
                    )

                    if mail_time >= min_acceptable_time:
                        logger.info(
                            f"[OTP_DEBUG] Poll #{poll_attempt}: Timestamp is within acceptable window, extracting OTP..."
                        )
                        otp = self._extract_otp_from_latest_mail()
                        if otp:
                            logger.info(
                                f"[OTP_DEBUG] Poll #{poll_attempt}: Successfully extracted OTP: {otp}"
                            )
                            return otp
                        else:
                            logger.warning(
                                f"[OTP_DEBUG] Poll #{poll_attempt}: Valid timestamp but no OTP found in body"
                            )
                    else:
                        logger.info(
                            f"[OTP_DEBUG] Poll #{poll_attempt}: Timestamp still outside acceptable window ({mail_time.strftime(TIME_FORMAT)} < {min_acceptable_time.strftime(TIME_FORMAT)}), will retry..."
                        )
                else:
                    logger.warning(
                        f"[OTP_DEBUG] Poll #{poll_attempt}: Could not read timestamp, will retry..."
                    )

                logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Continuing to next attempt...")

        except Exception as ex:  # pragma: no cover - defensive
            otp = None
            self.logger.error(f"Error while fetching OTP through email: {ex}")
            with allure.step("Error while fetching OTP through email"):
                allure.attach(
                    str(ex),
                    name="OTP Fetch Error",
                    attachment_type=allure.attachment_type.TEXT,
                )
        finally:
            try:
                if parent_page is not None:
                    parent_page.bring_to_front()
            except Exception as ex:
                self.logger.error(f"Failed to bring parent_page to front after get_otp: {ex}")

        return otp

    def get_otp_with_retry(
        self,
        timeout: float = 60.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Optional[str]:
        """
        Retrieve OTP from the OTP folder using self.page (already the Outlook email page).

        Args:
            timeout: Total timeout in seconds (default: 60 seconds)
            sent_after_epoch: Filter emails sent after this timestamp (optional)
            preferred_sender: Filter emails from this sender (optional)

        Returns:
            OTP code (6 digits) or None if not found
        """
        try:
            self.page.bring_to_front()
            self.page.reload(wait_until="domcontentloaded")

            # Navigate to OTP folder
            logger.info("[OTP_DEBUG] [get_otp_with_retry] Navigating to OTP folder...")
            self._navigate_to_otp_folder()
            logger.info("[OTP_DEBUG] [get_otp_with_retry] OTP folder navigation completed")

            # Wait a moment for OTP folder to fully render and load emails
            self.page.wait_for_timeout(2000)

            # Wait for the first mail to be present in OTP folder
            try:
                initial_count = self.message_rows.count()
                logger.info(
                    f"[OTP_DEBUG] [get_otp_with_retry] Initial mail count in OTP folder: {initial_count}"
                )

                if initial_count == 0:
                    logger.info(
                        "[OTP_DEBUG] [get_otp_with_retry] No mails found, waiting for mails to appear..."
                    )
                    wait_for_element_count(self.message_rows, count=1, timeout=10.0)
                    logger.info(
                        "[OTP_DEBUG] [get_otp_with_retry] First mail element appeared in OTP folder"
                    )
                else:
                    logger.info(
                        f"[OTP_DEBUG] [get_otp_with_retry] Mails already present ({initial_count}), proceeding..."
                    )

                self.message_rows.first.click()
                logger.info("[OTP_DEBUG] [get_otp_with_retry] Clicked on first mail in OTP folder")
                self.page.wait_for_timeout(1500)
                logger.info(
                    "[OTP_DEBUG] [get_otp_with_retry] Mail loaded and ready for OTP extraction"
                )

            except WaitTimeoutError as ex:
                logger.warning(
                    f"[OTP_DEBUG] [get_otp_with_retry] Timeout waiting for mail in OTP folder: {ex}"
                )
            except Exception as ex:
                logger.warning(
                    f"[OTP_DEBUG] [get_otp_with_retry] Could not click initial mail: {ex}"
                )

            otp = self.get_otp(
                submitting_time=datetime.now().time(),
                max_wait_time_in_seconds=int(timeout),
            )

            if otp:
                logger.info(f"Successfully retrieved OTP from OTP folder in Outlook: {otp}")
                return otp
            else:
                logger.error(f"Failed to retrieve OTP from OTP folder within {int(timeout)}s")
                return None

        except Exception as e:
            logger.error(f"Error in OTP retrieval workflow: {str(e).splitlines()[0]}")
            return None

    def _navigate_to_otp_folder(self) -> None:
        """Navigate to the OTP folder in Outlook using self.page."""
        try:
            otp_folder_locators = [
                self.page.get_by_text("OTP", exact=False).first,
                self.page.get_by_role("link", name=re.compile(r"OTP", re.I)),
                self.page.locator('[aria-label*="OTP"]').first,
                self.page.locator('//span[contains(text(), "OTP")]').first,
                self.page.locator('[role="treeitem"][aria-label*="OTP"]').first,
            ]

            otp_folder_clicked = False
            for locator in otp_folder_locators:
                try:
                    locator.wait_for(state="visible", timeout=3_000)
                    locator.click()
                    otp_folder_clicked = True
                    logger.info("Successfully navigated to OTP folder in Outlook.")
                    self.page.wait_for_load_state("domcontentloaded", timeout=10_000)
                    break
                except PlaywrightTimeoutError:
                    continue
                except Exception as ex:
                    logger.warning(f"Error while trying OTP folder locator: {ex}")
                    continue

            if not otp_folder_clicked:
                logger.warning("Could not find OTP folder; proceeding with current view")

        except Exception as ex:
            logger.error(f"Error while navigating to OTP folder: {ex}")
            raise

    # --- Internal helpers -----------------------------------------------

    def handle_sign_in(self) -> bool:
        """Handle Outlook sign-in page if it is currently shown.

        Returns ``True`` if either no sign-in was required (already signed in)
        or the username/password flow completed without errors.
        Returns ``False`` if required login elements could not be found.
        """
        try:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass

            try:
                self.page.title().lower()
            except Exception as ex:
                self.logger.warning(f"Outlook sign-in: unable to read page title: {ex}")

            username_locators = [
                self.username_field_primary,
                self.username_field_fallback1,
                self.username_field_fallback2,
            ]
            password_locators = [
                self.password_field_primary,
                self.password_field_fallback1,
                self.password_field_fallback2,
            ]
            next_button_locators = [
                self.signin_button_primary,
                self.signin_button_fallback1,
                self.signin_button_fallback2,
                self.signin_button_fallback3,
            ]

            def _first_visible(locators, timeout_ms: int):
                for loc in locators:
                    try:
                        loc.wait_for(state="visible", timeout=timeout_ms)
                        return loc
                    except PlaywrightTimeoutError:
                        continue
                    except Exception as ex_inner:
                        self.logger.warning(
                            f"Outlook sign-in: error while probing locator; continuing: {ex_inner}"
                        )
                return None

            inbox_locators = [
                self.page.get_by_text("Inbox").first,
                self.page.get_by_role("link", name=re.compile(r"^Inbox$", re.I)),
                self.inbox_link,
            ]
            if _first_visible(inbox_locators, 3_000) is not None:
                self.logger.info(
                    "Outlook sign-in: Inbox UI visible; assuming session already signed in."
                )
                return True

            if (
                _first_visible(username_locators, 5_000) is None
                and _first_visible(password_locators, 5_000) is None
            ):
                self.logger.info(
                    "Outlook sign-in: no username or password fields visible; "
                    "assuming session already signed in."
                )
                return True

            try:
                user_id_locator = _first_visible(username_locators, 20_000)
                if not user_id_locator:
                    self.logger.error(
                        "Outlook sign-in: could not find a visible username/email input."
                    )
                    return False
                else:
                    self.logger.info("Outlook sign-in: filling username/email field.")
                    user_id_locator.fill(self.config.email)

                next_button = _first_visible(next_button_locators, 20_000)
                if next_button:
                    self.logger.info(
                        "Outlook sign-in: clicking Next/Sign in button after username."
                    )
                    next_button.click()
                else:
                    self.logger.error(
                        "Outlook sign-in: could not find Next/Sign in button after username entry."
                    )
                    return False
            except Exception as ex:
                self.logger.error(f"Error while entering Outlook username: {ex}")
                return False

            try:
                try:
                    enter_pwd_heading = self.page.get_by_role(
                        "heading", name=re.compile("Enter password", re.I)
                    )
                    enter_pwd_heading.wait_for(state="visible", timeout=20_000)
                    self.logger.info(
                        "Outlook sign-in: 'Enter password' heading is visible; locating password field."
                    )
                except PlaywrightTimeoutError:
                    self.logger.info(
                        "Outlook sign-in: 'Enter password' heading not visible within timeout; probing password field directly."
                    )
                except Exception as heading_ex:
                    self.logger.warning(
                        f"Outlook sign-in: error while waiting for 'Enter password' heading; continuing: {heading_ex}"
                    )

                password_locator = _first_visible(password_locators, 20_000)
                if not password_locator:
                    self.logger.error("Outlook sign-in: could not find a visible password input.")
                    return False

                try:
                    password_locator.wait_for(state="visible", timeout=10_000)
                except Exception as wait_ex:
                    self.logger.error(
                        f"Outlook sign-in: password input did not become visible in time: {wait_ex}"
                    )
                    return False

                self.logger.info("Outlook sign-in: filling password field.")
                password_locator.fill(self.config.password)

                sign_in_button = _first_visible(next_button_locators, 20_000)
                if sign_in_button:
                    self.logger.info("Outlook sign-in: clicking Sign in button after password.")
                    sign_in_button.click()
                else:
                    self.logger.error(
                        "Outlook sign-in: could not find Sign in button after password entry."
                    )
                    return False

                try:
                    self.stay_signed_in_yes.wait_for(state="visible", timeout=5_000)
                    self.stay_signed_in_yes.click()
                except (PlaywrightTimeoutError, Exception) as ex:
                    self.logger.error(f"Error while handling 'Stay signed in' prompt: {ex}")
                return True
            except (PlaywrightTimeoutError, Exception) as ex:
                self.logger.error(f"Error while entering Outlook password: {ex}")
                return False
        except Exception as ex:
            self.logger.error(f"Unexpected error in handle_sign_in: {ex}")
            return False

    def _read_latest_mail_time(self) -> Optional[time]:
        """Read the timestamp of the currently clicked email in Outlook.

        Locates the timestamp element for the clicked mail and parses it to a time object.
        Waits for the timestamp element to be present before attempting to read.

        Returns:
            time object if successfully parsed, None if not found or parsing fails
        """
        logger.info("[OTP_DEBUG] [_read_latest_mail_time] Starting to read clicked email timestamp")
        logger.info(
            f"[OTP_DEBUG] [_read_latest_mail_time] Using locator: //div[@data-testid='SentReceivedSavedTime'] (first instance)"
        )
        logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Expected TIME_FORMAT: {TIME_FORMAT}")

        # Use the first SentReceivedSavedTime element which is the clicked mail's timestamp
        time_elements = self.page.locator("//div[@data-testid='SentReceivedSavedTime']")

        try:
            # Wait for timestamp element to be present (at least 1)
            logger.info(
                "[OTP_DEBUG] [_read_latest_mail_time] Waiting for timestamp element to appear..."
            )
            wait_for_element_count(time_elements, count=1, timeout=10.0)
            logger.info("[OTP_DEBUG] [_read_latest_mail_time] Timestamp element is now present")

            element_count = time_elements.count()
            logger.info(
                f"[OTP_DEBUG] [_read_latest_mail_time] Found {element_count} timestamp element(s)"
            )

            if element_count > 0:
                logger.info(
                    "[OTP_DEBUG] [_read_latest_mail_time] Reading inner text from first element"
                )
                full_text = time_elements.first.inner_text().strip()
                logger.info(
                    f"[OTP_DEBUG] [_read_latest_mail_time] Raw timestamp text: '{full_text}'"
                )

                # Extract just the time portion (e.g., "1:40 AM" from "Tue 3/31/2026 1:40 AM")
                time_match = re.search(r"(\d{1,2}:\d{2}\s(?:AM|PM))", full_text)
                if time_match:
                    time_str = time_match.group(1)
                    logger.info(
                        f"[OTP_DEBUG] [_read_latest_mail_time] Extracted time portion: '{time_str}'"
                    )

                    parsed_time = datetime.strptime(time_str, TIME_FORMAT).time()
                    logger.info(
                        f"[OTP_DEBUG] [_read_latest_mail_time] Successfully parsed to time object: {parsed_time.strftime(TIME_FORMAT)}"
                    )
                    return parsed_time
                else:
                    logger.error(
                        f"[OTP_DEBUG] [_read_latest_mail_time] Could not extract time pattern from text: '{full_text}'"
                    )
            else:
                logger.warning(
                    "[OTP_DEBUG] [_read_latest_mail_time] No timestamp elements found on page"
                )

        except WaitTimeoutError as ex:
            logger.error(
                f"[OTP_DEBUG] [_read_latest_mail_time] Timeout waiting for timestamp element: {ex}"
            )
            logger.warning(
                "[OTP_DEBUG] [_read_latest_mail_time] Timestamp element did not appear within timeout"
            )
        except ValueError as ex:
            self.logger.error(
                f"[OTP_DEBUG] [_read_latest_mail_time] ValueError parsing timestamp - invalid format: {ex}"
            )
            logger.info(
                f"[OTP_DEBUG] [_read_latest_mail_time] Raw text was: '{time_elements.first.inner_text().strip() if time_elements.count() > 0 else 'N/A'}'"
            )
            with allure.step("Failed to parse mail time - invalid format"):
                pass
        except Exception as ex:
            self.logger.error(
                f"[OTP_DEBUG] [_read_latest_mail_time] Unexpected error reading/parsing mail time: {type(ex).__name__}: {ex}"
            )
            with allure.step("Unexpected error parsing mail time"):
                pass

        logger.warning(
            "[OTP_DEBUG] [_read_latest_mail_time] Could not retrieve/parse latest email time; returning None"
        )
        return None

    def _extract_otp_from_latest_mail(self) -> Optional[str]:
        message_rows = self.page.locator("div[role='option']").filter(
            has_text=re.compile("Docusign verification", re.I)
        )

        if message_rows.count() == 0:
            return None

        message_rows.first.click()

        body_container = self.mail_body_container.first
        try:
            body_container.wait_for(state="visible", timeout=10_000)
            otp_text = body_container.inner_text()
        except PlaywrightTimeoutError as ex:
            self.logger.error(f"Timeout while reading OTP body text from mail body container: {ex}")
            return None
        except Exception as ex:
            # Catch any other unexpected Playwright or locator errors here
            self.logger.error(
                f"Unexpected error while reading OTP body text from mail body container: {ex}"
            )
            return None

        match = re.search(r"\b\d{6}\b", otp_text)
        if match:
            return match.group(0)

        # Body text was found but did not contain a 6-digit OTP
        self.logger.error(
            f"Email body did not contain a valid 6-digit OTP. Body text: {otp_text!r}"
        )
        return None

    def _click_inbox_search_and_select(
        self,
        search_text: str,
        retries: int = 1,
        subject: Optional[str] = None,
        body: Optional[str] = None,
    ) -> None:
        """Click Inbox, run the search_text search, and open a result.

        Uses self.page (the Outlook email page) for all interactions.
        """

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                if attempt > 0:
                    try:
                        self.logger.info(
                            "Outlook Inbox/search: reloading page before retry attempt "
                            f"{attempt + 1} of {retries}."
                        )
                        self.page.reload(wait_until="domcontentloaded")
                    except Exception as reload_ex:
                        self.logger.warning(
                            f"Outlook Inbox/search: error while reloading before retry: {reload_ex}"
                        )

                self.logger.info(
                    f"Outlook Inbox/search attempt {attempt + 1} of {retries} for search text: {search_text!r}."
                )

                inbox_clicked = False
                inbox_locators = [
                    self.page.get_by_text("Inbox").first,
                    self.page.get_by_role("link", name=re.compile(r"^Inbox$", re.I)),
                    self.inbox_link,
                ]

                for locator in inbox_locators:
                    try:
                        locator.wait_for(state="visible", timeout=2_000)
                        locator.click()
                        inbox_clicked = True
                        self.logger.info("Clicked Inbox folder in Outlook.")
                        break
                    except PlaywrightTimeoutError:
                        continue
                    except Exception as ex:
                        self.logger.warning(
                            f"Error while trying to click Inbox locator; continuing: {ex}"
                        )

                if not inbox_clicked:
                    self.logger.warning(
                        "Could not explicitly click Inbox; proceeding to search across all mail."
                    )

                search_box = None
                search_locators = [
                    self.page.get_by_role("combobox", name=re.compile("search", re.I)),
                    self.page.get_by_role("textbox", name=re.compile("search", re.I)),
                    self.page.locator('[role="searchbox"]'),
                    self.page.locator('[aria-label="Search"]'),
                    self.page.locator('input[type="search"]'),
                ]

                for locator in search_locators:
                    try:
                        locator.wait_for(state="visible", timeout=2_000)
                        search_box = locator
                        self.logger.info(
                            f"Outlook search: using located search input for search text: {search_text!r}."
                        )
                        break
                    except PlaywrightTimeoutError:
                        continue
                    except Exception as ex:
                        self.logger.warning(
                            f"Outlook search: error while probing search box locator; continuing: {ex}"
                        )

                if not search_box:
                    raise RuntimeError("Outlook search: could not locate a visible search box.")

                search_box.fill(search_text)
                search_box.press("Enter")

                results = self.message_rows
                self.page.wait_for_timeout(2_000)
                count = results.count()
                if count == 0:
                    raise RuntimeError(
                        f"Outlook search: no email rows found after searching for {search_text!r}."
                    )
                self.logger.info(
                    f"Outlook search: found {count} email row(s) after searching for {search_text!r}."
                )

                candidate_rows = results
                if subject:
                    try:
                        subject_rows = results.filter(has_text=re.compile(re.escape(subject), re.I))
                        if subject_rows.count() > 0:
                            self.logger.info(
                                f"Outlook search: restricting candidates to email rows matching subject {subject!r}."
                            )
                            candidate_rows = subject_rows
                        else:
                            self.logger.warning(
                                f"Outlook search: no email row matched subject {subject!r}; using all search results."
                            )
                    except Exception as subject_ex:
                        self.logger.warning(
                            f"Outlook search: error filtering by subject {subject!r}: {subject_ex}"
                        )

                if body:
                    body_pattern = re.compile(re.escape(body), re.I)
                    candidate_count = candidate_rows.count()
                    self.logger.info(
                        "Outlook search: scanning up to %d candidate email(s) for body text %r.",
                        candidate_count,
                        body,
                    )

                    for idx in range(candidate_count):
                        row = candidate_rows.nth(idx)
                        try:
                            row.click()
                            self.mail_body_container.first.wait_for(state="visible", timeout=10_000)
                            email_body_text = self.mail_body_container.first.inner_text()

                            if body_pattern.search(email_body_text or ""):
                                self.logger.info(
                                    "Outlook search: found email whose body contains the requested text."
                                )
                                return

                            self.logger.info(
                                "Outlook search: candidate email %d/%d did not contain requested body text; continuing.",
                                idx + 1,
                                candidate_count,
                            )
                        except Exception as body_ex:
                            self.logger.warning(
                                f"Outlook search: error while checking email body for candidate {idx + 1}/{candidate_count}: {body_ex}"
                            )

                    raise RuntimeError(
                        f"Outlook search: no email in search results contained the requested body text {body!r}."
                    )

                candidate_rows.first.click()
                self.logger.info(
                    "Outlook search: clicking first email row from candidate search results."
                )
                return

            except Exception as ex:
                last_error = ex
                self.logger.warning(
                    f"Outlook Inbox/search attempt {attempt + 1} of {retries} failed; "
                    f"will retry if attempts remain: {ex}"
                )

        if last_error is not None:
            raise last_error

    def search_authorized_signer_email(
        self,
        search_text: str,
        subject: str = "Electronic Signature",
        body: str = "Please review and sign the document electronically",
    ) -> None:
        """Search for authorized signer email using D-number with subject and body filters."""
        try:
            self._click_inbox_search_and_select(
                search_text,
                retries=10,
                subject=subject,
                body=body,
            )
            logger.info(
                f"Successfully searched and opened authorized signer email for D-number: {search_text}"
            )
        except Exception as ex:
            self.logger.error(f"Error while searching email: {ex}")
            raise

    def fetch_authorized_signer_email_subject_and_body(self, d_number: str) -> tuple[str, str]:
        """Fetch and return the authorized signer email subject and body content separately."""
        try:
            subject_element = self.page.locator(
                '//div[contains(@id,"SUBJECT")]/descendant::span[1]'
            )
            try:
                subject_element.wait_for(state="visible", timeout=5_000)
                subject_text = subject_element.inner_text()
            except PlaywrightTimeoutError:
                raise RuntimeError(
                    f"Email subject element not found or not visible for D-number: {d_number}"
                )

            self.logger.info(f"Fetched Email Subject: {subject_text}")

            body_container = self.page.locator('//div[@data-test-id="mailMessageBodyContainer"]')
            try:
                body_container.wait_for(state="visible", timeout=10_000)
                body_text = self.page.locator(
                    '//div[@data-test-id="mailMessageBodyContainer"]/descendant::table[@role="presentation"][1]/descendant::table[1]/tbody/tr[3]/td/span'
                ).first.inner_text()
            except PlaywrightTimeoutError:
                raise RuntimeError("Email body container not found or not visible")

            self.logger.info("Fetched Email Body successfully")

            with allure.step(f"Email content fetched for D-number: {d_number}"):
                allure.attach(
                    subject_text, name="Email Subject", attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    body_text[:1000],
                    name="Email Body Content",
                    attachment_type=allure.attachment_type.TEXT,
                )

            return (subject_text, body_text)

        except Exception as ex:
            self.logger.error(f"Error while fetching email content: {ex}")
            raise

    def click_review_document_link(self) -> Page:
        """Click the 'REVIEW DOCUMENT' link in the authorized signer email.

        Returns:
            Page: The new DocuSign page that opens after clicking
        """
        try:
            # Outlook ATP may block external email content (shows "Show blocked content").
            # We must unblock it before clicking REVIEW DOCUMENT, otherwise the link
            # href resolves to null and the popup navigates to a safelink error page.
            self._unblock_email_content_if_needed()

            with self.page.expect_popup() as popup_info:
                review_link = self.page.get_by_role("link", name="REVIEW DOCUMENT")
                review_link.wait_for(state="visible", timeout=10_000)
                self.logger.info("Clicking 'REVIEW DOCUMENT' link in authorized signer email")
                review_link.click()

            docusign_page = popup_info.value
            # Wait for the safelink redirect to resolve to DocuSign
            try:
                docusign_page.wait_for_url(re.compile(r"docusign", re.I), timeout=20_000)
            except Exception:
                self.logger.warning("DocuSign URL not detected after popup; proceeding anyway")
            self.logger.info("✓ successfully clicked 'REVIEW DOCUMENT' link, DocuSign page opened")
            return docusign_page

        except Exception as ex:
            self.logger.error(f"Error while clicking Review Document link: {ex}")
            raise

    def _unblock_email_content_if_needed(self) -> None:
        """Click 'Show blocked content' in Outlook if ATP has blocked the email body.

        When an external sender is not in the Safe Senders list, Outlook blocks
        embedded content and the REVIEW DOCUMENT link href becomes null.
        Clicking 'Show blocked content' loads the real link URLs.
        """
        try:
            blocked_content_btn = self.page.get_by_role(
                "button", name=re.compile("show blocked content", re.I)
            )
            blocked_content_btn.wait_for(state="visible", timeout=3_000)
            blocked_content_btn.click()
            self.logger.info("Clicked 'Show blocked content' to unblock email body")
            self.page.wait_for_timeout(2_000)
        except Exception:
            # Button not present — content is already visible, no action needed
            pass
