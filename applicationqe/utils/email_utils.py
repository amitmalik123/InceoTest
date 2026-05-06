"""
Email Testing Utilities

Provides integration with email testing services (MailHog, Mailtrap, etc.)
for automated email validation in tests.
"""

import imaplib
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data class"""

    id: str
    from_address: str
    to_addresses: List[str]
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    attachments: Optional[List[str]] = None
    timestamp: Optional[str] = None


class MailHogClient:
    """
    MailHog email testing client.

    Prerequisites:
        - MailHog server running (docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog)

    Example:
        mailhog = MailHogClient("http://localhost:8025")
        mailhog.delete_all_messages()
        # ... trigger email sending ...
        email = mailhog.wait_for_email(to="user@example.com", timeout=30)
        mailhog.assert_email_subject_contains(email, "Welcome")
    """

    def __init__(self, api_url: str = "http://localhost:8025"):
        """
        Initialize MailHog client.

        Args:
            api_url: MailHog API URL
        """
        self.api_url = api_url.rstrip("/")

    def get_all_messages(self) -> List[EmailMessage]:
        """
        Get all messages from MailHog.

        Returns:
            List of EmailMessage objects
        """
        try:
            response = requests.get(f"{self.api_url}/api/v2/messages")
            response.raise_for_status()

            data = response.json()
            messages = []

            for item in data.get("items", []):
                msg = self._parse_mailhog_message(item)
                messages.append(msg)

            logger.debug(f"Retrieved {len(messages)} messages from MailHog")
            return messages

        except requests.RequestException as e:
            logger.error(f"Failed to get messages from MailHog: {e}")
            return []

    def _parse_mailhog_message(self, item: Dict) -> EmailMessage:
        """Parse MailHog message format"""
        content = item.get("Content", {})
        headers = content.get("Headers", {})

        return EmailMessage(
            id=item.get("ID", ""),
            from_address=headers.get("From", [""])[0],
            to_addresses=headers.get("To", []),
            subject=headers.get("Subject", [""])[0],
            body_text=content.get("Body", ""),
            body_html=None,  # MailHog API doesn't separate HTML
            headers=headers,
            timestamp=item.get("Created", ""),
        )

    def get_message_by_id(self, message_id: str) -> Optional[EmailMessage]:
        """Get specific message by ID"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/messages/{message_id}")
            response.raise_for_status()
            return self._parse_mailhog_message(response.json())
        except requests.RequestException as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None

    def delete_message(self, message_id: str) -> bool:
        """Delete specific message"""
        try:
            response = requests.delete(f"{self.api_url}/api/v1/messages/{message_id}")
            response.raise_for_status()
            logger.debug(f"Deleted message: {message_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to delete message: {e}")
            return False

    def delete_all_messages(self) -> bool:
        """Delete all messages"""
        try:
            response = requests.delete(f"{self.api_url}/api/v1/messages")
            response.raise_for_status()
            logger.info("All messages deleted from MailHog")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to delete all messages: {e}")
            return False

    def wait_for_email(
        self,
        to: Optional[str] = None,
        from_address: Optional[str] = None,
        subject_contains: Optional[str] = None,
        timeout: float = 30.0,
        poll_interval: float = 1.0,
    ) -> Optional[EmailMessage]:
        """
        Wait for email matching criteria.

        Args:
            to: Recipient email address
            from_address: Sender email address
            subject_contains: Subject text to match
            timeout: Timeout in seconds
            poll_interval: Polling interval

        Returns:
            EmailMessage if found, None otherwise
        """
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            messages = self.get_all_messages()

            for msg in messages:
                # Check filters
                if to and to not in msg.to_addresses:
                    continue
                if from_address and from_address != msg.from_address:
                    continue
                if subject_contains and subject_contains not in msg.subject:
                    continue

                logger.info(f"Email found: {msg.subject}")
                return msg

            time.sleep(poll_interval)

        logger.warning(f"Email not found within {timeout}s")
        return None

    def assert_email_received(
        self,
        to: Optional[str] = None,
        from_address: Optional[str] = None,
        subject_contains: Optional[str] = None,
        timeout: float = 30.0,
    ) -> EmailMessage:
        """
        Assert email was received.

        Returns:
            EmailMessage

        Raises:
            AssertionError if email not found
        """
        email = self.wait_for_email(to, from_address, subject_contains, timeout)
        assert email is not None, "Email not received"
        logger.info("[OK] Email received")
        return email

    def assert_email_subject_contains(
        self, email_msg: EmailMessage, text: str, case_sensitive: bool = False
    ) -> bool:
        """Assert email subject contains text"""
        subject = email_msg.subject
        search_text = text

        if not case_sensitive:
            subject = subject.lower()
            search_text = text.lower()

        assert search_text in subject, f"Subject '{email_msg.subject}' does not contain '{text}'"

        logger.info(f"[OK] Subject contains: '{text}'")
        return True

    def assert_email_body_contains(
        self, email_msg: EmailMessage, text: str, case_sensitive: bool = False
    ) -> bool:
        """Assert email body contains text"""
        body = email_msg.body_text or email_msg.body_html or ""
        search_text = text

        if not case_sensitive:
            body = body.lower()
            search_text = text.lower()

        assert search_text in body, f"Body does not contain '{text}'"

        logger.info(f"[OK] Body contains: '{text}'")
        return True

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.get_all_messages())


