The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "requests_futures" version 1.0.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "requests_futures".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "requests_futures".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import pytest
import requests
from unittest.mock import MagicMock, patch

from ..sms_services.smspool import SMSPool, APIError

# Mocking requests.post
@pytest.fixture
def mock_requests_post(mocker):
    mock = mocker.patch("requests.post")
    mock.return_value.raise_for_status.return_value = None
    mock.return_value.json.return_value = {"success": True}
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of SMSPool
@pytest.fixture
def sms_pool():
    return SMSPool(service="service_id", token="api_key", country="hk")

def test_request_success(mock_requests_post, sms_pool):
    response = sms_pool.request("some_command")
    assert response == {"success": True}
    mock_requests_post.assert_called_once_with(
        "http://api.smspool.net/some_command",
        params={"key": "api_key"}
    )

def test_request_failure(mock_requests_post, sms_pool):
    mock_requests_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        sms_pool.request("some_command")

def test_get_phone(mock_requests_post, sms_pool):
    mock_requests_post.return_value.json.return_value = {
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890", 
        "order_id": "order123"
    }
    phone, order_id = sms_pool.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_requests_post, sms_pool):
    mock_requests_post.return_value.json.return_value = {
        "success": True,
        "sms": "12345"
    }
    code = sms_pool.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_requests_post, sms_pool):
    mock_requests_post.return_value.json.return_value = {
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890",
        "order_id": "order123"
    }
    phone, order_id = sms_pool.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_requests_post, sms_pool):
    mock_requests_post.return_value.json.return_value = {
        "success": False,
        "message": "Error message"
    }
    with pytest.raises(APIError) as exc_info:
        sms_pool.request("some_command")
    assert str(exc_info.value) == "Error message"

def test_get_phone_error_response(mock_requests_post, sms_pool):
    mock_requests_post.return_value.json.return_value = {
        "success": False,
        "message": "Error message"
    }
    with pytest.raises(APIError) as exc_info:
        sms_pool.get_phone()
    assert str(exc_info.value) == "Error message"

def test_get_code_error_response(mock_requests_post, mock_time_sleep, sms_pool):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_requests_post.return_value.json.return_value = {
        "success": False,
        "message": "Error message"
    }
    with pytest.raises(Exception) as exc_info:
        sms_pool.get_code("order123")
    assert str(exc_info.value) == "Test exception"

```