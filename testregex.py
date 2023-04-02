import re
from config import Config
import logging
from pathlib import Path
from datetime import datetime

APP_NAME = "test"
c = Config(APP_NAME)
cfg = c.cfg
log = logging.getLogger(APP_NAME)

regex = re.compile(cfg["watcher_settings"]["regex_compile_string"])
files = [
    "Screenshot 2023-03-06 at 1.35.38 PM.png",
    "Screenshot 2023-03-06 at 1.48.33 PM.jpg",
    "abc.png",
]
files = [Path(x) for x in files]
matches = [fp for fp in files if re.match(regex, fp.name)]
print(f"{regex=}")
print(matches)

for fp in matches:
    sp = fp.stem.split(" ")
    fp_date = sp[1]
    fp_time = datetime.strptime(" ".join(sp[3:5]), "%I.%M.%S %p").strftime("%H%M%SH")
    new_filename = f"ss-{fp_date}-{fp_time}"
    print(f"{new_filename=}")