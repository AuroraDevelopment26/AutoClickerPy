# AutoClicker

Ein einfacher, aber leistungsfähiger AutoClicker für Windows.

## Features

- **Frei konfigurierbares Intervall** – Stunden, Minuten, Sekunden, Millisekunden
- **Maustaste wählbar** – Links, Rechts, Mitte
- **Klick-Typ** – Single oder Double
- **Frei wählbarer Shortcut** – F6–F12, Strg+Kombos
- **Live-Klickzähler**
- **Automatische Update-Prüfung**
- **Einstellungen werden gespeichert**

## Download

[Letzte Version herunterladen](https://github.com/AnimaDev24/AutoClickerPy/releases)

## Nutzung

1. Setup.exe installieren
2. Mit **F6** (oder eigenem Shortcut) starten/stoppen
3. Intervall und Maustaste nach Wunsch einstellen

## Development

```bash
pip install pynput
python autoclicker.py
```

## Build

```bash
pip install pynput pyinstaller pillow
pyinstaller --onefile --windowed --name AutoClicker --icon icon.ico autoclicker.py
```
