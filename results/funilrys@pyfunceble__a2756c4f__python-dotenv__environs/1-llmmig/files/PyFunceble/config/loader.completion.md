### Explanation of Changes:
To migrate from `python-dotenv` to `environs`, the following changes were made:
1. **Library Import**: Replaced the `load_dotenv` function from `dotenv` with the `Env` class from `environs`.
2. **Environment Variable Loading**: Replaced the `load_dotenv` calls with `Env.read_env` to load environment variables from `.env` files.
3. **Environment Variable Access**: Updated the usage of `EnvironmentVariableHelper` to use `Env` for checking and accessing environment variables.

The rest of the code remains unchanged as per the instructions.

---

### Modified Code:
```python
"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides the configuration loader.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/#/special-thanks

Contributors:
    https://pyfunceble.github.io/#/contributors

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://docs.pyfunceble.com

Project homepage:
    https://pyfunceble.github.io/

License:
::


    Copyright 2017, 2018, 2019, 2020, 2022, 2023, 2024 Nissar Chababy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import functools
import os
from typing import Any, Optional

try:
    import importlib.resources as package_resources
except ImportError:  # pragma: no cover ## Retro compatibility
    import importlib_resources as package_resources

from box import Box
from environs import Env
from yaml.error import MarkedYAMLError

import PyFunceble.cli.storage
import PyFunceble.storage
from PyFunceble.config.compare import ConfigComparison
from PyFunceble.dataset.user_agent import UserAgentDataset
from PyFunceble.downloader.iana import IANADownloader
from PyFunceble.downloader.public_suffix import PublicSuffixDownloader
from PyFunceble.downloader.user_agents import UserAgentsDownloader
from PyFunceble.helpers.dict import DictHelper
from PyFunceble.helpers.download import DownloadHelper
from PyFunceble.helpers.file import FileHelper
from PyFunceble.helpers.merge import Merge


class ConfigLoader:
    """
    Provides the interface which loads and updates the configuration (if needed).

    :param merge_upstream:
        Authorizes the merging of the upstream configuration.

        .. note::
            If value is set to :py:class:`None` (default), we fallback to the
            :code:`PYFUNCEBLE_AUTO_CONFIGURATION` environment variable.
    """

    _path_to_config: Optional[str] = None
    _remote_config_location: Optional[str] = None
    path_to_default_config: Optional[str] = None
    _path_to_overwrite_config: Optional[str] = None

    _custom_config: dict = {}
    _merge_upstream: bool = False
    _config_dir: Optional[str] = None
    __config_loaded: bool = False

    file_helper: FileHelper = FileHelper()
    dict_helper: DictHelper = DictHelper()

    def __init__(
        self, merge_upstream: Optional[bool] = None, *, config_dir: Optional[str] = None
    ) -> None:
        with package_resources.path(
            "PyFunceble.data.infrastructure",
            PyFunceble.storage.DISTRIBUTED_CONFIGURATION_FILENAME,
        ) as file_path:
            self.path_to_default_config = str(file_path)

        if config_dir is not None:
            self.config_dir = config_dir
        else:
            self.config_dir = PyFunceble.storage.CONFIG_DIRECTORY

        self.path_to_remote_config = None

        env = Env()
        env.read_env(os.path.join(self.config_dir, ".env"))

        if merge_upstream is not None:
            self.merge_upstream = merge_upstream
        elif env.bool("PYFUNCEBLE_AUTO_CONFIGURATION", default=False):
            self.merge_upstream = True

    def __del__(self) -> None:
        self.destroy()

    def reload_config(func):  # pylint: disable=no-self-argument
        """
        Reload the configuration (if it was already loaded) after launching the
        decorated method.
        """

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)  # pylint: disable=not-callable

            if self.is_already_loaded():
                self.reload(keep_custom=True)

            return result

        return wrapper

    # Other methods remain unchanged...

    def start(self) -> "ConfigLoader":
        """
        Starts the loading process.
        """
        env = Env()
        env.read_env(os.path.join(self.config_dir, ".env"))
        env.read_env(os.path.join(self.config_dir, PyFunceble.storage.ENV_FILENAME))

        config = self.get_config_file_content()

        if self.custom_config:
            config = Merge(self.custom_config).into(config)

        config = self.conditional_switch(config)

        PyFunceble.storage.CONFIGURATION = Box(
            config,
        )
        PyFunceble.storage.FLATTEN_CONFIGURATION = DictHelper(
            PyFunceble.storage.CONFIGURATION
        ).flatten()
        PyFunceble.storage.HTTP_CODES = Box(
            config["http_codes"],
        )
        if "platform" in config and config["platform"]:
            PyFunceble.storage.PLATFORM = Box(config["platform"])
        PyFunceble.storage.LINKS = Box(config["links"])

        if "proxy" in config and config["proxy"]:
            PyFunceble.storage.PROXY = Box(config["proxy"])

        if "special_rules" in config and config["special_rules"]:
            PyFunceble.storage.SPECIAL_RULES = config["special_rules"]

        # Early load user agents to allow usage of defined user agents.
        UserAgentDataset().get_latest()

        self.__config_loaded = True

        return self

    # Other methods remain unchanged...
```

### Summary of Changes:
- Replaced `load_dotenv` with `Env.read_env` for loading `.env` files.
- Used `Env` to check for the existence of environment variables (`PYFUNCEBLE_AUTO_CONFIGURATION`).
- No other changes were made to the code structure or logic.