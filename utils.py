import logging
from pathlib import Path
import shutil
import time
import subprocess
import platform
import os

from datetime import datetime
from config import Config

APP_NAME = "ssWatchdog"
cfg = Config().cfg
log = logging.getLogger(APP_NAME)


class ConfigError(Exception):
    """Error due to invalid parameters in user config file"""


class QueueHandler(logging.Handler):
    """
    Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget

    Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread
    """

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


def copyfile(src: Path, dst: Path, exist_ok=True, overwrite=False):
    """
    Wrapper to copy a file src to dst
    Exceptions will be caught and logged, without breaking the code
    """
    log = logging.getLogger(APP_NAME)
    if dst.is_file():
        if (not exist_ok) and (overwrite is False):
            raise FileExistsError(f"{dst.name=}")

    try:
        shutil.copyfile(src, dst)
    except OSError as e:
        errmsg = f"copying file error, no permissions to src=//{dst.parent.name}"
        log.error(errmsg)
        log.error(e)
    except Exception as e:
        errmsg = f"copying file error; {e}"
        log.error(errmsg)


def get_time(datetimestrformat: str = "%Y%m%d_%H%M%S"):
    """
    Returns the datetime string at the time of function call
    :param datetimestrformat: datetime string format, defaults to "%Y%m%d_%H%M%S"
    :type datetimestrformat: str, optional
    :return: datetime in string format
    :rtype: str
    """
    return time.strftime(datetimestrformat, time.localtime(time.time()))


def classtimer(func):
    def wrapper(ref_self, *args, **kwargs):
        log = logging.getLogger(APP_NAME)
        t0 = time.perf_counter()
        a = func(ref_self, *args, **kwargs)
        time_taken = time.perf_counter() - t0
        if time_taken < 100:
            time_taken = f"{time_taken:.4f}s"
        else:
            time_taken = f"{(time_taken/60):.2f}mins"
        log.info(f"[{func.__name__}] elapsed_time = {time_taken}")
        return a

    return wrapper


def timer(func):
    def wrapper(*args, **kwargs):
        log = logging.getLogger(APP_NAME)
        t0 = time.perf_counter()
        a = func(*args, **kwargs)
        log.info(f"[{func.__name__}] elapsed_time = {(time.perf_counter()-t0):.4f}s")
        return a

    return wrapper


def get_latest_git_tag(repo_path: Path = None, err_code: str = "versionError"):
    """function to use GitPython to get a list of tags

    :param repo_path: path where .git resides in
    :type repo_path: pathlib.Path
    :return: latest git tag
    :rtype: str
    """
    try:
        sp = subprocess.run(
            ["git", "describe", "--tag"],
            check=True,
            timeout=5,
            capture_output=True,
            encoding="utf-8",
        )
        results = sp.stdout.strip()

        if not results:
            results = err_code

    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            results = "git_fatal_err"
        else:
            results = f"{e=}"

    except Exception as e:
        results = f"{e=}"

    finally:
        return results


def open_folder(path):
    log = logging.getLogger(APP_NAME)
    path = Path(path)
    if path.is_dir():
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    else:
        raise Exception(f"invalid {path=}")
    log.info(f"Open folder success //{path.name}")


def write_version_file(
    parent_dir: Path,
    filename: str = "version.txt",
    version: str = "versionErr",
):
    log = logging.getLogger(APP_NAME)
    version_file = parent_dir / filename
    try:
        with open(version_file, "w") as fm:
            fm.write(version)
        log.info(f"version updated to {version}")
        return True
    except IOError:
        log.error("IOError: software version update failed")
    finally:
        return False


def copy_version_to_userConfigFolder(
    srcDir: Path, dstDir: Path, filename: str = "version.txt"
):
    src = srcDir / filename
    dst = dstDir / filename
    try:
        shutil.copy2(src, dst)
    except FileNotFoundError:
        raise FileNotFoundError(f"Copy src=~/{srcDir.name}/{filename}")
    except PermissionError:
        raise PermissionError(f"Copy dst=~/{dst.parent}/{dst.name}")
    except Exception as e:
        raise e


def get_version(version_file: Path):
    try:
        with open(version_file, "r") as fm:
            version = fm.readline()
        return version
    except IOError:
        log = logging.getLogger(APP_NAME)
        log.warning(f"{version_file=}")
        log.error(f"IOError: unable to access {version_file=}")
        return "versionErr"


def rmtree(path_to_clear: Path):
    try:
        log = logging.getLogger(APP_NAME)
        if not isinstance(path_to_clear, Path):
            path = Path(path_to_clear)
        else:
            path = path_to_clear
        if not path.is_dir():
            return None

        for fp in path.rglob("*"):
            log.info(f"removing //{fp.parent.name}/{fp.name}")
            try:
                os.remove(fp)
            except Exception as e:
                if fp.is_dir():
                    continue
                else:
                    log.warning(f"failed to remove!, {e=}")

        for fp in path.rglob("*"):
            os.rmdir(fp)
        os.rmdir(path)
        # shutil.rmtree(path=path_to_clear)
        path.mkdir(parents=True, exist_ok=True)
        log.info(f"deleted //{path.parent.name}/{path.name}/*.*")
        return path
    except Exception as e:
        raise e


