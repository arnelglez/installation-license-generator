#!/usr/bin/env python3
"""Embed app secrets into the executable at build time."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from license_generator.apps import (
    APP_BIZ_CONTROL,
    APP_VENDIX,
    _parse_env_file,
    _secret_env_key,
)

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT = PROJECT_ROOT / "license_generator" / "bundled_secrets.env"

DEFAULT_SOURCES = {
    APP_VENDIX: [
        Path.home() / "Projects" / "Vendix" / "backend" / ".env",
        PROJECT_ROOT / ".env.vendix",
    ],
    APP_BIZ_CONTROL: [
        Path.home() / "Projects" / "biz-control" / "backend" / ".env",
        PROJECT_ROOT / ".env.biz-control",
    ],
}

DEV_DEFAULTS = {
    APP_VENDIX: "vendix-installation-license-dev-secret",
    APP_BIZ_CONTROL: "biz-control-installation-license-dev-secret",
}


def _read_secret(app_id: str, explicit: str, sources: list[Path]) -> str:
    if explicit:
        return explicit.strip()

    env_key = _secret_env_key(app_id)
    from_env = os.environ.get(env_key, "").strip()
    if from_env:
        return from_env

    shared_path = PROJECT_ROOT / ".env"
    if shared_path.is_file():
        shared = _parse_env_file(shared_path)
        if secret := shared.get(env_key) or shared.get("INSTALLATION_LICENSE_SECRET", ""):
            return secret

    for path in sources:
        if path.is_file():
            secret = _parse_env_file(path).get("INSTALLATION_LICENSE_SECRET", "")
            if secret:
                return secret

    return DEV_DEFAULTS[app_id]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--vendix-secret", default="")
    parser.add_argument("--biz-control-secret", default="")
    args = parser.parse_args()

    lines = ["# Bundled at build time — do not commit"]
    missing = []
    for app_id, explicit in (
        (APP_VENDIX, args.vendix_secret),
        (APP_BIZ_CONTROL, args.biz_control_secret),
    ):
        secret = _read_secret(app_id, explicit, DEFAULT_SOURCES[app_id])
        if not secret:
            missing.append(app_id)
            continue
        lines.append(f"{_secret_env_key(app_id)}={secret}")

    if missing:
        print(f"Missing secrets for: {', '.join(missing)}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} (secrets embedded for build)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
