import os
from abc import ABC, abstractmethod
from pathlib import Path

from johnnydep import JohnnyDist

from libmig.cmd import run_and_get_output, run


def get_venv(venv_dir: Path, python_version: str = None):
    if os.name == "nt":
        return WindowsVenv(venv_dir, python_version)
    elif os.name == "posix":
        return UnixVenv(venv_dir, python_version)
    else:
        raise ValueError(f"Unsupported OS: {os.name}")


class Venv(ABC):
    default_args = {
        "pip": ["--disable-pip-version-check"],
    }

    def __init__(self, venv_dir: Path, python_version: str):
        self.venv_dir = venv_dir
        self.python_version = python_version

    @abstractmethod
    def script(self, script_name: str) -> Path:
        pass

    def run_script(self, script_name: str, *args, read_output: bool = True, cwd: Path = None):
        script = self.script(script_name)
        default_args = self.default_args.get(script_name, [])
        default_args_not_provided = [arg for arg in default_args if arg not in args]
        args = [*args, *default_args_not_provided]
        if read_output:
            return run_and_get_output([script, *args], cwd=cwd)
        else:
            return run([script, *args], cwd=cwd)

    def install(self, package_name: str, version: str):
        """
        Install a package in the virtual environment.
        :param package_name: name of the package to install
        :param version: version of the package to install. Use "latest" to upgrade the package to the latest version.
        """
        installed_version = self.installed_version(package_name)
        if installed_version == version:
            # already installed
            return
        args = ["install", package_name]
        # install with source distribution for this library. :all: causes some installations to fail
        if version == "latest":
            args += ["--upgrade", package_name]
        else:
            args += [f"{package_name}=={version}"]

        self.run_script("pip", *args)

    def import_names(self, package_name: str, version: str):
        dist = JohnnyDist(f"{package_name}=={version}")
        return dist.import_names

    def installed_version(self, package_name: str):
        # todo: test for uninstalled packages
        code = f"""
from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
try:
    dist = distribution("{package_name}")
    ver = dist.version
except PackageNotFoundError:
    ver = ""
print(ver)
"""

        version = self.run_script("python", "-c", code, read_output=True)
        return version.strip()

    @abstractmethod
    def lib_path(self, import_name: str):
        pass

    @abstractmethod
    def create(self):
        pass

    def exists(self):
        return self.script("python").exists()

    def has_script(self, script_name: str):
        return self.script(script_name).exists()


class WindowsVenv(Venv):
    def script(self, script_name: str):
        return self.venv_dir / "Scripts" / (script_name + ".exe")

    def create(self):
        os.system(f"py -{self.python_version} -m venv {self.venv_dir}")

    def lib_path(self, import_name: str):
        return self.venv_dir / "Lib" / "site-packages" / import_name


class UnixVenv(Venv):
    def script(self, script_name: str):
        return self.venv_dir / "bin" / script_name

    def create(self):
        print("\n \n \n \nhi hi", self.venv_dir) #debug
        os.system(f"python -m venv .venv")

    def lib_path(self, import_name: str):
        py_version = self.run_script("python", "--version", read_output=True).split()[1]
        py_minor_version = py_version.rsplit(".", 1)[0]
        return self.venv_dir / "lib" / f"python{py_minor_version}" / "site-packages" / import_name
