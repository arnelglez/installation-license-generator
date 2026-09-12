# installation-license-generator

Desktop and CLI tool to generate installation licenses for **Vendix** (`VX1.`) and **biz-control** (`BC1.`).

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional for local dev
```

For local development, secrets can live in `.env`:

```env
INSTALLATION_LICENSE_SECRET_VENDIX=...
INSTALLATION_LICENSE_SECRET_BIZ_CONTROL=...
```

## Executable (macOS)

```bash
./build.sh
```

Output: `dist/Generador de licencias.app`

Secrets are read from your local Vendix/biz-control `.env` files (or dev defaults) at **build time** and embedded inside the app. No external `.env` is needed to run the executable.

To override before building:

```bash
python prepare_bundled_secrets.py \
  --vendix-secret "..." \
  --biz-control-secret "..."
./build.sh
```

## GUI

```bash
python main.py
```

1. Select application (Vendix or biz-control)
2. Select period (1 month or 1 year)
3. Paste request code and generate

## CLI

```bash
python generate.py --app vendix --secret "..." --request "VX1...." --period year
python generate.py --app biz-control --secret "..." --request "BC1...." --period month
```
