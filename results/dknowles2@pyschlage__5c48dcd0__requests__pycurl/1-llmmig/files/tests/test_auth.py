from unittest import mock
import io

from botocore.exceptions import ClientError
import pytest
import pycurl

import pyschlage
from pyschlage import auth as _auth


@mock.patch("pycurl.Curl")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_authenticate(mock_cognito, mock_srp_auth, mock_curl):
    auth = _auth.Auth("__username__", "__password__")

    mock_cognito.assert_called_once()
    assert mock_cognito.call_args.kwargs["username"] == "__username__"

    mock_srp_auth.assert_called_once_with(
        password="__password__", cognito=mock_cognito.return_value
    )

    auth.authenticate()
    mock_srp_auth.return_value.assert_called_once_with(mock_curl.return_value)


@mock.patch("pycurl.Curl")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_request(mock_cognito, mock_srp_auth, mock_curl):
    auth = _auth.Auth("__username__", "__password__")
    auth.request("get", "/foo/bar", baz="bam")

    mock_curl_instance = mock_curl.return_value
    mock_curl_instance.setopt.assert_any_call(pycurl.URL, "https://api.allegion.yonomi.cloud/v1/foo/bar")
    mock_curl_instance.setopt.assert_any_call(pycurl.CUSTOMREQUEST, "GET")
    mock_curl_instance.setopt.assert_any_call(pycurl.TIMEOUT, 60)
    mock_curl_instance.setopt.assert_any_call(
        pycurl.HTTPHEADER, ["X-Api-Key: " + _auth.API_KEY]
    )
    mock_curl_instance.perform.assert_called_once()


@mock.patch("pycurl.Curl", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
def test_request_not_authorized(mock_cognito, mock_srp_auth, mock_curl):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")

    mock_curl_instance = mock_curl.return_value
    mock_curl_instance.perform.side_effect = pycurl.error(
        pycurl.E_HTTP_RETURNED_ERROR, f"Unauthorized for url: {url}"
    )

    with pytest.raises(
        pyschlage.exceptions.NotAuthorizedError, match=f"Unauthorized for url: {url}"
    ):
        auth.request("get", "/foo/bar", baz="bam")

    mock_curl_instance.setopt.assert_any_call(pycurl.URL, url)
    mock_curl_instance.setopt.assert_any_call(pycurl.CUSTOMREQUEST, "GET")
    mock_curl_instance.setopt.assert_any_call(pycurl.TIMEOUT, 60)
    mock_curl_instance.setopt.assert_any_call(
        pycurl.HTTPHEADER, ["X-Api-Key: " + _auth.API_KEY]
    )
    mock_curl_instance.perform.assert_called_once()


@mock.patch("pycurl.Curl", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
def test_request_unknown_error(mock_cognito, mock_srp_auth, mock_curl):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")

    mock_curl_instance = mock_curl.return_value
    mock_curl_instance.perform.side_effect = pycurl.error(
        pycurl.E_HTTP_RETURNED_ERROR, f"500 Server Error: Internal for url: {url}"
    )

    with pytest.raises(pyschlage.exceptions.UnknownError):
        auth.request("get", "/foo/bar", baz="bam")

    mock_curl_instance.setopt.assert_any_call(pycurl.URL, url)
    mock_curl_instance.setopt.assert_any_call(pycurl.CUSTOMREQUEST, "GET")
    mock_curl_instance.setopt.assert_any_call(pycurl.TIMEOUT, 60)
    mock_curl_instance.setopt.assert_any_call(
        pycurl.HTTPHEADER, ["X-Api-Key: " + _auth.API_KEY]
    )
    mock_curl_instance.perform.assert_called_once()


@mock.patch("pycurl.Curl")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_user_id(mock_cognito, mock_srp_auth, mock_curl):
    auth = _auth.Auth("__username__", "__password__")

    mock_curl_instance = mock_curl.return_value
    response_buffer = io.BytesIO()
    response_data = b"""
    {
        "consentRecords": [],
        "created": "2022-12-24T20:00:00.000Z",
        "email": "asdf@asdf.com",
        "friendlyName": "username",
        "identityId": "<user-id>",
        "lastUpdated": "2022-12-24T20:00:00.000Z"
    }
    """
    response_buffer.write(response_data)
    response_buffer.seek(0)

    mock_curl_instance.setopt.side_effect = lambda opt, val: None
    mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)

    assert auth.user_id == "<user-id>"

    mock_curl_instance.setopt.assert_any_call(
        pycurl.URL, "https://api.allegion.yonomi.cloud/v1/users/@me"
    )
    mock_curl_instance.setopt.assert_any_call(pycurl.CUSTOMREQUEST, "GET")
    mock_curl_instance.setopt.assert_any_call(pycurl.TIMEOUT, 60)
    mock_curl_instance.setopt.assert_any_call(
        pycurl.HTTPHEADER, ["X-Api-Key: " + _auth.API_KEY]
    )
    mock_curl_instance.perform.assert_called_once()


@mock.patch("pycurl.Curl")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_user_id_is_cached(mock_cognito, mock_srp_auth, mock_curl):
    auth = _auth.Auth("__username__", "__password__")

    mock_curl_instance = mock_curl.return_value
    response_buffer = io.BytesIO()
    response_data = b"""
    {
        "consentRecords": [],
        "created": "2022-12-24T20:00:00.000Z",
        "email": "asdf@asdf.com",
        "friendlyName": "username",
        "identityId": "<user-id>",
        "lastUpdated": "2022-12-24T20:00:00.000Z"
    }
    """
    response_buffer.write(response_data)
    response_buffer.seek(0)

    mock_curl_instance.setopt.side_effect = lambda opt, val: None
    mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)

    assert auth.user_id == "<user-id>"
    mock_curl_instance.perform.assert_called_once()

    mock_curl_instance.reset_mock()
    assert auth.user_id == "<user-id>"
    mock_curl_instance.perform.assert_not_called()
