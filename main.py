import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QInputDialog,
    QLineEdit,
    QMessageBox,
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QLinearGradient, QFont
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import keyboard


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
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "G")
    painter.end()
    return QIcon(pixmap)


def is_autostart_enabled():
    """Return True if the app is set to start with Windows."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
    except Exception:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
        ) as key:
            winreg.QueryValueEx(key, "ChatGPTShortcut")
            return True
    except FileNotFoundError:
        return False


def set_autostart(enable: bool) -> None:
    """Enable or disable autostart via the Windows registry."""
    if sys.platform != "win32":
        return
    try:
        import winreg
    except Exception:
        return
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enable:
            value = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, "ChatGPTShortcut", 0, winreg.REG_SZ, value)
        else:
            try:
                winreg.DeleteValue(key, "ChatGPTShortcut")
            except FileNotFoundError:
                pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Shortcut")
        self.resize(1024, 768)
        self.web = QWebEngineView()
        self.web.load(QUrl("https://chatgpt.com"))
        self.setCentralWidget(self.web)
        self.setStyleSheet("background-color: #202124; color: white;")


class TrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.window = MainWindow()
        self.hotkey = 'ctrl+g, g'
        self.tray = QSystemTrayIcon(create_icon())
        self.menu = QMenu()
        self.toggle_action = self.menu.addAction('Show')
        self.toggle_action.triggered.connect(self.toggle_window)
        self.hotkey_action = self.menu.addAction(f'Set Hotkey ({self.hotkey})')
        self.hotkey_action.triggered.connect(self.change_hotkey)
        if sys.platform == 'win32':
            self.autostart_action = self.menu.addAction('Start with Windows')
            self.autostart_action.setCheckable(True)
            self.autostart_action.setChecked(is_autostart_enabled())
            self.autostart_action.triggered.connect(self.toggle_autostart)
        else:
            self.autostart_action = self.menu.addAction('Start with Windows')
            self.autostart_action.setEnabled(False)
        self.menu.addSeparator()
        quit_action = self.menu.addAction('Quit')
        quit_action.triggered.connect(self.exit_app)
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip('ChatGPT Shortcut')
        self.tray.show()
        self.register_hotkey()

    def toggle_window(self):
        if self.window.isVisible():
            self.window.hide()
            self.toggle_action.setText('Show')
        else:
            self.window.show()
            self.toggle_action.setText('Hide')

    def register_hotkey(self):
        keyboard.add_hotkey(self.hotkey, self.toggle_window)

    def toggle_autostart(self):
        enabled = self.autostart_action.isChecked()
        set_autostart(enabled)

    def change_hotkey(self):
        text, ok = QInputDialog.getText(
            None,
            'Set Hotkey',
            'Enter new hotkey (e.g., ctrl+g, g):',
            QLineEdit.Normal,
            self.hotkey,
        )
        if ok and text:
            try:
                keyboard.add_hotkey(text, self.toggle_window)
            except ValueError as exc:
                QMessageBox.warning(None, 'Invalid Hotkey', str(exc))
                return
            keyboard.remove_hotkey(self.hotkey)
            self.hotkey = text
            self.hotkey_action.setText(f'Set Hotkey ({self.hotkey})')

    def exit_app(self):
        keyboard.unhook_all_hotkeys()
        self.quit()


def main():
    app = TrayApp(sys.argv)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
