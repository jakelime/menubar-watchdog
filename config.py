# config.py
# Responsible for initializing configuration needed
# for the application.

# global libraries
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "ssWatchdog"
# local libraries

###############################
#### User configurations ####
###############################
INPUT_FOLDER = "~/Desktop"
TARGET_FOLDER = "~/Pictures/screenshots"
################################


class Config:
    """
    This class is responsible intialising a logger object (to log messages)
    and initialising a tomlDocument object to be used as user configuration

    self.log = logging.Logger object
    self.cfg = tomlDocument object (similar to dict)
    """

    cfg: dict
    bundles: Path
    user_bundles: Path
    user_docs: Path
    user_wd: Path
    log: logging.Logger = None

    def __init__(
        self,
    ) -> None:
        self.user_docs = Path(os.path.expanduser("~/Documents/"))
        self.user_wd = self.user_docs / f"_tools-{APP_NAME}"

        self.log = self.setup_logger()
        self.log.info("logger initialized")

        self.cfg = self.load_config()
        self.cfg = self.init_user_paths(self.cfg)

    def setup_logger(self, default_loglevel="WARNING"):
        """
        Creates a logger object
        Logs to both console stdout and also a log file
        """

        logger = logging.getLogger(APP_NAME)

        if logger.hasHandlers():
            return logger

        self.logfile = self.user_wd / f"{APP_NAME}.log"
        if not self.logfile.is_file():
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("w", encoding="utf-8") as f:
                f.write("")

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = RotatingFileHandler(
            self.logfile, maxBytes=5_242_880, backupCount=10
        )
        c_handler.setLevel(default_loglevel)
        f_handler.setLevel(default_loglevel)

        # Create formatters and add it to handlers
        c_format = logging.Formatter("%(levelname)-8s: %(message)s")
        f_format = logging.Formatter(
            "[%(asctime)s]%(levelname)-8s: %(message)s", "%y-%j %H:%M:%S"
        )
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        logger.setLevel(default_loglevel)
        return logger

    def load_config(self) -> dict:

        cfg = {}
        cfg["watched_folders"] = {}

        input_folder = (
            os.path.expanduser(INPUT_FOLDER) if "~" in INPUT_FOLDER else INPUT_FOLDER
        )
        cfg["watched_folders"]["input"] = input_folder

        target_folder = (
            os.path.expanduser(TARGET_FOLDER) if "~" in TARGET_FOLDER else TARGET_FOLDER
        )
        cfg["output_folders"] = {}
        cfg["output_folders"]["target"] = target_folder

        cfg["watcher_settings"] = {}
        cfg["watcher_settings"]["file_suffix"] = "png"
        cfg["watcher_settings"]["regex_compile_string"] = "Screenshot.+.png"

        self.cfg = cfg

        return self.cfg

    def init_user_paths(self, cfg_input: dict):
        cfg = cfg_input.copy()
        cfg["folders"] = {}
        for folder_type in ["watched_folders", "output_folders"]:
            for folderkey, foldername in cfg[folder_type].items():
                if os.sep in foldername:
                    folderpath = Path(foldername)
                    assert folderpath.is_dir(), f"{folderpath=} must be a directory"
                else:
                    folderpath = self.user_wd / foldername
                if not folderpath.is_dir():
                    folderpath.mkdir(parents=True, exist_ok=True)
                cfg["folders"][folderkey] = str(folderpath.resolve())
        cfg["folders"]["user_working_folder"] = str(self.user_wd.resolve())
        return cfg


def pretty_print(d, n: int = 0):
    log = logging.getLogger(APP_NAME)
    spaces = " " * n * 2
    for k, v in d.items():
        if isinstance(v, dict):
            log.info(f"{spaces}{k}:")
            pretty_print(v, n=n + 1)
        else:
            try:
                log.info(f"{spaces}{k}: {v}")
            except AttributeError:
                # Happens when parsing toml (below is to handle tomlkit class)
                log.info(f"{spaces}{k=}, {v=}")


def main():
    cfg = Config().cfg
    pretty_print(cfg)


if __name__ == "__main__":
    main()
