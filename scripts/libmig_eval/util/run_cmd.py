import time
from datetime import datetime
from os import PathLike
from pathlib import Path
from subprocess import Popen, PIPE
from threading import Timer


class CommandError(Exception):
    def __init__(self, message, returncode):
        super().__init__(message)
        self.returncode = returncode


def _show_progress(process: Popen):
    start = time.time()
    sleep_time = .1

    while process.poll() is None:
        time.sleep(sleep_time)
        duration = int(time.time() - start)
        if duration >= 1:
            break

    if process.poll() is not None:
        return

    sleep_time = 1
    while process.poll() is None:
        duration = int(time.time() - start)
        symbol = "|" if duration % 10 == 0 else "."
        print(symbol, end="")
        if duration % 60 == 0:
            print(f" {(duration / 60):.0f}m")
        time.sleep(sleep_time)

    print()


def run_cmd(args: list[any], cwd: Path = None, raise_error=True, timeout_minutes=60.0):
    def _arg_as_str(arg):
        if isinstance(arg, Path):
            if cwd and arg.is_relative_to(cwd):
                arg = arg.relative_to(cwd)
            arg = arg.as_posix()
        return str(arg)

    arg_str = " ".join(_arg_as_str(arg) for arg in args)
    print(f"Running command at {datetime.now()}: {arg_str}")
    process = Popen(args, stdout=PIPE, stderr=PIPE, text=True, cwd=cwd, encoding="utf-8")

    def timeout_proc():
        process.kill()

    timer = Timer(timeout_minutes * 60, timeout_proc)
    try:
        timer.start()
        out, err = process.communicate()
        if not timer.is_alive():
            raise TimeoutError(f"Command timed out after {timeout_minutes} minutes")

        print(f"  Finished at {datetime.now()}")
        if process.returncode != 0:
            if raise_error:
                raise CommandError(err, process.returncode)
            out = err
        return out, process.returncode
    finally:
        timer.cancel()


def run_with_venv(venv_path: Path, args: list[any], cwd: Path = None, raise_error=True, timeout_minutes=60.0):
    args[0] = venv_path / "Scripts" / args[0]
    return run_cmd(args, cwd=cwd, raise_error=raise_error, timeout_minutes=timeout_minutes)


def shallow_clone(repo: str, commit: str, repo_path: Path):
    url = f"https://github.com/{repo}"
    if repo_path.exists():
        print(f"  {repo_path.name} already exists. Skipping.")
        return
    run_cmd(["git", "init", repo_path])
    run_cmd(["git", "remote", "add", "origin", url], cwd=repo_path)
    run_cmd(["git", "fetch", "--depth", "1", "origin", commit], cwd=repo_path)
    run_cmd(["git", "checkout", commit], cwd=repo_path)


def pip_install(venv_path: Path, *args: str | PathLike):
    return run_with_venv(venv_path, ["pip", "install", "--disable-pip-version-check"] + list(args),
                         raise_error=False, timeout_minutes=10)
