


https://pythonhosted.org/watchdog/api.html#module-watchdog.observers.api
https://github.com/gorakhargosh/watchdog
https://github.com/jaredks/rumps



1. The first step is to create a setup.py file for your script. setup.py is the “project file” that tells setuptools everything it needs to know to build your application. We’ll use the py2applet script to do that:


   .. codeblock:: bash

        py2applet --make-setup main.py

2. edit setup.py

   .. codeblock:: python

        OPTIONS = {
            'argv_emulation': True,
            'plist': {
                'LSUIElement': True,
            },
            'packages': ['rumps'],
            }


.. codeblock:: bash

    N2390113:197-menubar-watchdog jli8$ python3 -m venv venv
    N2390113:197-menubar-watchdog jli8$ source venv/bin/activate
    python setup.py py2app


.. codeblock:: text

    pip install rumps
    pip install py2app
    pip install tomlkit
