# Screenshot watchdog

Tired of countless screenshots on your desktop (MacOS)?

-   OneDrive\'s \'auto transfer\' screeenshots is just bad!
-   My company blocked dropbox too :(

This simple taskbar python app uses

1.  `rumps` <https://github.com/jaredks/rumps>
2.  `watchdog` <https://github.com/gorakhargosh/watchdog>

to help you automatically watch your filesytem (desktop), performs
action on update.

You can use it to shift (and rename) screenshots to your target folder.

## Quick Start

``` bash
python venv venv
source venv/bin/activate
pip install -r req.txt
python setup.py py2app
```

Open `main.app` from your `dist` folder

## Configurations

Basic configuration in `config.py`.

``` python
# config.py clas Config -> change these settings to your system configuration

def load_config(self) -> dict:

    cfg = {}
    cfg["watched_folders"] = {}
    cfg["watched_folders"]["input"] = "/Users/jli8/Desktop"

    cfg["output_folders"] = {}
    cfg["output_folders"]["target"] = "/Users/jli8/Pictures/screenshots"

    cfg["watcher_settings"] = {}
    cfg["watcher_settings"]["file_suffix"] = "png"
    cfg["watcher_settings"]["regex_compile_string"] = "Screenshot.+.png"
```

Change the actions you need when file changes are detected in
`watcher.py`

``` python
def check_and_move_file(filename: str):
    """
    This function checks the filename, using regex to match
    On match, moves the file to target dir + rename
    """
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
    """
    Overrides the event handler
    You can set your actions here
    """

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
```

## Environments

MacOS only. Tested on Montery 12.6.3 with python 3.11.2.

``` text
pip install rumps
pip install py2app
pip install tomlkit
```

## How to compile using py2app

The first step is to create a setup.py file for your script. setup.py is
the "project file" that tells setuptools everything it needs to know to
build your application. We use the py2applet script to do that:

``` bash
py2applet --make-setup main.py
```

edit setup.py

``` python
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

``` bash
N2390113:197-menubar-watchdog jli8$ python3 -m venv venv
N2390113:197-menubar-watchdog jli8$ source venv/bin/activate
python setup.py py2app
```
