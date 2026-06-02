import json
import os
import sys
import tempfile
from urllib.request import urlopen, Request
from urllib.error import URLError

USER_AGENT = "AutoClicker-Updater/1.0"
DEFAULT_VERSION = "1.2"
DEFAULT_UPDATE_URL = "https://gist.githubusercontent.com/AnimaDev24/4aef74220ecad2f569e06b6027a2199e/raw/gistfile1.txt"


def _get_config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "autoclicker_config.json")
    return os.path.join(os.path.dirname(__file__), "autoclicker_config.json")


def _read_config(key, default):
    cfg = _get_config_path()
    if os.path.exists(cfg):
        try:
            with open(cfg) as f:
                return json.load(f).get(key, default)
        except Exception:
            pass
    return default


def get_version():
    return _read_config("version", DEFAULT_VERSION)


def get_update_url():
    return _read_config("update_url", DEFAULT_UPDATE_URL)


def check_for_update():
    url = get_update_url()
    ver = get_version()
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        remote = data.get("version", "")
        installer_url = data.get("installer_url", "")

        if _is_newer(remote, ver) and installer_url:
            return {
                "update_available": True,
                "current": ver,
                "latest": remote,
                "installer_url": installer_url,
                "changelog": data.get("changelog", ""),
            }
        return {"update_available": False, "current": ver, "latest": remote}
    except (URLError, json.JSONDecodeError, Exception) as e:
        return {"update_available": False, "error": str(e), "current": ver}


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
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
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
