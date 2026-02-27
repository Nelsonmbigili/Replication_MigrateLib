import re
import pytest
from unittest.mock import MagicMock, patch
import urllib3
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking urllib3.PoolManager.request
@pytest.fixture
def mock_urllib3_request(mocker):
    mock = mocker.patch("urllib3.PoolManager.request")
    mock.return_value.status = 200
    mock.return_value.data = b"Success"
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

@patch("urllib3.PoolManager.request")
def test_request(mock_request, gs):
    mock_request.return_value.status = 200
    mock_request.return_value.data = b"Success"
    response = gs.request(action="getmobile")
    assert response == "Success"

@patch("urllib3.PoolManager.request")
def test_get_phone(mock_request, gs):
    mock_request.return_value.status = 200
    mock_request.return_value.data = b"234567"
    phone = gs.get_phone()
    assert phone == "234567"

@patch("urllib3.PoolManager.request")
def test_get_phone_with_prefix(mock_request, gs):
    mock_request.return_value.status = 200
    mock_request.return_value.data = b"1234567"
    phone = gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@patch("urllib3.PoolManager.request")
def test_get_code(mock_request, gs):
    mock_request.return_value.status = 200
    mock_request.return_value.data = b"Success|12345"
    code = gs.get_code("1234567")
    assert code == "12345"

@patch("urllib3.PoolManager.request")
def test_request_failure(mock_request, gs):
    mock_request.side_effect = urllib3.exceptions.RequestError("Network error")
    with pytest.raises(urllib3.exceptions.RequestError):
        gs.request(action="getmobile")

@patch("urllib3.PoolManager.request")
def test_api_error_response_message(mock_request, gs):
    mock_request.return_value.status = 400
    mock_request.return_value.data = b"Error|Invalid request"
    with pytest.raises(urllib3.exceptions.HTTPError) as exc_info:
        gs.request(action="getmobile")
    assert str(exc_info.value) == ""

@patch("urllib3.PoolManager.request")
def test_no_code_found(mock_request, gs):
    mock_request.return_value.status = 200
    mock_request.return_value.data = b"Success|"
    with pytest.raises(AssertionError):
        gs.get_code("1234567")

@patch("urllib3.PoolManager.request")
def test_request_timeout(mock_request, gs):
    mock_request.side_effect = urllib3.exceptions.TimeoutError()
    with pytest.raises(urllib3.exceptions.TimeoutError):
        gs.request(action="getmobile")
