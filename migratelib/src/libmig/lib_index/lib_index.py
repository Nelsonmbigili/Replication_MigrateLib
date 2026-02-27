import json
from collections import defaultdict
from pathlib import Path

from libmig.lib_index.api_models import API
from libmig.utils.cache import cache_file_path
from libmig.utils.venv import Venv


class LibIndex:
    """
    Indexes a library's APIs.
    This class initializes a virtual environment, and installs the library in it.
    Then from the virtual environment, it generates the info.

    This caches the library info, so should not assume that the library is installed in the virtual environment.
    """

    def __init__(self, module_name: str, module_version: str, venv: Venv = None):
        self.module_name = module_name.lower()
        self.module_version = module_version
        self.venv = venv
        self._apis: list[API] = None
        self._api_index: dict[str, list[API]] = None
        self.import_names: list[str] = []
        self._public_apis = None
        self._init()

    def _init(self):
        lib_info_path = cache_file_path(f"lib-info/{self.module_name}-{self.module_version}.json")

        if not lib_info_path.exists():
            venv = self.venv
            venv.install(self.module_name, self.module_version)

            import_names = venv.import_names(self.module_name, self.module_version)

            if not import_names:
                raise ValueError(f"No top-level import names found for {self.module_name}=={self.module_version}")

            this_script_path = Path(__file__)
            gen_script_path = (this_script_path.parent / "generate_lib_info.py").absolute().as_posix()
            r_code = venv.run_script("python", gen_script_path, ",".join(import_names),
                                     lib_info_path.as_posix(), read_output=False)
            if r_code != 0:
                raise ValueError(f"Failed to generate library info for {self.module_name}=={self.module_version}")

        lib_info = json.load(open(lib_info_path))
        self.import_names = lib_info["import_names"]

        apis = [API(**api_info) for api_info in lib_info["apis"]]
        self._api_index = defaultdict(list)
        for api in apis:
            self._api_index[api.qualified_name].append(api)

        self._apis = apis
        self._public_apis = [api for api in self._apis if api.is_public()]

    def get_all_apis(self):
        return self._apis

    def get_public_apis(self):
        return self._public_apis

    def get_api(self, qualified_name: str):
        if qualified_name not in self._api_index:
            self._api_index[qualified_name] = [api for api in self.get_all_apis() if
                                               api["qualified_name"] == qualified_name]
        apis = self._api_index[qualified_name]
        if not apis:
            raise ValueError(f"API {qualified_name} not found in {self.module_name}")
        if len(apis) > 1:
            raise ValueError(f"Multiple APIs found for {qualified_name} in {self.module_name}")
        return apis[0]

    def search_apis(self, name: str, file: str = None, line: int = None):
        searched = [api for api in self.get_all_apis() if api.short_name == name or api.qualified_name == name]
        if file:
            searched = [api for api in searched if api.file == file]

        if line:
            searched = [api for api in searched if api.line == line]

        return searched

    def find_api(self, name: str, file: str = None, line: int = None) -> API:
        apis = self.search_apis(name, file, line)
        if not apis:
            raise ValueError(f"API {name} not found in {self.module_name} at {file}:{line}")
        if len(apis) > 1:
            raise ValueError(f"Multiple APIs found for {name} in {self.module_name} at {file}:{line}")
        return apis[0]

    @classmethod
    def from_venv(cls, name: str, venv: Venv):
        v = venv.installed_version(name)
        return cls(name, v, venv)
