### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Library Import**: Replaced the `requests` import with `requests_futures`.
2. **Asynchronous Requests**: The `requests_futures` library provides asynchronous capabilities by using `FuturesSession`. Any usage of `requests` in the code (e.g., `requests.get`, `requests.post`) would need to be replaced with the corresponding asynchronous calls using a `FuturesSession` object.
3. **Session Initialization**: A `FuturesSession` object is created and used for making HTTP requests. This replaces direct calls to `requests` methods.
4. **No Changes to Non-HTTP Code**: Since the provided code does not directly use `requests` for HTTP calls (it seems to rely on `coguard_cli.auth` for such operations), the migration only involves updating the import statement to ensure compatibility with `requests_futures`.

### Modified Code
Here is the updated code after migrating to `requests_futures`:

```python
"""
Tests for the common functions in the coguard_cli.auth package.
"""

import os
import unittest
import unittest.mock
from requests_futures.sessions import FuturesSession
import coguard_cli.auth

class TestAuthClass(unittest.TestCase):
    """
    The class for testing the auth module.
    """

    def setUp(self):
        """
        Method to be run before all tests are being executed.
        """
        self.path_to_resources = "./coguard_cli/tests/auth/resources"

    def test_get_auth_file_non_existing_path(self):
        """
        Tests that the return value of get_auth_file is the empty dictionary
        if the path does not exist.
        """
        res = coguard_cli.auth.get_auth_file(
            os.path.join(
                self.path_to_resources, "I_WILL_NEVER_EXIST.json"
            )
        )
        self.assertDictEqual(res, {})

    def test_get_auth_file_existing_path(self):
        """
        Tests that the return value of get_auth_file represents the contents
        of the file if the path does exist.
        """
        res = coguard_cli.auth.get_auth_file(
            os.path.join(
                self.path_to_resources,
                "sample_config"
            )
        )
        self.assertDictEqual(res, {
            "password": "df28fd0e-58b0-416a-b659-cfeafdbef74a",
            "username": "email@email.com",
            "coguard-url": "https://portal.coguard.io"
        })

    def test_get_auth_file_existing_path_not_400(self):
        """
        Tests that the return value of get_auth_file represents the contents
        of the file if the path does exist.
        """
        res = coguard_cli.auth.get_auth_file(
            os.path.join(
                self.path_to_resources,
                "sample_config_not_400"
            )
        )
        self.assertDictEqual(res, {})

    def test_get_file_without_json(self):
        """
        Tests that the return value of get_auth_file is the empty dictionary
        if the contents of the file are not json
        """
        res = coguard_cli.auth.get_auth_file(
            os.path.join(
                self.path_to_resources,
                "sample_config_not_json"
            )
        )
        self.assertDictEqual(res, {})

    def test_retrieve_configuration_object_non_existing_path(self):
        """
        Tests that the return value of retrieve_configuration_object is the empty dictionary
        if the path does not exist.
        """
        with unittest.mock.patch(
                'os.environ.get',
                new_callable=lambda: lambda x: None):
            res = coguard_cli.auth.retrieve_configuration_object(
                os.path.join(
                    self.path_to_resources, "I_WILL_NEVER_EXIST.json"
                )
            )
            self.assertIsNone(res)

    def test_retrieve_configuration_object_existing_path(self):
        """
        Tests that the return value of retrieve_configuration_object represents the contents
        of the file if the path does exist.
        """
        with unittest.mock.patch(
                'os.environ.get',
                new_callable=lambda: lambda x: None):
            res = coguard_cli.auth.retrieve_configuration_object(
                os.path.join(
                    self.path_to_resources,
                    "sample_config"
                )
            )
            self.assertIsNotNone(res)
            self.assertEqual(res.get_username(), "email@email.com")
            self.assertEqual(res.get_password(), "df28fd0e-58b0-416a-b659-cfeafdbef74a")
            self.assertEqual(res.get_coguard_url(), "https://portal.coguard.io")

    def test_get_config_object_without_json(self):
        """
        Tests that the return value of retrieve_configuration_object is the empty dictionary
        if the contents of the file are not json
        """
        with unittest.mock.patch(
                'os.environ.get',
                new_callable=lambda: lambda x: None):
            res = coguard_cli.auth.retrieve_configuration_object(
                os.path.join(
                    self.path_to_resources,
                    "sample_config_not_json"
                )
            )
            self.assertIsNone(res)

    def test_store_config_object_in_auth_file(self):
        """
        Testing the storing of the configuration object
        """
        config_object = unittest.mock.Mock()
        makedirs_mock = unittest.mock.MagicMock()
        with unittest.mock.patch(
                'os.makedirs',
                makedirs_mock
        ), unittest.mock.patch(
            'os.chmod'
        ), unittest.mock.patch(
            'builtins.open',
            unittest.mock.mock_open()
        ):
            coguard_cli.auth.store_config_object_in_auth_file(
                config_object,
                "foo/bar/baz.conf"
            )
            makedirs_mock.assert_called_with("foo/bar", exist_ok=True)
```

### Summary of Changes
- Replaced `import requests` with `from requests_futures.sessions import FuturesSession`.
- No other changes were necessary because the provided code does not directly use `requests` for HTTP calls. If `coguard_cli.auth` internally uses `requests`, it would need to be updated separately to use `FuturesSession`.