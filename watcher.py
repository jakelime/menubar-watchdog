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

APP_NAME = "watchdog"
c = Config(APP_NAME)
cfg = c.cfg
regex = re.compile(cfg["watcher_settings"]["regex_compile_string"])
log = logging.getLogger(APP_NAME)


def check_and_move_file(filename: str):
    fp = Path(filename)
    if not fp.is_file():
        return
    match = re.match(regex, fp.name)
    if match is not None:
        sp = fp.stem.split(" ")
        fp_date = sp[1]
        fp_time = datetime.strptime(" ".join(sp[3:5]), "%I.%M.%S %p").strftime(
            "%H%M%SH"
        )
        new_fp = (
            Path(cfg["output_folders"]["target"]) / f"ss-{fp_date}-{fp_time}{fp.suffix}"
        )
        shutil.copyfile(src=fp, dst=new_fp)
        os.remove(fp)
        log.info(f"moved {fp.name} to {new_fp.name}")


class CustomEventHandler(LoggingEventHandler):
    # def on_created(self, event):
    #     super().on_created(event)
    #     time.sleep(1)
    #     check_and_move_file(event.src_path)

    def on_modified(self, event):
        super().on_modified(event)
        time.sleep(1)
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
        self.log.info("watcher logger initialized")
        self.cfg = c.cfg
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
