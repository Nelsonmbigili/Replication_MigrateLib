# -*- coding: utf-8 -*-

import unittest.mock
import pycurl
from io import BytesIO


def test_camundarequest_keeps_query_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, query_param='aStr').query_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, query_param=1).query_parameters()['param'] == 1


def test_camundarequest_keeps_body_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, body_param='aStr').body_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, body_param=1).body_parameters()['param'] == 1
    assert MyRequest(url=engine_url, body_param=True).body_parameters()['param'] is True
    assert MyRequest(url=engine_url, body_param=False).body_parameters()['param'] is False


def test_camundarequest_converts_bool_query_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, query_param=True).query_parameters()['param'] == 'true'
    assert MyRequest(url=engine_url, query_param=False).query_parameters()['param'] == 'false'


def test_camundarequest_converts_datetime_params(
    engine_url, MyRequest, date, date_tz, date_str, date_tz_str
):

    assert MyRequest(url=engine_url, query_param=date).query_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, query_param=date_tz).query_parameters()['param'] == date_tz_str

    assert MyRequest(url=engine_url, body_param=date).body_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, body_param=date_tz).body_parameters()['param'] == date_tz_str


@unittest.mock.patch('pycurl.Curl.perform')
def test_camundarequest_session(mock_perform, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth_username = 'Jane'
    auth_password = 'password'

    # Create a pycurl.Curl object to simulate a session
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, engine_url)
    curl.setopt(pycurl.USERPWD, f"{auth_username}:{auth_password}")

    # Mock the perform method
    request.session = curl

    # Simulate the request
    request()

    # Assertions
    assert mock_perform.called
    assert curl.getinfo(pycurl.EFFECTIVE_URL) == engine_url
    assert curl.getinfo(pycurl.USERPWD) == f"{auth_username}:{auth_password}"
