# Menubar Watchdog - Screenshot app

App to automatically clean up screenshots captured on MacOS.

## Quickstart

1. Setup environment, compile a `.app` app package using `py2app`

   ```shell
   python venv venv
   source ./venv/bin/activate
   pip install -r requirements.txt # to use latest libaries
   ## or pip install -r requirements-frozen.txt # debug
   python setup.py py2app
   ```

1. Run the application.

   - The app will appear in the menubar

## Usage guide

### Problem statement

- MacOS has a default screenshot capture shortcut: `cmd + shift + 4`

  - The problem is that the images will be saved by default to Desktop
  - This makes the desktop looks cluttered and messy over time, and it
    will be difficult to find what you need.

### Solution

- Any screenshots made will be automatically renamed and moved
   to `target_dir`
- `OpenConfigFolder` allows user to change the configurations (`config.toml`)
- `OpenFolder` opens the location where screenshots will be moved to

### Tips

- Move the `ss-watchdog.app` into your `/Applications` directory
- You can now  add this app into `login items` during startup

## Dependencies

1. [rumps](https://github.com/jaredks/rumps)
1. [watchdog](https://github.com/gorakhargosh/watchdog)
1. [py2app](https://github.com/ronaldoussoren/py2app)

## Guide to build MacOS app

Create `setup.py` for `py2app`.

Example:

```python
from setuptools import setup

APP = ["src/ssdog.py"]
DATA_FILES = [("", ["src/icons"])]
OPTIONS = {
   "argv_emulation": True,
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
```
