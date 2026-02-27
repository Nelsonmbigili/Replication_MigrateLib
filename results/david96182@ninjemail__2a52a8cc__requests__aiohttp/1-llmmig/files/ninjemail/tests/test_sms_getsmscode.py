import re
import pytest
from unittest.mock import AsyncMock, patch
import aiohttp
from ..sms_services.getsmscode import GetsmsCode, APIError

# Mocking aiohttp.ClientSession.post
@pytest.fixture
def mock_aiohttp_post(mocker):
    mock = mocker.patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
    mock.return_value.__aenter__.return_value.raise_for_status.return_value = None
    mock.return_value.__aenter__.return_value.text = "Success"
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

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_request(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.raise_for_status.return_value = None
    mock_post.return_value.__aenter__.return_value.text = "Success"
    response = await gs.request(action="getmobile")
    assert response == "Success"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_get_phone(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.raise_for_status.return_value = None
    mock_post.return_value.__aenter__.return_value.text = "234567"
    phone = await gs.get_phone()
    assert phone == "234567"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_get_phone_with_prefix(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.raise_for_status.return_value = None
    mock_post.return_value.__aenter__.return_value.text = "1234567"
    phone = await gs.get_phone(send_prefix=True)
    assert phone == "1234567"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_get_code(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.raise_for_status.return_value = None
    mock_post.return_value.__aenter__.return_value.text = "Success|12345"
    code = await gs.get_code("1234567")
    assert code == "12345"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_request_failure(mock_post, gs):
    mock_post.side_effect = aiohttp.ClientError("Network error")
    with pytest.raises(aiohttp.ClientError):
        await gs.request(action="getmobile")

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_api_error_response_message(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=None, history=None, status=400, message="Error|Invalid request"
    )
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        await gs.request(action="getmobile")
    assert str(exc_info.value) == "400, message='Error|Invalid request'"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_no_code_found(mock_post, gs):
    mock_post.return_value.__aenter__.return_value.text = "Success|"
    with pytest.raises(AssertionError):
        await gs.get_code("1234567")

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
async def test_request_timeout(mock_post, gs):
    mock_post.side_effect = aiohttp.ClientTimeout()
    with pytest.raises(aiohttp.ClientTimeout):
        await gs.request(action="getmobile")
