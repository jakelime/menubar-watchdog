import time
from pathlib import Path
from threading import Event, Thread

import rumps
from config import ConfigManager
from utils import LoggerManager, cleanup_folder, open_folder
from watcher import Watcher

APP_NAME = "ssdog"
VAR_RUN = True

cfg = ConfigManager().config
lg = LoggerManager(APP_NAME, debug_mode=cfg["debug"]).get_logger()


class StatusBarApp(rumps.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_dir = Path(cfg["target_dir"]).expanduser()
        self.thread = None
        self.event = Event()
        self.toggle_watchdog()

    def debug_toggle_switch(self, sender):
        sender.state = not sender.state
        if sender.state == 1:
            bool_value = True
            for h in lg.handlers:
                h.setLevel("DEBUG")
        else:
            bool_value = False
            for h in lg.handlers:
                h.setLevel("WARNING")
        rumps.debug_mode(bool_value)
        lg.critical(f"switched debug={bool_value}")

    def cleanup_folder(self, *args, **kwargs):
        cleanup_folder(lg, self.target_dir, clean_all=True)

    def open_folder(self, *args, **kwargs):
        open_folder(lg, self.target_dir)

    def open_config_folder(self, *args, **kwargs):
        targetfolder = ConfigManager().get_config_dirpath()
        open_folder(lg, targetfolder)

    def toggle_watchdog(self, sender=None):
        if sender is None:
            self.start_watchdog()
            lg.debug(f"Started {APP_NAME}")
            return

        sender.state = not sender.state
        if sender.state == 1:
            self.stop_watchdog()
            lg.critical(f"Stopped {APP_NAME}")
        else:
            self.start_watchdog()
            lg.debug(f"Started {APP_NAME}")

    def watchdog(self, *args, **kwargs):
        wt = Watcher()
        try:
            wt.observer.start()
            while True:
                time.sleep(1)
                if self.event.is_set():
                    break
        finally:
            wt.observer.stop()
            wt.observer.join()

    def start_watchdog(self, *args, **kwargs):
        if self.thread is None:
            lg.info("starting task for watchdog ...")
            self.thread = Thread(target=self.watchdog, args=(self.event,))
            self.thread.start()
        else:
            lg.error("watchdog is already running!")

    def stop_watchdog(self, *args, **kwargs):
        if self.thread is not None:
            lg.info("stopping watchdog ...")
            self.event.set()
            self.thread.join()
            self.event.clear()
            self.thread = None
            lg.info("stopped watchdog")
        else:
            lg.error("watchdog is not running")


def get_menubar_icon() -> str:
    match cfg["app_icon_color"].lower():
        case "black":
            menu_icon_img = "icons/icon-black.icns"
        case "white":
            menu_icon_img = "icons/icon-white.icns"
        case _:
            menu_icon_img = "icons/icon-white.icns"
    return menu_icon_img


if __name__ == "__main__":
    lg.debug(f"initializing {APP_NAME}...")
    app = StatusBarApp(APP_NAME, icon=get_menubar_icon())
    lg.debug("setting menu items...")
    app.menu = [
        rumps.MenuItem("Watchdog App"),  # can specify an icon to be placed near text
        rumps.MenuItem("OpenConfigFolder", callback=app.open_config_folder),
        # rumps.MenuItem("Debug", callback=app.debug_toggle_switch),
        None,  # None functions as a separator in your menu
        rumps.MenuItem("Pause", callback=app.toggle_watchdog),
        rumps.MenuItem("Cleanup", callback=app.cleanup_folder),
        rumps.MenuItem("OpenFolder", callback=app.open_folder),
        None,
    ]
    lg.debug("running app...")
    app.run()
