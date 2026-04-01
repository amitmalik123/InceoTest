# Mail Configuration - Quick Reference

## Quick Start

### For Local Development (Recommended)
```bash
# 1. Create .env file in project root
cat > .env << EOF
TEST_ENV=test11
OUTLOOK_EMAIL=your-email@company.com
OUTLOOK_PASSWORD=your-app-password
EOF

# 2. Run tests
pytest tests/bdd/test_runners/test_NAW.py -v
```

### Using Outlook in Code
```python
from config.settings import settings
from utils.outlook_utils import OutlookClient

# Option 1: Automatic (uses settings)
with OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password
) as client:
    emails = client.get_emails_by_subject("OTP")

# Option 2: Settings only
email = settings.outlook_email
password = settings.outlook_password
server = settings.outlook_imap_server
port = settings.outlook_imap_port
```

## Configuration Files

### Primary File
**`config/mail_config.properties`** (Encrypted credentials)
```properties
outlook.email=dDwTzWdq5f9qIsM7xcfhOBPazVB5iS7UbbrJLiP5Ldc=
outlook.password=8pBp0AreZeAS9uLF4uHqIg==
outlook.imap_server=outlook.office365.com
outlook.imap_port=993
```

### Settings File
**`config/settings.py`** (Loads from properties)
```python
# Properties are auto-loaded and decrypted
settings.outlook_email          # Decrypted
settings.outlook_password       # Decrypted
settings.outlook_imap_server
settings.outlook_imap_port
```

### Environment Variables (Optional Override)
```bash
export OUTLOOK_EMAIL="your-email@company.com"
export OUTLOOK_PASSWORD="your-app-password"
export OUTLOOK_IMAP_SERVER="outlook.office365.com"
export OUTLOOK_IMAP_PORT="993"
```

## Common Operations

### Fetching Emails by Subject
```python
from utils.outlook_utils import OutlookClient
from config.settings import settings

with OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password
) as client:
    # Get latest email
    email = client.get_latest_email_by_subject("OTP")
    
    # Extract OTP
    otp = client.extract_otp_from_email(email)
    print(f"OTP: {otp}")
```

### Waiting for Email (with timeout)
```python
email = client.wait_for_email_by_subject(
    subject="Password Reset",
    timeout=60,  # seconds
    exact_match=True
)

if email:
    otp = client.extract_otp_from_email(email)
```

### Extracting Links
```python
email = client.get_latest_email_by_subject("Verify Email")
links = client.extract_links_from_email(email)
for link in links:
    print(link)
```

### One-Shot Pattern (Most Common for Tests)
```python
# Find email, extract data in one call
otp = client.fetch_data_from_email_by_subject(
    subject="Verification Code",
    pattern=r"(\d{6})",  # Extract 6 digits
    group=1,
    wait=True,           # Wait up to 2 minutes
    wait_timeout=120
)
```

## Troubleshooting

### "ValueError: Email and password are required"
**Check:**
1. `.env` file exists with credentials
2. `mail_config.properties` is accessible
3. Credentials are not empty

### "Failed to login to outlook.office365.com"
**Check:**
1. Email and password are correct
2. For MFA accounts: using App Password (not regular password)
3. IMAP is enabled on the account
4. Network access to outlook.office365.com:993

### "Pattern not found in email"
**Check:**
1. Email subject is correct
2. Pattern regex is valid
3. Email contains the expected text
4. Try: `email.body_text` or `email.body_html` directly

### Encryption/Decryption Issues
**Regenerate credentials:**
```bash
python generate_credentials.py
# Update mail_config.properties with new values
```

## FAQ

**Q: How do I update my password in the config?**
```bash
python generate_credentials.py
# Enter new password when prompted
# Copy encrypted value to mail_config.properties
```

**Q: Can I use my regular password or must I use App Password?**
- If MFA is enabled on your account: **Only App Passwords work**
- If MFA is disabled: Regular password works, but recommend App Password anyway

**Q: Where do I get an App Password?**
- **Personal Account:** https://account.live.com/proofs/AppPassword
- **Work/School:** Contact your Microsoft 365 admin

**Q: How often do credentials expire?**
- App Passwords never expire unless you revoke them manually
- Regular passwords may expire per your organization's policy

**Q: Can I share the mail_config.properties file?**
- **NO** - It contains encrypted credentials secured by the secret_key
- Only share in private channels or add to `.gitignore`
- Never commit to public repositories

**Q: What's the difference between YAML and properties configuration?**
- **YAML** (env.test11.yaml): Application-wide settings
- **Properties** (mail_config.properties): Mail-specific settings
- Properties take priority when both exist

**Q: How does the priority chain work?**
1. `mail_config.properties` (encrypted values)
2. Environment variables (`OUTLOOK_EMAIL`, etc.)
3. Azure Key Vault (cloud secrets)
4. YAML config (backward compatibility)
5. Defaults (outlook.office365.com, port 993)

## Common Patterns

### Pattern 1: Simple Email Check
```python
client = OutlookClient(settings.outlook_email, settings.outlook_password)
try:
    emails = client.get_unread_emails(top=1)
    print(f"✅ Connected, {len(emails)} unread email(s)")
finally:
    client.close()
```

### Pattern 2: Extract OTP
```python
otp = OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password
).fetch_data_from_email_by_subject(
    subject="Verification",
    pattern=r"(\d{6})",
    group=1,
    wait=True
)
```

### Pattern 3: Test with Context Manager
```python
with OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password
) as client:
    email = client.get_latest_email_by_subject("Confirm")
    if email:
        print(f"Got email: {email.subject}")
    # Auto-closes on exit
```

### Pattern 4: Batch Processing
```python
with OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password
) as client:
    emails = client.get_emails_by_subject("Report", top=10)
    for email in emails:
        print(f"{email.received_datetime}: {email.subject}")
        links = client.extract_links_from_email(email)
        print(f"  Links: {links}")
```

## Documentation Links

| Document | Purpose |
|----------|---------|
| `docs/MAIL_CONFIG_SETUP.md` | Comprehensive setup guide |
| `docs/MAIL_CONFIG_MIGRATION_SUMMARY.md` | Migration details |
| `config/mail_config.properties` | Configuration file |
| `utils/outlook_utils.py` | OutlookClient API |

## Version
- **Created:** March 27, 2026
- **Last Updated:** March 27, 2026
- **Status:** ✅ Production Ready

---

**Need Help?** See `docs/MAIL_CONFIG_SETUP.md` for detailed troubleshooting
