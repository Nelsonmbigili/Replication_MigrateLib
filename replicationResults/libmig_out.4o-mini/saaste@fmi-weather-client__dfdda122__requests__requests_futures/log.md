## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/saaste@fmi-weather-client__dfdda122__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating fmi_weather_client/http.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/test_http.py::HTTPTest::test_create_params_invalid_request_type: passed != not found`
- `test/test_http.py::HTTPTest::test_create_params_missing_location: passed != not found`
- `test/test_http.py::HTTPTest::test_handle_errors_client_error_with_exception_text: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_async_get_forecast_by_coordinates: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_async_get_forecast_by_place_name: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_async_get_weather_by_coordinates: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_async_get_weather_by_place: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_get_forecast_by_coordinates: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_get_forecast_by_place_name: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_get_weather_by_coordinates: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_get_weather_by_place: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_invalid_lat_lon_exception_response: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_nil_forecast_response: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_nil_weather_response: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_no_data_available_exception_response: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_no_location_exception_response: passed != not found`
- `test/test_init.py::FMIWeatherTest::test_server_error_response: passed != not found`
- `test/test_models.py::ModelsTest::test_fmi_place: passed != not found`
- `test/test_models.py::ModelsTest::test_value: passed != not found`
- `test/test_parsers_forecast.py::ForecastParserTest::test_feels_like: passed != not found`
- `test/test_parsers_forecast.py::ForecastParserTest::test_float_or_none: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
