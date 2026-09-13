"""License crypto compatible with Vendix and biz-control backends."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet

from license_generator.apps import APP_CONFIGS, AppConfig, LicensePeriod, load_secret_for_app

REQUEST_PREFIX = "VX2."


@dataclass(frozen=True)
class ParsedRequestCode:
    app_id: str
    key_id: str
    installation_id: str


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


def secret_key_id(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]


def _request_sign_message(app_id: str, key_id: str, installation_id: str) -> str:
    return f"v2|{app_id}|{key_id}|{installation_id}"


def _parse_request_code_v1(config: AppConfig, secret: str, request_code: str) -> str | None:
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


def _parse_request_code_v2(
    secret: str,
    request_code: str,
    *,
    expected_app_id: str | None = None,
) -> str | None:
    code = request_code.strip()
    if not code.startswith(REQUEST_PREFIX):
        return None

    body = code[len(REQUEST_PREFIX) :]
    parts = body.split(".")
    if len(parts) != 4:
        return None

    app_id, key_id, installation_id, signature = parts
    if expected_app_id and app_id != expected_app_id:
        return None
    if secret_key_id(secret) != key_id:
        return None

    message = _request_sign_message(app_id, key_id, installation_id)
    expected = _sign_payload(secret, message)
    if not hmac.compare_digest(signature, expected):
        return None
    return installation_id


def resolve_request_code(request_code: str) -> tuple[AppConfig, str, str] | None:
    code = request_code.strip()
    if not code.startswith(REQUEST_PREFIX):
        return None

    body = code[len(REQUEST_PREFIX) :]
    parts = body.split(".")
    if len(parts) != 4:
        return None

    app_id, key_id, installation_id, _signature = parts
    config = APP_CONFIGS.get(app_id)
    if not config:
        return None

    secret = load_secret_for_app(app_id)
    if not secret or secret_key_id(secret) != key_id:
        return None

    verified = _parse_request_code_v2(secret, code)
    if verified != installation_id:
        return None
    return config, secret, installation_id


def parse_request_code(config: AppConfig, secret: str, request_code: str) -> str | None:
    code = request_code.strip()
    if code.startswith(REQUEST_PREFIX):
        resolved = resolve_request_code(code)
        if not resolved:
            return None
        resolved_config, resolved_secret, installation_id = resolved
        if resolved_config.app_id != config.app_id:
            return None
        if resolved_secret != secret:
            return None
        return installation_id
    return _parse_request_code_v1(config, secret, request_code)


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
