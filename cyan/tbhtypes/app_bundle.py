
import os
import shutil
from glob import glob
from cyan.telegram_utils import send_telegram_message
from uuid import uuid4
from typing import Optional, Literal
import logging
import concurrent.futures

from .executable import Executable
from .main_executable import MainExecutable
from .plist import Plist

class AppBundle:
    def __init__(self, path: str):
        self.path = path
        self.plist = Plist(f"{path}/Info.plist", path)
        self.executable = MainExecutable(
            f"{path}/{self.plist['CFBundleExecutable']}",
            path
        )
        self.cached_executables: Optional[list[str]] = None

    def remove(self, *names: str) -> bool:
        existed = False
        removed_names = []
        for name in names:
            path = name if self.path in name else f"{self.path}/{name}"
            if not os.path.exists(path):
                continue
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            existed = True
            removed_names.append(name)
            self.cached_executables = None  # Invalidate cache if bundle changes
        if removed_names:
            send_telegram_message(f"�️ Removed: {', '.join(removed_names)} from bundle.")
        return existed

    def get_executables(self) -> list[str]:
        # Use os.walk for better performance on large bundles
        exts = ('.dylib', '.appex', '.framework')
        result = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith(exts):
                    result.append(os.path.join(root, f))
        return result

    def mass_operate(self, op: str, func: Literal["fakesign", "thin"]) -> None:
        if self.cached_executables is None:
            self.cached_executables = self.get_executables()

        logging.basicConfig(level=logging.INFO)

        def operate(ts):
            if ts.endswith(".dylib"):
                return getattr(Executable(ts), func)()
            else:
                pl = Plist(f"{ts}/Info.plist")
                return getattr(Executable(f"{ts}/{pl['CFBundleExecutable']}"), func)()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(operate, self.cached_executables))
        count = 1 if getattr(self.executable, func)() else 0
        count += sum(1 for r in results if r)
        logging.info(f"[*] {op} {count} item(s)")

    def remove_plugins(self, plugins: list[str]) -> None:
        logging.basicConfig(level=logging.INFO)
        removed = []
        for plugin in plugins:
            if self.remove(plugin):
                removed.append(plugin)
        if removed:
            logging.info(f"[*] removed plugins: {', '.join(removed)}")
            send_telegram_message(f"🔌 Plugins removed: {', '.join(removed)}")
        else:
            logging.warning("[?] no specified plugins were found or removed")
            send_telegram_message("⚠️ No specified plugins were found or removed.")

    def has_watchkit(self) -> bool:
        # Check for WatchKit or related items in the bundle
        watchkit_paths = [
            os.path.join(self.path, "Watch"),
            os.path.join(self.path, "WatchKit"),
            os.path.join(self.path, "com.apple.WatchPlaceholder")
        ]
        return any(os.path.exists(p) for p in watchkit_paths)

    def remove_watch_apps(self, skip: bool = False) -> None:
        """
        Remove WatchKit and related items unless skip is True.
        """
        if skip:
            print("[i] Skipping removal of WatchKit and related items.")
            return
        if self.remove("Watch", "WatchKit", "com.apple.WatchPlaceholder"):
            print("[*] removed watch app")
        else:
            print("[?] watch app not present")

    def fakesign_all(self) -> None:
        self.mass_operate("fakesigned", "fakesign")
        send_telegram_message("🔏 All executables fakesigned! ✅")

    def thin_all(self) -> None:
        self.mass_operate("thinned", "thin")
        send_telegram_message("📦 All executables thinned! ✅")

    def remove_all_extensions(self) -> None:
        if self.remove("Extensions", "PlugIns"):
            print("[*] removed app extensions")
        else:
            print("[?] no app extensions")

    def remove_encrypted_extensions(self) -> None:
        removed: list[str] = []
        for plugin in glob(f"{self.path}/*/*.appex"):
            bundle = AppBundle(plugin)
            if bundle.executable.is_encrypted():
                self.remove(plugin)
                removed.append(bundle.executable.bn)
        if len(removed) == 0:
            print("[?] no encrypted plugins")
        else:
            print("[*] removed encrypted plugins:", ", ".join(removed))

    def change_icon(self, path: str, tmpdir: str) -> None:
        try:
            from PIL import Image  # type: ignore
        except Exception:
            return print("[?] pillow is not installed, -k is not available")

        tmpath = f"{tmpdir}/icon.png"
        if not path.endswith(".png"):
            with Image.open(path) as img:
                img.save(tmpath, "PNG")
        else:
            shutil.copyfile(path, tmpath)

        uid = f"cyan_{uuid4().hex[:7]}a"  # can't have it end with a num
        i60 = f"{uid}60x60"
        i76 = f"{uid}76x76"

        with Image.open(tmpath) as img:
            img.resize((120, 120)).save(f"{self.path}/{i60}@2x.png", "PNG")
            img.resize((152, 152)).save(f"{self.path}/{i76}@2x~ipad.png", "PNG")

        if "CFBundleIcons" not in self.plist:
            self.plist["CFBundleIcons"] = {}
        if "CFBundleIcons~ipad" not in self.plist:
            self.plist["CFBundleIcons~ipad"] = {}

        self.plist["CFBundleIcons"] = self.plist["CFBundleIcons"] | {
            "CFBundlePrimaryIcon": {
                "CFBundleIconFiles": [i60],
                "CFBundleIconName": uid
            }
        }
        self.plist["CFBundleIcons~ipad"] = self.plist["CFBundleIcons~ipad"] | {
            "CFBundlePrimaryIcon": {
                "CFBundleIconFiles": [i60, i76],
                "CFBundleIconName": uid
            }
        }

        self.plist.save()
        print("[*] updated app icon")