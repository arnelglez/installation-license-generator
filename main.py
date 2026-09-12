#!/usr/bin/env python3
"""PyQt license generator for Vendix and biz-control installations."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from license_generator.apps import APP_BIZ_CONTROL, APP_CONFIGS, APP_LABELS, APP_VENDIX, load_secret_for_app
from license_generator.crypto import generate_license, parse_request_code


class LicenseGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de licencias — Vendix / biz-control")
        self.resize(720, 680)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.intro = QLabel()
        self.intro.setWordWrap(True)
        layout.addWidget(self.intro)

        form = QFormLayout()

        self.app_combo = QComboBox()
        for app_id, label in APP_LABELS.items():
            self.app_combo.addItem(label, app_id)
        self.app_combo.currentIndexChanged.connect(self.on_app_changed)
        form.addRow("Aplicación", self.app_combo)

        self.period_combo = QComboBox()
        self.period_combo.addItem("1 mes", "month")
        self.period_combo.addItem("1 año", "year")
        self.period_combo.setCurrentIndex(1)
        form.addRow("Vigencia", self.period_combo)

        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.secret_input.setPlaceholderText("INSTALLATION_LICENSE_SECRET")
        form.addRow("Secreto", self.secret_input)

        self.request_code_input = QTextEdit()
        self.request_code_input.setFixedHeight(90)
        form.addRow("Código solicitud", self.request_code_input)

        layout.addLayout(form)

        actions = QHBoxLayout()
        generate_btn = QPushButton("Generar licencia")
        generate_btn.clicked.connect(self.generate_license)
        actions.addWidget(generate_btn)
        layout.addLayout(actions)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Licencia generada…")
        layout.addWidget(self.output)

        copy_row = QHBoxLayout()
        copy_btn = QPushButton("Copiar licencia")
        copy_btn.clicked.connect(self.copy_license)
        save_btn = QPushButton("Guardar como archivo…")
        save_btn.clicked.connect(self.save_license)
        copy_row.addWidget(copy_btn)
        copy_row.addWidget(save_btn)
        layout.addLayout(copy_row)

        self.on_app_changed()

    def current_app(self) -> str:
        return self.app_combo.currentData()

    def current_config(self):
        return APP_CONFIGS[self.current_app()]

    def on_app_changed(self):
        config = self.current_config()
        self.intro.setText(
            f"Selecciona {config.label}, elige vigencia mensual o anual, pega el código de "
            f"solicitud ({config.prefix}…) y genera la licencia. El secreto debe coincidir con "
            f"INSTALLATION_LICENSE_SECRET del servidor {config.label}."
        )
        self.request_code_input.setPlaceholderText(f"{config.prefix}…")
        self.output.clear()

        secret = load_secret_for_app(config.app_id)
        if secret:
            self.secret_input.setText(secret)
        else:
            self.secret_input.clear()

    def generate_license(self):
        config = self.current_config()
        secret = self.secret_input.text().strip()
        request_code = self.request_code_input.toPlainText().strip()
        period = self.period_combo.currentData()

        if not secret:
            QMessageBox.warning(self, "Validación", "El secreto es obligatorio.")
            return
        if not request_code:
            QMessageBox.warning(self, "Validación", "El código de solicitud es obligatorio.")
            return
        if not request_code.startswith(config.prefix):
            QMessageBox.warning(
                self,
                "Validación",
                f"El código debe empezar por {config.prefix} (licencia {config.label}).",
            )
            return

        installation_id = parse_request_code(config, secret, request_code)
        if not installation_id:
            QMessageBox.critical(
                self,
                "Código inválido",
                "El código de solicitud no es válido o no coincide con el secreto.",
            )
            return

        license_key = generate_license(config, secret, installation_id, period)
        self.output.setPlainText(license_key)

    def copy_license(self):
        text = self.output.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Copiar", "Genera una licencia primero.")
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copiar", "Licencia copiada al portapapeles.")

    def save_license(self):
        text = self.output.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Guardar", "Genera una licencia primero.")
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
            QMessageBox.information(self, "Guardar", f"Licencia guardada en {path}")


def main():
    app = QApplication(sys.argv)
    window = LicenseGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
