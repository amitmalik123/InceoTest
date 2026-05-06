# Advanced Utilities Guide

## 📚 Overview

This guide covers the advanced utility features added to the framework:

1. **Retry Decorators** - Exponential backoff and retry mechanisms
2. **Custom Waiters** - Flexible waiting conditions
3. **Browser Storage** - localStorage, sessionStorage, and cookie management
4. **Download Validation** - File download handling and validation
5. **PDF Testing** - PDF content extraction and validation
6. **Email Testing** - Email verification with MailHog/Mailtrap

---

## 🔁 1. Retry Utilities

### **Module:** `utils/retry_utils.py`

### Features

- Exponential backoff with jitter
- Retry on specific exceptions
- Retry context managers
- Fluent retry API

### Basic Usage

```python
from utils.retry_utils import exponential_backoff, retry_until_true

# Decorator with auto-retry
@exponential_backoff(max_retries=3, initial_delay=1.0)
def unstable_operation():
    response = api.get_data()
    return response.json()

# Retry until condition is true
retry_until_true(
    lambda: page.locator("#status").inner_text() == "Complete",
    max_attempts=10,
    delay=2.0
)
```

### Advanced Examples

```python
from utils.retry_utils import RetryableAction, RetryContext

# Fluent API
action = RetryableAction(lambda: page.click("#button"))
action.with_retries(5).with_delay(2.0).execute()

# Context manager
with RetryContext(max_retries=3, initial_delay=1.0) as retry:
    while retry.should_retry():
        try:
            result = operation()
            retry.success()
            break
        except Exception as e:
            retry.failed(e)
```

---

## ⏱️ 2. Custom Wait Utilities

### **Module:** `utils/wait_utils.py`

### Features

- Custom condition waits
- Text and attribute waits
- URL and network waits
- Console message waits
- Fluent wait context

### Basic Usage

```python
from utils.wait_utils import (
    wait_for_condition,
    wait_for_text_to_contain,
    wait_for_element_count,
    WaitContext
)

# Wait for custom condition
wait_for_condition(
    lambda: page.locator(".item").count() == 5,
    timeout=10.0
)

# Wait for text
wait_for_text_to_contain(
    page.locator("#status"),
    "Success",
    timeout=30.0
)

# Wait context (fluent API)
with WaitContext(timeout=10.0) as wait:
    wait.until_visible(page.locator("#modal"))
    wait.until_text_contains(page.locator("#message"), "Complete")
```

### Advanced Examples

```python
from utils.wait_utils import (
    wait_for_value,
    wait_for_url_to_match,
    wait_for_class_to_contain
)

# Wait for specific value
count = wait_for_value(
    lambda: int(page.locator("#count").inner_text()),
    expected_value=100,
    timeout=10.0
)

# Wait for URL change
wait_for_url_to_match(page, "/dashboard", timeout=5.0)

# Wait for CSS class
wait_for_class_to_contain(page.locator("#button"), "active")
```

---

## 💾 3. Browser Storage Management

### **Module:** `utils/storage_utils.py`

### Features

- localStorage management
- sessionStorage management
- Cookie management
- Complete storage state save/restore

### localStorage

```python
from utils.storage_utils import LocalStorageManager

storage = LocalStorageManager(page)

# Set items
storage.set_item("user_id", "12345")
storage.set_item("config", {"theme": "dark", "lang": "en"})

# Get items
user_id = storage.get_item("user_id")
config = storage.get_item_as_json("config")

# Get all items
all_items = storage.get_all_items()

# Save/load from file
storage.save_to_file("storage_backup.json")
storage.load_from_file("storage_backup.json")

# Clear
storage.clear()
```

### Cookie Management

```python
from utils.storage_utils import CookieManager

cookies = CookieManager(context)

# Set cookie
cookies.set_cookie("session", "abc123", domain="example.com")

# Get cookie
session = cookies.get_cookie("session")
value = cookies.get_cookie_value("session")

# Persistent cookie
cookies.set_persistent_cookie("remember_me", "true", days=30)

# Save/load cookies
cookies.save_cookies_to_file("cookies.json")
cookies.load_cookies_from_file("cookies.json")
```

### Complete Storage State

