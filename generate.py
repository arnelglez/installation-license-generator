#!/usr/bin/env python3
"""Headless license generator for Vendix or biz-control."""

from __future__ import annotations

import argparse
import sys

from license_generator.apps import APP_BIZ_CONTROL, APP_CONFIGS, APP_VENDIX
from license_generator.crypto import generate_license, parse_request_code, resolve_request_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an installation license from a request code."
    )
    parser.add_argument(
        "--app",
        choices=(APP_VENDIX, APP_BIZ_CONTROL),
        help="Target application (optional for VX2 request codes)",
    )
    parser.add_argument(
        "--secret",
        help="INSTALLATION_LICENSE_SECRET (optional for VX2 request codes)",
    )
    parser.add_argument("--request", required=True, help="Request code from the installation")
    parser.add_argument(
        "--period",
        choices=("month", "year"),
        default="year",
        help="License duration (default: year)",
    )
    args = parser.parse_args()

    request_code = args.request.strip()
    resolved = resolve_request_code(request_code)
    if resolved:
        config, secret, installation_id = resolved
    else:
        if not args.app or not args.secret:
            print(
                "Legacy request codes require --app and --secret. "
                "Use a VX2 request code to resolve them automatically.",
                file=sys.stderr,
            )
            return 1
        config = APP_CONFIGS[args.app]
        secret = args.secret
        if not request_code.startswith(config.prefix):
            print(
                f"Request code must start with {config.prefix} ({config.label}).",
                file=sys.stderr,
            )
            return 1
        installation_id = parse_request_code(config, secret, request_code)
        if not installation_id:
            print("Invalid request code or secret mismatch.", file=sys.stderr)
            return 1

    print(generate_license(config, secret, installation_id, args.period))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
