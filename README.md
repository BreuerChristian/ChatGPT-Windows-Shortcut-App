# ChatGPT Windows Shortcut App

This is a small Windows application that shows [chatgpt.com](https://chatgpt.com) in a window. The window can be toggled either via a global keyboard shortcut or through the tray icon.

## Features

- Global shortcut (default `Ctrl+G` followed by `G`) toggles the window.
- Tray icon with options to show/hide the window, change the hotkey, and quit the application.
 - The hotkey can be changed using the tray icon menu.
- Optional setting to start the app automatically with Windows (via tray icon).
- Uses a simple dark theme for a clean look.

## Running

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python3 main.py
```

The app starts minimized to the tray. Use the default shortcut `Ctrl+G` then `G` to show or hide the window. You can change this shortcut from the tray icon menu.

## ChatGPT Translator

`translator_app.py` implements a small helper similar to DeepL. Press `Ctrl+C` twice to rewrite or translate the selected text using the OpenAI ChatGPT API. The result is shown in a popup and copied back to the clipboard.

Before using it, set your OpenAI key in the tray icon menu under *Settings*.

Run it via:

```bash
python3 translator_app.py
```