```python
from utils.storage_utils import StorageState

storage_state = StorageState(page, context)

# Save complete state (localStorage + sessionStorage + cookies)
storage_state.save_state("user_session.json")

# Restore state
storage_state.load_state("user_session.json")

# Clear everything
storage_state.clear_all()
```

---

## 📥 4. Download File Validation

### **Module:** `utils/download_utils.py`

### Features

- Download triggering and capture
- File validation (name, extension, size)
- Hash validation
- CSV/JSON content validation

### Basic Usage

```python
from utils.download_utils import DownloadManager

manager = DownloadManager(page, download_dir="downloads")

# Trigger download
download = manager.trigger_download(
    lambda: page.click("#download-btn"),
    timeout=30.0
)

# Validate download
manager.validate_download(
    download,
    expected_extension=".pdf",
    min_size_bytes=1000
)

# Get file path
filepath = manager.save_download(download)
```

### Advanced Examples

```python
# Validate file hash
manager.validate_file_hash(
    filepath,
    expected_hash="abc123def456",
    algorithm="md5"
)

# Validate CSV content
manager.validate_csv_content(
    filepath,
    expected_columns=["Name", "Email", "Status"],
    min_rows=10,
    max_rows=1000
)

# Validate JSON content
data = manager.validate_json_content(filepath)

# Cleanup old downloads
manager.cleanup_downloads(older_than_seconds=3600)
```

---

## 📄 5. PDF Testing

### **Module:** `utils/pdf_utils.py`

### Prerequisites

```bash
pip install PyPDF2
```

### Features

- Page count validation
- Text extraction and validation
- Metadata validation
- Link extraction
- Search across pages

### Basic Usage

```python
from utils.pdf_utils import PDFValidator

validator = PDFValidator("document.pdf")

# Validate page count
validator.validate_page_count(min_pages=1, max_pages=10)

# Extract and validate text
text = validator.extract_text()
validator.assert_text_contains("Invoice")

# Validate metadata
validator.validate_metadata(
    expected_title="Invoice",
    expected_author="Company Name"
)

# Generate report
report = validator.generate_report()
print(report)
```

### Advanced Examples

```python
# Extract from specific page
page1_text = validator.extract_text(page_num=0)

# Extract from page range
text = validator.extract_text_from_pages(start_page=0, end_page=3)

# Search for text across pages
pages = validator.search_text("Total Amount:", case_sensitive=False)
print(f"Found on pages: {pages}")

# Extract links
links = validator.extract_links()

# Validate file size
validator.validate_file_size(max_size_mb=5.0)
```

### Complete PDF Download & Validation

```python
# Download PDF
download = download_manager.trigger_download(
    lambda: page.click("#download-invoice")
)
filepath = download_manager.save_download(download)

# Validate PDF
validator = PDFValidator(filepath)
validator.validate_page_count(expected_count=3)
validator.assert_text_contains("Invoice Number:")
validator.assert_text_contains("Total: $1,234.56")
```

---

## 📧 6. Email Testing

### **Module:** `utils/email_utils.py`

### Supported Services

- **MailHog** - Local email testing
- **Mailtrap** - Cloud email testing
- **IMAP** - Real email accounts

### MailHog Setup

```bash
# Run MailHog with Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Access UI: http://localhost:8025
# SMTP: localhost:1025
```

### MailHog Usage

```python
from utils.email_utils import MailHogClient

mailhog = MailHogClient("http://localhost:8025")

# Clear previous emails
mailhog.delete_all_messages()

# ... trigger email sending ...

# Wait for email
email = mailhog.wait_for_email(
    to="user@example.com",
    subject_contains="Welcome",
    timeout=30.0
)

# Validate email
mailhog.assert_email_subject_contains(email, "Welcome")
mailhog.assert_email_body_contains(email, "Thank you for registering")
```

### Mailtrap Usage

```python
from utils.email_utils import MailtrapClient

mailtrap = MailtrapClient(
    api_token="your_api_token",
    inbox_id="12345"
)

# Clean inbox
mailtrap.delete_all_messages()

# Wait for email
email = mailtrap.wait_for_email(
    to="test@example.com",
    subject_contains="Verification",
    timeout=30.0
)
```

### IMAP Usage

