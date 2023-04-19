import logging
from pathlib import Path
import rumps
from threading import Thread, Event
from config import Config
from watcher import Watcher
import time
from utils import cleanup_folder

APP_NAME = "ssWatchdog"
VAR_RUN = True

cfg = Config().cfg
log = logging.getLogger(APP_NAME)

class StatusBarApp(rumps.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = None
        self.event = Event()
        self.toggle_watchdog()

    def debug_toggle_switch(self, sender):
        sender.state = not sender.state
        if sender.state == 1:
            bool_value = True
            rumps.debug_mode(True)
            log.info(f"switched debug={bool_value}")
        else:
            bool_value = False
            rumps.debug_mode(bool_value)
            log.info(f"switched debug={bool_value}")

    def cleanup_folder(self, *args, **kwargs):
        targetfolder = Path(cfg["output_folders"]["target"])
        cleanup_folder(targetfolder, clean_all=True)


    def toggle_watchdog(self, sender=None):
        if sender is None:
            self.start_watchdog()
            log.critical(f"Started {APP_NAME}")
            return

        sender.state = not sender.state
        if sender.state == 1:
            self.stop_watchdog()
            log.critical(f"Stopped {APP_NAME}")
        else:
            self.start_watchdog()
            log.critical(f"Started {APP_NAME}")

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
            log.info("starting task for watchdog ...")
            self.thread = Thread(target=self.watchdog, args=(self.event,))
            self.thread.start()
        else:
            log.error("watchdog is already running!")

    def stop_watchdog(self, *args, **kwargs):
        if self.thread is not None:
            log.info("stopping watchdog ...")
            self.event.set()
            self.thread.join()
            self.event.clear()
            self.thread = None
            log.info("stopped watchdog")
        else:
            log.error("watchdog is not running")


if __name__ == "__main__":
    # 📷
    app = StatusBarApp(APP_NAME, icon="images/icon-white.icns")
    app.menu = [
        rumps.MenuItem("Watchdog App"),  # can specify an icon to be placed near text
        rumps.MenuItem("Debug", callback=app.debug_toggle_switch),
        None,  # None functions as a separator in your menu
        rumps.MenuItem("Pause", callback=app.toggle_watchdog),
        rumps.MenuItem("Cleanup", callback=app.cleanup_folder),
        None,
    ]
    app.run()
