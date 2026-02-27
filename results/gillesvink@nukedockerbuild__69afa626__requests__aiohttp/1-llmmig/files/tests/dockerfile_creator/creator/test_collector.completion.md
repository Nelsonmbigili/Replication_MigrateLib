### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Replaced `requests.get` with `aiohttp.ClientSession.get`**:
   - `aiohttp` is asynchronous, so the `fetch_json_data` function was modified to use `async def` and `await` for making HTTP requests.
   - The `aiohttp.ClientSession` context manager was used to manage the session.
2. **Updated Mocking**:
   - Mocking `requests.get` was replaced with mocking `aiohttp.ClientSession.get` and its associated methods (`__aenter__`, `json`, etc.).
3. **Modified Tests**:
   - Since `aiohttp` is asynchronous, the tests for `fetch_json_data` were updated to use `pytest.mark.asyncio` to handle asynchronous test functions.
   - Mocking the `aiohttp` response required handling the asynchronous nature of `aiohttp` methods like `json()` and `__aenter__`.

Below is the modified code:

---

### Modified Code
```python
"""Tests related to the collector script.

@maintainer: Gilles Vink
"""

from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.fixture(autouse=True)
def _mock_aiohttp():
    """Automatically patch every test to prevent actual calls."""
    with patch("nukedockerbuild.creator.collector.aiohttp.ClientSession.get"):
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


@pytest.mark.asyncio
async def test_fetch_json_data(dummy_data: dict) -> None:
    """Test to make requests to Github and collect JSON."""
    response_mock = AsyncMock()
    response_mock.json.return_value = dummy_data
    response_mock.status = 200
    with patch(
        "nukedockerbuild.creator.collector.aiohttp.ClientSession.get",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=response_mock)),
    ) as aiohttp_get_mock:
        collected_data = await fetch_json_data()
    aiohttp_get_mock.assert_called_once_with(JSON_DATA_SOURCE, timeout=10)
    assert collected_data == dummy_data


@pytest.mark.asyncio
@pytest.mark.parametrize("test_status_code", [403, 404])
async def test_fetch_json_data_but_no_data_found(test_status_code: int) -> None:
    """Test to make sure we raise an exception when data is not found."""
    response_mock = AsyncMock()
    response_mock.status = test_status_code
    with patch(
        "nukedockerbuild.creator.collector.aiohttp.ClientSession.get",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=response_mock)),
    ), pytest.raises(
        ValueError,
        match="Request returned 404. Please check the URL and try again.",
    ):
        await fetch_json_data()


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

### Key Notes
1. The `fetch_json_data` function and its tests were updated to handle asynchronous behavior using `aiohttp`.
2. Mocking `aiohttp.ClientSession.get` required handling the asynchronous context manager (`__aenter__`) and the `json()` method.
3. The rest of the code remains unchanged, as it is unrelated to the migration from `requests` to `aiohttp`.