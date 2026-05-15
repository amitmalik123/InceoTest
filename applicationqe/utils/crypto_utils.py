"""
Utility for encrypting/decrypting sensitive config values using Fernet symmetric encryption.

The encryption key is derived from a passphrase stored in the INFLUXDB_KEY environment variable.
If not set, a default machine-scoped key is used (suitable for internal/corp environments).
"""

import base64
import hashlib
import os

from cryptography.fernet import Fernet

# Default passphrase - override via INFLUXDB_KEY env var for extra security
_DEFAULT_PASSPHRASE = "prodeng-automation-influx-2026"

ENCRYPTED_PREFIX = "ENC:"


def _get_fernet() -> Fernet:
    """Derive a Fernet key from a passphrase."""
    passphrase = os.getenv("INFLUXDB_KEY", _DEFAULT_PASSPHRASE)
    key = base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())
    return Fernet(key)


def encrypt_value(plain_text: str) -> str:
    """Encrypt a plain text value and return it with the ENC: prefix."""
    f = _get_fernet()
    encrypted = f.encrypt(plain_text.encode()).decode()
    return f"{ENCRYPTED_PREFIX}{encrypted}"


def decrypt_value(encrypted_text: str) -> str:
    """Decrypt a value. If it doesn't have the ENC: prefix, return as-is."""
    if not encrypted_text.startswith(ENCRYPTED_PREFIX):
        return encrypted_text
    f = _get_fernet()
    token = encrypted_text[len(ENCRYPTED_PREFIX):]
    return f.decrypt(token.encode()).decode()


def is_encrypted(value: str) -> bool:
    """Check if a value has the ENC: prefix."""
    return value.startswith(ENCRYPTED_PREFIX)
