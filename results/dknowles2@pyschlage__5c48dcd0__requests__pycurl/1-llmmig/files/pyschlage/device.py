"""Schlage devices."""

from dataclasses import dataclass
from enum import Enum
import pycurl
from io import BytesIO
import json

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

    @staticmethod
    def request_path(device_id: str | None = None) -> str:
        """Returns the request path for a Lock.

        :meta private:
        """
        path = "devices"
        if device_id:
            path = f"{path}/{device_id}"
        return path

    def send_command(self, command: str, data=dict) -> dict:
        """Sends a command to the device."""
        if not self._auth:
            raise NotAuthenticatedError

        path = f"{self.request_path(self.device_id)}/commands"
        url = self._auth.base_url + path  # Assuming _auth has a base_url attribute
        headers = self._auth.headers  # Assuming _auth has a headers attribute

        # Prepare the JSON payload
        payload = json.dumps({"data": data, "name": command})

        # Use pycurl to send the POST request
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, payload)
            curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.perform()
            curl.close()
        except pycurl.error as e:
            curl.close()
            raise RuntimeError(f"Failed to send command: {e}")

        # Parse the response
        response_data = buffer.getvalue().decode("utf-8")
        try:
            return json.loads(response_data)
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid response received: {response_data}")
