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
