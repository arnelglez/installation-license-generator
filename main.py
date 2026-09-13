#!/usr/bin/env python3
"""PyQt license generator for Vendix and biz-control installations."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from license_generator.apps import (
    APP_BIZ_CONTROL,
    APP_CONFIGS,
    APP_LABELS,
    APP_VENDIX,
    load_secret_for_app,
    secrets_are_bundled,
)
from license_generator.crypto import generate_license, parse_request_code, resolve_request_code
from license_generator.styles import APP_STYLESHEET

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def _assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "assets"
        if bundled.is_dir():
            return bundled
        return Path(sys._MEIPASS)
    return ASSETS_DIR


def _app_icon() -> QIcon | None:
    for name in ("vlaxsoft.icns", "vlaxsoft-icon.svg"):
        path = _assets_dir() / name
        if path.is_file():
            return QIcon(str(path))
    return None


def _card(object_name: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setFrameShape(QFrame.Shape.NoFrame)
    return frame


class LicenseGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de licencias — Vendix / biz-control")
        icon = _app_icon()
        if icon is not None:
            self.setWindowIcon(icon)
        self.resize(760, 720)
        self.setMinimumSize(640, 620)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        root = QWidget()
        scroll.setWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = _card("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(4)

        title = QLabel("Generador de licencias")
        title.setObjectName("headerTitle")
        subtitle = QLabel("Vendix · biz-control")
        subtitle.setObjectName("headerSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        intro_card = _card("introCard")
        intro_layout = QVBoxLayout(intro_card)
        intro_layout.setContentsMargins(16, 14, 16, 14)
        self.intro = QLabel()
        self.intro.setObjectName("intro")
        self.intro.setWordWrap(True)
        intro_layout.addWidget(self.intro)
        layout.addWidget(intro_card)

        form_card = _card("formCard")
        form_outer = QVBoxLayout(form_card)
        form_outer.setContentsMargins(16, 14, 16, 16)
        form_outer.setSpacing(12)

        form_title = QLabel("Datos de la licencia")
        form_title.setObjectName("sectionTitle")
        form_outer.addWidget(form_title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        self.app_combo = QComboBox()
        for app_id, label in APP_LABELS.items():
            self.app_combo.addItem(label, app_id)
        self.app_combo.currentIndexChanged.connect(self.on_app_changed)
        form.addRow(self._field_label("Aplicación"), self.app_combo)

        self.period_combo = QComboBox()
        self.period_combo.addItem("1 mes", "month")
        self.period_combo.addItem("1 año", "year")
        self.period_combo.setCurrentIndex(1)
        form.addRow(self._field_label("Vigencia"), self.period_combo)

        self.bundled_secrets = secrets_are_bundled()
        self.secret_label = self._field_label("Secreto")
        secret_row = QHBoxLayout()
        secret_row.setSpacing(8)
        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.secret_input.setPlaceholderText("INSTALLATION_LICENSE_SECRET")
        self.toggle_secret_btn = QPushButton("Mostrar")
        self.toggle_secret_btn.setObjectName("secondaryButton")
        self.toggle_secret_btn.setFixedWidth(88)
        self.toggle_secret_btn.clicked.connect(self.toggle_secret_visibility)
        secret_row.addWidget(self.secret_input, stretch=1)
        secret_row.addWidget(self.toggle_secret_btn)
        form.addRow(self.secret_label, secret_row)

        self.request_code_input = QTextEdit()
        self.request_code_input.setObjectName("requestInput")
        self.request_code_input.setFixedHeight(96)
        self.request_code_input.textChanged.connect(self.on_request_code_changed)
        form.addRow(self._field_label("Código solicitud"), self.request_code_input)

        form_outer.addLayout(form)
        layout.addWidget(form_card)

        self.generate_btn = QPushButton("Generar licencia")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_btn.clicked.connect(self.generate_license)
        layout.addWidget(self.generate_btn)

        output_card = _card("outputCard")
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(16, 14, 16, 16)
        output_layout.setSpacing(10)

        output_title = QLabel("Licencia generada")
        output_title.setObjectName("sectionTitle")
        output_layout.addWidget(output_title)

        self.output = QTextEdit()
        self.output.setObjectName("licenseOutput")
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("La licencia aparecerá aquí después de generarla…")
        self.output.setMinimumHeight(140)
        output_layout.addWidget(self.output)

        copy_row = QHBoxLayout()
        copy_row.setSpacing(10)
        self.copy_btn = QPushButton("Copiar licencia")
        self.copy_btn.setObjectName("secondaryButton")
        self.copy_btn.clicked.connect(self.copy_license)
        self.save_btn = QPushButton("Guardar como archivo…")
        self.save_btn.setObjectName("secondaryButton")
        self.save_btn.clicked.connect(self.save_license)
        copy_row.addWidget(self.copy_btn)
        copy_row.addWidget(self.save_btn)
        copy_row.addStretch()
        output_layout.addLayout(copy_row)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        output_layout.addWidget(self.status_label)

        layout.addWidget(output_card)
        layout.addStretch()

        if self.bundled_secrets:
            self.secret_label.hide()
            self.secret_input.hide()
            self.toggle_secret_btn.hide()

        self.on_app_changed()

    @staticmethod
    def _field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def current_app(self) -> str:
        return self.app_combo.currentData()

    def current_config(self):
        return APP_CONFIGS[self.current_app()]

    def set_status(self, message: str, *, error: bool = False) -> None:
        self.status_label.setText(message)
        self.status_label.setProperty("status", "error" if error else "ok")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def clear_status_later(self, delay_ms: int = 3000) -> None:
        QTimer.singleShot(delay_ms, lambda: self.set_status(""))

    def toggle_secret_visibility(self) -> None:
        if self.secret_input.echoMode() == QLineEdit.EchoMode.Password:
            self.secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_secret_btn.setText("Ocultar")
        else:
            self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_secret_btn.setText("Mostrar")

    def on_app_changed(self):
        config = self.current_config()
        if self.bundled_secrets:
            self.intro.setText(
                f"Pega un código de solicitud VX2 (incluye app, referencia al secreto e "
                f"instalación), elige vigencia y genera la licencia {config.prefix}."
            )
        else:
            self.intro.setText(
                f"Pega un código VX2 o legacy ({config.prefix}…), elige vigencia y genera "
                f"la licencia. Los códigos VX2 identifican la app y el secreto automáticamente."
            )
        self.request_code_input.setPlaceholderText("VX2.vendix.… o VX1.…")
        self.output.clear()
        self.set_status("")

        secret = load_secret_for_app(config.app_id)
        if secret and not self.bundled_secrets:
            self.secret_input.setText(secret)
        elif not self.bundled_secrets:
            self.secret_input.clear()

    def on_request_code_changed(self):
        request_code = self.request_code_input.toPlainText().strip()
        resolved = resolve_request_code(request_code)
        if not resolved:
            return
        config, _secret, _installation_id = resolved
        index = self.app_combo.findData(config.app_id)
        if index >= 0:
            self.app_combo.setCurrentIndex(index)

    def current_secret(self) -> str:
        if self.bundled_secrets:
            return load_secret_for_app(self.current_app())
        return self.secret_input.text().strip()

    def generate_license(self):
        request_code = self.request_code_input.toPlainText().strip()
        period = self.period_combo.currentData()

        if not request_code:
            self.set_status("El código de solicitud es obligatorio.", error=True)
            QMessageBox.warning(self, "Validación", "El código de solicitud es obligatorio.")
            return

        resolved = resolve_request_code(request_code)
        if resolved:
            config, secret, installation_id = resolved
        else:
            config = self.current_config()
            secret = self.current_secret()
            if not secret:
                self.set_status("El secreto es obligatorio.", error=True)
                QMessageBox.warning(self, "Validación", "El secreto es obligatorio.")
                return
            if not request_code.startswith(config.prefix):
                self.set_status(
                    f"El código legacy debe empezar por {config.prefix}.",
                    error=True,
                )
                QMessageBox.warning(
                    self,
                    "Validación",
                    f"El código legacy debe empezar por {config.prefix} "
                    f"(licencia {config.label}). Use VX2 para auto-detectar la app.",
                )
                return
            installation_id = parse_request_code(config, secret, request_code)
            if not installation_id:
                self.set_status("Código inválido o secreto incorrecto.", error=True)
                QMessageBox.critical(
                    self,
                    "Código inválido",
                    "El código de solicitud no es válido o no coincide con el secreto.",
                )
                return

        license_key = generate_license(config, secret, installation_id, period)
        self.output.setPlainText(license_key)
        period_label = "1 mes" if period == "month" else "1 año"
        self.set_status(f"Licencia {config.label} generada ({period_label}).")

    def copy_license(self):
        text = self.output.toPlainText().strip()
        if not text:
            self.set_status("Genera una licencia primero.", error=True)
            return
        QApplication.clipboard().setText(text)
        self.set_status("Licencia copiada al portapapeles.")
        self.clear_status_later()

    def save_license(self):
        text = self.output.toPlainText().strip()
        if not text:
            self.set_status("Genera una licencia primero.", error=True)
            return
        app = self.current_app()
        default_name = "vendix.license" if app == APP_VENDIX else "biz-control.license"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar licencia",
            default_name,
            "Licencia (*.license);;Texto (*.txt);;Todos (*)",
        )
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.set_status(f"Licencia guardada en {path}")
            self.clear_status_later(5000)


def main():
    app = QApplication(sys.argv)
    icon = _app_icon()
    if icon is not None:
        app.setWindowIcon(icon)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = LicenseGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
