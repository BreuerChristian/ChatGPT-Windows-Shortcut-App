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
