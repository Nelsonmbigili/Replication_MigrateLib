### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was replaced with `requests_futures.sessions`.
2. **Session Creation**: Instead of using `requests.post`, we now create a `FuturesSession` object from `requests_futures.sessions` and use it to make asynchronous requests.
3. **Handling Responses**: Since `requests_futures` allows for asynchronous requests, we need to call `.result()` on the future object returned by the `post` method to get the actual response.

The overall structure of the code remains the same, but the way requests are made and handled has been updated to accommodate the asynchronous nature of `requests_futures`.

### Modified Code
```python
import re
import pytest
from unittest.mock import MagicMock, patch
from requests_futures.sessions import FuturesSession
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking requests_futures.sessions.FuturesSession.post
@pytest.fixture
def mock_requests_post(mocker):
    mock = mocker.patch("requests_futures.sessions.FuturesSession.post")
    mock.return_value.result.return_value.raise_for_status.return_value = None
    mock.return_value.result.return_value.text = "Success"
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

@patch("requests_futures.sessions.FuturesSession.post")
def test_request(mock_post, gs):
    mock_post.return_value.result.return_value.raise_for_status.return_value = None
    mock_post.return_value.result.return_value.text = "Success"
    response = gs.request(action="getmobile")
    assert response == "Success"

@patch("requests_futures.sessions.FuturesSession.post")
def test_get_phone(mock_post, gs):
    mock_post.return_value.result.return_value.raise_for_status.return_value = None
    mock_post.return_value.result.return_value.text = "234567"
    phone = gs.get_phone()
    assert phone == "234567"

@patch("requests_futures.sessions.FuturesSession.post")
def test_get_phone_with_prefix(mock_post, gs):
    mock_post.return_value.result.return_value.raise_for_status.return_value = None
    mock_post.return_value.result.return_value.text = "1234567"
    phone = gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@patch("requests_futures.sessions.FuturesSession.post")
def test_get_code(mock_post, gs):
    mock_post.return_value.result.return_value.raise_for_status.return_value = None
    mock_post.return_value.result.return_value.text = "Success|12345"
    code = gs.get_code("1234567")
    assert code == "12345"

@patch("requests_futures.sessions.FuturesSession.post")
def test_request_failure(mock_post, gs):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")
    with pytest.raises(requests.exceptions.RequestException):
        gs.request(action="getmobile")

@patch("requests_futures.sessions.FuturesSession.post")
def test_api_error_response_message(mock_post, gs):
    mock_post.return_value.result.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value.result.return_value.text = "Error|Invalid request"
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        gs.request(action="getmobile")
    assert str(exc_info.value) == ""

@patch("requests_futures.sessions.FuturesSession.post")
def test_no_code_found(mock_post, gs):
    mock_post.return_value.result.return_value.text = "Success|"
    with pytest.raises(AssertionError):
        gs.get_code("1234567")

@patch("requests_futures.sessions.FuturesSession.post")
def test_request_timeout(mock_post, gs):
    mock_post.side_effect = requests.exceptions.Timeout()
    with pytest.raises(requests.exceptions.Timeout):
        gs.request(action="getmobile")
```