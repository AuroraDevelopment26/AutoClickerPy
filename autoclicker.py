import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError
from pynput import mouse, keyboard


CONFIG_FILE = "autoclicker_config.json"
DEFAULT_VERSION = "1.2"
DEFAULT_UPDATE_URL = "https://gist.githubusercontent.com/AnimaDev24/4aef74220ecad2f569e06b6027a2199e/raw/gistfile1.txt"


def _read_config(key, default):
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f).get(key, default)
    except Exception:
        return default


def get_app_version():
    return _read_config("version", DEFAULT_VERSION)


def get_update_url():
    return _read_config("update_url", DEFAULT_UPDATE_URL)

HOTKEY_DISPLAY = [
    "F6", "F7", "F8", "F9",
    "F10", "F11", "F12",
    "Strg+F6", "Strg+F7", "Strg+F8",
    "Strg+Umschalt+X", "Strg+Umschalt+Z",
    "Strg+Alt+X", "Strg+Alt+Z",
]

HOTKEY_MAP = {
    "F6": "<f6>", "F7": "<f7>", "F8": "<f8>", "F9": "<f9>",
    "F10": "<f10>", "F11": "<f11>", "F12": "<f12>",
    "Strg+F6": "<ctrl>+f6", "Strg+F7": "<ctrl>+f7", "Strg+F8": "<ctrl>+f8",
    "Strg+Umschalt+X": "<ctrl>+<shift>+x",
    "Strg+Umschalt+Z": "<ctrl>+<shift>+z",
    "Strg+Alt+X": "<ctrl>+<alt>+x",
    "Strg+Alt+Z": "<ctrl>+<alt>+z",
}


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.geometry("420x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

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

        self._setup_styles()
        self._set_icon()
        self._load_config()
        self._build_ui()
        self._start_listener()
        self._update_status()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        threading.Thread(target=self._check_update_silent, daemon=True).start()

    def _set_icon(self):
        base = os.path.dirname(__file__)
        ico = os.path.join(base, "icon.ico")
        png = os.path.join(base, "icon.png")
        if os.path.exists(ico):
            try:
                self.root.iconbitmap(ico)
                return
            except Exception:
                pass
        if os.path.exists(png):
            try:
                img = tk.PhotoImage(file=png)
                self.root.iconphoto(True, img)
                self._icon_img = img
            except Exception:
                pass

    def _start_listener(self):
        if hasattr(self, 'listener'):
            self.listener.stop()
        display = self.hotkey.get()
        hk = HOTKEY_MAP.get(display, display)
        self.listener = keyboard.GlobalHotKeys({hk: self.toggle})
        self.listener.start()

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE) as f:
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
        with open(CONFIG_FILE, "w") as f:
            json.dump(d, f, indent=2)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 9))
        style.configure("TButton", background="#313244", foreground="#cdd6f4",
                        font=("Segoe UI", 9), borderwidth=1, focusthickness=0)
        style.map("TButton", background=[("active", "#45475a")])
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"),
                        background="#1e1e2e", foreground="#cdd6f4")
        style.configure("Accent.TButton", background="#89b4fa",
                        foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#74c7ec")])
        style.configure("TSeparator", background="#45475a")
        style.configure("TCombobox", fieldbackground="#313244",
                        background="#313244", foreground="#cdd6f4",
                        arrowcolor="#cdd6f4")
        style.map("TCombobox", fieldbackground=[("readonly", "#313244")])
        style.configure("TSpinbox", fieldbackground="#313244",
                        background="#313244", foreground="#cdd6f4",
                        arrowcolor="#cdd6f4")

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Intervall", style="Bold.TLabel").grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 6)
        )

        for i, txt in enumerate(["Std", "Min", "Sek", "ms"]):
            ttk.Label(main, text=txt).grid(row=1, column=i, padx=2)

        self._spinbox(main, self.interval_h, 0, 23, 2, 0)
        self._spinbox(main, self.interval_m, 0, 59, 2, 1)
        self._spinbox(main, self.interval_s, 0, 59, 2, 2)
        self._spinbox(main, self.interval_ms, 0, 999, 2, 3)

        ttk.Separator(main, orient="horizontal").grid(
            row=3, column=0, columnspan=4, sticky=tk.EW, pady=16
        )

        ttk.Label(main, text="Maustaste", style="Bold.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 6)
        )
        btn_c = ttk.Combobox(main, textvariable=self.click_button,
                             values=["Links", "Rechts", "Mitte"],
                             state="readonly", width=16)
        btn_c.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=(10, 0))

        ttk.Label(main, text="Klick-Typ", style="Bold.TLabel").grid(
            row=5, column=0, sticky=tk.W, pady=(8, 6)
        )
        type_c = ttk.Combobox(main, textvariable=self.click_type,
                              values=["Single", "Double"],
                              state="readonly", width=16)
        type_c.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=(10, 0))

        ttk.Label(main, text="Shortcut", style="Bold.TLabel").grid(
            row=6, column=0, sticky=tk.W, pady=(8, 6)
        )
        hk_c = ttk.Combobox(main, textvariable=self.hotkey,
                            values=HOTKEY_DISPLAY, state="readonly", width=16)
        hk_c.grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=(10, 0))
        hk_c.bind("<<ComboboxSelected>>", lambda e: self._start_listener())

        ttk.Separator(main, orient="horizontal").grid(
            row=7, column=0, columnspan=4, sticky=tk.EW, pady=16
        )

        status_frame = ttk.Frame(main)
        status_frame.grid(row=8, column=0, columnspan=4, sticky=tk.EW, pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Gestoppt",
                                       style="Bold.TLabel")
        self.status_label.pack(side=tk.LEFT)

        self.count_label = ttk.Label(status_frame, text="Klicks: 0")
        self.count_label.pack(side=tk.RIGHT)

        self.toggle_btn = ttk.Button(
            main, text="Starten (F6)", style="Accent.TButton",
            command=self.toggle
        )
        self.toggle_btn.grid(row=9, column=0, columnspan=4, sticky=tk.EW,
                              ipady=6)

        update_frame = ttk.Frame(main)
        update_frame.grid(row=10, column=0, columnspan=4, pady=(6, 0))
        ttk.Button(update_frame, text="Nach Updates suchen",
                   command=self._check_update).pack(side=tk.LEFT)
        self.update_label = ttk.Label(update_frame, text="",
                                       font=("Segoe UI", 8))
        self.update_label.pack(side=tk.LEFT, padx=(8, 0))

    def _spinbox(self, parent, var, lo, hi, row, col):
        sb = ttk.Spinbox(parent, from_=lo, to=hi, textvariable=var,
                         width=5, justify=tk.CENTER)
        sb.grid(row=row, column=col, padx=3)

    def _get_interval_sec(self):
        return (
            self.interval_h.get() * 3600
            + self.interval_m.get() * 60
            + self.interval_s.get()
            + self.interval_ms.get() / 1000
        )

    def _update_status(self):
        if self.clicking:
            self.status_label.config(text="Aktiv - Klickt...",
                                     foreground="#a6e3a1")
            self.toggle_btn.config(text="Stoppen (F6)")
        else:
            self.status_label.config(text="Gestoppt", foreground="#f38ba8")
            self.toggle_btn.config(text="Starten (F6)")

    def toggle(self):
        self.clicking = not self.clicking
        self._update_status()
        if not self.clicking:
            self._save_config()
        else:
            self.click_count = 0
            self.count_label.config(text="Klicks: 0")
            threading.Thread(target=self._click_loop, daemon=True).start()

    # ── Update Check ──

    def _get_update_url(self):
        return get_update_url()

    def _check_update_silent(self):
        time.sleep(3)
        try:
            self._do_check(silent=True)
        except Exception:
            pass

    def _check_update(self):
        self.update_label.config(text="Suche...", foreground="#555")
        self.root.update_idletasks()
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self, silent=False):
        url = self._get_update_url()
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
                self.root.after(0, lambda: self.update_label.config(
                    text=f"v{app_ver} ist aktuell", foreground="#107c10"))
        except Exception:
            if not silent:
                self.root.after(0, lambda: self.update_label.config(
                    text="Keine Verbindung", foreground="#d32f2f"))

    def _is_newer(self, remote, current):
        try:
            r = tuple(int(x) for x in remote.split("."))
            c = tuple(int(x) for x in current.split("."))
            return r > c
        except Exception:
            return False

    def _ask_update(self, version, installer_url):
        app_ver = get_app_version()
        if messagebox.askyesno(
            "Update verfügbar",
            f"Version {version} ist verfügbar.\n"
            f"Aktuelle Version: {app_ver}\n\n"
            "Die App wird geschlossen und der Download gestartet."
        ):
            self._download_and_close(installer_url)

    def _download_and_close(self, url):
        self.clicking = False
        self.running = False
        self.listener.stop()
        self.root.withdraw()

        import tempfile
        try:
            path = os.path.join(tempfile.gettempdir(),
                                "AutoClicker_Update_Setup.exe")
            req = Request(url, headers={"User-Agent": "AutoClicker/1.0"})
            with urlopen(req, timeout=120) as resp:
                with open(path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            os.startfile(path)
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

            self.count_label.config(text=f"Klicks: {self.click_count}")
            time.sleep(interval)

    def _on_close(self):
        self._save_config()
        self.running = False
        self.clicking = False
        self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
