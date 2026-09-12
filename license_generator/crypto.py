"""License crypto compatible with Vendix and biz-control backends."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet

from license_generator.apps import AppConfig, LicensePeriod


def _fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _fernet(secret: str) -> Fernet:
    return Fernet(_fernet_key(secret))


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _sign_payload(secret: str, payload_json: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), payload_json.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def parse_request_code(config: AppConfig, secret: str, request_code: str) -> str | None:
    code = request_code.strip()
    if not code.startswith(config.prefix):
        return None
    try:
        token = _b64url_decode(code[len(config.prefix) :]).decode("utf-8")
        installation_id, signature = token.rsplit(".", 1)
    except (ValueError, UnicodeDecodeError):
        return None

    expected = _sign_payload(secret, installation_id)
    if not hmac.compare_digest(signature, expected):
        return None
    return installation_id


def generate_license(
    config: AppConfig,
    secret: str,
    installation_id: str,
    period: LicensePeriod,
    issued_at: datetime | None = None,
) -> str:
    issued = issued_at or datetime.now(timezone.utc)
    days = 30 if period == "month" else 365
    expires_at = issued + timedelta(days=days)
    payload = {
        "iid": installation_id,
        "exp": expires_at.isoformat(),
        "plan": period,
    }
    if config.payload_app:
        payload["app"] = config.payload_app

    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    signature = _sign_payload(secret, payload_json)
    blob = json.dumps({"p": payload, "s": signature}, separators=(",", ":"))
    encrypted = _fernet(secret).encrypt(blob.encode("utf-8"))
    return config.prefix + _b64url_encode(encrypted)