def factory_reset(app_name: str) -> int:
    log = logging.getLogger(APP_NAME)
    user_docs = Path(os.path.expanduser("~/Documents/"))
    working_dir = user_docs / f"_tools-{app_name}"
    counter = 0
    if not working_dir.is_dir():
        errmsg = f"nothing to reset. {working_dir=}"
        if log is None:
            print(errmsg)
        else:
            log.error(errmsg)
        return 1

    src_dir = working_dir
    dst_dir = user_docs / f"_tools-{app_name}_backup_{get_time()}"
    try:
        shutil.copytree(src=src_dir, dst=dst_dir)
        if log is None:
            print(f"backup done //{dst_dir.parent.name}/{dst_dir.name}")
        else:
            log.info(f"backup done //{dst_dir.parent.name}/{dst_dir.name}")
    except Exception as e:
        errmsg = f"backup failed; {e=}"
        if log is None:
            print(errmsg)
        else:
            log.error(errmsg)

    try:
        if log is None:
            shutil.rmtree(path=src_dir)
            print(f"rmdir done //{src_dir.parent.name}/{src_dir.name}")
        else:
            if platform.system().lower() == "windows":
                log.info(f"system OS = {platform.system()}")
                log.warning("logger will shut down during factory reset")
                for handler in log.handlers:
                    if "FileHandler" in str(handler.__class__):
                        log.info(f"shutting down {handler.__class__}")
                        handler.close()
                        log.removeHandler(handler)
                        counter += 1
            shutil.rmtree(path=src_dir)
            log.info(f"rmdir done //{src_dir.parent.name}/{src_dir.name}")
    except Exception as e:
        errmsg = f"rmdir failed; {e=}"
        if log is None:
            print(errmsg)
        else:
            log.error(errmsg)
        return 2

    if counter > 0:
        if log is None:
            print("RESTARTING APP IS COMPULSORY")
            print("Please restart this app to complete factory reset!")
        else:
            log.error("RESTARTING APP IS COMPULSORY")
            log.warning("Please restart this app to complete factory reset!")
        return 3

    if log is None:
        print("reset completed successfully")
    else:
        log.error("reset completed successfully")
    return 0


def setup_basic_logger(default_loglevel=logging.INFO):
    logger = logging.getLogger(__name__)
    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(default_loglevel)

    # Create formatters and add it to handlers
    c_format = logging.Formatter("%(levelname)-8s: %(message)s")
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.setLevel(default_loglevel)
    return logger


def get_file(
    folderpath_str: str,
    wildcard_str: str,
    default_index: None | int = -1,
):
    """Get file(s) from a given folder, using the given wildcard

    :param folderpath_str: folderpath in string format
    :type folderpath_str: str
    :param wildcard_str: wildcard
    :type wildcard_str: str
    :param default_index: {None: returns all files in a list, 0: returns oldest modified file, -1: returns latest modified file}, defaults to -1
    :type default_index: None | int
    :return: list of Path objects or Path, depending on default_index
    :rtype: list[Path] or Path
    """
    log = logging.getLogger(APP_NAME)
    folderpath = Path(folderpath_str)
    if not folderpath.is_dir():
        raise NotADirectoryError(f"{folderpath}=")
    files = [f for f in folderpath.rglob(wildcard_str)]
    if not files:
        raise FileNotFoundError(f"{wildcard_str=}; {folderpath=}")
    # files = sorted(files)
    files = sorted(files, key=lambda fp: os.stat(fp).st_mtime)
    if default_index is None:
        return files
    elif len(files) > 1:
        log.debug(f"multiple files found, selected #{default_index}")
        filepath = files[default_index]
    else:
        filepath = files[0]
    return filepath


def cleanup_folder(folderpath: Path=None, clean_all=False):
    if folderpath is None:
        targetfolder = Path(cfg["output_folders"]["target"])
    else:
        targetfolder = folderpath
    wknumber_today = datetime.today().strftime("%yw%U")
    datefolder = targetfolder / f"archived-{wknumber_today}"

    for fp in targetfolder.glob("*.png"):
        if wknumber_today in fp.name and not clean_all:
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
            fp_time = datetime.strptime(" ".join(sp[3:5]), "%I.%M.%S %p").strftime(
                "%H%M%SH"
            )
            newname = f"ss-{fp_date}-{fp_time}.png"

        os.rename(fp, fp.parent / newname)
        log.warning(f"renamed {newname=}")


if __name__ == "__main__":
    # print(get_latest_git_tag(repo_path=Path(__file__).parent.parent))
    logger = setup_basic_logger()
    factory_reset(app_name=APP_NAME)
