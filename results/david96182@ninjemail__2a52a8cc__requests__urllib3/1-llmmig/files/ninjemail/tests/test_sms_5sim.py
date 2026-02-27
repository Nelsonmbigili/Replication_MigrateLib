import pytest
import urllib3
import json

from ..sms_services.fivesim import FiveSim, APIError

# Mocking urllib3.PoolManager().request
@pytest.fixture
def mock_urllib3_request(mocker):
    mock = mocker.patch("urllib3.PoolManager.request")
    mock.return_value.status = 200
    mock.return_value.data = json.dumps({"success": True}).encode('utf-8')
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of FiveSim
@pytest.fixture
def fivesim():
    return FiveSim(service="service_id", token="api_key", country="usa")

def test_request_success(mock_urllib3_request, fivesim):
    response = fivesim.request("some_command")
    assert response == {"success": True}
    mock_urllib3_request.assert_called_once_with(
        "GET",
        "https://5sim.net/v1/user/some_command",
        headers={
            'Authorization': 'Bearer ' + 'api_key',
        }
    )

def test_request_failure(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.status = 400
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.data = json.dumps({
        "phone": "+1234567890",
        "id": "order123"
    }).encode('utf-8')
    phone, order_id = fivesim.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.data = json.dumps({
        "sms": [{"code": "12345"}]
    }).encode('utf-8')
    code = fivesim.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.data = json.dumps({
        "phone": "+1234567890",
        "id": "order123"
    }).encode('utf-8')
    phone, order_id = fivesim.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.status = 400
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone_error_response(mock_urllib3_request, fivesim):
    mock_urllib3_request.return_value.status = 400
    with pytest.raises(APIError):
        fivesim.get_phone()

def test_request_error_no_free_phones(mock_urllib3_request, fivesim):
    mock_response = mock_urllib3_request.return_value
    mock_response.data = "no free phones".encode('utf-8')

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_phone')
    assert str(exc_info.value) == '5Sim has no free phones'

def test_request_error_not_enough_balance(mock_urllib3_request, fivesim):
    mock_response = mock_urllib3_request.return_value
    mock_response.data = "not enough user balance".encode('utf-8')

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_balance')
    assert str(exc_info.value) == 'Not enough balance'

def test_get_code_error_response(mock_urllib3_request, mock_time_sleep, fivesim):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_urllib3_request.return_value.data = json.dumps({
        "status": "CANCELLED",
        "sms": []
    }).encode('utf-8')
    with pytest.raises(Exception) as exc_info:
        fivesim.get_code("order123")
    assert str(exc_info.value) == "Test exception"
