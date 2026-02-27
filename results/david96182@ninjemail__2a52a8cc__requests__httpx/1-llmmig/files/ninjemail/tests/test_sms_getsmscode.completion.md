### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. **Import Changes**: Replaced `requests` with `httpx` where necessary.
2. **Mocking Changes**: Updated the `@patch` decorators and `mock_requests_post` fixture to mock `httpx.post` instead of `requests.post`.
3. **Exception Handling**: Updated exception classes from `requests.exceptions` to `httpx` equivalents (e.g., `httpx.RequestError`, `httpx.HTTPStatusError`, `httpx.TimeoutException`).
4. **Method Calls**: Adjusted method calls to align with `httpx`'s API, which is similar to `requests` but has slight differences in exception handling and behavior.

### Modified Code
```python
import re
import pytest
from unittest.mock import MagicMock, patch
import httpx
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking httpx.post
@pytest.fixture
def mock_requests_post(mocker):
    mock = mocker.patch("httpx.post")
    mock.return_value.raise_for_status.return_value = None
    mock.return_value.text = "Success"
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of GetsmsCode
@pytest.fixture
def gs():
    return GetsmsCode(project="123", user="user", token="token", country="us")

def test_initialization(gs):
    assert gs.user == "user"
    assert gs.token == "token"
    assert gs.project == "123"
    assert gs.country == "us"
    assert gs.prefix == "1"
    assert gs.API_URL == "http://api.getsmscode.com/usdo.php"

def test_generate_generic(gs):
    phone = gs._generate_generic()
    assert phone.startswith("52")
    assert len(phone) == 8

def test_get_endpoint(gs):
    assert gs.get_endpoint("us") == "usdo"
    assert gs.get_endpoint("hk") == "vndo"
    assert gs.get_endpoint("cn") == "do"

@patch("httpx.post")
def test_request(mock_post, gs):
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.text = "Success"
    response = gs.request(action="getmobile")
    assert response == "Success"

@patch("httpx.post")
def test_get_phone(mock_post, gs):
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.text = "234567"
    phone = gs.get_phone()
    assert phone == "234567"

@patch("httpx.post")
def test_get_phone_with_prefix(mock_post, gs):
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.text = "1234567"
    phone = gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@patch("httpx.post")
def test_get_code(mock_post, gs):
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.text = "Success|12345"
    code = gs.get_code("1234567")
    assert code == "12345"

@patch("httpx.post")
def test_request_failure(mock_post, gs):
    mock_post.side_effect = httpx.RequestError("Network error")
    with pytest.raises(httpx.RequestError):
        gs.request(action="getmobile")

@patch("httpx.post")
def test_api_error_response_message(mock_post, gs):
    mock_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError("HTTP error")
    mock_post.return_value.text = "Error|Invalid request"
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        gs.request(action="getmobile")
    assert str(exc_info.value) == "HTTP error"

@patch("httpx.post")
def test_no_code_found(mock_post, gs):
    mock_post.return_value.text = "Success|"
    with pytest.raises(AssertionError):
        gs.get_code("1234567")

@patch("httpx.post")
def test_request_timeout(mock_post, gs):
    mock_post.side_effect = httpx.TimeoutException()
    with pytest.raises(httpx.TimeoutException):
        gs.request(action="getmobile")
```

### Key Notes
- The `httpx` library is very similar to `requests`, so the migration primarily involved replacing `requests` with `httpx` and updating exception classes.
- The `httpx` exceptions used are:
  - `httpx.RequestError` (equivalent to `requests.exceptions.RequestException`)
  - `httpx.HTTPStatusError` (equivalent to `requests.exceptions.HTTPError`)
  - `httpx.TimeoutException` (equivalent to `requests.exceptions.Timeout`)
- The `mock_requests_post` fixture and `@patch` decorators now mock `httpx.post` instead of `requests.post`.