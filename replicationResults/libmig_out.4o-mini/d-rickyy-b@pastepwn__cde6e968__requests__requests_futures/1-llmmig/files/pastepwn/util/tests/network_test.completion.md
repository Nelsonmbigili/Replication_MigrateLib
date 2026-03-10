### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves replacing the synchronous request calls with asynchronous ones provided by `requests_futures`. This requires using the `FuturesSession` class from the `requests_futures.sessions` module instead of the standard `requests` session. The `FuturesSession` allows for non-blocking requests, enabling the program to continue executing while waiting for the response.

### Modified Code
Here is the modified code with the necessary changes to use `requests_futures`:

```python
import os
import socket
import unittest
from unittest.mock import Mock

import requests.packages.urllib3.util.connection as urllib3_cn
from requests_futures.sessions import FuturesSession  # Import FuturesSession

from pastepwn.util import enforce_ip_version


@unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.")
class TestNetwork(unittest.TestCase):
    """Tests for the network utils - these tests might fail on CI"""

    def setUp(self):
        self.session = FuturesSession()  # Use FuturesSession instead of requests.Session

    def test_enforce_ip_version_4(self):
        enforce_ip_version(4)
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_INET)
        enforce_ip_version("4")
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_INET)

    def test_enforce_ip_version_5(self):
        with self.assertRaises(Exception):
            enforce_ip_version(5)

        with self.assertRaises(Exception):
            enforce_ip_version("5")

    def test_enforce_ip_version_6(self):
        enforce_ip_version(6)
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_INET6)
        enforce_ip_version("6")
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_INET6)

    def test_enforce_ip_version_None(self):
        enforce_ip_version(None)
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_UNSPEC)

        enforce_ip_version()
        self.assertEqual(urllib3_cn.allowed_gai_family(), socket.AF_UNSPEC)

    def test_enforce_ip_version_obj(self):
        mock = Mock()
        with self.assertRaises(ValueError):
            enforce_ip_version(mock)


if __name__ == "__main__":
    unittest.main()
```

### Note
In this migration, I added a `setUp` method to initialize the `FuturesSession`, which allows for asynchronous requests. However, since the original code does not contain any actual HTTP requests, the migration primarily demonstrates the setup for using `requests_futures`. If there were specific request calls in the original code, they would need to be modified to use the `self.session` object for making requests asynchronously.