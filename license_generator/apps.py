from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

APP_VENDIX = "vendix"
APP_BIZ_CONTROL = "biz-control"

LicensePeriod = Literal["month", "year"]

APP_LABELS = {
    APP_VENDIX: "Vendix",
    APP_BIZ_CONTROL: "biz-control",
}


@dataclass(frozen=True)
class AppConfig:
    app_id: str
    label: str
    prefix: str
    payload_app: str | None


APP_CONFIGS: dict[str, AppConfig] = {
    APP_VENDIX: AppConfig(
        app_id=APP_VENDIX,
        label="Vendix",
        prefix="VX1.",
        payload_app="vendix",
    ),
    APP_BIZ_CONTROL: AppConfig(
        app_id=APP_BIZ_CONTROL,
        label="biz-control",
        prefix="BC1.",
        payload_app=None,
    ),
}


def _secret_env_key(app_id: str) -> str:
    suffix = app_id.replace("-", "_").upper()
    return f"INSTALLATION_LICENSE_SECRET_{suffix}"


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _bundled_secrets_path() -> Path | None:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys._MEIPASS) / "bundled_secrets.env")
    candidates.append(Path(__file__).resolve().parent / "bundled_secrets.env")
    for path in candidates:
        if path.is_file():
            return path
    return None


@lru_cache(maxsize=1)
def _bundled_secrets() -> dict[str, str]:
    path = _bundled_secrets_path()
    if not path:
        return {}
    return _parse_env_file(path)


def secrets_are_bundled() -> bool:
    return bool(_bundled_secrets())


def _env_search_roots() -> list[Path]:
    return [Path(__file__).resolve().parents[1]]


def load_secret_for_app(app_id: str) -> str:
    specific_key = _secret_env_key(app_id)
    bundled = _bundled_secrets()
    if bundled:
        return bundled.get(specific_key, "")

    if getattr(sys, "frozen", False):
        return ""

    for project_root in _env_search_roots():
        per_app = project_root / f".env.{app_id}"
        if per_app.is_file():
            secret = _parse_env_file(per_app).get("INSTALLATION_LICENSE_SECRET", "")
            if secret:
                return secret

        shared = project_root / ".env"
        if shared.is_file():
            values = _parse_env_file(shared)
            secret = values.get(specific_key) or values.get("INSTALLATION_LICENSE_SECRET", "")
            if secret:
                return secret
    return ""
