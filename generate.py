#!/usr/bin/env python3
"""Headless license generator for Vendix or biz-control."""

from __future__ import annotations

import argparse
import sys

from license_generator.apps import APP_BIZ_CONTROL, APP_CONFIGS, APP_VENDIX
from license_generator.crypto import generate_license, parse_request_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an installation license from a request code."
    )
    parser.add_argument(
        "--app",
        choices=(APP_VENDIX, APP_BIZ_CONTROL),
        required=True,
        help="Target application",
    )
    parser.add_argument("--secret", required=True, help="INSTALLATION_LICENSE_SECRET")
    parser.add_argument("--request", required=True, help="Request code from the installation")
    parser.add_argument(
        "--period",
        choices=("month", "year"),
        default="year",
        help="License duration (default: year)",
    )
    args = parser.parse_args()

    config = APP_CONFIGS[args.app]
    request_code = args.request.strip()
    if not request_code.startswith(config.prefix):
        print(
            f"Request code must start with {config.prefix} ({config.label}).",
            file=sys.stderr,
        )
        return 1

    installation_id = parse_request_code(config, args.secret, request_code)
    if not installation_id:
        print("Invalid request code or secret mismatch.", file=sys.stderr)
        return 1

    print(generate_license(config, args.secret, installation_id, args.period))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
