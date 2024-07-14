from setuptools import setup

APP = ["src/ssdog.py"]
DATA_FILES = [("", ["src/icons"])]
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "src/icons/icon.icns",
    "plist": {
        "LSUIElement": True,
    },
    "packages": ["rumps", "tomlkit"],
}

setup(
    name="ss-watchdog",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
