The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from unittest import mock

from botocore.exceptions import ClientError
import pytest
import requests

import pyschlage
from pyschlage import auth as _auth


@mock.patch("requests.Request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_authenticate(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")

    mock_cognito.assert_called_once()
    assert mock_cognito.call_args.kwargs["username"] == "__username__"

    mock_srp_auth.assert_called_once_with(
        password="__password__", cognito=mock_cognito.return_value
    )

    auth.authenticate()
    mock_srp_auth.return_value.assert_called_once_with(mock_request.return_value)


@mock.patch("requests.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_request(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    auth.request("get", "/foo/bar", baz="bam")
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/foo/bar",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("requests.request", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
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
        auth.request("get", "/foo/bar", baz="bam")

    mock_request.assert_called_once_with(
        "get",
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("requests.request", spec=True)
@mock.patch("pycognito.utils.RequestsSrpAuth", spec=True)
@mock.patch("pycognito.Cognito")
def test_request_unknown_error(mock_cognito, mock_srp_auth, mock_request):
    url = "https://api.allegion.yonomi.cloud/v1/foo/bar"
    auth = _auth.Auth("__username__", "__password__")
    mock_resp = mock.create_autospec(requests.Response)
    mock_resp.raise_for_status.side_effect = requests.HTTPError(
        f"500 Server Error: Internal for url: {url}"
    )
    mock_resp.status_code = 500
    mock_resp.reason = "Internal"
    mock_resp.json.side_effect = requests.JSONDecodeError("msg", "doc", 1)
    mock_request.return_value = mock_resp

    with pytest.raises(pyschlage.exceptions.UnknownError):
        auth.request("get", "/foo/bar", baz="bam")

    mock_request.assert_called_once_with(
        "get",
        url,
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
        baz="bam",
    )


@mock.patch("requests.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_user_id(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    mock_request.return_value = mock.Mock(
        json=mock.Mock(
            return_value={
                "consentRecords": [],
                "created": "2022-12-24T20:00:00.000Z",
                "email": "asdf@asdf.com",
                "friendlyName": "username",
                "identityId": "<user-id>",
                "lastUpdated": "2022-12-24T20:00:00.000Z",
            }
        )
    )
    assert auth.user_id == "<user-id>"
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )


@mock.patch("requests.request")
@mock.patch("pycognito.utils.RequestsSrpAuth")
@mock.patch("pycognito.Cognito")
def test_user_id_is_cached(mock_cognito, mock_srp_auth, mock_request):
    auth = _auth.Auth("__username__", "__password__")
    mock_request.return_value = mock.Mock(
        json=mock.Mock(
            return_value={
                "consentRecords": [],
                "created": "2022-12-24T20:00:00.000Z",
                "email": "asdf@asdf.com",
                "friendlyName": "username",
                "identityId": "<user-id>",
                "lastUpdated": "2022-12-24T20:00:00.000Z",
            }
        )
    )
    assert auth.user_id == "<user-id>"
    mock_request.assert_called_once_with(
        "get",
        "https://api.allegion.yonomi.cloud/v1/users/@me",
        timeout=60,
        auth=mock_srp_auth.return_value,
        headers={"X-Api-Key": _auth.API_KEY},
    )
    mock_request.reset_mock()
    assert auth.user_id == "<user-id>"
    mock_request.assert_not_called()

```