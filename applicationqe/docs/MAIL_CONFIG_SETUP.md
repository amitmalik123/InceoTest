# Mail Configuration Setup Guide

## Overview

The outlook email credentials have been moved from environment YAML configuration files to a centralized `mail_config.properties` file for improved security and maintainability.

## File Structure

### New Files
- **`config/mail_config.properties`** - Centralized mail configuration with encrypted credentials

### Updated Files
- **`config/settings.py`** - Updated to load from properties file
- **`config/env.test11.yaml`** - Removed outlook section
- **`config/env.qa.yaml`** - Removed outlook section

## Configuration Priority

The following priority is used to resolve mail configuration:

```
1. config/mail_config.properties (encrypted values)
   ↓
2. Environment Variables (OUTLOOK_EMAIL, OUTLOOK_PASSWORD, etc.)
   ↓
3. Azure Key Vault (if CI/CD pipeline sets it)
   ↓
4. YAML config (backward compatibility)
   ↓
5. Default values
```

## Configuration Properties

### mail_config.properties Structure

```properties
# Outlook email address (AES-encrypted)
outlook.email=dDwTzWdq5f9qIsM7xcfhOBPazVB5iS7UbbrJLiP5Ldc=

# Outlook password or App Password (AES-encrypted)
outlook.password=8pBp0AreZeAS9uLF4uHqIg==

# IMAP server hostname
outlook.imap_server=outlook.office365.com

# IMAP port (993 for SSL, 143 for non-SSL)
outlook.imap_port=993

# Mail folder to read from
outlook.mail_folder=INBOX

# Connection timeout in seconds
outlook.connection_timeout=30

# Read timeout in seconds
outlook.read_timeout=30
```

## Code Changes

### Settings.py Updates

#### New Methods:
- `_load_mail_config()` - Loads and parses mail_config.properties file

#### Updated Properties:
- `outlook_email` - Now reads from properties first with fallback chain
- `outlook_password` - Now reads from properties first with fallback chain
- `outlook_imap_server` - Now reads from properties first with fallback chain
- `outlook_imap_port` - Now reads from properties first with fallback chain

#### Usage:
```python
from config.settings import settings

# Access outlook credentials
email = settings.outlook_email          # Automatically decrypted
password = settings.outlook_password    # Automatically decrypted
imap_server = settings.outlook_imap_server
imap_port = settings.outlook_imap_port
```

## Security

### Encryption
- All sensitive values in `mail_config.properties` are AES-encrypted
- Decryption happens automatically via `crypto_utils.decrypt_value()`
- The encryption key is stored in the environment YAML as `secret_key`

### To Encrypt New Credentials

```python
from utils.crypto_utils import encrypt_value

# Get the actual value (email, password, etc.)
raw_value = "saransh.saxena@assetmark.com"

# Encrypt it
encrypted = encrypt_value(raw_value)
# Output: ENC:dDwTzWdq5f9qIsM7xcfhOBPazVB5iS7UbbrJLiP5Ldc=

# Add to mail_config.properties:
# outlook.email=dDwTzWdq5f9qIsM7xcfhOBPazVB5iS7UbbrJLiP5Ldc=
```

## Usage Examples

### Basic Outlook Usage
```python
from utils.outlook_utils import OutlookClient
from config.settings import settings

# Credentials are automatically loaded and decrypted
client = OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password,
    imap_server=settings.outlook_imap_server,
    imap_port=settings.outlook_imap_port,
)

# Fetch emails using the client
emails = client.get_emails_by_subject("OTP")
client.close()
```

### In Tests (with context manager)
```python
from utils.outlook_utils import OutlookClient
from config.settings import settings

with OutlookClient(
    email=settings.outlook_email,
    password=settings.outlook_password,
) as client:
    latest_email = client.get_latest_email_by_subject("Verification Code")
    otp = client.extract_otp_from_email(latest_email)
    print(f"OTP: {otp}")
```

## CI/CD Integration (Azure Pipelines)

### Method 1: Environment Variables (Recommended)
The Azure Pipelines pipeline can set environment variables:

