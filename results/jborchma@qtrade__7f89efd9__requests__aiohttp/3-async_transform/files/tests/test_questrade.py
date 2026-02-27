"""Questrade test module
"""

from unittest import mock
import pytest
import aiohttp
from qtrade import Questrade

TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

VALID_ACCESS_TOKEN = {
    "access_token": "hunter2",
    "api_server": "https://questrade.api",
    "expires_in": 1234,
    "refresh_token": "hunter2",
    "token_type": "Bearer",
}

INVALID_ACCESS_TOKEN = {
    "access_token": "hunter3",
    "api_server": "https://questrade.api",
    "expires_in": 1234,
    "refresh_token": "hunter3",
}

# Other constants remain unchanged...

class MockResponse:
    """Class that includes json data and status code for request get results"""

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    async def json(self):
        """Method to return mocked json data"""
        return self.json_data

    def raise_for_status(self):
        """Method to raise Exceptions for certain returned statuses"""
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = "%s Client Error" % (self.status_code)

        elif 500 <= self.status_code < 600:
            http_error_msg = "%s Server Error" % (self.status_code)

        if http_error_msg:
            raise Exception(http_error_msg)


### Specific request responses ###

async def mocked_access_token_requests_get(*args, **kwargs):
    """mocking access token requests get method"""
    if args[0] == TOKEN_URL + "hunter2":
        return MockResponse(VALID_ACCESS_TOKEN, 200)
    elif args[0] == TOKEN_URL + "hunter3":
        return MockResponse(INVALID_ACCESS_TOKEN, 200)
    else:
        return MockResponse(None, 404)


async def mocked_acct_id_get(*args, **kwargs):
    """mocking acct_id requests get"""
    if args[1] == "http://www.api_url.com/v1/accounts":
        return MockResponse(ACCOUNT_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_positions_get(*args, **kwargs):
    """mocking acct_id requests get"""
    if args[1] == "http://www.api_url.com/v1/accounts/123/positions":
        return MockResponse(POSITION_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_balances_get(*args, **kwargs):
    """mocking acct_id requests get"""
    if args[1] == "http://www.api_url.com/v1/accounts/123/balances":
        return MockResponse(BALANCE_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_activities_get(*args, **kwargs):
    """mocking activities requests get"""
    if args[1] == "http://www.api_url.com/v1/accounts/123/activities" and kwargs["params"] == {
        "endTime": "2018-08-10T00:00:00-05:00",
        "startTime": "2018-08-07T00:00:00-05:00",
    }:
        return MockResponse(ACTIVITY_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_executions_get(*args, **kwargs):
    """mocking executions requests get"""
    if args[1] == "http://www.api_url.com/v1/accounts/123/executions" and kwargs["params"] == {
        "endTime": "2018-08-10T00:00:00-05:00",
        "startTime": "2018-08-07T00:00:00-05:00",
    }:
        return MockResponse(EXECUTION_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_ticker_get(*args, **kwargs):
    """mocking ticker info requests get"""
    if args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {"names": "XYZ"}:
        return MockResponse(TICKER_RESPONSE_SINGLE, 200)
    elif args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {
        "names": "XYZ,ABC"
    }:
        return MockResponse(TICKER_RESPONSE_MULTIPLE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_quote_get(*args, **kwargs):
    """mocking quote requests get"""
    if args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {"names": "XYZ"}:
        return MockResponse(TICKER_RESPONSE_SINGLE, 200)
    elif args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {
        "names": "XYZ,ABC"
    }:
        return MockResponse(TICKER_RESPONSE_MULTIPLE, 200)
    if args[1] == "http://www.api_url.com/v1/markets/quotes" and kwargs["params"] == {
        "ids": "1234567"
    }:
        return MockResponse(QUOTE_RESPONSE_SINGLE, 200)
    elif args[1] == "http://www.api_url.com/v1/markets/quotes" and kwargs["params"] == {
        "ids": "1234567,1234567"
    }:
        return MockResponse(QUOTE_RESPONSE_MULTIPLE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_historical_get(*args, **kwargs):
    """mocking historical data requests get"""
    if args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {"names": "XYZ"}:
        return MockResponse(TICKER_RESPONSE_SINGLE, 200)
    if args[1] == "http://www.api_url.com/v1/markets/candles/1234567" and kwargs["params"] == {
        "startTime": "2018-08-01T00:00:00-05:00",
        "interval": "OneDay",
        "endTime": "2018-08-02T00:00:00-05:00",
    }:
        return MockResponse(HIST_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


async def mocked_option_chain_get(*args, **kwargs):
    """mocking option chain requests get"""
    if args[1] == "http://www.api_url.com/v1/symbols" and kwargs["params"] == {"names": "XYZ"}:
        return MockResponse(TICKER_RESPONSE_SINGLE, 200)
    if args[1] == "http://www.api_url.com/v1/symbols/1234567/options":
        return MockResponse(OPTIONS_CHAIN_RESPONSE, 200)
    else:
        return MockResponse(None, 404)


### TEST FUNCTIONS ###

@pytest.mark.asyncio
@mock.patch("qtrade.questrade.aiohttp.ClientSession.get", side_effect=mocked_access_token_requests_get)
async def test_del_method_session_close(mock_get):
    """ "This function tests the successful session closing."""
    with mock.patch.object(aiohttp.ClientSession, "close") as mock_close:
        qtrade = Questrade(access_code="hunter2")
        await qtrade.__del__()
        mock_close.assert_called_once()


@pytest.mark.asyncio
@mock.patch("qtrade.questrade.aiohttp.ClientSession.get", side_effect=mocked_access_token_requests_get)
async def test_get_access_token(mock_get):
    """This function tests the get access token method."""
    qtrade = Questrade(access_code="hunter2")
    assert set(qtrade.access_token.keys()) == set(
        ["access_token", "api_server", "expires_in", "refresh_token", "token_type"]
    )
    with pytest.raises(Exception) as e_info:
        _ = Questrade(access_code="hunter3")
        assert str(e_info.value) == "Token type was not provided."

# Other test functions follow the same pattern...
