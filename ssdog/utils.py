import datetime
import logging
import os
import platform
import shutil
import subprocess
import timeit
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "ssdog"


class LoggerManager:
    def __init__(self, app_name: str = ""):
        if not app_name:
            app_name = __name__
        self.app_name = app_name
        self.logger_name = app_name
        self.logger = logging.getLogger(self.app_name)
        if not self.logger.handlers:
            # Set ups the logger if it is not already initialised
            self.init_logger(self.logger)

    def init_logger(self, logger):
        logger_filepath = self.set_log_filepath()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s-%(levelname)s: %(message)s")
        fhandler = RotatingFileHandler(
            filename=logger_filepath, maxBytes=2_097_152, backupCount=10
        )
        fhandler.setFormatter(formatter)
        fhandler.setLevel(logging.INFO)
        chandler = logging.StreamHandler()
        chandler.setLevel(logging.INFO)
        chandler.setFormatter(formatter)
        logger.addHandler(fhandler)
        logger.addHandler(chandler)
        logger.info(f"logger initialised - {logger_filepath}")
        return logger

    def get_logger(self):
        return self.logger

    def getLogger(self):
        return self.logger

    def setLevel(self, level: str = "info"):
        match level.lower():
            case "info":
                for h in self.logger.handlers:
                    h.setLevel("INFO")
            case "debug":
                for h in self.logger.handlers:
                    h.setLevel("DEBUG")
            case "warning" | "warn":
                for h in self.logger.handlers:
                    h.setLevel("WARNING")
            case "error":
                for h in self.logger.handlers:
                    h.setLevel("ERROR")
            case _:
                raise RuntimeError(f"unknown log {level=}")
        self.logger.critical(f"logger level changed to {level}")

    def change_level(self, level: str = "info"):
        self.setLevel(level)

    def set_level(self, level: str = "info"):
        self.setLevel(level)

    def set_log_filepath(self, dirpath: str = "~/Library/Logs") -> Path:
        logs_dirpath = Path(dirpath).expanduser()
        if not os.access(logs_dirpath, os.W_OK):
            raise OSError(f"logs directory is not writeable - {dirpath=}")
        logger_filepath = logs_dirpath / self.app_name / "main_application.log"
        if not logger_filepath.parent.is_dir():
            logger_filepath.parent.mkdir()
        self.logger_filepath = logger_filepath
        return logger_filepath


lg = LoggerManager(APP_NAME).get_logger()


def check_write_permission(directory_path):
    if not os.access(directory_path, os.W_OK):
        raise OSError(f"directory is not writeable - {directory_path=}")


def get_datetime_str(
    dtformat: str = "%Y%m%d_%H%M%S", append_microseconds: bool = False
) -> str:
    now = datetime.datetime.now()
    timestr = now.strftime(dtformat)
    if append_microseconds:
        ms = now.strftime("%f")[:2]
        timestr = f"{timestr}{ms}"
    return timestr


def function_timer(func):
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        lg.info(f"fn('{func.__name__}') took {elapsed_time:.4f} seconds.")
        return result

    return wrapper


def cleanup_folder(folderpath: Path | None = None, clean_all=False):
    if folderpath is None:
        targetfolder = Path(cfg["output_folders"]["target"])
    else:
        targetfolder = folderpath
    wknumber_today = datetime.datetime.today().strftime("%yw%U")
    datefolder = targetfolder / f"archived-{wknumber_today}"

    for fp in targetfolder.glob("*.png"):
        if wknumber_today in fp.name and not clean_all:
            continue

        fp_wknumber = fp.stem.split("-")[1]
        datefolder = fp.parent / f"archived-{fp_wknumber}"
        if not datefolder.is_dir():
            datefolder.mkdir(parents=True, exist_ok=True)
            lg.warning(f"created {datefolder=}")

        dst = datefolder / fp.name
        shutil.copyfile(src=fp, dst=dst)
        os.remove(fp)
        lg.warning(f"moved {fp.name} to //{dst.parent.name}/{dst.name}")


def open_folder(path: Path | str):
    if not isinstance(path, Path):
        path = Path(path)
    if path.is_dir():
        if platform.system() == "Windows":
            subprocess.Popen(["explorer.exe", path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    else:
        raise Exception(f"invalid {path=}")
    lg.info(f"Open folder success //{path.name}")


def main():
    lg.info("success!")


if __name__ == "__main__":
    main()
