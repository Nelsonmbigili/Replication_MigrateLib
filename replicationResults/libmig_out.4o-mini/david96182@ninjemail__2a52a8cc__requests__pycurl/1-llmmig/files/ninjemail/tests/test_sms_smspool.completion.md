### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Importing `pycurl`**: The `requests` library was replaced with `pycurl`.
2. **Mocking `pycurl`**: The mocking of `requests.post` was changed to mock the behavior of `pycurl` for making HTTP requests.
3. **Handling Responses**: The way responses are handled changed from using `response.json()` to manually parsing the response from `pycurl`.
4. **Error Handling**: The error handling for HTTP errors was adjusted to reflect how `pycurl` raises exceptions.

The overall structure of the tests remains the same, but the underlying implementation details were updated to accommodate the differences between `requests` and `pycurl`.

### Modified Code

```python
import pytest
import pycurl
from unittest.mock import MagicMock, patch
from io import BytesIO

from ..sms_services.smspool import SMSPool, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_pycurl(mocker):
    mock = mocker.patch("pycurl.Curl")
    mock.return_value.perform.return_value = None
    mock.return_value.getinfo.return_value = 200  # Simulate HTTP status code
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of SMSPool
@pytest.fixture
def sms_pool():
    return SMSPool(service="service_id", token="api_key", country="hk")

def test_request_success(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_pycurl.return_value.perform.side_effect = lambda: mock_response.write(b'{"success": true}')
    mock_pycurl.return_value.getinfo.return_value = 200
    response = sms_pool.request("some_command")
    assert response == {"success": True}
    mock_pycurl.assert_called_once_with(
        "http://api.smspool.net/some_command",
        params={"key": "api_key"}
    )

def test_request_failure(mock_pycurl, sms_pool):
    mock_pycurl.return_value.perform.side_effect = pycurl.error(400)
    with pytest.raises(pycurl.error):
        sms_pool.request("some_command")

def test_get_phone(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_pycurl.return_value.perform.side_effect = lambda: mock_response.write(b'{"success": true, "number": "1234567890", "phonenumber": "234567890", "order_id": "order123"}')
    phone, order_id = sms_pool.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_pycurl.return_value.perform.side_effect = lambda: mock_response.write(b'{"success": true, "sms": "12345"}')
    code = sms_pool.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_pycurl.return_value.perform.side_effect = lambda: mock_response.write(b'{"success": true, "number": "1234567890", "phonenumber": "234567890", "order_id": "order123"}')
    phone, order_id = sms_pool.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_response.write(b'{"success": false, "message": "Error message"}')
    with pytest.raises(APIError) as exc_info:
        sms_pool.request("some_command")
    assert str(exc_info.value) == "Error message"

def test_get_phone_error_response(mock_pycurl, sms_pool):
    mock_response = BytesIO()
    mock_response.write(b'{"success": false, "message": "Error message"}')
    with pytest.raises(APIError) as exc_info:
        sms_pool.get_phone()
    assert str(exc_info.value) == "Error message"

def test_get_code_error_response(mock_pycurl, mock_time_sleep, sms_pool):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_response = BytesIO()
    mock_response.write(b'{"success": false, "message": "Error message"}')
    with pytest.raises(Exception) as exc_info:
        sms_pool.get_code("order123")
    assert str(exc_info.value) == "Test exception"
``` 

This modified code now uses `pycurl` for HTTP requests while maintaining the original structure and logic of the tests.