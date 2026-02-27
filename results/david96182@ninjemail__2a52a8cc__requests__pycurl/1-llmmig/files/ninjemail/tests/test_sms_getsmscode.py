import re
import pytest
from unittest.mock import MagicMock, patch
import pycurl
from io import BytesIO
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_pycurl_curl(mocker):
    mock = mocker.patch("pycurl.Curl")
    mock_instance = mock.return_value
    mock_instance.perform.return_value = None
    mock_instance.getinfo.return_value = 200
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
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"Success")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 200

    response = gs.request(action="getmobile")
    assert response == "Success"

@patch("pycurl.Curl")
def test_get_phone(mock_curl, gs):
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"234567")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 200

    phone = gs.get_phone()
    assert phone == "234567"

@patch("pycurl.Curl")
def test_get_phone_with_prefix(mock_curl, gs):
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"1234567")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 200

    phone = gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@patch("pycurl.Curl")
def test_get_code(mock_curl, gs):
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"Success|12345")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 200

    code = gs.get_code("1234567")
    assert code == "12345"

@patch("pycurl.Curl")
def test_request_failure(mock_curl, gs):
    mock_instance = mock_curl.return_value
    mock_instance.perform.side_effect = pycurl.error("Network error")
    with pytest.raises(pycurl.error):
        gs.request(action="getmobile")

@patch("pycurl.Curl")
def test_api_error_response_message(mock_curl, gs):
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"Error|Invalid request")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 400

    with pytest.raises(APIError) as exc_info:
        gs.request(action="getmobile")
    assert str(exc_info.value) == "Error|Invalid request"

@patch("pycurl.Curl")
def test_no_code_found(mock_curl, gs):
    mock_instance = mock_curl.return_value
    response_buffer = BytesIO()
    response_buffer.write(b"Success|")
    response_buffer.seek(0)
    mock_instance.perform.side_effect = lambda: response_buffer.seek(0)
    mock_instance.getinfo.return_value = 200

    with pytest.raises(AssertionError):
        gs.get_code("1234567")

@patch("pycurl.Curl")
def test_request_timeout(mock_curl, gs):
    mock_instance = mock_curl.return_value
    mock_instance.perform.side_effect = pycurl.error("Timeout")
    with pytest.raises(pycurl.error):
        gs.request(action="getmobile")
