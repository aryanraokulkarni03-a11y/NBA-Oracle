from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from nba_oracle.config import ORACLE_SECRET_KEY, ORACLE_TOKEN_TTL_MINUTES

try:
    import bcrypt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback only matters before deps are installed
    bcrypt = None

try:
    import jwt  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback only matters before deps are installed
    jwt = None


def generate_secret_key() -> str:
    return secrets.token_urlsafe(48)


def hash_password(password: str, *, iterations: int = 200_000) -> str:
    if bcrypt is not None:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("utf-8").rstrip("="),
        base64.urlsafe_b64encode(derived).decode("utf-8").rstrip("="),
    )


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("$2") and bcrypt is not None:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    try:
        algorithm, iteration_text, salt_text, digest_text = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    iterations = int(iteration_text)
    salt = _b64url_decode(salt_text)
    expected = _b64url_decode(digest_text)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(derived, expected)


def create_access_token(
    subject: str,
    *,
    secret_key: str | None = None,
    ttl_minutes: int = ORACLE_TOKEN_TTL_MINUTES,
    extra: dict[str, Any] | None = None,
) -> str:
    key = secret_key or ORACLE_SECRET_KEY
    if not key:
        raise RuntimeError("oracle_secret_key_missing")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    if jwt is not None:
        return str(jwt.encode(payload, key, algorithm="HS256"))

    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        key.encode("utf-8"),
        f"{encoded_header}.{encoded_payload}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    encoded_signature = _b64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str, *, secret_key: str | None = None) -> dict[str, Any]:
    key = secret_key or ORACLE_SECRET_KEY
    if not key:
        raise RuntimeError("oracle_secret_key_missing")
    if jwt is not None:
        try:
            return dict(jwt.decode(token, key, algorithms=["HS256"]))
        except Exception as exc:  # pragma: no cover - normalized into legacy ValueError contract
            raise ValueError("token_invalid") from exc

    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
    except ValueError as exc:
        raise ValueError("token_format_invalid") from exc

    expected_signature = hmac.new(
        key.encode("utf-8"),
        f"{encoded_header}.{encoded_payload}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64url_encode(expected_signature), encoded_signature):
        raise ValueError("token_signature_invalid")

    payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("token_expired")
    return dict(payload)


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)
