### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl` for HTTP GET requests**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with options such as the URL, query parameters, and timeout.
   - The response body is captured using a `BytesIO` buffer.
2. **Modified `_send_request`**:
   - Replaced the `requests.get` call with `pycurl` logic to handle the HTTP request.
   - Used `pycurl` options to set the URL, query parameters, and timeout.
   - Captured the response body and HTTP status code using `pycurl`.
3. **Modified `_handle_errors`**:
   - Updated the function to accept the raw response body and status code instead of a `requests.Response` object.
   - Parsed the response body using `xmltodict` as before.
4. **Removed `requests` imports**:
   - Removed the `requests` import since it is no longer used.

### Modified Code
Below is the complete code after migrating to `pycurl`:

```python
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional
import pycurl
from io import BytesIO
import xmltodict

from fmi_weather_client.errors import ClientError, ServerError

_LOGGER = logging.getLogger(__name__)


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
    query_string = '&'.join(f"{key}={value}" for key, value in params.items())
    full_url = f"{url}?{query_string}"

    _LOGGER.debug("GET request to %s. Parameters: %s", url, params)

    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, full_url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.setopt(pycurl.TIMEOUT, 10)

    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_time = curl.getinfo(pycurl.TOTAL_TIME) * 1000  # Convert to ms
        _LOGGER.debug("GET response from %s in %.2f ms. Status: %d.",
                      url, response_time, status_code)
    finally:
        curl.close()

    response_body = buffer.getvalue().decode('utf-8')

    if status_code == 200:
        return response_body
    else:
        _handle_errors(response_body, status_code)


def _handle_errors(response_body: str, status_code: int):
    """Handle error responses from FMI service"""
    if 400 <= status_code < 500:
        data = xmltodict.parse(response_body)
        try:
            error_message = data['ExceptionReport']['Exception']['ExceptionText'][0]
            raise ClientError(status_code, error_message)
        except (KeyError, IndexError) as err:
            raise ClientError(status_code, response_body) from err

    raise ServerError(status_code, response_body)
```

### Key Notes
- The `pycurl` library requires more manual setup compared to `requests`, but it is highly efficient for low-level HTTP operations.
- The `_send_request` function now constructs the full URL with query parameters manually and uses `pycurl` to perform the request.
- The `_handle_errors` function was updated to work with the raw response body and status code instead of a `requests.Response` object.