```yaml
- task: AzureKeyVault@2
  inputs:
    azureSubscription: '...'
    KeyVaultName: '...'
    SecretsFilter: 'outlook-email,outlook-password'

- script: |
    export OUTLOOK_EMAIL=$(outlook-email)
    export OUTLOOK_PASSWORD=$(outlook-password)
    export OUTLOOK_IMAP_SERVER=$(outlook-imap-server)
    export OUTLOOK_IMAP_PORT=$(outlook-imap-port)
    pytest tests/...
```

### Method 2: Direct Key Vault (Azure Pipelines)
The pipeline can fetch secrets and map them to Azure Key Vault:

```yaml
- task: AzureKeyVault@2
  inputs:
    azureSubscription: 'Azure Subscription'
    KeyVaultName: 'YourKeyVault'
    SecretsFilter: '*'
```

Then the Settings class reads via: `self._vault.get_secret(f"{self.env}-outlook-password")`

## Local Development Setup

### Method 1: Using .env File (Recommended)
Create a `.env` file in the project root:

```bash
# .env
TEST_ENV=test11
OUTLOOK_EMAIL=your-email@company.com
OUTLOOK_PASSWORD=your-app-password
OUTLOOK_IMAP_SERVER=outlook.office365.com
OUTLOOK_IMAP_PORT=993
```

**Important:** Never commit `.env` to git!

### Method 2: Update mail_config.properties
Encrypt your credentials and update `config/mail_config.properties`:

```bash
# Using Python REPL or script:
from utils.crypto_utils import encrypt_value

email = encrypt_value("your-email@company.com")        # Get encrypted value
password = encrypt_value("your-app-password")          # Get encrypted value

# Then update mail_config.properties with encrypted values
```

### Method 3: System Environment Variables
Export directly in your shell:

```bash
export OUTLOOK_EMAIL="your-email@company.com"
export OUTLOOK_PASSWORD="your-app-password"
export OUTLOOK_IMAP_SERVER="outlook.office365.com"
export OUTLOOK_IMAP_PORT=993
```

## Used By

### Utilities
- **`utils/outlook_utils.py`** - OutlookClient class uses settings for credentials
- **`utils/email_utils.py`** - EmailClient for general email access

### Pages
- **`pages/docusign_page.py`** - Uses outlook for OTP verification during eSignature

### Steps
- **`tests/bdd/steps/view_documents_step.py`** - DocuSign signing flow with OTP

## Verification

To verify the mail configuration is working:

```bash
# Run a simple test
python -c "
from config.settings import settings
print(f'Email: {settings.outlook_email}')
print(f'IMAP Server: {settings.outlook_imap_server}')
print(f'IMAP Port: {settings.outlook_imap_port}')
"
```

## Troubleshooting

### Issue: "ValueError: Email and password are required"
**Cause:** Outlook credentials not resolved from any source
**Solution:** 
1. Check .env file exists and has OUTLOOK_EMAIL/OUTLOOK_PASSWORD
2. Check mail_config.properties exists and is readable
3. Verify encryption key in settings.py matches the one used to encrypt credentials

### Issue: "Error decrypting outlook password"
**Cause:** Encryption key mismatch or corrupted encrypted value
**Solution:**
1. Verify `secret_key` in env.test11.yaml matches the one used for encryption
2. Re-encrypt credentials using current encryption key
3. Check that mail_config.properties file is not corrupted

### Issue: "Connection refused" on IMAP
**Cause:** Wrong server or port
**Solution:**
1. For Outlook.com/Office365: Use `outlook.office365.com:993`
2. For on-prem Exchange: Use your Exchange server FQDN with appropriate port
3. Verify credentials have not expired (for App Passwords)

## Migration Notes

### For Existing Code
All existing code using `settings.outlook_*` properties will automatically use the new properties file. No code changes needed.

### For New Code
Prefer using:
```python
from config.settings import settings

email = settings.outlook_email
password = settings.outlook_password
```

Instead of directly accessing environment variables or YAML.

## Summary

| Item | Location | Purpose |
|------|----------|---------|
| Config File | `config/mail_config.properties` | Centralized outlook configuration |
| Settings Class | `config/settings.py` | Loads and provides access to mail config |
| YAML Files | `config/env.*.yaml` | No longer contain outlook config |
| Utilities | `utils/outlook_utils.py` | Uses settings for credentials |
| Documentation | `docs/MAIL_CONFIG_SETUP.md` | This file |

---

**Last Updated:** March 27, 2026  
**Version:** 1.0
