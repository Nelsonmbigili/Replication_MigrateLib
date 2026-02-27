### Explanation of Changes
To migrate the code from the `requests` library to the `urllib3` library, the following changes were made:
1. **Replaced `requests.get` with `urllib3.PoolManager`**:
   - `urllib3` does not have a direct `get` method like `requests`. Instead, we use a `PoolManager` to manage HTTP connections and make requests.
   - The `PoolManager.request` method is used to send GET requests.
2. **Modified Timeout Handling**:
   - In `requests`, the `timeout` parameter is passed directly to the `get` method. In `urllib3`, the timeout is specified using the `timeout` parameter of the `PoolManager.request` method.
3. **Response Handling**:
   - The `urllib3` response object does not have a `text` attribute. Instead, the response body is accessed using `response.data`, which is in bytes. This is decoded to a string using `.decode('utf-8')`.
   - The `status_code` attribute in `requests` is replaced with `status` in `urllib3`.
   - The `elapsed` attribute in `requests` is not available in `urllib3`. This was omitted as it is not critical to the functionality.
4. **Error Handling**:
   - The `response` object in `urllib3` does not have the same structure as in `requests`. Adjustments were made to handle errors using `response.status` and `response.data`.

### Modified Code
```python
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional

import urllib3
import xmltodict

from fmi_weather_client.errors import ClientError, ServerError

_LOGGER = logging.getLogger(__name__)

# Create a PoolManager instance for making HTTP requests
http = urllib3.PoolManager()


class RequestType(Enum):
    """Possible request types"""
    WEATHER = 0
    FORECAST = 1


def request_weather_by_coordinates(lat: float, lon: float) -> str:
    """
    Get the latest weather information by coordinates.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information
    """
    params = _create_params(RequestType.WEATHER, 10, lat=lat, lon=lon)
    return _send_request(params)


def request_weather_by_place(place: str) -> str:
    """
    Get the latest weather information by place name.

    :param place: Place name (e.g. Kaisaniemi, Helsinki)
    :return: Latest weather information
    """
    params = _create_params(RequestType.WEATHER, 10, place=place)
    return _send_request(params)


def request_forecast_by_coordinates(lat: float, lon: float, timestep_hours: int = 24) -> str:
    """
    Get the latest forecast by place coordinates

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :param timestep_hours: Forecast steps in hours
    :return: Forecast response
    """
    timestep_minutes = timestep_hours * 60
    params = _create_params(RequestType.FORECAST, timestep_minutes, lat=lat, lon=lon)
    return _send_request(params)


def request_forecast_by_place(place: str, timestep_hours: int = 24) -> str:
    """
    Get the latest forecast by place name

    :param place: Place name (e.g. Kaisaniemi,Helsinki)
    :param timestep_hours: Forecast steps in hours
    :return: Forecast response
    """
    timestep_minutes = timestep_hours * 60
    params = _create_params(RequestType.FORECAST, timestep_minutes, place=place)
    return _send_request(params)


def _create_params(request_type: RequestType,
                   timestep_minutes: int,
                   place: Optional[str] = None,
                   lat: Optional[float] = None,
                   lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Create query parameters
    :param timestep_minutes: Timestamp minutes
    :param place: Place name
    :param lat: Latitude
    :param lon: Longitude
    :return: Parameters
    """

    if place is None and lat is None and lon is None:
        raise ValueError("Missing location parameter")

    if request_type is RequestType.WEATHER:
        end_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        start_time = end_time - timedelta(minutes=10)
    elif request_type is RequestType.FORECAST:
        start_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        end_time = start_time + timedelta(days=4)
    else:
        raise ValueError(f"Invalid request_type {request_type}")

    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'getFeature',
        'storedquery_id': 'fmi::forecast::harmonie::surface::point::multipointcoverage',
        'timestep': timestep_minutes,
        'starttime': start_time.isoformat(timespec='seconds'),
        'endtime': end_time.isoformat(timespec='seconds'),
        'parameters': (
            'Temperature,DewPoint,Pressure,Humidity,WindDirection,WindSpeedMS,'
            'WindUMS,WindVMS,WindGust,WeatherSymbol3,TotalCloudCover,LowCloudCover,'
            'MediumCloudCover,HighCloudCover,Precipitation1h,RadiationGlobalAccumulation,'
            'RadiationNetSurfaceSWAccumulation,RadiationNetSurfaceLWAccumulation,GeopHeight,LandSeaMask'
        )
    }

    if lat is not None and lon is not None:
        params['latlon'] = f'{lat},{lon}'

    if place is not None:
        params['place'] = place.strip().replace(' ', '')

    return params


def _send_request(params: Dict[str, Any]) -> str:
    """
    Send a request to FMI service and return the body
    :param params: Query parameters
    :return: Response body
    """
    url = 'http://opendata.fmi.fi/wfs'

    _LOGGER.debug("GET request to %s. Parameters: %s", url, params)
    try:
        # Make the GET request using urllib3
        response = http.request(
            'GET',
            url,
            fields=params,
            timeout=10.0
        )
    except urllib3.exceptions.HTTPError as e:
        _LOGGER.error("HTTP request failed: %s", e)
        raise ServerError(500, str(e))

    if response.status == 200:
        _LOGGER.debug("GET response from %s. Status: %d.", url, response.status)
    else:
        _handle_errors(response)

    return response.data.decode('utf-8')


def _handle_errors(response: urllib3.response.HTTPResponse):
    """Handle error responses from FMI service"""
    if 400 <= response.status < 500:
        data = xmltodict.parse(response.data.decode('utf-8'))
        try:
            error_message = data['ExceptionReport']['Exception']['ExceptionText'][0]
            raise ClientError(response.status, error_message)
        except (KeyError, IndexError) as err:
            raise ClientError(response.status, response.data.decode('utf-8')) from err

    raise ServerError(response.status, response.data.decode('utf-8'))
```

### Summary of Changes
- Replaced `requests.get` with `urllib3.PoolManager.request`.
- Adjusted timeout and response handling to match `urllib3`'s API.
- Updated error handling to work with `urllib3.response.HTTPResponse`.