### Explanation of Changes
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Replaced `requests.get` and `requests.post`**:
   - `requests.get` was replaced with `urllib3.PoolManager().request('GET', ...)`.
   - `requests.post` was replaced with `urllib3.PoolManager().request('POST', ...)`.
2. **Mocking Changes**:
   - Updated the mocking of `requests.get` and `requests.post` to mock `urllib3.PoolManager().request`.
   - Adjusted the mock responses to align with `urllib3`'s response structure.
3. **Response Handling**:
   - `requests.Response` was replaced with `urllib3.response.HTTPResponse`.
   - Accessing the status code and JSON data was updated to match `urllib3`'s API. For example:
     - `response.status_code` → `response.status`.
     - `response.json()` → `json.loads(response.data.decode('utf-8'))` (since `urllib3` does not have a `json()` method).
4. **Imports**:
   - Removed the `requests` import and added `urllib3` and `json` imports.

### Modified Code
Here is the entire code after migration:

```python
"""
Tests for the token class.
"""

import unittest
import unittest.mock
import urllib3
import json
from coguard_cli.auth.token import Token
from coguard_cli.auth.auth_config import CoGuardCliConfig
from coguard_cli.auth.util import DealEnum

class TestTokenClass(unittest.TestCase):
    """
    The class for testing the token class.
    """

    def test_get_public_key_status_not_200(self):
        """
        Tests the public key extraction of the authentication server.
        """
        mock_response = unittest.mock.Mock(
            status = 420
        )
        mock_config_object = unittest.mock.Mock(
            get_auth_url = lambda: "https://portal.coguard.io"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('urllib3.PoolManager.request',
                                 new_callable=lambda: lambda method, url, timeout: mock_response):
            result = token.get_public_key()
            self.assertIsNone(result)

    def test_get_public_key_status_200_no_public_key(self):
        """
        Tests the public key extraction of the authentication server.
        """
        mock_response = unittest.mock.Mock(
            status = 200,
            data = json.dumps({}).encode('utf-8')
        )
        mock_config_object = unittest.mock.Mock(
            get_auth_url = lambda: "https://portal.coguard.io/auth"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('urllib3.PoolManager.request',
                                 new_callable=lambda: lambda method, url, timeout: mock_response):
            result = token.get_public_key()
            self.assertIsNone(result)

    def test_get_public_key_status_200_public_key(self):
        """
        Tests the public key extraction of the authentication server.
        """
        mock_response = unittest.mock.Mock(
            status = 200,
            data = json.dumps({"public_key": "123456"}).encode('utf-8')
        )
        mock_config_object = unittest.mock.Mock(
            get_auth_url = lambda: "https://portal.coguard.io/auth"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('urllib3.PoolManager.request',
                                 new_callable=lambda: lambda method, url, timeout: mock_response):
            result = token.get_public_key()
            self.assertEqual(result, "123456")

    def test_get_decoded_jwt_token(self):
        """
        Tests the decoded jwt token.
        """
        mock_result = unittest.mock.Mock()
        mock_jwt = unittest.mock.Mock(
            decode = lambda token, public_key: mock_result
        )
        with unittest.mock.patch(
                'jwt.JWT',
                return_value=mock_jwt
        ), \
        unittest.mock.patch(
                'jwt.jwk_from_pem',
                new_callable = lambda: lambda b: "foo"
        ):
            token = Token("foo", {})
            result = token.get_decoded_jwt_token(
                "bar"
            )
            self.assertEqual(result, mock_result)

    def test_extract_organization_from_token_no_pk(self):
        """
        Tests the extraction of the organization key from the token.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: ""
        ):
            token = Token("foo", {})
            result = token.extract_organization_from_token()
            self.assertIsNone(result)

    def test_extract_organization_from_token_pk_empty(self):
        """
        Tests the extraction of the organization key from the token.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: "pk"
        ), \
        unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_decoded_jwt_token',
                new_callable=lambda: lambda token, public_key: {}
        ):
            token = Token("foo", {})
            result = token.extract_organization_from_token()
            self.assertIsNone(result)

    def test_extract_organization_from_token_pk(self):
        """
        Tests the extraction of the organization key from the token.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: "pk"
        ), \
        unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_decoded_jwt_token',
                new_callable=lambda: lambda token, public_key: {"organization": "bar"}
        ):
            token = Token("foo", {})
            result = token.extract_organization_from_token()
            self.assertEqual(result, "bar")

    def test_extract_deal_type_from_token_no_pk(self):
        """
        Tests the extraction of deal type from the token no public key.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: ""
        ):
            token = Token("foo", {})
            result = token.extract_deal_type_from_token()
            self.assertEqual(result, DealEnum.FREE)

    def test_extract_deal_type_from_token_pk_no_deal_id(self):
        """
        Tests the extraction of deal type from the token no public key.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: "foo"
        ), \
        unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_decoded_jwt_token',
                new_callable=lambda: lambda token, pk: {}
        ):
            token = Token("foo", {})
            result = token.extract_deal_type_from_token()
            self.assertEqual(result, DealEnum.FREE)

    def test_extract_deal_type_from_token_pk_deal_id(self):
        """
        Tests the extraction of deal type from the token no public key.
        """
        with unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_public_key',
                new_callable=lambda: lambda c: "foo"
        ), \
        unittest.mock.patch(
                'coguard_cli.auth.token.Token.get_decoded_jwt_token',
                new_callable=lambda: lambda token, pk: {
                    "realm_access": {
                        "roles": [
                            "DEV"
                        ]
                    }
                }):
            token = Token("foo", {})
            result = token.extract_deal_type_from_token()
            self.assertEqual(result, DealEnum.DEV)

    def test_authenticate_to_server_empty_config_object(self):
        """
        Tests that the authentication returns None if the configuration object is None
        """
        token = Token("foo", None)
        self.assertIsNone(token.authenticate_to_server())

    def test_authenticate_to_server_non_empty_config_object_404(self):
        """
        Tests that the authentication returns None if the status code
        is not 200.
        """
        config_obj = CoGuardCliConfig("foo", "bar")
        def new_callable(method, url, body, headers, timeout):
            response = unittest.mock.Mock(
                status = 404
            )
            return response
        with unittest.mock.patch('urllib3.PoolManager.request',
                                 new_callable=lambda: new_callable):
            token = Token("foo", config_obj)
            self.assertIsNone(token.authenticate_to_server())

    def test_authenticate_to_server_non_empty_config_object_success(self):
        """
        Tests that the authentication returns None if the status code
        is not 200.
        """
        config_obj = CoGuardCliConfig("foo", "bar")
        def new_callable(method, url, body, headers, timeout):
            response = unittest.mock.Mock(
                status = 200,
                data = json.dumps({"access_token": "foo"}).encode('utf-8')
            )
            return response
        with unittest.mock.patch('urllib3.PoolManager.request',
                                 new_callable=lambda: new_callable):
            token = Token("foo", config_obj)
            result = token.authenticate_to_server()
            self.assertIsNotNone(result)
            self.assertEqual(result, "foo")
```

This code now uses `urllib3` instead of `requests` while maintaining the original functionality and structure.