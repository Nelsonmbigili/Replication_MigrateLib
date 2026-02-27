#!/usr/bin/env python
# coding=utf-8

import io
import os
import tempfile
import time
import urllib.parse as urlparse
from array import array
from unittest import mock

import pytest
import requests

from tdclient import api, version
from tdclient.test.test_helper import *


def setup_function(function):
    unset_environ()


def test_apikey_success():
    td = api.API("apikey")
    assert td.apikey == "apikey"


def test_apikey_from_environ():
    os.environ["TD_API_KEY"] = "APIKEY"
    td = api.API()
    assert td.apikey == "APIKEY"


def test_apikey_failure():
    with pytest.raises(ValueError) as error:
        api.API()
    assert error.value.args == ("no API key given",)


def test_default_user_agent():
    td = api.API("apikey")
    assert td._user_agent.startswith("TD-Client-Python/%s" % version.__version__)


def test_user_agent_from_keyword():
    td = api.API("apikey", user_agent="user_agent")
    assert td._user_agent == "user_agent"


def test_default_endpoint():
    td = api.API("apikey")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "https://api.treasuredata.com/" == url


def test_endpoint_from_environ():
    os.environ["TD_API_SERVER"] = "http://api1.example.com"
    td = api.API("apikey")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "http://api1.example.com" == url


def test_endpoint_from_keyword():
    td = api.API("apikey", endpoint="http://api2.example.com")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "http://api2.example.com" == url


def test_endpoint_prefer_keyword():
    os.environ["TD_API_SERVER"] = "http://api1.example.com"
    td = api.API("apikey", endpoint="http://api2.example.com")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "http://api2.example.com" == url


def test_http_endpoint_with_custom_port():
    td = api.API("apikey", endpoint="http://api.example.com:8080/")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "http://api.example.com:8080/" == url


def test_https_endpoint():
    td = api.API("apikey", endpoint="https://api.example.com/")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "https://api.example.com/" == url


def test_https_endpoint_with_custom_path():
    td = api.API("apikey", endpoint="https://api.example.com/v1/")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "https://api.example.com/v1/" == url


def test_https_endpoint():
    td = api.API("apikey", endpoint="api.example.com")
    assert isinstance(td.http, requests.Session)
    url, headers = td.build_request()
    assert "https://api.example.com" == url


def test_http_proxy_from_environ():
    os.environ["HTTP_PROXY"] = "http://proxy1.example.com:8080"
    td = api.API("apikey")
    assert isinstance(td.http, requests.Session)
    assert td.http.proxies["http"] == "http://proxy1.example.com:8080"


def test_http_proxy_from_keyword():
    td = api.API("apikey", http_proxy="http://proxy2.example.com:8080")
    assert isinstance(td.http, requests.Session)
    assert td.http.proxies["http"] == "http://proxy2.example.com:8080"


def test_http_proxy_prefer_keyword():
    os.environ["HTTP_PROXY"] = "http://proxy1.example.com:8080"
    td = api.API("apikey", http_proxy="http://proxy2.example.com:8080")
    assert isinstance(td.http, requests.Session)
    assert td.http.proxies["http"] == "http://proxy2.example.com:8080"


def test_http_proxy_with_scheme():
    td = api.API("apikey", http_proxy="http://proxy1.example.com:8080/")
    assert isinstance(td.http, requests.Session)
    assert td.http.proxies["http"] == "http://proxy1.example.com:8080/"


def test_http_proxy_with_credentials():
    td = api.API("apikey", http_proxy="http://john:doe@proxy1.example.com:8080")
    assert isinstance(td.http, requests.Session)
    assert td.http.proxies["http"] == "http://john:doe@proxy1.example.com:8080"


def test_no_timeout():
    with mock.patch("tdclient.api.requests.Session") as session_mock:
        td = api.API("apikey")
        session_mock.assert_called_once()
        assert td.http.timeout == 60


def test_timeout():
    with mock.patch("tdclient.api.requests.Session") as session_mock:
        td = api.API("apikey", timeout=12345)
        session_mock.assert_called_once()
        assert td.http.timeout == 12345


def test_get_success():
    td = api.API("APIKEY")
    with mock.patch("time.sleep") as t_sleep:
        td.http.get = mock.MagicMock()
        td.http.get.return_value = mock.Mock(status_code=200, content=b"body")
        response = td.get("/foo", {"bar": "baz"})
        td.http.get.assert_called_once_with(
            "https://api.treasuredata.com/foo",
            params={"bar": "baz"},
            headers=mock.ANY,
        )
        assert response.status_code == 200
        assert response.content == b"body"
        assert not t_sleep.called


# Other test cases would follow a similar pattern, replacing `urllib3` calls with `requests` equivalents.
