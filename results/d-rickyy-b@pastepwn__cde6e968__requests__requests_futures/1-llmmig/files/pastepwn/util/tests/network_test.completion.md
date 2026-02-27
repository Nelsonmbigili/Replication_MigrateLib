### Explanation of Changes:
The provided code does not directly use the `requests` library for making HTTP requests, so there is no need to migrate to `requests_futures`. The code primarily tests the `enforce_ip_version` function and uses `unittest` for testing. Since no HTTP requests are being made in the code, there is no dependency on `requests` or `requests_futures` for this specific code snippet.

Thus, no changes are required to migrate this code to use `requests_futures`. The original code remains valid and functional as is.

### Modified Code:
No modifications are necessary. The original code is provided below unchanged:

```python
import os
import socket
import unittest
from unittest.mock import Mock

import requests.packages.urllib3.util.connection as urllib3_cn

from pastepwn.util import enforce_ip_version


@unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.")
class TestNetwork(unittest.TestCase):
    """Tests for the network utils - these tests might fail on CI"""

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