### Explanation of Changes
The migration from `requests` to `aiohttp` involves switching from synchronous HTTP requests to asynchronous HTTP requests. The key changes made are:
1. **Importing `aiohttp`**: Replaced the `requests` library with `aiohttp`.
2. **Asynchronous Function**: The `fetch_json_data` function is now an `async` function to accommodate the asynchronous nature of `aiohttp`.
3. **Using `aiohttp.ClientSession`**: Replaced `requests.get` with `aiohttp.ClientSession` for making HTTP requests.
4. **Error Handling**: Used `aiohttp.ClientResponse` to check the status code and raise an exception if the response is not successful.
5. **JSON Parsing**: Used the `await response.json()` method to parse the JSON data asynchronously.
6. **Calling the Function**: Since `fetch_json_data` is now asynchronous, it must be awaited when called. However, this change is not reflected in the provided code because the calling context is not included.

### Modified Code
```python
"""Script that collects Dockerfiles that can be created.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import re

import aiohttp

from nukedockerbuild.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from nukedockerbuild.datamodel.docker_data import Dockerfile

_VERSION_REGEX = re.compile("^[^v]*")

logger = logging.getLogger(__name__)


async def fetch_json_data() -> dict:
    """Fetch data from JSON on Github and return as dict."""
    async with aiohttp.ClientSession() as session:
        async with session.get(JSON_DATA_SOURCE, timeout=10) as response:
            if response.status != 200:
                msg = "Request returned 404. Please check the URL and try again."
                raise ValueError(msg)
            logger.info("Fetched JSON data containing Nuke releases.")
            return await response.json()


def _nuke_version_to_float(nuke_version: str) -> float:
    """Return Nuke version as a float.

    Args:
        nuke_version: something like 10.0v2

    Returns:
        nuke version as float, for example 10.0
    """
    if "v" not in nuke_version:
        msg = f"Provided data is not a valid version. '{nuke_version}'"
        raise ValueError(msg)
    match = re.search(_VERSION_REGEX, nuke_version)
    return float(match.group())


def get_dockerfiles(data: dict) -> list[Dockerfile]:
    """Convert provided data dict to list of Dockerfile.

    Args:
        data: the requested JSON data.

    Returns:
        list of Dockerfile.
    """
    releases = {
        inner_key: inner_value
        for _, outer_value in data.items()
        for inner_key, inner_value in outer_value.items()
    }

    dockerfiles: list[Dockerfile] = []
    for version, release_data in releases.items():
        installer_data = release_data.get("installer")
        version_number = _nuke_version_to_float(version)

        # As everything below Nuke 13 is considered EOL. Skipping it.
        if version_number < 13:
            continue

        for os in ["linux_x86", "windows_x86"]:
            install_url = installer_data.get(os)
            if not install_url:
                continue
            dockerfiles.append(
                Dockerfile(
                    operating_system=OperatingSystem.from_mapped_name(os),
                    nuke_version=version_number,
                    nuke_source=install_url,
                )
            )
    msg = f"Found {len(dockerfiles)} possible dockerfiles."
    logger.info(msg)

    return dockerfiles
```

### Notes
1. The `fetch_json_data` function is now asynchronous, so it must be called with `await` in an asynchronous context. If the calling code is not asynchronous, you may need to use an event loop to run it.
2. No other parts of the code were changed, as per the instructions.