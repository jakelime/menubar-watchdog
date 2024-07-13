# Menubar Watchdog - Screenshot app

App to automatically clean up screenshots captured on MacOS.

## Quickstart

1. Standard python `venv` setup

   ```shell
   python venv venv
   source ./venv/bin/activate
   pip install -r requirements.txt
   ## or pip install -r requirements-frozen.txt

   ```

1. Check the `py2app` settings in `setup.py`

   ```python
   from setuptools import setup

    APP = ["ssdog.py"]
    DATA_FILES = [("", ["images"])]
    ...
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={"py2app": OPTIONS},
        setup_requires=["py2app"],
    )

   ```

1. Compile the application

   ```shell
   python setup.py py2app
   ```

1. Run the application.

   - The app will appear in the menubar
   - Any screenshots made will be automatically renamed and moved
     to `target_dir`
   - `open config folder` to open the folder that houses the configurations
   - `open folder` opens the location where screenshots will be moved to
   - Move the `application.app` into the `/Applications` directory
   - You can choose to add this app into login items during startup
