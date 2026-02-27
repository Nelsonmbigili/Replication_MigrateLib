import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from ..sms_services.smspool import SMSPool, APIError

# Mocking treq.post
@pytest.fixture
def mock_treq_post(mocker):
    mock = mocker.patch("treq.post", new_callable=AsyncMock)
    mock.return_value.json = AsyncMock(return_value={"success": True})
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of SMSPool
@pytest.fixture
def sms_pool():
    return SMSPool(service="service_id", token="api_key", country="hk")

@pytest.mark.asyncio
async def test_request_success(mock_treq_post, sms_pool):
    response = await sms_pool.request("some_command")
    assert response == {"success": True}
    mock_treq_post.assert_called_once_with(
        "http://api.smspool.net/some_command",
        params={"key": "api_key"}
    )

@pytest.mark.asyncio
async def test_request_failure(mock_treq_post, sms_pool):
    mock_treq_post.side_effect = Exception("HTTP Error")
    with pytest.raises(Exception, match="HTTP Error"):
        await sms_pool.request("some_command")

@pytest.mark.asyncio
async def test_get_phone(mock_treq_post, sms_pool):
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890", 
        "order_id": "order123"
    })
    phone, order_id = await sms_pool.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_get_code(mock_treq_post, sms_pool):
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": True,
        "sms": "12345"
    })
    code = await sms_pool.get_code("order123")
    assert code == "12345"

@pytest.mark.asyncio
async def test_get_phone_with_prefix(mock_treq_post, sms_pool):
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890",
        "order_id": "order123"
    })
    phone, order_id = await sms_pool.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_request_error_response(mock_treq_post, sms_pool):
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": False,
        "message": "Error message"
    })
    with pytest.raises(APIError) as exc_info:
        await sms_pool.request("some_command")
    assert str(exc_info.value) == "Error message"

@pytest.mark.asyncio
async def test_get_phone_error_response(mock_treq_post, sms_pool):
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": False,
        "message": "Error message"
    })
    with pytest.raises(APIError) as exc_info:
        await sms_pool.get_phone()
    assert str(exc_info.value) == "Error message"

@pytest.mark.asyncio
async def test_get_code_error_response(mock_treq_post, mock_time_sleep, sms_pool):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_treq_post.return_value.json = AsyncMock(return_value={
        "success": False,
        "message": "Error message"
    })
    with pytest.raises(Exception) as exc_info:
        await sms_pool.get_code("order123")
    assert str(exc_info.value) == "Test exception"
