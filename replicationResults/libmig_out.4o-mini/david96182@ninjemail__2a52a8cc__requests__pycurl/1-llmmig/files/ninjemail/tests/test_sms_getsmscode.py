import re
import pytest
from unittest.mock import MagicMock, patch
import pycurl
from io import BytesIO
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_pycurl(mocker):
    mock = mocker.patch("pycurl.Curl")
    mock.return_value.perform.return_value = None
    mock.return_value.getinfo.return_value = "Success"
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

@patch("pycurl.Curl")
def test_request(mock_curl, gs):
    mock_curl.return_value.perform.return_value = None
    mock_curl.return_value.getinfo.return_value = "Success"
    response = gs.request(action="getmobile")
    assert response == "Success"

@patch("pycurl.Curl")
def test_get_phone(mock_curl, gs):
    mock_curl.return_value.perform.return_value = None
    mock_curl.return_value.getinfo.return_value = "234567"
    phone = gs.get_phone()
    assert phone == "234567"

@patch("pycurl.Curl")
def test_get_phone_with_prefix(mock_curl, gs):
    mock_curl.return_value.perform.return_value = None
    mock_curl.return_value.getinfo.return_value = "1234567"
    phone = gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@patch("pycurl.Curl")
def test_get_code(mock_curl, gs):
    mock_curl.return_value.perform.return_value = None
    mock_curl.return_value.getinfo.return_value = "Success|12345"
    code = gs.get_code("1234567")
    assert code == "12345"

@patch("pycurl.Curl")
def test_request_failure(mock_curl, gs):
    mock_curl.side_effect = pycurl.error("Network error")
    with pytest.raises(pycurl.error):
        gs.request(action="getmobile")

@patch("pycurl.Curl")
def test_api_error_response_message(mock_curl, gs):
    mock_curl.return_value.perform.side_effect = pycurl.error()
    mock_curl.return_value.getinfo.return_value = "Error|Invalid request"
    with pytest.raises(pycurl.error) as exc_info:
        gs.request(action="getmobile")
    assert str(exc_info.value) == ""

@patch("pycurl.Curl")
def test_no_code_found(mock_curl, gs):
    mock_curl.return_value.getinfo.return_value = "Success|"
    with pytest.raises(AssertionError):
        gs.get_code("1234567")

@patch("pycurl.Curl")
def test_request_timeout(mock_curl, gs):
    mock_curl.side_effect = pycurl.error("Timeout")
    with pytest.raises(pycurl.error):
        gs.request(action="getmobile")
