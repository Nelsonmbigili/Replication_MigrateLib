### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` is a lower-level library compared to `requests`, so it requires more setup. Specifically, we need to:
     - Initialize a `pycurl.Curl` object.
     - Set the URL, timeout, and other options manually.
     - Use a `BytesIO` object to capture the response data.
   - The HTTP status code is retrieved using `curl.getinfo(pycurl.RESPONSE_CODE)`.
2. **Replaced `fetched_data.json()`**:
   - `pycurl` does not have a built-in method to parse JSON. Instead, the response is captured as a byte string, which is then decoded and parsed using the `json.loads` function from the `json` module.
3. **Error Handling**:
   - Added error handling for HTTP status codes and connection issues using `pycurl`'s exception mechanism.

Below is the modified code:

---

### Modified Code:
```python
"""Script that collects Dockerfiles that can be created.

@maintainer: Gilles Vink
"""
from __future__ import annotations

import logging
import re
import json
import pycurl
from io import BytesIO

from nukedockerbuild.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from nukedockerbuild.datamodel.docker_data import Dockerfile

_VERSION_REGEX = re.compile("^[^v]*")

logger = logging.getLogger(__name__)


def fetch_json_data() -> dict:
    """Fetch data from JSON on Github and return as dict."""
    buffer = BytesIO()
    curl = pycurl.Curl()
    try:
        curl.setopt(pycurl.URL, JSON_DATA_SOURCE)
        curl.setopt(pycurl.TIMEOUT, 10)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.perform()

        # Check HTTP response code
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code != 200:
            msg = f"Request returned {status_code}. Please check the URL and try again."
            raise ValueError(msg)

        # Decode and parse JSON response
        response_data = buffer.getvalue().decode("utf-8")
        logger.info("Fetched JSON data containing Nuke releases.")
        return json.loads(response_data)

    except pycurl.error as e:
        msg = f"An error occurred while making the request: {e}"
        raise ValueError(msg)

    finally:
        curl.close()


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

---

### Key Points:
1. The `requests.get` call was replaced with `pycurl` setup and execution.
2. The response data is captured using a `BytesIO` buffer and decoded manually.
3. JSON parsing is done using the `json.loads` function.
4. Error handling for HTTP status codes and `pycurl` exceptions was added.

This ensures the functionality remains the same while using `pycurl` instead of `requests`.