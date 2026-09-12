# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = collect_submodules("cryptography")

bundled_secrets = Path("license_generator/bundled_secrets.env")
icon_file = Path("assets/vlaxsoft.icns")
if not bundled_secrets.is_file():
    raise SystemExit(
        "Missing license_generator/bundled_secrets.env — run: python prepare_bundled_secrets.py"
    )
if not icon_file.is_file():
    raise SystemExit("Missing assets/vlaxsoft.icns — run: python build_icon.py")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (str(bundled_secrets), "."),
        (str(icon_file), "assets"),
        ("assets/vlaxsoft-icon.svg", "assets"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="license-generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="license-generator",
)

app = BUNDLE(
    coll,
    name="Generador de licencias.app",
    icon="assets/vlaxsoft.icns",
    bundle_identifier="com.vlaxsoft.license-generator",
)
