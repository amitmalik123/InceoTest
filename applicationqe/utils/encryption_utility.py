"""AES Encryption/Decryption Utility for secure credential management"""

import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class EncryptionUtility:
    """
    AES encryption/decryption utility for storing sensitive credentials
    
    Mirrors the Java EncryptionUtility implementation using AES/ECB mode
    
    Example:
        encrypted = EncryptionUtility.encrypt("jn.venkateshbabu@assetmark.com", "4125356372804196")
        decrypted = EncryptionUtility.decrypt(encrypted, "4125356372804196")
        assert decrypted == "jn.venkateshbabu@assetmark.com"
    """
    
    @staticmethod
    def encrypt(plaintext: str, secret_key: str) -> str:
        """
        Encrypt plaintext using AES with ECB mode
        
        Args:
            plaintext: Data to encrypt (e.g., email address or password)
            secret_key: Secret key string (will be padded to 32 bytes for AES-256)
            
        Returns:
            Base64-encoded encrypted data
        """
        try:
            # Pad secret key to 32 bytes (256-bit) for AES-256
            # If shorter, pad with spaces; if longer, truncate
            key_bytes = secret_key.encode('utf-8')
            if len(key_bytes) < 32:
                key_bytes = key_bytes + b'\x00' * (32 - len(key_bytes))
            else:
                key_bytes = key_bytes[:32]
            
            # Create cipher in ECB mode (mirrors Java implementation)
            cipher = Cipher(
                algorithms.AES(key_bytes),
                modes.ECB(),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad plaintext to multiple of 16 bytes (PKCS7 padding)
            plaintext_bytes = plaintext.encode('utf-8')
            padded_plaintext = EncryptionUtility._pkcs7_pad(plaintext_bytes)
            
            # Encrypt
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            
            # Encode to Base64
            encrypted_b64 = base64.b64encode(ciphertext).decode('utf-8')
            logger.info(f"Encrypted data successfully (length: {len(plaintext)} → {len(encrypted_b64)})")
            
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e).splitlines()[0]}")
            raise
    
    @staticmethod
    def decrypt(encrypted_data: str, secret_key: str) -> str:
        """
        Decrypt Base64-encoded AES encrypted data
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            secret_key: Secret key string (must match encryption key)
            
        Returns:
            Decrypted plaintext
        """
        try:
            # Pad secret key to 32 bytes (matches encryption)
            key_bytes = secret_key.encode('utf-8')
            if len(key_bytes) < 32:
                key_bytes = key_bytes + b'\x00' * (32 - len(key_bytes))
            else:
                key_bytes = key_bytes[:32]
            
            # Decode from Base64
            ciphertext = base64.b64decode(encrypted_data)
            
            # Create cipher in ECB mode
            cipher = Cipher(
                algorithms.AES(key_bytes),
                modes.ECB(),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove PKCS7 padding
            plaintext_bytes = EncryptionUtility._pkcs7_unpad(padded_plaintext)
            plaintext = plaintext_bytes.decode('utf-8')
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e).splitlines()[0]}")
            raise
    
    @staticmethod
    def _pkcs7_pad(data: bytes) -> bytes:
        """
        Add PKCS7 padding to data
        
        Args:
            data: Data to pad
            
        Returns:
            Padded data
        """
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        """
        Remove PKCS7 padding from data
        
        Args:
            data: Padded data
            
        Returns:
            Unpadded data
        """
        if len(data) == 0:
            return data
        
        padding_length = data[-1]
        
        # Validate padding
        if padding_length > 16 or padding_length == 0:
            raise ValueError(f"Invalid PKCS7 padding: {padding_length}")
        
        # Check all padding bytes are correct
        for byte in data[-padding_length:]:
            if byte != padding_length:
                raise ValueError("Invalid PKCS7 padding")
        
        return data[:-padding_length]
