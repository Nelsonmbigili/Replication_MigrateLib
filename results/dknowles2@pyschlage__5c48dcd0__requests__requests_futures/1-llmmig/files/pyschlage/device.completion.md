### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Changes**: The `Response` class from `requests` was replaced with the `Response` class from `requests_futures`.
2. **Asynchronous Requests**: The `requests_futures` library provides asynchronous request capabilities. The `send_command` method was updated to use the `FuturesSession` object for making asynchronous requests. This required initializing a `FuturesSession` instance and using it to send the request.
3. **Return Type**: The `send_command` method now returns a `Future` object instead of a `Response` object. This allows the caller to handle the asynchronous response.

### Modified Code
```python
"""Schlage devices."""

from dataclasses import dataclass
from enum import Enum

from requests_futures.sessions import FuturesSession
from requests_futures.sessions import Response

from .common import Mutable
from .exceptions import NotAuthenticatedError


class DeviceType(str, Enum):
    """Known device types."""

    BRIDGE = "br400"
    DENALI = "be489"
    DENALI_BLE = "be489ble"
    DENALI_MCKINLEY = "be489wb2"
    DENALI_MCKINLEY_BLE = "be489ble2"
    DENALI_MCKINLEY_WIFI = "be489wifi2"
    DENALI_WIFI = "be489wifi"
    ENCODE_LEVER = "fe789"
    ENCODE_LEVER_BLE = "fe789ble"
    ENCODE_LEVER_MCKINLEY = "fe789wb2"
    ENCODE_LEVER_MCKINLEY_BLE = "fe789ble2"
    ENCODE_LEVER_MCKINLEY_WIFI = "fe789wifi2"
    ENCODE_LEVER_WIFI = "fe789wifi"
    JACKALOPE = "be499"
    JACKALOPE_BLE = "be499ble"
    JACKALOPE_MCKINLEY = "be499wb2"
    JACKALOPE_MCKINLEY_BLE = "be499ble2"
    JACKALOPE_MCKINLEY_WIFI = "be499wifi2"
    JACKALOPE_WIFI = "be499wifi"
    SENSE = "be479"


@dataclass
class Device(Mutable):
    """Base class for Schlage devices."""

    device_id: str = ""
    """Schlage-generated unique device identifier."""

    device_type: str = ""
    """The device type of the lock.

    See |DeviceType| for currently known types.
    """

    def __post_init__(self):
        """Initialize the FuturesSession for asynchronous requests."""
        self._session = FuturesSession()

    @staticmethod
    def request_path(device_id: str | None = None) -> str:
        """Returns the request path for a Lock.

        :meta private:
        """
        path = "devices"
        if device_id:
            path = f"{path}/{device_id}"
        return path

    def send_command(self, command: str, data=dict) -> Response:
        """Sends a command to the device."""
        if not self._auth:
            raise NotAuthenticatedError
        path = f"{self.request_path(self.device_id)}/commands"
        json = {"data": data, "name": command}
        # Use FuturesSession to send the request asynchronously
        return self._session.post(self._auth.base_url + path, json=json, headers=self._auth.headers)
```

### Key Notes
- The `FuturesSession` object is initialized in the `__post_init__` method of the `Device` class. This ensures that the session is available for all instances of the class.
- The `send_command` method now uses the `FuturesSession.post` method to send the request asynchronously.
- The `Response` object returned by `FuturesSession.post` is a `Future` object, which allows the caller to handle the response asynchronously. If synchronous behavior is needed, the caller can use `.result()` on the returned `Future` object to block until the response is available.