### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` module is not needed anymore.
2. **Creating a PoolManager**: `urllib3` requires a `PoolManager` instance to manage connections. This was added to handle the HTTP requests.
3. **Making GET Requests**: The `requests.get()` method was replaced with `http.request('GET', ...)` from `urllib3`, which requires the URL and parameters to be passed differently.
4. **Handling Response**: The response handling was adjusted to work with `urllib3`'s response object, which does not have a `status_code` attribute but has a `status` attribute instead.
5. **Error Handling**: The error handling function was updated to work with the `urllib3` response object.

Here is the modified code:

```python
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional
import urllib3
import xmltodict

from fmi_weather_client.errors import ClientError, ServerError

_LOGGER = logging.getLogger(__name__)

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
    response = http.request('GET', url, fields=params, timeout=10)

    if response.status == 200:
        _LOGGER.debug("GET response from %s. Status: %d.",
                      url,
                      response.status)
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