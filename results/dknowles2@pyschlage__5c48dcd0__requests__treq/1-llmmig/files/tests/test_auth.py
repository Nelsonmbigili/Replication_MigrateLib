from unittest import mock
from twisted.internet.defer import succeed, inlineCallbacks
from botocore.exceptions import ClientError
import pytest
import treq

import pyschlage
from pyschlage import auth as _auth


@mock.patch("treq.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_authenticate(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")

    mock_cognito.assert_called_once()
    assert mock_cognito.call_args.kwargs["username"] == "__username__"

    mock_srp_auth.assert_called_once_with(
        password="__password__", cognito=mock_cognito.return_value
    )

    yield auth.authenticate()
    mock_srp_auth.return_value.assert_called_once_with(mock_request.return_value)


@mock.patch("treq.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_request(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    yield auth.request("get", "/foo/bar", baz="bam")
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/foo/bar",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("treq.request", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_request_not_authorized(mock_cognito, mock_srp_auth, mock_request):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")
    mock_request.side_effect = ClientError(
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
        yield auth.request("get", "/foo/bar", baz="bam")

    mock_request.assert_called_once_with(
        "get",
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("treq.request", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_request_unknown_error(mock_cognito, mock_srp_auth, mock_request):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")
    mock_resp = mock.Mock()
    mock_resp.raise_for_status.side_effect = Exception(
        f"500 Server Error: Internal for url: {url}"
    )
    mock_resp.code = 500
    mock_resp.reason = "Internal"
    mock_resp.json.side_effect = Exception("JSONDecodeError")
    mock_request.return_value = succeed(mock_resp)

    with pytest.raises(pyschlage.exceptions.UnknownError):
        yield auth.request("get", "/foo/bar", baz="bam")

    mock_request.assert_called_once_with(
        "get",
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("treq.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_user_id(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    mock_request.return_value = succeed(
        mock.Mock(
            json=mock.Mock(
                return_value=succeed(
                    {
                        "consentRecords": [],
                        "created": "2022-12-24T20:00:00.000Z",
                        "email": "asdf@asdf.com",
                        "friendlyName": "username",
                        "identityId": "<user-id>",
                        "lastUpdated": "2022-12-24T20:00:00.000Z",
                    }
                )
            )
        )
    )
    user_id = yield auth.user_id
    assert user_id == "<user-id>"
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )


@mock.patch("treq.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
@inlineCallbacks
def test_user_id_is_cached(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    mock_request.return_value = succeed(
        mock.Mock(
            json=mock.Mock(
                return_value=succeed(
                    {
                        "consentRecords": [],
                        "created": "2022-12-24T20:00:00.000Z",
                        "email": "asdf@asdf.com",
                        "friendlyName": "username",
                        "identityId": "<user-id>",
                        "lastUpdated": "2022-12-24T20:00:00.000Z",
                    }
                )
            )
        )
    )
    user_id = yield auth.user_id
    assert user_id == "<user-id>"
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )
    mock_request.reset_mock()
    user_id = yield auth.user_id
    assert user_id == "<user-id>"
    mock_request.assert_not_called()
