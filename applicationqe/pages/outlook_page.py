from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from locators.oam import outlook_locators
from pages.oam.base_page import BasePage
from utils.credential_encrypter import decrypt
from utils.allure_logger import get_allure_logger
from utils.wait_utils import wait_for_element_count, WaitTimeoutError

if TYPE_CHECKING:
    from pages.oam.docusign_page import DocuSignPage

logger = get_allure_logger(__name__)

TIME_FORMAT = "%I:%M %p"  # corresponds to pattern "h:m a"


@dataclass
class OutlookOtpConfig:
    mail_field1: str
    mail_field2: str
    secret_key: str


class OutlookPage(BasePage):
    """Page Object for handling OTP retrieval from Outlook webmail.

    Usage example (sync Playwright):

        page2 = context.new_page()
        otp_page = OutlookPage.from_config(page2)
        otp = otp_page.get_otp(submitting_time=datetime.now().time(), max_wait_time_in_seconds=60)
    """

    OUTLOOK_URL = outlook_locators.OUTLOOK_URL
    
    # Import locators from locators module
    LOADING_LOGO = outlook_locators.LOADING_LOGO
    EMAIL_TIME_SPAN = outlook_locators.EMAIL_TIME_SPAN
    MESSAGE_ROWS = outlook_locators.MESSAGE_ROWS
    MAIL_BODY_CONTAINER = outlook_locators.MAIL_BODY_CONTAINER
    USERNAME_FIELD_PRIMARY = outlook_locators.USERNAME_FIELD_PRIMARY
    USERNAME_FIELD_FALLBACK1 = outlook_locators.USERNAME_FIELD_FALLBACK1
    USERNAME_FIELD_FALLBACK2 = outlook_locators.USERNAME_FIELD_FALLBACK2
    PASSWORD_FIELD_PRIMARY = outlook_locators.PASSWORD_FIELD_PRIMARY
    PASSWORD_FIELD_FALLBACK1 = outlook_locators.PASSWORD_FIELD_FALLBACK1
    PASSWORD_FIELD_FALLBACK2 = outlook_locators.PASSWORD_FIELD_FALLBACK2
    SIGNIN_BUTTON_PRIMARY = outlook_locators.SIGNIN_BUTTON_PRIMARY
    SIGNIN_BUTTON_FALLBACK1 = outlook_locators.SIGNIN_BUTTON_FALLBACK1
    SIGNIN_BUTTON_FALLBACK2 = outlook_locators.SIGNIN_BUTTON_FALLBACK2
    SIGNIN_BUTTON_FALLBACK3 = outlook_locators.SIGNIN_BUTTON_FALLBACK3
    STAY_SIGNED_IN_YES = outlook_locators.STAY_SIGNED_IN_YES
    INBOX_LINK_LABEL = outlook_locators.INBOX_LINK_LABEL

    def __init__(self, page: Page, config: OutlookOtpConfig):
        # Initialize BasePage (logging, auto-healing, etc.)
        super().__init__(page)
        self.context = page.context
        self.config = config

    @classmethod
    def from_config(
        cls,
        page: Page,
        config_path: Optional[Path] = None,
    ) -> "OutlookPage":
        """Factory method to create OutlookPage instance from encrypted credentials.
        
        Loads credentials from the environment configuration file (env.{env}.yaml)
        instead of an external config.yaml file.
        
        Args:
            page: Playwright Page instance
            config_path: Deprecated - kept for backward compatibility, ignored
        
        Returns:
            OutlookPage: Configured instance with decrypted credentials
            
        Raises:
            ValueError: If secret_key or encrypted credentials not found in config
        """
        from config.settings import get_settings
        
        settings = get_settings()
        
        # Get values from environment configuration (env.test11.yaml, etc.)
        secret_key = str(settings.secret_key or "")
        if not secret_key:
            raise ValueError(
                f"secret_key not found in env.{settings.env}.yaml. "
                "Add 'secret_key: <16-or-32-byte-key>' to your environment config."
            )
        
        encrypted_email = str(settings.outlook_email or "")
        encrypted_password = str(settings.outlook_password or "")
        if not encrypted_email or not encrypted_password:
            raise ValueError(
                f"Outlook credentials not found in env.{settings.env}.yaml. "
                "Add email.outlook.email_address and email.outlook.password to your environment config."
            )
        
        # Decrypt credentials
        field1 = decrypt(encrypted_email, secret_key)
        field2 = decrypt(encrypted_password, secret_key)
        
        config = OutlookOtpConfig(mail_field1=field1, mail_field2=field2, secret_key=secret_key)
        return cls(page=page, config=config)

    # --- Public API -----------------------------------------------------

    def get_otp(self, submitting_time: time, max_wait_time_in_seconds: int, parent_page = None, email_page: Optional[Page] = None) -> Optional[str]:
        """Read OTP from Outlook mail.

        Args:
            submitting_time: Time when 'Send Now' was clicked
            max_wait_time_in_seconds: Maximum time to wait for OTP
            parent_page: Parent page to bring to front when done
            email_page: Outlook page (if None, will create new one; if provided, won't close it)

        Returns the 6-digit OTP as a string, or None if not found.
        """
        logger.info("Starting OTP retrieval from Outlook")
        otp: Optional[str] = None
        page_created_locally = False

        try:
            normalized_submitting = datetime.strptime(
                submitting_time.strftime(TIME_FORMAT), TIME_FORMAT
            ).time()
            logger.info(f"[OTP_DEBUG] normalized_submitting (Send Now time): {normalized_submitting.strftime(TIME_FORMAT)}")

            # Calculate minimum acceptable email time (allow 2 minutes before Send Now for delivery delays)
            min_acceptable_datetime = datetime.combine(datetime.today(), normalized_submitting) - timedelta(minutes=2)
            min_acceptable_time = min_acceptable_datetime.time()
            logger.info(f"[OTP_DEBUG] Min acceptable email time (Send Now - 2 min): {min_acceptable_time.strftime(TIME_FORMAT)}")

            received_time = (datetime.now() - timedelta(minutes=10)).time()
            logger.info(f"[OTP_DEBUG] Initial received_time (current time - 10 min): {received_time.strftime(TIME_FORMAT)}")

            if email_page is None:
                # Use centralized login function
                email_page = self.login_outlook(context_message="OTP retrieval")
                page_created_locally = True
                logger.info("[OTP_DEBUG] Created new Outlook page in get_otp()")
            else:
                logger.info("[OTP_DEBUG] Using provided Outlook page in get_otp()")
                email_page.bring_to_front()
                # Avoid strict networkidle here as well; a simple reload with
                # DOM content loaded is sufficient for updated inbox content.
                email_page.reload(wait_until="domcontentloaded")

            # Click first mail and check its timestamp
            logger.info("[OTP_DEBUG] Clicking first mail to check timestamp...")
            try:
                first_mail = email_page.locator("div[role='option']").first
                first_mail.click()
                email_page.wait_for_timeout(500)
                logger.info("[OTP_DEBUG] Clicked first mail")
            except Exception as ex:
                logger.warning(f"[OTP_DEBUG] Could not click first mail: {ex}")
            
            # Read timestamp from clicked mail
            mail_time = self._read_latest_mail_time(email_page)
            
            if mail_time is not None:
                logger.info(f"[OTP_DEBUG] First mail timestamp: {mail_time.strftime(TIME_FORMAT)}")
                logger.info(f"[OTP_DEBUG] Comparing: {mail_time.strftime(TIME_FORMAT)} >= {min_acceptable_time.strftime(TIME_FORMAT)}? (tolerance: 2 min before Send Now)")
                
                if mail_time >= min_acceptable_time:
                    logger.info("[OTP_DEBUG] First mail timestamp is within acceptable window, extracting OTP...")
                    otp = self._extract_otp_from_latest_mail(email_page)
                    if otp:
                        logger.info(f"[OTP_DEBUG] Successfully extracted OTP: {otp}")
                        return otp
                    else:
                        logger.warning("[OTP_DEBUG] Valid timestamp but no OTP found in body")
                else:
                    logger.info(f"[OTP_DEBUG] First mail timestamp too old ({mail_time.strftime(TIME_FORMAT)} < {min_acceptable_time.strftime(TIME_FORMAT)}), will poll and retry...")
            else:
                logger.warning("[OTP_DEBUG] Could not read timestamp from first mail, will poll and retry...")
            
            # Enter polling retry loop - refresh page and recheck first mail each time
            logger.info("[OTP_DEBUG] Entering polling retry loop...")
            step = 5
            poll_attempt = 0
            
            for _ in range(0, max_wait_time_in_seconds, step):
                poll_attempt += 1
                logger.info(f"[OTP_DEBUG] Poll attempt #{poll_attempt}")
                
                # Refresh page to get latest emails
                email_page.reload(wait_until="domcontentloaded")
                email_page.wait_for_timeout(step * 1000)
                logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Page refreshed, now navigating to OTP folder...")
                
                # Navigate back to OTP folder
                try:
                    self._navigate_to_otp_folder(email_page)
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Navigated to OTP folder")
                except Exception as ex:
                    logger.warning(f"[OTP_DEBUG] Poll #{poll_attempt}: Error navigating to OTP folder: {ex}")
                
                # Click first mail again
                try:
                    first_mail = email_page.locator("div[role='option']").first
                    first_mail.click()
                    email_page.wait_for_timeout(500)
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Clicked first mail")
                except Exception as ex:
                    logger.warning(f"[OTP_DEBUG] Poll #{poll_attempt}: Could not click first mail: {ex}")
                    continue
                
                # Read timestamp
                mail_time = self._read_latest_mail_time(email_page)
                
                if mail_time is not None:
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: First mail timestamp: {mail_time.strftime(TIME_FORMAT)}")
                    logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Comparing: {mail_time.strftime(TIME_FORMAT)} >= {min_acceptable_time.strftime(TIME_FORMAT)}? (tolerance: 2 min before Send Now)")
                    
                    if mail_time >= min_acceptable_time:
                        logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Timestamp is within acceptable window, extracting OTP...")
                        otp = self._extract_otp_from_latest_mail(email_page)
                        if otp:
                            logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Successfully extracted OTP: {otp}")
                            return otp
                        else:
                            logger.warning(f"[OTP_DEBUG] Poll #{poll_attempt}: Valid timestamp but no OTP found in body")
                    else:
                        logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Timestamp still outside acceptable window ({mail_time.strftime(TIME_FORMAT)} < {min_acceptable_time.strftime(TIME_FORMAT)}), will retry...")
                else:
                    logger.warning(f"[OTP_DEBUG] Poll #{poll_attempt}: Could not read timestamp, will retry...")
                
                logger.info(f"[OTP_DEBUG] Poll #{poll_attempt}: Continuing to next attempt...")

        except Exception as ex:  # pragma: no cover - defensive
            otp = None
            # Log the exception and attach details to Allure
            self.logger.error(f"Error while fetching OTP through email: {ex}")
            with allure.step("Error while fetching OTP through email"):
                allure.attach(
                    str(ex),
                    name="OTP Fetch Error",
                    attachment_type=allure.attachment_type.TEXT,
                )
        finally:
            # Only close the page if we created it locally
            # If page was provided by caller, don't close it - let them manage its lifecycle
            if page_created_locally and email_page is not None:
                try:
                    email_page.close()
                    logger.info("[OTP_DEBUG] Closed locally-created Outlook page")
                except Exception as ex:
                    logger.warning(f"[OTP_DEBUG] Failed to close page: {ex}")
            
            # Focus back to original page
            try:
                if parent_page is not None:
                    parent_page.bring_to_front()
            except Exception as ex:
                self.logger.error(f"Failed to bring parent_page to front after get_otp: {ex}")

        return otp

    def get_otp_with_retry(
        self,
        email: str = None,
        password: str = None,
        timeout: float = 60.0,
        refresh_interval: float = 5.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
        outlook_page: Optional[Page] = None,
    ) -> Optional[str]:
        """
        Complete Outlook workflow to retrieve OTP from OTP folder with time-based refresh.
        
        This method:
        1. Uses provided Outlook page OR logs in to create new one
        2. Navigates to the OTP folder
        3. Waits for and retrieves the OTP email from OTP folder only
        4. Refreshes page every 5 seconds for up to 1 minute to ensure latest OTP is fetched
        
        Args:
            email: Email address for login (optional, uses config if not provided)
            password: Email password (optional, uses config if not provided)
            timeout: Total timeout in seconds (default: 60 seconds)
            refresh_interval: Interval between page refreshes in seconds (default: 5 seconds)
            sent_after_epoch: Filter emails sent after this timestamp (optional)
            preferred_sender: Filter emails from this sender (optional)
            outlook_page: Existing Outlook page to use (optional). If provided, uses this instead of creating new one.
            
        Returns:
            OTP code (6 digits) or None if not found
        """
        email_page = outlook_page
        page_created_locally = False
        
        try:
            # Use provided page or create a new one
            if email_page is None:
                email_page = self.login_outlook(context_message="OTP retrieval with retry")
                page_created_locally = True
                logger.info("Created new Outlook page for OTP retrieval")
            else:
                logger.info("Using provided Outlook page for OTP retrieval")
                # Ensure the provided page is visible and ready
                email_page.bring_to_front()
                email_page.reload(wait_until="domcontentloaded")
            
            # Navigate to OTP folder
            logger.info("[OTP_DEBUG] [get_otp_with_retry] Navigating to OTP folder...")
            self._navigate_to_otp_folder(email_page)
            logger.info("[OTP_DEBUG] [get_otp_with_retry] OTP folder navigation completed")
            
            # Wait a moment for OTP folder to fully render and load emails
            email_page.wait_for_timeout(2000)
            
            # Wait for the first mail to be present in OTP folder
            try:
                mail_locator = email_page.locator("div[role='option']")
                initial_count = mail_locator.count()
                logger.info(f"[OTP_DEBUG] [get_otp_with_retry] Initial mail count in OTP folder: {initial_count}")
                
                # If no mails yet, wait for at least one to appear
                if initial_count == 0:
                    logger.info("[OTP_DEBUG] [get_otp_with_retry] No mails found, waiting for mails to appear...")
                    wait_for_element_count(mail_locator, count=1, timeout=10.0)
                    logger.info("[OTP_DEBUG] [get_otp_with_retry] First mail element appeared in OTP folder")
                else:
                    logger.info(f"[OTP_DEBUG] [get_otp_with_retry] Mails already present ({initial_count}), proceeding...")
                
                # Click on the first/initial mail in the OTP folder to load it
                first_mail = mail_locator.first
                first_mail.click()
                logger.info("[OTP_DEBUG] [get_otp_with_retry] Clicked on first mail in OTP folder")
                email_page.wait_for_timeout(1500)  # Brief wait for mail to load
                logger.info("[OTP_DEBUG] [get_otp_with_retry] Mail loaded and ready for OTP extraction")
                
            except WaitTimeoutError as ex:
                logger.warning(f"[OTP_DEBUG] [get_otp_with_retry] Timeout waiting for mail in OTP folder: {ex}")
                logger.warning("[OTP_DEBUG] [get_otp_with_retry] OTP folder may be empty or locator may be incorrect")
            except Exception as ex:
                logger.warning(f"[OTP_DEBUG] [get_otp_with_retry] Could not click initial mail: {ex}")
            
            # Retrieve OTP from OTP folder using the working get_otp() method
            otp = self.get_otp(
                submitting_time=datetime.now().time(),
                max_wait_time_in_seconds=int(timeout),
                email_page=email_page
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
        finally:
            # Only close the page if we created it locally
            # If a page was provided, don't close it - let the caller manage its lifecycle
            if page_created_locally and email_page is not None:
                try:
                    email_page.close()
                    logger.info("Closed locally created Outlook page")
                except Exception:
                    pass


    def login_outlook(self, context_message: str = "Outlook login") -> Page:
        """Login to Outlook and wait for the inbox to load.
        
        This is a centralized login function that handles:
        - Opening a new page to Outlook
        - Navigating to OUTLOOK_URL
        - Handling sign-in if needed
        - Waiting for loading logo to disappear
        
        Args:
            context_message: Description of what we're logging in for (used in error messages)
            
        Returns:
            Page: The authenticated Outlook page
            
        Raises:
            RuntimeError: If sign-in fails
        """
        outlook_email_page = self.context.new_page()
        try:
            # Global fixtures define viewport/window size; do not override here.
            # Use a lighter DOM load wait instead of networkidle to avoid
            # Outlook SPA timeouts.
            outlook_email_page.goto(self.OUTLOOK_URL, wait_until="domcontentloaded")

            # Sign-in flow if needed; if this fails, do not
            # continue with inbox/search as if authenticated.
            if not self._handle_sign_in_if_needed(outlook_email_page):
                raise RuntimeError(
                    f"Outlook sign-in did not complete successfully for {context_message}."
                )

            # Try to wait for the loading logo to disappear if present
            loading_logo = outlook_email_page.locator("#loadingLogo")
            try:
                loading_logo.wait_for(state="hidden", timeout=10_000)
            except PlaywrightTimeoutError as ex:
                # Not critical; log and continue
                self.logger.error(f"loadingLogo did not disappear within timeout ({context_message}): {ex}")
                with allure.step(
                    "loadingLogo did not disappear within timeout; continuing"
                ):
                    pass
        except Exception:
            # If something failed during login, close the page and re-raise
            try:
                outlook_email_page.close()
            except Exception:
                pass
            raise

        return outlook_email_page

    def _navigate_to_otp_folder(self, email_page: Page) -> None:
        """Navigate to the OTP folder in Outlook.
        
        Clicks on the OTP folder in the folder pane to view emails in that folder.
        
        Args:
            email_page: The authenticated Outlook page
            
        Raises:
            Exception: If OTP folder cannot be found or clicked
        """
        try:
            # Try to find and click the OTP folder using multiple strategies
            otp_folder_locators = [
                email_page.get_by_text("OTP", exact=False).first,
                email_page.get_by_role("link", name=re.compile(r"OTP", re.I)),
                email_page.locator('[aria-label*="OTP"]').first,
                email_page.locator('//span[contains(text(), "OTP")]').first,
                email_page.locator('[role="treeitem"][aria-label*="OTP"]').first,
            ]
            
            otp_folder_clicked = False
            for locator in otp_folder_locators:
                try:
                    locator.wait_for(state="visible", timeout=3_000)
                    locator.click()
                    otp_folder_clicked = True
                    logger.info("Successfully navigated to OTP folder in Outlook.")
                    # Wait for the folder contents to load
                    email_page.wait_for_load_state("domcontentloaded", timeout=10_000)
                    break
                except PlaywrightTimeoutError:
                    # Try the next locator
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

    def _handle_sign_in_if_needed(self, page: Page) -> bool:
        """Handle Outlook sign-in page if it is currently shown.

        Returns ``True`` if either no sign-in was required (already
        signed in) or the username/password flow was executed without
        obvious locator failures. Returns ``False`` if required login
        elements could not be found or another blocking error occurred.

        This method is defensive against navigation races. If the page is
        navigating while we try to read the title, Playwright can raise an
        "execution context was destroyed" error. In that case we simply log
        and return ``False`` so callers can avoid proceeding as if
        Outlook were authenticated.
        """
        try:
            # Best-effort wait for the page to reach a stable state.
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                # Non-fatal; continue and attempt to read title anyway.
                pass

            try:
                title = page.title().lower()
            except Exception as ex:
                # If the execution context was destroyed due to navigation,
                # log but continue; we'll decide based on field presence.
                # Log at debug level via generic logger if needed; do not
                # treat this as an error for normal test runs.
                self.logger.warning(
                    f"Outlook sign-in: unable to read page title: {ex}"
                )

            # Try multiple locators for username/email, password, and buttons,
            # since Microsoft occasionally updates the markup and IDs.
            username_locators = [
                page.locator("#i0116"),
                page.locator("input[name='loginfmt']"),
                page.locator("input[type='email']"),
            ]
            password_locators = [
                page.locator("#i0118"),
                page.locator("input[name='passwd']"),
                page.locator("input[type='password']"),
            ]
            next_button_locators = [
                page.locator("#idSIButton9"),
                page.locator("//input[@type='submit' and @value='Next']"),
                page.locator("//input[@type='submit' and @value='Sign in']"),
                page.locator("button[type='submit']"),
            ]
            stay_signed_in_yes = page.locator("//input[@type='submit' and @value='Yes']")

            # Helper to pick the first visible locator from a list.
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

            # Fast-path: if an Inbox marker is already visible, assume we are
            # signed in and skip probing username/password fields. This avoids
            # spending several seconds waiting for fields that will never
            # appear when the mailbox UI is already loaded.
            inbox_locators = [
                page.get_by_text("Inbox").first,
                page.get_by_role("link", name=re.compile(r"^Inbox$", re.I)),
                page.locator('[aria-label="Inbox"]'),
            ]
            if _first_visible(inbox_locators, 3_000) is not None:
                self.logger.info(
                    "Outlook sign-in: Inbox UI visible; assuming session already signed in."
                )
                return True

            # If neither username nor password fields are visible, assume we
            # are already signed in and skip the sign-in flow.
            if (
                _first_visible(username_locators, 5_000) is None
                and _first_visible(password_locators, 5_000) is None
            ):
                self.logger.info(
                    "Outlook sign-in: no username or password fields visible; "
                    "assuming session already signed in."
                )
                return True

            # Enter email directly on the Outlook page (avoid BasePage
            # helpers so we don't accidentally target the EWM tab).
            try:
                user_id_locator = _first_visible(username_locators, 20_000)
                if not user_id_locator:
                    self.logger.error(
                        "Outlook sign-in: could not find a visible username/email input."
                    )
                    return False
                else:
                    self.logger.info("Outlook sign-in: filling username/email field.")
                    user_id_locator.fill(self.config.mail_field1)

                next_button = _first_visible(next_button_locators, 20_000)
                if next_button:
                    self.logger.info("Outlook sign-in: clicking Next/Sign in button after username.")
                    next_button.click()
                else:
                    self.logger.error(
                        "Outlook sign-in: could not find Next/Sign in button after username entry."
                    )
                    return False
            except Exception as ex:
                self.logger.error(f"Error while entering Outlook username: {ex}")
                return False

            # Enter password on the same Outlook page
            try:
                # When the dedicated "Enter password" screen is shown,
                # wait explicitly for its heading so we don't attempt to
                # type into the password field before the page is ready.
                try:
                    import re as _re  # local alias to avoid shadowing

                    enter_pwd_heading = page.get_by_role(
                        "heading", name=_re.compile("Enter password", _re.I)
                    )
                    enter_pwd_heading.wait_for(state="visible", timeout=20_000)
                    self.logger.info(
                        "Outlook sign-in: 'Enter password' heading is visible; "
                        "locating password field."
                    )
                except PlaywrightTimeoutError:
                    # Heading not shown in this variant of the flow;
                    # proceed to locate password directly.
                    self.logger.info(
                        "Outlook sign-in: 'Enter password' heading not visible within "
                        "timeout; probing password field directly."
                    )
                except Exception as heading_ex:
                    self.logger.warning(
                        "Outlook sign-in: error while waiting for 'Enter password' "
                        f"heading; continuing to locate password field: {heading_ex}"
                    )

                password_locator = _first_visible(password_locators, 20_000)
                if not password_locator:
                    self.logger.error(
                        "Outlook sign-in: could not find a visible password input."
                    )
                    return False

                # Make sure the password field is ready before typing
                try:
                    password_locator.wait_for(state="visible", timeout=10_000)
                except Exception as wait_ex:
                    self.logger.error(
                        f"Outlook sign-in: password input did not become visible in time: {wait_ex}"
                    )
                    return False

                self.logger.info("Outlook sign-in: filling password field.")
                password_locator.fill(self.config.mail_field2)

                sign_in_button = _first_visible(next_button_locators, 20_000)
                if sign_in_button:
                    self.logger.info("Outlook sign-in: clicking Sign in button after password.")
                    sign_in_button.click()
                else:
                    self.logger.error(
                        "Outlook sign-in: could not find Sign in button after password entry."
                    )
                    return False

                # Stay signed in prompt (best-effort only).
                try:
                    stay_signed_in_yes.wait_for(state="visible", timeout=5_000)
                    stay_signed_in_yes.click()
                except (PlaywrightTimeoutError, Exception) as ex:
                    self.logger.error(
                        f"Error while handling 'Stay signed in' prompt: {ex}"
                    )
                # If we've reached this point, treat sign-in as completed
                # from the automation point of view.
                return True
            except (PlaywrightTimeoutError, Exception) as ex:
                self.logger.error(f"Error while entering Outlook password: {ex}")
                return False
        except Exception as ex:
            # Fully defensive: never let unexpected errors here fail the test.
            self.logger.error(f"Unexpected error in _handle_sign_in_if_needed: {ex}")
            return False

    def _read_latest_mail_time(self, page: Page) -> Optional[time]:
        """Read the timestamp of the currently clicked email in Outlook.
        
        Locates the timestamp element for the clicked mail and parses it to a time object.
        Waits for the timestamp element to be present before attempting to read.
        
        Returns:
            time object if successfully parsed, None if not found or parsing fails
        """
        logger.info("[OTP_DEBUG] [_read_latest_mail_time] Starting to read clicked email timestamp")
        logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Using locator: //div[@data-testid='SentReceivedSavedTime'] (first instance)")
        logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Expected TIME_FORMAT: {TIME_FORMAT}")

        # Use the first SentReceivedSavedTime element which is the clicked mail's timestamp
        time_elements = page.locator("//div[@data-testid='SentReceivedSavedTime']")
        
        try:
            # Wait for timestamp element to be present (at least 1)
            logger.info("[OTP_DEBUG] [_read_latest_mail_time] Waiting for timestamp element to appear...")
            wait_for_element_count(time_elements, count=1, timeout=10.0)
            logger.info("[OTP_DEBUG] [_read_latest_mail_time] Timestamp element is now present")
            
            element_count = time_elements.count()
            logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Found {element_count} timestamp element(s)")
            
            if element_count > 0:
                logger.info("[OTP_DEBUG] [_read_latest_mail_time] Reading inner text from first element")
                full_text = time_elements.first.inner_text().strip()
                logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Raw timestamp text: '{full_text}'")
                
                # Extract just the time portion (e.g., "1:40 AM" from "Tue 3/31/2026 1:40 AM")
                time_match = re.search(r'(\d{1,2}:\d{2}\s(?:AM|PM))', full_text)
                if time_match:
                    time_str = time_match.group(1)
                    logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Extracted time portion: '{time_str}'")
                    
                    parsed_time = datetime.strptime(time_str, TIME_FORMAT).time()
                    logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Successfully parsed to time object: {parsed_time.strftime(TIME_FORMAT)}")
                    return parsed_time
                else:
                    logger.error(f"[OTP_DEBUG] [_read_latest_mail_time] Could not extract time pattern from text: '{full_text}'")
            else:
                logger.warning("[OTP_DEBUG] [_read_latest_mail_time] No timestamp elements found on page")
                
        except WaitTimeoutError as ex:
            logger.error(f"[OTP_DEBUG] [_read_latest_mail_time] Timeout waiting for timestamp element: {ex}")
            logger.warning("[OTP_DEBUG] [_read_latest_mail_time] Timestamp element did not appear within timeout")
        except ValueError as ex:
            self.logger.error(f"[OTP_DEBUG] [_read_latest_mail_time] ValueError parsing timestamp - invalid format: {ex}")
            logger.info(f"[OTP_DEBUG] [_read_latest_mail_time] Raw text was: '{time_elements.first.inner_text().strip() if time_elements.count() > 0 else 'N/A'}'")
            with allure.step("Failed to parse mail time - invalid format"):
                pass
        except Exception as ex:
            self.logger.error(f"[OTP_DEBUG] [_read_latest_mail_time] Unexpected error reading/parsing mail time: {type(ex).__name__}: {ex}")
            with allure.step("Unexpected error parsing mail time"):
                pass
        
        logger.warning("[OTP_DEBUG] [_read_latest_mail_time] Could not retrieve/parse latest email time; returning None")
        return None

    def _extract_otp_from_latest_mail(self, page: Page) -> Optional[str]:
        # When multiple DocuSign verification emails exist, always pick the
        # newest one from the Outlook message list. In modern Outlook Web,
        # each message row is typically a `div[role="option"]` in the inbox.
        message_rows = page.locator("div[role='option']").filter(
            has_text=re.compile("Docusign verification", re.I)
        )

        if message_rows.count() == 0:
            return None

        # Click the first matching row (top-most = newest) directly on the
        # Outlook page to avoid BasePage auto-healing targeting another tab.
        newest_row = message_rows.first
        newest_row.click()

        # Scope OTP extraction to the opened mail body container to avoid
        # strict-mode violations from multiple matching preview items.
        body_container = page.locator('[data-test-id="mailMessageBodyContainer"]').first
        try:
            body_container.wait_for(state="visible", timeout=10_000)
            otp_text = body_container.inner_text()
        except PlaywrightTimeoutError as ex:
            self.logger.error(f"Timeout while reading OTP body text from mail body container: {ex}")
            return None
        except Exception as ex:
            # Catch any other unexpected Playwright or locator errors here
            self.logger.error(f"Unexpected error while reading OTP body text from mail body container: {ex}")
            return None

        match = re.search(r"\b\d{6}\b", otp_text)
        if match:
            return match.group(0)

        # Body text was found but did not contain a 6-digit OTP
        self.logger.error(f"Email body did not contain a valid 6-digit OTP. Body text: {otp_text!r}")
        return None

    def _click_inbox_search_and_select(
        self,
        outlook_email_page: Page,
        search_text: str,
        retries: int = 1,
        subject: Optional[str] = None,
        body: Optional[str] = None,
    ) -> None:
        """Click Inbox, run the search_text search, and open a result.

        If ``subject`` is provided, this method attempts to click the first
        email whose subject/text matches it (case-insensitive). If ``subject``
        is None, it clicks the first email row from the search results.

        If ``body`` is provided, then after searching (and optionally filtering
        by ``subject``), this method will open each candidate email in turn and
        inspect the message body. The first email whose body text contains the
        given ``body`` substring (case-insensitive) will be selected.

        For each retry attempt after the first, the page is reloaded before
        performing the Inbox/search steps again.
        """

        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                # Reload for every retry attempt after the first.
                if attempt > 0:
                    try:
                        self.logger.info(
                            "Outlook Inbox/search: reloading page before retry attempt "
                            f"{attempt + 1} of {retries}."
                        )
                        outlook_email_page.reload(wait_until="domcontentloaded")
                    except Exception as reload_ex:
                        self.logger.warning(
                            f"Outlook Inbox/search: error while reloading before retry: {reload_ex}"
                        )

                self.logger.info(
                    f"Outlook Inbox/search attempt {attempt + 1} of {retries} for search text: {search_text!r}."
                )

                # Click Inbox if it is easily available. In some Outlook
                # layouts the default view is already Inbox or the folder
                # pane may be collapsed, so failure to find an explicit
                # "Inbox" link should not fail the whole flow.
                inbox_clicked = False
                inbox_locators = [
                    outlook_email_page.get_by_text("Inbox").first,
                    outlook_email_page.get_by_role(
                        "link", name=re.compile(r"^Inbox$", re.I)
                    ),
                    outlook_email_page.locator('[aria-label="Inbox"]'),
                ]

                for locator in inbox_locators:
                    try:
                        locator.wait_for(state="visible", timeout=2_000)
                        locator.click()
                        inbox_clicked = True
                        self.logger.info("Clicked Inbox folder in Outlook.")
                        break
                    except PlaywrightTimeoutError:
                        # Try the next locator; not fatal if none are visible.
                        continue
                    except Exception as ex:
                        # Log and continue trying other locators.
                        self.logger.warning(
                            f"Error while trying to click Inbox locator; continuing: {ex}"
                        )

                if not inbox_clicked:
                    self.logger.warning(
                        "Could not explicitly click Inbox; proceeding to search across all mail."
                    )

                # Search for the AssetMark DocuSign email using the D-number.
                # Outlook layouts vary, so try several strategies to locate
                # the search box and wait for it to be visible.
                search_box = None
                search_locators = [
                    outlook_email_page.get_by_role(
                        "combobox", name=re.compile("search", re.I)
                    ),
                    outlook_email_page.get_by_role(
                        "textbox", name=re.compile("search", re.I)
                    ),
                    outlook_email_page.locator('[role="searchbox"]'),
                    outlook_email_page.locator('[aria-label="Search"]'),
                    outlook_email_page.locator('input[type="search"]'),
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
                    raise RuntimeError(
                        "Outlook search: could not locate a visible search box to search for authorized signer email."
                    )

                search_box.fill(search_text)
                search_box.press("Enter")

                # After running the search, ensure that we actually have at
                # least one email result row, then click either a subject-
                # matching row or the first result.
                results = outlook_email_page.locator("div[role='option']")
                # Give Outlook a short moment to render the filtered list.
                outlook_email_page.wait_for_timeout(2_000)
                count = results.count()
                if count == 0:
                    raise RuntimeError(
                        f"Outlook search: no email rows found after searching for {search_text!r}."
                    )
                self.logger.info(
                    f"Outlook search: found {count} email row(s) after searching for {search_text!r}."
                )

                # Choose which email row to open.
                candidate_rows = results
                if subject:
                    try:
                        subject_rows = results.filter(
                            has_text=re.compile(re.escape(subject), re.I)
                        )
                        if subject_rows.count() > 0:
                            self.logger.info(
                                "Outlook search: restricting candidates to email rows "
                                f"matching subject {subject!r}."
                            )
                            candidate_rows = subject_rows
                        else:
                            self.logger.warning(
                                "Outlook search: no email row matched subject "
                                f"{subject!r}; using all search results as candidates."
                            )
                    except Exception as subject_ex:
                        self.logger.warning(
                            "Outlook search: error while filtering results by subject "
                            f"{subject!r}; using all search results as candidates: {subject_ex}"
                        )

                # If a specific body text is requested, iterate through
                # candidate rows, open each email, and check its body for the
                # given substring.
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
                            # Wait for message body container to be visible
                            body_container = outlook_email_page.locator(
                                '[data-test-id="mailMessageBodyContainer"]'
                            ).first
                            body_container.wait_for(state="visible", timeout=10_000)
                            email_body_text = body_container.inner_text()

                            if body_pattern.search(email_body_text or ""):
                                self.logger.info(
                                    "Outlook search: found email whose body contains the "
                                    "requested text; selecting this email."
                                )
                                return

                            self.logger.info(
                                "Outlook search: candidate email %d/%d did not contain "
                                "requested body text; continuing.",
                                idx + 1,
                                candidate_count,
                            )
                        except Exception as body_ex:
                            self.logger.warning(
                                "Outlook search: error while checking email body for "
                                f"candidate {idx + 1}/{candidate_count}: {body_ex}"
                            )

                    # If we exhaust all candidates without finding the body
                    # text, treat this attempt as failed so outer retry logic
                    # can decide whether to reload and try again.
                    raise RuntimeError(
                        "Outlook search: no email in search results contained the "
                        f"requested body text {body!r}."
                    )

                # No body filter requested: click a single target row.
                target_row = candidate_rows.first
                self.logger.info(
                    "Outlook search: clicking first email row from candidate search results."
                )
                target_row.click()

                # If we reached here without raising, treat this attempt as
                # successful and stop retrying.
                return

            except Exception as ex:
                last_error = ex
                self.logger.warning(
                    f"Outlook Inbox/search attempt {attempt + 1} of {retries} failed; "
                    f"will retry if attempts remain: {ex}"
                )

        # If all attempts failed, re-raise the last error so the caller can handle it.
        if last_error is not None:
            raise last_error

    def search_authorized_signer_email(self, outlook_email_page: Page, search_text: str) -> None:
        """Search for authorized signer email using D-number only, then validate content.
        
        Strategy:
        1. Search Outlook by D-number ONLY (no subject/body filters in search)
        2. Click first result (most likely to be correct email)
        3. Validate the opened email:
           - Subject must contain "Electronic Signature"
           - Body must contain "ready for you to sign"
        4. If validation fails, retry entire search (up to 10 times with page reload)
        
        This ensures we find emails for the correct D-number and avoid picking old test emails.
        
        Args:
            outlook_email_page: Authenticated Outlook page to search in
            search_text: D-number to search for (e.g., "D003614220")
            
        Raises:
            RuntimeError: If email cannot be found and validated after 10 retries
        """
        max_retries = 10
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                retry_count += 1
                logger.info(f"Search attempt {retry_count}/{max_retries} for D-number: {search_text}")
                
                # Reload page before retry (except on first attempt)
                if retry_count > 1:
                    logger.info(f"Reloading page before retry attempt {retry_count}...")
                    outlook_email_page.reload(wait_until="domcontentloaded")
                    outlook_email_page.wait_for_timeout(2000)
                
                # Step 1: Search by D-number only (no subject/body filters)
                self._click_inbox_search_and_select(
                    outlook_email_page,
                    search_text,
                    retries=1,  # Single attempt per retry loop (we handle retries at this level)
                    subject=None,  # Don't filter by subject in search
                    body=None,     # Don't filter by body in search
                )
                
                logger.info(f"Search returned result for D-number: {search_text}")
                
                # Step 2: Validate the opened email
                logger.info("Validating email content...")
                
                # Validate subject contains "Electronic Signature"
                email_subject = outlook_email_page.locator('//div[contains(@id,"SUBJECT")]/descendant::span[1]').inner_text()
                logger.info(f"Email subject: {email_subject}")
                
                if "Electronic Signature" not in email_subject:
                    raise AssertionError(
                        f"Subject validation failed: expected 'Electronic Signature' in subject, "
                        f"but got: '{email_subject}'"
                    )
                logger.info("✓ Subject validation passed")
                
                # Validate body contains "ready for you to sign"
                body_container = outlook_email_page.locator('[data-test-id="mailMessageBodyContainer"]').first
                body_container.wait_for(state="visible", timeout=10000)
                email_body = body_container.inner_text()
                
                if "ready for you to sign" not in email_body.lower():
                    raise AssertionError(
                        f"Body validation failed: expected 'ready for you to sign' in body"
                    )
                logger.info("✓ Body validation passed")
                
                # Validate D-number is in the subject
                if search_text not in email_subject:
                    raise AssertionError(
                        f"D-number validation failed: expected '{search_text}' in subject, "
                        f"but got: '{email_subject}'"
                    )
                logger.info(f"✓ D-number validation passed: {search_text}")
                
                logger.info(f"✓ Successfully found and validated authorized signer email for D-number: {search_text}")
                return  # Success - exit function
                
            except Exception as ex:
                last_error = ex
                logger.warning(
                    f"Search attempt {retry_count}/{max_retries} failed: {str(ex)}\n"
                    f"Will retry search..."
                )
        
        # All retries exhausted
        raise RuntimeError(
            f"Failed to find and validate authorized signer email for D-number '{search_text}' "
            f"after {max_retries} attempts.\n"
            f"Last error: {str(last_error)}"
        )

    def fetch_authorized_signer_email_subject_and_body(self, outlook_email_page: Page, d_number: str) -> tuple[str, str]:
        """Fetch and return the authorized signer email subject and body content separately.
        
        Args:
            outlook_email_page: Outlook page containing the open email
            d_number: The D-number expected in the email subject (for logging purposes)
            
        Returns:
            tuple[str, str]: (subject_text, body_text) - Subject and body as separate strings
            
        Raises:
            Exception: If content cannot be retrieved
        """
        try:
            # Fetch email subject
            subject_element = outlook_email_page.locator('//div[contains(@id,"SUBJECT")]/descendant::span[1]')
            
            try:
                subject_element.wait_for(state="visible", timeout=5_000)
                subject_text = subject_element.inner_text()
            except PlaywrightTimeoutError:
                raise RuntimeError(f"Email subject element not found or not visible for D-number: {d_number}")
            
            self.logger.info(f"Fetched Email Subject: {subject_text}")
            
            # Fetch email body - use more robust locator for the container
            # Try multiple approaches: look for the mailMessageBodyContainer div first
            body_container = outlook_email_page.locator('//div[@data-test-id="mailMessageBodyContainer"]')
            
            try:
                body_container.wait_for(state="visible", timeout=10_000)
                # Get all text content from the container
                body_text = outlook_email_page.locator('//div[@data-test-id="mailMessageBodyContainer"]/descendant::table[@role="presentation"][1]/descendant::table[1]/tbody/tr[3]/td/span').first.inner_text()
            except PlaywrightTimeoutError:
                raise RuntimeError("Email body container not found or not visible")
            
            self.logger.info("Fetched Email Body successfully")
            
            with allure.step(f"Email content fetched for D-number: {d_number}"):
                allure.attach(
                    subject_text,
                    name="Email Subject",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    body_text[:1000],
                    name="Email Body Content",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            return (subject_text, body_text)
                
        except Exception as ex:  # pragma: no cover - defensive
            self.logger.error(f"Error while fetching email content: {ex}")
            raise

    def click_review_document_link(self, outlook_email_page: Page) -> Page:
        """Click the 'REVIEW DOCUMENT' link in the authorized signer email.
        
        IMPORTANT: Outlook ATP blocks external sender content, making the link href null.
        We must click 'Show blocked content' FIRST before clicking the link.
        
        Also handles Microsoft Safe Links (URL wrapping) and ATP warning pages.
        
        Clicking this link opens DocuSign in a new tab/popup.
        
        Args:
            outlook_email_page: Outlook page containing the email with Review Document link
            
        Returns:
            Page: The new DocuSign page that opens after clicking
            
        Raises:
            Exception: If Review Document link cannot be found or clicked
        """
        try:
            # Step 1: Unblock email content if ATP has blocked it
            # When external sender content is blocked, the REVIEW DOCUMENT link href is null
            self.logger.info("Step 1: Checking if email content is blocked by Outlook ATP...")
            self._unblock_email_content_if_needed(outlook_email_page)
            
            # Step 2: Click the REVIEW DOCUMENT link
            # Now the href should be populated with the actual DocuSign URL
            with outlook_email_page.expect_popup() as popup_info:
                review_link = outlook_email_page.get_by_role("link", name="REVIEW DOCUMENT")
                review_link.wait_for(state="visible", timeout=10_000)
                self.logger.info("Step 2: Clicking 'REVIEW DOCUMENT' link in authorized signer email")
                review_link.click()
            
            docusign_page = popup_info.value
            
            # Step 3: Handle Microsoft Safe Links and ATP warning redirects
            # Safe Links wrap URLs, and there might be ATP warning pages before actual content
            self.logger.info("Step 3: Handling potential Safe Links and ATP warning pages...")
            self._handle_safe_links_redirect(docusign_page)
            
            # Step 4: Wait for DocuSign page to load
            try:
                docusign_page.wait_for_load_state("networkidle", timeout=30_000)
                self.logger.info("✓ DocuSign page reached networkidle state")
            except Exception as e:
                self.logger.warning(f"DocuSign networkidle timeout: {e}, proceeding anyway")
            
            # Verify we're on DocuSign (not ATP warning page)
            try:
                docusign_page.wait_for_url(lambda url: "docusign" in url.lower(), timeout=30_000)
                self.logger.info("✓ Confirmed on DocuSign page")
            except Exception as e:
                self.logger.warning(f"DocuSign URL detection timeout: {e}, current URL: {docusign_page.url}")
            
            self.logger.info("✓ Successfully clicked 'REVIEW DOCUMENT' link, DocuSign page opened")
            return docusign_page
            
        except Exception as ex:
            self.logger.error(f"Error while clicking Review Document link: {ex}")
            raise
    
    def _handle_safe_links_redirect(self, page: Page) -> None:
        """Handle Microsoft Safe Links redirect pages and ATP warnings.
        
        Detects if we're stuck on a Safe Links error page (url=null) and closes it.
        Otherwise waits for any redirects to complete.
        
        Args:
            page: Playwright Page to handle redirects on
        """
        try:
            self.logger.info("Checking for Safe Links issues...")
            
            # Wait a moment for page to load
            page.wait_for_timeout(2000)
            
            current_url = page.url
            self.logger.info(f"Current URL after click: {current_url[:100]}...")
            
            # Check if we're stuck on Safe Links error page (url=null, cordid=null)
            if "safelink.html" in current_url and "url=null" in current_url:
                self.logger.error(
                    "Stuck on Safe Links error page (url=null). "
                    "Review Document link href was not populated properly. Closing this tab."
                )
                try:
                    page.close()
                except:
                    pass
                raise RuntimeError(
                    "Safe Links error: Review Document link href is null. "
                    "ATP unblock may not have fully loaded the link. Retrying..."
                )
            
            # If we're on safe links but with a valid URL, wait for redirect
            if "safelink.html" in current_url or "protection.outlook" in current_url:
                self.logger.info("On Safe Links page, waiting for redirect...")
                page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info(f"✓ Redirected to: {page.url[:100]}...")
                
        except Exception as e:
            self.logger.warning(f"⚠ Error handling Safe Links: {e}, proceeding anyway")
    
    def _unblock_email_content_if_needed(self, outlook_email_page: Page) -> None:
        """Click 'Show blocked content' in Outlook if ATP has blocked the email body.
        
        When an external sender is not in the Safe Senders list, Outlook blocks
        embedded content and the REVIEW DOCUMENT link href becomes null.
        Clicking 'Show blocked content' loads the real link URLs.
        
        Args:
            outlook_email_page: Outlook page containing the email
        """
        try:
            # Look for the "Show blocked content" button with various selector patterns
            blocked_content_locators = [
                outlook_email_page.get_by_role("button", name=lambda name: "show blocked content" in name.lower()),
                outlook_email_page.locator('button:has-text("Show blocked content")'),
                outlook_email_page.locator('button:has-text("Block content")'),
                outlook_email_page.locator('[role="button"]:has-text("Show")'),
            ]
            
            button_found = False
            for locator in blocked_content_locators:
                try:
                    locator.wait_for(state="visible", timeout=3_000)
                    self.logger.info("🔓 Found 'Show blocked content' button, clicking to unblock email...")
                    locator.click()
                    outlook_email_page.wait_for_timeout(2_000)  # Wait for content to load
                    self.logger.info("✓ Email content unblocked")
                    button_found = True
                    break
                except Exception:
                    continue
            
            if not button_found:
                self.logger.info("✓ No 'Show blocked content' button found - email content is not blocked")
                
        except Exception as e:
            self.logger.warning(f"⚠ Could not unblock email content: {e}, proceeding anyway")
            # Continue anyway - maybe content is already unblocked

    def login_and_complete_the_signing(self, search_text: str) -> None:
        """Login to Outlook and search for emails containing search_text."""
        parent_page = self.page
        outlook_email_page: Optional[Page] = None
        docusign_page: Optional["DocuSignPage"] = None

        try:
            # Use centralized login function
            outlook_email_page = self.login_outlook(context_message="complete signing workflow")

            # Use shared helper to click Inbox (best-effort), run the
            # search_text search (with retry handled inside the helper), and
            # open the AssetMark email for the authorized signer flow.
            self._click_inbox_search_and_select(
                outlook_email_page,
                search_text,
                retries=3,
                subject="AssetMark for eSig",
            )

            # When clicking REVIEW DOCUMENT, DocuSign opens in a new tab.
            with outlook_email_page.expect_popup() as docusign_page_info:
                review_link = outlook_email_page.get_by_role(
                    "link", name="REVIEW DOCUMENT"
                )
                review_link.wait_for(state="visible", timeout=10_000)
                review_link.click()

            docusign_raw_page = docusign_page_info.value

            # Lazy import to avoid circular import
            from pages.oam.docusign_page import DocuSignPage
            
            docusign_page = DocuSignPage(docusign_raw_page)
            docusign_page.verify_docusign_page_loaded()
            # Use the already-open Outlook tab to provide the OTP so that
            # we don't open a second Outlook window.

            def _fetch_otp_from_outlook() -> Optional[str]:
                submitting_time = datetime.now().time()
                return self.get_otp(
                    submitting_time=submitting_time,
                    max_wait_time_in_seconds=60,
                    parent_page=docusign_raw_page,
                    email_page=outlook_email_page,
                )

            docusign_page.complete_docusign_signing_with_otp(
                fetch_otp=_fetch_otp_from_outlook,
                session_timeout_check=False,
            )

        except Exception as ex:  # pragma: no cover - defensive
            self.logger.error(f"Error while searching email: {ex}")
            raise
        finally:
            if outlook_email_page is not None:
                try:
                    # get_otp may already have closed this page when using
                    # it as email_page; close only if still open.
                    if not outlook_email_page.is_closed():
                        outlook_email_page.close()
                except Exception:
                    pass
            if docusign_page is not None:
                try:
                    docusign_page.close()
                except Exception:
                    pass
            try:
                parent_page.bring_to_front()
            except Exception as ex:
                self.logger.error(f"Failed to bring parent_page to front after login_and_search_email: {ex}")

    def login_and_complete_the_signing_without_otp(self, search_text: str) -> None:
        """Login to Outlook and search for emails containing search_text."""
        parent_page = self.page
        outlook_email_page: Optional[Page] = None
        docusign_page: Optional["DocuSignPage"] = None

        try:
            # Use centralized login function
            outlook_email_page = self.login_outlook(context_message="complete ERSD consent")

            # Use shared helper to click Inbox (best-effort), run the
            # search_text search (with retry handled inside the helper), and
            # open the AssetMark email for the authorized signer flow.
            self._click_inbox_search_and_select(
                outlook_email_page,
                search_text,
                retries=3,
                subject="AssetMark for eSig",
            )

            # When clicking REVIEW DOCUMENT, DocuSign opens in a new tab.
            with outlook_email_page.expect_popup() as docusign_page_info:
                review_link = outlook_email_page.get_by_role(
                    "link", name="REVIEW DOCUMENT"
                )
                review_link.wait_for(state="visible", timeout=10_000)
                review_link.click()

            docusign_raw_page = docusign_page_info.value

            # Lazy import to avoid circular import
            from pages.oam.docusign_page import DocuSignPage
            
            docusign_page = DocuSignPage(docusign_raw_page)
            docusign_page.verify_docusign_page_loaded()

            docusign_page.complete_ersd_and_finish()

        except Exception as ex:  # pragma: no cover - defensive
            self.logger.error(f"Error while searching email: {ex}")
            raise
        finally:
            if outlook_email_page is not None:
                outlook_email_page.close()
            if docusign_page is not None:
                docusign_page.close()
            try:
                parent_page.bring_to_front()
            except Exception as ex:
                self.logger.error(f"Failed to bring parent_page to front after login_and_search_email: {ex}")

    def login_and_click_the_carbon_copy(self, search_text: str) -> None:
        """Login to Outlook and search for emails containing search_text."""
        parent_page = self.page
        outlook_email_page: Optional[Page] = None
        docusign_page: Optional["DocuSignPage"] = None

        try:
            # Use centralized login function
            outlook_email_page = self.login_outlook(context_message="view completed document")

            # Use shared helper to click Inbox (best-effort), run the
            # search_text search (with retry handled inside the helper), and
            # open the AssetMark email for the authorized signer flow.
            self._click_inbox_search_and_select(
                outlook_email_page,
                search_text,
                retries=3,
                subject="AssetMark for eSig",
                body=(
                    "All signers have completed the request and AssetMark has approved. Please process these documents."
                ),
            )

            # When clicking VIEW COMPLETED DOCUMENT, DocuSign opens in a new tab.
            with outlook_email_page.expect_popup() as docusign_page_info:
                review_link = outlook_email_page.get_by_role(
                    "link", name="VIEW COMPLETED DOCUMENT"
                )
                review_link.wait_for(state="visible", timeout=10_000)
                review_link.click()

            docusign_raw_page = docusign_page_info.value

            # Lazy import to avoid circular import
            from pages.oam.docusign_page import DocuSignPage
            
            docusign_page = DocuSignPage(docusign_raw_page)
            docusign_page.verify_docusign_page_loaded()


        except Exception as ex:  # pragma: no cover - defensive
            self.logger.error(f"Error while searching email: {ex}")
            raise
        finally:
            if outlook_email_page is not None:
                outlook_email_page.close()
            if docusign_page is not None:
                docusign_page.close()
            try:
                parent_page.bring_to_front()
            except Exception as ex:
                self.logger.error(f"Failed to bring parent_page to front after login_and_search_email: {ex}")
                

    
