"""Small background app that rewrites or translates text using ChatGPT."""

import json
import os
import sys

import openai
from langdetect import detect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QLinearGradient, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
)
import keyboard


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".chatgpt_translator.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


class SettingsDialog(QDialog):
    def __init__(self, api_key):
        super().__init__()
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("OpenAI API Key:"))
        self.edit = QLineEdit(api_key)
        self.edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.edit)
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def api_key(self):  # noqa: D401 - simple getter
        """Return key entered."""
        return self.edit.text().strip()


class ProcessDialog(QDialog):
    MODES = {
        "Rewrite": "Rewrite the following text with improved style and clarity without changing its meaning:",
        "Translate to English": "Translate the following text into English:",
        "Friendlier": "Rewrite the following text in a friendlier tone:",
        "Summarize": "Summarize the following text:",
    }

    def __init__(self, text, api_key):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.resize(500, 400)
        self.api_key = api_key
        self.original = text
        layout = QVBoxLayout(self)
        lang = "?"
        try:  # pragma: no cover - simple heuristic
            lang = detect(text)
        except Exception:
            pass
        layout.addWidget(QLabel(f"Detected language: {lang}"))
        self.combo = QComboBox()
        self.combo.addItems(self.MODES.keys())
        layout.addWidget(self.combo)
        self.text = QTextEdit(text)
        layout.addWidget(self.text)
        btns = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run)
        btns.addWidget(self.run_btn)
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        btns.addWidget(undo_btn)
        layout.addLayout(btns)

    def run(self):
        if not self.api_key:
            QMessageBox.warning(self, "Missing Key", "Please set your API key in settings.")
            return
        openai.api_key = self.api_key
        prompt = self.MODES[self.combo.currentText()] + "\n\n" + self.original
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            result = resp["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # pragma: no cover - network errors
            QMessageBox.warning(self, "Error", str(exc))
            return
        QApplication.clipboard().setText(result)
        self.text.setPlainText(result)

    def undo(self):
        QApplication.clipboard().setText(self.original)
        self.text.setPlainText(self.original)


def create_icon():
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(0, 128, 64))
    gradient.setColorAt(1, QColor(0, 64, 128))
    painter.fillRect(pixmap.rect(), gradient)
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 28, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "T")
    painter.end()
    return QIcon(pixmap)


class TrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.config = load_config()
        self.api_key = self.config.get("api_key", "")
        self.tray = QSystemTrayIcon(create_icon())
        self.menu = QMenu()
        settings_action = self.menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        self.menu.addSeparator()
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.exit_app)
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("ChatGPT Translator")
        self.tray.show()
        keyboard.add_hotkey("ctrl+c, c", self.process_clipboard)

    def process_clipboard(self):
        text = QApplication.clipboard().text()
        if not text:
            return
        dlg = ProcessDialog(text, self.api_key)
        dlg.exec()

    def show_settings(self):
        dlg = SettingsDialog(self.api_key)
        if dlg.exec() == QDialog.Accepted:
            self.api_key = dlg.api_key()
            self.config["api_key"] = self.api_key
            save_config(self.config)

    def exit_app(self):
        keyboard.unhook_all_hotkeys()
        self.quit()


def main():
    app = TrayApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
