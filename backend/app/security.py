"""Helper keamanan: password hashing, API key, OAuth state, dan verifikasi Midtrans."""
import hashlib
import hmac
import secrets
import time

import bcrypt

from app.config import SECRET_KEY

# ─── API Key ────────────────────────────────────────────────────

def generate_api_key() -> str:
    return f"ac_{secrets.token_hex(16)}"

def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

# ─── Password (bcrypt, dengan fallback hash SHA256 lama) ────────

_LEGACY_SALT = "autoclipper_salt_"

def hash_password(password: str) -> str:
    # bcrypt hanya membaca 72 byte pertama
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("$2"):
        try:
            return bcrypt.checkpw(password.encode()[:72], stored_hash.encode())
        except ValueError:
            return False
    # Hash lama: sha256("autoclipper_salt_" + password) — akun dibuat sebelum upgrade
    legacy = hashlib.sha256(f"{_LEGACY_SALT}{password}".encode()).hexdigest()
    return hmac.compare_digest(legacy, stored_hash)

def password_needs_rehash(stored_hash: str) -> bool:
    return bool(stored_hash) and not stored_hash.startswith("$2")

# ─── OAuth state (stateless, ditandatangani HMAC) ───────────────

_STATE_TTL_SECONDS = 600

def _sign_state(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

def generate_oauth_state() -> str:
    payload = f"{int(time.time())}.{secrets.token_urlsafe(16)}"
    return f"{payload}.{_sign_state(payload)}"

def verify_oauth_state(state: str) -> bool:
    if not state:
        return False
    parts = state.rsplit(".", 1)
    if len(parts) != 2:
        return False
    payload, sig = parts
    if not hmac.compare_digest(_sign_state(payload), sig):
        return False
    try:
        ts = int(payload.split(".", 1)[0])
    except ValueError:
        return False
    return (time.time() - ts) <= _STATE_TTL_SECONDS

# ─── Midtrans ───────────────────────────────────────────────────

def verify_midtrans_signature(order_id: str, status_code: str, gross_amount: str,
                              server_key: str, signature_key: str) -> bool:
    """signature_key = sha512(order_id + status_code + gross_amount + server_key)"""
    if not (order_id and status_code and gross_amount and server_key and signature_key):
        return False
    expected = hashlib.sha512(
        f"{order_id}{status_code}{gross_amount}{server_key}".encode()
    ).hexdigest()
    return hmac.compare_digest(expected, signature_key)
