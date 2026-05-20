"""Outlook OTP Page Object for Playwright-based email automation"""

import time
import os
import re
import email as pyemail
from typing import Optional
from configparser import ConfigParser
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.encryption_utility import EncryptionUtility
from utils.email_utils import IMAPEmailClient

logger = get_allure_logger(__name__)


class OutlookOTPPage(BasePage):
    """
    Page object for Outlook email interaction to extract OTP from DocuSign verification emails
    
    This page handles:
    - Logging into Outlook
    - Navigating to inbox
    - Finding DocuSign verification emails
    - Extracting OTP codes
    """

    _config: Optional[ConfigParser] = None
    _decrypted_cache: dict[str, str] = {}
    SEARCH_COMBOBOX_NAME_PATTERN = re.compile(r"Search for email, meetings", re.IGNORECASE)
    LOGIN_EMAIL_INPUT_SELECTORS = [
        'input[name="loginfmt"]',
        'input[id="i0116"]',
        'input[type="email"]',
        'input[placeholder*="email"]',
    ]
    LOGIN_NEXT_BUTTON_SELECTORS = ['input[id="idSIButton9"]', 'button:has-text("Next")', 'input[value="Next"]']
    LOGIN_PASSWORD_INPUT_SELECTORS = [
        'input[name="passwd"]',
        'input[id="i0118"]',
        'input[type="password"]',
    ]
    LOGIN_SIGNIN_BUTTON_SELECTORS = ['input[id="idSIButton9"]', 'button:has-text("Sign in")', 'input[value="Sign in"]']
    LOGIN_STAY_SIGNED_IN_NO_SELECTORS = ['input[id="idBtn_Back"]', 'button:has-text("No")', 'input[value="No"]']
    OTP_EXTRACTION_PATTERNS = [
        r"your\s+docusign\s+verification\s+code\s+is\s+(\d{6})",
        r"verification\s+code\s+is\s+(\d{6})",
        r"verification\s+code[:\s]+(\d{6})",
        r"(\d{6})\s*is\s+your\s+verification\s+code",
    ]

    @classmethod
    def load_config(cls) -> ConfigParser:
        """Load configuration from config/config.properties."""
        if cls._config is not None:
            return cls._config

        config_path = os.path.join(os.getcwd(), "config", "config.properties")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        parser = ConfigParser()
        parser.read(config_path)
        cls._config = parser
        logger.info(f"Loaded OTP configuration from: {config_path}")
        return cls._config

    @classmethod
    def _decrypt_config_value(cls, config_key: str) -> str:
        """Decrypt a credential value from config.properties."""
        if config_key in cls._decrypted_cache:
            return cls._decrypted_cache[config_key]

        config = cls.load_config()
        encrypted_value = config.get("DEFAULT", config_key)
        secret_key = config.get("DEFAULT", "SECRET_KEY")

        if not encrypted_value or not secret_key:
            raise ValueError(f"Missing {config_key} or SECRET_KEY in config.properties")

        decrypted_value = EncryptionUtility.decrypt(encrypted_value, secret_key)
        cls._decrypted_cache[config_key] = decrypted_value
        return decrypted_value

    @classmethod
    def get_email(cls, config_key: str = "MAIL_FIELD1") -> str:
        """Get decrypted Outlook email used for OTP retrieval."""
        return cls._decrypt_config_value(config_key)

    @classmethod
    def get_password(cls, config_key: str = "MAIL_FIELD2") -> str:
        """Get decrypted Outlook password used for OTP retrieval."""
        return cls._decrypt_config_value(config_key)

    @classmethod
    def get_imap_server(cls, config_key: str = "IMAP_SERVER") -> str:
        """Get IMAP server value from config.properties."""
        config = cls.load_config()
        return config.get("DEFAULT", config_key, fallback="imap-mail.outlook.com")

    @classmethod
    def clear_credential_cache(cls) -> None:
        """Clear decrypted credential cache."""
        cls._decrypted_cache.clear()

    @staticmethod
    def extract_otp_from_email_body(email_body: str) -> Optional[str]:
        """Extract OTP from plain email body text."""
        if not email_body:
            logger.warning("Email body is empty")
            return None

        otp = OutlookOTPPage._extract_latest_otp_from_text(
            email_body,
            context="email-body",
            log_attempts=False,
        )
        if otp:
            logger.info(f"Extracted OTP from email body: {otp}")
            return otp

        logger.warning("Could not extract OTP from email body")
        return None

    @classmethod
    def get_docusign_otp(
        cls,
        email_address: str,
        timeout: float = 60.0,
        poll_interval: float = 5.0,
        max_retries: int = 3,
    ) -> Optional[str]:
        """Retrieve DocuSign OTP via IMAP by reading the latest matching email."""
        imap_server = cls.get_imap_server()
        imap_user = cls.get_email()
        imap_password = cls.get_password()

        logger.info(f"Connecting to IMAP server: {imap_server}")

        start_time = time.time()
        retry_count = 0

        while (time.time() - start_time) < timeout and retry_count < max_retries:
            try:
                with IMAPEmailClient(
                    imap_server=imap_server,
                    email_address=imap_user,
                    password=imap_password,
                ) as imap_client:
                    email_id = imap_client.wait_for_email(
                        from_address="noreply@docusign.net",
                        subject_contains="verify",
                        timeout=poll_interval,
                        poll_interval=1.0,
                    )

                    if not email_id:
                        retry_count += 1
                        time.sleep(poll_interval)
                        continue

                    if not imap_client.connection:
                        retry_count += 1
                        time.sleep(poll_interval)
                        continue

                    status, message_data = imap_client.connection.fetch(email_id, "(RFC822)")
                    if status != "OK" or not message_data:
                        retry_count += 1
                        time.sleep(poll_interval)
                        continue

                    raw_email = None
                    for entry in message_data:
                        if isinstance(entry, tuple) and len(entry) > 1:
                            raw_email = entry[1]
                            break

                    if not raw_email:
                        retry_count += 1
                        time.sleep(poll_interval)
                        continue

                    body_text = cls._extract_text_from_email_bytes(raw_email)
                    otp = cls.extract_otp_from_email_body(body_text)

                    if otp and cls.validate_otp_format(otp):
                        logger.info(f"Successfully retrieved OTP via IMAP for {email_address}: {otp}")
                        return otp

                    retry_count += 1
                    time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error retrieving OTP via IMAP: {e}")
                retry_count += 1
                time.sleep(poll_interval)

        logger.error(f"Could not retrieve OTP via IMAP after {max_retries} retries")
        return None

    @staticmethod
    def _extract_text_from_email_bytes(raw_email: bytes) -> str:
        """Extract text/plain body from RFC822 bytes."""
        message = pyemail.message_from_bytes(raw_email)

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        return payload.decode(charset, errors="ignore")
        else:
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="ignore")

        return ""
    
    def __init__(self, page: Page):
        """Initialize Outlook OTP page"""
        super().__init__(page)
        self._init_locators()
    
    def _init_locators(self):
        """Initialize Outlook email locators"""
        # Login page locators
        self.email_input = self.page.locator('input[name="loginfmt"]')
        self.email_next_button = self.page.locator('input[id="idSIButton9"]')
        self.password_input = self.page.locator('input[name="passwd"]')
        self.password_next_button = self.page.locator('input[id="idSIButton9"]')
        self.stay_signed_in_no = self.page.locator('input[id="idBtn_Back"]')
        
        # Inbox locators
        self.inbox_button = self.page.locator('button[title="Inbox"]')
        self.folder_tree = self.page.locator('[role="tree"]')
        self.mail_main_container = self.page.locator('div[role="main"]').first
        self.mail_module_container = self.page.locator('div[data-app-section="MailModule"]').first
        self.message_list_container = self.page.locator('[aria-label*="Message list"]').first
        self.inbox_email_item_rows = self.page.locator('[data-item-id]')
        self.email_list = self.page.locator('div[role="option"][data-focusable-row="true"]')
        self.docusign_email = self.page.locator('text=/DocuSign|noreply@docusign/')
        
        # OTP folder locators - multiple fallbacks for robustness
        self.otp_folder = self.page.locator(
            'div[role="treeitem"][data-folder-name="otp"][aria-level="2"], '
            'div[role="treeitem"][data-folder-name="OTP"][aria-level="2"]'
        )
        self.otp_folder_alt = self.page.locator(
            'div[role="treeitem"][title^="OTP -"], '
            'div[role="treeitem"][data-folder-name="otp"]:has(span:has-text("OTP"))'
        )
        self.otp_folder_inbox = self.page.locator('button[title="Inbox"]')
        
        # Email content locators
        self.email_body = self.page.locator('div[role="document"][aria-label="Message body"]')
        self.email_body_alt = self.page.locator('[data-is-body-content=true]')
        self.email_document_container = self.page.locator('[role="document"]').first
        self.email_subject = self.page.locator('span[id*="SubjectLine"]')
        self.docusign_email_row = self.page.locator(
            'div[role="option"][data-focusable-row="true"]:has-text("DocuSign")'
        )
        
        # Close button
        self.close_email_button = self.page.locator('button[aria-label="Close"]').first

        # Tracking Center by-mail flow locators
        self.search_tracking_input_combobox = self.page.get_by_role("combobox", name=self.SEARCH_COMBOBOX_NAME_PATTERN).first
        self.search_tracking_button = self.page.get_by_role("button", name="Search", exact=True).first
        self.review_documents_action_link = self.page.get_by_role("link", name="REVIEW DOCUMENTS", exact=True).first

        # Backward-compatible aliases
        self.searchBox = self.search_tracking_input_combobox
        self.searchIcon = self.search_tracking_button
        self.review_documents_link = self.review_documents_action_link

    def search_tracking_number(self, tracking_number: str, timeout: float) -> Optional[Locator]:
        """Search tracking number repeatedly until result appears or retry window expires."""
        tracking_result_row = self._get_tracking_result_row(tracking_number)
        search_window_ms = max(int(timeout), 60000)
        search_deadline = time.time() + (search_window_ms / 1000.0)
        search_cycle = 0

        while time.time() < search_deadline:
            search_cycle += 1

            self._reapply_tracking_number(tracking_number)

            if self._run_tracking_search_cycle(tracking_result_row):
                return tracking_result_row

            sleep_ms = min(3000, int((search_deadline - time.time()) * 1000))
            if sleep_ms > 0:
                self.page.wait_for_timeout(sleep_ms)

        logger.warning(
            f"[outlook-tracking] Tracking number '{tracking_number}' not visible after {search_window_ms // 1000}s"
        )
        self.fail(
            f"Tracking number result not found in Outlook search: '{tracking_number}' "
            f"after {search_window_ms // 1000}s"
        )

    def _run_tracking_search_cycle(self, tracking_result_row: Locator) -> bool:
        """Run one full search cycle across all trigger strategies."""
        for strategy_name, trigger in self._get_tracking_search_trigger_strategies():
            try:
                self.search_tracking_input_combobox.click(timeout=3000)
                trigger()
                self.page.wait_for_timeout(2500)
                if tracking_result_row.is_visible(timeout=4000):
                    return True
            except Exception as strategy_error:
                logger.debug(f"[outlook-tracking] Search trigger failed via {strategy_name}: {strategy_error}")
        return False

    def _get_tracking_search_trigger_strategies(self):
        """Return all supported strategies to trigger Outlook search."""
        return [
            ("search box Enter", lambda: self.search_tracking_input_combobox.press("Enter", timeout=3000)),
            ("page keyboard Enter", lambda: self.page.keyboard.press("Enter")),
            ("search icon click", lambda: self.search_tracking_button.click(timeout=5000)),
            ("search box search shortcut", lambda: self.search_tracking_input_combobox.press("Control+Enter", timeout=3000)),
        ]

    def _reapply_tracking_number(self, tracking_number: str) -> None:
        """Refocus the search box and re-enter the tracking number."""
        self.search_tracking_input_combobox.click(timeout=5000)
        self.search_tracking_input_combobox.press("Control+A", timeout=3000)
        self.search_tracking_input_combobox.fill(tracking_number)
        self.page.wait_for_timeout(500)

    def _get_tracking_result_row(self, tracking_number: str) -> Locator:
        return self.page.locator(
            f"div[role='option'][aria-label*='{tracking_number}'], "
            f"div[role='option']:has-text('{tracking_number}'), "
            f"div[role='listitem']:has-text('{tracking_number}'), "
            f"div[data-convid]:has-text('{tracking_number}'), "
            f"div[draggable='true']:has-text('{tracking_number}'), "
            f"span:has-text('{tracking_number}')"
        ).first

    def open_client_review_documents_page(
        self,
        tracking_number: str,
        email: str = None,
        password: str = None,
        timeout: float = 30000,
    ) -> Optional[Page]:
        """Login/open Outlook, search by tracking number, open matched email, click REVIEW DOCUMENTS, and return the newly opened page."""
        logger.info(
            f"[outlook-tracking] Start flow | tracking_number={tracking_number}"
        )
        
        if not tracking_number:
            logger.warning("[outlook-tracking] Empty tracking number")
            return None

        if not email or not password:
            email = OutlookOTPPage.get_email()
            password = OutlookOTPPage.get_password()

        try:

            self.navigate_to_outlook()
            if not self.login(email, password):
                logger.error("[outlook-tracking] Outlook login failed")
                return None

            logger.info("[outlook-tracking] Waiting 30s before starting tracking search")
            self.page.wait_for_timeout(30000)

            self.search_tracking_input_combobox.wait_for(state="visible", timeout=timeout)

            tracking_result_row = self.search_tracking_number(tracking_number, timeout)
            if not tracking_result_row:
                self.fail(
                    f"Tracking number result not found in Outlook search: '{tracking_number}'"
                )
            tracking_result_row.click(timeout=10000)

            try:
                row_meta = ""
                try:
                    row_meta = tracking_result_row.inner_text(timeout=3000) or ""
                except Exception:
                    row_meta = ""
                if not row_meta:
                    try:
                        row_meta = tracking_result_row.get_attribute("aria-label", timeout=3000) or ""
                    except Exception:
                        row_meta = ""

                preferred_sender = None
                for raw_line in row_meta.splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    lowered = line.lower()
                    if tracking_number.lower() in lowered:
                        continue
                    if re.search(r"docusign|verification|review documents|\b(am|pm)\b|\b(mon|tue|wed|thu|fri|sat|sun)\b", lowered):
                        continue
                    if re.search(r"\d", line):
                        continue
                    if len(line) < 3:
                        continue
                    preferred_sender = line
                    break

                self._preferred_otp_sender = preferred_sender
                if preferred_sender:
                    logger.debug(f"[outlook-tracking] Preferred OTP sender captured: {preferred_sender}")
            except Exception as e:
                logger.debug(f"[outlook-tracking] Could not capture preferred OTP sender: {e}")
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                review_documents_timeout = max(int(timeout), 90000)
                self.review_documents_action_link.wait_for(state="visible", timeout=review_documents_timeout)
                self.review_documents_action_link.click(timeout=review_documents_timeout)

            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)
            logger.info(f"[outlook-tracking] REVIEW DOCUMENTS opened in new tab: {new_page.url}")
            return new_page
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"[outlook-tracking] Failed to open REVIEW DOCUMENTS from tracking number {tracking_number}: {e}")
            return None
    
    def navigate_to_outlook(self, outlook_url: str = "https://outlook.office.com"):
        """
        Navigate to Outlook and ensure page loads
        
        Args:
            outlook_url: Outlook URL to navigate to
        """
        logger.info(f"Navigating to Outlook: {outlook_url}")
        try:
            self.page.goto(outlook_url, wait_until="domcontentloaded", timeout=30000)
            logger.info(f"Goto completed. Current URL: {self.page.url}")
            
            # Wait for DOM to be ready instead of networkidle (headless compatible)
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=10000)
                logger.info("DOM content loaded")
            except Exception as e:
                logger.warning(f"DOM load wait timeout, continuing anyway: {e}")
            
            logger.info(f"Outlook page loaded. Current URL: {self.page.url}")
        except Exception as e:
            logger.error(f"Failed to navigate to Outlook: {e}")
            logger.info(f"Current page URL: {self.page.url}")
            raise
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Outlook with email and password
        
        Uses encrypted credentials from config/config.properties if email/password are None
        
        Args:
            email: Email address (or None to use config values)
            password: Password (or None to use config values)
            
        Returns:
            True if login successful
        """
        # If credentials not provided, load from encrypted config
        if not email or not password:
            email = OutlookOTPPage.get_email()
            password = OutlookOTPPage.get_password()
        
        masked_email = f"{email[:4]}***{email[-8:]}" if email and len(email) > 12 else "***"
        logger.info(f"OUTLOOK_LOGIN: Starting login workflow with email={masked_email}")
        logger.info(f"OUTLOOK_LOGIN: Current page before login: {self.page.url}")
        
        # Check if we're already on the mail page (already logged in)
        if "/mail/" in self.page.url:
            logger.info("OUTLOOK_LOGIN: ✓ Already on Outlook mail URL, validating stability")
            
            # CRITICAL: Verify page is actually stable and not about to redirect
            # Wait for key UI elements to confirm we're really on Outlook mail page
            try:
                # Wait for URL to stabilize - check it doesn't change
                initial_url = self.page.url
                self.page.wait_for_timeout(2000)
                
                # Check if URL changed (session expired/redirected)
                if self.page.url != initial_url:
                    logger.warning(f"OUTLOOK_LOGIN: URL changed during stability check: {initial_url} -> {self.page.url}")
                    
                    # If redirected to auth page, session expired - need to re-login
                    if 'login.microsoftonline.com' in self.page.url:
                        logger.warning("OUTLOOK_LOGIN: Session expired, continuing with login flow")
                        # Fall through to login code below
                    else:
                        return True
                else:
                    # URL stable, verify key UI elements are present
                    # Look for inbox button or folder list to confirm we're on actual mail page
                    inbox_count = self.inbox_button.count()
                    folder_list_count = self.folder_tree.count()
                    
                    if inbox_count > 0 or folder_list_count > 0:
                        logger.info("OUTLOOK_LOGIN: ✓ Outlook UI elements verified - page is stable")
                        return True
                    else:
                        logger.warning("OUTLOOK_LOGIN: Outlook UI elements not visible yet")
                        # Wait a bit more and try again
                        self.page.wait_for_timeout(3000)
                        inbox_count = self.inbox_button.count()
                        folder_list_count = self.folder_tree.count()
                        
                        if inbox_count > 0 or folder_list_count > 0:
                            logger.info("OUTLOOK_LOGIN: ✓ Outlook UI elements verified after retry")
                            return True
                        else:
                            logger.warning("OUTLOOK_LOGIN: Outlook UI still not visible; continuing with login flow")
                            # Fall through to login code below
            except Exception as stability_error:
                logger.warning(f"OUTLOOK_LOGIN: Stability check failed: {stability_error}")
                # Fall through to login code below
        
        try:
            logger.info("OUTLOOK_LOGIN: Locating email input field")
            # Try multiple selectors for email input field
            email_input = self._find_visible_locator_from_selectors(
                self.LOGIN_EMAIL_INPUT_SELECTORS,
                timeout=5000,
                description="email input"
            )
            
            if not email_input:
                logger.error("Email input field not found.")
                # Check if we're on an unexpected page
                if "/mail/" in self.page.url:
                    logger.info("On mail page but couldn't find email input - presuming logged in")
                    return True
                raise Exception("Email input field not found")
            
            # Fill email
            logger.info("OUTLOOK_LOGIN: Filling email input")
            email_input.fill(email)
            
            # Find and click next button
            logger.info("OUTLOOK_LOGIN: Locating next button after email")
            next_btn = self._find_visible_locator_from_selectors(
                self.LOGIN_NEXT_BUTTON_SELECTORS,
                timeout=5000,
                description="next button"
            )
            
            if next_btn:
                logger.info("OUTLOOK_LOGIN: Clicking next button")
                next_btn.click()
                self.page.wait_for_timeout(2000)
            else:
                logger.error("Next button not found after email")
            
            # Find password input
            logger.info("OUTLOOK_LOGIN: Locating password input")
            logger.debug("Waiting for password field")
            password_input = self._find_visible_locator_from_selectors(
                self.LOGIN_PASSWORD_INPUT_SELECTORS,
                timeout=15000,
                description="password field"
            )
            
            if not password_input:
                logger.error("Password input not found")
                raise Exception("Password input not found")
            
            # Fill password
            logger.info("OUTLOOK_LOGIN: Filling password input")
            password_input.fill(password)
            
            # Click next/sign in button
            logger.info("OUTLOOK_LOGIN: Locating sign-in button")
            signin_btn = self._find_visible_locator_from_selectors(
                self.LOGIN_SIGNIN_BUTTON_SELECTORS,
                timeout=5000,
                description="sign-in button"
            )
            
            if signin_btn:
                logger.info("OUTLOOK_LOGIN: Clicking sign-in button")
                signin_btn.click()
                logger.debug("Sign in button clicked, waiting for navigation...")
            else:
                logger.warning("OUTLOOK_LOGIN: Sign-in button not found; continuing to URL checks")
            
            # Wait for navigation to complete - use URL change instead of networkidle (headless compatible)
            try:
                # Wait for URL to change away from login page
                self.page.wait_for_function(
                    "() => !window.location.href.includes('login.microsoftonline.com')",
                    timeout=30000
                )
                logger.info(f"OUTLOOK_LOGIN: Navigated away from login page to: {self.page.url}")
            except Exception as e:
                logger.warning(f"OUTLOOK_LOGIN: URL change wait timed out: {e}, checking current URL...")
            
            # Handle "Stay signed in?" dialog if present
            logger.debug("Checking for stay signed in dialog")
            try:
                stay_no_btn = self._find_visible_locator_from_selectors(
                    self.LOGIN_STAY_SIGNED_IN_NO_SELECTORS,
                    timeout=5000,
                    description="stay signed in 'No' button"
                )
                if stay_no_btn:
                    logger.debug("Found 'Stay signed in?' dialog, clicking 'No'")
                    stay_no_btn.click(timeout=5000)
                    # Wait for navigation after clicking No
                    self.page.wait_for_load_state('domcontentloaded', timeout=15000)
            except Exception as e:
                logger.debug(f"Stay signed in dialog not found or already handled: {e}")
            
            # Wait for Outlook mail page to load - use DOM elements instead of networkidle
            logger.debug("Waiting for Outlook to load...")
            try:
                # Wait for either the inbox button or any mail container to appear
                inbox_indicators = [
                    (self.inbox_button.first, 'button[title="Inbox"]'),
                    (self.mail_main_container, 'div[role="main"]'),
                    (self.mail_module_container, 'div[data-app-section="MailModule"]'),
                    (self.message_list_container, '[aria-label*="Message list"]'),
                ]
                
                for indicator_locator, indicator_name in inbox_indicators:
                    try:
                        indicator_locator.wait_for(state="attached", timeout=10000)
                        logger.info(f"OUTLOOK_LOGIN: ✓ Outlook loaded - found indicator: {indicator_name}")
                        break
                    except:
                        continue
                        
                logger.info(f"OUTLOOK_LOGIN: Page URL after login: {self.page.url}")
                
            except Exception as load_err:
                logger.warning(f"OUTLOOK_LOGIN: Could not detect Outlook UI elements: {load_err}")
            
            # Check if we're in the Outlook inbox
            if 'outlook.office.com' in self.page.url or '/mail' in self.page.url:
                logger.info("OUTLOOK_LOGIN: ✓ Outlook login successful")
                return True
            else:
                logger.warning(f"OUTLOOK_LOGIN: Not in Outlook inbox. Current URL: {self.page.url}")
                # Check if we got past login at least
                if 'login.microsoftonline.com' not in self.page.url:
                    logger.info("OUTLOOK_LOGIN: Past login page, continuing anyway")
                    return True
                return False
            
        except Exception as e:
            logger.error(f"OUTLOOK_LOGIN: Login failed with exception: {e}")
            return False

    def _find_visible_locator_from_selectors(
        self,
        selectors: list[str],
        timeout: int = 5000,
        description: str = "element"
    ) -> Optional[Locator]:
        """
        Try multiple selectors and return the first one that becomes visible.

        Args:
            selectors: List of selector strings to try
            timeout: Timeout in milliseconds for each selector
            description: Description of element being found (for logging)

        Returns:
            Locator if found, None otherwise
        """
        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                locator.wait_for(state="visible", timeout=timeout)
                logger.info(f"Found {description} with selector: {selector}")
                return locator
            except:
                continue
        logger.warning(f"{description} not found with any of the {len(selectors)} selectors")
        return None
    
    def wait_for_docusign_email(
        self,
        timeout: float = 60.0,
        poll_interval: float = 5.0,
        max_retries: int = 3,
    ) -> Optional[Locator]:
        """
        Wait for DocuSign verification email to arrive
        
        Args:
            timeout: Total timeout in seconds
            poll_interval: Interval between polls in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            Email locator if found, None otherwise
        """
        logger.info("Waiting for DocuSign verification email")
        
        start_time = time.time()
        retry_count = 0
        
        while (time.time() - start_time) < timeout and retry_count < max_retries:
            try:
                # Refresh inbox
                logger.debug(f"Checking for DocuSign email (attempt {retry_count + 1}/{max_retries})")
                self.page.reload()
                self.page.wait_for_timeout(2000)
                
                # Try to find DocuSign email
                email_elements = self.docusign_email.all()
                
                if email_elements:
                    logger.info(f"Found {len(email_elements)} DocuSign email(s)")
                    return self.docusign_email.first
                
                retry_count += 1
                if retry_count < max_retries:
                    logger.debug(f"DocuSign email not found, waiting {poll_interval}s before retry")
                    time.sleep(poll_interval)
                    
            except Exception as e:
                logger.warning(f"Error checking for DocuSign email: {e}")
                retry_count += 1
                time.sleep(poll_interval)
        
        logger.error(f"DocuSign email not found after {max_retries} retries")
        return None
    
    def open_email(self, email_locator: Locator) -> bool:
        """
        Open a specific email
        
        Args:
            email_locator: Locator for email to open
            
        Returns:
            True if opened successfully
        """
        logger.info("Opening DocuSign verification email")
        
        try:
            email_locator.click()
            self.page.wait_for_timeout(3000)
            
            # Wait for email body to load
            if self.email_body.count() > 0:
                expect(self.email_body.first).to_be_visible(timeout=10000)
            else:
                expect(self.email_body_alt.first).to_be_visible(timeout=10000)
            
            logger.info("Email opened successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open email: {e}")
            return False
    
    def extract_otp_from_email(self) -> Optional[str]:
        """
        Extract OTP from currently opened email

        Returns:
            OTP code (6 digits) or None
        """
        logger.info("Extracting OTP from opened email")
        
        try:
            # Get email body text
            body_locators = []
            primary_count = self.email_body.count()
            alt_count = self.email_body_alt.count()
            
            if primary_count > 0:
                body_locators = self.email_body.all()
            elif alt_count > 0:
                body_locators = self.email_body_alt.all()

            email_body_text = ""
            for i, body in enumerate(body_locators):
                try:
                    email_body_text = body.inner_text().strip()
                    if not email_body_text:
                        text_content = body.text_content()
                        email_body_text = text_content.strip() if text_content else ""
                    if email_body_text:
                        break
                except Exception as e:
                    logger.debug(f"Error extracting body from element #{i+1}: {e}")
                    continue
            
            if not email_body_text:
                logger.warning("Email body is empty")
                try:
                    subject_text = None
                    if self.email_subject.count() > 0:
                        subject_text = self.email_subject.first.text_content()
                    os.makedirs("reports/oam/screenshots", exist_ok=True)
                    screenshot_path = f"reports/oam/screenshots/outlook_email_empty_{int(time.time())}.png"
                    self.page.screenshot(path=screenshot_path, full_page=True)
                    logger.info(
                        f"Saved Outlook email debug screenshot: {screenshot_path} (subject={subject_text})"
                    )
                except Exception as screenshot_error:
                    logger.warning(f"Failed to capture Outlook email screenshot: {screenshot_error}")
                return None
            
            otp = self._extract_latest_otp_from_text(
                email_body_text,
                context="opened-email",
                log_attempts=False,
            )
            if otp:
                return otp
            
            logger.warning("Could not extract OTP from email body")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting OTP from email: {e}")
            return None

    def get_otp_with_retry(
        self,
        email: str = None,
        password: str = None,
        timeout: float = 60.0,
        refresh_interval: float = 5.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Optional[str]:
        """
        Complete Outlook workflow to retrieve OTP from OTP folder with time-based refresh
        
        This is the UNIFIED method that:
        1. Navigates to Outlook
        2. Logs in with credentials
        3. Navigates to OTP folder
        4. Fetches latest OTP note
        5. Refreshes page every 5 seconds for up to 1 minute to ensure latest OTP is fetched
        
        If email/password not provided, uses encrypted credentials from config/config.properties
        
        Args:
            email: Email address for login (uses config if None)
            password: Email password (uses config if None)
            timeout: Total timeout in seconds (default: 60 seconds = 1 minute)
            refresh_interval: Interval between page refreshes in seconds (default: 5 seconds)
            
        Returns:
            OTP code (6 digits) or None if not found
        """
        # Load encrypted credentials from config if not provided
        if not email or not password:
            email = OutlookOTPPage.get_email()
            password = OutlookOTPPage.get_password()
        
        logger.info("Starting unified Outlook OTP retrieval workflow")
        
        try:
            # Navigate to Outlook
            self.navigate_to_outlook()
            
            # Login
            if not self.login(email, password):
                logger.error("Failed to login to Outlook")
                return None
            
            # Navigate to OTP folder and fetch latest OTP with refresh logic
            otp = self.get_latest_otp_from_folder(
                timeout=timeout,
                refresh_interval=refresh_interval,
                sent_after_epoch=sent_after_epoch,
                preferred_sender=preferred_sender,
            )
            
            if otp:
                logger.info(f"Successfully retrieved OTP from Outlook OTP folder: {otp}")
            else:
                logger.error("Failed to retrieve OTP from OTP folder")
                self.fail(
                    f"OTP not found in Outlook within {int(timeout)}s while checking OTP folder"
                )
            
            return otp

        except Exception as e:
            logger.error(f"Error in unified OTP retrieval workflow: {e}")
            return None
    
    def close_email(self):
        """Close currently opened email and return to inbox"""
        logger.info("Closing email")
        
        try:
            self.close_email_button.click()
            self.page.wait_for_timeout(1000)
            logger.info("Email closed successfully")
        except Exception as e:
            logger.warning(f"Error closing email: {e}")
    
    def navigate_to_otp_folder(self) -> bool:
        """
        Navigate to the OTP folder in Outlook.

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            self.folder_tree.first.wait_for(state="visible", timeout=20000)
            self.page.wait_for_timeout(500)

            selector1 = self.otp_folder.first
            selector2 = self.otp_folder_alt.first

            for label, locator in (("primary otp selector", selector1), ("alternate otp selector", selector2)):
                try:
                    if locator.count() <= 0:
                        continue
                    locator.wait_for(state="visible", timeout=10000)
                    locator.scroll_into_view_if_needed()
                    locator.click(timeout=10000)
                    logger.info(f"OTP folder opened via {label}")
                    self.page.wait_for_timeout(2000)
                    return True
                except Exception as click_err:
                    logger.debug(f"OTP click failed via {label}: {click_err}")

            logger.error("OTP folder not found or not clickable")
            try:
                os.makedirs("reports/oam/screenshots", exist_ok=True)
                screenshot_path = f"reports/oam/screenshots/otp_folder_not_found_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception:
                pass
            return False

        except Exception as e:
            logger.error(f"Error navigating to OTP folder: {e}")
            try:
                os.makedirs("reports/oam/screenshots", exist_ok=True)
                screenshot_path = f"reports/oam/screenshots/otp_folder_navigation_exception_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception:
                pass
            return False

    def get_latest_otp_from_folder(
        self,
        timeout: float = 60.0,
        refresh_interval: float = 5.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Optional[str]:
        """
        Fetch the latest OTP from the OTP folder
        
        This method:
        1. Navigates to OTP folder (already done)
        2. Finds first email with recent received time (within last few minutes)
        3. Clicks and opens the email
        4. Extracts OTP from email body
        5. Returns the OTP
        
        Args:
            timeout: Total timeout in seconds
            refresh_interval: Interval between page refreshes in seconds
            
        Returns:
            OTP code if found, None otherwise
        """
        logger.info(f"Retrieving OTP from folder (timeout={timeout}s, refresh={refresh_interval}s)")

        def _ensure_outlook_mail_shell() -> bool:
            if "outlook.office.com" not in self.page.url:
                logger.warning("Not on Outlook domain yet; waiting for redirect")
                self.page.wait_for_timeout(3000)

            if "outlook.office.com" not in self.page.url or "/mail" not in self.page.url:
                try:
                    logger.warning("Navigating to Outlook mail shell")
                    self.page.goto("https://outlook.office.com/mail/", wait_until="domcontentloaded", timeout=30000)
                    self.page.wait_for_timeout(2000)
                except Exception as e:
                    logger.error(f"Failed to navigate to Outlook mail shell: {e}")
                    return False

            try:
                self.folder_tree.first.wait_for(state="visible", timeout=20000)
            except Exception as e:
                logger.error(f"Folder tree not visible: {e}")
                return False

            return True

        try:
            if not _ensure_outlook_mail_shell():
                return None
            
            if not self.navigate_to_otp_folder():
                logger.error("Could not navigate to OTP folder")
                return None

            start_time = time.time()
            
            # Wait for emails and try multiple times
            cycle = 0
            while (time.time() - start_time) < timeout:
                cycle += 1
                try:
                    # Wait for email list to load
                    self.page.wait_for_timeout(2000)
                    
                    # Prefer the most recent DocuSign email row; fallback to first row
                    docusign_count = self.docusign_email_row.count()
                    email_list_count = self.email_list.count()
                    
                    first_email = None
                    preferred_sender_lower = (preferred_sender or "").strip().lower()
                    min_allowed_epoch = (sent_after_epoch - 90) if sent_after_epoch else None
                    
                    if docusign_count > 0:
                        first_email = self._find_first_matching_docusign_verification_row()

                        if sent_after_epoch:
                            first_email = first_email or self._select_closest_emaild_row_after_click_send_now(
                                docusign_count=docusign_count,
                                sent_after_epoch=sent_after_epoch,
                                preferred_sender_lower=preferred_sender_lower,
                                min_allowed_epoch=min_allowed_epoch,
                                require_sender=bool(preferred_sender_lower),
                            )

                        if not first_email and sent_after_epoch:
                            first_email = self._select_closest_emaild_row_after_click_send_now(
                                docusign_count=docusign_count,
                                sent_after_epoch=sent_after_epoch,
                                preferred_sender_lower=preferred_sender_lower,
                                min_allowed_epoch=min_allowed_epoch,
                                require_sender=False,
                            )

                        if sent_after_epoch and not first_email:
                            logger.debug(
                                "No email found at/near send-now time yet; waiting for refresh"
                            )
                            raise Exception("No near/post-send OTP email yet")

                        if not first_email and preferred_sender_lower:
                            for idx in range(min(docusign_count, 3)):
                                candidate = self.docusign_email_row.nth(idx)
                                row_meta = self._get_email_row_metadata(candidate)
                                row_meta_lower = row_meta.lower()
                                if preferred_sender_lower in row_meta_lower:
                                    first_email = candidate
                                    logger.debug(f"Selected row {idx} by sender-only filter")
                                    break

                        if not first_email:
                            first_email = self.docusign_email_row.first
                            
                    elif email_list_count > 0:
                        first_email = self.email_list.first
                    else:
                        self.page.wait_for_timeout(3000)  # Wait a bit longer
                        # Try again
                        docusign_count = self.docusign_email_row.count()
                        email_list_count = self.email_list.count()
                        
                        if docusign_count > 0:
                            first_email = self.docusign_email_row.first
                        elif email_list_count > 0:
                            first_email = self.email_list.first
                        else:
                            raise Exception("No emails found after retry")
                    
                    if not first_email:
                        raise Exception("Could not determine which email to open")

                    try:
                        selected_meta = self._get_email_row_metadata(first_email)
                    except Exception:
                        selected_meta = ""
                    logger.debug(f"Selected row metadata: {selected_meta[:300]}")
                    
                    # Click the first email
                    if not self._click_email_row(first_email):
                        raise Exception("Failed to click selected OTP email row")
                    # Wait for email body to appear (headless compatible)
                    try:
                        self.email_document_container.wait_for(state="attached", timeout=10000)
                    except:
                        # Fallback to timeout if body detection fails
                        self.page.wait_for_timeout(3000)
                    
                    # Extract OTP from email body
                    otp = self.extract_otp_from_email()
                    
                    if otp:
                        logger.info(f"Successfully extracted OTP: {otp}")
                        return otp
                    else:
                        
                        # Close email and refresh to try again
                        try:
                            self.close_email_button.click(timeout=5000)
                            self.page.wait_for_timeout(1000)
                        except Exception as e:
                            logger.debug(f"Close email failed: {e}")
                    
                except Exception as e:
                    logger.warning(f"Cycle {cycle} failed while opening/reading OTP email: {e}")
                    
                # Wait and refresh if we haven't found OTP yet
                elapsed = time.time() - start_time
                if elapsed < timeout:
                    remaining = min(refresh_interval, timeout - elapsed)
                    self.page.wait_for_timeout(int(remaining * 1000))

                    try:
                        self.page.reload(wait_until="domcontentloaded", timeout=30000)
                    except Exception as reload_err:
                        logger.warning(f"Outlook reload failed: {reload_err}")

                    if not _ensure_outlook_mail_shell():
                        return None

                    if not self.navigate_to_otp_folder():
                        logger.error("OTP folder could not be re-opened after reload")
                        try:
                            os.makedirs("reports/oam/screenshots", exist_ok=True)
                            screenshot_path = f"reports/oam/screenshots/otp_folder_lost_after_reload_{int(time.time())}.png"
                            self.page.screenshot(path=screenshot_path, full_page=True)
                            logger.info(f"Screenshot saved: {screenshot_path}")
                        except Exception:
                            pass
                        return None
                else:
                    break
            
            logger.error(f"Failed to extract OTP from OTP folder after {timeout}s")
            self.fail(
                f"OTP not found in Outlook OTP folder after {int(timeout)}s"
            )

        except Exception as e:
            logger.error(f"Error retrieving OTP from folder: {e}")
            return None

    def _find_first_matching_docusign_verification_row(self) -> Optional[Locator]:
        rows = self.email_list
        row_count = rows.count()
        if row_count <= 0:
            return None

        for idx in range(row_count):
            candidate = rows.nth(idx)
            try:
                row_text = candidate.inner_text(timeout=2000) or ""
            except Exception:
                continue

            lowered = row_text.lower()
            if "docusign" in lowered and "verification" in lowered:
                logger.debug(f"First DocuSign verification row found at index {idx}")
                return candidate
        return None

    def _click_email_row(self, row: Locator) -> bool:
        logger.debug("Attempting to open selected email row")

        click_strategies = [
            ("direct", lambda: row.click(timeout=10000)),
            ("force", lambda: row.click(timeout=5000, force=True)),
            ("double_click", lambda: row.dblclick(timeout=5000)),
            ("js", lambda: row.evaluate("el => el.click()")),
        ]

        for strategy_name, strategy in click_strategies:
            try:
                strategy()
                logger.info(f"Opened email row via {strategy_name} click")
                return True
            except Exception as click_err:
                logger.debug(f"Email row click failed via {strategy_name}: {click_err}")

        return False
    
    def _fetch_otp_from_inbox_emails(self, timeout: float = 30.0) -> Optional[str]:
        """
        Fetch OTP from DocuSign emails in Inbox
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            OTP code if found, None otherwise
        """
        logger.info(f"Checking Inbox for DocuSign OTP email (timeout: {timeout}s)")
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < timeout:
                try:
                    # Find DocuSign emails
                    emails = self.inbox_email_item_rows
                    email_count = emails.count()
                    logger.info(f"Found {email_count} email(s) in Inbox")
                    
                    if email_count > 0:
                        # Check each email for OTP
                        for i in range(min(email_count, 5)):  # Check top 5 emails
                            try:
                                email = emails.nth(i)
                                # Check if subject contains "DocuSign"
                                subject_text = email.inner_text()
                                logger.debug(f"Email {i}: {subject_text[:50]}...")
                                
                                if 'docusign' in subject_text.lower():
                                    email.click(timeout=5000)
                                    self.page.wait_for_timeout(2000)
                                    
                                    try:
                                        body_text = self.email_body_alt.first.inner_text(timeout=5000)
                                        
                                        if body_text:
                                            otp_code = self._extract_latest_otp_from_text(
                                                body_text,
                                                context=f"inbox-email-{i}",
                                            )
                                            if otp_code:
                                                logger.info(f"Found OTP in Inbox email: {otp_code}")
                                                return otp_code
                                    except Exception as e:
                                        logger.debug(f"Error extracting OTP from email {i}: {e}")
                                    
                                    # Close email
                                    try:
                                        self.close_email_button.click(timeout=5000)
                                        self.page.wait_for_timeout(1000)
                                    except:
                                        pass
                            except Exception as e:
                                logger.debug(f"Error checking email {i}: {e}")
                                continue
                    
                except Exception as e:
                    logger.debug(f"Error checking emails: {e}")
                
                # Refresh and retry
                remaining = timeout - (time.time() - start_time)
                if remaining > 0:
                    self.page.reload()
                    self.page.wait_for_timeout(min(5000, int(remaining * 1000)))
            
            return None
        except Exception as e:
            logger.error(f"Error fetching OTP from Inbox: {e}")
            return None

    def _select_closest_emaild_row_after_click_send_now(
        self,
        docusign_count: int,
        sent_after_epoch: float,
        preferred_sender_lower: str,
        min_allowed_epoch: float,
        require_sender: bool,
    ) -> Optional[Locator]:
        rows_to_check = min(docusign_count, 3)
        best_candidate = None
        best_delta = None
        best_index = None

        for idx in range(rows_to_check):
            candidate = self.docusign_email_row.nth(idx)
            row_meta = self._get_email_row_metadata(candidate)
            row_meta_lower = row_meta.lower()
            row_epoch = self._parse_email_row_time_to_epoch(row_meta)

            if require_sender and preferred_sender_lower and preferred_sender_lower not in row_meta_lower:
                continue
            if not row_epoch or (min_allowed_epoch is not None and row_epoch < min_allowed_epoch):
                continue

            delta = row_epoch - sent_after_epoch if sent_after_epoch else 0
            if sent_after_epoch and delta < 0:
                continue
            if (
                best_candidate is None
                or delta < best_delta
                or (delta == best_delta and idx > best_index)
            ):
                best_candidate = candidate
                best_delta = delta
                best_index = idx

        if best_candidate is not None:
            mode = "sender+nearest-time" if require_sender else "nearest-time"
            logger.debug(f"Selected row {best_index} by {mode} filter")
        return best_candidate

    def _get_email_row_metadata(self, row: Locator) -> str:
        parts = []
        try:
            row_text = row.inner_text(timeout=2000)
            if row_text:
                parts.append(row_text)
        except Exception:
            pass
        try:
            aria = row.get_attribute("aria-label", timeout=2000)
            if aria:
                parts.append(aria)
        except Exception:
            pass
        return " ".join(parts)

    def _parse_email_row_time_to_epoch(self, row_text: str) -> float:
        if not row_text:
            return 0.0
        lowered = row_text.lower()
        now_epoch = time.time()

        if "just now" in lowered or "now" in lowered:
            return now_epoch

        minute_match = re.search(r"(\d+)\s*(m|min|mins|minute|minutes)\b", lowered)
        if minute_match:
            return now_epoch - int(minute_match.group(1)) * 60

        hour_match = re.search(r"(\d+)\s*(h|hr|hrs|hour|hours)\b", lowered)
        if hour_match:
            return now_epoch - int(hour_match.group(1)) * 3600

        if "yesterday" in lowered:
            return now_epoch - 24 * 3600

        time_match = re.search(r"\b(\d{1,2}):(\d{2})\s*([ap]m)\b", lowered)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            ampm = time_match.group(3)

            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0

            now_local = time.localtime(now_epoch)
            row_epoch = time.mktime((
                now_local.tm_year,
                now_local.tm_mon,
                now_local.tm_mday,
                hour,
                minute,
                59,
                now_local.tm_wday,
                now_local.tm_yday,
                now_local.tm_isdst,
            ))

            if row_epoch > now_epoch + 120:
                row_epoch -= 24 * 3600
            return row_epoch

        return 0.0

    @classmethod
    def _extract_latest_otp_from_text(
        cls,
        text: str,
        context: str,
        log_attempts: bool = False,
    ) -> Optional[str]:
        """Extract the latest 6-digit OTP from text using shared patterns."""
        if not text:
            return None

        for index, pattern in enumerate(cls.OTP_EXTRACTION_PATTERNS, start=1):
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if not matches:
                continue

            otp_candidate = matches[-1].group(1)
            if cls.validate_otp_format(otp_candidate):
                logger.info(f"Extracted OTP for {context} using pattern #{index}: {otp_candidate}")
                return otp_candidate

        return None

    @staticmethod
    def validate_otp_format(otp: str) -> bool:
        """Validate OTP format (6 digits)."""
        if not otp or not re.match(r"^\d{6}$", otp):
            logger.warning(f"Invalid OTP format: {otp}")
            return False
        return True

