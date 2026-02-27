### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `httpx`.
2. **HTTP Request**: Updated the `requests.get` call to `httpx.get`. The `httpx` library has a similar API to `requests`, so the change is straightforward.
3. **Timeout Handling**: The `timeout` parameter in `httpx.get` works similarly to `requests.get`, so no additional changes were needed.
4. **Response Handling**: The `httpx` response object has the same `status_code` and `json()` methods as `requests`, so no changes were required in how the response is processed.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
"""Script that collects Dockerfiles that can be created.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import re

import httpx  # Updated import from requests to httpx

from nukedockerbuild.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from nukedockerbuild.datamodel.docker_data import Dockerfile

_VERSION_REGEX = re.compile("^[^v]*")

logger = logging.getLogger(__name__)


def fetch_json_data() -> dict:
    """Fetch data from JSON on Github and return as dict."""
    fetched_data = httpx.get(JSON_DATA_SOURCE, timeout=10)  # Updated to use httpx.get
    if fetched_data.status_code != 200:
        msg = "Request returned 404. Please check the URL and try again."
        raise ValueError(msg)
    logger.info("Fetched JSON data containing Nuke releases.")
    return fetched_data.json()


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

### Summary of Changes
- Replaced `requests` with `httpx` in the import statement.
- Updated the `requests.get` call to `httpx.get` in the `fetch_json_data` function.
- No other changes were made, as the `httpx` library provides a similar interface to `requests` for the functionality used in this script.