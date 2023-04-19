import os
import logging
import shutil
from pathlib import Path
from datetime import datetime
from config import Config

APP_NAME = "ssWatchdog"
cfg = Config().cfg
log = logging.getLogger(APP_NAME)


def main():
    targetfolder = Path(cfg["output_folders"]["target"])
    wknumber_today = datetime.today().strftime("%yw%U")
    datefolder = targetfolder / f"archived-{wknumber_today}"

    for fp in targetfolder.glob("*.png"):
        if wknumber_today in fp.name:
            continue

        fp_wknumber = fp.stem.split("-")[1]
        datefolder = fp.parent / f"archived-{fp_wknumber}"
        if not datefolder.is_dir():
            datefolder.mkdir(parents=True, exist_ok=True)
            log.warning(f"created {datefolder=}")

        dst = datefolder / fp.name
        shutil.copyfile(src=fp, dst=dst)
        os.remove(fp)
        log.warning(f"moved {fp.name} to //{dst.parent.name}/{dst.name}")



def special_fn_rename():
    targetfolder = Path(cfg["output_folders"]["target"])

    for fp in targetfolder.glob("*.png"):
        if "23w16" in fp.stem:
            continue

        if "ss-2023-04" in fp.stem:
            # ss-2023-04-19-090844H.png
            fp_date = "-".join(fp.stem.split("-")[1:4])
            fp_date = datetime.strptime(fp_date, "%Y-%m-%d").strftime("%yw%U-%m%d")
            fp_time = fp.stem.split("-")[-1]
            newname = f"ss-{fp_date}-{fp_time}.png"

        elif "Screenshot" in fp.stem:
            sp = fp.stem.split(" ")
            fp_date = datetime.strptime(sp[1], "%Y-%m-%d").strftime("%yw%U-%m%d")
            fp_time = datetime.strptime(" ".join(sp[3:5]), "%I.%M.%S %p").strftime("%H%M%SH")
            newname = f"ss-{fp_date}-{fp_time}.png"

        os.rename(fp, fp.parent/newname)
        log.warning(f"renamed {newname=}")





if __name__ == "__main__":
    # special_fn_rename()
    main()