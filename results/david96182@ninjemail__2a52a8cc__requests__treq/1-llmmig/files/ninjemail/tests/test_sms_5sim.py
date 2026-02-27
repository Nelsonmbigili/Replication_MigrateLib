import pytest
import treq
import asyncio
from pytest_asyncio import fixture

from ..sms_services.fivesim import FiveSim, APIError

# Mocking treq.get
@fixture
def mock_treq_get(mocker):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def json(self):
                return {"success": True}

            async def text(self):
                return "mocked text"

            async def raise_for_status(self):
                pass

        return MockResponse()

    mock = mocker.patch("treq.get", side_effect=mock_response)
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
async def test_request_success(mock_treq_get, fivesim):
    response = await fivesim.request("some_command")
    assert response == {"success": True}
    mock_treq_get.assert_called_once_with(
        "https://5sim.net/v1/user/some_command",
        headers={
            'Authorization': 'Bearer ' + 'api_key',
        }
    )

@pytest.mark.asyncio
async def test_request_failure(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def raise_for_status(self):
                raise Exception("HTTPError")

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(APIError):
        await fivesim.request("some_command")

@pytest.mark.asyncio
async def test_get_phone(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def json(self):
                return {"phone": "+1234567890", "id": "order123"}

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    phone, order_id = await fivesim.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_get_code(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def json(self):
                return {"sms": [{"code": "12345"}]}

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    code = await fivesim.get_code("order123")
    assert code == "12345"

@pytest.mark.asyncio
async def test_get_phone_with_prefix(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def json(self):
                return {"phone": "+1234567890", "id": "order123"}

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    phone, order_id = await fivesim.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

@pytest.mark.asyncio
async def test_request_error_response(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def raise_for_status(self):
                raise Exception("HTTPError")

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(APIError):
        await fivesim.request("some_command")

@pytest.mark.asyncio
async def test_get_phone_error_response(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def raise_for_status(self):
                raise Exception("HTTPError")

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(APIError):
        await fivesim.get_phone()

@pytest.mark.asyncio
async def test_request_error_no_free_phones(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def text(self):
                return "no free phones"

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(APIError) as exc_info:
        await fivesim.request('no_phone')
    assert str(exc_info.value) == '5Sim has no free phones'

@pytest.mark.asyncio
async def test_request_error_not_enough_balance(mock_treq_get, fivesim):
    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def text(self):
                return "not enough user balance"

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(APIError) as exc_info:
        await fivesim.request('no_balance')
    assert str(exc_info.value) == 'Not enough balance'

@pytest.mark.asyncio
async def test_get_code_error_response(mock_treq_get, mock_time_sleep, fivesim):
    mock_time_sleep.side_effect = Exception("Test exception")

    async def mock_response(*args, **kwargs):
        class MockResponse:
            async def json(self):
                return {"status": "CANCELLED", "sms": []}

        return MockResponse()

    mock_treq_get.side_effect = mock_response
    with pytest.raises(Exception) as exc_info:
        await fivesim.get_code("order123")
    assert str(exc_info.value) == "Test exception"
