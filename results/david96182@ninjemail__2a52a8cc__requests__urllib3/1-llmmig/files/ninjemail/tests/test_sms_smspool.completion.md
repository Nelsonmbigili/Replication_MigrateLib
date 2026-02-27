### Explanation of Changes

To migrate the code from using the `requests` library to `urllib3`, the following changes were made:

1. **Replaced `requests.post` with `urllib3.PoolManager.request`**:
   - The `requests.post` method was replaced with `urllib3.PoolManager.request` for making HTTP POST requests.
   - `urllib3` requires explicitly specifying the HTTP method (e.g., `POST`) and passing parameters as `fields` for query parameters or `body` for request bodies.

2. **Mocking `urllib3.PoolManager.request`**:
   - The `requests.post` mock was replaced with a mock for `urllib3.PoolManager.request`.
   - The `return_value` of the mock was updated to simulate the behavior of `urllib3` responses, which use `data` instead of `json()` for response content.

3. **Response Handling**:
   - `urllib3` responses return raw bytes in the `data` attribute. These were decoded to strings and parsed as JSON using `json.loads`.

4. **Error Handling**:
   - `requests.exceptions.HTTPError` was replaced with `urllib3.exceptions.HTTPError` for exception handling.

5. **Updated Test Fixtures**:
   - The `mock_requests_post` fixture was updated to mock `urllib3.PoolManager.request` instead of `requests.post`.

### Modified Code

```python
import pytest
import json
from unittest.mock import MagicMock, patch
import urllib3
from urllib3.exceptions import HTTPError

from ..sms_services.smspool import SMSPool, APIError

# Mocking urllib3.PoolManager.request
@pytest.fixture
def mock_urllib3_request(mocker):
    mock = mocker.patch("urllib3.PoolManager.request")
    mock.return_value.status = 200
    mock.return_value.data = json.dumps({"success": True}).encode("utf-8")
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of SMSPool
@pytest.fixture
def sms_pool():
    return SMSPool(service="service_id", token="api_key", country="hk")

def test_request_success(mock_urllib3_request, sms_pool):
    response = sms_pool.request("some_command")
    assert response == {"success": True}
    mock_urllib3_request.assert_called_once_with(
        "POST",
        "http://api.smspool.net/some_command",
        fields={"key": "api_key"}
    )

def test_request_failure(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.status = 400
    mock_urllib3_request.side_effect = HTTPError
    with pytest.raises(HTTPError):
        sms_pool.request("some_command")

def test_get_phone(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.data = json.dumps({
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890", 
        "order_id": "order123"
    }).encode("utf-8")
    phone, order_id = sms_pool.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.data = json.dumps({
        "success": True,
        "sms": "12345"
    }).encode("utf-8")
    code = sms_pool.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.data = json.dumps({
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890",
        "order_id": "order123"
    }).encode("utf-8")
    phone, order_id = sms_pool.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.data = json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8")
    with pytest.raises(APIError) as exc_info:
        sms_pool.request("some_command")
    assert str(exc_info.value) == "Error message"

def test_get_phone_error_response(mock_urllib3_request, sms_pool):
    mock_urllib3_request.return_value.data = json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8")
    with pytest.raises(APIError) as exc_info:
        sms_pool.get_phone()
    assert str(exc_info.value) == "Error message"

def test_get_code_error_response(mock_urllib3_request, mock_time_sleep, sms_pool):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_urllib3_request.return_value.data = json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8")
    with pytest.raises(Exception) as exc_info:
        sms_pool.get_code("order123")
    assert str(exc_info.value) == "Test exception"
```

### Key Notes:
- The `urllib3.PoolManager.request` method is used for all HTTP requests.
- The `fields` parameter is used to pass query parameters (equivalent to `params` in `requests`).
- The `data` attribute of the response is decoded and parsed as JSON using `json.loads`.
- Exceptions are updated to use `urllib3.exceptions.HTTPError`.