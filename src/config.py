from pathlib import Path

import tomlkit as tmk
import utils
from tomlkit import toml_file
from tomlkit.toml_document import TOMLDocument

APP_NAME = "ssdog"


class ConfigManager:
    def __init__(self, dirpath: str = "~/Library/Preferences") -> None:
        self.app_name = APP_NAME
        self.dirpath = dirpath
        self.config_filepath = self.get_config_filepath()
        if not self.config_filepath.is_file():
            self.write_toml_file(self.config_filepath)
        self.config = self.parse_config(self.config_filepath)
        self.config = self.post_parse_config(self.config)

    def get_config_dirpath(self) -> Path:
        dirpath = Path(self.dirpath).expanduser()
        utils.check_write_permission(dirpath)
        dirpath = Path(self.dirpath).expanduser() / self.app_name
        if not dirpath.is_dir():
            dirpath.mkdir()
        return dirpath

    def get_config_filepath(self, filename: str = "config.toml") -> Path:
        config_filepath = self.get_config_dirpath() / filename
        return config_filepath

    @staticmethod
    def write_toml_file(outpath: Path) -> None:
        toml_doc = ConfigToml(outpath)
        toml_doc.write_to_file()

    @staticmethod
    def parse_config(fpath) -> dict:
        tf = toml_file.TOMLFile(fpath)
        doc = tf.read()
        config = doc.unwrap()
        return config

    @staticmethod
    def post_parse_config(v: dict) -> dict:
        # os_version = int(platform.platform().split("-")[1].split(".")[0])
        # if os_version >= 14:
        #     # macos Sonoma 14.5 has the same menubar regardless dark or light mode
        #     v["app_icon_color"] = "black"

        if v["app_icon_color"] == "auto":
            if utils.is_macos_dark_mode():
                v["app_icon_color"] = "white"
            else:
                v["app_icon_color"] = "black"
        return v

    def reset(self) -> None:
        """
        Resets the configuration file by writing a new TOML file and parsing it.

        This function writes a new TOML file to the configured filepath using the `write_toml_file` method.
        It then parses the newly written TOML file using the `parse_config` method and updates the `config` attribute
        with the parsed configuration.

        Parameters:
            None

        Returns:
            None
        """
        self.write_toml_file(self.config_filepath)
        self.config = self.parse_config(self.config_filepath)


class ConfigToml:
    def __init__(self, config_filepath: Path) -> None:
        self.config_filepath = config_filepath
        self.doc = self.init_doc()

    def write_to_file(self) -> Path:
        tf = toml_file.TOMLFile(self.config_filepath)
        tf.write(self.doc)
        print(f"wrote config to {self.config_filepath}")
        return self.config_filepath

    def init_doc(self) -> TOMLDocument:
        doc = tmk.document()
        doc.add(tmk.comment("Configuration file for ssdog - Screenshot Watchdog"))
        doc.add(tmk.nl())
        doc["debug"] = False
        doc["watch_dirs"] = [r"~/Downloads"]
        doc["target_dir"] = r"~/Pictures/screenshots"
        doc["app_icon_color"] = "auto"
        doc["app_icon_color"].comment("possible choices are [white, black, auto]")  # type: ignore

        wds = tmk.table()
        wds["file_suffix"] = "png"
        wds["regex_compile_string"] = r"Screenshot.+.png"
        doc["watchdog_settings"] = wds
        return doc


def main():
    # cfg = ConfigManager().config
    confm = ConfigManager()
    confm.reset()
    cfg = confm.config
    print(cfg)


if __name__ == "__main__":
    main()
