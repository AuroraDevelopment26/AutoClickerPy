import tkinter as tk
import customtkinter as ctk  
import threading
import time
import json
import os
import sys
import ctypes
from urllib.request import urlopen, Request
from pynput import mouse, keyboard


def _app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def _config_path():
    return os.path.join(_app_path(), "autoclicker_config.json")


def _read_config(key, default=None):
    try:
        with open(_config_path()) as f:
            return json.load(f).get(key, default)
    except Exception:
        return default


def get_app_version():
    return _read_config("version") or "1.0"


def get_update_url():
    return _read_config("update_url") or ""

HOTKEY_DISPLAY = [
    "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "Strg+F6", "Strg+F7", "Strg+F8",
    "Strg+Umschalt+X", "Strg+Umschalt+Z",
    "Strg+Alt+X", "Strg+Alt+Z"
]

HOTKEY_MAP = {
    "F6": "<f6>", "F7": "<f7>", "F8": "<f8>", "F9": "<f9>",
    "F10": "<f10>", "F11": "<f11>", "F12": "<f12>",
    "Strg+F6": "<ctrl>+f6", "Strg+F7": "<ctrl>+f7", "Strg+F8": "<ctrl>+f8",
    "Strg+Umschalt+X": "<ctrl>+<shift>+x",
    "Strg+Umschalt+Z": "<ctrl>+<shift>+z",
    "Strg+Alt+X": "<ctrl>+<alt>+x",
    "Strg+Alt+Z": "<ctrl>+<alt>+z"
}

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker – Aurora")
        self.root.geometry("420x500")
        self.root.resizable(False, False)
        
        # 1. Kantigen Windows-Rahmen komplett entfernen
        self.root.overrideredirect(True)
        
        # 2. Windows-Spezifischer Transparenz-Trick für abgerundete Ecken
        self.root.wm_attributes("-transparentcolor", "#010101")
        self.root.configure(fg_color="#010101") 
        
        # 3. Restliche Windows-Rahmenlinien via Windows-API entfernen
        self._remove_windows_border()

        self.clicking = False
        self.running = True
        self.click_count = 0

        self.interval_h = tk.IntVar(value=0)
        self.interval_m = tk.IntVar(value=0)
        self.interval_s = tk.IntVar(value=0)
        self.interval_ms = tk.IntVar(value=100)

        self.click_button = tk.StringVar(value="Links")
        self.click_type = tk.StringVar(value="Single")
        self.hotkey = tk.StringVar(value="F6")

        self._load_config()
        self._build_ui()
        self._start_listener()
        self._update_status()
        self._update_version_label()
        
        # Variablen für das Verschieben des Fensters per Maus
        self._start_x = 0
        self._start_y = 0

        threading.Thread(target=self._check_update_silent, daemon=True).start()

    def _remove_windows_border(self):
        # Nutzt die Windows DWM-API, um verbleibende Rahmenlinien unsichtbar zu machen
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            
            DWMWA_BORDER_COLOR = 34
            color = 0xFFFFFFFE  # Spezieller Windows-Flag für "Kein Rahmen"
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_BORDER_COLOR, ctypes.byref(ctypes.c_int(color)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    def _build_ui(self):
        # Die abgerundete Hauptkarte (unser eigentlicher Fenster-Hintergrund)
        window_card = ctk.CTkFrame(self.root, fg_color="#181825", corner_radius=24, border_width=1, border_color="#252538")
        window_card.pack(fill=tk.BOTH, expand=True)

        # Neuer, moderner Titelbalken zum Verschieben und Schließen
        title_bar = ctk.CTkFrame(window_card, fg_color="transparent", height=40)
        title_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        title_bar.pack_propagate(False)
        
        # Drag & Drop Events an den Titelbalken binden
        title_bar.bind("<Button-1>", self._on_press)
        title_bar.bind("<B1-Motion>", self._on_drag)

        # Schließen-Button (X) oben rechts
        close_btn = ctk.CTkButton(title_bar, text="×", font=("Plus Jakarta Sans", 18), 
                                  fg_color="transparent", text_color="#6c7086", hover_color="#f38ba8", 
                                  width=28, height=28, corner_radius=8, command=self._on_close)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Kleiner Titel im Balken
        title_mini = ctk.CTkLabel(title_bar, text="AutoClicker", font=("Plus Jakarta Sans", 12, "bold"), text_color="#585b70")
        title_mini.pack(side=tk.LEFT, padx=10)
        title_mini.bind("<Button-1>", self._on_press)
        title_mini.bind("<B1-Motion>", self._on_drag)

        # Haupt-Container für die Controls
        container = ctk.CTkFrame(window_card, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))

        # Titel / Header
        title_label = ctk.CTkLabel(container, text="AutoClicker", font=("Plus Jakarta Sans", 24, "bold"), text_color="#ffffff")
        title_label.pack(pady=(5, 2))
        
        # FEHLER BEHOBEN: 'text_spacing' wurde hier entfernt, da es von CTkLabel nicht unterstützt wird
        sub_label = ctk.CTkLabel(container, text="AURORA DEVELOPMENT", font=("Plus Jakarta Sans", 9, "bold"), text_color="#6c7086")
        sub_label.pack(pady=(0, 20))

        # --- SEKTION: INTERVALL ---
        interval_frame = ctk.CTkFrame(container, fg_color="transparent")
        interval_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(interval_frame, text="Klick-Intervall", font=("Plus Jakarta Sans", 12, "bold"), text_color="#cdd6f4").pack(anchor=tk.W, padx=4)
        
        spin_container = ctk.CTkFrame(interval_frame, fg_color="transparent")
        spin_container.pack(fill=tk.X, pady=(6, 10))

        def create_input_field(label_text, var):
            frame = ctk.CTkFrame(spin_container, fg_color="transparent")
            frame.pack(side=tk.LEFT, expand=True, padx=4)
            ctk.CTkLabel(frame, text=label_text, font=("Plus Jakarta Sans", 10, "bold"), text_color="#585b70").pack(pady=(0, 2))
            entry = ctk.CTkEntry(frame, width=60, height=32, textvariable=var, justify=tk.CENTER, font=("Plus Jakarta Sans", 13, "bold"), fg_color="#313244", border_color="#45475a", text_color="#cdd6f4", corner_radius=8)
            entry.pack()

        create_input_field("Std", self.interval_h)
        create_input_field("Min", self.interval_m)
        create_input_field("Sek", self.interval_s)
        create_input_field("ms", self.interval_ms)

        # --- SEKTION: DROPDOWNS ---
        dropdown_frame = ctk.CTkFrame(container, fg_color="transparent")
        dropdown_frame.pack(fill=tk.X, pady=10)
        dropdown_frame.columnconfigure(1, weight=1)

        def add_row(row_idx, label_text, var, values, callback=None):
            lbl = ctk.CTkLabel(dropdown_frame, text=label_text, font=("Plus Jakarta Sans", 12, "bold"), text_color="#cdd6f4")
            lbl.grid(row=row_idx, column=0, sticky=tk.W, pady=8, padx=4)
            
            combo = ctk.CTkComboBox(dropdown_frame, values=values, variable=var, font=("Plus Jakarta Sans", 12, "bold"),
                                    fg_color="#313244", border_color="#45475a", button_color="#45475a",
                                    button_hover_color="#585b70", text_color="#cdd6f4", dropdown_fg_color="#1e1e2e",
                                    dropdown_text_color="#cdd6f4", dropdown_hover_color="#313244", corner_radius=8, height=36)
            combo.grid(row=row_idx, column=1, sticky=tk.EW, padx=(24, 0), pady=8)
            if callback:
                combo.configure(command=lambda _: callback())

        add_row(0, "Maustaste", self.click_button, ["Links", "Rechts", "Mitte"])
        add_row(1, "Klick-Typ", self.click_type, ["Single", "Double"])
        add_row(2, "Shortcut", self.hotkey, HOTKEY_DISPLAY, self._start_listener)

        # --- SEKTION: STATUS & UTILS ---
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(fill=tk.X, pady=(15, 10))

        self.status_label = ctk.CTkLabel(info_frame, text="Gestoppt", font=("Plus Jakarta Sans", 13, "bold"), text_color="#f38ba8")
        self.status_label.pack(side=tk.LEFT, padx=4)

        self.count_label = ctk.CTkLabel(info_frame, text="Klicks: 0", font=("Plus Jakarta Sans", 12, "bold"), text_color="#a6adc8")
        self.count_label.pack(side=tk.RIGHT, padx=4)

        # Großer Start/Stopp Action-Button
        self.toggle_btn = ctk.CTkButton(container, text="Starten (F6)", font=("Plus Jakarta Sans", 14, "bold"),
                                        fg_color="#ffffff", text_color="#11111b", hover_color="#89b4fa",
                                        corner_radius=10, height=46, command=self.toggle)
        self.toggle_btn.pack(fill=tk.X, pady=(5, 15))

        # Footer / Updates
        update_frame = ctk.CTkFrame(container, fg_color="transparent")
        update_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_btn = ctk.CTkButton(update_frame, text="Nach Updates suchen", font=("Plus Jakarta Sans", 11, "bold"),
                                        fg_color="#313244", text_color="#cdd6f4", hover_color="#45475a",
                                        height=28, corner_radius=6, command=self._check_update)
        self.update_btn.pack(side=tk.LEFT, padx=4)

        self.update_label = ctk.CTkLabel(update_frame, text="", font=("Plus Jakarta Sans", 11), text_color="#6c7086")
        self.update_label.pack(side=tk.LEFT, padx=(10, 0))

        self.version_label = ctk.CTkLabel(update_frame, text="", font=("Plus Jakarta Sans", 10), text_color="#585b70")
        self.version_label.pack(side=tk.RIGHT, padx=4)

    # Fenster-Bewegungs-Logik per Mauszug
    def _on_press(self, event):
        self._start_x = event.x
        self._start_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._start_x + event.x
        y = self.root.winfo_y() - self._start_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def _get_interval_sec(self):
        try:
            return (self.interval_h.get() * 3600 +
                    self.interval_m.get() * 60 +
                    self.interval_s.get() +
                    self.interval_ms.get() / 1000)
        except Exception:
            return 0.1

    def _update_version_label(self):
        ver = get_app_version()
        self.version_label.configure(text=f"v{ver}")

    def _update_status(self):
        current_hotkey = self.hotkey.get()
        if self.clicking:
            self.status_label.configure(text="Aktiv - Klickt...", text_color="#a6e3a1")
            self.toggle_btn.configure(text=f"Stoppen ({current_hotkey})", fg_color="#89b4fa", text_color="#11111b")
        else:
            self.status_label.configure(text="Gestoppt", text_color="#f38ba8")
            self.toggle_btn.configure(text=f"Starten ({current_hotkey})", fg_color="#ffffff", text_color="#11111b")

    def toggle(self):
        self.clicking = not self.clicking
        self._update_status()
        if not self.clicking:
            self._save_config()
        else:
            self.click_count = 0
            self.count_label.configure(text="Klicks: 0")
            threading.Thread(target=self._click_loop, daemon=True).start()

    def _start_listener(self):
        if hasattr(self, 'listener'):
            self.listener.stop()
        display = self.hotkey.get()
        hk = HOTKEY_MAP.get(display, display)
        self.listener = keyboard.GlobalHotKeys({hk: self.toggle})
        self.listener.start()

    def _load_config(self):
        p = _config_path()
        if not os.path.exists(p):
            return
        try:
            with open(p) as f:
                d = json.load(f)
            self.interval_h.set(d.get("h", 0))
            self.interval_m.set(d.get("m", 0))
            self.interval_s.set(d.get("s", 0))
            self.interval_ms.set(d.get("ms", 100))
            self.click_button.set(d.get("btn", "Links"))
            self.click_type.set(d.get("type", "Single"))
            self.hotkey.set(d.get("hotkey", "F6"))
        except Exception:
            pass

    def _save_config(self):
        d = {
            "version": get_app_version(),
            "update_url": get_update_url(),
            "h": self.interval_h.get(),
            "m": self.interval_m.get(),
            "s": self.interval_s.get(),
            "ms": self.interval_ms.get(),
            "btn": self.click_button.get(),
            "type": self.click_type.get(),
            "hotkey": self.hotkey.get(),
        }
        with open(_config_path(), "w") as f:
            json.dump(d, f, indent=2)

    def _check_update_silent(self):
        time.sleep(3)
        try:
            self._do_check(silent=True)
        except Exception:
            pass

    def _check_update(self):
        self.update_label.configure(text="Suche...", text_color="#6c7086")
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self, silent=False):
        url = get_update_url()
        try:
            req = Request(url, headers={"User-Agent": "AutoClicker/1.0"})
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            remote = data.get("version", "")
            installer = data.get("installer_url", "")

            if not remote or not installer:
                return

            app_ver = get_app_version()
            if self._is_newer(remote, app_ver):
                self.root.after(0, lambda: self._ask_update(remote, installer))
            elif not silent:
                self.root.after(0, lambda: self.update_label.configure(
                    text=f"v{app_ver} ist aktuell", text_color="#a6e3a1"))
        except Exception:
            if not silent:
                self.root.after(0, lambda: self.update_label.configure(
                    text="Offline", text_color="#f38ba8"))

    def _is_newer(self, remote, current):
        try:
            r = tuple(int(x) for x in remote.split("."))
            c = tuple(int(x) for x in current.split("."))
            return r > c
        except Exception:
            return False

    def _ask_update(self, version, installer_url):
        from tkinter import messagebox
        app_ver = get_app_version()
        if messagebox.askyesno(
            "Update verfügbar",
            f"Version {version} ist verfügbar.\n"
            f"Aktuelle Version: {app_ver}\n\n"
            "Die App wird geschlossen und der Download gestartet."
        ):
            self._download_and_close(installer_url)

    def _download_and_close(self, url):
        from tkinter import messagebox
        self.clicking = False
        self.running = False
        self.listener.stop()
        self.root.withdraw()

        import tempfile
        import subprocess
        try:
            path = os.path.join(tempfile.gettempdir(), "AutoClicker_Update_Setup.exe")
            req = Request(url, headers={"User-Agent": "AutoClicker/1.0"})
            with urlopen(req, timeout=120) as resp:
                with open(path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            subprocess.Popen(
                [path, "/SP-", "/NORESTART"],
                creationflags=subprocess.DETACHED_PROCESS,
                close_fds=True
            )
        except Exception:
            messagebox.showerror("Fehler", "Download fehlgeschlagen.")
        finally:
            self.root.destroy()

    def _click_loop(self):
        ctrl = mouse.Controller()
        btn_map = {"Links": mouse.Button.left,
                   "Rechts": mouse.Button.right,
                   "Mitte": mouse.Button.middle}
        btn = btn_map[self.click_button.get()]

        while self.clicking and self.running:
            interval = self._get_interval_sec()
            if interval <= 0:
                interval = 0.001

            if self.click_type.get() == "Double":
                ctrl.click(btn, 2)
                self.click_count += 2
            else:
                ctrl.click(btn)
                self.click_count += 1

            self.count_label.configure(text=f"Klicks: {self.click_count}")
            time.sleep(interval)

    def _on_close(self):
        self._save_config()
        self.running = False
        self.clicking = False
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AutoClicker(root)
    root.mainloop()