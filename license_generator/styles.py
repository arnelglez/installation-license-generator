"""Application stylesheet and visual tokens."""

APP_STYLESHEET = """
* {
    font-family: "Helvetica Neue", "Segoe UI", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background: #eef1f5;
}

#header {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1e3a5f,
        stop:1 #2563eb
    );
    border-radius: 12px;
}

#headerTitle {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
}

#headerSubtitle {
    color: rgba(255, 255, 255, 0.82);
    font-size: 13px;
}

#introCard, #formCard, #outputCard {
    background: #ffffff;
    border: 1px solid #d8dee8;
    border-radius: 12px;
}

#sectionTitle {
    color: #1f2937;
    font-size: 14px;
    font-weight: 600;
}

#intro {
    color: #4b5563;
    font-size: 13px;
    line-height: 1.45;
}

QLabel#fieldLabel {
    color: #374151;
    font-weight: 600;
    min-width: 120px;
}

QLineEdit, QComboBox, QTextEdit {
    background: #f9fafb;
    border: 1px solid #cfd6e0;
    border-radius: 8px;
    padding: 8px 10px;
    color: #111827;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #2563eb;
    background: #ffffff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}

#requestInput, #licenseOutput {
    font-family: "SF Mono", "Menlo", "Consolas", monospace;
    font-size: 12px;
}

#licenseOutput {
    background: #f3f6fb;
}

QPushButton {
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton#primaryButton {
    background: #2563eb;
    color: #ffffff;
    border: none;
}

QPushButton#primaryButton:hover {
    background: #1d4ed8;
}

QPushButton#primaryButton:pressed {
    background: #1e40af;
}

QPushButton#secondaryButton {
    background: #ffffff;
    color: #1f2937;
    border: 1px solid #cfd6e0;
}

QPushButton#secondaryButton:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
}

QPushButton#secondaryButton:pressed {
    background: #e5e7eb;
}

#statusLabel {
    color: #059669;
    font-weight: 600;
}

#statusLabel[status="error"] {
    color: #dc2626;
}
"""
