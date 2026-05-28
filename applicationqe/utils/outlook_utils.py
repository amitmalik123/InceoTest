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

from configparser import ConfigParser

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
        self.email = email or os.getenv("OUTLOOK_EMAIL", "")
        self.password = password or os.getenv("OUTLOOK_PASSWORD", "")
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
        msg_id_str = email_obj.id if isinstance(email_obj.id, str) else email_obj.id.decode("utf-8")
        status, data = mail.fetch(msg_id_str, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return []

        raw: bytes = data[0][1]  # type: ignore[index]
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


# Lazy import to avoid circular dependency (pages.base_page imports from utils)
from pages.base_page import BasePage  # noqa: E402
from playwright.sync_api import Locator, Page  # noqa: E402


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

        _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(_base_dir, "config", "naw", "config.properties")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        parser = ConfigParser()
        parser.read(config_path)
        cls._config = parser
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
                logger.error(f"Error retrieving OTP via IMAP: {str(e).splitlines()[0]}")
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
        search_window_ms = max(int(timeout), 300000)
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

            # Smart wait: wait for the search box to be ready instead of a blind 30s sleep
            try:
                self.search_tracking_input_combobox.wait_for(state="visible", timeout=60000)
                logger.info("[outlook-tracking] Search box is visible, Outlook is ready")
            except Exception:
                logger.warning("[outlook-tracking] Search box not visible after 60s, waiting for page to stabilize")
                self.page.wait_for_timeout(10000)
                self.search_tracking_input_combobox.wait_for(state="visible", timeout=30000)

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

            review_documents_timeout = max(int(timeout), 90000)
            self.review_documents_action_link.wait_for(state="visible", timeout=review_documents_timeout)

            # Capture the actual href before clicking (email security proxies mangle URLs)
            actual_href = None
            try:
                raw_href = self.review_documents_action_link.get_attribute("href", timeout=5000)
                if raw_href:
                    from urllib.parse import unquote
                    # Check Point Harmony: protect.checkpoint.com/v2/.../___REAL_URL___.token
                    checkpoint_match = re.search(r"___(https?://.+?)___\.", raw_href)
                    # Microsoft Safe Links: safelinks.protection.outlook.com/?url=ENCODED
                    safe_links_match = re.search(r"[?&]url=([^&]+)", raw_href)
                    if checkpoint_match:
                        actual_href = checkpoint_match.group(1)
                    elif safe_links_match:
                        actual_href = unquote(safe_links_match.group(1))
                    elif "protect.checkpoint.com" not in raw_href.lower() and "safelink" not in raw_href.lower():
                        actual_href = raw_href
                    logger.info(f"[outlook-tracking] REVIEW DOCUMENTS raw href: {raw_href[:120]}")
                    logger.info(f"[outlook-tracking] REVIEW DOCUMENTS actual href: {actual_href}")
            except Exception:
                logger.debug("[outlook-tracking] Could not capture href from REVIEW DOCUMENTS link")

            try:
                with self.page.context.expect_page(timeout=review_documents_timeout) as new_page_info:
                    self.review_documents_action_link.click(timeout=review_documents_timeout)
            except Exception:
                logger.warning("[outlook-tracking] Normal click failed, retrying with JS click")
                tracking_result_row.click(timeout=10000)
                self.page.wait_for_timeout(5000)
                self.review_documents_action_link.wait_for(state="visible", timeout=review_documents_timeout)
                with self.page.context.expect_page(timeout=review_documents_timeout) as new_page_info:
                    self.review_documents_action_link.evaluate("el => el.click()")

            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

            # Handle email security proxy interception (Safe Links, Check Point, etc.)
            new_url = new_page.url.lower()
            is_intercepted = "safelink" in new_url or "url=null" in new_url or "protect.checkpoint.com" in new_url
            if is_intercepted:
                logger.warning(f"[outlook-tracking] Email security proxy intercepted: {new_page.url}")
                if actual_href and "protect.checkpoint.com" not in actual_href.lower() and "safelink" not in actual_href.lower():
                    logger.info(f"[outlook-tracking] Navigating directly to real URL: {actual_href}")
                    new_page.goto(actual_href, wait_until="domcontentloaded", timeout=60000)
                else:
                    logger.error("[outlook-tracking] No valid href to bypass email security proxy")
                    return None

            logger.info("[outlook-tracking] REVIEW DOCUMENTS opened in new tab")
            return new_page
        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"[outlook-tracking] Failed to open REVIEW DOCUMENTS from tracking number {tracking_number}: {str(e).splitlines()[0]}")
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
            
            # Wait for DOM to be ready instead of networkidle (headless compatible)
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=10000)
            except Exception as e:
                logger.warning(f"DOM load wait timeout, continuing anyway: {str(e).splitlines()[0]}")
        except Exception as e:
            logger.error(f"Failed to navigate to Outlook: {str(e).splitlines()[0]}")
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
        
        # Check if we're already on the mail page (already logged in)
        if "/mail/" in self.page.url:
            
            # CRITICAL: Verify page is actually stable and not about to redirect
            # Wait for key UI elements to confirm we're really on Outlook mail page
            try:
                # Wait for URL to stabilize - check it doesn't change
                initial_url = self.page.url
                self.page.wait_for_timeout(2000)
                
                # Check if URL changed (session expired/redirected)
                if self.page.url != initial_url:
                    # If redirected to auth page, session expired - need to re-login
                    if 'login.microsoftonline.com' in self.page.url:
                        # Fall through to login code below
                        pass
                    else:
                        return True
                else:
                    # URL stable, verify key UI elements are present
                    # Look for inbox button or folder list to confirm we're on actual mail page
                    inbox_count = self.inbox_button.count()
                    folder_list_count = self.folder_tree.count()
                    
                    if inbox_count > 0 or folder_list_count > 0:
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
            email_input.fill(email)
            
            # Find and click next button
            next_btn = self._find_visible_locator_from_selectors(
                self.LOGIN_NEXT_BUTTON_SELECTORS,
                timeout=5000,
                description="next button"
            )
            
            if next_btn:
                next_btn.click()
                self.page.wait_for_timeout(2000)
            else:
                logger.error("Next button not found after email")
            
            # Find password input
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
            password_input.fill(password)
            
            # Click next/sign in button
            signin_btn = self._find_visible_locator_from_selectors(
                self.LOGIN_SIGNIN_BUTTON_SELECTORS,
                timeout=5000,
                description="sign-in button"
            )
            
            if signin_btn:
                signin_btn.click()
                logger.debug("Sign in button clicked, waiting for navigation...")
            else:
                logger.warning("OUTLOOK_LOGIN: Sign-in button not found; continuing to URL checks")
            
            # Wait for navigation to complete - use URL change instead of networkidle (headless compatible)
            try:
                # Wait for URL to change away from login page
                self.page.wait_for_function(
                    "() => !window.location.href.includes('login.microsoftonline.com')",
                    timeout=10000
                )
                logger.info(f"OUTLOOK_LOGIN: Navigated away from login page to: {self.page.url}")
            except Exception as e:
                logger.debug(f"URL change wait timed out, checking current URL...")
            
            # Handle "Stay signed in?" dialog if present
            logger.debug("Checking for stay signed in dialog")
            try:
                stay_no_btn = self._find_visible_locator_from_selectors(
                    self.LOGIN_STAY_SIGNED_IN_NO_SELECTORS,
                    timeout=2000,
                    description="stay signed in 'No' button"
                )
                if stay_no_btn:
                    logger.debug("Found 'Stay signed in?' dialog, clicking 'No'")
                    stay_no_btn.click(timeout=5000)
                    # Wait for navigation after clicking No
                    self.page.wait_for_load_state('domcontentloaded', timeout=5000)
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
                        break
                    except:
                        continue
                
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
            logger.error(f"OUTLOOK_LOGIN: Login failed with exception: {str(e).splitlines()[0]}")
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
                logger.warning(f"Error checking for DocuSign email: {str(e).splitlines()[0]}")
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
            logger.error(f"Failed to open email: {str(e).splitlines()[0]}")
            return False
    
    def extract_otp_from_email(self) -> Optional[str]:
        """
        Extract OTP from currently opened email

        Returns:
            OTP code (6 digits) or None
        """
        
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
                    os.makedirs("reports/screenshots", exist_ok=True)
                    screenshot_path = f"reports/screenshots/outlook_email_empty_{int(time.time())}.png"
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
            logger.error(f"Error extracting OTP from email: {str(e).splitlines()[0]}")
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
            logger.error(f"Error in unified OTP retrieval workflow: {str(e).splitlines()[0]}")
            return None
    
    def close_email(self):
        """Close currently opened email and return to inbox"""
        logger.info("Closing email")
        
        try:
            self.close_email_button.click()
            self.page.wait_for_timeout(1000)
            logger.info("Email closed successfully")
        except Exception as e:
            logger.warning(f"Error closing email: {str(e).splitlines()[0]}")
    
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
                    logger.info("OTP folder opened successfully")
                    self.page.wait_for_timeout(2000)
                    return True
                except Exception as click_err:
                    logger.debug(f"OTP click failed via {label}: {click_err}")

            logger.error("OTP folder not found or not clickable")
            try:
                os.makedirs("reports/screenshots", exist_ok=True)
                screenshot_path = f"reports/screenshots/otp_folder_not_found_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception:
                pass
            return False

        except Exception as e:
            logger.error(f"Error navigating to OTP folder: {str(e).splitlines()[0]}")
            try:
                os.makedirs("reports/screenshots", exist_ok=True)
                screenshot_path = f"reports/screenshots/otp_folder_navigation_exception_{int(time.time())}.png"
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

        def _ensure_outlook_mail_shell() -> bool:
            if "outlook.office.com" not in self.page.url:
                self.page.wait_for_timeout(3000)

            if "outlook.office.com" not in self.page.url or "/mail" not in self.page.url:
                try:
                    self.page.goto("https://outlook.office.com/mail/", wait_until="domcontentloaded", timeout=30000)
                    self.page.wait_for_timeout(2000)
                except Exception as e:
                    logger.error(f"Failed to navigate to Outlook mail shell: {str(e).splitlines()[0]}")
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
                        return otp
                    else:
                        
                        # Close email and refresh to try again
                        try:
                            self.close_email_button.click(timeout=5000)
                            self.page.wait_for_timeout(1000)
                        except Exception as e:
                            logger.debug(f"Close email failed: {e}")
                    
                except Exception as e:
                    logger.warning(f"Cycle {cycle} failed while opening/reading OTP email: {str(e).splitlines()[0]}")
                    
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
                            os.makedirs("reports/screenshots", exist_ok=True)
                            screenshot_path = f"reports/screenshots/otp_folder_lost_after_reload_{int(time.time())}.png"
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
            logger.error(f"Error retrieving OTP from folder: {str(e).splitlines()[0]}")
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
            logger.error(f"Error fetching OTP from Inbox: {str(e).splitlines()[0]}")
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
                return otp_candidate

        return None

    @staticmethod
    def validate_otp_format(otp: str) -> bool:
        """Validate OTP format (6 digits)."""
        if not otp or not re.match(r"^\d{6}$", otp):
            logger.warning(f"Invalid OTP format: {otp}")
            return False
        return True
