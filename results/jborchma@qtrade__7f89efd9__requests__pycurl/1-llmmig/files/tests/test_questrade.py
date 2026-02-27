"""Questrade test module
"""

from unittest import mock
import io
import json
import pycurl
import pytest
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

# Helper function to perform pycurl requests
def perform_pycurl_request(url, method="GET", headers=None, params=None):
    """Helper function to perform a pycurl request."""
    buffer = io.BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.CUSTOMREQUEST, method)

    if headers:
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

    if params:
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        curl.setopt(pycurl.URL, f"{url}?{query_string}")

    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()

    response_data = buffer.getvalue().decode("utf-8")
    buffer.close()

    if 400 <= status_code < 600:
        raise Exception(f"{status_code} Error: {response_data}")

    return json.loads(response_data)


# Mocking functions for pycurl
def mocked_access_token_pycurl(*args, **kwargs):
    """Mocking access token pycurl request."""
    if args[0] == TOKEN_URL + "hunter2":
        return VALID_ACCESS_TOKEN
    elif args[0] == TOKEN_URL + "hunter3":
        return INVALID_ACCESS_TOKEN
    else:
        raise Exception("404 Not Found")


### TEST FUNCTIONS ###


@mock.patch("qtrade.questrade.perform_pycurl_request", side_effect=mocked_access_token_pycurl)
def test_del_method_session_close(mock_get):
    """ "This function tests the successful session closing."""
    qtrade = Questrade(access_code="hunter2")
    qtrade.__del__()


@mock.patch("qtrade.questrade.perform_pycurl_request", side_effect=mocked_access_token_pycurl)
def test_get_access_token(mock_get):
    """This function tests the get access token method."""
    qtrade = Questrade(access_code="hunter2")
    assert set(qtrade.access_token.keys()) == set(
        ["access_token", "api_server", "expires_in", "refresh_token", "token_type"]
    )
    with pytest.raises(Exception) as e_info:
        _ = Questrade(access_code="hunter3")
        assert str(e_info.value) == "Token type was not provided."


@mock.patch("builtins.open", mock.mock_open(read_data=ACCESS_TOKEN_YAML))
def test_init_via_yaml():
    """This function tests when the class is initiated via yaml file."""
    qtrade = Questrade(token_yaml="access_token.yml")
    assert set(qtrade.access_token.keys()) == set(
        ["access_token", "api_server", "expires_in", "refresh_token", "token_type"]
    )
    assert qtrade.access_token["access_token"] == "hunter2"
    assert qtrade.access_token["api_server"] == "http://www.api_url.com"
    assert qtrade.access_token["expires_in"] == 1234
    assert qtrade.access_token["refresh_token"] == "hunter2"
    assert qtrade.access_token["token_type"] == "Bearer"


@mock.patch("builtins.open", mock.mock_open(read_data=ACCESS_TOKEN_YAML))
def test_init_via_incomplete_yaml():
    """This function tests when the class is initiated via incomplete yaml file."""
    with pytest.raises(Exception) as e_info:
        _ = Questrade(token_yaml="access_token.yml")
        assert str(e_info.value) == "Refresh token was not provided."


@mock.patch("builtins.open", mock.mock_open(read_data=ACCESS_TOKEN_YAML))
@mock.patch("qtrade.questrade.perform_pycurl_request", side_effect=mocked_access_token_pycurl)
def test_refresh_token_yaml(mock_get):
    """This function tests the refresh token method by using the yaml."""
    qtrade = Questrade(token_yaml="access_token.yml")
    qtrade.refresh_access_token(from_yaml=True)
    assert set(qtrade.access_token.keys()) == set(
        ["access_token", "api_server", "expires_in", "refresh_token", "token_type"]
    )
    assert qtrade.access_token["api_server"] == "https://questrade.api"


@mock.patch("builtins.open", mock.mock_open(read_data=ACCESS_TOKEN_YAML))
@mock.patch("qtrade.questrade.perform_pycurl_request", side_effect=mocked_access_token_pycurl)
def test_refresh_token_non_yaml(mock_get):
    """This function tests the refresh token method without yaml use."""
    qtrade = Questrade(token_yaml="access_token.yml")
    qtrade.refresh_access_token()
    assert set(qtrade.access_token.keys()) == set(
        ["access_token", "api_server", "expires_in", "refresh_token", "token_type"]
    )
    assert qtrade.access_token["api_server"] == "https://questrade.api"
