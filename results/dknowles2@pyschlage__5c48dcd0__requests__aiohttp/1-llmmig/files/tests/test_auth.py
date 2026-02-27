from unittest import mock

from botocore.exceptions import ClientError
import pytest
import aiohttp

import pyschlage
from pyschlage import auth as _auth


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_authenticate(mock_cognito, mock_srp_auth, mock_client_session):
    auth = _auth.Auth("__username__", "__password__")

    mock_cognito.assert_called_once()
    assert mock_cognito.call_args.kwargs["username"] == "__username__"

    mock_srp_auth.assert_called_once_with(
        password="__password__", cognito=mock_cognito.return_value
    )

    await auth.authenticate()
    mock_srp_auth.return_value.assert_called_once_with(mock_client_session.return_value)


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_request(mock_cognito, mock_srp_auth, mock_client_session):
    auth = _auth.Auth("__username__", "__password__")
    mock_session_instance = mock_client_session.return_value
    mock_session_instance.get.return_value.__aenter__.return_value.json = mock.AsyncMock(
        return_value={}
    )

    await auth.request("get", "/foo/bar", baz="bam")
    mock_session_instance.get.assert_called_once_with(
        "https://api.allegion.yonomi.cloud/v1/foo/bar",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        params={"baz": "bam"},
    )


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_request_not_authorized(mock_cognito, mock_srp_auth, mock_client_session):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")
    mock_session_instance = mock_client_session.return_value
    mock_session_instance.get.side_effect = ClientError(
        {
            "Error": {
                "Code": "NotAuthorizedException",
                "Message": f"Unauthorized for url: {url}",
            }
        },
        "foo-op",
    )

    with pytest.raises(
        pyschlage.exceptions.NotAuthorizedError, match=f"Unauthorized for url: {url}"
    ):
        await auth.request("get", "/foo/bar", baz="bam")

    mock_session_instance.get.assert_called_once_with(
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        params={"baz": "bam"},
    )


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_request_unknown_error(mock_cognito, mock_srp_auth, mock_client_session):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")
    mock_session_instance = mock_client_session.return_value
    mock_resp = mock.Mock()
    mock_resp.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info=None, history=None, status=500, message="Internal"
    )
    mock_resp.status = 500
    mock_resp.reason = "Internal"
    mock_resp.json = mock.AsyncMock(side_effect=aiohttp.ContentTypeError(None, None))
    mock_session_instance.get.return_value.__aenter__.return_value = mock_resp

    with pytest.raises(pyschlage.exceptions.UnknownError):
        await auth.request("get", "/foo/bar", baz="bam")

    mock_session_instance.get.assert_called_once_with(
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        params={"baz": "bam"},
    )


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_user_id(mock_cognito, mock_srp_auth, mock_client_session):
    auth = _auth.Auth("__username__", "__password__")
    mock_session_instance = mock_client_session.return_value
    mock_session_instance.get.return_value.__aenter__.return_value.json = mock.AsyncMock(
        return_value={
            "consentRecords": [],
            "created": "2022-12-24T20:00:00.000Z",
            "email": "asdf@asdf.com",
            "friendlyName": "username",
            "identityId": "<user-id>",
            "lastUpdated": "2022-12-24T20:00:00.000Z",
        }
    )
    assert await auth.user_id == "<user-id>"
    mock_session_instance.get.assert_called_once_with(
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )


@mock.patch("aiohttp.ClientSession")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@pytest.mark.asyncio
async def test_user_id_is_cached(mock_cognito, mock_srp_auth, mock_client_session):
    auth = _auth.Auth("__username__", "__password__")
    mock_session_instance = mock_client_session.return_value
    mock_session_instance.get.return_value.__aenter__.return_value.json = mock.AsyncMock(
        return_value={
            "consentRecords": [],
            "created": "2022-12-24T20:00:00.000Z",
            "email": "asdf@asdf.com",
            "friendlyName": "username",
            "identityId": "<user-id>",
            "lastUpdated": "2022-12-24T20:00:00.000Z",
        }
    )
    assert await auth.user_id == "<user-id>"
    mock_session_instance.get.assert_called_once_with(
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )
    mock_session_instance.get.reset_mock()
    assert await auth.user_id == "<user-id>"
    mock_session_instance.get.assert_not_called()
