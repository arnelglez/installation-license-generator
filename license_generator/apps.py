from __future__ import annotations

from dataclasses import dataclass
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


def load_secret_for_app(app_id: str) -> str:
    project_root = Path(__file__).resolve().parents[1]
    candidates = [
        project_root / f".env.{app_id}",
        project_root / ".env",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("INSTALLATION_LICENSE_SECRET"):
                _, _, value = line.partition("=")
                return value.strip().strip("'").strip('"')
    return ""
