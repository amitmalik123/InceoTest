import base64
from typing import Union

try:
    from Crypto.Cipher import AES  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pycryptodome is required for encryption_utility.decrypt. "
        "Install it with `pip install pycryptodome`."
    ) from exc


def encrypt(plaintext: str, secret: str) -> str:
    """Encrypt a plaintext string using AES/ECB/PKCS5Padding.

    Returns Base64-encoded encrypted string.
    
    Mirrors the Java implementation:
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
    
    Args:
        plaintext: The value to encrypt (e.g., "user@example.com")
        secret: The secret key (must be 16, 24, or 32 bytes for AES key sizes)
    
    Returns:
        Base64-encoded encrypted string
        
    Example:
        secret = "your-16-byte-key"  # Must be 16, 24, or 32 bytes
        encrypted = encrypt("saransh.saxena@assetmark.com", secret)
        print(encrypted)  # Use this in config.yaml
    """
    key = secret.encode("utf-8")
    plaintext_bytes = plaintext.encode("utf-8")
    
    # PKCS5/PKCS7 padding: pad to next AES block size (16 bytes)
    block_size = 16
    pad_len = block_size - (len(plaintext_bytes) % block_size)
    padded_bytes = plaintext_bytes + bytes([pad_len]) * pad_len
    
    # Encrypt using AES/ECB mode
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(padded_bytes)
    
    # Return Base64-encoded result
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt(encrypted_data: Union[str, bytes], secret: str) -> str:
    """Decrypt a Base64-encoded AES-encrypted value.

    Mirrors the Java implementation:
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.DECRYPT_MODE, secretKey);

    which typically corresponds to AES/ECB/PKCS5Padding.
    """
    if isinstance(encrypted_data, str):
        encrypted_data_bytes = encrypted_data.encode("utf-8")
    else:
        encrypted_data_bytes = encrypted_data

    key = secret.encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    decoded_bytes = base64.b64decode(encrypted_data_bytes)
    decrypted_bytes = cipher.decrypt(decoded_bytes)

    # PKCS5/PKCS7 unpadding
    pad_len = decrypted_bytes[-1]
    if 1 <= pad_len <= 16:
        decrypted_bytes = decrypted_bytes[:-pad_len]

    return decrypted_bytes.decode("utf-8")
