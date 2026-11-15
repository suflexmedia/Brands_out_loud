"""Provides authenticated AES-256-GCM reversible encryption, deterministic blind indexing, and HMAC-SHA256 OTP hashing."""

import base64
import hashlib
import hmac
import os
import re
from typing import Optional

from Crypto.Cipher import AES

_RAW_KEY = os.getenv("DATA_ENCRYPTION_KEY") or os.getenv("JWT_SECRET") or "brands-out-loud-data-encryption-key-production-secret-2026"
_AES_KEY = hashlib.sha256(_RAW_KEY.encode("utf-8")).digest()
_BLIND_SALT = hashlib.sha256((_RAW_KEY + ":blind-index-salt").encode("utf-8")).digest()
_OTP_SALT = hashlib.sha256((_RAW_KEY + ":otp-salt").encode("utf-8")).digest()


def encrypt_pii(value: Optional[str]) -> Optional[str]:
    """Encrypts a plaintext string using AES-256 in GCM mode and returns base64 token."""
    if value is None:
        return None
    val_str = str(value).strip()
    if not val_str:
        return ""

    data = val_str.encode("utf-8")
    cipher = AES.new(_AES_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    packed = cipher.nonce + tag + ciphertext
    return base64.b64encode(packed).decode("utf-8")


def decrypt_pii(token: Optional[str]) -> Optional[str]:
    """Decrypts an AES-256-GCM base64 token back to UTF-8 plaintext, falling back gracefully."""
    if token is None:
        return None
    token_str = str(token).strip()
    if not token_str:
        return ""

    try:
        raw = base64.b64decode(token_str.encode("utf-8"))
        if len(raw) < 33:
            return token_str
        nonce = raw[:16]
        tag = raw[16:32]
        ciphertext = raw[32:]
        decipher = AES.new(_AES_KEY, AES.MODE_GCM, nonce=nonce)
        decrypted = decipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode("utf-8")
    except Exception:
        return token_str


def hash_blind_index(value: Optional[str]) -> str:
    """Computes a deterministic HMAC-SHA256 blind index hash for searchable encrypted fields."""
    if not value:
        return ""
    normalized = str(value).strip().lower()
    digits = re.sub(r"\D", "", normalized)
    to_hash = digits if len(digits) >= 10 else normalized
    return hmac.new(_BLIND_SALT, to_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def hash_otp(otp_code: Optional[str]) -> str:
    """Computes an irreversible HMAC-SHA256 hash of an OTP code for storage."""
    clean_code = re.sub(r"\D", "", str(otp_code or ""))
    return hmac.new(_OTP_SALT, clean_code.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_otp_hash(entered_otp: Optional[str], stored_hash: Optional[str]) -> bool:
    """Performs constant-time comparison of an entered OTP against its stored HMAC hash."""
    if not entered_otp or not stored_hash:
        return False
    computed = hash_otp(entered_otp)
    return hmac.compare_digest(computed, str(stored_hash).strip())
