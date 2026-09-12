#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d venv ]]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt pyinstaller

python prepare_bundled_secrets.py
python build_icon.py

rm -rf build dist
pyinstaller --noconfirm license-generator.spec

echo
echo "Build complete:"
echo "  dist/Generador de licencias.app"
echo
echo "Secrets are embedded in the executable (no external .env required)."
