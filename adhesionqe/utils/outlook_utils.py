"""
Outlook Email Utility

Reads Outlook / Office 365 emails and extracts data based on subject, sender, etc.

Uses IMAP with username + password. No extra dependencies — only Python's built-in
``imaplib`` and ``email`` modules.

Works with Outlook.com, Office 365, Hotmail, and on-prem Exchange (IMAP enabled).

Quick Start:
    from utils.outlook_utils import OutlookClient

    client = OutlookClient(
        email="your.name@company.com",
        password="your-password-or-app-password",
    )

    # Get emails by subject
    emails = client.get_emails_by_subject("Invoice #12345")
    print(emails[0].body_text)

    # Get latest email matching subject
    email = client.get_latest_email_by_subject("Password Reset")

    # Extract a 6-digit OTP
    otp = client.extract_otp_from_email(email)

    # One-shot: find email by subject + extract data via regex
    code = client.fetch_data_from_email_by_subject(
        subject="Verification Code",
        pattern=r"\\b(\\d{6})\\b",
        group=1,
    )

    # Always close when done (or use context manager)
    client.close()

    # Context-manager usage (auto-closes):
    with OutlookClient(email="...", password="...") as client:
        email = client.get_latest_email_by_subject("Welcome")

Note on App Passwords:
    If your account has Multi-Factor Authentication (MFA) enabled, you need
    an *App Password* instead of your regular password. Generate one at:
    https://account.live.com/proofs/AppPassword  (personal)
    or via your org's Microsoft 365 admin portal (work/school).
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
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import Any, List, Optional, Pattern, Union

logger = logging.getLogger(__name__)

# Default IMAP settings for Outlook / Office 365
DEFAULT_IMAP_SERVER = "outlook.office365.com"
DEFAULT_IMAP_PORT = 993


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class OutlookEmail:
    """Represents a single Outlook email message."""

    id: Union[str, bytes]
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


@dataclass
class OutlookAttachment:
    """Represents an email attachment."""

    id: str
    name: str
    content_type: str
    size: int
    content_bytes: Optional[bytes] = None


# ---------------------------------------------------------------------------
# IMAP-based Outlook Client (username + password)
# ---------------------------------------------------------------------------
class OutlookClient:
    """
    Outlook email client using IMAP with username and password.

    Connects to Outlook / Office 365 over IMAP-SSL and provides methods to
    search, fetch, and extract data from emails.

    No extra dependencies required — uses Python's built-in ``imaplib`` and
    ``email`` modules only.

    Args:
        email: Outlook email address (e.g. ``user@company.com``).
               Falls back to ``OUTLOOK_EMAIL`` env var.
        password: Account password or App Password (if MFA is enabled).
                  Falls back to ``OUTLOOK_PASSWORD`` env var.
        imap_server: IMAP server hostname.
                     Defaults to ``outlook.office365.com``.
        imap_port: IMAP port. Defaults to ``993`` (SSL).
        folder: Mailbox folder to operate on. Defaults to ``"INBOX"``.

    Example:
        client = OutlookClient(
            email="john.doe@company.com",
            password="my-app-password",
        )
        emails = client.get_emails_by_subject("Monthly Report")
        client.close()
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        imap_server: str = DEFAULT_IMAP_SERVER,
        imap_port: int = DEFAULT_IMAP_PORT,
        folder: str = "INBOX",
    ):
        self.email: str = str(email) if email is not None else os.getenv("OUTLOOK_EMAIL", "")
        self.password: str = (
            str(password) if password is not None else os.getenv("OUTLOOK_PASSWORD", "")
        )
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.folder = folder

        if not self.email or not self.password:
            raise ValueError(
                "Email and password are required. "
                "Pass them as arguments or set OUTLOOK_EMAIL / OUTLOOK_PASSWORD env vars."
            )

        self._mail: Optional[imaplib.IMAP4_SSL] = None
        self._connect()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------
    def __enter__(self) -> "OutlookClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
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
                "If MFA is enabled, use an App Password. "
                f"Error: {e}"
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

    def select_folder(self, folder: str) -> None:
        """
        Switch to a different mailbox folder.

        Args:
            folder: Folder name (e.g. ``"INBOX"``, ``"Sent"``,
                    ``"Drafts"``, ``"Junk"``, ``"Archive"``).
        """
        mail = self._ensure_connection()
        status, _ = mail.select(folder)
        if status != "OK":
            raise RuntimeError(f"Failed to select folder '{folder}'")
        self.folder = folder
        logger.info("Switched to folder '%s'", folder)

    def list_folders(self) -> List[str]:
        """
        List all available mailbox folders.

        Returns:
            List of folder names.
        """
        mail = self._ensure_connection()
        status, folder_list = mail.list()
        if status != "OK":
            return []

        folders: List[str] = []
        for item in folder_list:
            if isinstance(item, bytes):
                decoded = item.decode("utf-8", errors="replace")
                match = re.search(r'"([^"]*)"$', decoded)
                if match:
                    folders.append(match.group(1))
        return folders

    # ------------------------------------------------------------------
    # IMAP search helpers
    # ------------------------------------------------------------------
    def _search(self, criteria: str) -> List[bytes]:
        """
        Run an IMAP SEARCH command and return list of message IDs.

        Args:
            criteria: IMAP search criteria string
                (e.g. ``'SUBJECT "Invoice"'``, ``'FROM "noreply@example.com"'``).

        Returns:
            List of message IDs (bytes).
        """
        mail = self._ensure_connection()
        status, data = mail.search(None, criteria)
        if status != "OK":
            logger.warning("IMAP search failed for criteria: %s", criteria)
            return []

        msg_ids = data[0].split()
        logger.debug("IMAP search '%s' returned %d messages", criteria, len(msg_ids))
        return msg_ids

    def _fetch_email(self, msg_id: bytes) -> Optional[OutlookEmail]:
        """
        Fetch and parse a single email by its IMAP message ID.

        Args:
            msg_id: IMAP message ID (bytes).

        Returns:
            Parsed OutlookEmail or None on failure.
        """
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

        # --- Subject ---
        raw_subject = msg.get("Subject", "")
        subject = self._decode_header_value(raw_subject)

        # --- From ---
        from_address = self._extract_email_address(msg.get("From", ""))

        # --- To ---
        to_raw = msg.get("To", "")
        to_addresses = [
            self._extract_email_address(addr.strip()) for addr in to_raw.split(",") if addr.strip()
        ]

        # --- CC ---
        cc_raw = msg.get("Cc", "") or ""
        cc_addresses = [
            self._extract_email_address(addr.strip()) for addr in cc_raw.split(",") if addr.strip()
        ]

        # --- Date ---
        date_str = msg.get("Date", "")
        try:
            dt = parsedate_to_datetime(date_str)
            received_datetime = dt.isoformat()
        except Exception:
            received_datetime = date_str

        # --- Body ---
        body_text = ""
        body_html = ""
        has_attachments = False

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in disposition.lower():
                    has_attachments = True
                    continue

                payload = part.get_payload(decode=True)
                if payload is None or not isinstance(payload, bytes):
                    continue

                charset = part.get_content_charset() or "utf-8"
                try:
                    decoded = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    decoded = payload.decode("utf-8", errors="replace")

                if content_type == "text/plain" and not body_text:
                    body_text = decoded
                elif content_type == "text/html" and not body_html:
                    body_html = decoded
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload and isinstance(payload, bytes):
                charset = msg.get_content_charset() or "utf-8"
                try:
                    decoded = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    decoded = payload.decode("utf-8", errors="replace")

                if content_type == "text/html":
                    body_html = decoded
                else:
                    body_text = decoded

        # If we only have HTML, derive plain text
        if not body_text and body_html:
            body_text = self._html_to_text(body_html)

        # --- Importance ---
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
            is_read=True,  # Fetching via IMAP marks it as read
            importance=importance,
            cc_addresses=cc_addresses,
            conversation_id=msg.get("Message-ID"),
        )

    # ------------------------------------------------------------------
    # Header / address helpers
    # ------------------------------------------------------------------
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
        if match:
            return match.group(1).strip()
        return raw.strip()

    @staticmethod
    def _html_to_text(html_content: str) -> str:
        """Strip HTML tags and decode entities to get plain text."""
        text = re.sub(r"<br\s*/?>", "\n", html_content, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        return text.strip()

    # ------------------------------------------------------------------
    # Public API – Fetch emails
    # ------------------------------------------------------------------
    def get_emails_by_subject(
        self,
        subject: str,
        top: int = 10,
        exact_match: bool = False,
    ) -> List[OutlookEmail]:
        """
        Fetch emails whose subject contains (or exactly matches) the given text.

        Args:
            subject: Subject text to search for.
            top: Maximum number of results to return (newest first).
            exact_match: If True, subject must match exactly (case-insensitive).

        Returns:
            List of matching OutlookEmail objects, newest first.

        Example:
            emails = client.get_emails_by_subject("Monthly Report")
            for e in emails:
                print(e.subject, e.from_address, e.received_datetime)
        """
        criteria = f'SUBJECT "{subject}"'
        msg_ids = self._search(criteria)

        # Fetch newest first (reverse order), over-fetch in case exact_match filters some out
        msg_ids = list(reversed(msg_ids))[: top * 2]

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
        """
        Get the most recent email matching the given subject.

        Args:
            subject: Subject text to search for.
            exact_match: If True, subject must match exactly (case-insensitive).

        Returns:
            The latest matching OutlookEmail, or None if not found.

        Example:
            email = client.get_latest_email_by_subject("Password Reset")
            if email:
                print(email.body_text)
        """
        emails = self.get_emails_by_subject(subject, top=1, exact_match=exact_match)
        return emails[0] if emails else None

    def get_emails_by_sender(
        self,
        sender_email: str,
        top: int = 10,
    ) -> List[OutlookEmail]:
        """
        Fetch emails from a specific sender.

        Args:
            sender_email: Sender email address.
            top: Maximum number of results.

        Returns:
            List of matching OutlookEmail objects, newest first.
        """
        criteria = f'FROM "{sender_email}"'
        msg_ids = self._search(criteria)
        msg_ids = list(reversed(msg_ids))[:top]

        emails: List[OutlookEmail] = []
        for mid in msg_ids:
            email_obj = self._fetch_email(mid)
            if email_obj:
                emails.append(email_obj)

        logger.info("Found %d emails from sender %r", len(emails), sender_email)
        return emails

    def get_emails_by_date_range(
        self,
        since: Optional[datetime] = None,
        before: Optional[datetime] = None,
        top: int = 25,
    ) -> List[OutlookEmail]:
        """
        Fetch emails within a date range.

        Args:
            since: Start date (inclusive). Defaults to 7 days ago.
            before: End date (exclusive). Defaults to tomorrow.
            top: Maximum number of results.

        Returns:
            List of OutlookEmail objects, newest first.
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=7)
        if before is None:
            before = datetime.now(timezone.utc) + timedelta(days=1)

        since_str = since.strftime("%d-%b-%Y")
        before_str = before.strftime("%d-%b-%Y")
        criteria = f"SINCE {since_str} BEFORE {before_str}"

        msg_ids = self._search(criteria)
        msg_ids = list(reversed(msg_ids))[:top]

        emails: List[OutlookEmail] = []
        for mid in msg_ids:
            email_obj = self._fetch_email(mid)
            if email_obj:
                emails.append(email_obj)

        logger.info("Found %d emails between %s and %s", len(emails), since_str, before_str)
        return emails

    def get_unread_emails(self, top: int = 25) -> List[OutlookEmail]:
        """
        Fetch unread emails.

        Args:
            top: Maximum number of results.

        Returns:
            List of unread OutlookEmail objects, newest first.
        """
        msg_ids = self._search("UNSEEN")
        msg_ids = list(reversed(msg_ids))[:top]

        emails: List[OutlookEmail] = []
        for mid in msg_ids:
            email_obj = self._fetch_email(mid)
            if email_obj:
                emails.append(email_obj)

        logger.info("Found %d unread emails", len(emails))
        return emails

    def search_emails(
        self,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        since: Optional[datetime] = None,
        before: Optional[datetime] = None,
        unseen_only: bool = False,
        body_contains: Optional[str] = None,
        top: int = 25,
    ) -> List[OutlookEmail]:
        """
        Advanced email search with multiple criteria (AND logic).

        Args:
            subject: Subject substring to match.
            sender: Sender email address.
            since: Emails received on or after this date.
            before: Emails received before this date.
            unseen_only: Only return unread emails.
            body_contains: Text to search in the email body.
            top: Maximum number of results.

        Returns:
            List of matching OutlookEmail objects, newest first.

        Example:
            emails = client.search_emails(
                subject="Report",
                sender="reports@company.com",
                since=datetime(2026, 1, 1),
                unseen_only=True,
            )
        """
        parts: List[str] = []
        if subject:
            parts.append(f'SUBJECT "{subject}"')
        if sender:
            parts.append(f'FROM "{sender}"')
        if since:
            parts.append(f'SINCE {since.strftime("%d-%b-%Y")}')
        if before:
            parts.append(f'BEFORE {before.strftime("%d-%b-%Y")}')
        if unseen_only:
            parts.append("UNSEEN")
        if body_contains:
            parts.append(f'BODY "{body_contains}"')

        criteria = " ".join(parts) if parts else "ALL"

        msg_ids = self._search(criteria)
        msg_ids = list(reversed(msg_ids))[:top]

        emails: List[OutlookEmail] = []
        for mid in msg_ids:
            email_obj = self._fetch_email(mid)
            if email_obj:
                emails.append(email_obj)

        logger.info("Advanced search returned %d emails (criteria: %s)", len(emails), criteria)
        return emails

    def wait_for_email_by_subject(
        self,
        subject: str,
        timeout: int = 120,
        poll_interval: int = 5,
        exact_match: bool = False,
        received_after: Optional[datetime] = None,
    ) -> Optional[OutlookEmail]:
        """
        Poll the mailbox until an email matching the subject arrives.

        Useful when a test triggers an action (e.g. password reset) and needs
        to wait for the resulting email.

        Args:
            subject: Subject text to search for.
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between polling attempts.
            exact_match: If True, subject must match exactly.
            received_after: Only consider emails received after this timestamp.
                            Defaults to now minus 2 minutes.

        Returns:
            The matching OutlookEmail, or None if timeout is reached.

        Example:
            # Trigger password reset, then wait for the email
            email = client.wait_for_email_by_subject(
                subject="Password Reset",
                timeout=60,
            )
        """
        if received_after is None:
            received_after = datetime.now(timezone.utc) - timedelta(minutes=2)

        deadline = time.time() + timeout
        attempt = 0

        while time.time() < deadline:
            attempt += 1
            logger.debug("Polling for email (attempt %d, subject=%r)", attempt, subject)

            # Re-select folder to see new messages
            mail = self._ensure_connection()
            mail.select(self.folder)

            emails = self.get_emails_by_subject(subject, top=5, exact_match=exact_match)

            for eml in emails:
                try:
                    received_dt = datetime.fromisoformat(
                        eml.received_datetime.replace("Z", "+00:00")
                    )
                    if received_dt.tzinfo is None:
                        received_dt = received_dt.replace(tzinfo=timezone.utc)
                    if received_after.tzinfo is None:
                        received_after = received_after.replace(tzinfo=timezone.utc)
                    if received_dt >= received_after:
                        logger.info("Found email matching %r on attempt %d", subject, attempt)
                        return eml
                except (ValueError, TypeError):
                    logger.info("Found email matching %r on attempt %d", subject, attempt)
                    return eml

            time.sleep(poll_interval)

        logger.warning("Timeout (%ds) waiting for email with subject %r", timeout, subject)
        return None

    # ------------------------------------------------------------------
    # Public API – Extract data from emails
    # ------------------------------------------------------------------
    def extract_pattern_from_email(
        self,
        email: OutlookEmail,
        pattern: Union[str, "Pattern[str]"],
        group: int = 0,
    ) -> Optional[str]:
        """
        Extract text matching a regex pattern from the email body.

        Common patterns:
          - OTP / verification codes: ``r"\\b\\d{6}\\b"``
          - Tracking numbers: ``r"tracking[:\\s#]*(\\w+)"``
          - URLs: ``r"https?://[^\\s<>\\"']+"``

        Args:
            email: The OutlookEmail to search.
            pattern: Regex pattern (string or compiled Pattern).
            group: Regex group to return (0 = entire match).

        Returns:
            Matched text or None.

        Example:
            otp = client.extract_pattern_from_email(email, r"\\b(\\d{6})\\b", group=1)
        """
        if isinstance(pattern, str):
            compiled = re.compile(pattern, re.IGNORECASE)
        else:
            compiled = pattern

        for text in [email.body_text, email.body_html]:
            if text:
                match = compiled.search(text)
                if match:
                    result = match.group(group)
                    logger.debug("Extracted %r from email %r", result, email.subject)
                    return result

        logger.debug("Pattern %s not found in email %r", pattern, email.subject)
        return None

    def extract_all_patterns_from_email(
        self,
        email: OutlookEmail,
        pattern: Union[str, "Pattern[str]"],
    ) -> List[str]:
        """
        Extract all occurrences of a regex pattern from the email body.

        Args:
            email: The OutlookEmail to search.
            pattern: Regex pattern.

        Returns:
            List of all matched strings.
        """
        if isinstance(pattern, str):
            compiled = re.compile(pattern, re.IGNORECASE)
        else:
            compiled = pattern

        results: List[str] = []
        for text in [email.body_text, email.body_html]:
            if text:
                results.extend(compiled.findall(text))

        logger.debug("Found %d matches for pattern in email %r", len(results), email.subject)
        return results

    def extract_links_from_email(self, email: OutlookEmail) -> List[str]:
        """
        Extract all HTTP(S) links from the email body.

        Args:
            email: The OutlookEmail to extract links from.

        Returns:
            List of URL strings (deduplicated, order preserved).
        """
        href_pattern = re.compile(r'href=["\']?(https?://[^"\'>\s]+)', re.IGNORECASE)
        url_pattern = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)

        links: List[str] = []

        if email.body_html:
            links.extend(href_pattern.findall(email.body_html))
        if not links and email.body_text:
            links.extend(url_pattern.findall(email.body_text))

        seen: set = set()
        unique: List[str] = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique.append(link)

        logger.debug("Extracted %d unique links from email %r", len(unique), email.subject)
        return unique

    def extract_otp_from_email(
        self,
        email: OutlookEmail,
        digit_count: int = 6,
    ) -> Optional[str]:
        """
        Extract a numeric OTP / verification code from the email body.

        Args:
            email: The OutlookEmail to search.
            digit_count: Expected number of digits in the OTP (default: 6).

        Returns:
            The OTP string or None.
        """
        pattern = rf"\b\d{{{digit_count}}}\b"
        return self.extract_pattern_from_email(email, pattern)

    # ------------------------------------------------------------------
    # Attachments
    # ------------------------------------------------------------------
    def get_attachments(self, email_obj: OutlookEmail) -> List[OutlookAttachment]:
        """
        Fetch attachments for a given email (re-fetches the raw message).

        Args:
            email_obj: The OutlookEmail whose attachments to fetch.

        Returns:
            List of OutlookAttachment objects with content bytes.
        """
        mail = self._ensure_connection()
        msg_id = email_obj.id
        msg_id_str = msg_id if isinstance(msg_id, str) else msg_id.decode("utf-8")
        status, data = mail.fetch(msg_id_str, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return []

        raw_any = data[0][1]
        if isinstance(raw_any, (bytes, bytearray)):
            raw: bytes = bytes(raw_any)
        else:
            # Fallback: convert to bytes via utf-8 representation
            raw = str(raw_any).encode("utf-8")
        msg = email_lib.message_from_bytes(raw)

        attachments: List[OutlookAttachment] = []
        for idx, part in enumerate(msg.walk()):
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" not in disposition.lower():
                continue

            filename = part.get_filename()
            if filename:
                filename = self._decode_header_value(filename)
            else:
                filename = f"attachment_{idx}"

            content: Optional[bytes] = part.get_payload(decode=True)  # type: ignore[assignment]
            attachments.append(
                OutlookAttachment(
                    id=str(idx),
                    name=filename,
                    content_type=part.get_content_type(),
                    size=len(content) if content else 0,
                    content_bytes=content,
                )
            )

        logger.info("Fetched %d attachments for email %r", len(attachments), email_obj.subject)
        return attachments

    def save_attachment(
        self,
        attachment: OutlookAttachment,
        save_dir: str = ".",
    ) -> str:
        """
        Save an attachment to disk.

        Args:
            attachment: The OutlookAttachment to save.
            save_dir: Directory to save the file in.

        Returns:
            Full path to the saved file.
        """
        import pathlib

        save_path = pathlib.Path(save_dir) / attachment.name
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if attachment.content_bytes:
            with open(save_path, "wb") as f:
                f.write(attachment.content_bytes)
            logger.info("Saved attachment %r to %s", attachment.name, save_path)
        else:
            logger.warning("Attachment %r has no content bytes", attachment.name)

        return str(save_path)

    # ------------------------------------------------------------------
    # Convenience: search + extract in one call
    # ------------------------------------------------------------------
    def fetch_data_from_email_by_subject(
        self,
        subject: str,
        pattern: Union[str, "Pattern[str]"],
        group: int = 0,
        exact_match: bool = False,
        wait: bool = False,
        wait_timeout: int = 120,
    ) -> Optional[str]:
        """
        One-shot: find the latest email by subject and extract data via regex.

        This is the most common workflow for test automation — trigger an
        action, then call this to grab an OTP, link, or confirmation text.

        Args:
            subject: Subject text to search for.
            pattern: Regex pattern to extract from the email body.
            group: Regex group to return.
            exact_match: If True, subject must match exactly.
            wait: If True, poll until the email arrives (up to wait_timeout).
            wait_timeout: Seconds to wait when ``wait=True``.

        Returns:
            Extracted text or None if email/pattern not found.

        Example:
            # Grab a 6-digit OTP from a "Verification Code" email
            otp = client.fetch_data_from_email_by_subject(
                subject="Verification Code",
                pattern=r"(\\d{6})",
                group=1,
                wait=True,
            )
        """
        if wait:
            email_obj = self.wait_for_email_by_subject(
                subject, timeout=wait_timeout, exact_match=exact_match
            )
        else:
            email_obj = self.get_latest_email_by_subject(subject, exact_match=exact_match)

        if not email_obj:
            logger.warning("No email found for subject %r", subject)
            return None

        return self.extract_pattern_from_email(email_obj, pattern, group=group)

    def get_email_body_by_subject(
        self,
        subject: str,
        exact_match: bool = False,
        prefer_html: bool = False,
    ) -> Optional[str]:
        """
        Get the full body content of the latest email matching the subject.

        Args:
            subject: Subject text to search for.
            exact_match: If True, subject must match exactly.
            prefer_html: If True, return HTML body; otherwise plain text.

        Returns:
            Email body string or None.

        Example:
            body = client.get_email_body_by_subject("Welcome to Our Platform")
            print(body)
        """
        email_obj = self.get_latest_email_by_subject(subject, exact_match=exact_match)
        if not email_obj:
            return None
        return email_obj.body_html if prefer_html else email_obj.body_text