class MailtrapClient:
    """
    Mailtrap email testing client.

    Prerequisites:
        - Mailtrap account and API token

    Example:
        mailtrap = MailtrapClient(api_token="your_token", inbox_id="12345")
        email = mailtrap.wait_for_email(to="test@example.com")
    """

    def __init__(self, api_token: str, inbox_id: str):
        """
        Initialize Mailtrap client.

        Args:
            api_token: Mailtrap API token
            inbox_id: Mailtrap inbox ID
        """
        self.api_token = api_token
        self.inbox_id = inbox_id
        self.api_url = "https://mailtrap.io/api/v1"
        self.headers = {"Api-Token": api_token}

    def get_all_messages(self) -> List[EmailMessage]:
        """Get all messages from Mailtrap inbox"""
        try:
            response = requests.get(
                f"{self.api_url}/inboxes/{self.inbox_id}/messages", headers=self.headers
            )
            response.raise_for_status()

            messages = []
            for item in response.json():
                messages.append(
                    EmailMessage(
                        id=str(item["id"]),
                        from_address=item["from_email"],
                        to_addresses=[item["to_email"]],
                        subject=item["subject"],
                        body_text=item.get("text_body"),
                        body_html=item.get("html_body"),
                        timestamp=item["sent_at"],
                    )
                )

            logger.debug(f"Retrieved {len(messages)} messages from Mailtrap")
            return messages

        except requests.RequestException as e:
            logger.error(f"Failed to get messages from Mailtrap: {e}")
            return []

    def delete_all_messages(self) -> bool:
        """Clean Mailtrap inbox"""
        try:
            response = requests.patch(
                f"{self.api_url}/inboxes/{self.inbox_id}/clean", headers=self.headers
            )
            response.raise_for_status()
            logger.info("Mailtrap inbox cleaned")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to clean inbox: {e}")
            return False

    def wait_for_email(
        self,
        to: Optional[str] = None,
        subject_contains: Optional[str] = None,
        timeout: float = 30.0,
        poll_interval: float = 2.0,
    ) -> Optional[EmailMessage]:
        """Wait for email in Mailtrap"""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            messages = self.get_all_messages()

            for msg in messages:
                if to and to not in msg.to_addresses:
                    continue
                if subject_contains and subject_contains not in msg.subject:
                    continue

                logger.info(f"Email found: {msg.subject}")
                return msg

            time.sleep(poll_interval)

        logger.warning(f"Email not found within {timeout}s")
        return None


class IMAPEmailClient:
    """
    IMAP email client for real email accounts.

    Example:
        imap = IMAPEmailClient("imap.gmail.com", "user@gmail.com", "app_password")
        imap.connect()
        email = imap.wait_for_email(subject_contains="Order Confirmation")
        imap.disconnect()
    """

    def __init__(
        self,
        imap_server: str,
        email_address: str,
        password: str,
        port: int = 993,
        use_ssl: bool = True,
    ):
        """
        Initialize IMAP client.

        Args:
            imap_server: IMAP server address
            email_address: Email address
            password: Email password or app password
            port: IMAP port
            use_ssl: Use SSL connection
        """
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.imap_server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.imap_server, self.port)

            self.connection.login(self.email_address, self.password)
            logger.info(f"Connected to IMAP server: {self.imap_server}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to IMAP: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")

    def search_emails(
        self,
        folder: str = "INBOX",
        from_address: Optional[str] = None,
        subject_contains: Optional[str] = None,
        unseen_only: bool = False,
    ) -> List[str]:
        """
        Search for emails matching criteria.

        Returns:
            List of email IDs
        """
        if not self.connection:
            raise RuntimeError("Not connected to IMAP server")

        self.connection.select(folder)

        # Build search criteria
        criteria = []
        if unseen_only:
            criteria.append("UNSEEN")
        if from_address:
            criteria.append(f'FROM "{from_address}"')
        if subject_contains:
            criteria.append(f'SUBJECT "{subject_contains}"')

        search_str = " ".join(criteria) if criteria else "ALL"

        status, messages = self.connection.search(None, search_str)

        if status == "OK":
            email_ids = messages[0].split()
            logger.debug(f"Found {len(email_ids)} emails")
            return [id.decode() for id in email_ids]

        return []

    def wait_for_email(
        self,
        subject_contains: Optional[str] = None,
        from_address: Optional[str] = None,
        timeout: float = 30.0,
        poll_interval: float = 5.0,
    ) -> Optional[str]:
        """Wait for email matching criteria"""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            email_ids = self.search_emails(
                from_address=from_address, subject_contains=subject_contains, unseen_only=True
            )

            if email_ids:
                logger.info(f"Email found: {email_ids[0]}")
                return email_ids[0]

            time.sleep(poll_interval)

        logger.warning("Email not found within timeout")
        return None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
