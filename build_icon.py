#!/usr/bin/env python3
"""Render VLAXSoft SVG assets into a macOS .icns file."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parent
SVG_PATH = PROJECT_ROOT / "assets" / "vlaxsoft-icon.svg"
ICONSET_DIR = PROJECT_ROOT / "assets" / "vlaxsoft.iconset"
ICNS_PATH = PROJECT_ROOT / "assets" / "vlaxsoft.icns"

ICON_SIZES = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def render_png(svg: QSvgRenderer, size: int, output: Path) -> None:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    svg.render(painter)
    painter.end()
    output.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(output), "PNG"):
        raise RuntimeError(f"Could not write {output}")


def main() -> int:
    if not SVG_PATH.is_file():
        print(f"Missing SVG: {SVG_PATH}", file=sys.stderr)
        return 1

    app = QApplication(sys.argv)
    renderer = QSvgRenderer(str(SVG_PATH))
    if not renderer.isValid():
        print(f"Invalid SVG: {SVG_PATH}", file=sys.stderr)
        return 1

    if ICONSET_DIR.exists():
        shutil.rmtree(ICONSET_DIR)
    ICONSET_DIR.mkdir(parents=True)

    for filename, size in ICON_SIZES.items():
        render_png(renderer, size, ICONSET_DIR / filename)

    if ICNS_PATH.exists():
        ICNS_PATH.unlink()

    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_PATH)],
        check=True,
    )
    print(f"Wrote {ICNS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
