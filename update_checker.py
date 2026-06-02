import json
import os
import sys
import tempfile
import webbrowser
from urllib.request import urlopen, Request
from urllib.error import URLError

VERSION = "1.2"
UPDATE_URL = "https://gist.githubusercontent.com/AnimaDev24/4aef74220ecad2f569e06b6027a2199e/raw/gistfile1.txt"
USER_AGENT = "AutoClicker-Updater/1.0"


def _get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def _get_config_path():
    return os.path.join(_get_app_dir(), "autoclicker_config.json")


def get_update_url():
    url = UPDATE_URL
    cfg = _get_config_path()
    if os.path.exists(cfg):
        try:
            with open(cfg) as f:
                d = json.load(f)
            url = d.get("update_url", url)
        except Exception:
            pass
    return url


def check_for_update():
    url = get_update_url()
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        remote = data.get("version", "")
        installer_url = data.get("installer_url", "")

        if _is_newer(remote, VERSION) and installer_url:
            return {
                "update_available": True,
                "current": VERSION,
                "latest": remote,
                "installer_url": installer_url,
                "changelog": data.get("changelog", ""),
            }
        return {"update_available": False, "current": VERSION, "latest": remote}
    except (URLError, json.JSONDecodeError, Exception) as e:
        return {"update_available": False, "error": str(e), "current": VERSION}


def _is_newer(remote, current):
    try:
        r = tuple(int(x) for x in remote.split("."))
        c = tuple(int(x) for x in current.split("."))
        return r > c
    except Exception:
        return False


def download_and_install(installer_url):
    try:
        tmp = tempfile.gettempdir()
        path = os.path.join(tmp, "AutoClicker_Update_Setup.exe")

        req = Request(installer_url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

        os.startfile(path)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    result = check_for_update()
    if result.get("update_available"):
        print(f"Update verfuegbar: v{result['current']} -> v{result['latest']}")
        download_and_install(result["installer_url"])
    elif "error" in result:
        print(f"Fehler: {result['error']}")
    else:
        print(f"Kein Update (v{result['current']})")
