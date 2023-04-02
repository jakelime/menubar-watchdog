# config.py
# Responsible for initializing configuration needed
# for the application. There are 2 configurations here:
# factory configuration and user configuration.

# global libraries
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "wtch"
# local libraries


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
        name="noname",
        default_loglevel="INFO",
    ) -> None:

        self.name = name
        self.user_docs = Path(os.path.expanduser("~/Documents/"))
        self.user_wd = self.user_docs / f"_tools-{self.name}"

        self.log = self.setup_logger(APP_NAME)
        self.log.info("logger initialized")

        self.cfg = self.load_config()
        self.cfg = self.init_user_paths(self.cfg)

    def setup_logger(self, app_name, default_loglevel="INFO"):
        """
        Creates a logger object
        Logs to both console stdout and also a log file
        """

        logger = logging.getLogger(app_name)

        if logger.hasHandlers():
            return logger

        self.logfile = self.user_wd / f"{self.name}.log"
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
        cfg["watched_folders"]["input"] = "/Users/jli8/Desktop"

        cfg["output_folders"] = {}
        cfg["output_folders"]["target"] = "/Users/jli8/Pictures/screenshots"

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
    c = Config(APP_NAME)
    cfg = c.cfg
    pretty_print(cfg)


if __name__ == "__main__":
    main()
