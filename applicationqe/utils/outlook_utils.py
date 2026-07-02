"""
Outlook Email Utility

Reads Outlook / Office 365 emails and extracts data based on subject, sender, etc.

Uses IMAP with username + password. No extra dependencies — only Python's built-in
``imaplib`` and ``email`` modules.

Works with Outlook.com, Office 365, Hotmail, and on-prem Exchange (IMAP enabled).

Quick Start::

    from utils.outlook_utils import OutlookClient

    with OutlookClient(email="...", password="...") as client:
        email = client.get_latest_email_by_subject("Welcome")
        otp = client.extract_pattern_from_email(email, r"\\b(\\d{6})\\b", group=1)

Note on App Passwords:
    If your account has Multi-Factor Authentication (MFA) enabled, you need
    an *App Password* instead of your regular password.
"""

import email as email_lib
import email.message
import html
import imaplib
import logging
import os
import re
import time
from dataclasses import dataclass, field
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import Any, List, Optional, Pattern, Union

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_IMAP_SERVER = "outlook.office365.com"
DEFAULT_IMAP_PORT = 993

_OUTLOOK_OTP_PATTERNS = [
    r"your\s+docusign\s+verification\s+code\s+is\s+(\d{6})",
    r"verification\s+code\s+is\s+(\d{6})",
    r"verification\s+code[:\s]+(\d{6})",
    r"(\d{6})\s*is\s+your\s+verification\s+code",
]


# ═══════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class OutlookEmail:
    """Represents a single Outlook email message."""

    id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    received_datetime: str
    body_text: str
    body_html: str
    has_attachments: bool
    is_read: bool
    importance: str = "normal"
    cc_addresses: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    web_link: Optional[str] = None
    conversation_id: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"OutlookEmail(subject={self.subject!r}, "
            f"from={self.from_address!r}, "
            f"received={self.received_datetime!r})"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Shared Browser Automation Helpers
# (used by both OutlookOTPPage and pages.outlook_page.OutlookPage)
# ═══════════════════════════════════════════════════════════════════════════


def outlook_extract_otp_from_text(text: str) -> Optional[str]:
    """Extract a 6-digit OTP from email body text using DocuSign verification patterns.

    Tries each pattern in order, returning the last match's captured group.
    Falls back to any isolated 6-digit number if no pattern matches.
    Returns ``None`` when no OTP is found.
    """
    if not text:
        return None
    for pattern in _OUTLOOK_OTP_PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            candidate = matches[-1].group(1)
            if re.match(r"^\d{6}$", candidate):
                return candidate
    m = re.search(r"\b(\d{6})\b", text)
    return m.group(1) if m else None


def outlook_navigate_to_otp_folder(page: Page) -> bool:
    """Navigate to the OTP folder in an already-open Outlook web page.

    Tries a series of common locator strategies.
    Returns ``True`` on success, ``False`` if the folder could not be found.
    """
    try:
        otp_locators = [
            page.get_by_text("OTP", exact=False).first,
            page.get_by_role("link", name=re.compile(r"OTP", re.I)),
            page.locator('[aria-label*="OTP"]').first,
            page.locator('//span[contains(text(), "OTP")]').first,
            page.locator('[role="treeitem"][aria-label*="OTP"]').first,
        ]
        for locator in otp_locators:
            try:
                locator.wait_for(state="visible", timeout=3_000)
                locator.click()
                page.wait_for_load_state("domcontentloaded", timeout=10_000)
                logger.info("outlook_navigate_to_otp_folder: OTP folder opened.")
                return True
            except Exception:
                continue
        logger.warning(
            "outlook_navigate_to_otp_folder: OTP folder not found; proceeding with current view."
        )
        return False
    except Exception as ex:
        logger.error(f"outlook_navigate_to_otp_folder: unexpected error: {ex}")
        return False


