#!/usr/bin/env python3
"""Generate encrypted credentials for YAML configuration."""

from utils.credential_encrypter import encrypt

# Generate a 32-byte secret key for AES encryption
secret_key = "MyTestSecretKey123456789012345"  # 30 bytes, pad to 32
secret_key = secret_key.ljust(32, "0")  # Pad to 32 bytes

print("=== Generated Secret Key ===")
print(f"Secret Key (32 bytes): {secret_key}")
print(f"Length: {len(secret_key)}")

# Example Outlook credentials (using placeholder values for now)
test_email = "saransh.saxena@assetmark.com"
test_password = "WelcomeC02288!"

print("\n=== Encrypted Credentials ===")

encrypted_email = encrypt(test_email, secret_key)
print(f"Encrypted Email: {encrypted_email}")

encrypted_password = encrypt(test_password, secret_key)
print(f"Encrypted Password: {encrypted_password}")

print("\n=== YAML Configuration to Add ===")
yaml_config = f"""
secret_key: "{secret_key}"

outlook:
  email: "{encrypted_email}"
  password: "{encrypted_password}"
  imap_server: "outlook.office365.com"
  imap_port: 993
"""
print(yaml_config)
