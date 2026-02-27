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