def outlook_perform_sign_in(page: Page, email: str = None, password: str = None) -> bool:
    """Fill the Microsoft sign-in form using *email* and *password*.

    Handles the standard two-step flow (email → Next → password → Sign in)
    and dismisses the "Stay signed in?" prompt if it appears.

    Falls back to ``OUTLOOK_USERNAME`` / ``OUTLOOK_PASSWORD`` environment
    variables when *email* or *password* are not supplied.

    Returns ``True`` when the form was submitted (or sign-in was not needed),
    ``False`` on locator failures.
    """
    if not email:
        email = os.getenv("OUTLOOK_USERNAME", "")
    if not password:
        password = os.getenv("OUTLOOK_PASSWORD", "")
    if not email or not password:
        logger.error("outlook_perform_sign_in: email/password not provided and not in env vars.")
        return False

    try:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15_000)
        except Exception:
            pass

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

        def _first_visible(locators, timeout_ms: int):
            for loc in locators:
                try:
                    loc.wait_for(state="visible", timeout=timeout_ms)
                    return loc
                except Exception:
                    continue
            return None

        # Fast-path: Inbox already visible → already signed in
        inbox_locators = [
            page.get_by_text("Inbox").first,
            page.get_by_role("link", name=re.compile(r"^Inbox$", re.I)),
            page.locator('[aria-label="Inbox"]'),
        ]
        if _first_visible(inbox_locators, 3_000) is not None:
            logger.info("outlook_perform_sign_in: Inbox visible; already signed in.")
            return True

        # Handle "Pick an account" / account selector page
        account_picker_locators = [
            page.locator("#tilesHolder .table"),  # account tile
            page.locator('[data-test-id="otherTile"]'),  # "Use another account"
            page.get_by_text("Use another account"),
            page.get_by_text("Pick an account"),
        ]
        if _first_visible(account_picker_locators, 3_000) is not None:
            logger.info("outlook_perform_sign_in: Account picker detected")
            # Try clicking "Use another account" to get to the email form
            use_another = page.locator(
                '[data-test-id="otherTile"],'
                ' #otherTile,'
                ' div:has-text("Use another account")'
            ).first
            try:
                use_another.click(timeout=5_000)
                logger.info("outlook_perform_sign_in: clicked 'Use another account'")
                page.wait_for_timeout(2000)
            except Exception:
                # If no "Use another account", click the first account tile
                try:
                    first_tile = page.locator("#tilesHolder .table").first
                    first_tile.click(timeout=5_000)
                    logger.info("outlook_perform_sign_in: clicked first account tile")
                    page.wait_for_timeout(2000)
                except Exception as tile_err:
                    logger.warning(f"outlook_perform_sign_in: could not interact with account picker: {str(tile_err).splitlines()[0]}")

        # If neither form field is visible, check URL before assuming signed in
        if (
            _first_visible(username_locators, 5_000) is None
            and _first_visible(password_locators, 5_000) is None
        ):
            if "outlook.office.com" in page.url:
                logger.info("outlook_perform_sign_in: no login fields visible; assuming signed in.")
                return True
            else:
                logger.warning(f"outlook_perform_sign_in: no login fields but not on Outlook; URL={page.url}")
                # Save debug screenshot
                try:
                    os.makedirs("reports/screenshots", exist_ok=True)
                    page.screenshot(path=f"reports/screenshots/outlook_login_stuck_{int(time.time())}.png")
                except Exception:
                    pass
                return False

        # --- Enter email ---
        user_input = _first_visible(username_locators, 20_000)
        if not user_input:
            logger.error("outlook_perform_sign_in: username field not found.")
            return False
        user_input.fill(email)

        next_btn = _first_visible(next_button_locators, 20_000)
        if not next_btn:
            logger.error("outlook_perform_sign_in: Next button not found after email.")
            return False
        next_btn.click()

        # --- Wait for password screen ---
        try:
            page.get_by_role("heading", name=re.compile("Enter password", re.I)).wait_for(
                state="visible", timeout=20_000
            )
        except Exception:
            pass

        # --- Enter password ---
        pwd_input = _first_visible(password_locators, 20_000)
        if not pwd_input:
            logger.error("outlook_perform_sign_in: password field not found.")
            return False
        try:
            pwd_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        pwd_input.fill(password)

        sign_in_btn = _first_visible(next_button_locators, 20_000)
        if sign_in_btn:
            sign_in_btn.click()
        else:
            logger.warning("outlook_perform_sign_in: Sign in button not found after password.")

        # --- Handle "Stay signed in?" prompt (best-effort) ---
        # First wait for the redirect/prompt to appear (slower on headless/Linux)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15_000)
        except Exception:
            pass

        for stay_selector in [
            "//input[@type='submit' and @value='Yes']",
            'input[id="idBtn_Back"]',
            'button:has-text("No")',
        ]:
            try:
                btn = page.locator(stay_selector)
                btn.wait_for(state="visible", timeout=5_000)
                btn.click()
                break
            except Exception:
                continue

        # Wait for redirect to Outlook after dismissing the prompt
        try:
            page.wait_for_url("**/outlook.office.com/**", timeout=30_000)
        except Exception:
            logger.warning(f"outlook_perform_sign_in: did not redirect to Outlook; URL={page.url}")

        logger.info(f"outlook_perform_sign_in: sign-in form submitted; URL={page.url}")
        return True
    except Exception as ex:
        logger.error(f"outlook_perform_sign_in: unexpected error: {ex}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# IMAP-based Outlook Client
# ═══════════════════════════════════════════════════════════════════════════


class OutlookClient:
    """
    Outlook email client using IMAP with username and password.

    Connects to Outlook / Office 365 over IMAP-SSL and provides methods to
    search, fetch, and extract data from emails.

    Args:
        email: Outlook email address. Falls back to ``OUTLOOK_USERNAME`` env var.
        password: Account or App Password. Falls back to ``OUTLOOK_PASSWORD`` env var.
        imap_server: IMAP server hostname. Defaults to ``outlook.office365.com``.
        imap_port: IMAP port. Defaults to ``993`` (SSL).
        folder: Mailbox folder to operate on. Defaults to ``"INBOX"``.
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        imap_server: str = DEFAULT_IMAP_SERVER,
        imap_port: int = DEFAULT_IMAP_PORT,
        folder: str = "INBOX",
    ):
        self.email = email or os.getenv("OUTLOOK_USERNAME", "")
        self.password = password or os.getenv("OUTLOOK_PASSWORD", "")
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.folder = folder

        if not self.email or not self.password:
            raise ValueError(
                "Email and password are required. "
                "Pass them as arguments or set OUTLOOK_USERNAME / OUTLOOK_PASSWORD env vars."
            )

        self._mail: Optional[imaplib.IMAP4_SSL] = None
        self._connect()

    # --- Context manager ---

    def __enter__(self) -> "OutlookClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    # --- Connection management ---

    def _connect(self) -> None:
        """Establish IMAP-SSL connection and authenticate."""
        try:
            logger.info(
                "Connecting to %s:%d as %s ...", self.imap_server, self.imap_port, self.email
            )
            self._mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self._mail.login(self.email, self.password)
            self._mail.select(self.folder)
            logger.info("Connected and selected folder '%s'", self.folder)
        except imaplib.IMAP4.error as e:
            logger.error("IMAP login failed: %s", e)
            raise RuntimeError(
                f"Failed to login to {self.imap_server} as {self.email}. "
                f"If MFA is enabled, use an App Password. Error: {e}"
            ) from e

    def _ensure_connection(self) -> imaplib.IMAP4_SSL:
        """Return the IMAP connection, reconnecting if needed."""
        if self._mail is None:
            self._connect()
        try:
            self._mail.noop()  # type: ignore[union-attr]
        except (imaplib.IMAP4.error, OSError):
            logger.warning("IMAP connection lost, reconnecting...")
            self._connect()
        return self._mail  # type: ignore[return-value]

    def close(self) -> None:
        """Close the IMAP connection gracefully."""
        if self._mail:
            try:
                self._mail.close()
                self._mail.logout()
                logger.info("IMAP connection closed")
            except Exception:
                pass
            finally:
                self._mail = None

    # --- IMAP search / fetch ---

    def _search(self, criteria: str) -> List[bytes]:
        """Run an IMAP SEARCH and return message IDs."""
        mail = self._ensure_connection()
        status, data = mail.search(None, criteria)
        if status != "OK":
            logger.warning("IMAP search failed for criteria: %s", criteria)
            return []
        msg_ids = data[0].split()
        logger.debug("IMAP search '%s' returned %d messages", criteria, len(msg_ids))
        return msg_ids

    def _fetch_email(self, msg_id: bytes) -> Optional[OutlookEmail]:
        """Fetch and parse a single email by IMAP message ID."""
        mail = self._ensure_connection()
        status, data = mail.fetch(msg_id.decode("utf-8"), "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return None
        raw_email = data[0][1]  # type: ignore[index]
        if not isinstance(raw_email, bytes):
            return None
        msg = email_lib.message_from_bytes(raw_email)
        return self._parse_imap_message(msg, msg_id)

    def _parse_imap_message(self, msg: email.message.Message, msg_id: bytes) -> OutlookEmail:
        """Parse a Python email.message.Message into an OutlookEmail dataclass."""
        subject = self._decode_header_value(msg.get("Subject", ""))
        from_address = self._extract_email_address(msg.get("From", ""))

        to_addresses = [
            self._extract_email_address(a.strip())
            for a in (msg.get("To", "")).split(",")
            if a.strip()
        ]
        cc_addresses = [
            self._extract_email_address(a.strip())
            for a in (msg.get("Cc", "") or "").split(",")
            if a.strip()
        ]

        date_str = msg.get("Date", "")
        try:
            received_datetime = parsedate_to_datetime(date_str).isoformat()
        except Exception:
            received_datetime = date_str

        body_text, body_html, has_attachments = self._extract_body(msg)

        importance = (msg.get("Importance") or msg.get("X-Priority") or "normal").lower()
        if importance in ("1", "high"):
            importance = "high"
        elif importance in ("5", "low"):
            importance = "low"
        else:
            importance = "normal"

        return OutlookEmail(
            id=msg_id.decode("utf-8") if isinstance(msg_id, bytes) else str(msg_id),
            subject=subject,
            from_address=from_address,
            to_addresses=to_addresses,
            received_datetime=received_datetime,
            body_text=body_text,
            body_html=body_html,
            has_attachments=has_attachments,
            is_read=True,
            importance=importance,
            cc_addresses=cc_addresses,
            conversation_id=msg.get("Message-ID"),
        )

    @staticmethod
    def _extract_body(msg: email.message.Message) -> tuple:
        """Extract plain text, HTML, and attachment flag from a message."""
        body_text = ""
        body_html = ""
        has_attachments = False

        def _decode_payload(part):
            payload = part.get_payload(decode=True)
            if payload is None or not isinstance(payload, bytes):
                return ""
            charset = part.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                return payload.decode("utf-8", errors="replace")

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in disposition.lower():
                    has_attachments = True
                    continue
                decoded = _decode_payload(part)
                if not decoded:
                    continue
                if content_type == "text/plain" and not body_text:
                    body_text = decoded
                elif content_type == "text/html" and not body_html:
                    body_html = decoded
        else:
            decoded = _decode_payload(msg)
            if msg.get_content_type() == "text/html":
                body_html = decoded
            else:
                body_text = decoded

        if not body_text and body_html:
            body_text = OutlookClient._html_to_text(body_html)

        return body_text, body_html, has_attachments

    # --- Header / address helpers ---

    @staticmethod
    def _decode_header_value(raw: str) -> str:
        """Decode an RFC 2047-encoded header value."""
        parts = decode_header(raw)
        decoded_parts: List[str] = []
        for part, charset in parts:
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                decoded_parts.append(part)
        return "".join(decoded_parts)

    @staticmethod
    def _extract_email_address(raw: str) -> str:
        """Extract bare email address from a 'Name <email>' string."""
        match = re.search(r"<([^>]+)>", raw)
        return match.group(1).strip() if match else raw.strip()

    @staticmethod
    def _html_to_text(html_content: str) -> str:
        """Strip HTML tags and decode entities to get plain text."""
        text = re.sub(r"<br\s*/?>", "\n", html_content, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        return html.unescape(text).strip()

    # --- Public API: fetch emails ---

    def get_emails_by_subject(
        self,
        subject: str,
        top: int = 10,
        exact_match: bool = False,
    ) -> List[OutlookEmail]:
        """Fetch emails whose subject contains (or exactly matches) the given text.

        Returns up to *top* matching emails, newest first.
        """
        criteria = f'SUBJECT "{subject}"'
        msg_ids = list(reversed(self._search(criteria)))[: top * 2]

        emails: List[OutlookEmail] = []
        for mid in msg_ids:
            if len(emails) >= top:
                break
            email_obj = self._fetch_email(mid)
            if email_obj is None:
                continue
            if exact_match and email_obj.subject.strip().lower() != subject.strip().lower():
                continue
            emails.append(email_obj)

        logger.info(
            "Found %d emails matching subject %r (exact=%s)", len(emails), subject, exact_match
        )
        return emails

    def get_latest_email_by_subject(
        self,
        subject: str,
        exact_match: bool = False,
    ) -> Optional[OutlookEmail]:
        """Get the most recent email matching the given subject."""
        emails = self.get_emails_by_subject(subject, top=1, exact_match=exact_match)
        return emails[0] if emails else None

    # --- Public API: extract data ---

    def extract_pattern_from_email(
        self,
        email: OutlookEmail,
        pattern: Union[str, "Pattern[str]"],
        group: int = 0,
    ) -> Optional[str]:
        """Extract text matching a regex pattern from the email body."""
        compiled = re.compile(pattern, re.IGNORECASE) if isinstance(pattern, str) else pattern

        for text in [email.body_text, email.body_html]:
            if text:
                match = compiled.search(text)
                if match:
                    result = match.group(group)
                    logger.debug("Extracted %r from email %r", result, email.subject)
                    return result

        logger.debug("Pattern %s not found in email %r", pattern, email.subject)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Outlook OTP Page Object (Browser Automation)
# ═══════════════════════════════════════════════════════════════════════════


class OutlookOTPPage(BasePage):
    """
    Page object for Outlook email interaction to extract OTP codes
    and open tracking-number review documents.
    """

    SEARCH_COMBOBOX_NAME_PATTERN = re.compile(r"Search for email, meetings", re.IGNORECASE)

    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    # ─── Locators ─────────────────────────────────────────────────────────

    def _init_locators(self):
        """Initialize Outlook email locators."""
        # Folder tree
        self.folder_tree = self.page.locator('[role="tree"]')

        # Email list
        self.email_list = self.page.locator('div[role="option"][data-focusable-row="true"]')
        self.docusign_email_row = self.page.locator(
            'div[role="option"][data-focusable-row="true"]:has-text("DocuSign")'
        )

        # Email content
        self.email_body = self.page.locator('div[role="document"][aria-label="Message body"]')
        self.email_body_alt = self.page.locator("[data-is-body-content=true]")
        self.email_document_container = self.page.locator('[role="document"]').first
        self.email_subject = self.page.locator('span[id*="SubjectLine"]')
        self.close_email_button = self.page.locator('button[aria-label="Close"]').first

        # Tracking search
        self.search_tracking_input_combobox = self.page.get_by_role(
            "combobox", name=self.SEARCH_COMBOBOX_NAME_PATTERN
        ).first
        self.search_tracking_button = self.page.get_by_role(
            "button", name="Search", exact=True
        ).first
        self.review_documents_action_link = self.page.get_by_role(
            "link", name="REVIEW DOCUMENTS", exact=True
        ).first

    # ─── Navigation & Authentication ─────────────────────────────────────

    def navigate_to_outlook(self, outlook_url: str = "https://outlook.office.com"):
        """Navigate to Outlook and ensure page loads."""
        logger.info(f"Navigating to Outlook: {outlook_url}")
        try:
            self.page.goto(outlook_url, wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception as e:
                logger.warning(
                    f"DOM load wait timeout, continuing anyway: {str(e).splitlines()[0]}"
                )
        except Exception as e:
            logger.error(f"Failed to navigate to Outlook: {str(e).splitlines()[0]}")
            logger.info(f"Current page URL: {self.page.url}")
            raise

    def navigate_to_otp_folder(self) -> bool:
        """Navigate to the OTP folder in Outlook."""
        try:
            self.folder_tree.first.wait_for(state="visible", timeout=20000)
            self.page.wait_for_timeout(500)
        except Exception as e:
            logger.error(f"Error waiting for folder tree: {str(e).splitlines()[0]}")
            return False

        result = outlook_navigate_to_otp_folder(self.page)
        if not result:
            self._save_debug_screenshot("otp_folder_not_found")
        return result

    # ─── OTP Extraction ──────────────────────────────────────────────────

    def extract_otp_from_email(self) -> Optional[str]:
        """Extract OTP from currently opened email."""
        try:
            body_locators = []
            if self.email_body.count() > 0:
                body_locators = self.email_body.all()
            elif self.email_body_alt.count() > 0:
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
                    os.makedirs("reports/screenshots", exist_ok=True)
                    screenshot_path = (
                        f"reports/screenshots/outlook_email_empty_{int(time.time())}.png"
                    )
                    self.page.screenshot(path=screenshot_path, full_page=True)
                    logger.info(
                        f"Saved debug screenshot: {screenshot_path} (subject={subject_text})"
                    )
                except Exception as screenshot_error:
                    logger.warning(f"Failed to capture screenshot: {screenshot_error}")
                return None

            otp = outlook_extract_otp_from_text(email_body_text)
            if otp:
                return otp

            logger.warning("Could not extract OTP from email body")
            return None
        except Exception as e:
            logger.error(f"Error extracting OTP from email: {str(e).splitlines()[0]}")
            return None

    def get_otp_with_retry(
        self,
        timeout: float = 60.0,
        refresh_interval: float = 5.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Optional[str]:
        """Complete Outlook workflow: navigate → sign in → OTP folder → extract OTP.

        Refreshes the page periodically until *timeout* expires.

        Args:
            timeout: Total timeout in seconds (default 60).
            refresh_interval: Seconds between page refreshes (default 5).
            sent_after_epoch: Only consider emails received after this epoch time.
            preferred_sender: Prefer email rows whose metadata contains this sender name.

        Returns:
            6-digit OTP code, or None if not found.
        """
        try:
            self.navigate_to_outlook()

            if not outlook_perform_sign_in(self.page):
                logger.error("Failed to login to Outlook")
                return None

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
                logger.error(
                    f"OTP not found in Outlook within {int(timeout)}s while checking OTP folder"
                )

            return otp
        except Exception as e:
            logger.error(f"Error in unified OTP retrieval workflow: {str(e).splitlines()[0]}")
            return None

    def get_latest_otp_from_folder(
        self,
        timeout: float = 60.0,
        refresh_interval: float = 5.0,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Optional[str]:
        """Fetch the latest OTP from the OTP folder with retry/refresh logic.

        Args:
            timeout: Total timeout in seconds.
            refresh_interval: Seconds between page refreshes.
            sent_after_epoch: Only consider emails received after this epoch time.
            preferred_sender: Prefer email rows whose metadata contains this sender name.

        Returns:
            OTP code if found, None otherwise.
        """

        def _ensure_outlook_mail_shell() -> bool:
            if "outlook.office.com" not in self.page.url:
                self.page.wait_for_timeout(3000)
            if "outlook.office.com" not in self.page.url or "/mail" not in self.page.url:
                try:
                    self.page.goto(
                        "https://outlook.office.com/mail/",
                        wait_until="domcontentloaded",
                        timeout=30000,
                    )
                    self.page.wait_for_timeout(2000)
                except Exception as e:
                    logger.error(
                        f"Failed to navigate to Outlook mail shell: {str(e).splitlines()[0]}"
                    )
                    return False
            try:
                self.folder_tree.first.wait_for(state="visible", timeout=20000)
            except Exception as e:
                logger.error(f"Folder tree not visible: {str(e).splitlines()[0]}")
                return False
            return True

        try:
            if not _ensure_outlook_mail_shell():
                return None
            if not self.navigate_to_otp_folder():
                logger.error("Could not navigate to OTP folder")
                return None

            start_time = time.time()
            cycle = 0

            while (time.time() - start_time) < timeout:
                cycle += 1
                try:
                    self.page.wait_for_timeout(2000)

                    first_email = self._select_otp_email_row(
                        sent_after_epoch=sent_after_epoch,
                        preferred_sender=preferred_sender,
                    )

                    try:
                        selected_meta = self._get_email_row_metadata(first_email)
                    except Exception:
                        selected_meta = ""
                    logger.debug(f"Selected row metadata: {selected_meta[:300]}")

                    if not self._click_email_row(first_email):
                        raise Exception("Failed to click selected OTP email row")

                    try:
                        self.email_document_container.wait_for(state="attached", timeout=10000)
                    except Exception:
                        self.page.wait_for_timeout(3000)

                    otp = self.extract_otp_from_email()
                    if otp:
                        return otp

                    try:
                        self.close_email_button.click(timeout=5000)
                        self.page.wait_for_timeout(1000)
                    except Exception as e:
                        logger.debug(f"Close email failed: {e}")

                except Exception as e:
                    logger.warning(
                        f"Cycle {cycle} failed while opening/reading OTP email: {str(e).splitlines()[0]}"
                    )

                # Refresh and retry
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    break

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
                    self._save_debug_screenshot("otp_folder_lost_after_reload")
                    return None

            logger.error(f"Failed to extract OTP from OTP folder after {timeout}s")
            self.fail(f"OTP not found in Outlook OTP folder after {int(timeout)}s")

        except Exception as e:
            logger.error(f"Error retrieving OTP from folder: {str(e).splitlines()[0]}")
            return None

    # ─── Tracking Number Search ──────────────────────────────────────────

    def search_tracking_number(self, tracking_number: str, timeout: float) -> Optional[Locator]:
        """Search tracking number repeatedly until result appears or retry window expires."""
        tracking_result_row = self._get_tracking_result_row(tracking_number)
        search_window_ms = max(int(timeout), 300000)
        search_deadline = time.time() + (search_window_ms / 1000.0)

        while time.time() < search_deadline:
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

    def open_client_review_documents_page(
        self,
        tracking_number: str,
        timeout: float = 30000,
    ) -> Optional[Page]:
        """Login/open Outlook, search by tracking number, click REVIEW DOCUMENTS.

        Returns the newly opened page, or None on failure.
        """
        if not tracking_number:
            logger.warning("[outlook-tracking] Empty tracking number")
            return None

        try:
            self.navigate_to_outlook()
            if not outlook_perform_sign_in(self.page):
                logger.error("[outlook-tracking] Outlook login failed")
                return None

            # Wait for the search box to be ready
            try:
                self.search_tracking_input_combobox.wait_for(state="visible", timeout=60000)
                logger.info("[outlook-tracking] Search box is visible, Outlook is ready")
            except Exception:
                logger.warning(
                    "[outlook-tracking] Search box not visible after 60s, waiting for page to stabilize"
                )
                self.page.wait_for_timeout(10000)
                self.search_tracking_input_combobox.wait_for(state="visible", timeout=30000)

            tracking_result_row = self.search_tracking_number(tracking_number, timeout)
            if not tracking_result_row:
                self.fail(
                    f"Tracking number result not found in Outlook search: '{tracking_number}'"
                )
            tracking_result_row.click(timeout=10000)

            self._capture_preferred_otp_sender(tracking_result_row, tracking_number)

            review_documents_timeout = max(int(timeout), 90000)
            self.review_documents_action_link.wait_for(
                state="visible", timeout=review_documents_timeout
            )

            actual_href = self._extract_real_href_from_review_link()

            new_page = self._click_review_documents_link(
                tracking_result_row, review_documents_timeout
            )
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

            # Handle email security proxy interception
            new_url = new_page.url.lower()
            is_intercepted = (
                "safelink" in new_url
                or "url=null" in new_url
                or "protect.checkpoint.com" in new_url
            )
            if is_intercepted:
                logger.warning(
                    f"[outlook-tracking] Email security proxy intercepted: {new_page.url}"
                )
                if (
                    actual_href
                    and "protect.checkpoint.com" not in actual_href.lower()
                    and "safelink" not in actual_href.lower()
                ):
                    logger.info(
                        f"[outlook-tracking] Navigating directly to real URL: {actual_href}"
                    )
                    new_page.goto(actual_href, wait_until="domcontentloaded", timeout=60000)
                else:
                    logger.error("[outlook-tracking] No valid href to bypass email security proxy")
                    return None

            logger.info("[outlook-tracking] REVIEW DOCUMENTS opened in new tab")
            return new_page
        except AssertionError:
            raise
        except Exception as e:
            logger.error(
                f"[outlook-tracking] Failed to open REVIEW DOCUMENTS from tracking number {tracking_number}: {str(e).splitlines()[0]}"
            )
            return None

    # ─── Private: Email Row Selection ────────────────────────────────────

    def _select_otp_email_row(
        self,
        sent_after_epoch: float = None,
        preferred_sender: str = None,
    ) -> Locator:
        """Select the best email row to open for OTP extraction.

        Raises Exception if no suitable row is found.
        """
        docusign_count = self.docusign_email_row.count()
        email_list_count = self.email_list.count()
        preferred_sender_lower = (preferred_sender or "").strip().lower()
        min_allowed_epoch = (sent_after_epoch - 90) if sent_after_epoch else None

        if docusign_count > 0:
            first_email = self._find_first_matching_docusign_verification_row()

            if sent_after_epoch:
                first_email = first_email or self._select_closest_email_row_after_send(
                    docusign_count,
                    sent_after_epoch,
                    preferred_sender_lower,
                    min_allowed_epoch,
                    require_sender=bool(preferred_sender_lower),
                )

            if not first_email and sent_after_epoch:
                first_email = self._select_closest_email_row_after_send(
                    docusign_count,
                    sent_after_epoch,
                    preferred_sender_lower,
                    min_allowed_epoch,
                    require_sender=False,
                )

            if sent_after_epoch and not first_email:
                logger.debug("No email found at/near send-now time yet; waiting for refresh")
                raise Exception("No near/post-send OTP email yet")

            if not first_email and preferred_sender_lower:
                for idx in range(min(docusign_count, 3)):
                    candidate = self.docusign_email_row.nth(idx)
                    row_meta = self._get_email_row_metadata(candidate)
                    if preferred_sender_lower in row_meta.lower():
                        first_email = candidate
                        logger.debug(f"Selected row {idx} by sender-only filter")
                        break

            if not first_email:
                first_email = self.docusign_email_row.first
            return first_email

        if email_list_count > 0:
            return self.email_list.first

        # Retry once after a short wait
        self.page.wait_for_timeout(3000)
        docusign_count = self.docusign_email_row.count()
        email_list_count = self.email_list.count()
        if docusign_count > 0:
            return self.docusign_email_row.first
        if email_list_count > 0:
            return self.email_list.first

        raise Exception("No emails found after retry")

    def _find_first_matching_docusign_verification_row(self) -> Optional[Locator]:
        """Find the first email row containing both 'DocuSign' and 'verification'."""
        rows = self.email_list
        for idx in range(rows.count()):
            candidate = rows.nth(idx)
            try:
                row_text = (candidate.inner_text(timeout=2000) or "").lower()
            except Exception:
                continue
            if "docusign" in row_text and "verification" in row_text:
                logger.debug(f"First DocuSign verification row found at index {idx}")
                return candidate
        return None

    def _select_closest_email_row_after_send(
        self,
        docusign_count: int,
        sent_after_epoch: float,
        preferred_sender_lower: str,
        min_allowed_epoch: float,
        require_sender: bool,
    ) -> Optional[Locator]:
        """Select the DocuSign row closest in time after sent_after_epoch."""
        best_candidate = None
        best_delta = None
        best_index = None

        for idx in range(min(docusign_count, 3)):
            candidate = self.docusign_email_row.nth(idx)
            row_meta = self._get_email_row_metadata(candidate)
            row_meta_lower = row_meta.lower()
            row_epoch = self._parse_email_row_time_to_epoch(row_meta)

            if (
                require_sender
                and preferred_sender_lower
                and preferred_sender_lower not in row_meta_lower
            ):
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

    # ─── Private: Email Row Helpers ──────────────────────────────────────

    def _click_email_row(self, row: Locator) -> bool:
        """Try multiple strategies to click an email row."""
        logger.debug("Attempting to open selected email row")
        for strategy_name, strategy in [
            ("direct", lambda: row.click(timeout=10000)),
            ("force", lambda: row.click(timeout=5000, force=True)),
            ("double_click", lambda: row.dblclick(timeout=5000)),
            ("js", lambda: row.evaluate("el => el.click()")),
        ]:
            try:
                strategy()
                return True
            except Exception as click_err:
                logger.debug(f"Email row click failed via {strategy_name}: {click_err}")
        return False

    def _get_email_row_metadata(self, row: Locator) -> str:
        """Get combined inner text + aria-label from an email row."""
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
        """Parse relative/absolute time from email row text into epoch seconds."""
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
            row_epoch = time.mktime(
                (
                    now_local.tm_year,
                    now_local.tm_mon,
                    now_local.tm_mday,
                    hour,
                    minute,
                    59,
                    now_local.tm_wday,
                    now_local.tm_yday,
                    now_local.tm_isdst,
                )
            )
            if row_epoch > now_epoch + 120:
                row_epoch -= 24 * 3600
            return row_epoch

        return 0.0

    # ─── Private: Tracking Search Helpers ────────────────────────────────

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
                logger.debug(
                    f"[outlook-tracking] Search trigger failed via {strategy_name}: {strategy_error}"
                )
        return False

    def _get_tracking_search_trigger_strategies(self):
        """Return all supported strategies to trigger Outlook search."""
        return [
            (
                "search box Enter",
                lambda: self.search_tracking_input_combobox.press("Enter", timeout=3000),
            ),
            ("page keyboard Enter", lambda: self.page.keyboard.press("Enter")),
            ("search icon click", lambda: self.search_tracking_button.click(timeout=5000)),
            (
                "search box search shortcut",
                lambda: self.search_tracking_input_combobox.press("Control+Enter", timeout=3000),
            ),
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

    # ─── Private: Review Documents Helpers ───────────────────────────────

    def _capture_preferred_otp_sender(
        self, tracking_result_row: Locator, tracking_number: str
    ) -> None:
        """Extract and store the preferred OTP sender from a tracking result row."""
        try:
            row_meta = ""
            try:
                row_meta = tracking_result_row.inner_text(timeout=3000) or ""
            except Exception:
                pass
            if not row_meta:
                try:
                    row_meta = tracking_result_row.get_attribute("aria-label", timeout=3000) or ""
                except Exception:
                    pass

            preferred_sender = None
            for raw_line in row_meta.splitlines():
                line = raw_line.strip()
                if not line or len(line) < 3:
                    continue
                lowered = line.lower()
                if tracking_number.lower() in lowered:
                    continue
                if re.search(
                    r"docusign|verification|review documents|\b(am|pm)\b|\b(mon|tue|wed|thu|fri|sat|sun)\b",
                    lowered,
                ):
                    continue
                if re.search(r"\d", line):
                    continue
                preferred_sender = line
                break

            self._preferred_otp_sender = preferred_sender
            if preferred_sender:
                logger.debug(
                    f"[outlook-tracking] Preferred OTP sender captured: {preferred_sender}"
                )
        except Exception as e:
            logger.debug(f"[outlook-tracking] Could not capture preferred OTP sender: {e}")

    def _extract_real_href_from_review_link(self) -> Optional[str]:
        """Extract the real URL from the REVIEW DOCUMENTS link, unwrapping security proxies."""
        try:
            raw_href = self.review_documents_action_link.get_attribute("href", timeout=5000)
            if not raw_href:
                return None

            from urllib.parse import unquote

            checkpoint_match = re.search(r"___(https?://.+?)___\.", raw_href)
            safe_links_match = re.search(r"[?&]url=([^&]+)", raw_href)

            if checkpoint_match:
                actual_href = checkpoint_match.group(1)
            elif safe_links_match:
                actual_href = unquote(safe_links_match.group(1))
            elif (
                "protect.checkpoint.com" not in raw_href.lower()
                and "safelink" not in raw_href.lower()
            ):
                actual_href = raw_href
            else:
                actual_href = None

            logger.info(f"[outlook-tracking] REVIEW DOCUMENTS raw href: {raw_href[:120]}")
            logger.info(f"[outlook-tracking] REVIEW DOCUMENTS actual href: {actual_href}")
            return actual_href
        except Exception:
            logger.debug("[outlook-tracking] Could not capture href from REVIEW DOCUMENTS link")
            return None

    def _click_review_documents_link(self, tracking_result_row: Locator, timeout: int) -> Page:
        """Click the REVIEW DOCUMENTS link and return the new page."""
        try:
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                self.review_documents_action_link.click(timeout=timeout)
        except Exception:
            logger.warning("[outlook-tracking] Normal click failed, retrying with JS click")
            tracking_result_row.click(timeout=10000)
            self.page.wait_for_timeout(5000)
            self.review_documents_action_link.wait_for(state="visible", timeout=timeout)
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                self.review_documents_action_link.evaluate("el => el.click()")
        return new_page_info.value

    # ─── Private: Utility ────────────────────────────────────────────────

    def _save_debug_screenshot(self, label: str) -> None:
        """Save a debug screenshot with the given label."""
        try:
            os.makedirs("reports/screenshots", exist_ok=True)
            path = f"reports/screenshots/{label}_{int(time.time())}.png"
            self.page.screenshot(path=path, full_page=True)
            logger.info(f"Screenshot saved: {path}")
        except Exception:
            pass
