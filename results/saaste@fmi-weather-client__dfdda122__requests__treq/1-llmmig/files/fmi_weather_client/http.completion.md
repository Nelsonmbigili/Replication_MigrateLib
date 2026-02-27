### Explanation of Changes
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: `treq` is an asynchronous library, so the `_send_request` function was modified to be asynchronous (`async def`) and to use `await` for the `treq` calls.
2. **Replaced `requests.get` with `treq.get`**: The `requests.get` call was replaced with `treq.get`, which is asynchronous.
3. **Response Handling**: `treq` returns a `Response` object that requires asynchronous methods to access the response body. The `response.text` was replaced with `await response.text()` to handle this.
4. **Error Handling**: The `_handle_errors` function was updated to work with `treq`'s `Response` object. The response body is now accessed asynchronously using `await response.text()`.
5. **Logging Response Time**: `treq` does not provide `response.elapsed`, so this part of the logging was removed.
6. **Calling `_send_request`**: Since `_send_request` is now asynchronous, all calls to it must use `await`. The functions that call `_send_request` were updated to be asynchronous (`async def`) as well.

### Modified Code
Here is the entire code after migration to `treq`:

```python
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional

import treq
import xmltodict

from fmi_weather_client.errors import ClientError, ServerError

_LOGGER = logging.getLogger(__name__)


class RequestType(Enum):
    """Possible request types"""
    WEATHER = 0
    FORECAST = 1


async def request_weather_by_coordinates(lat: float, lon: float) -> str:
    """
    Get the latest weather information by coordinates.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information
    """
    params = _create_params(RequestType.WEATHER, 10, lat=lat, lon=lon)
    return await _send_request(params)


async def request_weather_by_place(place: str) -> str:
    """
    Get the latest weather information by place name.

    :param place: Place name (e.g. Kaisaniemi, Helsinki)
    :return: Latest weather information
    """
    params = _create_params(RequestType.WEATHER, 10, place=place)
    return await _send_request(params)


async def request_forecast_by_coordinates(lat: float, lon: float, timestep_hours: int = 24) -> str:
    """
    Get the latest forecast by place coordinates

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :param timestep_hours: Forecast steps in hours
    :return: Forecast response
    """
    timestep_minutes = timestep_hours * 60
    params = _create_params(RequestType.FORECAST, timestep_minutes, lat=lat, lon=lon)
    return await _send_request(params)


async def request_forecast_by_place(place: str, timestep_hours: int = 24) -> str:
    """
    Get the latest forecast by place name

    :param place: Place name (e.g. Kaisaniemi,Helsinki)
    :param timestep_hours: Forecast steps in hours
    :return: Forecast response
    """
    timestep_minutes = timestep_hours * 60
    params = _create_params(RequestType.FORECAST, timestep_minutes, place=place)
    return await _send_request(params)


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


async def _send_request(params: Dict[str, Any]) -> str:
    """
    Send a request to FMI service and return the body
    :param params: Query parameters
    :return: Response body
    """
    url = 'http://opendata.fmi.fi/wfs'

    _LOGGER.debug("GET request to %s. Parameters: %s", url, params)
    response = await treq.get(url, params=params, timeout=10)

    if response.code == 200:
        _LOGGER.debug("GET response from %s. Status: %d.", url, response.code)
    else:
        await _handle_errors(response)

    return await response.text()


async def _handle_errors(response):
    """Handle error responses from FMI service"""
    if 400 <= response.code < 500:
        data = xmltodict.parse(await response.text())
        try:
            error_message = data['ExceptionReport']['Exception']['ExceptionText'][0]
            raise ClientError(response.code, error_message)
        except (KeyError, IndexError) as err:
            raise ClientError(response.code, await response.text()) from err

    raise ServerError(response.code, await response.text())
```

### Key Notes
- All functions that call `_send_request` are now asynchronous (`async def`) and must be awaited when called.
- The `treq` library requires an asynchronous runtime (e.g., `Twisted` or `asyncio`) to execute the code.