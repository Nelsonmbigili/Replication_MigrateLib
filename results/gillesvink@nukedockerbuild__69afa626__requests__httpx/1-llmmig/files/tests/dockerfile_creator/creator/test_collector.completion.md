### Explanation of Changes
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Import Changes**: Replaced `requests` imports with `httpx`.
2. **Mocking Changes**: Updated the `patch` calls to mock `httpx.get` instead of `requests.get`.
3. **Response Mocking**: Updated the `MagicMock` to mock `httpx.Response` instead of `requests.Response`.
4. **Timeout Handling**: `httpx` uses a `timeout` parameter in a similar way to `requests`, so no changes were needed for the timeout argument.
5. **Behavioral Consistency**: The behavior of `httpx` is similar to `requests` for the purposes of this code, so the changes are minimal and focused on replacing `requests` with `httpx`.

### Modified Code
Here is the complete code after migrating to `httpx`:

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
from httpx import Response


@pytest.fixture(autouse=True)
def _mock_requests():
    """Automatically patch every test to prevent actual calls."""
    with patch("nukedockerbuild.creator.collector.httpx.get"):
        yield


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
    response_mock = MagicMock(spec=Response)
    response_mock.json.return_value = dummy_data
    response_mock.status_code = 200
    with patch(
        "nukedockerbuild.creator.collector.httpx.get",
        return_value=response_mock,
    ) as httpx_get_mock:
        collected_data = fetch_json_data()
    httpx_get_mock.assert_called_once_with(JSON_DATA_SOURCE, timeout=10)
    assert collected_data == dummy_data


@pytest.mark.parametrize("test_status_code", [403, 404])
def test_fetch_json_data_but_no_data_found(test_status_code: int) -> None:
    """Test to make sure we raise an exception when data is not found."""
    httpx_get_mock = MagicMock(spec=Response)
    httpx_get_mock.status_code = test_status_code
    with patch(
        "nukedockerbuild.creator.collector.httpx.get",
        return_value=httpx_get_mock,
    ), pytest.raises(
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

### Summary of Changes
- Replaced `requests` with `httpx` in imports and mock patches.
- Updated `MagicMock` to mock `httpx.Response` instead of `requests.Response`.
- Ensured all `httpx.get` calls and their arguments match the original `requests.get` behavior.