```python
from utils.email_utils import IMAPEmailClient

# Using context manager
with IMAPEmailClient("imap.gmail.com", "user@gmail.com", "app_password") as imap:
    email_id = imap.wait_for_email(
        subject_contains="Order Confirmation",
        timeout=60.0
    )
    assert email_id is not None
```

### Complete Email Verification Flow

```python
def test_registration_email_flow(page: Page):
    mailhog = MailHogClient()
    mailhog.delete_all_messages()

    # Register user
    page.goto("https://example.com/register")
    page.fill("#email", "test@example.com")
    page.click("#register")

    # Wait for confirmation email
    email = mailhog.assert_email_received(
        to="test@example.com",
        subject_contains="Verify your email",
        timeout=30.0
    )

    # Validate email content
    mailhog.assert_email_body_contains(email, "activation link")

    # Extract verification link (simplified)
    # In real scenario, parse email.body_text or email.body_html
    # verification_url = extract_url_from_email(email)
    # page.goto(verification_url)
```

---

## 🎯 Complete Example: Combined Usage

```python
def test_complete_workflow(page: Page, context, tmp_path):
    """Demonstrates using multiple utilities together"""

    # 1. Setup storage and authentication
    storage = StorageState(page, context)

    # 2. Login with retry
    @exponential_backoff(max_retries=3)
    def login():
        page.goto("https://app.example.com/login")
        page.fill("#username", "testuser")
        page.fill("#password", "password")
        page.click("#login-btn")

    login()

    # 3. Wait for dashboard
    with WaitContext(timeout=10.0) as wait:
        wait.until_visible(page.locator("#dashboard"))
        wait.until_text_contains(page.locator("#welcome"), "Welcome")

    # 4. Save authentication state
    storage.save_state(tmp_path / "auth.json")

    # 5. Download report
    download_mgr = DownloadManager(page, download_dir=str(tmp_path))
    download = download_mgr.trigger_download(
        lambda: page.click("#generate-report")
    )
    filepath = download_mgr.save_download(download)

    # 6. Validate PDF
    pdf = PDFValidator(filepath)
    pdf.validate_page_count(min_pages=1)
    pdf.assert_text_contains("Monthly Report")

    # 7. Check notification email
    mailhog = MailHogClient()
    email = mailhog.wait_for_email(
        to="user@example.com",
        subject_contains="Report Generated",
        timeout=30.0
    )
    mailhog.assert_email_body_contains(email, "Your report is ready")
```

---

## 📊 Quick Reference

### Installation

```bash
# Install additional dependencies
pip install -r requirements.txt

# For PDF testing
pip install PyPDF2

# For MailHog (Docker)
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

### Module Imports

```python
# Retry utilities
from utils.retry_utils import exponential_backoff, retry_until_true, RetryableAction

# Wait utilities
from utils.wait_utils import wait_for_condition, WaitContext

# Storage utilities
from utils.storage_utils import LocalStorageManager, CookieManager, StorageState

# Download utilities
from utils.download_utils import DownloadManager

# PDF utilities
from utils.pdf_utils import PDFValidator

# Email utilities
from utils.email_utils import MailHogClient, MailtrapClient
```

---

## 🎓 Example Tests

See `tests/utilities/test_utilities_examples.py` for complete working examples of all features.

---

## 🐛 Troubleshooting

### PDF Library Issues

```bash
# If PyPDF2 has issues, try pypdf
pip uninstall PyPDF2
pip install pypdf
```

### MailHog Not Working

```bash
# Check if MailHog is running
curl http://localhost:8025/api/v2/messages

# Check Docker container
docker ps | grep mailhog
```

### Download Timeout

```python
# Increase timeout for large files
download = manager.trigger_download(
    lambda: page.click("#download"),
    timeout=120.0  # 2 minutes
)
```

---

## 📚 Additional Resources

- [Retry Pattern](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [MailHog Documentation](https://github.com/mailhog/MailHog)
- [Mailtrap Documentation](https://mailtrap.io/docs/)

---

## ✅ Best Practices

1. **Retry Logic**: Use retries for flaky operations, not for masking real issues
2. **Waits**: Prefer explicit waits over fixed sleeps
3. **Storage**: Clean up storage state between tests
4. **Downloads**: Clean up downloaded files after tests
5. **Email**: Clear email inbox before each test
6. **PDF**: Validate both structure and content
