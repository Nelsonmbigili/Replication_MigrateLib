### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. The `requests` library's methods for making HTTP requests were replaced with equivalent `pycurl` methods.
  
2. **Making Requests**: The `requests.get` method was replaced with `pycurl.Curl()`, which requires setting options for the URL, headers, and handling the response differently.

3. **Handling Responses**: The response handling was modified to read the response data from a buffer instead of using the `json()` method from `requests`. A `BytesIO` buffer was used to capture the response data.

4. **Error Handling**: The error handling was adjusted to check for HTTP errors using `pycurl`'s error codes instead of raising exceptions directly from the response.

5. **Mocking**: The mocking of requests was updated to reflect the changes in how `pycurl` operates, particularly in how responses and errors are simulated.

Here is the modified code:

```python
import pytest
import pycurl
from io import BytesIO

from ..sms_services.fivesim import FiveSim, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch("pycurl.Curl")
    mock.return_value.perform.side_effect = None
    mock.return_value.getinfo.return_value = 200
    mock.return_value.response_buffer = BytesIO()
    mock.return_value.response_buffer.write(b'{"success": true}')
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of FiveSim
@pytest.fixture
def fivesim():
    return FiveSim(service="service_id", token="api_key", country="usa")

def test_request_success(mock_requests_get, fivesim):
    response = fivesim.request("some_command")
    assert response == {"success": True}
    mock_requests_get.assert_called_once()
    assert mock_requests_get.call_args[0][0].url == "https://5sim.net/v1/user/some_command"
    assert mock_requests_get.call_args[0][0].headers == {
        'Authorization': 'Bearer ' + 'api_key',
    }

def test_request_failure(mock_requests_get, fivesim):
    mock_requests_get.return_value.perform.side_effect = pycurl.error(400)
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone(mock_requests_get, fivesim):
    mock_requests_get.return_value.response_buffer.write(b'{"phone": "+1234567890", "id": "order123"}')
    phone, order_id = fivesim.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_requests_get, fivesim):
    mock_requests_get.return_value.response_buffer.write(b'{"sms": [{"code" :"12345"}]}')
    code = fivesim.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_requests_get, fivesim):
    mock_requests_get.return_value.response_buffer.write(b'{"phone": "+1234567890", "id": "order123"}')
    phone, order_id = fivesim.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_requests_get, fivesim):
    mock_requests_get.return_value.perform.side_effect = pycurl.error(400)
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone_error_response(mock_requests_get, fivesim):
    mock_requests_get.return_value.perform.side_effect = pycurl.error(400)

    with pytest.raises(APIError):
        fivesim.get_phone()

def test_request_error_no_free_phones(mock_requests_get, fivesim):
    mock_requests_get.return_value.response_buffer.write(b'no free phones')
    mock_requests_get.return_value.perform.side_effect = None

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_phone')
    assert str(exc_info.value) == '5Sim has no free phones'

def test_request_error_not_enough_balance(mock_requests_get, fivesim):
    mock_requests_get.return_value.response_buffer.write(b'not enough user balance')
    mock_requests_get.return_value.perform.side_effect = None

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_balance')
    assert str(exc_info.value) == 'Not enough balance'

def test_get_code_error_response(mock_requests_get, mock_time_sleep, fivesim):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_requests_get.return_value.response_buffer.write(b'{"status": "CANCELLED", "sms": []}')
    with pytest.raises(Exception) as exc_info:
        fivesim.get_code("order123")
    assert str(exc_info.value) == "Test exception"
```

This code now uses `pycurl` for HTTP requests while maintaining the original structure and functionality of the tests.