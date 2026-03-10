### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp` for asynchronous HTTP requests.
2. **Asynchronous Functions**: The functions that make HTTP requests need to be defined as asynchronous (`async def`) and use `await` when calling the HTTP methods.
3. **Mocking Asynchronous Calls**: The mocking of the HTTP requests was adjusted to accommodate the asynchronous nature of `aiohttp`.
4. **Using `aiohttp.ClientSession`**: Instead of directly calling `requests.get`, we create an instance of `aiohttp.ClientSession` to manage the session and make requests.
5. **Handling Responses**: The response handling was updated to use `await response.json()` to retrieve the JSON data from the response.

Here is the modified code:

```python
import pytest
import aiohttp
from unittest.mock import AsyncMock

from ..sms_services.fivesim import FiveSim, APIError

# Mocking aiohttp.ClientSession.get
@pytest.fixture
def mock_aiohttp_get(mocker):
    mock = mocker.patch("aiohttp.ClientSession.get", new_callable=AsyncMock)
    mock.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
    mock.return_value.__aenter__.return_value.json = AsyncMock(return_value={"success": True})
    return mock

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of FiveSim
@pytest.fixture
def fivesim():
    return FiveSim(service="service_id", token="api_key", country="usa")

@pytest.mark.asyncio
async def test_request_success(mock_aiohttp_get, fivesim):
    response = await fivesim.request("some_command")
    assert response == {"success": True}
    mock_aiohttp_get.assert_called_once_with(
        "https://5sim.net/v1/user/some_command",
        headers = {
                'Authorization': 'Bearer ' + 'api_key',
                }
    )

@pytest.mark.asyncio
async def test_request_failure(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.raise_for_status.side_effect = aiohttp.ClientError
    with pytest.raises(APIError):
        await fivesim.request("some_command")

@pytest.mark.asyncio
async def test_get_phone(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.json.return_value = {
        "phone": "+1234567890",
        "id": "order123"
    }
    phone, order_id = await fivesim.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_get_code(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.json.return_value = {
        "sms": [{"code" :"12345"}]
    }
    code = await fivesim.get_code("order123")
    assert code == "12345"

@pytest.mark.asyncio
async def test_get_phone_with_prefix(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.json.return_value = {
        "phone": "+1234567890",
        "id": "order123"
    }
    phone, order_id = await fivesim.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_request_error_response(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.raise_for_status.side_effect = aiohttp.ClientError
    with pytest.raises(APIError):
        await fivesim.request("some_command")

@pytest.mark.asyncio
async def test_get_phone_error_response(mock_aiohttp_get, fivesim):
    mock_aiohttp_get.return_value.__aenter__.return_value.raise_for_status.side_effect = aiohttp.ClientError

    with pytest.raises(APIError):
        await fivesim.get_phone()

@pytest.mark.asyncio
async def test_request_error_no_free_phones(mock_aiohttp_get, fivesim):
    mock_response = mock_aiohttp_get.return_value.__aenter__.return_value
    mock_response.text = "no free phones"

    with pytest.raises(APIError) as exc_info:
        await fivesim.request('no_phone')
    assert str(exc_info.value) == '5Sim has no free phones'

@pytest.mark.asyncio
async def test_request_error_not_enough_balance(mock_aiohttp_get, fivesim):
    mock_response = mock_aiohttp_get.return_value.__aenter__.return_value
    mock_response.text = "not enough user balance"

    with pytest.raises(APIError) as exc_info:
        await fivesim.request('no_balance')
    assert str(exc_info.value) == 'Not enough balance'

@pytest.mark.asyncio
async def test_get_code_error_response(mock_aiohttp_get, mock_time_sleep, fivesim):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_aiohttp_get.return_value.__aenter__.return_value.json.return_value = {
        "status": "CANCELLED",
        "sms": []
    }
    with pytest.raises(Exception) as exc_info:
        await fivesim.get_code("order123")
    assert str(exc_info.value) == "Test exception"
```

### Note
- The `@pytest.mark.asyncio` decorator is used to mark the test functions as asynchronous.
- The `AsyncMock` is used to mock asynchronous methods in the tests.