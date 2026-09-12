# installation-license-generator

Desktop and CLI tool to generate installation licenses for **Vendix** (`VX1.`) and **biz-control** (`BC1.`).

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: INSTALLATION_LICENSE_SECRET
```

Per-app secrets (optional): `.env.vendix`, `.env.biz-control`.

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
