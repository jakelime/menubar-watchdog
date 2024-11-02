import datetime
import os
import re
import shutil
import time
from pathlib import Path

from config import ConfigManager
from utils import LoggerManager, cleanup_folder
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

APP_NAME = "ssdog"

cfg = ConfigManager().config
lg = LoggerManager(APP_NAME, debug_mode=cfg["debug"]).get_logger()


def check_and_move_file(filename: str):
    regex_str = re.compile(cfg["watchdog_settings"]["regex_compile_string"])
    fp = Path(filename)
    if not fp.is_file():
        return
    match = re.match(regex_str, fp.name)
    if match is not None:
        sp = fp.stem.split(" ")
        fp_date = None
        fp_time = None
        fp_date = datetime.datetime.strptime(sp[1], "%Y-%m-%d").strftime("%yw%U-%m%d")
        for fmt in ["%H%M%SH", "%H%M%SH %p"]:
            try:
                fp_time = datetime.datetime.strptime(sp[3], "%H.%M.%S").strftime(
                    "%H%M%SH"
                )
            except Exception as e:
                lg.debug(f"{fmt=}, skipping to try another timefmt ({e=})")

        targetfolder = Path(cfg["target_dir"]).expanduser()
        new_fp = targetfolder / f"ss-{fp_date}-{fp_time}{fp.suffix}"
        i = 1
        while new_fp.is_file():
            new_fp = targetfolder / f"ss-{fp_date}-{fp_time}_{i}{fp.suffix}"
            i += 1
            if i > 99:
                raise RuntimeError(f"too many files of similar name - {new_fp=}")
        try:
            shutil.copyfile(src=fp, dst=new_fp)
            os.remove(fp)
            lg.warning(f"moved {fp.name} to {new_fp.name}")
        except FileNotFoundError:
            pass

        try:
            cleanup_folder(lg, targetfolder, clean_all=False)
        except Exception as e:
            lg.error(e)


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


class Watcher:
    def __init__(self):
        self.event_handler = CustomEventHandler(logger=lg)
        self.observer = Observer()
        self.watched_paths = []
        for folder in cfg["watch_dirs"]:
            self.add_path(folder)

    def add_path(self, path: Path | str):
        if not isinstance(path, Path):
            path = Path(path)
        path = path.expanduser()
        if not path.is_dir():
            path.mkdir()
        self.watched_paths.append(path)
        self.observer.schedule(self.event_handler, path, recursive=True)
        lg.info(f"Added path {path=}")


if __name__ == "__main__":
    wt = Watcher()
    try:
        wt.observer.start()
        while True:
            time.sleep(1)
    finally:
        wt.observer.stop()
        wt.observer.join()
