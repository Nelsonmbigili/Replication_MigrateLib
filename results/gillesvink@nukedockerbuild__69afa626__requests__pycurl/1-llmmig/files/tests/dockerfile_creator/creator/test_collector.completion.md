### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` calls**: The `requests.get` function was replaced with `pycurl` to perform HTTP GET requests. `pycurl` requires setting up a `pycurl.Curl` object, configuring it with options (e.g., URL, timeout), and capturing the response using a `BytesIO` buffer.
2. **Mocking `pycurl`**: Since `pycurl` does not have a direct equivalent to `requests.get`, the mocking strategy was adjusted to mock the behavior of `pycurl.Curl` and its options.
3. **Response Handling**: The `pycurl` response is captured in a `BytesIO` buffer, and the JSON data is extracted by decoding the buffer content. This replaces the `response.json()` method from `requests`.

Below is the modified code.

---

### Modified Code
```python
"""Tests related to the collector script.

@maintainer: Gilles Vink
"""

from unittest.mock import MagicMock, patch

import pytest
from nukedockerbuild.creator.collector import (
    _nuke_version_to_float,
    fetch_json_data,
    get_dockerfiles,
)
from nukedockerbuild.datamodel.constants import (
    JSON_DATA_SOURCE,
    OperatingSystem,
)
from nukedockerbuild.datamodel.docker_data import Dockerfile
import pycurl
from io import BytesIO


@pytest.fixture(autouse=True)
def _mock_pycurl():
    """Automatically patch every test to prevent actual calls."""
    with patch("nukedockerbuild.creator.collector.pycurl.Curl") as mock_curl:
        yield mock_curl


@pytest.fixture()
def dummy_data() -> dict:
    """Example data that would be fetched in the json requests."""
    return {
        "15": {
            "15.1v5": {
                "installer": {
                    "mac_x86": "mac_url",
                    "mac_arm": "mac_arm_url",
                }
            },
            "15.0v2": {
                "installer": {
                    "mac_x86": "mac_url",
                    "linux_x86": "linux_url",
                    "windows_x86": "windows_url",
                },
            },
        },
        "14": {
            "14.1v2": {
                "installer": {
                    "mac_x86": "mac_url",
                    "mac_arm": None,
                    "linux_x86": "linux_url",
                    "windows_x86": "windows_url",
                },
            },
        },
    }


def test_fetch_json_data(dummy_data: dict) -> None:
    """Test to make requests to Github and collect JSON."""
    response_mock = MagicMock()
    response_mock.getvalue.return_value = str(dummy_data).encode("utf-8")
    with patch(
        "nukedockerbuild.creator.collector.pycurl.Curl"
    ) as mock_curl, patch(
        "nukedockerbuild.creator.collector.BytesIO", return_value=response_mock
    ) as mock_buffer:
        curl_instance = mock_curl.return_value
        collected_data = fetch_json_data()
        curl_instance.setopt.assert_any_call(pycurl.URL, JSON_DATA_SOURCE)
        curl_instance.setopt.assert_any_call(pycurl.TIMEOUT, 10)
        curl_instance.perform.assert_called_once()
        curl_instance.close.assert_called_once()
        mock_buffer.assert_called_once()
    assert collected_data == dummy_data


@pytest.mark.parametrize("test_status_code", [403, 404])
def test_fetch_json_data_but_no_data_found(test_status_code: int) -> None:
    """Test to make sure we raise an exception when data is not found."""
    response_mock = MagicMock()
    response_mock.getvalue.return_value = b""
    with patch(
        "nukedockerbuild.creator.collector.pycurl.Curl"
    ) as mock_curl, patch(
        "nukedockerbuild.creator.collector.BytesIO", return_value=response_mock
    ):
        curl_instance = mock_curl.return_value
        curl_instance.getinfo.return_value = test_status_code
        with pytest.raises(
            ValueError,
            match="Request returned 404. Please check the URL and try again.",
        ):
            fetch_json_data()


@pytest.mark.parametrize(
    ("test_nuke_version", "expected_float"),
    [
        ("10.0v2", 10.0),
        ("15.5v51", 15.5),
        ("9.1v3", 9.1),
    ],
)
def test__nuke_version_to_float(
    test_nuke_version: str, expected_float: float
) -> None:
    """Test to convert string Nuke version to float."""
    assert _nuke_version_to_float(test_nuke_version) == expected_float


def test__nuke_version_to_float_raise_exception() -> None:
    """Test to raise an exception if no 'v' could be found."""
    with pytest.raises(
        ValueError, match="Provided data is not a valid version. '10.0b1'"
    ):
        _nuke_version_to_float("10.0b1")


def test_get_dockerfiles(dummy_data: dict) -> None:
    """Test to return from the dummy data a list of Dockerfile."""
    expected_dockerfiles = [
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=15.0,
            nuke_source="linux_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.WINDOWS,
            nuke_version=15.0,
            nuke_source="windows_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=14.1,
            nuke_source="linux_url",
        ),
        Dockerfile(
            operating_system=OperatingSystem.WINDOWS,
            nuke_version=14.1,
            nuke_source="windows_url",
        ),
    ]
    assert get_dockerfiles(dummy_data) == expected_dockerfiles


def test_get_dockerfiles_but_skip_12() -> None:
    """Test to not include version 12 as this is not valid for images."""
    dummy_data = {
        "15": {
            "15.0v2": {
                "installer": {
                    "linux_x86": "linux_url",
                },
            },
        },
        "12": {
            "12.0v2": {
                "installer": {
                    "linux_x86": "linux_url",
                },
            },
        },
    }
    expected_dockerfiles = [
        Dockerfile(
            operating_system=OperatingSystem.LINUX,
            nuke_version=15.0,
            nuke_source="linux_url",
        ),
    ]
    assert get_dockerfiles(dummy_data) == expected_dockerfiles
```

---

### Key Adjustments
1. **`pycurl` Setup**: Replaced `requests.get` with `pycurl.Curl` and configured it with `setopt` for URL and timeout.
2. **Response Handling**: Used `BytesIO` to capture the response body and decoded it to extract JSON data.
3. **Mocking**: Adjusted mocking to simulate `pycurl.Curl` behavior and the `BytesIO` buffer for response handling.