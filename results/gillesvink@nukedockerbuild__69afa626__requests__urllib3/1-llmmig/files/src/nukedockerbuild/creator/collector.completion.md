### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`, so the `requests` import was removed, and `urllib3` was imported instead.
2. **HTTP Request Handling**: The `requests.get` method was replaced with `urllib3.PoolManager().request`. This required creating an instance of `urllib3.PoolManager` to handle HTTP requests.
3. **Status Code Handling**: In `urllib3`, the status code is accessed via the `status` attribute of the response object instead of `status_code` as in `requests`.
4. **JSON Parsing**: The `json()` method in `requests` was replaced with `json.loads()` from the `json` module, as `urllib3` does not provide a built-in `json()` method for responses.
5. **Timeout Handling**: The `timeout` parameter in `requests.get` was replaced with the `timeout` parameter in `urllib3.PoolManager().request`.

### Modified Code:
```python
"""Script that collects Dockerfiles that can be created.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import re
import json  # Added for JSON parsing with urllib3

import urllib3  # Replaced requests with urllib3

from nukedockerbuild.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from nukedockerbuild.datamodel.docker_data import Dockerfile

_VERSION_REGEX = re.compile("^[^v]*")

logger = logging.getLogger(__name__)


def fetch_json_data() -> dict:
    """Fetch data from JSON on Github and return as dict."""
    http = urllib3.PoolManager()  # Create a PoolManager instance
    response = http.request("GET", JSON_DATA_SOURCE, timeout=10.0)  # Perform GET request with timeout
    if response.status != 200:  # Check the status code
        msg = "Request returned 404. Please check the URL and try again."
        raise ValueError(msg)
    logger.info("Fetched JSON data containing Nuke releases.")
    return json.loads(response.data.decode("utf-8"))  # Decode and parse JSON data


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

### Summary of Changes:
- Replaced `requests.get` with `urllib3.PoolManager().request`.
- Used `response.status` instead of `response.status_code`.
- Used `json.loads()` to parse the response data.
- Added `urllib3` and `json` imports.
- Ensured the timeout parameter was passed correctly to `urllib3`.