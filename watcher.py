from pathlib import Path
import re
import time
import logging
import shutil
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from config import Config
from utils import cleanup_folder

APP_NAME = "ssWatchdog"
cfg = Config().cfg
log = logging.getLogger(APP_NAME)
regex = re.compile(cfg["watcher_settings"]["regex_compile_string"])


def check_and_move_file(filename: str):
    fp = Path(filename)
    if not fp.is_file():
        return
    match = re.match(regex, fp.name)
    if match is not None:
        sp = fp.stem.split(" ")

        # Version 0
        # fp_date = datetime.strptime(sp[1], "%Y-%m-%d").strftime("%yw%U-%m%d")
        # fp_time = datetime.strptime(" ".join(sp[3:5]), "%I.%M.%S %p").strftime(
        #     "%H%M%SH"
        # )

        # Version 1 - "Screenshot 2023-10-21 at 20.38.15.png"
        # Version 2 - "Screenshot 2024-05-15 at 10.08.40 PM.png"
        fp_date = None
        fp_time = None
        fp_date = datetime.strptime(sp[1], "%Y-%m-%d").strftime("%yw%U-%m%d")
        for fmt in ["%H%M%SH", "%H%M%SH %p"]:
            try:
                fp_time = datetime.strptime(sp[3], "%H.%M.%S").strftime("%H%M%SH")
            except Exception as e:
                log.debug(f"{fmt=}, skipping to try another timefmt ({e=})")

        targetfolder = Path(cfg["output_folders"]["target"])
        new_fp = targetfolder / f"ss-{fp_date}-{fp_time}{fp.suffix}"
        try:
            shutil.copyfile(src=fp, dst=new_fp)
            os.remove(fp)
            log.warning(f"moved {fp.name} to {new_fp.name}")
        except FileNotFoundError:
            pass

        try:
            cleanup_folder(targetfolder, clean_all=False)
        except Exception as e:
            log.error(e)


class CustomEventHandler(LoggingEventHandler):
    # def on_created(self, event):
    #     super().on_created(event)
    #     time.sleep(1)
    #     check_and_move_file(event.src_path)

    def on_modified(self, event):
        super().on_modified(event)
        time.sleep(0.3)
        check_and_move_file(event.src_path)

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    # def on_modified(self, event):
    #     pass


class Watcher:
    def __init__(self):
        self.log = logging.getLogger(APP_NAME)
        self.cfg = Config().cfg
        self.event_handler = CustomEventHandler(logger=self.log)

        self.observer = Observer()
        self.watched_paths = []
        for folder in self.cfg["watched_folders"].values():
            self.add_path(folder)

    def add_path(self, path: str):
        if not isinstance(path, Path):
            path = Path(path)
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
        self.watched_paths.append(path)
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.log.info(f"Added path {path=}")


if __name__ == "__main__":
    wt = Watcher()
    try:
        wt.observer.start()
        while True:
            time.sleep(1)
    finally:
        wt.observer.stop()
        wt.observer.join()
