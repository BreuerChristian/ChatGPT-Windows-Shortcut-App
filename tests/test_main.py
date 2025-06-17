import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import types
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import main

app = QApplication.instance()
if app is None:
    app = QApplication([])

def test_create_icon_returns_qicon():
    icon = main.create_icon()
    assert isinstance(icon, QIcon)

def test_change_hotkey_logic(monkeypatch):
    dummy = types.SimpleNamespace()
    dummy.hotkey = 'ctrl+g, g'
    dummy.hotkey_action = types.SimpleNamespace()
    dummy.hotkey_action.setText = lambda text: setattr(dummy, 'action_text', text)
    dummy.toggle_window = lambda: None

    added = []
    removed = []
    monkeypatch.setattr(main.keyboard, 'add_hotkey', lambda hk, cb: added.append(hk))
    monkeypatch.setattr(main.keyboard, 'remove_hotkey', lambda hk: removed.append(hk))
    monkeypatch.setattr(main.QInputDialog, 'getText', lambda *a, **k: ('ctrl+h, h', True))
    monkeypatch.setattr(main.QMessageBox, 'warning', lambda *a, **k: None)

    main.TrayApp.change_hotkey(dummy)

    assert added == ['ctrl+h, h']
    assert removed == ['ctrl+g, g']
    assert dummy.hotkey == 'ctrl+h, h'
    assert dummy.action_text == 'Set Hotkey (ctrl+h, h)'


def test_set_autostart_enable_disable(monkeypatch):
    calls = {}

    class DummyKey:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    dummy_key = DummyKey()

    def open_key(hive, path, reserved=0, access=0):
        calls['open'] = (hive, path, access)
        return dummy_key

    def set_value_ex(key, name, reserved, typ, value):
        calls['set'] = (key, name, value)

    def delete_value(key, name):
        calls['del'] = (key, name)

    fake_winreg = types.SimpleNamespace(
        HKEY_CURRENT_USER=1,
        KEY_SET_VALUE=2,
        REG_SZ=1,
        OpenKey=open_key,
        SetValueEx=set_value_ex,
        DeleteValue=delete_value,
    )

    monkeypatch.setitem(sys.modules, 'winreg', fake_winreg)
    monkeypatch.setattr(main.sys, 'platform', 'win32')
    monkeypatch.setattr(main.sys, 'executable', 'python')
    monkeypatch.setattr(main.os.path, 'abspath', lambda p: 'main.py')

    main.set_autostart(True)
    assert calls['set'] == (dummy_key, 'ChatGPTShortcut', '"python" "main.py"')

    main.set_autostart(False)
    assert calls['del'] == (dummy_key, 'ChatGPTShortcut')
